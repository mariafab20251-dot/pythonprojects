# Instagram Authentication Guide

There are **two methods** to authenticate with Instagram for profile scraping and downloading videos.

## Method 1: GUI Login (Easiest) ⭐ RECOMMENDED

### Steps:
1. Run the application:
   ```bash
   python main.py
   ```

2. Look at the top of the dashboard - you'll see:
   - **Instagram Auth:** ❌ Not logged in
   - Purple **"Login"** button

3. Click the **"Login"** button

4. Enter your Instagram credentials:
   - Username (not email)
   - Password

5. Click **"Login"** in the dialog

6. Status will change to: **✅ Logged in (session)**

7. Session is saved to `data/ig_session` and persists across restarts

### Benefits:
- ✅ One-time login
- ✅ Session persists
- ✅ No browser extensions needed
- ✅ Works for profile scraping

---

## Method 2: Browser Cookies (Alternative)

If you prefer not to enter your password in the app, use browser cookies instead.

### Steps:

1. **Install Browser Extension:**
   - Chrome/Edge: [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
   - Firefox: [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)

2. **Export Cookies:**
   - Login to Instagram in your browser
   - Click the extension icon
   - Click "Export" or "Download"
   - Save as `cookies.txt`

3. **Place File:**
   ```
   VideoTextExtractor/
   └── data/
       └── cookies.txt  ← Put the file here
   ```

4. Restart the application - status will show: **✅ Auth (cookies.txt)**

### Benefits:
- ✅ No password in app
- ✅ Works with 2FA accounts
- ✅ Browser session stays logged in

---

## Which Method Should I Use?

| Feature | GUI Login | Browser Cookies |
|---------|-----------|-----------------|
| Easy setup | ⭐⭐⭐ | ⭐⭐ |
| No browser needed | ✅ | ❌ |
| Works with 2FA | ❌ | ✅ |
| Session persistence | ✅ | ✅ |
| Profile scraping | ✅ | ✅ |

**Recommendation:** Use **GUI Login** unless you have 2FA enabled, then use **Browser Cookies**.

---

## Troubleshooting

### Login Failed
- Check your username and password
- Make sure you're using username, not email
- Try logging in to Instagram website first
- If 2FA enabled, use Browser Cookies method instead

### Cookies Not Working
- Make sure cookies.txt is in the correct location: `data/cookies.txt`
- Export fresh cookies (they expire)
- Login to Instagram in browser first before exporting

### Status Shows Red "Not logged in"
- Check if `data/ig_session` or `data/cookies.txt` exists
- Try logging in again
- Restart the application

---

## Security Notes

- Your credentials are only used to login to Instagram via official API
- Session file is stored locally in `data/ig_session`
- Never share your session file or cookies.txt
- The app does not store your password
