import os
import time
import subprocess
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
USERNAME = os.getenv("USERNAME")


def get_stream():
    try:
        cmd = [
            "yt-dlp",
            "--no-warnings",
            "-f", "best",
            "-g",
            f"https://www.tiktok.com/@{USERNAME}/live"
        ]

        stream = subprocess.check_output(cmd).decode().strip()

        if stream:
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
        "1200",
        "-c",
        "copy",
        filename
    ]

    print("Recording 20 menit...")
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


while True:
    try:
        print("Monitoring...")

        file = record()

        if file and os.path.exists(file):
            send_telegram(file)
            os.remove(file)

    except Exception as e:
        print("Error:", e)

    time.sleep(10)
