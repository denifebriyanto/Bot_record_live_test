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
        "-i", stream_url,
        "-t", str(duration),
        "-c", "copy",
        "-movflags", "frag_keyframe+empty_moov",
        filename
    ]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL
    )
    active_recordings[username] = (process, filename)
    print(f"🎥 Mulai rekam @{username}")
    return filename

async def stop_recording(username: str) -> str | None:
    if username not in active_recordings:
        return None
    process, filename = active_recordings.pop(username)
    process.terminate()
    await process.wait()
    print(f"🛑 Stop rekam @{username}")
    return filename

def is_recording(username: str) -> bool:
    return username in active_recordings
