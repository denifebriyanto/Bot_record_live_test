import asyncio
from TikTokLive import TikTokLiveClient

async def is_live(username):
    try:
        client = TikTokLiveClient(unique_id=username)

        await client.start()

        stream_url = client.webcast.stream_url

        await client.disconnect()

        return True, stream_url

    except Exception:
        return False, None
