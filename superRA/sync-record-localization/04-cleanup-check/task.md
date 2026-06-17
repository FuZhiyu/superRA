---
title: "Cleanup Mechanism: Warn-Only task check for Lingering ## Sync Impact"
status: not-started
depends_on:
  - 01-canonical-model
tags: []
created: 2026-06-17
---

## Objective

`## Sync Impact` is temporary scaffolding that must not survive past Integrate. Build the durable safety net that catches a leak, since the workflow closeout (in `03-integrate-skills`) relies on the agent remembering. This is the code half of the cleanup mechanism.

Add a warn-only `sync-impact` check category to the task-tree CLI:

- **`skills/task-tree/scripts/task_check.py`:** add a `sync-impact` category that walks the tree and emits an advisory (not error) finding for any task whose `task.md` carries a `## Sync Impact` section. Message guides the reader to remove it at Integrate closeout (or confirm it is a lasting task assumption that should be reworded out of the temporary section). Follow the existing category-function pattern (`status` / `dependency` / `rollup` / `placement`) and the existing `CheckFinding` shape.
- **`skills/task-tree/scripts/cli.py`:** add `sync-impact` to the `--category` choices (line ~575).
- **Tests:** add coverage in the check's test file (mirror the existing placement/rollup check tests) — a tree with a `## Sync Impact` section yields one advisory finding; a clean tree yields none; `--category sync-impact` selects only this check.

**Reconcile any Sync-Map handling in task-tree scripts:** check whether `skills/task-tree/scripts/plan_migrate.py` (legacy PLAN.md → tree migration) or `skills/task-tree/scripts/test_task_tree.py` carry `## Sync Map` handling or fixtures, and remove/adjust so migration does not resurrect a Sync Map section.

### Conventions

- **Warn-only, never auto-mutate.** Per superRA automation discipline, the check emits an advisory; it must not delete the section or change status. A `## Sync Impact` section is legitimate mid-Integrate, so this is a leak-detector, not a hard gate.

## Planner Guidance

The canonical section name is `## Sync Impact` (from `01-canonical-model`); match it exactly so the check does not miss or over-match.

Run the suite per the repo CLAUDE.md: `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts`.
