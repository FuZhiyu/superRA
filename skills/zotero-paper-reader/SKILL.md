---
name: zotero-paper-reader
description: Read and analyze academic papers from the user's Zotero library. Use proactively when the user asks to read, find, access, summarize, or analyze a paper by title, author, DOI, or topic from their Zotero library. Handles the complete workflow: search Zotero, locate the PDF, convert to markdown via the mistral-pdf-to-markdown skill, save under Notes/PaperInMarkdown, and analyze in sections. Also use for library queries: metadata search, full-text search, collection listing, tag listing, DOI-to-key lookup, and attachment retrieval.
user-invocable: true
---

# Zotero Paper Reader

Search, retrieve, and analyze papers from a Zotero library using pyzotero. Defaults to the Zotero Desktop local API; falls back to the Zotero Web API when local Zotero is unavailable.

## Access Model

Load [`references/access-modes.md`](references/access-modes.md) before the first `zotero_tool.py` call if you are unsure which mode applies or need fallback rules and credential details.

The bundled tool (`scripts/zotero_tool.py`) detects which mode to use automatically. Run it with `uv run --script ${CLAUDE_SKILL_DIR}/scripts/zotero_tool.py` so it resolves correctly regardless of where the skill is installed.

## Paper-Reading Workflow

### Step 1: Search the library

```bash
uv run --script ${CLAUDE_SKILL_DIR}/scripts/zotero_tool.py search "title or author or keywords"
# For full-text search (PDF content):
uv run --script ${CLAUDE_SKILL_DIR}/scripts/zotero_tool.py search "term" --fulltext
```

Present results when multiple papers match. Note the `item_key` of the chosen paper.

### Step 2: Get the PDF attachment key

```bash
uv run --script ${CLAUDE_SKILL_DIR}/scripts/zotero_tool.py children ITEM_KEY
```

Find the attachment with `contentType: application/pdf` and note its `key` (the attachment key).

### Step 3: Get the PDF file path

```bash
uv run --script ${CLAUDE_SKILL_DIR}/scripts/zotero_tool.py pdf ATTACHMENT_KEY
```

The command tries local Zotero storage first (`~/Zotero/storage/ATTACHMENT_KEY/`). If the PDF is absent locally, it downloads from the Web API to `/tmp/`. Prints the resolved path on stdout.

### Step 4: Convert to markdown

Invoke the `mistral-pdf-to-markdown` skill (a separate installed plugin). Pass the PDF path from Step 3 and save the output to `Notes/PaperInMarkdown/CLEAN_FILENAME.md`.

**Filename convention:** `Author_Year_ShortTitle.md` — replace spaces with underscores, remove special characters.
Example: `Du_et_al_2023_Are_Intermediary_Constraints_Priced.md`

The conversion skill places extracted images in an `images/` subfolder next to the markdown file.

### Step 5: Read and analyze

```python
Read(file_path="Notes/PaperInMarkdown/FILENAME.md", offset=1, limit=500)
```

Academic papers are often large. Read strategically: start with abstract and introduction, then target sections by interest. Provide the user with: paper metadata, abstract summary, main findings, and an offer to explore specific sections.

## Library Query Commands

Beyond the paper-reading workflow, you can answer broader library questions:

| Goal | Command |
|---|---|
| Metadata search | `search "query"` |
| Full-text search | `search "query" --fulltext` |
| Single item | `item ITEM_KEY` |
| Child items / attachments | `children ITEM_KEY` |
| Attachment full-text (indexed) | `fulltext ATTACHMENT_KEY` |
| PDF path or download | `pdf ATTACHMENT_KEY` |
| All collections | `collections` |
| All tags | `tags` |
| DOI-to-key index | `doiindex` |
| Health / access check | `health` |

All commands emit JSON. Add `--help` to any subcommand for parameter details.

## Configuration

Credentials are read from environment variables or, when present, from `Notes/.env`. They are never printed to the agent transcript. Required variables for Web API mode: `ZOTERO_LIBRARY_ID`, `ZOTERO_LIBRARY_TYPE` (default `user`), `ZOTERO_API_KEY`. Local mode needs no credentials. See [`references/access-modes.md`](references/access-modes.md) for full details including how to enable the local API in Zotero Desktop.

## Resources

- [`references/access-modes.md`](references/access-modes.md) — local vs. web access rules, credential setup, fallback logic, troubleshooting
- [`scripts/zotero_tool.py`](scripts/zotero_tool.py) — unified pyzotero command surface (implemented in task 02)
