# Instagram Authentication & Cookie Setup Guide

## Method 1: Using Browser Cookies (RECOMMENDED)

### Step 1: Install Browser Extension
Install "Get cookies.txt LOCALLY" extension:
- Chrome: https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc
- Firefox: https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/

### Step 2: Export Instagram Cookies
1. Login to Instagram in your browser
2. Navigate to instagram.com
3. Click the extension icon
4. Click "Export" or "Download"
5. Save as `cookies.txt`

### Step 3: Place Cookie File
Copy `cookies.txt` to:
```
VideoTextExtractor/data/cookies.txt
```

## Method 2: Using Username/Password (Less Reliable)

Instagram may block automated logins. Use cookies instead if possible.

## Troubleshooting

**401 Unauthorized / Login Required:**
- Instagram requires authentication for downloads
- Use cookies.txt method (Method 1)
- Make sure you're logged in to Instagram in browser before exporting cookies

**Two-Factor Authentication:**
- Complete 2FA in browser first
- Then export cookies while logged in
- Cookies will contain session token

**Rate Limiting:**
- Instagram may block excessive requests
- Wait 15-30 minutes between large batches
- Use authenticated cookies to increase limits

## Testing
After placing cookies.txt, try downloading a single video first to verify it works.
