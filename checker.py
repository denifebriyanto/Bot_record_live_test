import asyncio
from TikTokLive import TikTokLiveClient
from TikTokLive.client.errors import UserOfflineError, UserNotFoundError

async def is_live(username: str):
    client = TikTokLiveClient(unique_id=f"@{username}")
    try:
        # Cek status live
        is_online = await client.is_live()
        
        if not is_online:
            print(f"⭕ @{username} tidak live")
            return False, None

        # Ambil stream URL
        await client.retrieve_room_info()
        room = client.room_info or {}

        # Coba ambil HLS url dari berbagai key
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
            # Live tapi URL tidak ketangkap, pakai fallback ffmpeg langsung
            fallback = f"https://www.tiktok.com/@{username}/live"
            print(f"✅ @{username} LIVE (fallback url)")
            return True, fallback

    except UserOfflineError:
        print(f"⭕ @{username} offline")
        return False, None
    except UserNotFoundError:
        print(f"❌ @{username} tidak ditemukan")
        return False, None
    except Exception as e:
        print(f"❌ Checker error @{username}: {e}")
        return False, None
