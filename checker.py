import asyncio
from TikTokLive import TikTokLiveClient

async def is_live(username: str):
    client = TikTokLiveClient(unique_id=f"@{username}")
    try:
        is_online = await client.is_live()

        if not is_online:
            print(f"⭕ @{username} tidak live")
            return False, None

        await client.retrieve_room_info()
        room = client.room_info or {}

        stream_data = room.get("stream_url") or room.get("streamData") or {}

        hls = (
            stream_data.get("hls_pull_url") or
            stream_data.get("hls_pull_url_map", {}).get("SD1") or
            stream_data.get("hls_pull_url_map", {}).get("LD") or
            stream_data.get("rtmp_pull_url")
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
