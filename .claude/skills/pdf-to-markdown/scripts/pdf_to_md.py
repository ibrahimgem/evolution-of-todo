#!/usr/bin/env python3
"""
PDF to Markdown Converter

Converts PDF files to Markdown format, preserving structure and formatting.
Supports text extraction, heading detection, and list formatting.
"""

import sys
import re
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber not installed. Run: pip install pdfplumber", file=sys.stderr)
    sys.exit(1)


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file."""
    text_content = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if text:
                text_content.append(f"<!-- Page {page_num} -->\n{text}\n")

    return "\n".join(text_content)


def convert_to_markdown(text: str) -> str:
    """Convert extracted text to Markdown format."""
    lines = text.split('\n')
    markdown_lines = []

    for line in lines:
        line = line.strip()

        if not line:
            markdown_lines.append('')
            continue

        # Detect headings (all caps, short lines)
        if line.isupper() and len(line) < 60 and not line.startswith('<!--'):
            markdown_lines.append(f"## {line.title()}")

        # Detect numbered lists
        elif re.match(r'^\d+[\.\)]\s+', line):
            markdown_lines.append(line)

        # Detect bullet points
        elif line.startswith(('•', '-', '*')):
            markdown_lines.append(f"- {line[1:].strip()}")

        # Regular paragraphs
        else:
            markdown_lines.append(line)

    return '\n'.join(markdown_lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_md.py <input.pdf> [output.md]")
        sys.exit(1)

    input_pdf = Path(sys.argv[1])

    if not input_pdf.exists():
        print(f"Error: File not found: {input_pdf}", file=sys.stderr)
        sys.exit(1)

    # Determine output file
    if len(sys.argv) >= 3:
        output_md = Path(sys.argv[2])
    else:
        output_md = input_pdf.with_suffix('.md')

    print(f"Converting {input_pdf} to Markdown...")

    # Extract and convert
    text = extract_text_from_pdf(str(input_pdf))
    markdown = convert_to_markdown(text)

    # Write output
    output_md.write_text(markdown, encoding='utf-8')
    print(f"✓ Conversion complete: {output_md}")


if __name__ == "__main__":
    main()
