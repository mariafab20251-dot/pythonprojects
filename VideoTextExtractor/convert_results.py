import json
import pandas as pd
from pathlib import Path
import re

def clean_text(text):
    """Remove duplicate lines and clean text"""
    if not text:
        return ""

    # Split into lines
    lines = text.split('\n')

    # Remove duplicates while preserving order
    seen = set()
    unique_lines = []
    for line in lines:
        line = line.strip()
        if line and line not in seen:
            seen.add(line)
            unique_lines.append(line)

    return ' '.join(unique_lines)

def json_to_excel(json_path, output_path):
    """Convert JSON results to clean Excel file"""

    # Load JSON data
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Clean and format data
    cleaned_data = []
    for item in data:
        cleaned_data.append({
            'Video ID': item['video_id'],
            'Platform': item['platform'].upper(),
            'URL': item['url'],
            'Overlay Text': clean_text(item['overlay_text']),
            'Speech Transcript': item['speech_text'],
            'Captions': item['captions'],
            'Hashtags': item['hashtags'],
            'Date Processed': item['timestamp'].split('T')[0]  # Just the date
        })

    # Create DataFrame
    df = pd.DataFrame(cleaned_data)

    # Export to Excel with formatting
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Video Extractions')

        # Get workbook and sheet
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

        # Enable text wrapping for all cells
        from openpyxl.styles import Alignment
        for row in worksheet.iter_rows():
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical='top')

    print(f"✅ Excel file created: {output_path}")

def json_to_txt_reports(json_path, output_dir):
    """Convert JSON to individual TXT reports per video"""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load JSON data
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for item in data:
        video_id = item['video_id']
        platform = item['platform'].upper()

        # Create readable TXT report
        report = f"""
{'='*80}
VIDEO EXTRACTION REPORT
{'='*80}

Video ID:       {video_id}
Platform:       {platform}
URL:            {item['url']}
Date Processed: {item['timestamp'].split('T')[0]}

{'='*80}
OVERLAY TEXT (OCR)
{'='*80}

{clean_text(item['overlay_text']) or '(No text detected)'}

{'='*80}
SPEECH TRANSCRIPT (WHISPER)
{'='*80}

{item['speech_text'] or '(No speech detected)'}

{'='*80}
CAPTIONS & METADATA
{'='*80}

Captions:  {item['captions'] or '(None)'}
Hashtags:  {item['hashtags'] or '(None)'}

{'='*80}
"""

        # Save to TXT file
        txt_path = output_dir / f"{platform}_{video_id}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(report.strip())

        print(f"✅ Created report: {txt_path.name}")

def main():
    print("=" * 80)
    print("VIDEO EXTRACTION RESULTS CONVERTER")
    print("=" * 80)
    print()

    # Paths
    json_path = Path(__file__).parent / 'data' / 'results.json'
    excel_path = Path(__file__).parent / 'data' / 'results_clean.xlsx'
    txt_dir = Path(__file__).parent / 'data' / 'reports'

    if not json_path.exists():
        print(f"❌ Error: {json_path} not found")
        return

    print(f"📁 Input: {json_path}")
    print()

    # Convert to Excel
    print("Converting to Excel...")
    try:
        json_to_excel(json_path, excel_path)
    except ImportError:
        print("⚠️  pandas/openpyxl not installed. Skipping Excel conversion.")
        print("   Install with: pip install pandas openpyxl")
    except Exception as e:
        print(f"❌ Excel conversion failed: {e}")

    print()

    # Convert to TXT reports
    print("Creating TXT reports...")
    try:
        json_to_txt_reports(json_path, txt_dir)
    except Exception as e:
        print(f"❌ TXT conversion failed: {e}")

    print()
    print("=" * 80)
    print("✅ CONVERSION COMPLETE")
    print("=" * 80)
    print(f"Excel file: {excel_path}")
    print(f"TXT reports: {txt_dir}")

if __name__ == "__main__":
    main()
