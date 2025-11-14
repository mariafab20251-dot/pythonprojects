# Metadata Scan: Platform Comparison

Quick reference guide for choosing the right platform and understanding limitations.

## 🚀 At a Glance

| Platform  | Speed | Max Videos | Auth Required | Reliability | Extra Data |
|-----------|-------|------------|---------------|-------------|------------|
| YouTube   | ⚡️⚡️⚡️ | Unlimited  | No            | ✅ Excellent | Duration   |
| TikTok    | ⚡️⚡️⚡️ | Unlimited  | No            | ✅ Excellent | Duration   |
| Instagram | ⚡️     | 50         | **YES**       | ⚠️ Good     | Likes, Views, Hashtags |
| Facebook  | ⚡️     | Unlimited  | No*           | ❌ Poor     | Duration   |

*Facebook: No auth for public pages, but may require cookies for some content

---

## 📊 Detailed Comparison

### YouTube

**Best For**: Bulk channel analysis, playlist processing, content research

**Pros**:
- ✅ Very fast (100 videos in 2-3 minutes)
- ✅ No authentication required
- ✅ No rate limits
- ✅ Unlimited videos
- ✅ Works with channels, playlists, user pages
- ✅ Reliable metadata extraction
- ✅ Full descriptions/captions available

**Cons**:
- None really - this is the most reliable platform

**Use When**:
- Analyzing competitor channels
- Researching content ideas
- Bulk downloading from playlists
- Filtering videos by duration/title
- Any YouTube-related task

**Example URLs**:
```
https://youtube.com/@channelname
https://youtube.com/channel/UC...
https://youtube.com/c/username
https://youtube.com/playlist?list=...
```

---

### TikTok

**Best For**: Profile analysis, trend research, content aggregation

**Pros**:
- ✅ Fast scanning (50+ videos in 1-2 minutes)
- ✅ No authentication required
- ✅ No rate limits (reasonable use)
- ✅ Unlimited videos
- ✅ Reliable extraction
- ✅ Full captions available

**Cons**:
- May occasionally fail due to TikTok's anti-bot measures
- Less metadata than YouTube (no detailed descriptions)

**Use When**:
- Analyzing TikTok creators
- Collecting trending videos
- Researching hashtags and topics
- Bulk TikTok processing

**Example URLs**:
```
https://tiktok.com/@username
```

---

### Instagram

**Best For**: Small profiles, engagement analysis, when you need metrics

**Pros**:
- ✅ Extra engagement data (likes, views)
- ✅ Hashtag extraction
- ✅ Full captions
- ✅ Works well for small profiles (< 50 videos)
- ✅ Integrates with existing Instagram login

**Cons**:
- ❌ **Requires authentication** (must login first)
- ⚠️ **Max 50 videos** per scan (Instagram limit)
- ⚠️ **Rate limited** (2s pause every 10 posts)
- ⚠️ Slower than other platforms (5-10 minutes)
- ⚠️ Risk of temporary blocks if overused
- ⚠️ May hit 401 errors during scan

**Use When**:
- You need engagement metrics (likes, views)
- Profile has < 50 videos
- You want to identify top-performing content
- Hashtag analysis is important
- You have Instagram credentials

**Avoid When**:
- Profile has > 50 videos (scan will be incomplete)
- You're in a hurry
- You don't have login credentials
- You've recently scanned multiple profiles

**Example URLs**:
```
https://instagram.com/username
@username (automatically converted)
```

**Important Notes**:
1. Login via GUI before scanning
2. Wait 10-15 minutes between scans to avoid blocks
3. Consider processing individual URLs for large profiles
4. Excel output includes extra columns: hashtags, likes, views

---

### Facebook

**Best For**: When you absolutely must try (not recommended)

**Pros**:
- Works for some fully public pages
- No authentication needed for public content
- Unlimited video count (in theory)

**Cons**:
- ❌ **Very unreliable** (50% failure rate)
- ❌ Only works for fully public pages
- ❌ May fail silently or with cryptic errors
- ❌ Facebook actively blocks automation
- ❌ May require cookies even for public content
- ❌ Less detailed metadata
- ❌ Unpredictable behavior

**Use When**:
- You have no other option
- Page is confirmed to be fully public
- You're willing to accept failure
- You have low expectations

**Better Alternative**:
Process individual Facebook video URLs instead of scanning:
1. Manually collect video URLs from the page
2. Save to TXT file
3. Use "Browse File" to load URLs
4. Process normally

**Example URLs**:
```
https://facebook.com/pagename
https://facebook.com/groups/groupname
```

**Important Notes**:
1. Expect failures - have a backup plan
2. For private content, manual collection is more reliable
3. Consider using browser extensions to extract URLs
4. Facebook scanning is a "best effort" feature

