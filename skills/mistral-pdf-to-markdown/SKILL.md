---
name: mistral-pdf-to-markdown
description: Convert PDFs to Markdown using Mistral OCR API with image extraction. Use when you need to extract structured text and images from PDFs, especially for scanned documents or documents with complex formatting. Outputs Markdown with embedded images.
user-invocable: true
---

# Mistral PDF to Markdown Converter

Convert PDF documents to Markdown format using Mistral's OCR API. Automatically extracts text, formatting, and images.

## When to Use

- Converting research papers or documents to Markdown
- Extracting text from scanned PDFs (OCR capability)
- Preserving document structure with headers and formatting
- Extracting embedded images from PDFs

## Quick Start

Run the conversion script from this skill's directory. In the commands below, `<skill-dir>` is the directory containing this `SKILL.md` — substitute the real path so the invocation works regardless of which harness loaded the skill or where it is installed.

```bash
# Convert entire PDF
uv run --script <skill-dir>/scripts/convert_pdf_to_markdown.py input.pdf output.md

# Convert specific pages
uv run --script <skill-dir>/scripts/convert_pdf_to_markdown.py input.pdf output.md --pages "1-5"
uv run --script <skill-dir>/scripts/convert_pdf_to_markdown.py input.pdf output.md --pages "1,3,5"
```

## Output Structure

```
Output/PDFConversions/
├── document.md          # Markdown with text and image references
└── images/
    ├── img-0.jpeg      # Extracted images
    ├── img-1.jpeg
    └── ...
```

## Usage in Code

```python
from pathlib import Path
import subprocess

# Run conversion script
result = subprocess.run([
    "uv", "run", "--script",
    "<skill-dir>/scripts/convert_pdf_to_markdown.py",
    "input.pdf",
    "Output/PDFConversions/output.md",
    "--pages", "1-10"
], capture_output=True, text=True)

print(result.stdout)
```

## Key Features

- **Markdown formatting**: Preserves headers, lists, and structure
- **Image extraction**: Saves images to `images/` subfolder automatically
- **Page selection**: Extract specific pages or ranges
- **Scanned PDF support**: True OCR capability for image-based PDFs
- **Relative paths**: Image references use `![...](images/img-X.jpeg)`

## Requirements

The script requires:
- Mistral API key (see API Key Setup below)
- Python packages: `mistralai`, `python-dotenv`, `pypdf`, `pyyaml` (declared inline in the script's PEP 723 header)

## API Key Setup

The script checks these locations in order (first match wins):

1. **Environment variable** `MISTRAL_API_KEY` — recommended for personal use (e.g., add `export MISTRAL_API_KEY=your-key` to `secrets.sh`)
2. **Shared config** — `.claude/agent-contract.yaml` or `~/.config/agent-contract/config.yaml` under `paper-reader.mistral_api_key`
3. **`Notes/.env`** — add `MISTRAL_API_KEY=your-key`. This file is gitignored but Dropbox-synced, making it convenient for teams sharing a project folder

> **Never commit API keys to git.** Use environment variables or Dropbox-synced `Notes/.env` instead.

## Common Use Cases

### Convert Research Paper
```bash
uv run --script <skill-dir>/scripts/convert_pdf_to_markdown.py \
  "Data/papers/research.pdf" \
  "Notes/Paper Markdown/research.md"
```

### Extract Specific Sections
```bash
# Extract pages 10-20 (introduction and methods)
uv run --script <skill-dir>/scripts/convert_pdf_to_markdown.py \
  "paper.pdf" \
  "Notes/Paper Markdown/intro_methods.md" \
  --pages "10-20"
```

### Extract Figures Only
```bash
# Extract pages with figures
uv run --script <skill-dir>/scripts/convert_pdf_to_markdown.py \
  "paper.pdf" \
  "Notes/Paper Markdown/figures.md" \
  --pages "25,27,30,35"
```

## Error Handling

**API Key Not Found:**
```
Error: Mistral API key not found
```
→ See **API Key Setup** above for three ways to configure it

**Page Out of Range:**
```
Warning: Page 100 out of range, skipping
```
→ Check PDF page count and adjust page selection

**API Rate Limit:**
→ Wait a moment and retry, or reduce page count per request

## Notes

- Images are saved as JPEG files in `images/` subfolder
- Markdown image references are automatically updated to `images/img-X.jpeg`
- Large PDFs may take longer to process due to API limits
- For simple text extraction without OCR, consider using the `pdf` skill instead
- Scanned PDFs benefit most from this skill's OCR capability

## See Also

- `pdf` skill - For local PDF manipulation without API calls
- `references/reference.md` - Additional details about the Mistral OCR API
