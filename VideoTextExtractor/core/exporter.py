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

    def export_to_csv(self, data):
        with open(CSV_PATH, 'a', newline='', encoding='utf-8') as f:
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

    def export_to_json(self, data):
        existing_data = []
        if JSON_PATH.exists():
            with open(JSON_PATH, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)

        existing_data.append(data)

        with open(JSON_PATH, 'w', encoding='utf-8') as f:
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

    def export_to_txt(self, data):
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

        txt_path = self.reports_dir / f"{platform}_{video_id}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(report.strip())