---

## 🎯 Decision Matrix

### Choose YouTube scanning when:
- ✅ Source is a YouTube channel/playlist
- ✅ You need bulk analysis
- ✅ Speed is important
- ✅ You want reliable results

### Choose TikTok scanning when:
- ✅ Source is a TikTok profile
- ✅ You need quick profile analysis
- ✅ Content research for TikTok

### Choose Instagram scanning when:
- ✅ You need engagement metrics (likes/views)
- ✅ Hashtag analysis is important
- ✅ Profile has < 50 videos
- ✅ You have Instagram login
- ⚠️ You can wait 5-10 minutes
- ⚠️ You understand rate limit risks

### Choose Facebook scanning when:
- ⚠️ Page is fully public AND
- ⚠️ You've exhausted other options AND
- ⚠️ You're willing to accept failure

### Skip metadata scan entirely when:
- You only have 1-5 videos to process
- You already have the specific URLs you need
- Platform is too unreliable (Facebook)
- You need immediate results and Instagram is too slow

---

## 💡 Pro Tips

### YouTube/TikTok Best Practices:
```
✅ Use freely - no limits
✅ Scan multiple channels at once (comma-separated)
✅ Process 100s or 1000s of videos
✅ Filter results in Excel afterward
✅ Load URLs for batch processing
```

### Instagram Best Practices:
```
⚠️ Login first via GUI
⚠️ Wait 10-15 min between scans
⚠️ Max 50 videos - for larger profiles, use regular scraping
⚠️ Use engagement data to filter top performers
⚠️ Consider metadata-only mode to skip downloads
⚠️ If you get 401 errors, wait longer between scans
```

### Facebook Best Practices:
```
❌ Try to avoid if possible
❌ Use individual URLs instead
❌ Have backup plan ready
❌ Check page is fully public first
❌ Consider browser-based URL collection
```

---

## 📈 Performance Benchmarks

Based on real-world testing:

### YouTube
```
100 videos: ~2-3 minutes
500 videos: ~8-10 minutes
1000 videos: ~15-20 minutes
```

### TikTok
```
50 videos: ~1-2 minutes
100 videos: ~3-5 minutes
200 videos: ~8-10 minutes
```

### Instagram
```
10 videos: ~2-3 minutes (with pauses)
25 videos: ~5-6 minutes (with pauses)
50 videos: ~8-10 minutes (with pauses)
Max: 50 videos (hard limit)
```

### Facebook
```
Success rate: ~50% (highly variable)
When it works: Similar to YouTube
When it fails: Immediate error
```

---

## 🔄 Migration Guide

### From Flask-based MetadataExtractor

If you were using the old Flask MetadataExtractor:

**Old Way** (Flask app):
```bash
python MetadataExtractor/app.py
# Open browser
# Navigate to http://localhost:5000
# Enter URL
# Download Excel
```

**New Way** (Integrated):
```bash
python main.py
# Select platform
# Enter URL
# Click "Metadata Scan"
# Choose output folder
# Excel + URLs created automatically
```

**Benefits of New Way**:
- ✅ No separate Flask server
- ✅ Integrated with main app
- ✅ Same GUI for everything
- ✅ Supports all 4 platforms
- ✅ Direct integration with processing workflow
- ✅ Auto-prompt to load URLs after scan

---

## 🆘 Troubleshooting

### "Instagram login required"
➡️ Click the "Login" button, enter credentials, try again

### "Instagram rate limit exceeded"
➡️ Wait 10-15 minutes, try again with fewer videos

### "Facebook could not fetch videos"
➡️ Page is likely private or blocked - use individual URLs instead

### YouTube/TikTok taking too long
➡️ Normal for 1000+ videos - use filters in Excel to narrow down

### Excel missing columns (hashtags, likes, views)
➡️ Those columns are Instagram-only, other platforms don't have this data

### Scan stops at 50 videos (Instagram)
➡️ Expected - Instagram has a 50 video limit to avoid rate limiting

---

## 📚 Related Documentation

- **Setup Guide**: [METADATA_SCAN_GUIDE.md](METADATA_SCAN_GUIDE.md)
- **Quick Start**: [QUICK_START_METADATA_SCAN.md](QUICK_START_METADATA_SCAN.md)
- **Instagram Login**: [INSTAGRAM_LOGIN_GUIDE.md](INSTAGRAM_LOGIN_GUIDE.md)
- **Main README**: [README.md](README.md)

---

**Summary**: Use YouTube/TikTok for fast, reliable bulk scanning. Use Instagram for small profiles when you need engagement data. Avoid Facebook scanning when possible.
