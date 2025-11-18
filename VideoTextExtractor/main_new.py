import tkinter as tk
import sys
import os
import re
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from gui.dashboard_new import Dashboard  # Use new dashboard
from core.database import VideoDatabase
from core.downloader import VideoDownloader
from core.extractor import MediaExtractor
from core.exporter import DataExporter
from platforms.instagram import InstagramScraper
from platforms.tiktok import TikTokScraper
from platforms.youtube import YouTubeScraper
from platforms.facebook import FacebookScraper
from datetime import datetime

class VideoProcessor:
    def __init__(self):
        self.db = VideoDatabase()
        self.extractor = MediaExtractor()
        self.exporter = DataExporter()
        self.scrapers = {
            'instagram': InstagramScraper(),
            'tiktok': TikTokScraper(),
            'youtube': YouTubeScraper(),
            'facebook': FacebookScraper()
        }
        self.current_channel_folder = None

    def extract_channel_name(self, url_input, platform):
        """Extract channel/profile name from URL"""
        import re

        if platform == 'youtube':
            if 'youtube.com/@' in url_input:
                match = re.search(r'youtube\.com/@([^/?]+)', url_input)
                if match:
                    return match.group(1)
            elif 'youtube.com/c/' in url_input:
                match = re.search(r'youtube\.com/c/([^/?]+)', url_input)
                if match:
                    return match.group(1)
            elif 'youtube.com/channel/' in url_input:
                match = re.search(r'youtube\.com/channel/([^/?]+)', url_input)
                if match:
                    return match.group(1)[:20]

        elif platform == 'instagram':
            if 'instagram.com' in url_input and '/reel/' not in url_input and '/p/' not in url_input:
                username = url_input.split('/')[-1] or url_input.split('/')[-2]
                return username

        elif platform == 'facebook':
            if 'facebook.com' in url_input:
                match = re.search(r'facebook\.com/([^/?]+)', url_input)
                if match:
                    return match.group(1)

        elif platform == 'tiktok':
            if 'tiktok.com/@' in url_input:
                match = re.search(r'tiktok\.com/@([^/?]+)', url_input)
                if match:
                    return match.group(1)

        return None

    def setup_channel_folder(self, channel_name, platform):
        """Create folder structure for channel"""
        from pathlib import Path
        from config import BASE_DIR

        if not channel_name:
            return None

        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', channel_name)
        safe_name = safe_name[:50]

        channel_folder = BASE_DIR / "channels" / platform / safe_name
        channel_folder.mkdir(parents=True, exist_ok=True)

        videos_folder = channel_folder / "videos"
        reports_folder = channel_folder / "reports"
        videos_folder.mkdir(exist_ok=True)
        reports_folder.mkdir(exist_ok=True)

        return channel_folder

    def parse_input(self, url_input, platform):
        if ',' in url_input:
            urls = [url.strip() for url in url_input.split(',')]
            channel_name = self.detect_channel_from_urls(urls, platform)
            if channel_name:
                self.current_channel_folder = self.setup_channel_folder(channel_name, platform)
            else:
                self.current_channel_folder = None
            return urls

        scraper = self.scrapers[platform]
        channel_name = self.extract_channel_name(url_input, platform)
        if channel_name:
            self.current_channel_folder = self.setup_channel_folder(channel_name, platform)

        if platform == 'instagram' and 'instagram.com' in url_input and '/reel/' not in url_input and '/p/' not in url_input:
            username = url_input.split('/')[-1] or url_input.split('/')[-2]
            return scraper.get_all_videos_from_profile(username)

        if platform == 'youtube' and ('youtube.com/channel/' in url_input or 'youtube.com/@' in url_input or 'youtube.com/c/' in url_input):
            return scraper.get_all_videos_from_channel(url_input)

        self.current_channel_folder = None
        return [url_input]

    def detect_channel_from_urls(self, urls, platform):
        """Detect if all URLs belong to the same channel"""
        if not urls:
            return None

        channel_names = set()

        for url in urls[:10]:
            if platform == 'youtube':
                return None

            elif platform == 'instagram':
                match = re.search(r'instagram\.com/([^/]+)/(?:reel|p|tv)/', url)
                if match:
                    username = match.group(1)
                    if username not in ['reel', 'p', 'tv']:
                        channel_names.add(username)

            elif platform == 'tiktok':
                match = re.search(r'tiktok\.com/@([^/]+)/', url)
                if match:
                    channel_names.add(match.group(1))

            elif platform == 'facebook':
                match = re.search(r'facebook\.com/([^/]+)/', url)
                if match:
                    channel_names.add(match.group(1))

        if len(channel_names) == 1:
            return channel_names.pop()

        return None

    def process_video(self, url, platform, log_callback, force_reprocess=False, download_video=True):
        if self.db.is_processed(url) and not force_reprocess:
            log_callback(f"⏭️ Skipping (already processed): {url}")
            return "skipped"

        video_path = None
        try:
            scraper = self.scrapers[platform]
            video_id, captions, hashtags = scraper.get_post_metadata(url)

            if not video_id:
                raise Exception("Could not extract video ID")

            overlay_text = ""
            speech_text = ""

            if download_video:
                log_callback(f"📥 Downloading video {video_id}...")
                downloader = VideoDownloader(platform, channel_folder=self.current_channel_folder)
                video_path = downloader.download(url, video_id)

                if not video_path or not os.path.exists(video_path):
                    raise Exception("Download failed")

                log_callback(f"🔍 Extracting overlay text...")
                overlay_text = self.extractor.extract_overlay_text(video_path, video_id)

                log_callback(f"🎤 Transcribing speech...")
                speech_text = self.extractor.extract_speech(video_path)
            else:
                log_callback(f"📝 Extracting metadata only (video download skipped)...")

            self.exporter.save_results(
                video_id, url, platform, overlay_text,
                speech_text, captions, hashtags,
                channel_folder=self.current_channel_folder
            )

            self.db.mark_processed(url)
            log_callback(f"✅ Completed: {video_id}")

            return "success"

        except Exception as e:
            log_callback(f"❌ Failed {url}: {str(e)}")
            if video_path and os.path.exists(video_path):
                try:
                    os.remove(video_path)
                except:
                    pass
            raise

    def process_local_video(self, video_path, log_callback):
        try:
            video_id = Path(video_path).stem
            log_callback(f"🔍 Extracting overlay text...")
            overlay_text = self.extractor.extract_overlay_text(video_path, video_id)

            log_callback(f"🎤 Transcribing speech...")
            speech_text = self.extractor.extract_speech(video_path)

            self.exporter.save_results(
                video_id, video_path, "local", overlay_text,
                speech_text, "", ""
            )

            log_callback(f"✅ Completed: {video_id}")
            return "success"

        except Exception as e:
            log_callback(f"❌ Failed: {str(e)}")
            raise

if __name__ == "__main__":
    root = tk.Tk()
    processor = VideoProcessor()
    app = Dashboard(root, processor)
    root.mainloop()
