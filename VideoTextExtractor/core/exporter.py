import csv
import json
from pathlib import Path
from config import CSV_PATH, JSON_PATH

class DataExporter:
    def __init__(self):
        self.ensure_csv_header()

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
