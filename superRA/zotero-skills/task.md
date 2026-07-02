---
title: "Replace Zotero MCP with Zotero Skills"
status: approved
depends_on: []
---

## Objective

Create a local-first Zotero skill in this repo that preserves the current Zotero paper-reading workflow while removing the MCP dependency. The skill should use `pyzotero` through `uv`-managed commands, prefer Zotero Desktop local API access when available, and keep the Zotero Web API as a fallback for machines without local Zotero.

### Context

Repo guidance requires skill edits to follow `skill-creator`, to keep instructions minimal and behavior-shaping, and to update inventories when adding a skill. `AGENTS.md` is an alias for `CLAUDE.md`. `README.md` describes superRA as a PLAN -> IMPLEMENT -> INTEGRATE workflow with workflow, domain, utility, and meta skills. `skills/CATEGORIES.md` is the contributor-facing skill grouping index, while `skills/using-superra/SKILL.md` is the runtime-facing skill inventory. The previous personal `zotero-paper-reader` skill used Zotero MCP for search and child-item lookup, then a helper script to find or download PDFs, then the Mistral PDF-to-Markdown skill.

### Constraints

Use `pyzotero`, not a Zotero MCP server. Pyzotero 1.13.0 is the planning baseline checked on 2026-06-04 from PyPI/GitHub/Read the Docs; implementation must pin or otherwise log the exact version used so behavior drift is visible. Local Zotero API access is read-only, so mutating operations must either stay out of scope or route through the Web API with explicit user confirmation and credential handling. The skill must tell users how to enable local API access in Zotero Desktop: Zotero -> Settings -> Advanced -> allow other applications on this computer to communicate with Zotero.

## Workflow Status

- Landed on `main` across four increments (2026-06); synced into `better-handoff` on 2026-06-09.
- Protect: drift/regression suite is `tests/test-zotero-tool.sh` (42), `tests/test-zotero-skill-text.sh` (32), and `tests/test-mistral-skill-text.sh` (11).

## Results

The MCP-free `skills/zotero-paper-reader/` skill is complete, verified, and self-contained in-repo, with `skills/mistral-pdf-to-markdown/` vendored alongside it as the canonical in-repo home for the PDF→Markdown conversion step.

`skills/zotero-paper-reader/scripts/zotero_tool.py` (PEP 723, `pyzotero==1.13.0` pinned with a sidecar lock) exposes the library-query subcommands as JSON — local-first with Web-API fallback, local-storage-first PDF retrieval, and a no-secret-leak invariant. `references/access-modes.md` defines the capability matrix, keeping full-text *search* (`items(q=..., qmode="everything")`, honored in local mode) distinct from attachment full-text *retrieval* (`fulltext_item`). `references/paper-reading.md` carries the search → locate PDF → convert via `mistral-pdf-to-markdown` → save `Notes/PaperInMarkdown/Author_Year_ShortTitle.md` → section-by-section read workflow, with no MCP anywhere.

BibTeX/citation support reuses the researcher's Better BibTeX citekeys over BBT's local JSON-RPC, with Zotero's built-in translator as a warned fallback (`bbt_fallback: true`) when BBT is unreachable: `bibtex` export with dedup-append sync into a master `.bib`, `cite` insertion (`\cite{key}` for TeX, `[@key]` for Markdown) that validates the draft and markers before mutating the `.bib`, and `bibliography` rendering of formatted references. Depth documentation lives in `skills/zotero-paper-reader/references/bibtex-citations.md`.

Both skills are registered in `README.md`, `skills/CATEGORIES.md`, and `skills/using-superra/SKILL.md` as standalone Utility skills (not loaded by the Skill-Load Manifest). Credential-free deterministic suites cover behavior, the no-secret-leak invariant, and MCP/stale-instruction regression guards; live local-mode smoke tests confirmed health/search/children/PDF retrieval, the local full-text-search boundary, BBT key matching, idempotent `.bib` sync, and the fallback path.
