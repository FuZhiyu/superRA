---
title: "Cleanup Mechanism: Warn-Only task check for Lingering ## Sync Impact"
status: approved
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

## Results

Added a warn-only `sync-impact` check category to the task-tree diagnostic CLI.

- **Check function** — [task_check.py](../../../skills/task-tree/scripts/task_check.py): added `check_sync_impact` / `_check_sync_impact_recursive` (Check 5), mirroring the existing recursive category pattern (`status` / `dependency` / `rollup` / `placement`) and reusing the existing `Finding` dataclass (the objective's `CheckFinding` is named `Finding` in this codebase). The check matches the canonical heading exactly via `_SYNC_IMPACT_HEADING = re.compile(r"^##\s+Sync Impact\s*$", re.MULTILINE)` so it neither misses the canonical form nor over-matches near-misses. Every finding is advisory `severity="warning"`; the function reads `task.md` and never mutates. Wired into `run_checks` and the module docstring.
- **CLI choices** — added `sync-impact` to the `--category` choices in both [task_check.py:`parse_args`](../../../skills/task-tree/scripts/task_check.py) and [cli.py:575](../../../skills/task-tree/scripts/cli.py) (the wrapper subcommand surface).
- **Tests** — [test_task_tree.py](../../../skills/task-tree/scripts/test_task_tree.py): four tests after the placement-check block — lingering section yields one advisory finding on the right task; clean tree yields none; `--category sync-impact` selects only this check (verified against a tree that would otherwise trip placement); and a read-only/never-mutates assertion.
- **Sync-Map reconciliation** — grep of `skills/task-tree/scripts/` for `Sync Map` / `sync_map` / `SEMANTIC_MERGE` found **no** matches; `plan_migrate.py` already parses and preserves `## Sync Impact` (not a Sync Map) and never emits a Sync Map section, so migration cannot resurrect one. No change needed.

### Verification

- Full suite (repo CLAUDE.md run-line): **688 passed, 2 skipped**.
- The four new `sync_impact` tests pass in isolation: `4 passed, 270 deselected`.
- End-to-end through the wrapper: `superra task check --root <tree> --category sync-impact` on a tree where `01-a` carries `## Sync Impact` and `02-b` is clean emits exactly one `[WARNING] [sync-impact] 01-a: ...` finding (exit 1), and flags no other task.

Deviation from the objective wording: the objective names the finding class `CheckFinding`; the actual class is `Finding`. I reused `Finding` (the real shape) — this satisfies the objective intent (existing finding shape) rather than introducing a second, divergent class.
