import os
import time
import subprocess
import requests
import json

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
USERNAME = os.getenv("USERNAME")

ROOM_ID = None


def install_ffmpeg():
    try:
        subprocess.run(
            "apt-get update && apt-get install -y ffmpeg",
            shell=True
        )
        print("FFMPEG Installed")
    except:
        print("Install ffmpeg gagal")


def get_room():

    global ROOM_ID

    try:

        url = f"https://www.tiktok.com/@{USERNAME}/live"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(url, headers=headers)

        if "roomId" in r.text:

            room = r.text.split('"roomId":"')[1].split('"')[0]

            ROOM_ID = room

            print("Room ID:", ROOM_ID)

            return True

    except:
        pass

    return False


def get_stream():

    global ROOM_ID

    try:

        url = f"https://webcast.tiktok.com/webcast/room/info/?room_id={ROOM_ID}"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(url, headers=headers).json()

        stream = r["data"]["stream_url"]["hls_pull_url"]

        print("Stream ditemukan")

        return stream

    except:

        print("Belum live...")

    return None


def record():

    stream = get_stream()

    if not stream:
        return None

    filename = f"record_{int(time.time())}.mp4"

    command = [
        "ffmpeg",
        "-loglevel",
        "error",
        "-i",
        stream,
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


install_ffmpeg()

while True:

    try:

        print("Monitoring...")

        if not ROOM_ID:
            get_room()

        file = record()

        if file and os.path.exists(file):

            send_telegram(file)

            os.remove(file)

    except Exception as e:

        print("Error:", e)

    time.sleep(10)
