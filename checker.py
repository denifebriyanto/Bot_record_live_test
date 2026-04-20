import asyncio
import aiohttp
import re

async def is_live(username: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.tiktok.com/",
        "Accept": "application/json",
    }
    url = f"https://www.tiktok.com/@{username}/live"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15), allow_redirects=True) as resp:
                html = await resp.text()

                if "LiveRoom" not in html and "liveRoom" not in html:
                    print(f"⭕ @{username} tidak live")
                    return False, None

                # Cari HLS url langsung dari HTML
                match = re.search(r'(https://[^"\'\\]+\.m3u8[^"\'\\]*)', html)
                if match:
                    hls = match.group(1)
                    print(f"✅ @{username} LIVE: {hls[:60]}...")
                    return True, hls

                # Fallback: ambil room_id lalu hit webcast API
                room_match = re.search(r'"roomId"\s*:\s*"?(\d+)"?', html)
                if not room_match:
                    print(f"✅ @{username} LIVE (no room_id, fallback)")
                    return True, f"https://www.tiktok.com/@{username}/live"

                room_id = room_match.group(1)
                print(f"✅ @{username} LIVE room_id: {room_id}")

                # Coba beberapa endpoint webcast
                endpoints = [
                    f"https://webcast.tiktok.com/webcast/room/info/?room_id={room_id}&aid=1988",
                    f"https://www.tiktok.com/api/live/detail/?aid=1988&roomID={room_id}",
                ]

                for endpoint in endpoints:
                    try:
                        async with session.get(endpoint, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as api_resp:
                            text = await api_resp.text()
                            print(f"🔍 endpoint raw: {text[:200]}")

                            import json
                            try:
                                data = json.loads(text)
                            except Exception:
                                continue

                            if data is None:
                                continue

                            stream = (
                                data.get("data", {}).get("stream_url") or
                                data.get("LiveRoomInfo", {}).get("stream_url") or
                                {}
                            )
                            hls = (
                                stream.get("hls_pull_url") or
                                stream.get("hls_pull_url_map", {}).get("SD1") or
                                stream.get("rtmp_pull_url")
                            )
                            if hls:
                                print(f"✅ stream url: {hls[:60]}...")
                                return True, hls
                    except Exception as e:
                        print(f"⚠️ endpoint error: {e}")
                        continue

                # Kalau semua endpoint gagal, pakai streamlink sebagai fallback
                print(f"✅ @{username} LIVE (fallback url)")
                return True, f"https://www.tiktok.com/@{username}/live"

    except Exception as e:
        print(f"❌ Checker error @{username}: {e}")
        return False, None
