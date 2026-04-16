import asyncio
import requests
import time
import os
import subprocess

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

USERNAME = "arvianetha"


def check_live():
    url = f"https://www.tiktok.com/@{USERNAME}/live"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    return "live" in r.text.lower()


def record_live():
    filename = f"{USERNAME}.mp4"
    url = f"https://www.tiktok.com/@{USERNAME}/live"

    command = [
        "yt-dlp",
        "-o", filename,
        url
    ]

    subprocess.run(command)

    return filename


async def set_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global USERNAME
    USERNAME = context.args[0]
    await update.message.reply_text(f"Target diganti ke @{USERNAME}")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Target sekarang: @{USERNAME}")


async def monitor(application):
    global USERNAME
    while True:
        try:
            if check_live():
                await application.bot.send_message(
                    chat_id=CHAT_ID,
                    text=f"🔴 @{USERNAME} sedang LIVE - Recording..."
                )

                file = record_live()

                await application.bot.send_document(
                    chat_id=CHAT_ID,
                    document=open(file, "rb")
                )

                time.sleep(600)

            time.sleep(30)

        except Exception as e:
            print(e)
            time.sleep(60)


async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("set", set_user))
    app.add_handler(CommandHandler("status", status))

    asyncio.create_task(monitor(app))

    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.get_event_loop().run_until_complete(main())
