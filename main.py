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

os.makedirs("recordings", exist_ok=True)


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

    text = "📋 Watchlist:\n"
    for u in watches:
        text += f"• @{u}\n"

    await update.message.reply_text(text)


# ── Scheduler cek live ───────────────────────────────

async def check_all_lives(app: Application):
    watches = await get_all_watches()
    seen = set()

    for chat_id, username in watches:

        if username in seen:
            continue

        seen.add(username)

        print(f"Checking @{username}...")

        try:
            live, stream_url = await is_live(username)
        except Exception as e:
            print(f"Retry @{username}: {e}")
            await asyncio.sleep(5)
            continue

        # Jika Live
        if live and not is_recording(username):

            print(f"🔴 @{username} LIVE")

            filename = await start_recording(username, stream_url)

            for cid, uname in watches:
                if uname == username:
                    await app.bot.send_message(
                        cid,
                        f"🔴 @{username} LIVE\n🎥 Mulai Rekam..."
                    )

        # Jika Live Berhenti
        elif not live and is_recording(username):

            print(f"⏹️ @{username} selesai")

            filename = await stop_recording(username)

            for cid, uname in watches:
                if uname == username:

                    try:
                        await app.bot.send_document(
                            cid,
                            document=open(filename, "rb"),
                            caption=f"✅ Rekaman @{username} selesai"
                        )

                        os.remove(filename)

                    except Exception as e:
                        print("Send file error:", e)

                        await app.bot.send_message(
                            cid,
                            f"✅ Rekaman selesai\nFile: {filename}"
                        )


# ── Main ─────────────────────────────────────────────

async def main():

    await init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("watch", cmd_watch))
    app.add_handler(CommandHandler("unwatch", cmd_unwatch))
    app.add_handler(CommandHandler("list", cmd_list))

    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        check_all_lives,
        "interval",
        seconds=CHECK_INTERVAL,
        args=[app]
    )

    scheduler.start()

    print("🚀 Bot jalan...")

    await app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
