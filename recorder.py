import asyncio
import os
from datetime import datetime

SAVE_DIR = "recordings"
active_recordings = {}

async def start_recording(username: str, stream_url: str, duration: int = 600) -> str | None:
    if username in active_recordings:
        return None
    os.makedirs(SAVE_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{SAVE_DIR}/{username}_{timestamp}.mp4"
    cmd = [
        "ffmpeg",
        "-y",
        "-user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "-headers", "Referer: https://www.tiktok.com/\r\n",
        "-timeout", "10000000",
        "-reconnect", "1",
        "-reconnect_streamed", "1",
        "-reconnect_delay_max", "5",
        "-i", stream_url,
        "-t", str(duration),
        "-c", "copy",
        "-movflags", "frag_keyframe+empty_moov",
        filename
    ]
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        active_recordings[username] = (process, filename)
        print(f"🎥 Mulai rekam @{username} PID:{process.pid}")
        return filename
    except FileNotFoundError:
        print(f"❌ ffmpeg tidak ditemukan!")
        return None
    except Exception as e:
        print(f"❌ Error start recording: {e}")
        return None

async def stop_recording(username: str) -> str | None:
    if username not in active_recordings:
        return None
    process, filename = active_recordings.pop(username)
    try:
        process.terminate()
        stdout, stderr = await process.communicate()
        if stderr:
            print(f"🔍 ffmpeg: {stderr.decode()[-300:]}")
    except Exception as e:
        print(f"⚠️ Stop error: {e}")
    print(f"🛑 Stop rekam @{username} -> {filename}")
    return filename

def is_recording(username: str) -> bool:
    return username in active_recordings
