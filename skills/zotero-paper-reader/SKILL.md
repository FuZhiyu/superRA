---
name: zotero-paper-reader
description: "Use Zotero to find, read, summarize, cite, export, or save academic papers. Use for paper lookup, library searches, attachments, BibTeX, draft citation work, and adding discovered papers to the library."
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

## Adding Papers

Save a discovered paper to the library. The default write path is the **local Zotero connector** — no key, no cloud, only Zotero desktop running with "allow other applications to communicate" enabled. It falls back to the **Web API** (write-scoped key) when the connector is unreachable or the destination is one it cannot target.

| Goal | Command |
|---|---|
| Report the desktop UI's current save target | `selected` |
| Add a paper from a citation-client record | `add --record record.json` (or pipe the JSON on stdin) |
| Add a paper and let the connector fetch a PDF URL | `add --record record.json --pdf-url URL` |
| Attach a local PDF file to an existing item | `attach --item-key KEY --file paper.pdf` (Web API only) |

The record is a citation-client `metadata` record — piped straight from screening, so there is no second lookup. A mapper covers the econ/finance item types (journalArticle, preprint, working-paper report), taking every bibliographic field **verbatim** from the record and its `--raw` Crossref payload — never agent-authored, always the published version of record.

**Save target.** The connector saves to whatever library/collection is **selected in the Zotero desktop UI** (`saveItems` takes no target). Run `selected` first and report it to the user; tell them to switch the UI selection if they want a different destination. A group library (`--library group:<id>`) or a specific `--collection KEY` the connector cannot target routes `add` to the Web API automatically.

**PDF attachments.** Prefer `add --pdf-url URL` when adding a new item and a stable PDF URL is available; the local connector fetches the PDF during `saveItems`. Use `attach --item-key KEY --file paper.pdf` only for an existing item when Web API write credentials are available. The local `/api` cannot attach files, and the connector path used here does not attach an arbitrary local file to an already-saved item.

**Dedup** runs by default (DOI vs the target library) before saving — the connector never dedups and would create duplicates. Surface a **PDF version divergence** (metadata = published, PDF = working paper) with `--pdf-divergence "..."`; it lands as a tag and an `extra` note.

Load [`references/access-modes.md`](references/access-modes.md) for the connector wire details, path-selection rules, and write-key setup.

## Configuration

Credentials are read from environment variables or, when present, from `Notes/.env`. They are never printed to the agent transcript. Required variables for Web API mode: `ZOTERO_LIBRARY_ID`, `ZOTERO_LIBRARY_TYPE` (default `user`), `ZOTERO_API_KEY`. Local mode needs no credentials. See [`references/access-modes.md`](references/access-modes.md) for full details.

## Resources

- [`references/paper-reading.md`](references/paper-reading.md) — full workflow with command examples, JSON field guide, disambiguation, and troubleshooting
- [`references/access-modes.md`](references/access-modes.md) — local vs. web access rules, the read-only local API and the connector/Web-API write paths, credential setup, fallback logic, troubleshooting
- [`references/bibtex-citations.md`](references/bibtex-citations.md) — load for the `bibtex` / `cite` / `bibliography` commands: examples, full flag list, the Better BibTeX key model and fallback semantics, group-library targeting, and troubleshooting
- [`scripts/zotero_tool.py`](scripts/zotero_tool.py) — unified pyzotero command surface (pinned to pyzotero 1.13.0 via PEP 723 inline metadata)
