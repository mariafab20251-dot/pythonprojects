import instaloader
import re
from pathlib import Path

class InstagramScraper:
    def __init__(self):
        self.loader = instaloader.Instaloader(
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )
        self.session_file = Path(__file__).parent.parent / "data" / "ig_session"
        self._load_session()

    def _load_session(self):
        if self.session_file.exists():
            try:
                self.loader.load_session_from_file(str(self.session_file))
            except:
                pass

    def login(self, username, password):
        try:
            self.loader.login(username, password)
            self.loader.save_session_to_file(str(self.session_file))
            return True
        except Exception as e:
            raise Exception(f"Instagram login failed: {str(e)}")

    def extract_video_id(self, url):
        # Extract shortcode from URL
        patterns = [
            r'instagram.com/reel/([A-Za-z0-9_-]+)',
            r'instagram.com/p/([A-Za-z0-9_-]+)',
            r'instagram.com/tv/([A-Za-z0-9_-]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def get_post_metadata(self, url):
        video_id = self.extract_video_id(url)
        if not video_id:
            return None, "", ""

        # Return basic info - yt-dlp will handle download
        return video_id, "", ""

    def get_all_videos_from_profile(self, username):
        raise NotImplementedError(
            "Instagram profile scraping requires authentication.\n"
            "Please use direct video URLs instead.\n"
            "See INSTAGRAM_AUTH.md for setup instructions."
        )
