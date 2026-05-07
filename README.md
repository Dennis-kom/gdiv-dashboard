# gdiv-dashboard

## OCR helper

This project includes a PNG-to-table OCR utility in `utils/data_recognition.py`.

### Function

- `pic_to_table(image_path, ...) -> pandas.DataFrame`
- Input must be a `.png` file path.
- By default, the first detected row is used as column headers.
- **Safe fallback**: If OCR is unavailable, shows user-friendly error in Streamlit UI or console (doesn't crash).

### Requirements

1. Install Python dependencies from `requirements.txt`.
2. Install Tesseract OCR binary on your machine and ensure it is in `PATH`.
   - Windows: https://github.com/UB-Mannheim/tesseract/wiki

### Features

- ✅ Automatic image preprocessing (grayscale, denoise, contrast enhancement)
- ✅ Smart table reconstruction from OCR token positions
- ✅ Support for Hebrew & English text (configurable via `lang` parameter)
- ✅ **Safe fallback when Tesseract is missing** (returns empty DataFrame + friendly error message)
- ✅ OCR confidence filtering (skips low-confidence tokens)
- ✅ Automatic header deduplication

### Quick run

```powershell
# Test core table reconstruction logic
python -m utils.data_recognition_smoke

# Test fallback behavior (when OCR unavailable)
python -m utils.data_recognition_fallback_test
```

### Usage Example

```python
from utils.data_recognition import pic_to_table

# Basic usage
df = pic_to_table("table.png")
print(df)

# With custom language (Hebrew only)
df = pic_to_table("table.png", lang="heb")

# With custom Tesseract installation path (Windows)
df = pic_to_table("table.png", tesseract_cmd=r"C:\Program Files\Tesseract-OCR\tesseract.exe")
```
# gdiv-dashboard

## OCR helper

This project now includes a PNG-to-table OCR utility in `utils/data_recognition.py`.

### Function

- `pic_to_table(image_path, ...) -> pandas.DataFrame`
- Input must be a `.png` file path.
- By default, the first detected row is used as column headers.

### Requirements

1. Install Python dependencies from `requirements.txt`.
2. Install **Tesseract OCR** binary on your machine and ensure it is in `PATH`.
   - On Windows, install from the official Tesseract installer and restart terminal.

### Quick run

```powershell
python -m utils.data_recognition_smoke
```

If you want to run real OCR, call `pic_to_table` from your app and pass a PNG path.


