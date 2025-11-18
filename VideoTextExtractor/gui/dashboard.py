import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
from datetime import datetime
from pathlib import Path

class Dashboard:
    def __init__(self, root, processor):
        self.root = root
        self.processor = processor
        self.root.title("Video Text Extractor - Professional Edition")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        self.stop_processing = False

        # Feature selections
        self.features = {
            'download_video': tk.BooleanVar(value=True),
            'extract_ocr': tk.BooleanVar(value=True),
            'extract_speech': tk.BooleanVar(value=True),
            'extract_metadata': tk.BooleanVar(value=True),
            'auto_excel': tk.BooleanVar(value=True),
        }

        self.create_modern_ui()
        self.check_instagram_auth()

    def create_modern_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="🎥 Video Text Extractor",
                font=("Arial", 18, "bold"), bg='#2c3e50', fg='white').pack(side=tk.LEFT, padx=20, pady=15)

        # Platform selector in header
        tk.Label(header_frame, text="Platform:", bg='#2c3e50', fg='white',
                font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.platform_var = tk.StringVar(value="youtube")
        platform_combo = ttk.Combobox(header_frame, textvariable=self.platform_var,
                                     values=["youtube", "tiktok", "instagram", "facebook"],
                                     state="readonly", width=12)
        platform_combo.pack(side=tk.LEFT, padx=5)

        # Instagram auth status in header
        self.auth_label = tk.Label(header_frame, text="", bg='#2c3e50', fg='white', font=("Arial", 9))
        self.auth_label.pack(side=tk.RIGHT, padx=20)

        # Main content area with tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Quick Process
        self.quick_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.quick_tab, text="  Quick Process  ")
        self.create_quick_tab()

        # Tab 2: Metadata Scan
        self.metadata_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.metadata_tab, text="  Metadata Scan  ")
        self.create_metadata_tab()

        # Tab 3: Settings
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="  Settings  ")
        self.create_settings_tab()

        # Tab 4: Activity Log
        self.log_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.log_tab, text="  Activity Log  ")
        self.create_log_tab()

        # Status bar at bottom
        self.create_status_bar()

    def create_quick_tab(self):
        """Quick Process tab - for immediate video processing"""
        # Input Section
        input_section = tk.LabelFrame(self.quick_tab, text="📥 Input Source",
                                     font=("Arial", 11, "bold"), padx=15, pady=15)
        input_section.pack(fill=tk.X, padx=10, pady=10)

        # URL Input
        tk.Label(input_section, text="Video URLs or Channel:",
                font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)

        url_frame = tk.Frame(input_section)
        url_frame.grid(row=1, column=0, columnspan=3, sticky=tk.EW, pady=5)

        self.input_text = tk.Entry(url_frame, font=("Arial", 10))
        self.input_text.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Button(url_frame, text="Browse File", command=self.browse_url_file,
                 bg='#607D8B', fg='white', width=12).pack(side=tk.LEFT, padx=(5, 0))

        tk.Button(url_frame, text="Browse Folder", command=self.browse_folder,
                 bg='#FF9800', fg='white', width=12).pack(side=tk.LEFT, padx=(5, 0))

        # Processing Options Section
        options_section = tk.LabelFrame(self.quick_tab, text="⚙️ Processing Options",
                                       font=("Arial", 11, "bold"), padx=15, pady=15)
        options_section.pack(fill=tk.X, padx=10, pady=10)

        # Left column - Extraction features
        left_col = tk.Frame(options_section)
        left_col.grid(row=0, column=0, sticky=tk.W, padx=10)

        tk.Label(left_col, text="Select Features to Extract:",
                font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))

        tk.Checkbutton(left_col, text="📥 Download Videos",
                      variable=self.features['download_video'],
                      font=("Arial", 10), command=self.update_feature_status).pack(anchor=tk.W, pady=2)

        tk.Checkbutton(left_col, text="🔍 OCR - Overlay Text",
                      variable=self.features['extract_ocr'],
                      font=("Arial", 10)).pack(anchor=tk.W, pady=2)

        tk.Checkbutton(left_col, text="🎤 Speech Transcription",
                      variable=self.features['extract_speech'],
                      font=("Arial", 10)).pack(anchor=tk.W, pady=2)

        tk.Checkbutton(left_col, text="📋 Metadata (Captions/Hashtags)",
                      variable=self.features['extract_metadata'],
                      font=("Arial", 10)).pack(anchor=tk.W, pady=2)

        # Right column - Output features
        right_col = tk.Frame(options_section)
        right_col.grid(row=0, column=1, sticky=tk.W, padx=50)

        tk.Label(right_col, text="Output Options:",
                font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))

        tk.Checkbutton(right_col, text="📊 Auto-generate Excel Report",
                      variable=self.features['auto_excel'],
                      font=("Arial", 10)).pack(anchor=tk.W, pady=2)

        # Feature status label
        self.feature_status = tk.Label(options_section, text="",
                                      font=("Arial", 9), fg='#666')
        self.feature_status.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        self.update_feature_status()

        # Action Buttons Section
        action_section = tk.Frame(self.quick_tab)
        action_section.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(action_section, text="▶ Process Now", command=self.process_input,
                 bg='#4CAF50', fg='white', font=("Arial", 12, "bold"),
                 height=2, width=15).pack(side=tk.LEFT, padx=5)

        tk.Button(action_section, text="⏹ Stop", command=self.stop_process,
                 bg='#f44336', fg='white', font=("Arial", 12, "bold"),
                 height=2, width=12).pack(side=tk.LEFT, padx=5)

        tk.Button(action_section, text="📊 Export Results", command=self.export_data,
                 bg='#2196F3', fg='white', font=("Arial", 11),
                 height=2, width=12).pack(side=tk.LEFT, padx=5)

        # Progress
        progress_frame = tk.LabelFrame(self.quick_tab, text="Progress",
                                      font=("Arial", 10, "bold"), padx=10, pady=10)
        progress_frame.pack(fill=tk.X, padx=10, pady=10)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                           maximum=100, length=400)
        self.progress_bar.pack(fill=tk.X)

        self.progress_label = tk.Label(progress_frame, text="Ready",
                                      font=("Arial", 9), fg='#666')
        self.progress_label.pack(pady=(5, 0))

    def create_metadata_tab(self):
        """Metadata Scan tab - for bulk metadata extraction"""
        # Info banner
        info_frame = tk.Frame(self.metadata_tab, bg='#e3f2fd', relief=tk.RAISED, borderwidth=1)
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(info_frame, text="💡 Metadata Scan: Quickly extract metadata from entire channels without downloading videos",
                bg='#e3f2fd', font=("Arial", 10, "italic"), fg='#1976d2').pack(pady=10, padx=10)

        # Scan section
        scan_section = tk.LabelFrame(self.metadata_tab, text="🔍 Metadata Scanner",
                                    font=("Arial", 11, "bold"), padx=15, pady=15)
        scan_section.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(scan_section, text="Channel/Profile URL:",
                font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=5)

        self.metadata_url = tk.Entry(scan_section, font=("Arial", 10))
        self.metadata_url.pack(fill=tk.X, pady=5)

        # Platform info
        platform_info_frame = tk.Frame(scan_section)
        platform_info_frame.pack(fill=tk.X, pady=10)

        tk.Label(platform_info_frame, text="✅ YouTube: Unlimited videos, fast",
                font=("Arial", 9), fg='green').pack(anchor=tk.W, padx=20)
        tk.Label(platform_info_frame, text="✅ TikTok: Unlimited videos, fast",
                font=("Arial", 9), fg='green').pack(anchor=tk.W, padx=20)
        tk.Label(platform_info_frame, text="⚠️ Instagram: Max 50 videos, requires login",
                font=("Arial", 9), fg='orange').pack(anchor=tk.W, padx=20)
        tk.Label(platform_info_frame, text="⚠️ Facebook: Public pages only, less reliable",
                font=("Arial", 9), fg='orange').pack(anchor=tk.W, padx=20)

        # Scan button
        scan_btn_frame = tk.Frame(scan_section)
        scan_btn_frame.pack(pady=20)

        tk.Button(scan_btn_frame, text="🚀 Start Metadata Scan",
                 command=self.start_metadata_scan,
                 bg='#673AB7', fg='white', font=("Arial", 12, "bold"),
                 height=2, width=20).pack()

        # Results info
        results_frame = tk.LabelFrame(scan_section, text="📊 What You'll Get",
                                     font=("Arial", 10, "bold"))
        results_frame.pack(fill=tk.X, pady=10)

        tk.Label(results_frame, text="• Excel file with all video metadata (titles, URLs, durations)",
                font=("Arial", 9)).pack(anchor=tk.W, padx=10, pady=2)
        tk.Label(results_frame, text="• TXT file with all URLs for batch processing",
                font=("Arial", 9)).pack(anchor=tk.W, padx=10, pady=2)
        tk.Label(results_frame, text="• Load URLs with 'Browse File' for selective processing",
                font=("Arial", 9)).pack(anchor=tk.W, padx=10, pady=2)

    def create_settings_tab(self):
        """Settings tab - platform settings and preferences"""
        # Instagram Settings
        ig_section = tk.LabelFrame(self.settings_tab, text="📱 Instagram Settings",
                                  font=("Arial", 11, "bold"), padx=15, pady=15)
        ig_section.pack(fill=tk.X, padx=10, pady=10)

        status_frame = tk.Frame(ig_section)
        status_frame.pack(fill=tk.X, pady=5)

        tk.Label(status_frame, text="Authentication Status:",
                font=("Arial", 10, "bold")).pack(side=tk.LEFT)

        self.ig_status_label = tk.Label(status_frame, text="Not logged in",
                                       font=("Arial", 10), fg='red')
        self.ig_status_label.pack(side=tk.LEFT, padx=10)

        tk.Button(ig_section, text="🔐 Login to Instagram",
                 command=self.show_instagram_login,
                 bg='#9C27B0', fg='white', font=("Arial", 10, "bold"),
                 width=20).pack(pady=10)

        tk.Label(ig_section, text="Note: Instagram login is required for profile scanning and metadata extraction",
                font=("Arial", 9, "italic"), fg='#666').pack()

        # General Settings
        general_section = tk.LabelFrame(self.settings_tab, text="⚙️ General Settings",
                                       font=("Arial", 11, "bold"), padx=15, pady=15)
        general_section.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(general_section, text="Default Settings:",
                font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=5)

        tk.Label(general_section, text="• Videos save to: channels/platform/channelname/videos/",
                font=("Arial", 9)).pack(anchor=tk.W, padx=20, pady=2)
        tk.Label(general_section, text="• Results save to: channels/platform/channelname/",
                font=("Arial", 9)).pack(anchor=tk.W, padx=20, pady=2)
        tk.Label(general_section, text="• Excel reports auto-generated after processing",
                font=("Arial", 9)).pack(anchor=tk.W, padx=20, pady=2)

    def create_log_tab(self):
        """Activity Log tab"""
        log_frame = tk.Frame(self.log_tab)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Log controls
        control_frame = tk.Frame(log_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(control_frame, text="Activity Log",
                font=("Arial", 11, "bold")).pack(side=tk.LEFT)

        tk.Button(control_frame, text="Clear Log", command=self.clear_log,
                 bg='#9E9E9E', fg='white').pack(side=tk.RIGHT, padx=5)

        # Log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, height=25,
                                                  bg='#f5f5f5', fg='#333',
                                                  font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def create_status_bar(self):
        """Status bar at bottom"""
        self.status_bar = tk.Frame(self.root, bg='#34495e', height=30)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)

        self.status_label = tk.Label(self.status_bar, text="Ready",
                                     bg='#34495e', fg='white',
                                     font=("Arial", 9), anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=10)

    def update_feature_status(self):
        """Update the feature status label"""
        download = self.features['download_video'].get()
        ocr = self.features['extract_ocr'].get()
        speech = self.features['extract_speech'].get()
        metadata = self.features['extract_metadata'].get()

        if not download and (ocr or speech):
            self.feature_status.config(
                text="⚠️ Warning: OCR and Speech require video download",
                fg='orange'
            )
        elif not any([ocr, speech, metadata]):
            self.feature_status.config(
                text="⚠️ Select at least one extraction feature",
                fg='red'
            )
        elif download and ocr and speech and metadata:
            self.feature_status.config(
                text="✅ Full extraction mode: All features enabled",
                fg='green'
            )
        elif not download:
            self.feature_status.config(
                text="📝 Metadata-only mode: Fast extraction without downloads",
                fg='blue'
            )
        else:
            enabled = []
            if ocr: enabled.append("OCR")
            if speech: enabled.append("Speech")
            if metadata: enabled.append("Metadata")
            self.feature_status.config(
                text=f"Enabled: {', '.join(enabled)}",
                fg='green'
            )

    def log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.status_label.config(text=message[:80])

    def clear_log(self):
        """Clear the log"""
        self.log_text.delete(1.0, tk.END)

    def stop_process(self):
        """Stop processing"""
        self.stop_processing = True
        self.log("🛑 Stop requested - will stop after current video...")

    def browse_url_file(self):
        """Browse and load URLs from file"""
        file_path = filedialog.askopenfilename(
            title="Select URL List File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            urls = []
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    if ',' in line:
                        urls.extend([u.strip() for u in line.split(',') if u.strip()])
                    else:
                        urls.append(line)

            if not urls:
                messagebox.showwarning("Empty File", "No URLs found in the file.")
                return

            # Detect channel folder from path
            file_path_obj = Path(file_path)
            if 'channels' in file_path_obj.parts:
                try:
                    channels_idx = file_path_obj.parts.index('channels')
                    if len(file_path_obj.parts) > channels_idx + 2:
                        platform = file_path_obj.parts[channels_idx + 1]
                        channel_name = file_path_obj.parts[channels_idx + 2]
                        channel_folder = file_path_obj.parent

                        self.processor.current_channel_folder = channel_folder
                        self.log(f"📁 Detected channel folder: {platform}/{channel_name}")
                except (ValueError, IndexError):
                    pass

            self.input_text.delete(0, tk.END)
            self.input_text.insert(0, ', '.join(urls))
            self.log(f"📁 Loaded {len(urls)} URL(s) from file: {file_path_obj.name}")

        except Exception as e:
            messagebox.showerror("File Error", f"Failed to read file:\n{str(e)}")
            self.log(f"❌ Failed to load URL file: {str(e)}")

    def browse_folder(self):
        """Browse folder for local videos"""
        folder_path = filedialog.askdirectory(title="Select Folder with Downloaded Videos")

        if not folder_path:
            return

        self.log(f"📁 Selected folder: {folder_path}")

        self.stop_processing = False
        self.progress_label.config(text="Processing folder...")

        thread = threading.Thread(target=self._process_folder_thread, args=(folder_path,))
        thread.daemon = True
        thread.start()

    def process_input(self):
        """Process URLs from input"""
        url_input = self.input_text.get().strip()
        if not url_input:
            messagebox.showwarning("Input Required", "Please enter a URL, channel, or video IDs")
            return

        platform = self.platform_var.get()

        self.stop_processing = False
        self.progress_label.config(text="Starting processing...")
        self.log("Starting processing...")

        thread = threading.Thread(target=self._process_thread, args=(url_input, platform))
        thread.daemon = True
        thread.start()

    def _process_thread(self, url_input, platform):
        """Processing thread"""
        failed_count = 0
        success_count = 0

        try:
            urls = self.processor.parse_input(url_input, platform)
            total = len(urls)

            self.log(f"Found {total} video(s) to process")

            # Get feature selections
            download_video = self.features['download_video'].get()

            for idx, url in enumerate(urls, 1):
                if self.stop_processing:
                    self.log("❌ Processing stopped by user")
                    break

                self.log(f"Processing {idx}/{total}: {url}")
                self.progress_var.set((idx / total) * 100)
                self.progress_label.config(text=f"Processing {idx}/{total}")

                try:
                    if self.processor.db.is_processed(url):
                        response = messagebox.askyesno(
                            "Already Processed",
                            f"This video has already been processed:\n{url}\n\nDo you want to reprocess it?",
                            parent=self.root
                        )
                        if not response:
                            self.log(f"⏭️ Skipping (user chose not to reprocess)")
                            success_count += 1
                            continue

                        self.log(f"♻️ Reprocessing video...")
                        result = self.processor.process_video(
                            url, platform, self.log,
                            force_reprocess=True,
                            download_video=download_video
                        )
                    else:
                        result = self.processor.process_video(
                            url, platform, self.log,
                            download_video=download_video
                        )

                    if result != "skipped":
                        success_count += 1
                except Exception as e:
                    failed_count += 1
                    self.log(f"❌ Skipping to next video")

            self.log(f"✅ Processing complete: {success_count} succeeded, {failed_count} failed")
            self.progress_var.set(0)
            self.progress_label.config(text="Complete!")

            # Auto-generate Excel if enabled
            if success_count > 0 and self.features['auto_excel'].get():
                self.log("📊 Generating Excel report...")
                try:
                    excel_path = self.processor.exporter.generate_excel_report(
                        channel_folder=self.processor.current_channel_folder
                    )
                    if excel_path:
                        self.log(f"✅ Excel report created: {excel_path}")
                except Exception as e:
                    self.log(f"⚠️  Excel generation failed: {str(e)}")

        except Exception as e:
            self.log(f"❌ Fatal error: {str(e)}")
        finally:
            self.progress_label.config(text="Ready")

    def _process_folder_thread(self, folder_path):
        """Process folder thread"""
        from pathlib import Path

        failed_count = 0
        success_count = 0

        try:
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']
            video_files = []

            for ext in video_extensions:
                video_files.extend(Path(folder_path).glob(f'*{ext}'))

            if not video_files:
                self.log("❌ No video files found in folder")
                return

            total = len(video_files)
            self.log(f"Found {total} video file(s) to process")

            for idx, video_path in enumerate(video_files, 1):
                if self.stop_processing:
                    self.log("❌ Processing stopped by user")
                    break

                self.log(f"Processing {idx}/{total}: {video_path.name}")
                self.progress_var.set((idx / total) * 100)

                try:
                    result = self.processor.process_local_video(str(video_path), self.log)
                    if result != "skipped":
                        success_count += 1
                except Exception as e:
                    failed_count += 1
                    self.log(f"❌ Failed: {str(e)}")

            self.log(f"✅ Processing complete: {success_count} succeeded, {failed_count} failed")
            self.progress_var.set(0)

            if success_count > 0 and self.features['auto_excel'].get():
                self.log("📊 Generating Excel report...")
                try:
                    excel_path = self.processor.exporter.generate_excel_report()
                    if excel_path:
                        self.log(f"✅ Excel report created: {excel_path}")
                except Exception as e:
                    self.log(f"⚠️  Excel generation failed: {str(e)}")

        except Exception as e:
            self.log(f"❌ Fatal error: {str(e)}")
        finally:
            self.progress_label.config(text="Ready")

    def start_metadata_scan(self):
        """Start metadata scan from Metadata tab"""
        url = self.metadata_url.get().strip()
        if not url:
            messagebox.showwarning("Input Required", "Please enter a channel/playlist/profile URL")
            return

        # Switch to log tab to show progress
        self.notebook.select(self.log_tab)

        platform = self.platform_var.get()

        # Platform-specific checks
        if platform == 'instagram':
            session_file = Path(__file__).parent.parent / "data" / "ig_session"
            if not session_file.exists():
                messagebox.showwarning(
                    "Instagram Login Required",
                    "Please login via Settings tab first"
                )
                return

        self.log("🔍 Starting metadata scan...")

        thread = threading.Thread(target=self._metadata_scan_thread,
                                 args=(url, platform))
        thread.daemon = True
        thread.start()

    def _metadata_scan_thread(self, url_input, platform):
        """Metadata scan thread"""
        from core.metadata_scanner import MetadataScanner
        import re
        from config import BASE_DIR

        try:
            scanner = MetadataScanner()

            self.log(f"📡 Scanning: {url_input}")

            if platform == 'youtube':
                result = scanner.scan_youtube_channel(
                    url_input,
                    filter_shorts=False,
                    max_videos=None,
                    progress_callback=self.log
                )
            elif platform == 'tiktok':
                result = scanner.scan_tiktok_profile(
                    url_input,
                    max_videos=None,
                    progress_callback=self.log
                )
            elif platform == 'instagram':
                result = scanner.scan_instagram_profile(
                    url_input,
                    max_videos=50,
                    progress_callback=self.log
                )
            elif platform == 'facebook':
                result = scanner.scan_facebook_page(
                    url_input,
                    max_videos=None,
                    progress_callback=self.log
                )

            channel_name = result.get('channel_name', 'Unknown')
            videos = result.get('videos', [])
            self.log(f"✅ Found {len(videos)} videos from {channel_name}")

            # Auto-create channel folder structure
            safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', channel_name)
            safe_name = safe_name[:50]  # Limit length

            channel_folder = BASE_DIR / "channels" / platform / safe_name
            channel_folder.mkdir(parents=True, exist_ok=True)

            # Create subfolders
            videos_folder = channel_folder / "videos"
            reports_folder = channel_folder / "reports"
            videos_folder.mkdir(exist_ok=True)
            reports_folder.mkdir(exist_ok=True)

            self.log(f"📁 Auto-created folder: channels/{platform}/{safe_name}/")

            # Export with channel name in filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            self.log("📊 Exporting to Excel...")
            excel_file = channel_folder / f"metadata_{safe_name}_{timestamp}.xlsx"
            scanner.export_to_excel([result], str(excel_file))
            self.log(f"✅ Excel created: {excel_file.name}")

            self.log("📝 Exporting URLs to TXT...")
            txt_file = channel_folder / f"urls_{safe_name}_{timestamp}.txt"
            scanner.export_urls_to_txt([result], str(txt_file))
            self.log(f"✅ URL list created: {txt_file.name}")

            self.log(f"{'='*50}")
            self.log(f"✅ Metadata scan complete!")
            self.log(f"📁 Results saved to: {channel_folder}")
            self.log(f"{'='*50}")

            # Ask to load URLs
            def ask_load():
                if messagebox.askyesno(
                    "Scan Complete",
                    f"Metadata scan complete!\n\n"
                    f"✅ Channel: {channel_name}\n"
                    f"🎥 {len(videos)} video(s) found\n"
                    f"📁 Saved to: channels/{platform}/{safe_name}/\n\n"
                    f"Load URLs for processing?",
                    parent=self.root
                ):
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        urls = [line.strip() for line in f if line.strip()]

                    self.processor.current_channel_folder = channel_folder
                    self.input_text.delete(0, tk.END)
                    self.input_text.insert(0, ', '.join(urls))
                    self.log(f"📥 Loaded {len(urls)} URLs into input field")

                    # Switch to Quick Process tab
                    self.notebook.select(0)

            self.root.after(100, ask_load)

        except Exception as e:
            self.log(f"❌ Metadata scan error: {str(e)}")

    def export_data(self):
        """Export data to Excel"""
        self.log("📊 Generating Excel report...")
        try:
            excel_path = self.processor.exporter.generate_excel_report()
            if excel_path:
                self.log(f"✅ Excel report created: {excel_path}")
                messagebox.showinfo("Export Complete", f"Excel report created:\n{excel_path}")
        except Exception as e:
            self.log(f"❌ Excel generation failed: {str(e)}")
            messagebox.showerror("Export Error", f"Failed to generate Excel report:\n{str(e)}")

    def check_instagram_auth(self):
        """Check Instagram authentication status"""
        session_file = Path(__file__).parent.parent / "data" / "ig_session"
        cookies_file = Path(__file__).parent.parent / "data" / "cookies.txt"

        if session_file.exists():
            self.auth_label.config(text="✅ Instagram: Logged in")
            self.ig_status_label.config(text="✅ Logged in", fg='green')
            self.log("Instagram: Authenticated (session found)")
        elif cookies_file.exists():
            self.auth_label.config(text="✅ Instagram: Auth (cookies)")
            self.ig_status_label.config(text="✅ Auth (cookies.txt)", fg='green')
            self.log("Instagram: Authenticated (cookies.txt found)")
        else:
            self.auth_label.config(text="❌ Instagram: Not logged in")
            self.ig_status_label.config(text="❌ Not logged in", fg='red')

    def show_instagram_login(self):
        """Show Instagram login dialog"""
        login_window = tk.Toplevel(self.root)
        login_window.title("Instagram Login")
        login_window.geometry("400x250")
        login_window.resizable(False, False)
        login_window.transient(self.root)
        login_window.grab_set()

        tk.Label(login_window, text="Instagram Authentication",
                font=("Arial", 14, "bold")).pack(pady=20)

        form_frame = tk.Frame(login_window, padx=20, pady=10)
        form_frame.pack()

        tk.Label(form_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        username_entry = tk.Entry(form_frame, width=30)
        username_entry.grid(row=0, column=1, pady=5)

        tk.Label(form_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        password_entry = tk.Entry(form_frame, width=30, show="*")
        password_entry.grid(row=1, column=1, pady=5)

        status_label = tk.Label(login_window, text="", fg="red")
        status_label.pack(pady=5)

        def do_login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()

            if not username or not password:
                status_label.config(text="Please enter both username and password")
                return

            status_label.config(text="Logging in...", fg="blue")
            login_window.update()

            try:
                scraper = self.processor.scrapers['instagram']
                scraper.login(username, password)

                status_label.config(text="✅ Login successful!", fg="green")
                self.check_instagram_auth()
                self.log("✅ Instagram login successful")

                login_window.after(1000, login_window.destroy)
            except Exception as e:
                status_label.config(text=f"Login failed: {str(e)}", fg="red")
                self.log(f"❌ Instagram login failed: {str(e)}")

        button_frame = tk.Frame(login_window)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Login", command=do_login,
                 bg='#4CAF50', fg='white', width=12).pack(side=tk.LEFT, padx=5)

        tk.Button(button_frame, text="Cancel", command=login_window.destroy,
                 bg='#f44336', fg='white', width=12).pack(side=tk.LEFT, padx=5)

        username_entry.focus()
