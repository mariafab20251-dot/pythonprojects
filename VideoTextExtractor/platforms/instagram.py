import instaloader
import re
import time
from pathlib import Path

class InstagramScraper:
    def __init__(self):
        self.loader = instaloader.Instaloader(
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            sleep=True,  # Enable sleep between requests
            quiet=False
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
        # Supports both formats:
        # instagram.com/reel/ABC123 (direct)
        # instagram.com/username/reel/ABC123 (with username)
        patterns = [
            r'instagram\.com/(?:[^/]+/)?reel/([A-Za-z0-9_-]+)',
            r'instagram\.com/(?:[^/]+/)?p/([A-Za-z0-9_-]+)',
            r'instagram\.com/(?:[^/]+/)?tv/([A-Za-z0-9_-]+)',
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

    def get_all_videos_from_profile(self, username, max_videos=50):
        """Get video URLs from an Instagram profile with rate limiting"""
        try:
            # Check if logged in
            if not self.loader.context.is_logged_in:
                raise Exception(
                    "Not logged in to Instagram.\n"
                    "Click the 'Login' button to authenticate."
                )

            print(f"Fetching profile: @{username}")

            # Get profile
            profile = instaloader.Profile.from_username(self.loader.context, username)

            video_urls = []
            post_count = 0

            print(f"Scanning posts for videos (max {max_videos})...")

            # Iterate through posts with limit
            for post in profile.get_posts():
                post_count += 1

                # Add delay every 10 posts to avoid rate limiting
                if post_count % 10 == 0:
                    print(f"Checked {post_count} posts, found {len(video_urls)} videos. Pausing to avoid rate limits...")
                    time.sleep(2)  # 2 second pause every 10 posts

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
                    print(f"Found video: {post.shortcode}")

                    # Stop if we've reached max videos
                    if len(video_urls) >= max_videos:
                        print(f"Reached maximum of {max_videos} videos")
                        break

                # Safety limit: stop after checking 200 posts
                if post_count >= 200:
                    print(f"Checked {post_count} posts, stopping to avoid rate limits")
                    break

            if not video_urls:
                raise Exception(f"No videos found on profile @{username}")

            print(f"Total videos found: {len(video_urls)}")
            return video_urls

        except instaloader.exceptions.ProfileNotExistsException:
            raise Exception(f"Instagram profile '@{username}' does not exist")
        except instaloader.exceptions.LoginRequiredException:
            raise Exception(
                "Instagram login required.\n"
                "Click the 'Login' button to authenticate."
            )
        except instaloader.exceptions.QueryReturnedBadRequestException as e:
            raise Exception(
                "Instagram rate limit exceeded.\n"
                "Please wait 10-15 minutes before trying again.\n"
                "Tip: Try processing individual video URLs instead of entire profiles."
            )
        except instaloader.exceptions.ConnectionException as e:
            if "401" in str(e) or "Unauthorized" in str(e):
                raise Exception(
                    "Instagram rate limit exceeded (401 Unauthorized).\n\n"
                    "Instagram is blocking requests. Please:\n"
                    "1. Wait 10-15 minutes\n"
                    "2. Try again with a fresh login\n"
                    "3. Or process individual video URLs instead\n\n"
                    "For better results, use cookies.txt method (see INSTAGRAM_LOGIN_GUIDE.md)"
                )
            raise Exception(f"Instagram connection error: {str(e)}")
        except Exception as e:
            if "Not logged in" in str(e) or "Login" in str(e):
                raise
            if "401" in str(e) or "Unauthorized" in str(e) or "rate" in str(e).lower():
                raise Exception(
                    "Instagram rate limit hit.\n\n"
                    "Wait 10-15 minutes and try again.\n"
                    "Or process videos one by one using direct URLs."
                )
            raise Exception(f"Failed to scrape Instagram profile: {str(e)}")
