---
title: "Task System Skill — Plan"
status: not-started
review_status: ~
integration_status: ~
depends_on: []
tags: []
created: 2026-05-23
updated: 2026-05-23
---

# Task System Skill — Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all PLAN.md / RESULTS.md editing. Use `superRA:skill-creator` when editing any `skills/*/SKILL.md`. Steps use checkbox (`- [ ]`) syntax for tracking and cross-session handoff.

**Objective:** Add a `task-system` skill to superRA that replaces flat PLAN.md/RESULTS.md task tracking with a filesystem-based hierarchy where each task is a self-contained `task.md` (plan + results unified), and a generated HTML dashboard provides human-friendly visualization with tree, DAG, and kanban views.

**Methodology:** Build the system as a standalone skill (`skills/task-system/`) with Python CLI scripts for task CRUD, frontier computation, migration, and dashboard generation. Defer workflow integration to a follow-up PR.

**Conventions:**
- Scripts follow existing `skills/*/scripts/` patterns: stdlib-only Python, argparse CLI, `from __future__ import annotations`, type-annotated functions
- Task ID = relative path from plan root (e.g., `01-data-preparation/02-merge`)
- Dependencies are sibling-only (directory names within the same parent)
- Parent task status rolls up from children automatically

**Output:**
- `skills/task-system/SKILL.md` — skill definition + usage docs
- `skills/task-system/scripts/_task_io.py` — shared internals (parse, write, walk, frontier, rollup)
- `skills/task-system/scripts/task_create.py` — create task directory + task.md
- `skills/task-system/scripts/task_update.py` — update frontmatter fields
- `skills/task-system/scripts/task_query.py` — tree, frontier, DAG queries
- `skills/task-system/scripts/task_add_result.py` — append results to a task
- `skills/task-system/scripts/task_link.py` — add/remove dependency edges
- `skills/task-system/scripts/task_rename.py` — rename with sibling cascade
- `skills/task-system/scripts/plan_migrate.py` — convert PLAN.md + RESULTS.md to `.plan/` tree
- `skills/task-system/scripts/plan_dashboard.py` — generate self-contained HTML dashboard
- `skills/task-system/scripts/test_task_system.py` — pytest test suite

**Pipeline:** `~/.venv/bin/python -m pytest skills/task-system/scripts/test_task_system.py -v`

---

## Workflow Status

- [x] **Plan approved**
- [ ] **Execution complete**
- [ ] **Drift tests created**
- [ ] **Integrated**
- [ ] **Docs finalized**
- [ ] **Finished**

---

## Project Conventions

Walked at planning time (2026-05-23). Re-walk on-demand only.

### Repo root
- `/CLAUDE.md` (HEAD at 530e0ee): superRA contributor guidelines. Flat skill layout, lean agents + rich references, skill authoring guidelines, ownership table, DRY + Necessity tests for every instruction line.
- `/README.md` (HEAD at 530e0ee): User-facing product model. Skill categories table (domain, workflow, utility, meta). Install via `agents/.agents/plugins/marketplace.json`.

### Module-level docs walked
- `skills/CATEGORIES.md` (HEAD at 530e0ee): Skill category tables mirroring README, with one-line descriptions per skill.

### Not walked (not reachable from the planned diff)
- `skills/handoff-doc/`, workflow skills, agent specs, `skills/using-superRA/` — deferred to workflow integration PR.

---
