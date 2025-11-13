import whisper
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from moviepy.editor import VideoFileClip
import os
import re
from config import FRAMES_DIR, FRAME_INTERVAL, WHISPER_MODEL, TESSERACT_CONFIG

class MediaExtractor:
    def __init__(self):
        self.whisper_model = None

    def load_whisper(self):
        if self.whisper_model is None:
            self.whisper_model = whisper.load_model(WHISPER_MODEL)

    def clean_ocr_text(self, text):
        """Clean and normalize OCR text"""
        if not text:
            return ""

        # Remove special characters and excessive whitespace
        text = re.sub(r'[^\w\s.,!?-]', ' ', text)

        # Normalize whitespace
        text = ' '.join(text.split())

        # Remove very short fragments (likely noise)
        if len(text) < 3:
            return ""

        # Remove if mostly non-alphabetic (noise)
        alpha_ratio = sum(c.isalpha() for c in text) / max(len(text), 1)
        if alpha_ratio < 0.5:
            return ""

        return text.strip()

    def are_similar_texts(self, text1, text2, threshold=0.8):
        """Check if two texts are similar (for deduplication)"""
        if not text1 or not text2:
            return False

        # Normalize
        t1 = text1.lower().strip()
        t2 = text2.lower().strip()

        # Exact match
        if t1 == t2:
            return True

        # One contains the other (substring match)
        if t1 in t2 or t2 in t1:
            return True

        # Simple similarity: compare word sets
        words1 = set(t1.split())
        words2 = set(t2.split())

        if not words1 or not words2:
            return False

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        similarity = intersection / union if union > 0 else 0

        return similarity >= threshold

    def preprocess_image(self, image):
        """Enhance image for better OCR"""
        # Convert to grayscale
        image = image.convert('L')

        # Increase contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)

        # Sharpen
        image = image.filter(ImageFilter.SHARPEN)

        return image

    def extract_overlay_text(self, video_path, video_id):
        clip = None
        frames_dir = FRAMES_DIR / video_id

        try:
            clip = VideoFileClip(video_path)
            duration = int(clip.duration)

            frames_dir.mkdir(parents=True, exist_ok=True)

            unique_texts = []

            # Sample frames at intervals
            for t in range(0, duration, FRAME_INTERVAL):
                try:
                    frame_path = frames_dir / f"frame_{t}.png"
                    clip.save_frame(str(frame_path), t)

                    # Load and preprocess image
                    img = Image.open(frame_path)
                    img = self.preprocess_image(img)

                    # Extract text
                    raw_text = pytesseract.image_to_string(img, config=TESSERACT_CONFIG)
                    cleaned_text = self.clean_ocr_text(raw_text)

                    if cleaned_text:
                        # Check if this text is similar to any we already have
                        is_duplicate = False
                        for existing_text in unique_texts:
                            if self.are_similar_texts(cleaned_text, existing_text):
                                is_duplicate = True
                                break

                        if not is_duplicate:
                            unique_texts.append(cleaned_text)

                except Exception:
                    continue

            # Join unique texts
            result = ". ".join(unique_texts) if unique_texts else ""
            return result

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
