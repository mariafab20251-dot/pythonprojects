import sqlite3
import hashlib
from datetime import datetime
from config import DB_PATH

class VideoDatabase:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url_hash TEXT UNIQUE NOT NULL,
                video_id TEXT,
                platform TEXT,
                url TEXT,
                overlay_text TEXT,
                speech_text TEXT,
                captions TEXT,
                hashtags TEXT,
                timestamp TEXT
            )
        ''')
        self.conn.commit()

    def get_url_hash(self, url):
        return hashlib.md5(url.encode()).hexdigest()

    def is_processed(self, url):
        url_hash = self.get_url_hash(url)
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM processed_videos WHERE url_hash = ?', (url_hash,))
        return cursor.fetchone() is not None

    def add_video(self, video_id, platform, url, overlay_text, speech_text, captions, hashtags):
        url_hash = self.get_url_hash(url)
        timestamp = datetime.now().isoformat()
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO processed_videos
            (url_hash, video_id, platform, url, overlay_text, speech_text, captions, hashtags, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (url_hash, video_id, platform, url, overlay_text, speech_text, captions, hashtags, timestamp))
        self.conn.commit()

    def close(self):
        self.conn.close()
