---
title: "Task Tree Skill"
status: approved
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
- Hook does validation/status propagation only; dashboard renders on demand (`superra dashboard`) or via explicit export (`superra dashboard export`)
- Dashboard: live SSE server (FastAPI + htmx + markdown-it + KaTeX); Google Fonts CDN for typography; vendored render libraries for offline export

**Output (see `skills/task-tree/references/internals.md §Script Inventory` for the full table):**
- `skills/task-tree/SKILL.md` — skill definition + routing docs
- `skills/task-tree/scripts/` — 19 production scripts (4 data-layer modules + 15 entry scripts, including the hook and wrapper resolver) + 7 test modules
- Key entry scripts: `cli.py` (command router), `task_read.py`, `task_create.py`, `task_update.py`, `task_query.py`, `task_check.py`, `task_hook.py`, `plan_dashboard.py`, `plan_migrate.py`, `dashboard_artifact_workflow.py`

**Pipeline:** `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts`

## Results

### Key Findings
- 19 production scripts (4 data-layer modules + 15 entry scripts) + 7 test modules; 646 tests passing, 2 skipped
- Eliminated task/step distinction: everything is a task, leaf = no subdirectories
- Structured ownership: `## Objective` (planner) / `## Results` (implementer, recursive)
- Hook does validation/status propagation only — no auto-rebuild; dashboard renders on demand (live SSE server) or via explicit `superra dashboard export`
- Dashboard: live SSE server (FastAPI/htmx/markdown-it/KaTeX), multi-worktree support, vendored offline export; Source Serif 4 + IBM Plex Mono typography
- `superRA/` task files are now the primary researcher-facing results record: implementers write substantive task `## Results`, reviewers verify result substance, orchestrators selectively summarize approved child results into parent `## Results`, and the old separate `RESULTS.md` / `final-form.md` maturation path has been removed ([planning-redesign/planmd-sweep/task.md](planning-redesign/planmd-sweep/task.md)).
