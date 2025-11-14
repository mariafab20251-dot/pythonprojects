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

    def generate_excel_report(self, json_path=None, channel_folder=None):
        """Generate clean Excel report from JSON data"""
        import pandas as pd
        from openpyxl.styles import Alignment

        # Determine paths
        if channel_folder:
            source_json = channel_folder / "results.json"
            output_excel = channel_folder / "results_clean.xlsx"
        else:
            source_json = json_path or JSON_PATH
            output_excel = DATA_DIR / "results_clean.xlsx"

        if not source_json.exists():
            return None

        try:
            # Load JSON data
            with open(source_json, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not data:
                return None

            # Clean and format data
            cleaned_data = []
            for item in data:
                cleaned_data.append({
                    'Video ID': item['video_id'],
                    'Platform': item['platform'].upper(),
                    'URL': item['url'],
                    'Overlay Text': self.clean_text(item['overlay_text']),
                    'Speech Transcript': item['speech_text'] or '(No speech detected)',
                    'Captions': item['captions'] or '(None)',
                    'Hashtags': item['hashtags'] or '(None)',
                    'Date Processed': item['timestamp'].split('T')[0]
                })

            # Create DataFrame
            df = pd.DataFrame(cleaned_data)

            # Export to Excel with formatting
            with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Video Extractions')

                # Get worksheet
                worksheet = writer.sheets['Video Extractions']

                # Set column widths
                worksheet.column_dimensions['A'].width = 15  # Video ID
                worksheet.column_dimensions['B'].width = 12  # Platform
                worksheet.column_dimensions['C'].width = 50  # URL
                worksheet.column_dimensions['D'].width = 60  # Overlay Text
                worksheet.column_dimensions['E'].width = 60  # Speech
                worksheet.column_dimensions['F'].width = 40  # Captions
                worksheet.column_dimensions['G'].width = 30  # Hashtags
                worksheet.column_dimensions['H'].width = 15  # Date

                # Enable text wrapping
                for row in worksheet.iter_rows():
                    for cell in row:
                        cell.alignment = Alignment(wrap_text=True, vertical='top')

            return str(output_excel)

        except ImportError:
            # pandas/openpyxl not installed
            return None
        except Exception as e:
            print(f"Excel generation error: {e}")
            return None
