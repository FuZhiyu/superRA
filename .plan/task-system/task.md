---
title: "Task System Skill"
status: in-progress
depends_on: []
tags: []
created: 2026-05-23
updated: 2026-05-31
---

## Objective

Add a `task-system` skill to superRA that replaces flat PLAN.md/RESULTS.md task tracking with a filesystem-based hierarchy where each task is a self-contained `task.md` with planner-owned `## Objective` and implementer-owned `## Results` (recursive at every level), and a generated HTML dashboard provides human-friendly visualization.

**Methodology:** Build as a standalone skill (`skills/task-system/`) with Python CLI scripts for task CRUD, frontier computation, migration, and dashboard generation. Defer workflow integration to a follow-up PR.

**Conventions:**
- Scripts follow existing `skills/*/scripts/` patterns: stdlib-only Python, argparse CLI, `from __future__ import annotations`, type-annotated functions
- Task file body sections: `## Objective` (planner-owned), `## Results` (implementer-owned), `## Decisions`, `## Review Notes`
- Everything is a task — leaf tasks are directories without subdirectories
- Dependencies are sibling-only; parent status rolls up from children automatically
- Auto-rebuild is best-effort (try/except, never blocks the primary mutation)
- Dashboard uses Google Fonts CDN for typography, Mermaid.js CDN for DAG, markdown-it CDN for rendering

**Output:**
- `skills/task-system/SKILL.md` — skill definition + usage docs
- `skills/task-system/scripts/_task_io.py` — shared internals (parse, write, walk, frontier, rollup, body section parsing)
- `skills/task-system/scripts/task_create.py` — create task directory + task.md (with auto-rebuild)
- `skills/task-system/scripts/task_update.py` — update frontmatter fields (with auto-rebuild)
- `skills/task-system/scripts/task_query.py` — tree, frontier, DAG queries, structured JSON output
- `skills/task-system/scripts/task_add_result.py` — append results (with auto-rebuild)
- `skills/task-system/scripts/task_link.py` — add/remove dependency edges (with auto-rebuild)
- `skills/task-system/scripts/task_rename.py` — rename with sibling cascade (with auto-rebuild)
- `skills/task-system/scripts/plan_migrate.py` — PLAN.md migration + `--upgrade` for v1→v2
- `skills/task-system/scripts/plan_dashboard.py` — single-page recursive expand/collapse HTML dashboard
- `skills/task-system/scripts/test_task_system.py` — 53 tests

**Pipeline:** `~/.venv/bin/python -m pytest skills/task-system/scripts/test_task_system.py -v`

## Results

### Key Findings
- 11 scripts, 53 tests, full CRUD + migration + dashboard
- Eliminated task/step distinction: everything is a task, leaf = no subdirectories
- Structured ownership: `## Objective` (planner) / `## Results` (implementer, recursive)
- Auto-rebuild: dashboard stays current after every CLI mutation
- Dashboard: Source Serif 4 + IBM Plex Mono, recursive expand/collapse, dark/light mode
