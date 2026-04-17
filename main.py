import os
import time
import subprocess
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
USERNAME = os.getenv("pandaganjaya")

def get_stream():
    cmd = [
        "yt-dlp",
        "-g",
        f"https://www.tiktok.com/@{USERNAME}/live"
    ]
    
    try:
        stream = subprocess.check_output(cmd).decode().strip()
        return stream
    except:
        return None


def record():
    stream = get_stream()
    
    if not stream:
        print("Belum live...")
        return None

    filename = f"record_{int(time.time())}.mp4"

    command = [
        "ffmpeg",
        "-i",
        stream,
        "-t",
        "1200",
        "-c",
        "copy",
        filename
    ]

    subprocess.run(command)

    return filename


def send_telegram(file):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"

    with open(file, "rb") as f:
        requests.post(
            url,
            data={"chat_id": CHAT_ID},
            files={"video": f}
        )


while True:
    try:
        print("Monitoring...")

        file = record()

        if file and os.path.exists(file):
            print("Kirim Telegram...")
            send_telegram(file)
            os.remove(file)

    except Exception as e:
        print("Error:", e)

    time.sleep(10)
