import os
import time
import subprocess
import requests

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
        cmd = [
            "yt-dlp",
            "--no-warnings",
            "--impersonate", "chrome",
            "--geo-bypass",
            "--no-check-certificates",
            "--user-agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "-f",
            "best",
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
                send_message("Bot aktif dan monitoring")

            elif text == "/user":
                send_message(f"User: {USERNAME}")

            elif text.startswith("/setuser"):
                new_user = text.split(" ")[1]
                USERNAME = new_user
                send_message(f"Ganti user ke @{USERNAME}")

            elif text == "/restart":
                send_message("Restart recording...")

    except Exception as e:
        print("Command Error:", e)


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
