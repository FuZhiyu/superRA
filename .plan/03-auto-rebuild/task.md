---
title: "Auto-Rebuild Dashboard"
status: approved
review_status: approved
integration_status: ~
depends_on:
  - 01-data-model
tags: []
created: 2026-05-23
updated: 2026-05-24
---

## Objective

Add a lazy-import `generate_dashboard(plan_root)` call wrapped in `try/except Exception: pass` at the end of every mutating CLI function: `task_create`, `task_update`, `task_add_result`, `task_link`, `task_rename`. Best-effort — never blocks the primary mutation.

## Results

### Key Findings
- Auto-rebuild added to all 5 mutation scripts (7 call sites total, including both branches of `task_link`)
- Early-return no-op paths correctly skip rebuild (no mutation occurred)
- Dashboard regeneration adds ~0.1s to each CLI call on a typical plan tree
- Reviewer approved with no findings
