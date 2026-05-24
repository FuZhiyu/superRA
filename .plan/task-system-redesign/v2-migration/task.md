---
title: "V1-to-V2 Migration"
status: implemented
review_status: revise
integration_status: ~
depends_on:
  - data-model
tags: []
script: skills/task-system/scripts/plan_migrate.py
created: 2026-05-23
updated: 2026-05-24
---

## Objective

Update `_build_task_md()` to emit `## Objective` instead of `## Steps`. Add `_strip_checkboxes()` helper. Add `--upgrade` flag for in-place migration of existing `.plan/` directories. Idempotent.

## Results

### Key Findings
- `_build_task_md()` emits `## Objective` with stripped checkboxes, no `# Title` heading
- `--upgrade --plan-root .plan` walks tree recursively, converts format
- Mutually exclusive CLI: `--plan-md` vs `--upgrade`
- Idempotent: running on v2 files produces no changes

## Review Notes
> 1. [MAJOR] `_upgrade_task_body()` stripped checkboxes from entire body, not just `## Steps` section
>    → implemented: scoped stripping to Steps section only
> 2. [MINOR] Uppercase `[X]` not handled
>    → implemented: character class changed to `[xX ]`
> 3. [MINOR] Blank line after `## Objective` lost during `--upgrade`
>    → implemented: fixed via section-boundary rewrite
