# Mistral PDF to Markdown - Reference Guide

Advanced usage, API details, and troubleshooting for the Mistral OCR PDF converter.

In the path and command examples below, `<skill-dir>` is the directory containing this skill's `SKILL.md` — substitute the real path.

## API Details

The conversion uses the `mistral-ocr-latest` model.

**Endpoint:** `https://api.mistral.ai/v1/ocr`

**Authentication:** Bearer token via `MISTRAL_API_KEY`

**Supported formats:** PDF, PPTX, DOCX; PNG, JPEG, AVIF images

### Response Structure

```python
OCRResponse
├── pages: List[OCRPageObject]
│   ├── index: int
│   ├── markdown: str
│   ├── images: List[ImageObject]
│   │   ├── id: str (e.g., "img-0.jpeg")
│   │   ├── top_left_x, top_left_y: float
│   │   ├── bottom_right_x, bottom_right_y: float
│   │   └── image_base64: str (when include_image_base64=True)
│   └── dimensions: OCRPageDimensions
│       ├── dpi: int
│       ├── height: int
│       └── width: int
├── model: str ("mistral-ocr-2505-completion")
├── usage_info: OCRUsageInfo
│   ├── pages_processed: int
│   └── doc_size_bytes: int
└── document_annotation: Optional[Any]
```

### Image Data Format

Images come back base64-encoded:

```
data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD...
```

The script strips the data URI prefix (`data:image/jpeg;base64,`), decodes the base64 string, and saves JPEG files.

## Advanced Usage

### Programmatic Usage

```python
import sys
sys.path.append('<skill-dir>/scripts')
from convert_pdf_to_markdown import (
    load_api_key,
    extract_pages,
    process_with_mistral,
    save_images
)

# Load API key
api_key = load_api_key()

# Extract pages
base64_pdf = extract_pages("input.pdf", page_selection="1-5")

# Process with Mistral
ocr_response = process_with_mistral(api_key, base64_pdf)

# Custom image handling
for page_idx, page in enumerate(ocr_response.pages):
    print(f"Page {page_idx}: {len(page.images)} images")
    for img in page.images:
        print(f"  Image position: ({img.top_left_x}, {img.top_left_y})")
```

### Batch Processing

```python
from pathlib import Path
import subprocess

# Process multiple PDFs
pdf_dir = Path("Data/papers")
output_dir = Path("Output/PDFConversions")

for pdf_file in pdf_dir.glob("*.pdf"):
    output_file = output_dir / f"{pdf_file.stem}.md"

    subprocess.run([
        "uv", "run", "--script",
        "<skill-dir>/scripts/convert_pdf_to_markdown.py",
        str(pdf_file),
        str(output_file)
    ])
```

### Custom Output Location

The script always creates the `images/` folder in the output markdown file's own directory:

```python
# Output structure is automatically created
output_path = Path("custom/location/document.md")
# → Images saved to: custom/location/images/img-*.jpeg
```

## Performance Considerations

### API Limits

- **Rate limits:** Check Mistral API documentation for current limits
- **File size:** Large PDFs (>50 pages) may timeout; use page selection
- **Processing time:** ~2-5 seconds per page depending on complexity

### Optimization Tips

- **Extract specific pages** when you need only certain sections:
  ```bash
  --pages "10-20"  # Only process 10 pages instead of entire document
  ```
- **Batch similar requests** to minimize API overhead.
- **Cache results** — save the converted markdown rather than re-processing.

## Troubleshooting

### Empty or missing images

**Symptom:** Markdown shows image references but no files were saved.

**Cause:** The images may carry no `image_base64` attribute.

**Solution:** Verify `include_image_base64=True` in the API call.

```python
# Check API response
for page in ocr_response.pages:
    for img in page.images:
        if not hasattr(img, 'image_base64'):
            print(f"Warning: Image {img.id} missing base64 data")
```

### Incorrect image paths

**Symptom:** Markdown shows `![...](img-0.jpeg)` but the images sit in `images/`.

**Cause:** The path replacement was not applied.

**Solution:** The script fixes this automatically with:
```python
markdown_content = markdown_content.replace('](img-', '](images/img-')
```

### API authentication errors

**Symptom:** `401 Unauthorized`.

**Causes:** an invalid or expired API key, or a key that never loaded from `.env`.

**Solutions:**
```bash
# Verify API key exists
cat Notes/.env | grep mistral_api_key

# Test API key manually
export MISTRAL_API_KEY="your-key-here"
python -c "from mistralai.client import Mistral; print(Mistral(api_key='$MISTRAL_API_KEY'))"
```

### Large file processing

**Symptom:** Timeout or memory errors on large PDFs.

**Solutions:**
- Extract pages in chunks: `--pages "1-10"`, then `--pages "11-20"`, etc.
- Reduce the PDF size first (compress images).
- Process locally with the `pdf` skill for non-OCR needs.

### Debugging

Verbose output:

```python
# Add to script
import logging
logging.basicConfig(level=logging.DEBUG)
```

Response details:

```python
print(f"Pages processed: {ocr_response.usage_info.pages_processed}")
print(f"Document size: {ocr_response.usage_info.doc_size_bytes} bytes")
print(f"Model: {ocr_response.model}")
```

## Comparison with Other Methods

| Feature | Mistral OCR | pypdf | pdfplumber |
|---------|-------------|-------|------------|
| Text extraction | ✓ Excellent | ✓ Good | ✓ Good |
| Scanned PDFs | ✓ Yes (OCR) | ✗ No | ✗ No |
| Image extraction | ✓ Automatic | ✗ No | ✗ No |
| Markdown output | ✓ Native | ✗ Manual | ✗ Manual |
| Cost | \$ API calls | Free | Free |
| Speed | Moderate | Fast | Moderate |
| Formatting | ✓ Excellent | ~ Basic | ✓ Good |

**Use Mistral OCR when:** the PDF is scanned and needs OCR, you want formatted Markdown or automatic image extraction, and API cost is acceptable.

**Use local tools (`pdf` skill) when:** plain text extraction suffices, no OCR is required, or you are processing many documents and want the speed and cost savings.

## Example Workflow: Figures Only

Identify the figure pages (manually or via the table of contents), then extract just those:

```bash
uv run --script <skill-dir>/scripts/convert_pdf_to_markdown.py \
  "paper.pdf" \
  "Output/PDFConversions/paper_figures.md" \
  --pages "15,18,22,25"
```

The images land in the conversion's `images/` folder, and the markdown carries the captions and references.

## API Cost Estimation

Check Mistral's pricing page for current rates. Charged per page processed; image extraction may cost extra, and larger pages (higher DPI) may cost more.
