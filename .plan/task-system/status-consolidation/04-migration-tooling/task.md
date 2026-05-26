---
title: "Update migration tooling"
status: not-started
review_status: ~
integration_status: ~
depends_on:
  - 02-data-layer
tags: [code]
script: skills/task-system/scripts/plan_migrate.py
input: []
output: []
created: 2026-05-26
updated: 2026-05-26
---

## Objective

Two migration paths need updating:

### 1. PLAN.md → .plan/ migration (`plan_migrate.py`)

Update to merge old `**Review status:**` into the unified `status` field:
- Remove `review_status` from the regex patterns (line 27) and from generated task templates (line 240)
- Keep reading `**Review status:**` from source PLAN.md — use it to override `status` per the migration mapping from the design spec (e.g., APPROVED → `status: approved`)
- Remove `_normalize_review_status()` helper (lines 201-215) — fold its logic into the status-determination flow
- Remove `review_status` from `_create_task_md()` signature (line 220) and root task template (line 302)

### 2. In-place .plan/ upgrade

Add a new `--upgrade-status` flag to `plan_migrate.py` (or a separate `plan_upgrade.py` script) that:
- Walks all `task.md` files in an existing `.plan/` tree
- For each file, reads the `(status, review_status)` pair
- Applies the migration mapping: if `review_status` is set and non-`~`, it takes precedence over `status`
- Removes the `review_status` line from frontmatter
- Writes the file back with only `status` and `integration_status`
- Reports what changed (dry-run mode with `--dry-run`)

## Results
