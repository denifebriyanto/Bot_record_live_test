import os
import time
import subprocess
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
USERNAME = os.getenv("USERNAME")

DURATION = 600
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
        cmd = [
            "yt-dlp",
            "--no-warnings",
            "--user-agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
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
        str(DURATION),
        "-c",
        "copy",
        filename
    ]

    print(f"Recording {DURATION} detik...")
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


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": text
        }
    )


def check_command():
    global last_update_id, USERNAME, DURATION

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    r = requests.get(url).json()

    if not r["result"]:
        return

    update = r["result"][-1]

    if last_update_id == update["update_id"]:
        return

    last_update_id = update["update_id"]

    if "message" in update:
        text = update["message"].get("text", "")

        if text == "/status":
            send_message(
                f"Bot aktif\nUser: {USERNAME}\nDurasi: {DURATION//60} menit"
            )

        elif text == "/user":
            send_message(f"User sekarang: {USERNAME}")

        elif text.startswith("/setuser"):
            try:
                new_user = text.split(" ")[1]
                USERNAME = new_user
                send_message(f"User diganti ke: {USERNAME}")
            except:
                send_message("Format: /setuser username")

        elif text.startswith("/duration"):
            try:
                menit = int(text.split(" ")[1])
                DURATION = menit * 60
                send_message(f"Durasi diganti: {menit} menit")
            except:
                send_message("Format: /duration 10")

        elif text == "/restart":
            send_message("Restart recording...")


install_ffmpeg()

while True:
    try:
        check_command()

        print("Monitoring...")

        file = record()

        if file and os.path.exists(file):
            send_telegram(file)
            os.remove(file)

    except Exception as e:
        print("Error:", e)

    time.sleep(10)
