import os
import time
import subprocess
import requests
import asyncio

from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, DisconnectEvent

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
USERNAME = os.getenv("USERNAME")

is_live = False


def install_ffmpeg():
    try:
        subprocess.run(
            "apt-get update && apt-get install -y ffmpeg",
            shell=True
        )
        print("FFMPEG Installed")
    except:
        print("Install ffmpeg gagal")


def record():

    global USERNAME

    filename = f"record_{int(time.time())}.mp4"

    url = f"https://www.tiktok.com/@{USERNAME}/live"

    command = [
        "ffmpeg",
        "-loglevel", "error",
        "-i",
        url,
        "-t",
        "600",
        "-c",
        "copy",
        filename
    ]

    print("Recording 10 menit...")
    subprocess.run(command)

    return filename


def send_telegram(file):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"

    with open(file, "rb") as video:
        requests.post(
            url,
            data={"chat_id": CHAT_ID},
            files={"video": video}
        )

    print("Video terkirim")


async def main():

    global is_live

    client = TikTokLiveClient(unique_id=USERNAME)


    @client.on(ConnectEvent)
    async def on_connect(event):
        global is_live
        is_live = True
        print("LIVE TERDETEKSI")


    @client.on(DisconnectEvent)
    async def on_disconnect(event):
        global is_live
        is_live = False
        print("Live selesai")


    while True:

        try:

            if not client.connected:
                await client.start()

            if is_live:

                file = record()

                if os.path.exists(file):
                    send_telegram(file)
                    os.remove(file)

        except Exception as e:
            print("Error:", e)

        await asyncio.sleep(10)


install_ffmpeg()

asyncio.run(main())
