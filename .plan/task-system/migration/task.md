---
title: "Migration Script"
status: implemented
review_status: revise
integration_status: ~
depends_on:
  - core-data-layer
tags: []
script: skills/task-system/scripts/plan_migrate.py
created: 2026-05-23
updated: 2026-05-24
---

## Objective

Build `plan_migrate.py`: parse PLAN.md task blocks + RESULTS.md sections, generate `.plan/` tree with slugified directories, infer status from checkboxes. Emit `## Objective` (not `## Steps`). Add `--upgrade` flag for in-place v1→v2 migration of existing `.plan/` directories. Idempotent.

## Results

### Key Findings
- 450+ line script parsing PLAN.md via regex, RESULTS.md via section matching
- Slugify produces clean directory names (lowercase, strip non-word, hyphenate, max 60 chars)
- Status inference: all checked + no review → implemented; partial → in-progress; APPROVED → approved
- `--upgrade --plan-root .plan` walks recursively, renames `## Steps` → `## Objective`, strips checkbox prefixes
- Mutually exclusive CLI: `--plan-md` vs `--upgrade`

## Review Notes
> 1. [MAJOR] `_upgrade_task_body()` stripped checkboxes from entire body, not just `## Steps` section
>    → implemented: scoped stripping to Steps section only
> 2. [MINOR] Uppercase `[X]` not handled
>    → implemented: character class changed to `[xX]`
> 3. [MINOR] Blank line after `## Objective` lost during `--upgrade`
>    → implemented: fixed via section-boundary rewrite
