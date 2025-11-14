import csv
import json
from pathlib import Path
from config import CSV_PATH, JSON_PATH, DATA_DIR

class DataExporter:
    def __init__(self):
        self.ensure_csv_header()
        self.reports_dir = DATA_DIR / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def ensure_csv_header(self):
        if not CSV_PATH.exists():
            with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['video_id', 'platform', 'url', 'overlay_text', 'speech_text', 'captions', 'hashtags', 'timestamp'])

    def export_to_csv(self, data, channel_folder=None):
        csv_path = CSV_PATH
        if channel_folder:
            csv_path = channel_folder / "results.csv"
            # Ensure CSV header for channel folder
            if not csv_path.exists():
                with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['video_id', 'platform', 'url', 'overlay_text', 'speech_text', 'captions', 'hashtags', 'timestamp'])

        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                data['video_id'],
                data['platform'],
                data['url'],
                data['overlay_text'],
                data['speech_text'],
                data['captions'],
                data['hashtags'],
                data['timestamp']
            ])

    def export_to_json(self, data, channel_folder=None):
        json_path = JSON_PATH
        if channel_folder:
            json_path = channel_folder / "results.json"

        existing_data = []
        if json_path.exists():
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:  # Only parse if file has content
                        existing_data = json.loads(content)
            except (json.JSONDecodeError, ValueError):
                # File is corrupted or empty, start fresh
                existing_data = []

        existing_data.append(data)

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)

    def clean_text(self, text):
        """Remove duplicate lines and clean text"""
        if not text:
            return "(No text detected)"

        lines = text.split('\n')
        seen = set()
        unique_lines = []
        for line in lines:
            line = line.strip()
            if line and line not in seen:
                seen.add(line)
                unique_lines.append(line)

        return ' '.join(unique_lines) if unique_lines else "(No text detected)"

    def export_to_txt(self, data, channel_folder=None):
        """Export individual TXT report for each video"""
        video_id = data['video_id']
        platform = data['platform'].upper()

        report = f"""
{'='*80}
VIDEO EXTRACTION REPORT
{'='*80}

Video ID:       {video_id}
Platform:       {platform}
URL:            {data['url']}
Date Processed: {data['timestamp'].split('T')[0]}

{'='*80}
OVERLAY TEXT (OCR)
{'='*80}

{self.clean_text(data['overlay_text'])}

{'='*80}
SPEECH TRANSCRIPT (WHISPER)
{'='*80}

{data['speech_text'] or '(No speech detected)'}

{'='*80}
CAPTIONS & METADATA
{'='*80}

Captions:  {data['captions'] or '(None)'}
Hashtags:  {data['hashtags'] or '(None)'}

{'='*80}
"""

        reports_dir = self.reports_dir
        if channel_folder:
            reports_dir = channel_folder / "reports"
            reports_dir.mkdir(exist_ok=True)

        txt_path = reports_dir / f"{platform}_{video_id}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(report.strip())
