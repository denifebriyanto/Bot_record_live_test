import asyncio
from TikTokLive import TikTokLiveClient
from TikTokLive.client.errors import AlreadyConnectedError

async def is_live(username: str):
    client = TikTokLiveClient(unique_id=f"@{username}")
    try:
        await client.retrieve_room_info()
        room = client.room_info or {}

        # status 4 = sedang live
        status = room.get("status")
        print(f"🔍 @{username} status: {status}")

        if status != 4:
            print(f"⭕ @{username} tidak live")
            return False, None

        stream_data = room.get("stream_url") or {}
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
