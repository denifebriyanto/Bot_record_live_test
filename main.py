import asyncio
import requests
import time
from telegram import Bot

TOKEN = "8577721420:AAH5QJ7QEOH11BLZJTo4x0kGUje0iDRr5BM"
CHAT_ID = "6185081742"
USERNAME = "arvianetha"

bot = Bot(token=TOKEN)

def check_live():
    url = f"https://www.tiktok.com/@{USERNAME}/live"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    r = requests.get(url, headers=headers)
    return "live" in r.text.lower()

async def main():
    while True:
        try:
            if check_live():
                await bot.send_message(
                    chat_id=CHAT_ID,
                    text=f"🔴 @{USERNAME} sedang LIVE sekarang!"
                )
                time.sleep(600)
            time.sleep(30)
        except Exception as e:
            print(e)
            time.sleep(60)

asyncio.run(main())
