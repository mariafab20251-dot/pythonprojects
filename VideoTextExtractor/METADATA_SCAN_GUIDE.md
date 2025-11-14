# Metadata Scan Guide

The **Metadata Scan** feature enables fast bulk extraction of video metadata without downloading videos. This creates a two-step workflow for efficient processing.

## 🎯 Purpose

**Problem**: Downloading and processing hundreds of videos takes hours.

**Solution**: First scan metadata (fast), then selectively process only the videos you need.

## 🚀 Two-Step Workflow

### Step 1: Metadata Scan (Fast)
Extract metadata from entire channels in minutes:
- Video IDs
- Titles
- Captions/Descriptions
- URLs
- Duration
- Uploader/Username

**No video downloads** → Very fast!

### Step 2: Full Processing (Selective)
Load the extracted URLs and process with:
- OCR (overlay text extraction)
- Speech transcription
- Full metadata

Process only what you need instead of everything.

## 📋 How to Use

### 1. Run Metadata Scan

1. **Select Platform**: Choose YouTube or TikTok
2. **Enter Channel URL**:
   - YouTube: `https://youtube.com/@channelname` or playlist URL
   - TikTok: `https://tiktok.com/@username`
3. **Click "Metadata Scan"**
4. **Select output folder** where results will be saved
5. **Wait for scan to complete** (much faster than full processing)

### 2. Review Metadata

The scan creates two files:
- **Excel file** (`metadata_scan_YYYYMMDD_HHMMSS.xlsx`)
  - Formatted spreadsheet with all video metadata
  - Separate sheets for each channel
  - Columns: video_id, title, username, caption, url, duration

- **URL list** (`urls_YYYYMMDD_HHMMSS.txt`)
  - Plain text file with one URL per line
  - Ready to load for full processing

### 3. Load URLs for Full Processing

**Option A: Automatic**
- Click "Yes" when prompted after scan completes
- First 10 URLs load into input field automatically

**Option B: Manual**
- Click "Browse File" button
- Select the `urls_YYYYMMDD_HHMMSS.txt` file
- All URLs load into input field

### 4. Process Videos

- Optionally uncheck "Download Videos" for metadata-only processing
- Click "Process URLs"
- Full OCR, speech transcription, and metadata extraction begins

## 📊 Supported Platforms

### ✅ YouTube
- Channels: `youtube.com/@channelname`
- Playlists: `youtube.com/playlist?list=...`
- User channels: `youtube.com/c/username`
- Channel IDs: `youtube.com/channel/UC...`
- **Speed**: Very fast, no limits
- **Auth Required**: No

### ✅ TikTok
- User profiles: `tiktok.com/@username`
- **Speed**: Fast, reliable
- **Auth Required**: No

### ⚠️ Instagram
- User profiles: `instagram.com/username`
- **Speed**: Slower (rate limiting)
- **Auth Required**: **YES** - Must login first
- **Limitations**:
  - Max 50 videos per scan
  - Rate limited (2s pause every 10 posts)
  - Risk of temporary blocks if overused
  - Includes extra data: hashtags, likes, views
- **Best Practice**: Use for small profiles or when you need engagement data

### ⚠️ Facebook
- Public pages: `facebook.com/pagename`
- **Speed**: Variable, less reliable
- **Auth Required**: No (for public pages)
- **Limitations**:
  - Only works for public pages/groups
  - May fail for private or restricted content
  - Less reliable than other platforms
  - May require cookies for some pages
- **Best Practice**: Process individual video URLs instead when possible

## 🎬 Example Workflows

### Workflow 1: YouTube Channel Analysis

**Goal**: Extract all video metadata from a YouTube channel

```
1. Platform: YouTube
2. Input: https://youtube.com/@businesstips
3. Click "Metadata Scan"
4. Select: /channels/youtube/businesstips/
5. Wait ~2 minutes
6. Result: Excel with 250 videos + URL list
7. Review Excel to identify videos of interest
8. Load URLs → Process only what you need
```

### Workflow 2: TikTok Batch Processing

**Goal**: Process multiple TikTok profiles

```
1. Platform: TikTok
2. Input: https://tiktok.com/@user1, https://tiktok.com/@user2
3. Click "Metadata Scan"
4. Select: /data/tiktok_scan/
5. Wait ~5 minutes
6. Result: Excel with multiple sheets (one per profile)
7. Load all URLs → Batch process
```

### Workflow 3: Selective Processing

**Goal**: Process only YouTube shorts under 60 seconds

```
1. Run metadata scan on channel
2. Open Excel file
3. Filter by duration < 60 seconds
4. Copy filtered URLs to new TXT file
5. Load TXT file → Process only shorts
```

### Workflow 4: Instagram Profile Analysis

**Goal**: Extract metadata from Instagram profile with engagement data

```
1. Platform: Instagram
2. Click "Login" → Enter credentials
3. Input: https://instagram.com/businessaccount
4. Click "Metadata Scan"
5. Confirm rate limit warning
6. Wait ~5 minutes (pauses every 10 posts)
7. Result: Excel with 50 videos + hashtags, likes, views
8. Review engagement data to identify top-performing content
9. Load high-engagement URLs → Full processing
```

**Note**: Instagram scan includes extra columns not available for other platforms:
- Hashtags extracted from captions
- Like counts
- View counts

