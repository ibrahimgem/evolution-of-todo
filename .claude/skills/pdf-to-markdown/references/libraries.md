# PDF Processing Libraries

## pdfplumber (Recommended)

Best for text extraction with layout awareness.

```python
import pdfplumber

with pdfplumber.open('document.pdf') as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        # Extract tables
        tables = page.extract_tables()
```

**Installation**: `pip install pdfplumber`

## PyPDF2

Lightweight option for simple text extraction.

```python
from PyPDF2 import PdfReader

reader = PdfReader('document.pdf')
for page in reader.pages:
    text = page.extract_text()
```

**Installation**: `pip install PyPDF2`

## pdf2image + pytesseract

For scanned PDFs (OCR required).

```python
from pdf2image import convert_from_path
import pytesseract

images = convert_from_path('scanned.pdf')
text = '\n'.join(pytesseract.image_to_string(img) for img in images)
```

**Installation**: `pip install pdf2image pytesseract`
