import asyncio
import aiohttp

async def is_live(username: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.tiktok.com/",
        "Accept": "application/json",
    }
    url = f"https://www.tiktok.com/@{username}/live"

    try:
        async with aiohttp.ClientSession() as session:
            # Step 1: ambil room_id dari halaman live
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15), allow_redirects=True) as resp:
                html = await resp.text()

                # Cek apakah live
                if "LiveRoom" not in html and "liveRoom" not in html:
                    print(f"⭕ @{username} tidak live (no liveRoom)")
                    return False, None

                # Ambil stream url langsung dari HTML
                import re
                # Cari HLS url
                match = re.search(r'(https://[^"\'\\]+\.m3u8[^"\'\\]*)', html)
                if match:
                    hls = match.group(1)
                    print(f"✅ @{username} LIVE: {hls[:60]}...")
                    return True, hls

                # Cari room_id untuk fallback
                room_match = re.search(r'"roomId"\s*:\s*"?(\d+)"?', html)
                if room_match:
                    room_id = room_match.group(1)
                    print(f"✅ @{username} LIVE room_id: {room_id}")
                    # Ambil stream url via webcast API
                    api_url = f"https://webcast.tiktok.com/webcast/room/info/?room_id={room_id}"
                    async with session.get(api_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as api_resp:
                        data = await api_resp.json(content_type=None)
                        print(f"🔍 webcast raw: {str(data)[:200]}")
                        stream = data.get("data", {}).get("stream_url", {})
                        hls = (
                            stream.get("hls_pull_url") or
                            stream.get("hls_pull_url_map", {}).get("SD1") or
                            stream.get("rtmp_pull_url")
                        )
                        if hls:
                            print(f"✅ @{username} LIVE url: {hls[:60]}...")
                            return True, hls

                print(f"✅ @{username} LIVE (fallback)")
                return True, f"https://www.tiktok.com/@{username}/live"

    except Exception as e:
        print(f"❌ Checker error @{username}: {e}")
        return False, None
