# Folder Structure Guide

This document explains how the system organizes downloaded videos and extracted data.

## Channel/Profile Organization

When you process a **channel or profile URL**, all data for that channel is organized in one folder:

```
VideoTextExtractor/
└── channels/
    ├── youtube/
    │   └── channelname/
    │       ├── videos/               ← All downloaded MP4 files
    │       │   ├── video1.mp4
    │       │   ├── video2.mp4
    │       │   └── video3.mp4
    │       ├── reports/              ← Individual TXT reports per video
    │       │   ├── YOUTUBE_video1.txt
    │       │   ├── YOUTUBE_video2.txt
    │       │   └── YOUTUBE_video3.txt
    │       ├── results.csv           ← CSV with all videos
    │       ├── results.json          ← JSON with all videos
    │       └── results_clean.xlsx    ← Clean Excel report (auto-generated)
    │
    ├── instagram/
    │   └── username/
    │       ├── videos/
    │       ├── reports/
    │       ├── results.csv
    │       ├── results.json
    │       └── results_clean.xlsx
    │
    ├── tiktok/
    │   └── username/
    │       └── ... (same structure)
    │
    └── facebook/
        └── pagename/
            └── ... (same structure)
```

## Single Video Organization

When you process **individual video URLs** (not a channel), files go to the default data folder:

```
VideoTextExtractor/
└── data/
    ├── videos/
    │   ├── instagram/
    │   │   ├── video1.mp4
    │   │   └── video2.mp4
    │   ├── youtube/
    │   ├── tiktok/
    │   └── facebook/
    ├── reports/
    │   ├── INSTAGRAM_video1.txt
    │   ├── INSTAGRAM_video2.txt
    │   └── ...
    ├── frames/                   ← Temporary frames for OCR
    ├── results.csv              ← All videos combined
    ├── results.json
    └── results_clean.xlsx       ← Auto-generated Excel
```

## How Channel Detection Works

### Automatic (Profile/Channel URL)
Enter a profile or channel URL:
- `https://instagram.com/username` → Creates `channels/instagram/username/`
- `https://youtube.com/@channel` → Creates `channels/youtube/channel/`
- `https://tiktok.com/@user` → Creates `channels/tiktok/user/`

All videos from that profile/channel go into that folder.

### Manual (URL List from File)
If you load a TXT file with URLs:

**TikTok/Facebook:** System detects channel from video URLs
```txt
https://tiktok.com/@username/video/123
https://tiktok.com/@username/video/456
```
→ Creates `channels/tiktok/username/` (same user detected)

**Instagram/YouTube:** Can't detect channel from video URLs
```txt
https://instagram.com/reel/ABC
https://instagram.com/reel/DEF
```
→ Uses `data/` folder (different users or unknown)

### Best Practice for URL Lists

**Option 1: Use Profile URL (Recommended)**
```txt
https://instagram.com/username
```
System scrapes all videos automatically and organizes everything.

**Option 2: List Individual Videos**
```txt
https://instagram.com/reel/ABC123
https://instagram.com/reel/DEF456
https://instagram.com/reel/GHI789
```
Videos go to `data/` folder unless system can detect they're from same channel.

## File Types in Each Folder

### videos/
- All downloaded video files (.mp4)
- Kept permanently (configurable in config.py)

### reports/
- Individual text reports per video
- Format: `PLATFORM_videoid.txt`
- Human-readable with all extracted data

### results.csv
- Spreadsheet with all videos
- Columns: Video ID, Platform, URL, Overlay Text, Speech, Captions, Hashtags, Date

### results.json
- JSON format for programmatic access
- Same data as CSV but structured

### results_clean.xlsx
- Auto-generated Excel file with formatting
- Text wrapping, auto-sized columns
- Duplicate text removed
- Generated automatically after processing completes

## Tips

1. **Process entire channels** instead of individual videos for better organization
2. **Each channel gets its own folder** - no mixing of data
3. **Excel reports auto-generate** after processing
4. **Use Browse File button** to load URLs from text files
5. **Multiple platforms** are kept completely separate

## Example Workflow

1. Create `my_channels.txt`:
   ```
   https://instagram.com/motivationalpage
   https://youtube.com/@businesstips
   https://tiktok.com/@lifehacks
   ```

2. Click **"Browse File"** and select the file

3. Click **"Process URLs"**

4. Result:
   ```
   channels/
   ├── instagram/motivationalpage/  (all Instagram videos + data)
   ├── youtube/businesstips/        (all YouTube videos + data)
   └── tiktok/lifehacks/            (all TikTok videos + data)
   ```

Each folder is completely self-contained with videos, reports, CSV, JSON, and Excel!
