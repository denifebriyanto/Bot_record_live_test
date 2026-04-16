import asyncio
import requests
import time
import os
import subprocess
from telegram import Bot

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
USERNAME = "arvianetha"

bot = Bot(token=TOKEN)

def check_live():
    url = f"https://www.tiktok.com/@{USERNAME}/live"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
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

async def main():
    while True:
        try:
            if check_live():
                await bot.send_message(
                    chat_id=CHAT_ID,
                    text=f"🔴 @{USERNAME} sedang LIVE - Recording..."
                )

                file = record_live()

                await bot.send_document(
                    chat_id=CHAT_ID,
                    document=open(file, "rb")
                )

                time.sleep(600)

            time.sleep(30)

        except Exception as e:
            print(e)
            time.sleep(60)

asyncio.run(main())
