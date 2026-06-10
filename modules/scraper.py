"""Channel scraper using yt-dlp to extract all video URLs from a YouTube channel."""

import re
import yt_dlp
from typing import List, Dict


def _normalize_channel_url(channel_url: str) -> str:
    """
    If the URL points to a channel root page, redirect to its /videos tab
    so we get actual video entries instead of channel tabs.
    """
    url = channel_url.strip()
    # If it already points to a specific tab or playlist, leave it alone
    if any(url.endswith(tab) for tab in ["/videos", "/shorts", "/streams", "/live"]):
        return url
    if "/playlist?" in url or "/watch?" in url:
        return url
    # Channel-style URLs: @handle, /channel/ID, /c/name, /user/name
    if re.search(r"youtube\.com/(@|channel/|c/|user/)", url):
        return url.rstrip("/") + "/videos"
    return url


def _extract_entries(entries) -> List[Dict]:
    """Flatten yt-dlp entries, handling nested playlists (channel tabs)."""
    videos = []
    for entry in entries:
        if entry is None:
            continue
        # Nested playlist (e.g., channel tab)
        if entry.get("_type") == "playlist" and "entries" in entry:
            videos.extend(_extract_entries(entry["entries"]))
            continue
        # Actual video / URL entry
        video_id = entry.get("id")
        title = entry.get("title", "")
        duration = entry.get("duration")
        if video_id and not video_id.startswith("UC"):  # Skip channel IDs
            videos.append({
                "video_id": video_id,
                "title": title,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "duration": duration,
            })
    return videos


def get_channel_videos(channel_url: str) -> List[Dict]:
    """
    Extract all video URLs and metadata from a YouTube channel URL.

    Args:
        channel_url: YouTube channel URL (e.g., https://www.youtube.com/@channel)

    Returns:
        List of dicts with keys: video_id, title, url, duration
    """
    url = _normalize_channel_url(channel_url)

    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
        # No playlistend limit — fetch everything
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    if info is None:
        return []

    entries = info.get("entries", [])
    return _extract_entries(entries)
