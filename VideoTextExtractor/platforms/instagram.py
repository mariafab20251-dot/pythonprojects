import instaloader
import re

class InstagramScraper:
    def __init__(self):
        self.loader = instaloader.Instaloader()

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
            return None, None, None

        try:
            post = instaloader.Post.from_shortcode(self.loader.context, video_id)

            captions = post.caption or ""
            hashtags = " ".join([tag for tag in re.findall(r'#\w+', captions)])

            return video_id, captions, hashtags
        except Exception as e:
            return video_id, "", ""

    def get_all_videos_from_profile(self, username):
        try:
            profile = instaloader.Profile.from_username(self.loader.context, username)
            video_urls = []

            for post in profile.get_posts():
                if post.is_video:
                    video_urls.append(f"https://instagram.com/reel/{post.shortcode}")

            return video_urls
        except Exception as e:
            raise Exception(f"Failed to fetch profile videos: {str(e)}")
