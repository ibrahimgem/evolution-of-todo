---
name: pdf-to-markdown
description: Convert PDF files to Markdown format with text extraction, structure preservation, and formatting conversion. Use when converting PDF documents to Markdown, extracting text from PDFs, or transforming PDF content for documentation or note-taking purposes.
---

# PDF to Markdown Converter

Convert PDF documents to clean, readable Markdown format.

## Quick Start

Use the provided script for basic conversion:

```bash
python scripts/pdf_to_md.py input.pdf [output.md]
```

## Conversion Workflow

1. **Extract Text**: Use pdfplumber for layout-aware text extraction
2. **Detect Structure**: Identify headings, lists, and paragraphs
3. **Format Markdown**: Convert to proper Markdown syntax
4. **Preserve Metadata**: Keep page numbers as HTML comments

## Library Selection

- **pdfplumber** (recommended): Best for text-based PDFs with layout awareness
- **PyPDF2**: Lightweight option for simple extraction
- **OCR (pytesseract)**: Required for scanned/image-based PDFs

See [libraries.md](references/libraries.md) for detailed library usage.

## Common Patterns

### Basic Text Extraction

```python
import pdfplumber

with pdfplumber.open('document.pdf') as pdf:
    text = '\n'.join(page.extract_text() for page in pdf.pages)
```

### Preserve Page Numbers

```python
markdown = []
for i, page in enumerate(pdf.pages, 1):
    markdown.append(f"<!-- Page {i} -->\n{page.extract_text()}")
```

### Detect Headings

Use heuristics:
- All caps lines (likely headings)
- Short lines (<60 chars)
- Font size (if available)

## Limitations

- Complex layouts may require manual cleanup
- Tables need special handling
- Images are not extracted by default
- Footnotes may lose positioning
