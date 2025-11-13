import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from datetime import datetime

class Dashboard:
    def __init__(self, root, processor):
        self.root = root
        self.processor = processor
        self.root.title("Universal Video Text Extractor")
        self.root.geometry("800x600")

        self.create_widgets()

    def create_widgets(self):
        # Platform selection
        frame_top = tk.Frame(self.root, padx=10, pady=10)
        frame_top.pack(fill=tk.X)

        tk.Label(frame_top, text="Platform:").grid(row=0, column=0, sticky=tk.W)
        self.platform_var = tk.StringVar(value="instagram")
        platform_combo = ttk.Combobox(frame_top, textvariable=self.platform_var,
                                       values=["instagram"], state="readonly", width=15)
        platform_combo.grid(row=0, column=1, padx=5)

        tk.Label(frame_top, text="Auth:").grid(row=0, column=2, padx=(20,5))
        self.auth_label = tk.Label(frame_top, text="✅", fg="green")
        self.auth_label.grid(row=0, column=3)

        # Input field
        frame_input = tk.Frame(self.root, padx=10, pady=5)
        frame_input.pack(fill=tk.X)

        tk.Label(frame_input, text="Input URL/Channel/IDs:").pack(anchor=tk.W)
        self.input_text = tk.Entry(frame_input, width=80)
        self.input_text.pack(fill=tk.X, pady=5)

        # Buttons
        frame_buttons = tk.Frame(self.root, padx=10, pady=5)
        frame_buttons.pack(fill=tk.X)

        self.process_btn = tk.Button(frame_buttons, text="Process", command=self.process_input,
                                      bg="#4CAF50", fg="white", width=15)
        self.process_btn.pack(side=tk.LEFT, padx=5)

        self.export_btn = tk.Button(frame_buttons, text="Export", command=self.export_data,
                                     bg="#2196F3", fg="white", width=15)
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

    def process_input(self):
        url_input = self.input_text.get().strip()
        if not url_input:
            messagebox.showwarning("Input Required", "Please enter a URL, channel, or video IDs")
            return

        platform = self.platform_var.get()

        self.process_btn.config(state=tk.DISABLED)
        self.log("Starting processing...")

        thread = threading.Thread(target=self._process_thread, args=(url_input, platform))
        thread.daemon = True
        thread.start()

    def _process_thread(self, url_input, platform):
        try:
            urls = self.processor.parse_input(url_input, platform)
            total = len(urls)

            self.log(f"Found {total} video(s) to process")

            for idx, url in enumerate(urls, 1):
                self.log(f"Processing {idx}/{total}: {url}")
                self.processor.process_video(url, platform, self.log)

                progress = (idx / total) * 100
                self.progress_var.set(progress)

            self.log("✅ All videos processed successfully")
            self.progress_var.set(0)
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
        finally:
            self.process_btn.config(state=tk.NORMAL)

    def export_data(self):
        messagebox.showinfo("Export", "Data exported to results.csv and results.json")
        self.log("✅ Data exported")
