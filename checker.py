import asyncio
import aiohttp

async def is_live(username: str):
    url = f"https://www.tiktok.com/api/live/detail/?aid=1988&uniqueId={username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.tiktok.com/",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                data = await resp.json(content_type=None)
                print(f"🔍 @{username} raw: {str(data)[:200]}")

                live_room = data.get("LiveRoomInfo") or data.get("data") or {}
                status = live_room.get("status")
                print(f"🔍 @{username} status: {status}")

                if status != 4:
                    print(f"⭕ @{username} tidak live")
                    return False, None

                stream_data = live_room.get("liveUrl") or ""
                if stream_data:
                    print(f"✅ @{username} LIVE: {stream_data[:60]}")
                    return True, stream_data

                print(f"✅ @{username} LIVE (fallback)")
                return True, f"https://www.tiktok.com/@{username}/live"

    except Exception as e:
        print(f"❌ Checker error @{username}: {e}")
        return False, None
