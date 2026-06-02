---
title: "Auto-Rebuild Dashboard"
status: approved
depends_on:
  - core-data-layer
tags: []
created: 2026-05-23
---

## Objective

Add a lazy-import `generate_dashboard(plan_root)` call wrapped in `try/except Exception: pass` at the end of every mutating CLI function (`task_create`, `task_update`, `task_add_result`, `task_link`, `task_rename`). Best-effort — never blocks the primary mutation.

## Results

### Key Findings
- Auto-rebuild in all 5 mutation scripts (7 call sites total, including both branches of `task_link`)
- Early-return no-op paths correctly skip rebuild
- Adds ~0.1s per CLI call on a typical plan tree
