import yt_dlp
from pathlib import Path
from config import VIDEOS_DIR, MAX_RETRIES

class VideoDownloader:
    def __init__(self, platform):
        self.platform = platform
        self.output_dir = VIDEOS_DIR / platform
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download(self, url, video_id):
        output_path = self.output_dir / f"{video_id}.mp4"

        if output_path.exists():
            return str(output_path)

        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': str(output_path.with_suffix('')),
            'quiet': False,
            'no_warnings': False,
            'retries': MAX_RETRIES,
        }

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
            raise Exception(f"Download failed: {str(e)}")
