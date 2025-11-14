import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading
import os
import re

class UniversalShortsDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal Shorts Downloader - Facebook | TikTok | YouTube")
        self.root.geometry("750x750")
        self.root.resizable(False, False)
        
        # Variables
        self.download_path = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads", "Shorts_Videos"))
        self.is_downloading = False
        self.yt_dlp = None
        self.loaded_file_path = None
        
        self.setup_ui()
        self.check_dependencies()
    
    def setup_ui(self):
        # Title
        title_label = tk.Label(self.root, text="Universal Shorts Downloader", 
                              font=("Arial", 18, "bold"), pady=5, fg="#2196F3")
        title_label.pack()
        
        # Subtitle
        subtitle = tk.Label(self.root, text="Download from Facebook Reels, TikTok & YouTube Shorts", 
                           font=("Arial", 10), fg="gray")
        subtitle.pack()
        
        # Platform indicators
        platform_frame = tk.Frame(self.root, pady=5)
        platform_frame.pack()
        
        platforms = [
            ("🟦 Facebook", "#4267B2"),
            ("⚫ TikTok", "#000000"),
            ("🔴 YouTube", "#FF0000")
        ]
        
        for platform, color in platforms:
            label = tk.Label(platform_frame, text=platform, font=("Arial", 9, "bold"), 
                           fg=color, padx=10)
            label.pack(side="left")
        
        # Instructions
        instructions = tk.Label(self.root, 
                               text="Paste video URLs below (supports multiple platforms simultaneously)",
                               font=("Arial", 9), fg="#666")
        instructions.pack(pady=5)
        
        # URL Frame
        url_frame = tk.Frame(self.root, pady=10)
        url_frame.pack(fill="both", expand=True, padx=20)
        
        tk.Label(url_frame, text="Video URLs (one per line):", 
                font=("Arial", 10, "bold")).pack(anchor="w")
        
        # File selection frame
        file_frame = tk.Frame(url_frame)
        file_frame.pack(fill="x", pady=5)
        
        load_file_btn = tk.Button(file_frame, text="📁 Load URLs from File", 
                                 command=self.load_urls_from_file,
                                 font=("Arial", 9), cursor="hand2", 
                                 bg="#4CAF50", fg="white")
        load_file_btn.pack(side="left", padx=(0, 5))
        
        convert_ids_btn = tk.Button(file_frame, text="🔄 Convert FB IDs to URLs", 
                                   command=self.convert_facebook_ids,
                                   font=("Arial", 9), cursor="hand2", 
                                   bg="#2196F3", fg="white")
        convert_ids_btn.pack(side="left", padx=5)
        
        self.file_status = tk.Label(file_frame, text="", font=("Arial", 8), fg="gray")
        self.file_status.pack(side="left", padx=10)
        
        # Text area for multiple URLs
        url_text_frame = tk.Frame(url_frame)
        url_text_frame.pack(fill="both", expand=True, pady=5)
        
        self.url_text = tk.Text(url_text_frame, height=6, font=("Courier", 9), 
                               wrap=tk.WORD, relief="solid", borderwidth=1)
        self.url_text.pack(side="left", fill="both", expand=True)
        
        url_scrollbar = tk.Scrollbar(url_text_frame, command=self.url_text.yview)
        url_scrollbar.pack(side="right", fill="y")
        self.url_text.config(yscrollcommand=url_scrollbar.set)
        
        # Helper text with examples
        helper_frame = tk.Frame(url_frame, bg="#f0f0f0", relief="solid", borderwidth=1)
        helper_frame.pack(fill="x", pady=5)
        
        tk.Label(helper_frame, text="📌 Supported URL formats:", 
                font=("Arial", 8, "bold"), bg="#f0f0f0").pack(anchor="w", padx=5, pady=2)
        
        examples = [
            "Facebook: facebook.com/reel/..., fb.watch/...",
            "TikTok: tiktok.com/@username/video/..., vm.tiktok.com/...",
            "YouTube: youtube.com/shorts/..., youtu.be/..."
        ]
        
        for example in examples:
            tk.Label(helper_frame, text=f"  • {example}", font=("Arial", 7), 
                    bg="#f0f0f0", fg="#555", anchor="w").pack(anchor="w", padx=10)
        
        # Download Path Frame
        path_frame = tk.Frame(self.root, pady=10)
        path_frame.pack(fill="x", padx=20)
        
        tk.Label(path_frame, text="📂 Download Location:", 
                font=("Arial", 10, "bold")).pack(anchor="w")
        
        path_entry_frame = tk.Frame(path_frame)
        path_entry_frame.pack(fill="x", pady=5)
        
        path_entry = tk.Entry(path_entry_frame, textvariable=self.download_path, 
                             font=("Arial", 9), state="readonly")
        path_entry.pack(side="left", fill="x", expand=True)
        
        browse_btn = tk.Button(path_entry_frame, text="Browse", 
                              command=self.browse_folder, cursor="hand2")
        browse_btn.pack(side="left", padx=5)
        
        # Quality Selection Frame
        quality_frame = tk.Frame(self.root, pady=5)
        quality_frame.pack(fill="x", padx=20)
        
        tk.Label(quality_frame, text="Video Quality:", font=("Arial", 9)).pack(side="left")
        
        self.quality_var = tk.StringVar(value="best")
        qualities = [
            ("Best Quality", "best"),
            ("720p", "720"),
            ("480p", "480"),
            ("360p", "360")
        ]
        
        for text, value in qualities:
            tk.Radiobutton(quality_frame, text=text, variable=self.quality_var, 
                          value=value, font=("Arial", 8)).pack(side="left", padx=5)
        
        # Progress Frame
        progress_frame = tk.Frame(self.root, pady=10)
        progress_frame.pack(fill="x", padx=20)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill="x", pady=5)
        
        self.status_label = tk.Label(progress_frame, text="Ready to download", 
                                     font=("Arial", 9, "bold"), fg="green")
        self.status_label.pack(anchor="w")
        
        # Statistics Frame
        stats_frame = tk.Frame(progress_frame, bg="#f5f5f5", relief="solid", borderwidth=1)
        stats_frame.pack(fill="x", pady=5)
        
        self.stats_label = tk.Label(stats_frame, text="Downloaded: 0 | Failed: 0 | Total: 0", 
                                    font=("Arial", 8), bg="#f5f5f5", fg="#333")
        self.stats_label.pack(pady=3)
        
        # Log Frame
        log_frame = tk.Frame(self.root, pady=10)
        log_frame.pack(fill="both", expand=True, padx=20)
        
        tk.Label(log_frame, text="📋 Activity Log:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, 
                                                  font=("Courier", 8), wrap=tk.WORD,
                                                  relief="solid", borderwidth=1)
        self.log_text.pack(fill="both", expand=True)
        
        # Buttons Frame
        button_frame = tk.Frame(self.root, pady=15)
        button_frame.pack(fill="x", padx=20)
        
        self.download_btn = tk.Button(button_frame, text="⬇️ Download Videos", 
                                      command=self.start_download, 
                                      font=("Arial", 12, "bold"), 
                                      bg="#cccccc", fg="white", 
                                      cursor="hand2", pady=10,
                                      relief="raised", borderwidth=2,
                                      state="disabled")  # Start disabled, enable after dependency check
        self.download_btn.pack(side="left", fill="x", expand=True, padx=3)
        
        self.stop_btn = tk.Button(button_frame, text="⏹️ Stop", 
                                 command=self.stop_download, 
                                 font=("Arial", 12, "bold"), 
                                 bg="#f44336", fg="white", 
                                 cursor="hand2", pady=10, 
                                 state="disabled",
                                 relief="raised", borderwidth=2)
        self.stop_btn.pack(side="left", fill="x", expand=True, padx=3)
        
        clear_btn = tk.Button(button_frame, text="🗑️ Clear Log", 
                             command=self.clear_log, 
                             font=("Arial", 12), 
                             cursor="hand2", pady=10,
                             relief="raised", borderwidth=2)
        clear_btn.pack(side="left", fill="x", expand=True, padx=3)
    
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_path.set(folder)
    
    def convert_facebook_ids(self):
        """Convert Facebook post IDs to full URLs"""
        content = self.url_text.get("1.0", tk.END).strip()
        
        if not content:
            messagebox.showwarning("No Content", "Please paste Facebook post IDs first")
            return
        
        lines = content.split('\n')
        converted_urls = []
        converted_count = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if it's a numeric ID
            if line.isdigit() and len(line) >= 10:
                converted_urls.append(f"https://www.facebook.com/reel/{line}")
                converted_count += 1
            else:
                # Keep as is if already a URL
                converted_urls.append(line)
        
        if converted_count > 0:
            # Replace content with converted URLs
            self.url_text.delete("1.0", tk.END)
            self.url_text.insert("1.0", '\n'.join(converted_urls))
            
            self.log(f"✓ Converted {converted_count} Facebook IDs to URLs")
            self.file_status.config(text=f"✓ Converted {converted_count} IDs", fg="green")
            messagebox.showinfo("Success", f"Converted {converted_count} Facebook post IDs to full URLs!")
        else:
            messagebox.showinfo("No Conversion Needed", "No Facebook post IDs found to convert")
    
    def load_urls_from_file(self):
        """Load URLs from a text file"""
        file_path = filedialog.askopenfilename(
            title="Select URLs File",
            filetypes=[
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ],
            initialdir=os.path.expanduser("~")
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Clear existing content and insert new
                self.url_text.delete("1.0", tk.END)
                self.url_text.insert("1.0", content)
                
                # Count URLs
                urls = self.extract_urls(content)
                self.loaded_file_path = file_path
                
                # Count by platform
                platform_counts = self.count_urls_by_platform(urls)
                
                # Update status
                file_name = os.path.basename(file_path)
                status_text = f"✓ {file_name} ({len(urls)} URLs: "
                status_parts = []
                if platform_counts['facebook'] > 0:
                    status_parts.append(f"{platform_counts['facebook']} FB")
                if platform_counts['tiktok'] > 0:
                    status_parts.append(f"{platform_counts['tiktok']} TikTok")
                if platform_counts['youtube'] > 0:
                    status_parts.append(f"{platform_counts['youtube']} YT")
                status_text += ", ".join(status_parts) + ")"
                
                self.file_status.config(text=status_text, fg="green")
                
                self.log(f"✓ Loaded {len(urls)} URLs from: {file_name}")
                for platform, count in platform_counts.items():
                    if count > 0:
                        self.log(f"  • {platform.capitalize()}: {count} URLs")
                
            except Exception as e:
                self.file_status.config(text="✗ Error loading file", fg="red")
                messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
    
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        self.stats_label.config(text="Downloaded: 0 | Failed: 0 | Total: 0")
    
    def update_status(self, message, color="black"):
        self.status_label.config(text=message, fg=color)
    
    def update_stats(self, downloaded, failed, total):
        self.stats_label.config(
            text=f"Downloaded: {downloaded} | Failed: {failed} | Total: {total}"
        )
    
    def check_dependencies(self):
        """Check if yt-dlp is installed and enable/disable download button accordingly"""
        self.log("🔍 Checking dependencies...")
        try:
            import yt_dlp
            self.yt_dlp = yt_dlp
            version = yt_dlp.version.__version__
            self.log(f"✓ yt-dlp is installed (version: {version})")
            self.log(f"✓ Ready to download from Facebook, TikTok & YouTube")
            
            # Enable download button
            self.download_btn.config(state="normal", bg="#4CAF50")
            self.log(f"✓ Download button ENABLED and ready!")
            return True
            
        except ImportError:
            self.log("✗ yt-dlp is NOT installed")
            self.log("\n⚠️ To install yt-dlp, run:")
            self.log("  pip install yt-dlp")
            self.log("\n📌 Download button will remain disabled until yt-dlp is installed")
            
            # Keep download button disabled
            self.download_btn.config(state="disabled", bg="#cccccc")
            
            messagebox.showerror("Dependency Missing", 
                                 "yt-dlp is required but not installed.\n\n"
                                 "Please install it using:\n\n"
                                 "pip install yt-dlp\n\n"
                                 "Then restart the application.")
            return False
    
    def detect_platform(self, url):
        """Detect which platform the URL is from"""
        url_lower = url.lower()
        
        if any(x in url_lower for x in ['facebook.com', 'fb.watch', 'fb.com']):
            return 'facebook'
        elif any(x in url_lower for x in ['tiktok.com', 'vm.tiktok.com']):
            return 'tiktok'
        elif any(x in url_lower for x in ['youtube.com', 'youtu.be']):
            return 'youtube'
        else:
            return 'unknown'
    
    def count_urls_by_platform(self, urls):
        """Count URLs by platform"""
        counts = {'facebook': 0, 'tiktok': 0, 'youtube': 0, 'unknown': 0}
        for url in urls:
            platform = self.detect_platform(url)
            counts[platform] += 1
        return counts
    
    def extract_urls(self, text):
        """Extract all valid URLs from text and convert Facebook IDs"""
        urls = []
        lines = text.strip().split('\n')
        
        # Regex pattern for URLs
        url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is just a Facebook post ID (numbers only)
            if line.isdigit() and len(line) >= 10:
                # Convert Facebook ID to reel URL
                fb_url = f"https://www.facebook.com/reel/{line}"
                urls.append(fb_url)
                self.log(f"  ℹ️ Converted FB ID {line[:20]}... to URL")
                continue
            
            # Find URLs in the line
            found_urls = url_pattern.findall(line)
            
            if found_urls:
                urls.extend(found_urls)
            elif any(domain in line for domain in ['facebook.com', 'tiktok.com', 'youtube.com', 'youtu.be', 'fb.watch', 'vm.tiktok']):
                # Try to fix URL without http
                if not line.startswith('http'):
                    line = 'https://' + line
                urls.append(line)
        
        return urls
    
    def start_download(self):
        """Start the download process"""
        self.log("\n📘 Download button clicked!")
        
        if not self.yt_dlp:
            self.log("❌ yt-dlp not available")
            messagebox.showerror("Error", "yt-dlp is not available. Please install it:\npip install yt-dlp")
            return
        
        url_text = self.url_text.get("1.0", tk.END).strip()
        
        self.log(f"🔍 Checking URL text... Length: {len(url_text)}")
        
        if not url_text:
            self.log("❌ No URLs entered")
            messagebox.showerror("Error", "Please enter at least one video URL")
            return
        
        urls = self.extract_urls(url_text)
        
        self.log(f"🔍 Extracted {len(urls)} URLs")
        
        if not urls:
            self.log("❌ No valid URLs found")
            messagebox.showerror("Error", "No valid URLs found. Please check your input.")
            return
        
        # Log first few URLs for debugging
        self.log(f"📋 URLs to download:")
        for i, url in enumerate(urls[:3], 1):
            self.log(f"  {i}. {url[:60]}...")
        if len(urls) > 3:
            self.log(f"  ... and {len(urls) - 3} more")
        
        # Count by platform
        platform_counts = self.count_urls_by_platform(urls)
        
        # Confirm before starting
        msg = f"Found {len(urls)} video(s) to download:\n\n"
        if platform_counts['facebook'] > 0:
            msg += f"📘 Facebook: {platform_counts['facebook']}\n"
        if platform_counts['tiktok'] > 0:
            msg += f"🎵 TikTok: {platform_counts['tiktok']}\n"
        if platform_counts['youtube'] > 0:
            msg += f"📺 YouTube: {platform_counts['youtube']}\n"
        if platform_counts['unknown'] > 0:
            msg += f"❓ Unknown: {platform_counts['unknown']}\n"
        
        msg += f"\nQuality: {self.quality_var.get()}\n"
        msg += f"\nProceed with download?"
        
        self.log(f"⏳ Asking for confirmation...")
        
        if not messagebox.askyesno("Confirm Download", msg):
            self.log("❌ User cancelled download")
            return
        
        self.log("✅ User confirmed, starting download...")
        
        # Create download directory
        download_dir = self.download_path.get()
        os.makedirs(download_dir, exist_ok=True)
        
        self.is_downloading = True
        self.download_btn.config(state="disabled", bg="#cccccc")
        self.stop_btn.config(state="normal")
        self.progress_bar.start()
        
        # Start download in separate thread
        thread = threading.Thread(target=self.download_videos, args=(urls, download_dir))
        thread.daemon = True
        thread.start()
        
        self.log("🚀 Download thread started!")
    
    def stop_download(self):
        self.is_downloading = False
        self.update_status("Stopping...", "orange")
        self.log("\n⚠ Stop requested by user...")
    
    def progress_hook(self, d):
        if not self.is_downloading:
            raise Exception("Download cancelled by user")
        
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'N/A').strip()
            speed = d.get('_speed_str', 'N/A').strip()
            self.update_status(f"Downloading: {percent} at {speed}", "blue")
        elif d['status'] == 'finished':
            self.log(f"  ✓ Downloaded successfully")
    
    def get_ydl_opts(self, download_dir):
        """Get yt-dlp options based on quality selection"""
        quality = self.quality_var.get()
        
        # Format selection based on quality
        if quality == 'best':
            format_str = 'best'
        else:
            format_str = f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]'
        
        return {
            'outtmpl': os.path.join(download_dir, '%(extractor)s_%(title)s_%(id)s.%(ext)s'),
            'format': format_str,
            'quiet': False,
            'no_warnings': False,
            'progress_hooks': [self.progress_hook],
            'ignoreerrors': False,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
            },
            # TikTok specific options
            'extractor_args': {
                'tiktok': {
                    'webpage_download': True
                }
            }
        }
    
    def download_single_video(self, url, download_dir, index, total, platform):
        """Download a single video"""
        platform_emoji = {
            'facebook': '📘',
            'tiktok': '🎵',
            'youtube': '📺',
            'unknown': '❓'
        }
        
        emoji = platform_emoji.get(platform, '🔹')
        self.log(f"\n[{index}/{total}] {emoji} {platform.capitalize()}: {url[:70]}...")
        
        ydl_opts = self.get_ydl_opts(download_dir)
        
        try:
            with self.yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return True
        except Exception as e:
            error_msg = str(e).replace('[0;31m', '').replace('[0m', '')
            self.log(f"  ✗ Failed: {error_msg[:100]}")
            return False
    
    def download_videos(self, urls, download_dir):
        try:
            self.log(f"\n{'='*70}")
            self.log(f"🚀 Starting download process...")
            self.log(f"📊 Total URLs: {len(urls)}")
            
            platform_counts = self.count_urls_by_platform(urls)
            for platform, count in platform_counts.items():
                if count > 0:
                    self.log(f"  • {platform.capitalize()}: {count}")
            
            self.log(f"📂 Download location: {download_dir}")
            self.log(f"🎬 Quality: {self.quality_var.get()}")
            self.log(f"{'='*70}")
            
            downloaded = 0
            failed = 0
            
            for i, url in enumerate(urls, 1):
                if not self.is_downloading:
                    self.log("\n⚠ Download stopped by user")
                    break
                
                platform = self.detect_platform(url)
                
                if self.download_single_video(url, download_dir, i, len(urls), platform):
                    downloaded += 1
                else:
                    failed += 1
                
                # Update statistics
                self.update_stats(downloaded, failed, len(urls))
            
            self.log(f"\n{'='*70}")
            if self.is_downloading:
                self.log(f"✅ Process completed!")
                self.log(f"  Successfully downloaded: {downloaded}")
                self.log(f"  Failed: {failed}")
                self.log(f"  Total processed: {len(urls)}")
                self.update_status("Download completed!", "green")
                
                msg = f"Download completed!\n\n"
                msg += f"✓ Successfully downloaded: {downloaded}\n"
                msg += f"✗ Failed: {failed}\n"
                msg += f"📊 Total: {len(urls)}\n\n"
                msg += f"📂 Location: {download_dir}"
                
                if failed > 0:
                    msg += "\n\n⚠ Some videos failed. Possible reasons:\n"
                    msg += "  • Video is private or deleted\n"
                    msg += "  • Platform blocked the request\n"
                    msg += "  • Invalid URL format\n"
                    msg += "  • Network issues"
                
                messagebox.showinfo("Completed", msg)
            else:
                self.log("⏹ Process stopped by user")
                self.update_status("Stopped", "orange")
            
        except Exception as e:
            self.log(f"\n✗ Error: {str(e)}")
            self.update_status("Error occurred", "red")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
        
        finally:
            self.reset_ui()
    
    def reset_ui(self):
        self.is_downloading = False
        self.progress_bar.stop()
        # Only enable download button if yt-dlp is available
        if self.yt_dlp:
            self.download_btn.config(state="normal", bg="#4CAF50")
        self.stop_btn.config(state="disabled")
        self.log("✓ UI reset, ready for next download")

def main():
    root = tk.Tk()
    app = UniversalShortsDownloader(root)
    root.mainloop()

if __name__ == "__main__":
    main()