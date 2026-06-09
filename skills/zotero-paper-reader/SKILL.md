---
name: zotero-paper-reader
description: 'Read and analyze academic papers from the user''s Zotero library, and generate citations from it. Use proactively when the user asks to read, find, access, summarize, or analyze a paper by title, author, DOI, or topic from their Zotero library. Handles the complete workflow: search Zotero, locate the PDF, convert to markdown via the mistral-pdf-to-markdown skill, save under Notes/PaperInMarkdown, and analyze in sections. Also use for library queries: listing libraries (user and group), metadata search, full-text search, collection listing, tag listing, DOI-to-key lookup, and attachment retrieval — in the user''s own library or any group library. Also use for BibTeX export, inserting a `\cite`/`[@key]` citation into a draft, syncing entries into a master `.bib` file, and rendering a formatted bibliography — reusing the user''s Better BibTeX citekeys by default.'
user-invocable: true
---

# Zotero Paper Reader

Search, retrieve, and analyze papers from a Zotero library using pyzotero. Defaults to the Zotero Desktop local API; falls back to the Zotero Web API when local Zotero is unavailable.

## Access Model

The bundled tool (`scripts/zotero_tool.py`) detects which mode to use automatically. Run it with `uv run --script <skill-dir>/scripts/zotero_tool.py`, where `<skill-dir>` is the directory containing this `SKILL.md` — substitute the real path. This resolves correctly regardless of which harness loaded the skill or where it is installed.

Load [`references/access-modes.md`](references/access-modes.md) if you need fallback rules, credential setup details, or troubleshooting for access-mode issues.

## Paper-Reading Workflow

Load [`references/paper-reading.md`](references/paper-reading.md) for the full step-by-step workflow with exact command invocations, JSON field names, disambiguation logic, parent-item hydration for full-text search hits, and troubleshooting.

**Summary of steps:**

1. Search: `zotero_tool.py search "query"` — plain metadata search; `--fulltext` for indexed content (local or web).
2. Identify top-level item: inspect `data.itemType` on each hit; attachment hits from `--fulltext` need parent hydration via `data.parentItem`.
3. Choose: present concise metadata when multiple top-level papers match; ask the user only if the intended paper cannot be inferred.
4. Get PDF attachment key: `zotero_tool.py children ITEM_KEY` → find child with `data.contentType == "application/pdf"`.
5. Get PDF path: `zotero_tool.py pdf ATTACHMENT_KEY` → emits `{"source": ..., "path": ...}`.
6. Convert to markdown: invoke the `mistral-pdf-to-markdown` skill with the PDF path; save to `Notes/PaperInMarkdown/Author_Year_ShortTitle.md`.
7. Read and analyze: read the converted file in sections — abstract and introduction first, then targeted sections.

## Library Query Commands

| Goal | Command |
|---|---|
| List libraries (user + groups) | `libraries` |
| Metadata search (title/creator/year) | `search "query"` |
| Full-text search (indexed content; local or web) | `search "query" --fulltext` |
| Single item | `item ITEM_KEY` |
| Child items / attachments | `children ITEM_KEY` |
| Attachment full-text retrieval (one attachment) | `fulltext ATTACHMENT_KEY` |
| PDF path or download | `pdf ATTACHMENT_KEY` |
| All collections | `collections` |
| All tags | `tags` |
| DOI-to-key index | `doiindex` |
| BibTeX export + master-`.bib` sync | `bibtex --item-key KEY` (or `--query "text"` / `--doi DOI`) |
| Insert a citation into a draft + sync `.bib` | `cite --item-key KEY --tex FILE --bib PATH` (or `--markdown FILE`) |
| Render formatted references | `bibliography --item-key KEY` (default APA) |
| Health / access check | `health` |

All commands emit JSON. Add `--help` to any subcommand for parameter details.

**Targeting a library.** By default commands act on the user's own library ("My Library"). To act on a group library instead, run `libraries` first to get the group ids, then pass `--library <group-id>` (or `--library group:<id>`) — e.g. `search "your query" --library <group-id>`. Works on `search`, `item`, `children`, `collections`, `tags`, `fulltext`, `doiindex`, `pdf`, `bibtex`, `cite`, and `bibliography`.

## Citations & BibTeX

`bibtex`, `cite`, and `bibliography` generate citations from selected library items, reusing the researcher's **Better BibTeX (BBT)** citekeys by default (so entries stay consistent with a BBT-maintained master `.bib`) and falling back to Zotero's built-in translator — with a key-mismatch warning — when BBT is unreachable. They share the `--item-key` / `--query` / `--doi` selection flags, `--library` targeting, and the dedup-append `.bib` sync.

Load [`references/bibtex-citations.md`](references/bibtex-citations.md) for command examples, the full flag list (`--bib` / `--tex` / `--markdown` / `--marker` / `--style`), the BBT-vs-built-in key model and fallback semantics, JSON fields, and troubleshooting.

## Configuration

Credentials are read from environment variables or, when present, from `Notes/.env`. They are never printed to the agent transcript. Required variables for Web API mode: `ZOTERO_LIBRARY_ID`, `ZOTERO_LIBRARY_TYPE` (default `user`), `ZOTERO_API_KEY`. Local mode needs no credentials. See [`references/access-modes.md`](references/access-modes.md) for full details.

## Resources

- [`references/paper-reading.md`](references/paper-reading.md) — full workflow with command examples, JSON field guide, disambiguation, and troubleshooting
- [`references/access-modes.md`](references/access-modes.md) — local vs. web access rules, credential setup, fallback logic, troubleshooting
- [`references/bibtex-citations.md`](references/bibtex-citations.md) — load for the `bibtex` / `cite` / `bibliography` commands: examples, full flag list, the Better BibTeX key model and fallback semantics, group-library targeting, and troubleshooting
- [`scripts/zotero_tool.py`](scripts/zotero_tool.py) — unified pyzotero command surface (pinned to pyzotero 1.13.0 via PEP 723 inline metadata)
