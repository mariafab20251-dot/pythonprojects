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
            # Reload session to ensure it's active
            self._load_session()
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

        try:
            # Fetch post metadata using Instaloader
            post = instaloader.Post.from_shortcode(self.loader.context, video_id)

            # Extract caption
            caption = post.caption if post.caption else ""

            # Extract hashtags from caption
            hashtags = ""
            if caption:
                hashtag_pattern = r'#(\w+)'
                found_hashtags = re.findall(hashtag_pattern, caption)
                hashtags = ", ".join(found_hashtags) if found_hashtags else ""

            return video_id, caption, hashtags

        except Exception as e:
            # If metadata fetch fails, still return video_id so download can proceed
            print(f"Warning: Could not fetch Instagram metadata: {str(e)}")
            return video_id, "", ""

    def get_all_videos_from_profile(self, username):
        """Get all video URLs from an Instagram profile"""
        try:
            # Check if logged in
            if not self.loader.context.is_logged_in:
                raise Exception(
                    "Not logged in to Instagram.\n"
                    "Click the 'Login' button to authenticate."
                )

            # Get profile
            profile = instaloader.Profile.from_username(self.loader.context, username)

            video_urls = []

            # Iterate through posts
            for post in profile.get_posts():
                # Check if it's a video (reel, IGTV, or video post)
                if post.is_video:
                    # Construct URL
                    if post.typename == 'GraphVideo':
                        url = f"https://www.instagram.com/p/{post.shortcode}/"
                    elif post.typename == 'GraphSidecar':
                        # May contain videos in carousel
                        url = f"https://www.instagram.com/p/{post.shortcode}/"
                    else:
                        url = f"https://www.instagram.com/reel/{post.shortcode}/"

                    video_urls.append(url)

            if not video_urls:
                raise Exception(f"No videos found on profile @{username}")

            return video_urls

        except instaloader.exceptions.ProfileNotExistsException:
            raise Exception(f"Instagram profile '@{username}' does not exist")
        except instaloader.exceptions.LoginRequiredException:
            raise Exception(
                "Instagram login required.\n"
                "Click the 'Login' button to authenticate."
            )
        except Exception as e:
            if "Not logged in" in str(e) or "Login" in str(e):
                raise
            raise Exception(f"Failed to scrape Instagram profile: {str(e)}")
