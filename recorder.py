import asyncio
import os
from datetime import datetime

SAVE_DIR = "/tmp/recordings"
active_recordings = {}

async def start_recording(username: str, stream_url: str, duration: int = 300) -> str | None:
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
        "-i", stream_url,
        "-t", str(duration),
        "-c:v", "copy",
        "-c:a", "aac",
        "-bsf:a", "aac_adtstoasc",
        filename
    ]
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
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
    except Exception:
        pass
    try:
        await asyncio.wait_for(process.wait(), timeout=10)
    except asyncio.TimeoutError:
        try:
            process.kill()
            await process.wait()
        except Exception:
            pass
    except Exception:
        pass
    print(f"🛑 Stop rekam @{username} -> {filename}")
    if os.path.exists(filename):
        size = os.path.getsize(filename)
        print(f"📦 File size: {size} bytes")
    else:
        print(f"❌ File tidak ada: {filename}")
    return filename

def is_recording(username: str) -> bool:
    return username in active_recordings
