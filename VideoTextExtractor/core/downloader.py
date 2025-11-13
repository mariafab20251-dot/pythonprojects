import yt_dlp
from pathlib import Path
from config import VIDEOS_DIR, MAX_RETRIES
import os

class VideoDownloader:
    def __init__(self, platform):
        self.platform = platform
        self.output_dir = VIDEOS_DIR / platform
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cookies_file = VIDEOS_DIR.parent / "cookies.txt"

    def download(self, url, video_id):
        output_path = self.output_dir / f"{video_id}.mp4"

        if output_path.exists():
            return str(output_path)

        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': str(output_path.with_suffix('')),
            'quiet': True,
            'no_warnings': True,
            'retries': MAX_RETRIES,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        }

        # Add cookies if file exists
        if self.cookies_file.exists():
            ydl_opts['cookiefile'] = str(self.cookies_file)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # Handle extension variations
            for ext in ['.mp4', '.mkv', '.webm']:
                potential_path = output_path.with_suffix(ext)
                if potential_path.exists():
                    if ext != '.mp4':
                        potential_path.rename(output_path)
                    return str(output_path)

            return None
        except Exception as e:
            error_msg = str(e).lower()
            if 'login' in error_msg or '401' in error_msg or 'unauthorized' in error_msg:
                raise Exception(
                    f"Authentication required for {self.platform}. "
                    f"Please add cookies.txt file. See INSTAGRAM_AUTH.md for instructions."
                )
            raise Exception(f"Download failed: {str(e)}")
