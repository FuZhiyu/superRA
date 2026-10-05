---
title: "mistral-pdf-to-markdown"
status: not-started
depends_on:  []
---

## Objective

`mistral-pdf-to-markdown` converts a PDF to structured Markdown through Mistral's OCR API, with embedded images extracted as JPEGs. Reach for it when a plain text read fails:

- **Scans** have no text layer, so local tools return empty strings.
- **Multi-column layouts** get spliced across the page; OCR keeps reading order.
- **Tables and figures** collapse or vanish; OCR keeps tables, headers, and lists, and saves the images.

A clean single-column PDF needs only the local `pdf` skill, which is faster and free. This skill is also the conversion step behind the [Zotero reader](#/04-utility-skills/07-zotero-paper-reader).

## Ask with a file and a page range

Say "convert this scanned PDF to markdown" or "OCR pages 10-20 of this paper." The agent reports the output folder: the Markdown file plus an `images/` subfolder it links to.

Name only the pages you need ("just the introduction and methods," "pages 15, 18, and 22"). The API bills per page at roughly two to five seconds each, and PDFs over about fifty pages can time out, so convert long documents in chunks.

## Set up a Mistral API key once

Get a key from the [Mistral console](https://console.mistral.ai/). Without one, the script stops with `Error: Mistral API key not found`. It looks, in order, in:

1. the `MISTRAL_API_KEY` environment variable;
2. `paper-reader.mistral_api_key` in `.claude/agent-contract.yaml` or `~/.config/agent-contract/config.yaml`;
3. `MISTRAL_API_KEY=...` in `Notes/.env`.

Never commit the key: use the environment variable or a gitignored `Notes/.env`.

## Run it directly

```bash
uv run --script <skill-dir>/scripts/convert_pdf_to_markdown.py input.pdf output.md --pages "10-20"
```

`<skill-dir>` holds the skill's `SKILL.md`; `--pages` takes a range (`"10-20"`) or a list (`"15,18,22"`). Batch use and troubleshooting: [mistral-pdf-to-markdown](skills/mistral-pdf-to-markdown/SKILL.md).
