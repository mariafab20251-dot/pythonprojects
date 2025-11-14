import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
from datetime import datetime

class Dashboard:
    def __init__(self, root, processor):
        self.root = root
        self.processor = processor
        self.root.title("Universal Video Text Extractor")
        self.root.geometry("800x600")
        self.stop_processing = False

        self.create_widgets()
        self.check_instagram_auth()

    def create_widgets(self):
        # Platform selection
        frame_top = tk.Frame(self.root, padx=10, pady=10)
        frame_top.pack(fill=tk.X)

        tk.Label(frame_top, text="Platform:").grid(row=0, column=0, sticky=tk.W)
        self.platform_var = tk.StringVar(value="instagram")
        platform_combo = ttk.Combobox(frame_top, textvariable=self.platform_var,
                                       values=["instagram", "tiktok", "youtube", "facebook"],
                                       state="readonly", width=15)
        platform_combo.grid(row=0, column=1, padx=5)

        tk.Label(frame_top, text="Instagram Auth:").grid(row=0, column=2, padx=(20,5))
        self.auth_label = tk.Label(frame_top, text="❌ Not logged in", fg="red")
        self.auth_label.grid(row=0, column=3)

        self.login_btn = tk.Button(frame_top, text="Login", command=self.show_instagram_login,
                                    bg="#9C27B0", fg="white", width=8)
        self.login_btn.grid(row=0, column=4, padx=5)

        # Input field
        frame_input = tk.Frame(self.root, padx=10, pady=5)
        frame_input.pack(fill=tk.X)

        tk.Label(frame_input, text="Input URL/Channel/IDs:").pack(anchor=tk.W)
        self.input_text = tk.Entry(frame_input, width=80)
        self.input_text.pack(fill=tk.X, pady=5)

        # Buttons
        frame_buttons = tk.Frame(self.root, padx=10, pady=5)
        frame_buttons.pack(fill=tk.X)

        self.process_btn = tk.Button(frame_buttons, text="Process URLs", command=self.process_input,
                                      bg="#4CAF50", fg="white", width=12)
        self.process_btn.pack(side=tk.LEFT, padx=5)

        self.browse_btn = tk.Button(frame_buttons, text="Browse Folder", command=self.browse_folder,
                                     bg="#FF9800", fg="white", width=12)
        self.browse_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = tk.Button(frame_buttons, text="Stop", command=self.stop_process,
                                  bg="#f44336", fg="white", width=10, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.clear_log_btn = tk.Button(frame_buttons, text="Clear Log", command=self.clear_log,
                                        bg="#9E9E9E", fg="white", width=10)
        self.clear_log_btn.pack(side=tk.LEFT, padx=5)

        self.export_btn = tk.Button(frame_buttons, text="Export", command=self.export_data,
                                     bg="#2196F3", fg="white", width=10)
        self.export_btn.pack(side=tk.LEFT, padx=5)

        # Progress bar
        frame_progress = tk.Frame(self.root, padx=10, pady=5)
        frame_progress.pack(fill=tk.X)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(frame_progress, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X)

        # Activity log
        frame_log = tk.Frame(self.root, padx=10, pady=5)
        frame_log.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame_log, text="Activity Log:").pack(anchor=tk.W)
        self.log_text = scrolledtext.ScrolledText(frame_log, height=20, state=tk.DISABLED,
                                                   bg="#f5f5f5", fg="#333")
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def stop_process(self):
        self.stop_processing = True
        self.log("🛑 Stop requested - will stop after current video...")

    def process_input(self):
        url_input = self.input_text.get().strip()
        if not url_input:
            messagebox.showwarning("Input Required", "Please enter a URL, channel, or video IDs")
            return

        platform = self.platform_var.get()

        self.stop_processing = False
        self.process_btn.config(state=tk.DISABLED)
        self.browse_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.log("Starting processing...")

        thread = threading.Thread(target=self._process_thread, args=(url_input, platform))
        thread.daemon = True
        thread.start()

    def _process_thread(self, url_input, platform):
        failed_count = 0
        success_count = 0

        try:
            urls = self.processor.parse_input(url_input, platform)
            total = len(urls)

            self.log(f"Found {total} video(s) to process")

            for idx, url in enumerate(urls, 1):
                if self.stop_processing:
                    self.log("❌ Processing stopped by user")
                    break

                self.log(f"Processing {idx}/{total}: {url}")

                try:
                    # Check if already processed
                    if self.processor.db.is_processed(url):
                        response = messagebox.askyesno(
                            "Already Processed",
                            f"This video has already been processed:\n{url}\n\nDo you want to reprocess it?",
                            parent=self.root
                        )
                        if not response:
                            self.log(f"⏭️ Skipping (user chose not to reprocess)")
                            success_count += 1
                            progress = (idx / total) * 100
                            self.progress_var.set(progress)
                            continue

                        # User wants to reprocess
                        self.log(f"♻️ Reprocessing video...")
                        result = self.processor.process_video(url, platform, self.log, force_reprocess=True)
                    else:
                        result = self.processor.process_video(url, platform, self.log)

                    if result != "skipped":
                        success_count += 1
                except Exception as e:
                    failed_count += 1
                    self.log(f"❌ Skipping to next video")

                progress = (idx / total) * 100
                self.progress_var.set(progress)

            self.log(f"✅ Processing complete: {success_count} succeeded, {failed_count} failed")
            self.progress_var.set(0)

            # Auto-generate Excel report
            if success_count > 0:
                self.log("📊 Generating Excel report...")
                try:
                    excel_path = self.processor.exporter.generate_excel_report(
                        channel_folder=self.processor.current_channel_folder
                    )
                    if excel_path:
                        self.log(f"✅ Excel report created: {excel_path}")
                    else:
                        self.log("⚠️  Excel report not generated (pandas/openpyxl may not be installed)")
                except Exception as e:
                    self.log(f"⚠️  Excel generation failed: {str(e)}")

        except Exception as e:
            self.log(f"❌ Fatal error: {str(e)}")
        finally:
            self.process_btn.config(state=tk.NORMAL)
            self.browse_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

    def browse_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder with Downloaded Videos")

        if not folder_path:
            return

        self.log(f"📁 Selected folder: {folder_path}")

        self.stop_processing = False
        self.process_btn.config(state=tk.DISABLED)
        self.browse_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        thread = threading.Thread(target=self._process_folder_thread, args=(folder_path,))
        thread.daemon = True
        thread.start()

    def _process_folder_thread(self, folder_path):
        import os
        from pathlib import Path

        failed_count = 0
        success_count = 0

        try:
            # Get all video files from folder
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

                try:
                    result = self.processor.process_local_video(str(video_path), self.log)
                    if result != "skipped":
                        success_count += 1
                except Exception as e:
                    failed_count += 1
                    self.log(f"❌ Failed: {str(e)}")

                progress = (idx / total) * 100
                self.progress_var.set(progress)

            self.log(f"✅ Processing complete: {success_count} succeeded, {failed_count} failed")
            self.progress_var.set(0)

            # Auto-generate Excel report for local folder processing
            if success_count > 0:
                self.log("📊 Generating Excel report...")
                try:
                    excel_path = self.processor.exporter.generate_excel_report()
                    if excel_path:
                        self.log(f"✅ Excel report created: {excel_path}")
                    else:
                        self.log("⚠️  Excel report not generated (pandas/openpyxl may not be installed)")
                except Exception as e:
                    self.log(f"⚠️  Excel generation failed: {str(e)}")

        except Exception as e:
            self.log(f"❌ Fatal error: {str(e)}")
        finally:
            self.process_btn.config(state=tk.NORMAL)
            self.browse_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

    def export_data(self):
        """Manually trigger Excel report generation"""
        self.log("📊 Generating Excel report...")
        try:
            excel_path = self.processor.exporter.generate_excel_report()
            if excel_path:
                self.log(f"✅ Excel report created: {excel_path}")
                messagebox.showinfo("Export Complete", f"Excel report created:\n{excel_path}")
            else:
                self.log("⚠️  Excel report not generated")
                messagebox.showwarning("Export Failed",
                    "Could not generate Excel report.\n\n"
                    "Make sure pandas and openpyxl are installed:\n"
                    "pip install pandas openpyxl")
        except Exception as e:
            self.log(f"❌ Excel generation failed: {str(e)}")
            messagebox.showerror("Export Error", f"Failed to generate Excel report:\n{str(e)}")

    def check_instagram_auth(self):
        """Check if Instagram session exists"""
        from pathlib import Path
        session_file = Path(__file__).parent.parent / "data" / "ig_session"
        cookies_file = Path(__file__).parent.parent / "data" / "cookies.txt"

        if session_file.exists():
            self.auth_label.config(text="✅ Logged in (session)", fg="green")
            self.log("Instagram: Authenticated (session found)")
        elif cookies_file.exists():
            self.auth_label.config(text="✅ Auth (cookies.txt)", fg="green")
            self.log("Instagram: Authenticated (cookies.txt found)")
        else:
            self.auth_label.config(text="❌ Not logged in", fg="red")

    def show_instagram_login(self):
        """Show Instagram login dialog"""
        login_window = tk.Toplevel(self.root)
        login_window.title("Instagram Login")
        login_window.geometry("400x250")
        login_window.resizable(False, False)

        # Center the window
        login_window.transient(self.root)
        login_window.grab_set()

        # Header
        header = tk.Label(login_window, text="Instagram Authentication",
                         font=("Arial", 14, "bold"), pady=10)
        header.pack()

        info = tk.Label(login_window, text="Login to enable profile scraping",
                       fg="gray")
        info.pack()

        # Form frame
        form_frame = tk.Frame(login_window, padx=20, pady=20)
        form_frame.pack()

        tk.Label(form_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        username_entry = tk.Entry(form_frame, width=30)
        username_entry.grid(row=0, column=1, pady=5)

        tk.Label(form_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        password_entry = tk.Entry(form_frame, width=30, show="*")
        password_entry.grid(row=1, column=1, pady=5)

        # Status label
        status_label = tk.Label(login_window, text="", fg="red")
        status_label.pack(pady=5)

        # Buttons
        button_frame = tk.Frame(login_window)
        button_frame.pack(pady=10)

        def do_login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()

            if not username or not password:
                status_label.config(text="Please enter both username and password", fg="red")
                return

            status_label.config(text="Logging in...", fg="blue")
            login_window.update()

            try:
                scraper = self.processor.scrapers['instagram']
                scraper.login(username, password)

                status_label.config(text="✅ Login successful!", fg="green")
                self.auth_label.config(text="✅ Logged in (session)", fg="green")
                self.log("✅ Instagram login successful")

                login_window.after(1000, login_window.destroy)
            except Exception as e:
                status_label.config(text=f"Login failed: {str(e)}", fg="red")
                self.log(f"❌ Instagram login failed: {str(e)}")

        login_btn = tk.Button(button_frame, text="Login", command=do_login,
                             bg="#4CAF50", fg="white", width=12)
        login_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = tk.Button(button_frame, text="Cancel", command=login_window.destroy,
                              bg="#f44336", fg="white", width=12)
        cancel_btn.pack(side=tk.LEFT, padx=5)

        username_entry.focus()
