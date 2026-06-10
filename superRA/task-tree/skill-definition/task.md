---
title: "Skill Definition + Inventory"
status: approved
depends_on:
  - core-data-layer
  - cli-scripts
  - dashboard
tags: []
created: 2026-05-23
---

## Objective

Write `SKILL.md` with core concepts (everything is a task, `## Objective` planner-owned, `## Results` implementer-owned recursive, filesystem hierarchy, sibling-only deps, status rollup), directory structure, full command surface with examples, task file format template, auto-rebuild note, `--upgrade` docs. Update `CATEGORIES.md` and `README.md` skill inventory.

## Results

### Key Findings
- SKILL.md: ~90 lines, routing layer over three references (commands.md, task-file-contract.md, internals.md); `--upgrade` documented via pointer to internals.md §Migration
- Added `superra task check` routing row and `##Diagnostics` section to commands.md
- `CATEGORIES.md`: trimmed to discovery-level description; updated "HTML dashboard generation" to live SSE server wording
- `README.md`: trimmed to discovery-level description with live SSE server wording

