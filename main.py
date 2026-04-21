import asyncio
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database import init_db, add_watch, remove_watch, get_watchlist, get_all_watches
from checker import is_live
from recorder import start_recording, stop_recording, is_recording

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHECK_INTERVAL = 60
SEGMENT_DURATION = 300

os.makedirs("recordings", exist_ok=True)

segment_tasks = {}
checker_lock = None


# ── Commands ──────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Bot Rekam TikTok Live Aktif\n\n"
        "/watch @username — tambah watch\n"
        "/unwatch @username — hapus\n"
        "/list — lihat watchlist"
    )

async def cmd_watch(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Contoh: /watch @username")
        return
    username = ctx.args[0].lstrip("@").lower()
    chat_id = update.effective_chat.id
    added_by = update.effective_user.id
    ok = await add_watch(chat_id, username, added_by)
    if ok:
        await update.message.reply_text(f"✅ @{username} ditambahkan")
    else:
        await update.message.reply_text(f"⚠️ @{username} sudah ada")

async def cmd_unwatch(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Contoh: /unwatch @username")
        return
    username = ctx.args[0].lstrip("@").lower()
    chat_id = update.effective_chat.id
    await remove_watch(chat_id, username)
    await update.message.reply_text(f"🗑️ @{username} dihapus")

async def cmd_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    watches = await get_watchlist(chat_id)
    if not watches:
        await update.message.reply_text("Watchlist kosong")
        return
    text = "📋 Watchlist:\n" + "".join(f"• @{u}\n" for u in watches)
    await update.message.reply_text(text)


# ── Kirim segment ke Telegram ─────────────────────────

async def send_segment(app: Application, username: str, filename: str, segment_num: int):
    watches = await get_all_watches()

    if not os.path.exists(filename):
        print(f"❌ File tidak ada: {filename}")
        return

    file_size = os.path.getsize(filename)
    print(f"📦 Ukuran segment {segment_num}: {file_size} bytes")

    if file_size == 0:
        print(f"❌ File kosong, skip")
        os.remove(filename)
        return

    for cid, uname in watches:
        if uname != username:
            continue
        try:
            if file_size < 50 * 1024 * 1024:
                await app.bot.send_document(
                    cid,
                    document=open(filename, "rb"),
                    caption=f"🎬 @{username} — segment {segment_num}"
                )
                print(f"✅ Berhasil kirim segment {segment_num} ke {cid}")
            else:
                await app.bot.send_message(
                    cid,
                    f"⚠️ Segment {segment_num} @{username} terlalu besar "
                    f"({file_size // 1024 // 1024}MB), tidak bisa dikirim"
                )
        except Exception as e:
            print(f"❌ Error kirim segment {segment_num}: {e}")
    try:
        os.remove(filename)
    except Exception:
        pass


# ── Loop rekam per segment ────────────────────────────

async def recording_loop(app: Application, username: str, stream_url: str):
    segment_num = 1
    watches = await get_all_watches()

    for cid, uname in watches:
        if uname == username:
            await app.bot.send_message(
                cid,
                f"🔴 @{username} LIVE\n🎥 Mulai rekam segment {segment_num}..."
            )

    while True:
        try:
            live, new_url = await is_live(username)
        except Exception:
            live = False

        if not live:
            print(f"⏹️ @{username} sudah tidak live")
            watches2 = await get_all_watches()
            for cid, uname in watches2:
                if uname == username:
                    await app.bot.send_message(
                        cid,
                        f"✅ @{username} selesai live\nTotal: {segment_num - 1} segment"
                    )
            break

        url_to_use = new_url if new_url else stream_url
        filename = await start_recording(username, url_to_use, duration=SEGMENT_DURATION)
        if not filename:
            print(f"❌ Gagal start rekam @{username}")
            await asyncio.sleep(10)
            continue

        print(f"🎥 Rekam segment {segment_num} @{username}")

        # Cek live setiap 30 detik
        still_live = True
        elapsed = 0
        while elapsed < SEGMENT_DURATION:
            await asyncio.sleep(30)
            elapsed += 30
            try:
                still_live, _ = await is_live(username)
            except Exception:
                still_live = False

            if not still_live:
                print(f"⏹️ @{username} berhenti live di detik ke-{elapsed}")
                break

        # Stop dan kirim
        actual_file = await stop_recording(username)
        if actual_file and os.path.exists(actual_file):
            file_size = os.path.getsize(actual_file)
            if file_size > 0:
                print(f"📤 Kirim segment {segment_num} @{username}")
                await send_segment(app, username, actual_file, segment_num)
            else:
                print(f"⚠️ File kosong, skip")
                try:
                    os.remove(actual_file)
                except Exception:
                    pass

        if not still_live:
            watches2 = await get_all_watches()
            for cid, uname in watches2:
                if uname == username:
                    await app.bot.send_message(
                        cid,
                        f"✅ @{username} selesai live\nTotal: {segment_num} segment"
                    )
            break

        segment_num += 1
        await asyncio.sleep(2)

    segment_tasks.pop(username, None)


# ── Scheduler cek live ───────────────────────────────

async def check_all_lives(app: Application):
    global checker_lock
    if checker_lock is None:
        checker_lock = asyncio.Lock()

    if checker_lock.locked():
        return

    async with checker_lock:
        watches = await get_all_watches()
        seen = set()

        for chat_id, username in watches:
            if username in seen:
                continue
            seen.add(username)

            if username in segment_tasks:
                continue

            print(f"Checking @{username}...")

            try:
                live, stream_url = await is_live(username)
            except Exception as e:
                print(f"Error cek @{username}: {e}")
                continue

            if live and stream_url:
                print(f"🔴 @{username} LIVE, mulai recording loop")
                task = asyncio.create_task(
                    recording_loop(app, username, stream_url)
                )
                segment_tasks[username] = task


# ── Main ─────────────────────────────────────────────

async def on_startup(app: Application) -> None:
    await asyncio.sleep(5)
    await init_db()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        check_all_lives,
        "interval",
        seconds=CHECK_INTERVAL,
        args=[app]
    )
    scheduler.start()
    print("🚀 Bot jalan...")

def main():
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(on_startup)
        .build()
    )
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("watch", cmd_watch))
    app.add_handler(CommandHandler("unwatch", cmd_unwatch))
    app.add_handler(CommandHandler("list", cmd_list))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