### Workflow 5: Facebook Public Page

**Goal**: Scan public Facebook page (best effort)

```
1. Platform: Facebook
2. Input: https://facebook.com/publicpage
3. Click "Metadata Scan"
4. Confirm limitation warning
5. Wait for scan (may succeed or fail)
6. If successful: Excel with public videos
7. If failed: Process individual video URLs instead
```

**Important**: Facebook scanning is unreliable. For best results:
- Only use with fully public pages
- Have low expectations
- Be prepared to fall back to individual URL processing

## 💡 Tips

### Speed Benefits
- **Metadata scan**: 100 videos in ~3-5 minutes
- **Full processing**: 100 videos can take 2-3 hours
- **Recommendation**: Always scan first, process second

### Storage Benefits
- Metadata files are tiny (few KB)
- No temporary video downloads
- Can scan thousands of videos without disk space concerns

### Organization
- Save metadata scans to channel folders for organization
- Keep URL lists for future batch processing
- Excel files are great for filtering and analysis

### Batch Processing
- Scan multiple channels by entering comma-separated URLs
- Each channel gets its own sheet in the Excel file
- All URLs combined in single TXT file

### Integration with Main Features
- After scan, use "Browse File" to load URLs
- Uncheck "Download Videos" for metadata-only processing
- Use regular processing for Instagram/Facebook

## 🔧 Technical Details

### What Gets Extracted

**YouTube**:
- Video ID
- Title
- Uploader channel name
- Description (full)
- Duration (seconds)
- Video URL

**TikTok**:
- Video ID
- Title/Caption
- Username
- Description
- Duration
- Video URL

### How It Works

Uses `yt-dlp` with `--flat-playlist` mode:
- No video downloads
- Fetches only metadata from platform APIs
- Processes JSON responses
- Exports to formatted Excel + plain text

### Limitations

1. **Platform support**: Only YouTube and TikTok
2. **Rate limiting**: Very rare (metadata requests are lightweight)
3. **Accuracy**: Depends on platform API data
4. **Private videos**: Not accessible without authentication

## 📂 File Locations

Metadata scan results are saved to your chosen folder with timestamp:

```
chosen_folder/
├── metadata_scan_20250114_143022.xlsx    ← Formatted metadata
└── urls_20250114_143022.txt              ← URL list for processing
```

Recommended folder structure:

```
VideoTextExtractor/
└── channels/
    ├── youtube/
    │   └── channelname/
    │       ├── metadata_scan_20250114_143022.xlsx
    │       └── urls_20250114_143022.txt
    └── tiktok/
        └── username/
            ├── metadata_scan_20250114_143022.xlsx
            └── urls_20250114_143022.txt
```

## ❓ FAQ

**Q: Can I scan Instagram profiles?**
A: Yes! But you must login first. Instagram scans are rate-limited and max out at 50 videos per scan. Best for small profiles or when you need engagement data (likes, views, hashtags).

**Q: How many videos can I scan at once?**
A: Depends on platform:
- YouTube/TikTok: No hard limit, tested with 1000+ videos
- Instagram: Max 50 videos (rate limit protection)
- Facebook: No hard limit, but may fail for various reasons

**Q: Does scanning use my Instagram login?**
A: Yes, Instagram requires authentication. YouTube, TikTok, and Facebook (public pages) don't need login.

**Q: Can I filter videos during scan?**
A: Not during scan, but you can filter the Excel afterward by duration, title, likes, etc. Instagram scans include engagement metrics for advanced filtering.

**Q: What if Instagram scanning fails with rate limit error?**
A: Wait 10-15 minutes and try again. Instagram is very protective. Consider:
- Processing individual URLs instead of scanning entire profile
- Scanning smaller batches
- Using the regular profile scraper with individual URL processing

**Q: Why does Facebook scanning fail?**
A: Facebook has strict access controls. Common reasons:
- Page is private or restricted
- Facebook is blocking automated access
- Authentication/cookies required
- Page has no videos

For Facebook, it's often better to process individual video URLs instead of scanning.

**Q: What if scanning fails?**
A: Check your internet connection and ensure:
- URL is valid channel/playlist/profile URL
- For Instagram: You're logged in
- For Facebook: Page is fully public
- Platform is correctly selected

**Q: Can I resume a stopped scan?**
A: No. Scans start from beginning. YouTube/TikTok scans are fast enough that restarting isn't an issue. Instagram scans may take longer but are limited to 50 videos anyway.

**Q: What's the difference between Instagram scan and regular Instagram processing?**
A: Metadata scan extracts ALL video URLs at once with engagement data, then you can selectively process. Regular processing downloads and extracts from individual URLs. Scan first for bulk operations, direct processing for specific videos.

## 🔗 Related Features

- **Browse File**: Load scanned URLs for processing (gui/dashboard.py:137)
- **Download Videos Toggle**: Skip downloads, metadata only (gui/dashboard.py:38)
- **Channel Folders**: Organized data storage (FOLDER_STRUCTURE.md)
- **Excel Reports**: Auto-generated after processing (core/exporter.py)

## 📞 Support

If you encounter issues:
1. Check the Activity Log for error messages
2. Verify URL format is correct
3. Ensure platform is YouTube or TikTok
4. Check internet connection
5. Try with a smaller channel first

---

**Happy scanning!** 🚀
