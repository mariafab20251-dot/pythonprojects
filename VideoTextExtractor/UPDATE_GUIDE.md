# Update Guide - Switch to EasyOCR

## What Changed?
Replaced pytesseract with **EasyOCR** for much better text extraction accuracy. EasyOCR uses deep learning and is significantly more accurate with stylized social media text.

## Installation Steps

### 1. Pull Latest Changes
```bash
git pull
```

### 2. Uninstall Old Dependencies
```bash
pip uninstall pytesseract -y
```

### 3. Install New Dependencies
```bash
pip install easyocr>=1.7.0
```

Or reinstall all requirements:
```bash
pip install -r requirements.txt
```

### 4. Clear Database (To Reprocess Videos)
Delete the database to allow reprocessing with the new OCR engine:
```bash
# Windows
del data\processed.db

# Linux/Mac
rm data/processed.db
```

### 5. Test With Problem Video
Process the same video that had issues before and compare results.

## Benefits of EasyOCR
- ✅ **Much more accurate** with stylized fonts
- ✅ Better handling of shadows and overlays
- ✅ Improved text orientation detection
- ✅ Fewer garbage characters
- ✅ Better number detection
- ✅ No need for Tesseract system installation

## Notes
- First run will download EasyOCR models (~80MB)
- Processing may be slightly slower but much more accurate
- GPU support available (set `gpu=True` in extractor.py if you have CUDA)
