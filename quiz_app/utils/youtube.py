from urllib.parse import urlparse, parse_qs
from pathlib import Path
import tempfile

import yt_dlp


def extract_youtube_video_id(raw_url: str) -> str:
    """
    Extract the YouTube video ID from different URL formats.

    Supported examples:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID

    Raises:
        ValueError: If the URL is invalid or no video ID is found.
    """
    parsed = urlparse(raw_url)
    host = parsed.netloc.lower()
    path = parsed.path
    video_id = None

    if host in ("www.youtube.com", "youtube.com", "m.youtube.com"):
        query_params = parse_qs(parsed.query)
        video_id = query_params.get("v", [None])[0]
    elif host in ("youtu.be", "www.youtu.be"):
        video_id = path.lstrip("/")

    if not video_id:
        raise ValueError("Could not extract a YouTube video ID from the given URL.")
    return video_id


def build_canonical_youtube_url(video_id: str) -> str:
    """
    Build the canonical YouTube URL we store in the database.
    """
    return f"https://www.youtube.com/watch?v={video_id}"


def download_youtube_audio(raw_url: str) -> tuple[Path, str]:
    """
    Download the best audio stream of a YouTube video using yt_dlp.

    Returns:
        (audio_file_path, canonical_url)
    """
    video_id = extract_youtube_video_id(raw_url)
    canonical_url = build_canonical_youtube_url(video_id)

    tmp_dir = Path("tmp/audio")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_filename = str(tmp_dir / f"{video_id}.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": tmp_filename,
        "quiet": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(canonical_url, download=True)
        audio_file = Path(ydl.prepare_filename(info))

    return audio_file, canonical_url