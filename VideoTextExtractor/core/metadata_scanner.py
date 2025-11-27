import subprocess
import json
from pathlib import Path
import pandas as pd
from openpyxl.styles import Alignment
import time
import sys

class MetadataScanner:
    """Fast metadata extraction using yt-dlp flat-playlist mode"""

    def __init__(self):
        # Use Python module mode to avoid launcher issues on Windows
        self.yt_dlp = [sys.executable, "-m", "yt_dlp"]
        self.instagram_scraper = None
        self.facebook_scraper = None

    def run_cmd(self, cmd):
        """Run command and return output"""
        return subprocess.run(cmd, capture_output=True, text=True)

    def get_playlist_entries(self, url):
        """Get all entries from playlist/channel without downloading"""
        cmd = self.yt_dlp + ["--no-warnings", "--flat-playlist", "--dump-json", url]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
        entries = []
        for line in proc.stdout:
            try:
                entries.append(json.loads(line))
            except Exception:
                continue
        proc.wait()
        return entries

    def get_video_info(self, url):
        """Fetch full metadata for a single video"""
        cmd = self.yt_dlp + ["--no-warnings", "--skip-download", "--dump-json", url]
        result = self.run_cmd(cmd)
        if result.returncode != 0:
            return {}
        try:
            return json.loads(result.stdout)
        except:
            return {}

    def sanitize_sheet_name(self, name):
        """Sanitize name for Excel sheet"""
        import re
        safe = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
        return safe[:30]  # Excel sheet name limit

    def scan_youtube_channel(self, channel_url, filter_shorts=False, max_videos=None, progress_callback=None):
        """
        Fast scan of YouTube channel/playlist

        Args:
            channel_url: YouTube channel or playlist URL
            filter_shorts: If True, only include videos < 180 seconds
            max_videos: Maximum number of videos to scan (None = all)
            progress_callback: Function to call with progress updates

        Returns:
            dict with channel info and video list
        """
        if progress_callback:
            progress_callback("Fetching playlist entries...")

        entries = self.get_playlist_entries(channel_url)
        total = len(entries)

        if progress_callback:
            progress_callback(f"Found {total} entries. Extracting metadata...")

        videos = []
        channel_name = None

        for i, entry in enumerate(entries, 1):
            # Check max limit
            if max_videos and len(videos) >= max_videos:
                break

            vid_id = entry.get("id")
            title = entry.get("title", "")
            url = f"https://www.youtube.com/watch?v={vid_id}"

            if not channel_name:
                # Use playlist-level metadata first (always available and correct)
                channel_name = (entry.get("playlist_channel") or
                               entry.get("playlist_uploader") or
                               entry.get("channel") or
                               entry.get("uploader") or
                               "YouTube")

            # Use data directly from flat-playlist (much faster!)
            duration = entry.get("duration", 0)
            description = entry.get("description", "")

            # Filter shorts if requested
            if filter_shorts and duration > 180:
                if progress_callback and i % 20 == 0:
                    progress_callback(f"Scanning... {i}/{total} ({len(videos)} shorts found)")
                continue

            videos.append({
                "video_id": vid_id,
                "title": title,
                "channel_name": channel_name,  # Use channel_name instead of uploader
                "description": description,     # YouTube uses description, not caption
                "url": url,
                "duration": duration
            })

            if progress_callback and i % 20 == 0:
                progress_callback(f"Scanning... {i}/{total} ({len(videos)} videos found)")

        if progress_callback:
            progress_callback(f"✅ Extraction complete! Found {len(videos)} videos from {total} entries")

        return {
            "channel_name": channel_name,
            "platform": "youtube",
            "total_entries": total,
            "videos": videos
        }

    def scan_tiktok_profile(self, profile_url, max_videos=None, progress_callback=None):
        """
        Fast scan of TikTok profile

        Args:
            profile_url: TikTok profile URL
            max_videos: Maximum number of videos to scan
            progress_callback: Function to call with progress updates

        Returns:
            dict with profile info and video list
        """
        if progress_callback:
            progress_callback("Fetching TikTok profile entries...")

        entries = self.get_playlist_entries(profile_url)
        total = len(entries)

        username = profile_url.split("@")[-1].strip("/")

        if progress_callback:
            progress_callback(f"Found {total} videos in @{username}")

        videos = []

        for i, entry in enumerate(entries, 1):
            if max_videos and len(videos) >= max_videos:
                break

            vid_id = entry.get("id") or entry.get("url")
            title = entry.get("title", "")

            if not vid_id:
                continue

            video_url = entry.get("url") or f"https://www.tiktok.com/@{username}/video/{vid_id}"
            duration = entry.get("duration", 0)
            description = entry.get("description") or title

            videos.append({
                "video_id": vid_id,
                "title": title,
                "username": username,           # TikTok has username
                "description": description,     # TikTok uses description
                "url": video_url,
                "duration": duration
            })

            if progress_callback and i % 10 == 0:
                progress_callback(f"Scanning... {i}/{total}")

        return {
            "channel_name": username,
            "platform": "tiktok",
            "total_entries": total,
            "videos": videos
        }

    def scan_instagram_profile(self, profile_input, max_videos=50, progress_callback=None):
        """
        Fast scan of Instagram profile

        Args:
            profile_input: Instagram profile URL or username
            max_videos: Maximum number of videos to scan (default: 50)
            progress_callback: Function to call with progress updates

        Returns:
            dict with profile info and video list
        """
        # Lazy load Instagram scraper
        if not self.instagram_scraper:
            from platforms.instagram import InstagramScraper
            self.instagram_scraper = InstagramScraper()

        # Extract username from URL if needed
        import re
        if 'instagram.com' in profile_input:
            match = re.search(r'instagram\.com/([^/?]+)', profile_input)
            username = match.group(1) if match else profile_input
        else:
            username = profile_input.strip('@')

        if progress_callback:
            progress_callback(f"Fetching Instagram profile: @{username}")
            progress_callback("⚠️  Note: Instagram has rate limits. This may be slow.")

        # Check if logged in
        if not self.instagram_scraper.loader.context.is_logged_in:
            raise Exception(
                "Instagram login required for profile scanning.\n"
                "Click the 'Login' button to authenticate first."
            )

        try:
            import instaloader

            # Get profile
            profile = instaloader.Profile.from_username(
                self.instagram_scraper.loader.context,
                username
            )

            if progress_callback:
                progress_callback(f"Scanning posts from @{username} (max {max_videos} videos)...")

            videos = []
            post_count = 0

            # Iterate through posts
            for post in profile.get_posts():
                post_count += 1

                # Rate limiting: pause every 10 posts
                if post_count % 10 == 0:
                    if progress_callback:
                        progress_callback(
                            f"Checked {post_count} posts, found {len(videos)} videos. "
                            f"Pausing 2s to avoid rate limits..."
                        )
                    time.sleep(2)

                # Only process video posts
                if post.is_video:
                    # Determine URL format based on post type
                    if post.typename == 'GraphVideo':
                        url = f"https://www.instagram.com/p/{post.shortcode}/"
                    else:
                        url = f"https://www.instagram.com/reel/{post.shortcode}/"

                    # Extract metadata
                    caption = post.caption if post.caption else ""

                    # Extract hashtags
                    hashtags = []
                    if caption:
                        hashtag_pattern = r'#(\w+)'
                        hashtags = re.findall(hashtag_pattern, caption)

                    videos.append({
                        "video_id": post.shortcode,
                        "title": caption[:100] + "..." if len(caption) > 100 else caption,
                        "username": username,
                        "caption": caption,
                        "hashtags": ", ".join(hashtags),
                        "url": url,
                        "duration": post.video_duration if hasattr(post, 'video_duration') else 0,
                        "likes": post.likes,
                        "views": post.video_view_count if hasattr(post, 'video_view_count') else 0
                    })

                    if progress_callback:
                        progress_callback(f"Found video {len(videos)}: {post.shortcode}")

                    # Stop if we've reached max
                    if len(videos) >= max_videos:
                        if progress_callback:
                            progress_callback(f"Reached maximum of {max_videos} videos")
                        break

                # Safety limit
                if post_count >= 200:
                    if progress_callback:
                        progress_callback(f"Checked {post_count} posts, stopping to avoid rate limits")
                    break

            if not videos:
                raise Exception(f"No videos found on profile @{username}")

            return {
                "channel_name": username,
                "platform": "instagram",
                "total_entries": len(videos),
                "videos": videos
            }

        except Exception as e:
            if "rate limit" in str(e).lower() or "401" in str(e):
                raise Exception(
                    f"Instagram rate limit exceeded.\n\n"
                    f"Please wait 10-15 minutes before trying again.\n"
                    f"Tip: Process individual video URLs instead of scanning entire profiles."
                )
            raise

    def scan_facebook_page(self, page_url, max_videos=None, progress_callback=None):
        """
        Fast scan of Facebook page/group

        Args:
            page_url: Facebook page or group URL
            max_videos: Maximum number of videos to scan
            progress_callback: Function to call with progress updates

        Returns:
            dict with page info and video list

        Note: Facebook scanning has limitations and may not work for all pages
        """
        if progress_callback:
            progress_callback("Fetching Facebook page entries...")
            progress_callback("⚠️  Note: Facebook scanning is limited to public pages")

        try:
            entries = self.get_playlist_entries(page_url)
            total = len(entries)

            if total == 0:
                # Try single video info
                info = self.get_video_info(page_url)
                if info:
                    entries = [info]
                    total = 1

            if total == 0:
                raise Exception(
                    "Could not fetch Facebook videos.\n\n"
                    "This may be because:\n"
                    "• The page is private or requires login\n"
                    "• The page has no videos\n"
                    "• Facebook is blocking automated access\n\n"
                    "Try processing individual video URLs instead."
                )

            # Extract page name from URL
            import re
            page_match = re.search(r'facebook\.com/([^/?]+)', page_url)
            page_name = page_match.group(1) if page_match else "Facebook"

            if progress_callback:
                progress_callback(f"Found {total} entries from {page_name}")

            videos = []

            for i, entry in enumerate(entries, 1):
                if max_videos and len(videos) >= max_videos:
                    break

                vid_id = entry.get("id", "")
                title = entry.get("title", "")
                url = entry.get("url") or entry.get("webpage_url", "")
                duration = entry.get("duration", 0)
                description = entry.get("description", "")

                if not url:
                    continue

                videos.append({
                    "video_id": vid_id,
                    "title": title,
                    "page_name": page_name,        # Use page_name for consistency
                    "description": description,     # Facebook uses description, not caption
                    "url": url,
                    "duration": duration
                })

                if progress_callback and i % 10 == 0:
                    progress_callback(f"Scanning... {i}/{total}")

            if not videos:
                raise Exception("No video metadata could be extracted from Facebook page")

            return {
                "channel_name": page_name,
                "platform": "facebook",
                "total_entries": total,
                "videos": videos
            }

        except Exception as e:
            if "Could not fetch" in str(e):
                raise
            raise Exception(
                f"Facebook scanning failed: {str(e)}\n\n"
                f"Facebook has strict access controls. Try:\n"
                f"• Processing individual video URLs\n"
                f"• Ensuring the page is public\n"
                f"• Using yt-dlp with cookies for authentication"
            )

    def export_to_excel(self, scan_results, output_path, selected_columns=None):
        """
        Export scan results to Excel

        Args:
            scan_results: List of scan result dicts or single dict
            output_path: Path to save Excel file
            selected_columns: Dict of column names to boolean (True=include, False=exclude)
                            If None, include all columns

        Returns:
            Path to created Excel file or None if no data to export
        """
        if not isinstance(scan_results, list):
            scan_results = [scan_results]

        output_path = Path(output_path)

        # Check if there's any data to export
        has_data = any(result.get("videos", []) for result in scan_results)
        if not has_data:
            raise Exception("No videos to export - all scan results are empty")

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for result in scan_results:
                channel_name = result.get("channel_name", "Unknown")
                platform = result.get("platform", "unknown")
                videos = result.get("videos", [])

                if not videos:
                    continue

                # Determine columns based on platform
                if platform == "instagram":
                    # Instagram has extra fields: hashtags, likes, views
                    columns = [
                        "video_id", "title", "username", "caption",
                        "hashtags", "url", "duration", "likes", "views"
                    ]
                    col_widths = {
                        'A': 15,  # video_id
                        'B': 40,  # title
                        'C': 20,  # username
                        'D': 60,  # caption
                        'E': 30,  # hashtags
                        'F': 50,  # url
                        'G': 10,  # duration
                        'H': 10,  # likes
                        'I': 10   # views
                    }
                elif platform == "youtube":
                    # YouTube has channel_name and description (not username/caption)
                    columns = [
                        "video_id", "title", "channel_name", "description", "url", "duration"
                    ]
                    col_widths = {
                        'A': 15,  # video_id
                        'B': 50,  # title
                        'C': 25,  # channel_name
                        'D': 60,  # description
                        'E': 50,  # url
                        'F': 10   # duration
                    }
                elif platform == "tiktok":
                    # TikTok has username and description
                    columns = [
                        "video_id", "title", "username", "description", "url", "duration"
                    ]
                    col_widths = {
                        'A': 15,  # video_id
                        'B': 50,  # title
                        'C': 20,  # username
                        'D': 60,  # description
                        'E': 50,  # url
                        'F': 10   # duration
                    }
                elif platform == "facebook":
                    # Facebook has page_name and description
                    columns = [
                        "video_id", "title", "page_name", "description", "url", "duration"
                    ]
                    col_widths = {
                        'A': 15,  # video_id
                        'B': 50,  # title
                        'C': 25,  # page_name
                        'D': 60,  # description
                        'E': 50,  # url
                        'F': 10   # duration
                    }
                else:
                    # Fallback for unknown platforms
                    columns = [
                        "video_id", "title", "username", "caption", "url", "duration"
                    ]
                    col_widths = {
                        'A': 15,  # video_id
                        'B': 50,  # title
                        'C': 20,  # username
                        'D': 60,  # caption
                        'E': 50,  # url
                        'F': 10   # duration
                    }

                # Create DataFrame with available columns
                # Filter to only include columns that exist in the data
                available_columns = []
                for col in columns:
                    if any(col in video for video in videos):
                        available_columns.append(col)

                # Further filter by user selection if provided
                if selected_columns:
                    available_columns = [col for col in available_columns
                                        if selected_columns.get(col, True)]

                df = pd.DataFrame(videos, columns=available_columns)

                # Sanitize sheet name
                sheet_name = self.sanitize_sheet_name(channel_name)

                # Write to Excel
                df.to_excel(writer, sheet_name=sheet_name, index=False)

                # Format worksheet
                worksheet = writer.sheets[sheet_name]

                # Set column widths
                for col_letter, width in col_widths.items():
                    try:
                        worksheet.column_dimensions[col_letter].width = width
                    except:
                        pass

                # Enable text wrapping
                for row in worksheet.iter_rows():
                    for cell in row:
                        cell.alignment = Alignment(wrap_text=True, vertical='top')

        return str(output_path)

    def export_urls_to_txt(self, scan_results, output_path):
        """
        Export just URLs to TXT file for later processing

        Args:
            scan_results: Scan result dict or list
            output_path: Path to save TXT file

        Returns:
            Path to created TXT file
        """
        if not isinstance(scan_results, list):
            scan_results = [scan_results]

        output_path = Path(output_path)

        urls = []
        for result in scan_results:
            videos = result.get("videos", [])
            for video in videos:
                urls.append(video["url"])

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(urls))

        return str(output_path)
