import whisper
import pytesseract
from PIL import Image
from moviepy.editor import VideoFileClip
import os
from config import FRAMES_DIR, FRAME_INTERVAL, WHISPER_MODEL, TESSERACT_CONFIG

class MediaExtractor:
    def __init__(self):
        self.whisper_model = None

    def load_whisper(self):
        if self.whisper_model is None:
            self.whisper_model = whisper.load_model(WHISPER_MODEL)

    def extract_overlay_text(self, video_path, video_id):
        clip = None
        frames_dir = FRAMES_DIR / video_id

        try:
            clip = VideoFileClip(video_path)
            duration = int(clip.duration)

            frames_dir.mkdir(parents=True, exist_ok=True)

            all_text = []

            for t in range(0, duration, FRAME_INTERVAL):
                try:
                    frame_path = frames_dir / f"frame_{t}.png"
                    clip.save_frame(str(frame_path), t)

                    img = Image.open(frame_path)
                    text = pytesseract.image_to_string(img, config=TESSERACT_CONFIG)
                    if text.strip():
                        all_text.append(text.strip())
                except Exception:
                    continue

            return " | ".join(set(all_text))

        finally:
            if clip:
                clip.close()

            # Cleanup frames
            if frames_dir.exists():
                for f in frames_dir.glob("*.png"):
                    try:
                        f.unlink()
                    except:
                        pass
                try:
                    frames_dir.rmdir()
                except:
                    pass

    def extract_speech(self, video_path):
        self.load_whisper()

        result = self.whisper_model.transcribe(video_path)
        return result["text"].strip()
