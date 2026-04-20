import asyncio
import aiohttp
import re

async def is_live(username: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    url = f"https://www.tiktok.com/@{username}/live"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                html = await resp.text()

                # Kalau ada stream URL di HTML, berarti lagi live
                match = re.search(r'"playUrl":"(https://[^"]+\.m3u8[^"]*)"', html)
                if match:
                    stream_url = match.group(1).replace("\\u0026", "&")
                    print(f"✅ @{username} LIVE, url: {stream_url[:60]}...")
                    return True, stream_url

                # Cek tanda live lainnya
                if '"statusCode":0' in html and 'liveRoom' in html:
                    # Live tapi stream URL tidak ketangkap, coba fallback
                    fallback = f"https://webcast.tiktok.com/webcast/room/info/?uniqueId={username}"
                    return True, fallback

    except asyncio.TimeoutError:
        print(f"⏱️ Timeout cek @{username}")
    except Exception as e:
        print(f"❌ Checker error @{username}: {e}")

    return False, None
