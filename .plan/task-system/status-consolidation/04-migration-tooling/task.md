---
title: "Update migration tooling"
status: implemented
review_status: approved
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

Both migration paths updated in [`plan_migrate.py`](skills/task-system/scripts/plan_migrate.py).

### Part 1: PLAN.md -> .plan/ migration

- Replaced `_normalize_review_status()` with `_normalize_status_value()` (returns empty string instead of `~` for unrecognized values)
- Rewrote `_compute_status_from_steps()` to apply the migration mapping: `integration_status` > `review_status` > checkbox inference
- Removed `review_status` and `integration_status` parameters from `_build_task_md()` signature
- Removed both fields from the root task template in `migrate()`
- PLAN.md `**Review status:**` and `**Integration status:**` regex patterns kept in `FIELD_RE` for reading; values feed into the unified status determination

### Part 2: In-place .plan/ upgrade (`--upgrade-status`)

- Added `--upgrade-status` flag (mutually exclusive with `--plan-md` and `--upgrade`)
- Added `--dry-run` flag for preview mode
- `upgrade_status()` function walks all `task.md` files and applies `_apply_migration_mapping()` (integration_status > review_status > status), strips stale frontmatter fields, removes `## Workflow Status` sections, and cleans up double blank lines
- Dry-run tested against this project's `.plan/` tree: 60 files identified for update, precedence logic confirmed correct (e.g., integration_status=revise overrides review_status=approved)

### Tests

102 tests pass. New test classes in [`test_task_system.py`](skills/task-system/scripts/test_task_system.py):
- `TestUpgradeStatus` (8 tests): field stripping, migration mapping precedence, `## Workflow Status` removal, dry-run behavior, idempotency, multi-file processing
- `TestMigrationMapping` (3 tests): integration_status wins, review_status wins over checkboxes, checkbox fallback

Existing tests updated: removed `review_status` from fixtures and assertions that referenced the removed `Task.review_status` attribute; added assertions that migrated output contains no stale fields.
