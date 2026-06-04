---
title: "Replace Zotero MCP with Zotero Skills"
status: in-progress
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

## Results

### Key Findings

- Pending.

