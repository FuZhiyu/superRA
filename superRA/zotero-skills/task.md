---
title: "Replace Zotero MCP with Zotero Skills"
status: approved
depends_on: []
tags:
  - skill-creation
  - zotero
  - pyzotero
created: 2026-06-04
---

## Objective

Create a local-first Zotero skill in this repo that preserves the current Zotero paper-reading workflow while removing the MCP dependency. The skill should use `pyzotero` through `uv`-managed commands, prefer Zotero Desktop local API access when available, and keep the Zotero Web API as a fallback for machines without local Zotero.

### Context

Planning walk completed on 2026-06-04. Repo guidance requires skill edits to follow `skill-creator`, to keep instructions minimal and behavior-shaping, and to update inventories when adding a skill. `AGENTS.md` is an alias for `CLAUDE.md`. `README.md` describes superRA as a PLAN -> IMPLEMENT -> INTEGRATE workflow with workflow, domain, utility, and meta skills. `skills/CATEGORIES.md` is the contributor-facing skill grouping index, while `skills/using-superra/SKILL.md` is the runtime-facing skill inventory. The existing personal `zotero-paper-reader` skill uses Zotero MCP for search and child-item lookup, then a helper script to find or download PDFs, then the Mistral PDF-to-Markdown skill.

### Constraints

Use `pyzotero`, not a Zotero MCP server. Pyzotero 1.13.0 is the planning baseline checked on 2026-06-04 from PyPI/GitHub/Read the Docs; implementation must pin or otherwise log the exact version used so behavior drift is visible. Local Zotero API access is read-only, so mutating operations must either stay out of scope or route through the Web API with explicit user confirmation and credential handling. The skill must tell users how to enable local API access in Zotero Desktop: Zotero -> Settings -> Advanced -> allow other applications on this computer to communicate with Zotero.

### Planned Files

- `skills/zotero-paper-reader/SKILL.md`
- `skills/zotero-paper-reader/references/*.md`
- `skills/zotero-paper-reader/scripts/*`
- `skills/zotero-paper-reader/pyproject.toml`
- `skills/zotero-paper-reader/uv.lock`
- `skills/CATEGORIES.md`
- `README.md`
- `skills/using-superra/SKILL.md`
- tests or script-level verification artifacts under the repo's existing test structure if a durable test harness is practical

## Workflow Status

