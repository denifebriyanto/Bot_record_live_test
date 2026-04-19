from TikTokLive import TikTokLiveClient
from TikTokLive.client.errors import UserOfflineError, UserNotFoundError

async def is_live(username: str):
    try:
        client = TikTokLiveClient(unique_id=username)
        await client.retrieve_room_info()

        if client.room_info and client.room_info.get("status") == 4:
            stream_url = await get_stream_url(client)
            return True, stream_url

        return False, None

    except UserOfflineError:
        return False, None
    except UserNotFoundError:
        return False, None
    except Exception as e:
        print(f"Error cek @{username}: {e}")
        return False, None


async def get_stream_url(client):
    try:
        info = client.room_info

        stream = info.get("stream_url", {})

        hls = (
            stream.get("hls_pull_url")
            or stream.get("hls_pull_url_map", {}).get("SD1")
        )

        return hls

    except Exception:
        return None
