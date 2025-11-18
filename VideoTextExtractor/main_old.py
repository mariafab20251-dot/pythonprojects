import tkinter as tk
import sys
import os
import re
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from gui.dashboard import Dashboard
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
            # youtube.com/@channelname or youtube.com/c/channelname
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
                    return match.group(1)[:20]  # Limit channel ID length

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

        # Sanitize channel name for folder
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', channel_name)
        safe_name = safe_name[:50]  # Limit length

        # Create channel folder
        channel_folder = BASE_DIR / "channels" / platform / safe_name
        channel_folder.mkdir(parents=True, exist_ok=True)

        # Create subfolders
        videos_folder = channel_folder / "videos"
        reports_folder = channel_folder / "reports"
        videos_folder.mkdir(exist_ok=True)
        reports_folder.mkdir(exist_ok=True)

        return channel_folder

    def parse_input(self, url_input, platform):
        # Handle comma-separated URLs
        if ',' in url_input:
            urls = [url.strip() for url in url_input.split(',')]

            # Try to detect if all URLs are from the same channel
            channel_name = self.detect_channel_from_urls(urls, platform)
            if channel_name:
                self.current_channel_folder = self.setup_channel_folder(channel_name, platform)
            else:
                self.current_channel_folder = None

            return urls

        scraper = self.scrapers[platform]

        # Check if this is a channel/profile URL
        channel_name = self.extract_channel_name(url_input, platform)
        if channel_name:
            self.current_channel_folder = self.setup_channel_folder(channel_name, platform)

        # Instagram profile
        if platform == 'instagram' and 'instagram.com' in url_input and '/reel/' not in url_input and '/p/' not in url_input:
            username = url_input.split('/')[-1] or url_input.split('/')[-2]
            return scraper.get_all_videos_from_profile(username)

        # YouTube channel
        if platform == 'youtube' and ('youtube.com/channel/' in url_input or 'youtube.com/@' in url_input or 'youtube.com/c/' in url_input):
            return scraper.get_all_videos_from_channel(url_input)

        # Single URL - no channel folder needed
        self.current_channel_folder = None
        return [url_input]

    def detect_channel_from_urls(self, urls, platform):
        """Detect if all URLs belong to the same channel"""
        if not urls:
            return None

        channel_names = set()

        for url in urls[:10]:  # Check first 10 URLs only
            if platform == 'youtube':
                # Extract channel from video URL
                # youtube.com/watch?v=xxx or youtube.com/shorts/xxx
                # We can't reliably extract channel from video URLs, so return None
                return None

            elif platform == 'instagram':
                # instagram.com/username/reel/xxx or instagram.com/reel/xxx
                # Try to extract username from URL
                match = re.search(r'instagram\.com/([^/]+)/(?:reel|p|tv)/', url)
                if match:
                    username = match.group(1)
                    # Make sure it's not 'reel', 'p', or 'tv' (direct format)
                    if username not in ['reel', 'p', 'tv']:
                        channel_names.add(username)

            elif platform == 'tiktok':
                # tiktok.com/@username/video/xxx
                match = re.search(r'tiktok\.com/@([^/]+)/', url)
                if match:
                    channel_names.add(match.group(1))

            elif platform == 'facebook':
                # facebook.com/username/videos/xxx
                match = re.search(r'facebook\.com/([^/]+)/', url)
                if match:
                    channel_names.add(match.group(1))

        # If all URLs have the same channel name, return it
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
                # Full processing with video download
                log_callback(f"📥 Downloading video {video_id}...")
                downloader = VideoDownloader(platform, channel_folder=self.current_channel_folder)
                video_path = downloader.download(url, video_id)

                if not video_path or not os.path.exists(video_path):
                    raise Exception("Download failed")

                log_callback(f"🔍 Extracting overlay text...")
                try:
                    overlay_text = self.extractor.extract_overlay_text(video_path, video_id)
                except Exception as e:
                    log_callback(f"⚠️ OCR failed: {str(e)}")
                    overlay_text = ""

                log_callback(f"🎤 Transcribing speech...")
                try:
                    speech_text = self.extractor.extract_speech(video_path)
                except Exception as e:
                    log_callback(f"⚠️ Whisper failed: {str(e)}")
                    speech_text = ""
            else:
                # Metadata-only mode (no download)
                log_callback(f"📝 Extracting metadata only (video download skipped)...")

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
            self.exporter.export_to_csv(data, channel_folder=self.current_channel_folder)
            self.exporter.export_to_json(data, channel_folder=self.current_channel_folder)
            self.exporter.export_to_txt(data, channel_folder=self.current_channel_folder)

            if self.current_channel_folder:
                log_callback(f"✅ Completed: {video_id} (saved to channel folder)")
            else:
                log_callback(f"✅ Completed: {video_id}")

        except Exception as e:
            log_callback(f"❌ Failed {url}: {str(e)}")
            raise

        finally:
            # Cleanup temp files
            if video_path and os.path.exists(video_path) and not self._keep_videos():
                try:
                    os.remove(video_path)
                    log_callback(f"🗑️ Cleaned up video file")
                except:
                    pass

    def _keep_videos(self):
        from config import KEEP_VIDEOS
        return KEEP_VIDEOS

    def process_local_video(self, video_path, log_callback):
        """Process a local video file without downloading"""
        import hashlib
        import re
        from pathlib import Path

        try:
            video_file = Path(video_path)
            if not video_file.exists():
                raise Exception(f"Video file not found: {video_path}")

            # Generate safe video ID from filename
            original_name = video_file.stem  # filename without extension

            # Sanitize: remove special chars, limit length
            safe_id = re.sub(r'[^a-zA-Z0-9_-]', '_', original_name)
            safe_id = re.sub(r'_+', '_', safe_id)  # Replace multiple underscores
            safe_id = safe_id.strip('_')  # Remove leading/trailing underscores

            # Limit to 50 chars and add hash for uniqueness
            file_hash = hashlib.md5(original_name.encode()).hexdigest()[:8]
            if len(safe_id) > 50:
                safe_id = safe_id[:50]
            video_id = f"{safe_id}_{file_hash}"

            # Use file path hash as URL for duplicate detection
            url_hash = hashlib.md5(str(video_path).encode()).hexdigest()

            # Check if already processed
            if self.db.is_processed(url_hash):
                log_callback(f"⏭️ Skipping (already processed): {video_file.name}")
                return "skipped"

            log_callback(f"🔍 Extracting overlay text...")
            try:
                overlay_text = self.extractor.extract_overlay_text(str(video_path), video_id)
            except Exception as e:
                log_callback(f"⚠️ OCR failed: {str(e)}")
                overlay_text = ""

            log_callback(f"🎤 Transcribing speech...")
            try:
                speech_text = self.extractor.extract_speech(str(video_path))
            except Exception as e:
                log_callback(f"⚠️ Whisper failed: {str(e)}")
                speech_text = ""

            data = {
                'video_id': video_id,
                'platform': 'local',
                'url': original_name,  # Use original filename instead of full path
                'overlay_text': overlay_text,
                'speech_text': speech_text,
                'captions': '',
                'hashtags': '',
                'timestamp': datetime.now().isoformat()
            }

            self.db.add_video(video_id, 'local', url_hash, overlay_text, speech_text, '', '')
            self.exporter.export_to_csv(data)
            self.exporter.export_to_json(data)
            self.exporter.export_to_txt(data)

            log_callback(f"✅ Completed: {original_name}")

        except Exception as e:
            log_callback(f"❌ Failed {video_path}: {str(e)}")
            raise

def main():
    root = tk.Tk()
    processor = VideoProcessor()
    app = Dashboard(root, processor)
    root.mainloop()

if __name__ == "__main__":
    main()
