from pathlib import Path
from urllib.parse import urlparse, parse_qs

import yt_dlp


def extract_youtube_video_id(raw_url: str) -> str:
    """Return YouTube video id from various YouTube URL formats."""
    parsed = urlparse(raw_url)
    host = parsed.netloc.lower()
    if "youtube.com" in host:
        query = parse_qs(parsed.query)
        vid = query.get("v", [None])[0]
    elif "youtu.be" in host:
        vid = parsed.path.lstrip("/").split("/")[0]
    else:
        vid = None
    if not vid:
        raise ValueError("Could not extract video id from URL.")
    return vid


def build_canonical_youtube_url(video_id: str) -> str:
    """Return canonical YouTube watch URL for a given video id."""
    return f"https://www.youtube.com/watch?v={video_id}"


def download_youtube_audio(raw_url: str, output_dir: str = "tmp/audio") -> tuple[Path, str]:
    """Download best audio for a YouTube URL and return (file_path, canonical_url)."""
    video_id = extract_youtube_video_id(raw_url)
    canonical_url = build_canonical_youtube_url(video_id)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    tmp_pattern = str(output_path / f"{video_id}.%(ext)s")
    ydl_opts = {"format": "bestaudio/best", "outtmpl": tmp_pattern, "quiet": True, "noplaylist": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(canonical_url, download=True)
        audio_file = Path(ydl.prepare_filename(info))
    return audio_file, canonical_url