---
title: "Task Tree Skill"
status: revise
depends_on: []
tags: []
created: 2026-05-23
---

## Objective

Add a `task-tree` skill to superRA that replaces flat PLAN.md/RESULTS.md task tracking with a filesystem-based hierarchy where each task is a self-contained `task.md` with planner-owned `## Objective` and implementer-owned `## Results` (recursive at every level), and a generated HTML dashboard provides human-friendly visualization.

**Methodology:** Build as a standalone skill (`skills/task-tree/`) with Python CLI scripts for task CRUD, frontier computation, migration, and dashboard generation. Defer workflow integration to a follow-up PR.

**Conventions:**
- Scripts follow existing `skills/*/scripts/` patterns: stdlib-only Python, argparse CLI, `from __future__ import annotations`, type-annotated functions
- Task file body sections: `## Objective` (planner-owned), `## Results` (implementer-owned), `## Decisions`, `## Review Notes`
- Everything is a task — leaf tasks are directories without subdirectories
- Dependencies are sibling-only; parent status rolls up from children automatically
- Auto-rebuild is best-effort (try/except, never blocks the primary mutation)
- Dashboard uses Google Fonts CDN for typography, Mermaid.js CDN for DAG, markdown-it CDN for rendering

**Output:**
- `skills/task-tree/SKILL.md` — skill definition + usage docs
- `skills/task-tree/scripts/_task_io.py` — shared internals (parse, write, walk, frontier, rollup, body section parsing)
- `skills/task-tree/scripts/task_create.py` — create task directory + task.md (with auto-rebuild)
- `skills/task-tree/scripts/task_update.py` — update frontmatter fields (with auto-rebuild)
- `skills/task-tree/scripts/task_query.py` — tree, frontier, DAG queries, structured JSON output
- `skills/task-tree/scripts/task_add_result.py` — append results (with auto-rebuild)
- `skills/task-tree/scripts/task_link.py` — add/remove dependency edges (with auto-rebuild)
- `skills/task-tree/scripts/task_rename.py` — rename with sibling cascade (with auto-rebuild)
- `skills/task-tree/scripts/plan_migrate.py` — PLAN.md migration + `--upgrade` for v1→v2
- `skills/task-tree/scripts/plan_dashboard.py` — single-page recursive expand/collapse HTML dashboard
- `skills/task-tree/scripts/test_task_tree.py` — 53 tests

**Pipeline:** `~/.venv/bin/python -m pytest skills/task-tree/scripts/test_task_tree.py -v`

## Results

### Key Findings
- 11 scripts, 53 tests, full CRUD + migration + dashboard
- Eliminated task/step distinction: everything is a task, leaf = no subdirectories
- Structured ownership: `## Objective` (planner) / `## Results` (implementer, recursive)
- Auto-rebuild: dashboard stays current after every CLI mutation
- Dashboard: Source Serif 4 + IBM Plex Mono, recursive expand/collapse, dark/light mode
- `.plan/` task files are now the primary researcher-facing results record: implementers write substantive task `## Results`, reviewers verify result substance, orchestrators selectively summarize approved child results into parent `## Results`, and the old separate `RESULTS.md` / `final-form.md` maturation path has been removed ([planning-redesign/planmd-sweep/task.md](planning-redesign/planmd-sweep/task.md)).

## Review Notes

1. **[MAJOR]** [task.md:20](task.md#L20), [task.md:26-31](task.md#L26), [task.md:44](task.md#L44) — Objective conventions/output and Results assert auto-rebuild behavior ("with auto-rebuild" on five output lines; "Auto-rebuild is best-effort"; "dashboard stays current after every CLI mutation") that was deliberately removed: no dashboard file is written outside an explicit `superra dashboard export` ([task_hook.py](../../skills/task-tree/scripts/task_hook.py), [internals.md:263](../../skills/task-tree/references/internals.md#L263)), and [`TestNoAutoRebuild`](../../skills/task-tree/scripts/test_task_tree.py#L1705) locks in the opposite behavior. Fix: delete the auto-rebuild claims and state the current contract — hook does validation/status propagation only; dashboard renders on demand (live server) or via explicit export. (Handed over from the core-data-layer reviewer.)
2. **[MAJOR]** [task.md:23-36](task.md#L23) — the **Output** list and counts are two generations stale: "11 scripts, 53 tests", a script list ending at `plan_dashboard.py`, "`test_task_tree.py` — 53 tests". The live directory adds `cli.py`, `task_read.py`, `task_check.py`, `task_comment.py`, `task_hook.py`, `wrapper_resolver.py`, `_comments.py`, `_worktree_discovery.py`, `dashboard_artifact_workflow.py`, four more test modules plus a `tests/` package, and the suite is 612 tests (verified green). This is the workstream's public summary; the contract's stale-content checklist requires rewriting superseded output descriptions in place. Fix: rewrite Output to the current entry-script + data-layer shape (or point at a corrected `internals.md §Script Inventory`) and update "11 scripts, 53 tests" in Results accordingly.
3. **[MAJOR]** [task.md:46](task.md#L46) — present-tense "`.plan/` task files are now the primary researcher-facing results record"; the task root has been `superRA/` since the rename. Fix: replace `.plan/` with `superRA/`.
4. **[MINOR]** [task.md:36](task.md#L36) — the **Pipeline** line (`~/.venv/bin/python -m pytest skills/task-tree/scripts/test_task_tree.py -v`) contradicts the canonical run form in [CLAUDE.md §Local Task-Tree CLI Development](../../CLAUDE.md) and covers only one of seven test modules. Fix: update to the `uv run --with …` form over `skills/task-tree/scripts`.
