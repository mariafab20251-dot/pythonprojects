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

        print(f"[DEBUG] Attempting download for: {url}")
        print(f"[DEBUG] Output path: {output_path}")
        print(f"[DEBUG] Cookies file path: {self.cookies_file}")
        print(f"[DEBUG] Cookies file exists: {self.cookies_file.exists()}")

        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': str(output_path.with_suffix('')),
            'quiet': False,
            'no_warnings': False,
            'retries': MAX_RETRIES,
            'verbose': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        }

        # Add cookies if file exists
        if self.cookies_file.exists():
            ydl_opts['cookiefile'] = str(self.cookies_file)
            print(f"[DEBUG] Using cookies from: {self.cookies_file}")
        else:
            print(f"[DEBUG] WARNING: No cookies.txt found!")

        # Debug: Check cookies file
        cookies_exists = self.cookies_file.exists()

        try:
            print(f"[DEBUG] Starting yt-dlp download...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            print(f"[DEBUG] Download completed, checking for output files...")

            # Check for file without extension first (yt-dlp sometimes saves without extension)
            no_ext_path = output_path.with_suffix('')
            print(f"[DEBUG] Checking for file without extension: {no_ext_path}")
            if no_ext_path.exists():
                print(f"[DEBUG] Found file without extension, renaming to .mp4")
                no_ext_path.rename(output_path)
                return str(output_path)

            # Handle extension variations
            for ext in ['.mp4', '.mkv', '.webm']:
                potential_path = output_path.with_suffix(ext)
                print(f"[DEBUG] Checking for: {potential_path}")
                if potential_path.exists():
                    print(f"[DEBUG] Found file with extension: {ext}")
                    if ext != '.mp4':
                        potential_path.rename(output_path)
                    return str(output_path)

            print(f"[DEBUG] ERROR: No output file found after download!")
            return None
        except Exception as e:
            error_msg = str(e)
            print(f"[DEBUG] Exception occurred: {error_msg}")
            print(f"[DEBUG] Exception type: {type(e).__name__}")

            # Add cookies debug info
            if not cookies_exists:
                raise Exception(
                    f"Download failed: {error_msg}\n"
                    f"NOTE: cookies.txt not found at {self.cookies_file}\n"
                    f"Instagram requires authentication. See INSTAGRAM_AUTH.md"
                )

            # Check for auth errors
            if 'login' in error_msg.lower() or '401' in error_msg or 'unauthorized' in error_msg.lower():
                raise Exception(
                    f"Authentication failed: {error_msg}\n"
                    f"Your cookies may be expired. Re-export cookies.txt from browser."
                )

            raise Exception(f"Download failed: {error_msg}")
