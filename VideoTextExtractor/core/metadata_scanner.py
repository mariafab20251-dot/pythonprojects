import subprocess
import json
from pathlib import Path
import pandas as pd
from openpyxl.styles import Alignment

class MetadataScanner:
    """Fast metadata extraction using yt-dlp flat-playlist mode"""

    def __init__(self):
        self.yt_dlp = "yt-dlp"  # Assumes yt-dlp is in PATH

    def run_cmd(self, cmd):
        """Run command and return output"""
        return subprocess.run(cmd, capture_output=True, text=True)

    def get_playlist_entries(self, url):
        """Get all entries from playlist/channel without downloading"""
        cmd = [self.yt_dlp, "--no-warnings", "--flat-playlist", "--dump-json", url]
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
        cmd = [self.yt_dlp, "--no-warnings", "--skip-download", "--dump-json", url]
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
                channel_name = entry.get("channel") or "YouTube"

            # Get detailed info for duration
            info = self.get_video_info(url)
            duration = info.get("duration", 0)
            uploader = info.get("uploader", "")
            caption = info.get("description", "")

            # Filter shorts if requested
            if filter_shorts and duration > 180:
                if progress_callback and i % 10 == 0:
                    progress_callback(f"Scanning... {i}/{total} ({len(videos)} shorts found)")
                continue

            videos.append({
                "video_id": vid_id,
                "title": title,
                "username": uploader,
                "caption": caption,
                "url": url,
                "duration": duration
            })

            if progress_callback and i % 10 == 0:
                progress_callback(f"Scanning... {i}/{total} ({len(videos)} videos found)")

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
            caption = entry.get("description") or title

            videos.append({
                "video_id": vid_id,
                "title": title,
                "username": username,
                "caption": caption,
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

    def export_to_excel(self, scan_results, output_path):
        """
        Export scan results to Excel

        Args:
            scan_results: List of scan result dicts or single dict
            output_path: Path to save Excel file

        Returns:
            Path to created Excel file
        """
        if not isinstance(scan_results, list):
            scan_results = [scan_results]

        output_path = Path(output_path)

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for result in scan_results:
                channel_name = result.get("channel_name", "Unknown")
                videos = result.get("videos", [])

                if not videos:
                    continue

                # Create DataFrame
                df = pd.DataFrame(videos, columns=[
                    "video_id", "title", "username", "caption", "url", "duration"
                ])

                # Sanitize sheet name
                sheet_name = self.sanitize_sheet_name(channel_name)

                # Write to Excel
                df.to_excel(writer, sheet_name=sheet_name, index=False)

                # Format worksheet
                worksheet = writer.sheets[sheet_name]

                # Set column widths
                worksheet.column_dimensions['A'].width = 15  # video_id
                worksheet.column_dimensions['B'].width = 50  # title
                worksheet.column_dimensions['C'].width = 20  # username
                worksheet.column_dimensions['D'].width = 60  # caption
                worksheet.column_dimensions['E'].width = 50  # url
                worksheet.column_dimensions['F'].width = 10  # duration

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
