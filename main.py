import requests
import time
import os
import subprocess
import threading

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

USERNAME = "seccfia1"
STOP_RECORD = False


def check_live():
    url = f"https://www.tiktok.com/@{USERNAME}/live"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    return "live" in r.text.lower()


def record_live(duration=1200):  # 1200 = 20 menit
    global STOP_RECORD

    filename = f"{USERNAME}_{int(time.time())}.mp4"
    url = f"https://www.tiktok.com/@{USERNAME}/live"

    process = subprocess.Popen([
        "yt-dlp",
        "-o", filename,
        url
    ])

    start = time.time()

    while True:
        if STOP_RECORD:
            process.terminate()
            STOP_RECORD = False
            return None

        if time.time() - start > duration:
            process.terminate()
            return filename

        time.sleep(1)


async def set_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global USERNAME, STOP_RECORD
    STOP_RECORD = True

    if len(context.args) == 0:
        await update.message.reply_text("Gunakan: /set username")
        return

    USERNAME = context.args[0]

    await update.message.reply_text(
        f"🎯 Target diganti ke @{USERNAME}"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📡 Monitoring: @{USERNAME}"
    )


def monitor(app):
    global USERNAME

    while True:
        try:
            if check_live():
                app.bot.send_message(
                    chat_id=CHAT_ID,
                    text=f"🔴 @{USERNAME} sedang LIVE\n🎥 Mulai record 20 menit..."
                )

                file = record_live(1200)

                if file:
                    app.bot.send_document(
                        chat_id=CHAT_ID,
                        document=open(file, "rb")
                    )

                    os.remove(file)

                time.sleep(10)

            time.sleep(30)

        except Exception as e:
            print("Error:", e)
            time.sleep(60)


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("set", set_user))
    app.add_handler(CommandHandler("status", status))

    thread = threading.Thread(target=monitor, args=(app,))
    thread.start()

    app.run_polling()


if __name__ == "__main__":
    main()
