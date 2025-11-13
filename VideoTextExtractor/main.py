import tkinter as tk
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from gui.dashboard import Dashboard
from core.database import VideoDatabase
from core.downloader import VideoDownloader
from core.extractor import MediaExtractor
from core.exporter import DataExporter
from platforms.instagram import InstagramScraper
from datetime import datetime

class VideoProcessor:
    def __init__(self):
        self.db = VideoDatabase()
        self.extractor = MediaExtractor()
        self.exporter = DataExporter()
        self.scrapers = {
            'instagram': InstagramScraper()
        }

    def parse_input(self, url_input, platform):
        if ',' in url_input:
            return [url.strip() for url in url_input.split(',')]

        if 'instagram.com' in url_input and '/reel/' not in url_input and '/p/' not in url_input:
            username = url_input.split('/')[-1] or url_input.split('/')[-2]
            scraper = self.scrapers[platform]
            return scraper.get_all_videos_from_profile(username)

        return [url_input]

    def process_video(self, url, platform, log_callback):
        if self.db.is_processed(url):
            log_callback(f"⏭️ Skipping (already processed): {url}")
            return

        try:
            scraper = self.scrapers[platform]
            video_id, captions, hashtags = scraper.get_post_metadata(url)

            if not video_id:
                raise Exception("Could not extract video ID")

            log_callback(f"📥 Downloading video {video_id}...")
            downloader = VideoDownloader(platform)
            video_path = downloader.download(url, video_id)

            if not video_path:
                raise Exception("Download failed")

            log_callback(f"🔍 Extracting overlay text...")
            overlay_text = self.extractor.extract_overlay_text(video_path, video_id)

            log_callback(f"🎤 Transcribing speech...")
            speech_text = self.extractor.extract_speech(video_path)

            data = {
                'video_id': video_id,
                'platform': platform,
                'url': url,
                'overlay_text': overlay_text,
                'speech_text': speech_text,
                'captions': captions,
                'hashtags': hashtags,
                'timestamp': datetime.now().isoformat()
            }

            self.db.add_video(video_id, platform, url, overlay_text, speech_text, captions, hashtags)
            self.exporter.export_to_csv(data)
            self.exporter.export_to_json(data)

            log_callback(f"✅ Completed: {video_id}")

        except Exception as e:
            log_callback(f"❌ Failed {url}: {str(e)}")

def main():
    root = tk.Tk()
    processor = VideoProcessor()
    app = Dashboard(root, processor)
    root.mainloop()

if __name__ == "__main__":
    main()
