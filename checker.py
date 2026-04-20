import asyncio
from TikTokLive import TikTokLiveClient

async def is_live(username: str):
    client = TikTokLiveClient(unique_id=f"@{username}")
    try:
        room_info = await client.fetch_room_info()
        status = room_info.get("data", {}).get("status") or room_info.get("status")
        print(f"🔍 @{username} status: {status}")

        if status != 4:
            print(f"⭕ @{username} tidak live")
            return False, None

        stream_url_data = (
            room_info.get("data", {}).get("stream_url") or
            room_info.get("stream_url") or {}
        )

        hls = (
            stream_url_data.get("hls_pull_url") or
            stream_url_data.get("hls_pull_url_map", {}).get("SD1") or
            stream_url_data.get("hls_pull_url_map", {}).get("LD") or
            stream_url_data.get("rtmp_pull_url")
        )

        if hls:
            print(f"✅ @{username} LIVE url: {hls[:60]}...")
            return True, hls
        else:
            print(f"✅ @{username} LIVE (fallback)")
            return True, f"https://www.tiktok.com/@{username}/live"

    except Exception as e:
        print(f"❌ Checker error @{username}: {e}")
        return False, None
