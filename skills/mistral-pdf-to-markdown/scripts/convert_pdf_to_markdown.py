#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mistralai>=2,<3",
#     "pypdf",
#     "python-dotenv",
#     "pyyaml",
# ]
# ///
"""
Convert PDF to Markdown using Mistral OCR API.

Usage:
    python convert_pdf_to_markdown.py <input.pdf> <output.md> [--pages "1-5"]
"""

import argparse
import base64
import io
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
# mistralai 2.0 moved the client off the top level (the old top-level import
# raises ImportError on v2+). The PEP 723 header pins the v2 major.
from mistralai.client import Mistral
from pypdf import PdfReader, PdfWriter

# Config loader: use local copy (works when installed as plugin)
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from _config_loader import get_mistral_api_key
    USE_SHARED_CONFIG = True
except ImportError:
    USE_SHARED_CONFIG = False


def load_api_key():
    """
    Load Mistral API key.

    Resolution order:
    1. Environment variable MISTRAL_API_KEY (e.g., from secrets.sh)
    2. Shared config (.claude/agent-contract.yaml or ~/.config/agent-contract/config.yaml)
    3. Notes/.env file (Dropbox-synced, convenient for teams)
    """
    # 1. Environment variable
    api_key = os.getenv("MISTRAL_API_KEY")
    if api_key:
        return api_key

    # 2. Shared config
    if USE_SHARED_CONFIG:
        try:
            api_key = get_mistral_api_key()
            if api_key:
                return api_key
        except Exception:
            pass

    # 3. Notes/.env file
    env_path = Path("Notes/.env")
    load_dotenv(env_path)
    api_key = os.getenv("MISTRAL_API_KEY") or os.getenv("mistral_api_key")
    if api_key:
        return api_key

    raise ValueError(
        "Mistral API key not found. Supply it via one of:\n"
        "  1. Environment variable: export MISTRAL_API_KEY=your-key (e.g., in secrets.sh)\n"
        "  2. Config file: .claude/agent-contract.yaml (paper-reader.mistral_api_key)\n"
        "  3. Notes/.env: MISTRAL_API_KEY=your-key (Dropbox-synced for teams)"
    )


def extract_pages(pdf_path, page_selection=None):
    """
    Extract specific pages from PDF or return entire PDF as base64.

    Args:
        pdf_path: Path to PDF file
        page_selection: String like "1,3,5" or "1-5" or None for all pages

    Returns:
        base64-encoded PDF string
    """
    if not page_selection:
        # Return entire PDF
        with open(pdf_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')

    # Extract specific pages
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    # Parse page selection
    if '-' in page_selection:
        start, end = map(int, page_selection.split('-'))
        pages = range(start-1, end)  # Convert to 0-indexed
    else:
        pages = [int(p)-1 for p in page_selection.split(',')]  # Convert to 0-indexed

    # Add selected pages
    for page_num in pages:
        if 0 <= page_num < len(reader.pages):
            writer.add_page(reader.pages[page_num])
        else:
            print(f"Warning: Page {page_num+1} out of range, skipping")

    # Write to bytes
    pdf_bytes = io.BytesIO()
    writer.write(pdf_bytes)
    pdf_bytes.seek(0)

    return base64.b64encode(pdf_bytes.read()).decode('utf-8')


def process_with_mistral(api_key, base64_pdf):
    """
    Process PDF with Mistral OCR API.

    Args:
        api_key: Mistral API key
        base64_pdf: Base64-encoded PDF

    Returns:
        OCR response object
    """
    client = Mistral(api_key=api_key)

    response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{base64_pdf}"
        },
        include_image_base64=True
    )

    return response


