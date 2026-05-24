---
title: "Auto-Rebuild Dashboard"
status: approved
review_status: approved
integration_status: ~
depends_on:
  - data-model
tags: []
created: 2026-05-23
updated: 2026-05-24
---

## Objective

Add a lazy-import `generate_dashboard(plan_root)` call wrapped in `try/except Exception: pass` at the end of every mutating CLI function. Best-effort — never blocks the primary mutation.

## Results

### Key Findings
- Auto-rebuild added to all 5 mutation scripts (7 call sites total, including both branches of `task_link`)
- Early-return no-op paths correctly skip rebuild
- Dashboard regeneration adds ~0.1s per CLI call on a typical plan tree
