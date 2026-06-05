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

Planning walk completed on 2026-06-04. Repo guidance requires skill edits to follow `skill-creator`, to keep instructions minimal and behavior-shaping, and to update inventories when adding a skill. `AGENTS.md` is an alias for `CLAUDE.md`. `README.md` describes superRA as a PLAN -> IMPLEMENT -> INTEGRATE workflow with workflow, domain, utility, and meta skills. `skills/CATEGORIES.md` is the contributor-facing skill grouping index, while `skills/using-superRA/SKILL.md` is the runtime-facing skill inventory. The existing personal `zotero-paper-reader` skill uses Zotero MCP for search and child-item lookup, then a helper script to find or download PDFs, then the Mistral PDF-to-Markdown skill.

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
- `skills/using-superRA/SKILL.md`
- tests or script-level verification artifacts under the repo's existing test structure if a durable test harness is practical

## Workflow Status

- Base branch: `main` (GitHub default; researcher decision 2026-06-04). Branch forked from `main` HEAD `3e0de358`; `main` has not advanced, so Sync is a no-op (clean fast-forward).
- Protect: drift/regression tests are `tests/test-zotero-tool.sh` (21 checks) and `tests/test-zotero-skill-text.sh` (15 checks); full suite passes.
- Integrate: work is purely additive (new skill + 3 one-line inventory rows + tests) onto an unchanged base; each task passed substantive per-task review.
- Finish: integrated via PR [#31](https://github.com/FuZhiyu/superRA/pull/31) to `main` (2026-06-04). Freshness re-checked before push: `origin/main` unchanged at `3e0de358`.

## Results

### Key Findings

The MCP-free `zotero-paper-reader` skill is complete and verified across five approved tasks:

- **Contract** ([01-skill-contract](01-skill-contract/task.md)) — `SKILL.md` + `references/access-modes.md` define a local-first / Web-API-fallback contract with a capability matrix; full-text *search* (`items(q=..., qmode="everything")`) is kept distinct from attachment full-text *retrieval* (`fulltext_item`).
- **Tooling** ([02-pyzotero-tooling](02-pyzotero-tooling/task.md)) — `scripts/zotero_tool.py` (PEP 723, `pyzotero==1.13.0` pinned + sidecar lock) exposes 9 JSON subcommands, local-first with Web fallback, local-storage-first PDF retrieval, and no secret leakage. Local full-text search (`qmode="everything"`) was later verified live (task 05, after the local API was enabled) to work in local mode; an early bug that forced `--fulltext` to the Web API was fixed so it honors the active access mode.
- **Workflow** ([03-paper-reading-workflow](03-paper-reading-workflow/task.md)) — `references/paper-reading.md` migrates the search → locate PDF → convert via `mistral-pdf-to-markdown` → save `Notes/PaperInMarkdown/Author_Year_ShortTitle.md` → section-by-section read workflow onto the new tooling, with no MCP.
- **Inventory** ([04-inventory-and-packaging](04-inventory-and-packaging/task.md)) — registered in `README.md`, `skills/CATEGORIES.md`, and `skills/using-superRA/SKILL.md` as a standalone Utility skill (not loaded by the Skill-Load Manifest); workflow choreography and generated agent files untouched.
- **Verification** ([05-verification](05-verification/task.md)) — two credential-free deterministic suites (36 checks total) cover behavior, the no-secret-leak invariant, `.env` parsing, and MCP/stale-instruction regression guards; all pass.

