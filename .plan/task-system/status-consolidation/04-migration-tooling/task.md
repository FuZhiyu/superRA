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

Update to merge old `**Review status:**` and `**Integration status:**` into the unified `status` field:
- Remove `review_status` and `integration_status` from regex patterns and generated task templates
- Keep reading `**Review status:**` and `**Integration status:**` from source PLAN.md — use them to determine `status` per the migration mapping from the design spec
- Remove `_normalize_review_status()` helper — fold its logic into the status-determination flow
- Remove both fields from `_create_task_md()` signature and root task template

### 2. In-place .plan/ upgrade

Add a new `--upgrade-status` flag to `plan_migrate.py` (or a separate script) that:
- Walks all `task.md` files in an existing `.plan/` tree
- For each file, reads the `(status, review_status, integration_status)` triple
- Applies the migration mapping: most-recent lifecycle field takes precedence (`integration_status` > `review_status` > `status`)
- Removes both `review_status` and `integration_status` lines from frontmatter
- Also removes any `## Workflow Status` sections from task bodies
- Writes the file back with only `status`
- Reports what changed (dry-run mode with `--dry-run`)

## Results
