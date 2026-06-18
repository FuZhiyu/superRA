---
title: "mistral-pdf-to-markdown"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Ask the agent to "convert this scanned PDF to markdown" or "OCR pages 10-20 of this paper." You hand over a file path and an optional page range; the agent reports where the Markdown and its `images/` folder landed.

A bare agent given a scanned or multi-column PDF reads the text layer through `pypdf` or `pdfplumber`, and rarely flags the result. A scan has no text layer, so it returns empty strings. A two-column article reads straight across the page, interleaving paragraphs; tables collapse to one line and figures vanish. The mangled text passes downstream as if it were the document.

This skill sends the PDF to Mistral's OCR API instead, so it works on scans, reads multi-column layouts in order, preserves headers/lists/tables, and extracts embedded images as JPEGs into a sibling `images/` folder referenced by relative path. It also accepts PPTX, DOCX, and image inputs.

The page range is the main cost and runtime lever: the API bills per page and runs at roughly two to five seconds per page, and PDFs over about fifty pages can time out. Say what you need — "just the introduction and methods," "pages 15, 18, and 22" — and for a document that times out, ask for it in chunks and the agent concatenates the outputs.

This is the conversion step behind the [Zotero reader](#/04-utility-skills/07-zotero-paper-reader). When the PDF has a clean text layer and no scans, figures, or columns to recover, name the local `pdf` skill instead — it reads faster and without API cost.

### The key

The script calls a paid API and stops with `Error: Mistral API key not found` if it cannot locate a key. It checks, in order: the `MISTRAL_API_KEY` environment variable, a `paper-reader.mistral_api_key` entry in `.claude/agent-contract.yaml` or `~/.config/agent-contract/config.yaml`, then `MISTRAL_API_KEY=...` in `Notes/.env`. Never commit the key; the environment variable or a gitignored `Notes/.env` are the intended homes.

### Running it directly

```bash
uv run --script <skill-dir>/scripts/convert_pdf_to_markdown.py input.pdf output.md --pages "10-20"
```

`<skill-dir>` holds the skill's `SKILL.md`; substitute the real path. `--pages` takes a range (`"10-20"`) or a list (`"15,18,22"`). For the full command surface, batch patterns, and troubleshooting, see [`mistral-pdf-to-markdown`](skills/mistral-pdf-to-markdown/SKILL.md).