- Base branch: `main` (GitHub default; researcher decision 2026-06-04).
- **First increment** — the MCP-free `zotero-paper-reader` skill (tasks 01-05) was integrated via PR [#31](https://github.com/FuZhiyu/superRA/pull/31) to `main`.
- **Second increment** — the vendored `mistral-pdf-to-markdown` skill (task 06), multi-library support, the local-API full-text-search fix in `zotero_tool.py`, harness-neutral `<skill-dir>` paths, and expanded tests were integrated and re-approved.
- **Third increment** — PR [#32](https://github.com/FuZhiyu/superRA/pull/32) fixed the vendored converter's broken `mistralai` dependency by migrating to the v2 client import and pinning `mistralai>=2,<3`; `010a5c1e` then quoted the `zotero-paper-reader` SKILL.md frontmatter for valid YAML.
- **Fourth increment** — PR [#33](https://github.com/FuZhiyu/superRA/pull/33) added BibTeX/citation support (tasks 07-10): `bibtex` export plus master-`.bib` sync, `cite` insertion, `bibliography` rendering, Better BibTeX citekeys by default, docs, packaging, and regression coverage.
- Sync into `better-handoff` on 2026-06-09: local `main` at `b797260c` was merged from base `5dfe928b`. Resolution preserved the branch's repo-level root task and placed incoming tasks 07-10 under this `zotero-skills/` subtree.
- Protect: drift/regression suite is `tests/test-zotero-tool.sh` (42), `tests/test-zotero-skill-text.sh` (32), and `tests/test-mistral-skill-text.sh` (11) — full suite passed on the incoming branch before merge.
- Document: Results are reader-facing and reviewer-confirmed across all ten tasks; no separate maturation pass needed.

## Results

### Key Findings

The MCP-free `zotero-paper-reader` skill is complete and verified, and now self-contained in-repo. Tasks 01-06 built the reading/library-query skill; tasks 07-10 added BibTeX/citation support that reuses the researcher's Better BibTeX keys.

- **Contract** ([01-skill-contract](01-skill-contract/task.md)) — `SKILL.md` + `references/access-modes.md` define a local-first / Web-API-fallback contract with a capability matrix; full-text *search* (`items(q=..., qmode="everything")`) is kept distinct from attachment full-text *retrieval* (`fulltext_item`).
- **Tooling** ([02-pyzotero-tooling](02-pyzotero-tooling/task.md)) — `scripts/zotero_tool.py` (PEP 723, `pyzotero==1.13.0` pinned + sidecar lock) exposes 9 JSON subcommands, local-first with Web fallback, local-storage-first PDF retrieval, and no secret leakage. Local full-text search (`qmode="everything"`) was later verified live (task 05, after the local API was enabled) to work in local mode; an early bug that forced `--fulltext` to the Web API was fixed so it honors the active access mode.
- **Workflow** ([03-paper-reading-workflow](03-paper-reading-workflow/task.md)) — `references/paper-reading.md` migrates the search → locate PDF → convert via `mistral-pdf-to-markdown` → save `Notes/PaperInMarkdown/Author_Year_ShortTitle.md` → section-by-section read workflow onto the new tooling, with no MCP.
- **Inventory** ([04-inventory-and-packaging](04-inventory-and-packaging/task.md)) — registered in `README.md`, `skills/CATEGORIES.md`, and `skills/using-superra/SKILL.md` as a standalone Utility skill (not loaded by the Skill-Load Manifest); workflow choreography and generated agent files untouched.
- **Verification** ([05-verification](05-verification/task.md)) — credential-free deterministic suites cover behavior, the no-secret-leak invariant, `.env` parsing, and MCP/stale-instruction regression guards; plus a live local-mode smoke test (after the researcher enabled the Zotero local API) that confirmed health/search/children/pdf and the corrected local full-text-search boundary.
- **Vendored conversion skill** ([06-vendor-mistral-skill](06-vendor-mistral-skill/task.md)) — `mistral-pdf-to-markdown` was migrated into `skills/mistral-pdf-to-markdown/` as the canonical in-repo home for the PDF→Markdown step behind `zotero-paper-reader`, removing the external-plugin dependency that previously left conversion as a dead end. Registered as a standalone Utility skill (not loaded by the Manifest) and locked with a text-regression test.
- **BibTeX export + master-`.bib` sync** ([07-bibtex-export](07-bibtex-export/task.md)) — a `bibtex` command resolves item key to Better BibTeX citekey to entry over BBT's local JSON-RPC, with Zotero's built-in translator as a warned fallback (`bbt_fallback: true`) when BBT is unreachable. `--bib` dedup-appends into a master `.bib`, minimal-touch.
- **Citation insertion + bibliography** ([08-cite-and-bibliography](08-cite-and-bibliography/task.md)) — `cite` inserts `\cite{key}` (`--tex`) / `[@key]` (`--markdown`) and syncs the entry; `bibliography` renders formatted references. Draft and marker validation now happens before `.bib` mutation.
- **Docs + packaging** ([09-docs-and-packaging](09-docs-and-packaging/task.md)) — `SKILL.md` stays a lean routing surface, depth lives in `references/bibtex-citations.md`; CATEGORIES/README/using-superra inventories updated; skill remains a standalone Utility (not Manifest-loaded).
- **BibTeX/citation verification** ([10-bibtex-verification](10-bibtex-verification/task.md)) — credential-free suites cover the new commands, BBT-default / built-in-fallback model, master-`.bib` sync, no-secret-leak invariant, and documentation surfaces; a generic live smoke test confirmed the BBT key match, idempotent sync, draft insertion, `.bib`-protection ordering, and fallback.

## Revision Notes

- 2026-07-01 — Researcher-approved consolidation (Mature & Consolidate): collapse to this single `task.md`; delete the ten child directories. Distil `## Results` to a short narrative of the shipped skills (`skills/zotero-paper-reader/`, `skills/mistral-pdf-to-markdown/`). Self-contained: plain inline-code repo paths only — no markdown links outside `superRA/`, no links to deleted children. Normalize frontmatter to `title`/`status`/`depends_on`.
