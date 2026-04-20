import asyncio

async def is_live(username):

    url = f"https://www.tiktok.com/@{username}/live"

    try:
        proc = await asyncio.create_subprocess_exec(
            "streamlink",
            url,
            "best",
            "--stream-url",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await proc.communicate()

        if proc.returncode == 0:
            stream_url = stdout.decode().strip()

            if stream_url:
                return True, stream_url

    except Exception as e:
        print("Checker error:", e)

    return False, None
