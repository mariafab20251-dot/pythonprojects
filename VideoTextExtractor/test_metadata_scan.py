#!/usr/bin/env python
"""Test script for metadata scanner without GUI"""

from core.metadata_scanner import MetadataScanner
from datetime import datetime
import sys

def test_tiktok_scan():
    """Test TikTok metadata scanning"""
    print("=" * 60)
    print("Testing TikTok Metadata Scan")
    print("=" * 60)

    # Get URL from command line or use default
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        print("Usage: python test_metadata_scan.py <tiktok_profile_url>")
        print("Example: python test_metadata_scan.py https://tiktok.com/@username")
        return

    scanner = MetadataScanner()

    def progress_log(msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    try:
        progress_log(f"Starting scan for: {url}")

        result = scanner.scan_tiktok_profile(
            url,
            max_videos=10,  # Limit to 10 for testing
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
    test_tiktok_scan()
