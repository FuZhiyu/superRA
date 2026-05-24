---
title: "Task System Redesign"
status: in-progress
review_status: ~
integration_status: ~
depends_on: []
tags: []
created: 2026-05-23
updated: 2026-05-24
---

## Objective

Redesign the task-system skill to eliminate the task/step distinction (everything is a task), add structured planner/implementer ownership via `## Objective` (planner-owned) and `## Results` (implementer-owned, recursive at every tree level), auto-rebuild the dashboard after CLI mutations, and rewrite the dashboard UI as a single-page recursive expand/collapse interface using the `frontend-design` skill.

**Methodology:** Modify the existing `skills/task-system/scripts/` codebase in place. Phase 1 changes the data model and task file format. Phase 2 adds auto-rebuild hooks to all mutation scripts. Phase 3 rewrites the dashboard HTML. Phase 4 migrates the existing `.plan/` tree to the new format. Phase 5 updates tests. The existing test suite (`test_task_system.py`) provides regression coverage throughout.

**Conventions:**
- Scripts follow existing `skills/*/scripts/` patterns: stdlib-only Python, argparse CLI, `from __future__ import annotations`, type-annotated functions
- Task file body sections: `## Objective` (planner-owned), `## Results` (implementer-owned), `## Decisions`, `## Review Notes`
- No more `## Steps` or checkbox procedures — leaf tasks are directories without subdirectories
- Auto-rebuild is best-effort (try/except, never blocks the primary mutation)
- Dashboard uses Google Fonts CDN for typography, Mermaid.js CDN for DAG, markdown-it CDN for rendering

**Output:**
- `skills/task-system/scripts/_task_io.py` — updated with `parse_body_sections()`, `objective`/`results` fields on `Task`
- `skills/task-system/scripts/task_create.py` — updated template, `--objective` arg, auto-rebuild
- `skills/task-system/scripts/task_update.py` — auto-rebuild hook
- `skills/task-system/scripts/task_add_result.py` — auto-rebuild hook
- `skills/task-system/scripts/task_link.py` — auto-rebuild hook
- `skills/task-system/scripts/task_rename.py` — auto-rebuild hook
- `skills/task-system/scripts/task_query.py` — `tree_to_json()` includes structured sections
- `skills/task-system/scripts/plan_dashboard.py` — complete HTML rewrite
- `skills/task-system/scripts/plan_migrate.py` — `--upgrade` flag for v1-to-v2 migration
- `skills/task-system/scripts/test_task_system.py` — updated fixtures, new test classes
- `skills/task-system/SKILL.md` — rewritten core concepts, updated format example

**Pipeline:** `~/.venv/bin/python -m pytest skills/task-system/scripts/test_task_system.py -v`

## Results

### Key Findings
- 7 subtasks implemented, 6 approved, 1 in revise (v2-migration scoped-stripping fix)
- 53 tests passing (up from 45), 8 new tests across 3 new test classes
- Dashboard: Source Serif 4 + IBM Plex Mono, recursive expand/collapse, dark/light mode
- Auto-rebuild eliminates manual dashboard regeneration after every CLI mutation
