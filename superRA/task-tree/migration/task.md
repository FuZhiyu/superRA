---
title: "Migration Script"
status: approved
depends_on:
  - core-data-layer
---

## Objective

Build `plan_migrate.py`: parse PLAN.md task blocks and RESULTS.md sections and generate a `superRA/` task tree with slugified directories, inferring status from checkboxes and emitting `## Objective` (not `## Steps`). Provide an in-place `--upgrade` path for existing task trees. Idempotent.

## Results

`skills/task-tree/scripts/plan_migrate.py` is the durable home for task-tree migration. It parses PLAN.md via regex and RESULTS.md via section matching, and its default output is the `superRA/` root (`TASK_ROOT_DIRNAME`).

### Key Findings
- Slugify produces clean directory names (lowercase, strip non-word, hyphenate, max 60 chars).
- Status inference: all checked with no review → implemented; partial → in-progress; APPROVED → approved.
- `--upgrade` walks a task root recursively, renaming `## Steps` → `## Objective` and stripping checkbox prefixes; `--upgrade-status` migrates legacy `(status, review_status, integration_status)` triples to the single `status` field.
- The CLI mode group is three-way and mutually exclusive: `--plan-md` (from-plan) vs `--upgrade` vs `--upgrade-status`.
