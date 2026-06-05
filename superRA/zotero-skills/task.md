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
- **First increment** — the MCP-free `zotero-paper-reader` skill (tasks 01–05) was integrated via PR [#31](https://github.com/FuZhiyu/superRA/pull/31) to `main` (2026-06-04). The PR is still open (main unchanged at `3e0de358`).
- **Second increment (post-PR)** — after PR #31, the branch gained: the vendored `mistral-pdf-to-markdown` skill (task 06), multi-library support and the local-API full-text-search fix in `zotero_tool.py`, harness-neutral `<skill-dir>` paths, and expanded tests. Captured as task 06 plus refreshed Results in tasks 02–05; all of tasks 02–06 re-reviewed and re-approved in this second integration pass.
- Protect: drift/regression suite is `tests/test-zotero-tool.sh` (24), `tests/test-zotero-skill-text.sh` (16), and `tests/test-mistral-skill-text.sh` (9) — full suite passes.
- Integrate: integration review APPROVED over `3e0de358..HEAD`; one MAJOR (vendored converter must run via `uv run --script`, not `uv run python`/bare `python`, or PEP 723 deps are ignored) and one MINOR (stale verification prose) found and fixed. Minimum-net-diff sweep clean: every hunk is net-new and ties to an approved objective. Consolidation gate: clean-enough (6 coherent tasks, no structural debt) — no pass needed.
- Document: Results are reader-facing and reviewer-confirmed across all six tasks; no separate maturation pass needed.
- Finish: second increment pushed to update the existing open PR [#31](https://github.com/FuZhiyu/superRA/pull/31) to `main` (fast-forward, no re-create). Freshness re-checked before push: `origin/main` unchanged at `3e0de358`.

## Results

### Key Findings

The MCP-free `zotero-paper-reader` skill is complete and verified, and now self-contained in-repo, across six tasks:

- **Contract** ([01-skill-contract](01-skill-contract/task.md)) — `SKILL.md` + `references/access-modes.md` define a local-first / Web-API-fallback contract with a capability matrix; full-text *search* (`items(q=..., qmode="everything")`) is kept distinct from attachment full-text *retrieval* (`fulltext_item`).
- **Tooling** ([02-pyzotero-tooling](02-pyzotero-tooling/task.md)) — `scripts/zotero_tool.py` (PEP 723, `pyzotero==1.13.0` pinned + sidecar lock) exposes 9 JSON subcommands, local-first with Web fallback, local-storage-first PDF retrieval, and no secret leakage. Local full-text search (`qmode="everything"`) was later verified live (task 05, after the local API was enabled) to work in local mode; an early bug that forced `--fulltext` to the Web API was fixed so it honors the active access mode.
- **Workflow** ([03-paper-reading-workflow](03-paper-reading-workflow/task.md)) — `references/paper-reading.md` migrates the search → locate PDF → convert via `mistral-pdf-to-markdown` → save `Notes/PaperInMarkdown/Author_Year_ShortTitle.md` → section-by-section read workflow onto the new tooling, with no MCP.
- **Inventory** ([04-inventory-and-packaging](04-inventory-and-packaging/task.md)) — registered in `README.md`, `skills/CATEGORIES.md`, and `skills/using-superRA/SKILL.md` as a standalone Utility skill (not loaded by the Skill-Load Manifest); workflow choreography and generated agent files untouched.
- **Verification** ([05-verification](05-verification/task.md)) — credential-free deterministic suites cover behavior, the no-secret-leak invariant, `.env` parsing, and MCP/stale-instruction regression guards; plus a live local-mode smoke test (after the researcher enabled the Zotero local API) that confirmed health/search/children/pdf and the corrected local full-text-search boundary.
- **Vendored conversion skill** ([06-vendor-mistral-skill](06-vendor-mistral-skill/task.md)) — `mistral-pdf-to-markdown` was migrated into `skills/mistral-pdf-to-markdown/` as the canonical in-repo home for the PDF→Markdown step behind `zotero-paper-reader`, removing the external-plugin dependency that previously left conversion as a dead end. Registered as a standalone Utility skill (not loaded by the Manifest) and locked with a text-regression test.

