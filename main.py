import asyncio
import requests
import time
from telegram import Bot

TOKEN = "TOKEN_BOT_KAMU"
USERNAME = "arvianetha"

bot = Bot(token=TOKEN)

def check_live():
    url = f"https://www.tiktok.com/@{USERNAME}/live"
    r = requests.get(url)
    return "LIVE" in r.text

async def main():
    while True:
        if check_live():
            await bot.send_message(
                chat_id="YOUR_CHAT_ID",
                text=f"{USERNAME} sedang LIVE!"
            )
            time.sleep(600)
        time.sleep(30)

asyncio.run(main())
