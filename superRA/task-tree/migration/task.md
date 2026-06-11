---
title: "Migration Script"
status: approved
depends_on:
  - core-data-layer
tags: []
script: skills/task-tree/scripts/plan_migrate.py
created: 2026-05-23
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

Retrospective audit notes (all MINOR; status unchanged per orchestrator instruction). The three previously annotated `→ implemented` items were verified in [plan_migrate.py](../../../skills/task-tree/scripts/plan_migrate.py) (Steps-scoped stripping, `[xX]` character class, section-boundary rewrite) and removed per re-review protocol.

> 1. [MINOR] Objective ([task.md:13](task.md#L13)) still says "generate `.plan/` tree" and "existing `.plan/` directories", but the script's default output is the `superRA/` root ([plan_migrate.py:567](../../../skills/task-tree/scripts/plan_migrate.py#L567) uses `TASK_ROOT_DIRNAME`). Stale since the task-root rename; rewrite in place.
> 2. [MINOR] Results ([task.md:22](task.md#L22)) say "Mutually exclusive CLI: `--plan-md` vs `--upgrade`", but the group is now three-way with `--upgrade-status` ([plan_migrate.py:55](../../../skills/task-tree/scripts/plan_migrate.py#L55)), which this task — the durable home for `plan_migrate.py` per its `script:` frontmatter — never mentions. Refresh the Results to the current command set.
