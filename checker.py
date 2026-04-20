import aiohttp

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

async def is_live(username):
    url = f"https://www.tiktok.com/@{username}/live"

    try:
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            async with session.get(url, timeout=15) as resp:

                if resp.status != 200:
                    return False, None

                text = await resp.text()

                # Detect live
                if "liveRoom" in text or "isLiveBroadcast" in text:
                    
                    # Cari stream url
                    if "flv_pull_url" in text:
                        start = text.find("flv_pull_url")
                        start = text.find("http", start)
                        end = text.find(".flv", start) + 4

                        stream_url = text[start:end]
                        return True, stream_url

                    return True, None

    except Exception as e:
        print("Checker error:", e)

    return False, None