def save_images(ocr_response, output_path):
    """
    Extract and save images from OCR response.

    Images are namespaced per paper in a subfolder named after the output
    markdown filename stem: <output_dir>/images/<md-stem>/img-N.jpeg. This
    keeps multiple papers converted into one output directory from colliding
    on identically-numbered img-N files.

    Args:
        ocr_response: Mistral OCR response object
        output_path: Path to output markdown file

    Returns:
        Number of images saved
    """
    output_path = Path(output_path)
    images_dir = output_path.parent / "images" / output_path.stem
    images_dir.mkdir(parents=True, exist_ok=True)

    image_count = 0

    for page_idx, page in enumerate(ocr_response.pages):
        if page.images:
            for img in page.images:
                if hasattr(img, 'image_base64') and img.image_base64:
                    # Extract image data
                    img_data = img.image_base64
                    if img_data.startswith('data:image'):
                        # Remove data URI prefix
                        img_data = img_data.split(',', 1)[1]

                    # Decode and save
                    img_bytes = base64.b64decode(img_data)
                    img_filename = f"img-{image_count}.jpeg"
                    img_path = images_dir / img_filename

                    with open(img_path, 'wb') as f:
                        f.write(img_bytes)

                    print(f"  Saved image: {img_path} ({len(img_bytes) / 1024:.1f} KB)")
                    image_count += 1

    return image_count


def convert_pdf_to_markdown(pdf_path, output_path, page_selection=None):
    """
    Main conversion function.

    Args:
        pdf_path: Path to input PDF
        output_path: Path to output markdown file
        page_selection: Optional page selection string
    """
    pdf_path = Path(pdf_path)
    output_path = Path(output_path)

    print(f"Converting: {pdf_path.name}")
    if page_selection:
        print(f"Pages: {page_selection}")

    # Load API key
    print("Loading API key...")
    api_key = load_api_key()

    # Extract pages
    print("Extracting PDF pages...")
    base64_pdf = extract_pages(pdf_path, page_selection)
    print(f"  PDF size: {len(base64_pdf) / 1024:.1f} KB (base64)")

    # Process with Mistral
    print("Processing with Mistral OCR API...")
    ocr_response = process_with_mistral(api_key, base64_pdf)

    # Extract markdown
    markdown_content = '\n\n---\n\n'.join([page.markdown for page in ocr_response.pages])

    # Save images
    print("Extracting images...")
    image_count = save_images(ocr_response, output_path)

    # Fix image paths in markdown to the per-paper subfolder
    if image_count > 0:
        markdown_content = markdown_content.replace(
            '](img-', f'](images/{output_path.stem}/img-'
        )

    # Save markdown
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    # Report results
    print(f"\n✓ Conversion complete!")
    print(f"  Markdown: {output_path}")
    print(f"  Pages: {len(ocr_response.pages)}")
    print(f"  Characters: {len(markdown_content)}")
    print(f"  Images: {image_count}")


def reconvert_dir(input_dir, page_selection=None):
    """
    Reconvert every PDF in a directory into the per-paper image layout.

    For each `<name>.pdf` in `input_dir`, re-OCRs and writes `<name>.md`
    alongside it, placing figures under `images/<name>/`. Use this to repair a
    collection whose figures were flattened into a shared `images/` folder by
    an earlier version of this tool. Re-OCR is the only image source, so this
    re-calls the Mistral API (key required, same as a single conversion).
    """
    input_dir = Path(input_dir)
    pdfs = sorted(input_dir.glob("*.pdf"))
    if not pdfs:
        print(f"No PDF files found in {input_dir}")
        return

    print(f"Reconverting {len(pdfs)} PDF(s) in {input_dir}")
    for pdf_path in pdfs:
        output_path = pdf_path.with_suffix(".md")
        convert_pdf_to_markdown(pdf_path, output_path, page_selection)


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF to Markdown using Mistral OCR API"
    )
    parser.add_argument("input_pdf", nargs="?", help="Input PDF file path")
    parser.add_argument("output_md", nargs="?", help="Output Markdown file path")
    parser.add_argument("--pages", help='Page selection: "1,3,5" or "1-5"', default=None)
    parser.add_argument(
        "--reconvert-dir",
        help="Reconvert every PDF in this directory in place, writing "
             "<name>.md and figures under images/<name>/ to repair a "
             "collection whose figures were flattened by an earlier version",
        default=None,
    )

    args = parser.parse_args()

    try:
        if args.reconvert_dir:
            reconvert_dir(args.reconvert_dir, args.pages)
        else:
            if not args.input_pdf or not args.output_md:
                parser.error(
                    "input_pdf and output_md are required unless "
                    "--reconvert-dir is given"
                )
            convert_pdf_to_markdown(args.input_pdf, args.output_md, args.pages)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
