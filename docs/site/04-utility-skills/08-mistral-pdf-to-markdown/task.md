---
title: "mistral-pdf-to-markdown"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Hand a bare agent a scanned or multi-column PDF and ask for the text, and with no OCR tool in reach it falls back on the PDF's text layer through `pypdf` or `pdfplumber`. A scanned document has no text layer, so it gets back empty strings or a few stray ligatures. A two-column journal article reads straight across the page, splicing the left column into the right so paragraphs interleave; tables collapse into one run-on line; figures vanish. The agent usually does not flag any of this — it returns the mangled text as if it were the document, and every downstream summary or quote inherits the corruption.

This skill sends the PDF to Mistral's OCR API (`mistral-ocr-latest`) instead of reading the text layer, so it works on scans and reconstructs structure rather than raw character runs. It returns Markdown with headers, lists, and tables preserved, reads multi-column layouts in correct order, and extracts every embedded image as a JPEG into a sibling `images/` folder, rewriting the Markdown to reference them by relative path (`![...](images/img-0.jpeg)`) so the file renders with its figures in place. Mistral OCR also accepts PPTX, DOCX, and PNG/JPEG/AVIF inputs.

You run it as a standalone script that takes an input file and an output Markdown path. `<skill-dir>` is the directory holding the skill's `SKILL.md` — substitute the real path.

```bash
uv run --script <skill-dir>/scripts/convert_pdf_to_markdown.py \
  "Data/papers/scanned-paper.pdf" \
  "Notes/Paper Markdown/scanned-paper.md"
```

The Markdown lands at the path you name, and the `images/` folder is created next to it, so point the output at where you want both to land (e.g. `Notes/Paper Markdown/` or `Output/PDFConversions/`).

Restrict to a page range or list with `--pages` when the document is long or you only need part of it. This is the main lever on both cost and runtime: the API bills per page processed and runs at roughly two to five seconds per page, and PDFs over about fifty pages can time out.

```bash
# A contiguous range (introduction and methods)
uv run --script <skill-dir>/scripts/convert_pdf_to_markdown.py paper.pdf intro_methods.md --pages "10-20"

# A specific set of figure pages
uv run --script <skill-dir>/scripts/convert_pdf_to_markdown.py paper.pdf figures.md --pages "15,18,22,25"
```

If a large PDF times out, split it into chunks (`--pages "1-25"`, then `--pages "26-50"`) and concatenate the outputs.

The script calls a paid API, so it needs a Mistral key, and it stops with `Error: Mistral API key not found` before making any call if it cannot locate one. It checks three locations in order: the `MISTRAL_API_KEY` environment variable (simplest for personal use, e.g. exported from your secrets file), a `paper-reader.mistral_api_key` entry in `.claude/agent-contract.yaml` or `~/.config/agent-contract/config.yaml`, and finally `MISTRAL_API_KEY=...` in a `Notes/.env` file. Never commit the key to git; the environment variable or a gitignored `Notes/.env` are the intended homes.

This is the conversion step behind the [Zotero reader](#/04-utility-skills/07-zotero-paper-reader) and works standalone. When the PDF has a clean text layer and no scans, figures, or multi-column layout to recover, a local text-layer extractor (the `pdf` skill) reads it faster and without API cost. For the full command surface, API response shape, batch-processing patterns, and troubleshooting, see [`mistral-pdf-to-markdown`](skills/mistral-pdf-to-markdown/SKILL.md).
