import asyncio
import subprocess

async def is_live(username):
    url = f"https://www.tiktok.com/@{username}/live"

    try:
        process = await asyncio.create_subprocess_exec(
            "streamlink",
            "--stream-url",
            url,
            "best",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            stream_url = stdout.decode().strip()
            return True, stream_url

    except Exception as e:
        print("Checker error:", e)

    return False, None
