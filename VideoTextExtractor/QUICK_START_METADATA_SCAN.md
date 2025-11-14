# Quick Start: Metadata Scan

## 🎯 What is it?

**Metadata Scan** = Fast extraction of video info WITHOUT downloading videos

**Use case**: You want to scan 100+ videos from a YouTube channel but don't want to wait hours downloading everything.

## ⚡ Quick Steps

### 1. Open the App
```bash
cd VideoTextExtractor
python main.py
```

### 2. Scan a Channel

1. **Select Platform**: YouTube or TikTok
2. **Enter URL**:
   - YouTube: `https://youtube.com/@channelname`
   - TikTok: `https://tiktok.com/@username`
3. **Click** "Metadata Scan" button (purple button)
4. **Choose folder** to save results
5. **Wait** for scan to complete (usually 1-3 minutes)

### 3. Review Results

Two files are created:
- **Excel file**: `metadata_scan_TIMESTAMP.xlsx` - All video info in spreadsheet
- **URL file**: `urls_TIMESTAMP.txt` - List of URLs ready for processing

### 4. Process Videos (Optional)

After scanning:
- Click "Yes" when prompted to load URLs
- OR click "Browse File" and select the `urls_TIMESTAMP.txt` file
- Click "Process URLs" to start full extraction

## 🚀 Example

**Scenario**: Extract metadata from a YouTube channel with 200 videos

```
Platform: YouTube
URL: https://youtube.com/@businesschannel
Click: Metadata Scan
Select: /VideoTextExtractor/channels/youtube/businesschannel/
Wait: ~2 minutes
Result: Excel with 200 videos (titles, captions, URLs, durations)
```

**What you get**:
```
metadata_scan_20250114_143022.xlsx
├── Sheet: businesschannel
    ├── video_id    | title              | username        | caption      | url                           | duration
    ├── abc123      | How to Start...    | businesschannel | Full guide...| youtube.com/watch?v=abc123    | 305
    ├── def456      | 5 Tips for...      | businesschannel | Learn these..| youtube.com/watch?v=def456    | 187
    └── ...

urls_20250114_143022.txt
├── https://www.youtube.com/watch?v=abc123
├── https://www.youtube.com/watch?v=def456
└── ...
```

## 💡 Why Use This?

### Before (Old Way)
1. Enter channel URL
2. Click "Process URLs"
3. Wait 3+ hours for 100 videos to download and process
4. Discover most videos aren't relevant to your needs
5. Wasted time and disk space

### After (New Way)
1. Click "Metadata Scan"
2. Wait 2-3 minutes
3. Review Excel file - see all titles, captions, durations
4. Filter to only relevant videos (e.g., videos > 5 min)
5. Load filtered URLs
6. Process only what you need (saves hours!)

## 📊 Supported Platforms

| Platform | Metadata Scan | Notes |
|----------|---------------|-------|
| YouTube  | ✅ Yes        | Channels, playlists |
| TikTok   | ✅ Yes        | User profiles |
| Instagram| ❌ No         | Use regular processing |
| Facebook | ❌ No         | Use regular processing |

## 🎬 Complete Workflow Example

**Goal**: Extract text from all YouTube Shorts under 60 seconds from a channel

### Step 1: Metadata Scan
```
Platform: YouTube
URL: https://youtube.com/@motivationchannel
Click: Metadata Scan
Wait: 2 minutes
Result: 150 videos in Excel
```

### Step 2: Filter in Excel
```
Open: metadata_scan_20250114_143022.xlsx
Filter: duration <= 60
Result: 45 shorts found
Copy: URLs of those 45 videos
```

### Step 3: Create Custom URL File
```
Create: shorts_only.txt
Paste: 45 URLs (one per line)
Save: /VideoTextExtractor/data/shorts_only.txt
```

### Step 4: Process Filtered Videos
```
Click: Browse File
Select: shorts_only.txt
Click: Process URLs
Wait: ~1 hour for 45 videos
Result: OCR + Speech extracted from all shorts
```

**Time saved**: Instead of processing all 150 videos (5+ hours), you only processed 45 videos (1 hour) = 4 hours saved!

## 🔧 Advanced Tips

### Scan Multiple Channels
Enter comma-separated URLs:
```
https://youtube.com/@channel1, https://youtube.com/@channel2
```
Result: Excel with multiple sheets (one per channel)

### Organize Your Scans
Save to organized folders:
```
VideoTextExtractor/
└── channels/
    ├── youtube/
    │   ├── business/
    │   ├── motivation/
    │   └── tech/
    └── tiktok/
        ├── cooking/
        └── fitness/
```

### Reuse URL Lists
Save URL lists for batch processing later:
```
1. Scan channel → Get urls_TIMESTAMP.txt
2. Review and filter URLs as needed
3. Process now OR save for later
4. Load anytime with "Browse File"
```

### Combine with Metadata-Only Mode
For ultra-fast scanning:
```
1. Metadata Scan → Get URLs
2. Uncheck "Download Videos"
3. Process URLs → Extract captions/hashtags only (no OCR/Speech)
4. Review results
5. Re-process specific videos with full OCR if needed
```

## ❓ Common Questions

**Q: How long does scanning take?**
A: Usually 1-3 minutes for 100 videos. Depends on platform API speed.

**Q: Does it download videos?**
A: No! That's the point. Only metadata is fetched.

**Q: What if I want to scan Instagram?**
A: Use regular processing. Instagram requires authentication and has rate limits.

**Q: Can I stop a scan?**
A: Yes, click the "Stop" button. But scans are so fast you probably won't need to.

**Q: Where are results saved?**
A: You choose the folder. Recommended: `/channels/platform/channelname/`

**Q: Can I scan private playlists?**
A: Only if your yt-dlp is configured with authentication for that platform.

## 🔗 See Also

- **Full Guide**: [METADATA_SCAN_GUIDE.md](METADATA_SCAN_GUIDE.md)
- **Folder Structure**: [FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md)
- **Main README**: [README.md](README.md)

---

**That's it! Start scanning!** 🚀
