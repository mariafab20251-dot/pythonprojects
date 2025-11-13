import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
VIDEOS_DIR = DATA_DIR / "videos"
FRAMES_DIR = DATA_DIR / "frames"
MODELS_DIR = BASE_DIR / "models"
DB_PATH = DATA_DIR / "processed.db"
CSV_PATH = DATA_DIR / "results.csv"
JSON_PATH = DATA_DIR / "results.json"
AUTH_PATH = BASE_DIR / "auth" / "credentials.json"

# Ensure directories exist
for dir_path in [DATA_DIR, VIDEOS_DIR, FRAMES_DIR, MODELS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Whisper settings
WHISPER_MODEL = "base"  # tiny, base, small, medium, large

# OCR settings
FRAME_INTERVAL = 2  # Extract frame every N seconds
TESSERACT_CONFIG = "--oem 3 --psm 6"

# Download settings
KEEP_VIDEOS = True  # Keep downloaded videos after processing
MAX_RETRIES = 3
