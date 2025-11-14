#!/usr/bin/env python
"""Test script for metadata scanner without GUI"""

from core.metadata_scanner import MetadataScanner
from datetime import datetime
import sys

def detect_platform(url):
    """Auto-detect platform from URL"""
    url_lower = url.lower()
    if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'youtube'
    elif 'tiktok.com' in url_lower:
        return 'tiktok'
    elif 'instagram.com' in url_lower:
        return 'instagram'
    elif 'facebook.com' in url_lower or 'fb.com' in url_lower:
        return 'facebook'
    else:
        return None

def test_metadata_scan():
    """Test metadata scanning for any platform"""
    print("=" * 60)
    print("Metadata Scanner - Command Line Test")
    print("=" * 60)

    # Get URL from command line
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        print("Usage: python test_metadata_scan.py <url>")
        print("\nExamples:")
        print("  python test_metadata_scan.py https://youtube.com/@channelname")
        print("  python test_metadata_scan.py https://tiktok.com/@username")
        print("  python test_metadata_scan.py https://instagram.com/username")
        print("  python test_metadata_scan.py https://facebook.com/pagename")
        return

    # Detect platform
    platform = detect_platform(url)
    if not platform:
        print(f"❌ Could not detect platform from URL: {url}")
        print("Supported: YouTube, TikTok, Instagram, Facebook")
        return

    print(f"Platform detected: {platform.upper()}")

    scanner = MetadataScanner()

    def progress_log(msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    try:
        progress_log(f"Starting scan for: {url}")

        # Call appropriate scanner based on platform
        if platform == 'youtube':
            result = scanner.scan_youtube_channel(
                url,
                filter_shorts=False,
                max_videos=None,  # Get ALL videos
                progress_callback=progress_log
            )
        elif platform == 'tiktok':
            result = scanner.scan_tiktok_profile(
                url,
                max_videos=None,  # Get ALL videos
                progress_callback=progress_log
            )
        elif platform == 'instagram':
            progress_log("⚠️  Instagram: Max 50 videos (rate limit protection)")
            result = scanner.scan_instagram_profile(
                url,
                max_videos=50,  # Instagram limit
                progress_callback=progress_log
            )
        elif platform == 'facebook':
            progress_log("⚠️  Facebook: Public pages only, may be unreliable")
            result = scanner.scan_facebook_page(
                url,
                max_videos=None,  # Get ALL videos
                progress_callback=progress_log
            )

        channel_name = result.get('channel_name', 'Unknown')
        videos = result.get('videos', [])

        progress_log(f"✅ Scan complete!")
        print("\n" + "=" * 60)
        print(f"Channel: {channel_name}")
        print(f"Platform: {result.get('platform')}")
        print(f"Videos found: {len(videos)}")
        print("=" * 60)

        # Show first few videos
        print("\nFirst 3 videos:")
        for i, video in enumerate(videos[:3], 1):
            print(f"\n{i}. {video.get('title', 'No title')[:50]}")
            print(f"   URL: {video.get('url')}")
            print(f"   Duration: {video.get('duration')}s")

        # Export to Excel and TXT
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_file = f"test_scan_{timestamp}.xlsx"
        txt_file = f"test_urls_{timestamp}.txt"

        progress_log(f"Exporting to Excel: {excel_file}")
        scanner.export_to_excel([result], excel_file)

        progress_log(f"Exporting URLs to: {txt_file}")
        scanner.export_urls_to_txt([result], txt_file)

        print("\n" + "=" * 60)
        print(f"✅ Test complete!")
        print(f"📊 Excel file: {excel_file}")
        print(f"📝 URL file: {txt_file}")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_metadata_scan()
