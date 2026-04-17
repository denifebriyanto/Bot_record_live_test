import os
import time
import subprocess
import requests
import json
import re

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
USERNAME = os.getenv("USERNAME")

last_update_id = None


def install_ffmpeg():
    try:
        subprocess.run(
            "apt-get update && apt-get install -y ffmpeg",
            shell=True
        )
        print("FFMPEG Installed")
    except:
        print("Install ffmpeg gagal")


def get_stream():
    try:
        url = f"https://www.tiktok.com/@{USERNAME}/live"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(url, headers=headers)

        sigi = re.search(
            r'<script id="SIGI_STATE".*?>(.*?)</script>',
            r.text
        )

        if not sigi:
            print("Belum live...")
            return None

        data = json.loads(sigi.group(1))

        room = data["LiveRoom"]["liveRoomUserInfo"]["liveRoom"]["streamData"]["pull_data"]

        stream = json.loads(room)["stream_data"]["hls"]

        print("Stream ditemukan")

        return stream

    except Exception as e:
        print("Belum live...")

    return None


def record():

    stream = get_stream()

    if not stream:
        return None

    filename = f"record_{int(time.time())}.mp4"

    command = [
        "ffmpeg",
        "-loglevel", "error",
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


def check_command():

    global last_update_id
    global USERNAME

    try:

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        r = requests.get(url).json()

        if "result" not in r:
            return

        if not r["result"]:
            return

        update = r["result"][-1]

        if last_update_id == update["update_id"]:
            return

        last_update_id = update["update_id"]

        if "message" in update:

            text = update["message"].get("text", "")

            if text == "/status":
                send_message("Bot aktif")

            elif text.startswith("/setuser"):

                new_user = text.split(" ")[1]

                USERNAME = new_user

                send_message(f"Ganti user ke @{USERNAME}")

    except:
        pass


def send_message(text):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": text
        }
    )


install_ffmpeg()

while True:

    try:

        print("Monitoring...")

        check_command()

        file = record()

        if file and os.path.exists(file):

            send_telegram(file)

            os.remove(file)

    except Exception as e:

        print("Error:", e)

    time.sleep(10)
