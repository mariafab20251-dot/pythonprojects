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

        # Remove all special characters except basic punctuation
        text = re.sub(r'[^a-zA-Z0-9\s.,!?\'-]', ' ', text)

        # Remove excessive underscores and dashes
        text = re.sub(r'_{2,}', '', text)
        text = re.sub(r'-{2,}', '', text)

        # Remove single character fragments surrounded by spaces
        text = re.sub(r'\s[a-zA-Z]\s', ' ', text)

        # Normalize whitespace
        text = ' '.join(text.split())

        # Remove very short fragments (likely noise)
        if len(text) < 10:
            return ""

        # Remove if mostly non-alphabetic (noise)
        alpha_count = sum(c.isalpha() for c in text)
        if alpha_count < 15:  # At least 15 letters
            return ""

        return text.strip()

    def filter_sentences(self, text):
        """Filter out garbage sentences from text"""
        if not text:
            return ""

        # Split into sentences (rough)
        sentences = re.split(r'[.!?]+', text)

        clean_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            words = sentence.split()

            # Filter criteria for a valid sentence
            if len(words) < 3:  # Too short
                continue

            # Count very short words (1-2 letters)
            short_words = sum(1 for w in words if len(w) <= 2)
            short_word_ratio = short_words / len(words)

            # Reject if more than 40% are very short words (likely garbage)
            if short_word_ratio > 0.4:
                continue

            # Count words with 4+ letters (likely real words)
            real_words = sum(1 for w in words if len(w) >= 4)

            # Need at least 3 real words for a valid sentence
            if real_words < 3:
                continue

            clean_sentences.append(sentence)

        return '. '.join(clean_sentences) if clean_sentences else ""

    def normalize_for_comparison(self, text):
        """Strip text down to just words for similarity comparison"""
        # Remove all non-alphabetic characters
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        # Lowercase and normalize spaces
        text = ' '.join(text.lower().split())
        return text

    def are_similar_texts(self, text1, text2, threshold=0.75):
        """Check if two texts are similar (for deduplication)"""
        if not text1 or not text2:
            return False

        # Normalize both texts to just words
        norm1 = self.normalize_for_comparison(text1)
        norm2 = self.normalize_for_comparison(text2)

        if not norm1 or not norm2:
            return False

        # Exact match after normalization
        if norm1 == norm2:
            return True

        # One contains the other (substring match)
        if norm1 in norm2 or norm2 in norm1:
            return True

        # Word-based similarity
        words1 = set(norm1.split())
        words2 = set(norm2.split())

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

                    # Filter sentences to remove garbage
                    filtered_text = self.filter_sentences(cleaned_text)

                    if filtered_text:
                        # Check if this text is similar to any we already have
                        is_duplicate = False
                        for existing_text in unique_texts:
                            if self.are_similar_texts(filtered_text, existing_text):
                                is_duplicate = True
                                break

                        if not is_duplicate:
                            unique_texts.append(filtered_text)

                except Exception:
                    continue

            # Join unique texts - pick the longest/cleanest version if we have similar ones
            if unique_texts:
                # Sort by length descending - longest is usually cleanest
                unique_texts.sort(key=len, reverse=True)
                # Return the longest (cleanest) version
                result = unique_texts[0]
            else:
                result = ""

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
