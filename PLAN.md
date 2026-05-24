# Task System Skill — Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all PLAN.md / RESULTS.md editing. Use `superRA:skill-creator` when editing any `skills/*/SKILL.md`.

**Objective:** Add a `task-system` skill to superRA that replaces flat PLAN.md/RESULTS.md task tracking with a filesystem-based hierarchy where each task is a self-contained `task.md` with planner-owned `## Objective` and implementer-owned `## Results` (recursive at every level), and a generated HTML dashboard provides human-friendly visualization.

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
- `/CLAUDE.md` (HEAD at dd7ad7d): superRA contributor guidelines. Flat skill layout, lean agents + rich references, skill authoring guidelines, ownership table, DRY + Necessity tests for every instruction line.
- `/README.md` (HEAD at dd7ad7d): User-facing product model. Skill categories table (domain, workflow, utility, meta). Install via `agents/.agents/plugins/marketplace.json`.

### Module-level docs walked
- `skills/CATEGORIES.md` (HEAD at dd7ad7d): Skill category tables mirroring README, with one-line descriptions per skill. `task-system` listed under Utility with "DAG rendering" in description.
- `skills/using-superRA/SKILL.md` (HEAD at dd7ad7d): Skill inventory includes `task-system` row.

### Not walked (not reachable from the planned diff)
- `skills/handoff-doc/`, workflow skills, agent specs — not modified by this work.

---

### Task 1: Core Data Layer
**Depends on:** *(none)*
**Review status:** APPROVED

**Script:** `skills/task-system/scripts/_task_io.py`

Build `_task_io.py`: `Task` dataclass (path, title, status, review/integration status, depends_on, tags, script, input, output, timestamps, body, children + computed properties). YAML frontmatter parser (stdlib-only). Serializer with canonical field order. Tree walker (`walk_plan`). Frontier computation (`compute_frontier`). Status rollup (`compute_status`). Body section parsing (`parse_body_sections`) populating `objective`, `results`, `decisions`, `review_notes` fields.

---

### Task 2: CLI Scripts
**Depends on:** Task 1
**Review status:** APPROVED

**Scripts:** `task_create.py`, `task_update.py`, `task_add_result.py`, `task_link.py`, `task_rename.py`, `task_query.py`

Build 6 CLI scripts: `task_create.py` (template with `## Objective` / `## Results`, `--objective` arg), `task_update.py` (frontmatter updates with enum validation), `task_add_result.py` (append findings/figures/notes), `task_link.py` (add/remove sibling deps with cycle detection), `task_rename.py` (rename with sibling cascade), `task_query.py` (tree/frontier/DAG queries, `tree_to_json()` with structured section fields).

---

### Task 3: Auto-Rebuild Dashboard
**Depends on:** Task 1
**Review status:** APPROVED

**Scripts:** `task_create.py`, `task_update.py`, `task_add_result.py`, `task_link.py`, `task_rename.py`

Add lazy-import `generate_dashboard(plan_root)` call wrapped in `try/except Exception: pass` at the end of every mutating CLI function. Best-effort — never blocks the primary mutation. 7 call sites across 5 scripts.

---

### Task 4: Dashboard
**Depends on:** Task 1, Task 2
**Review status:** APPROVED

**Script:** `skills/task-system/scripts/plan_dashboard.py`

Build `plan_dashboard.py`: generate self-contained HTML dashboard from `.plan/` tree. Single-page recursive expand/collapse where all tasks are visible at once with progressive disclosure (3 levels: title row → children + section toggles → rendered markdown). Source Serif 4 + IBM Plex Mono typography, warm parchment/ink palette, tree connector lines, CSS transitions, dark/light mode. Tree, DAG (Mermaid), and Kanban views.

---

### Task 5: Migration
**Depends on:** Task 1
**Review status:** REVISE

**Script:** `skills/task-system/scripts/plan_migrate.py`

Build `plan_migrate.py`: parse PLAN.md task blocks + RESULTS.md sections, generate `.plan/` tree with slugified directories, infer status from checkboxes. Emit `## Objective` (not `## Steps`). Add `--upgrade` flag for in-place v1→v2 migration. Idempotent.

> **Review notes:**
> 1. [MAJOR] `_upgrade_task_body()` stripped checkboxes from entire body, not just `## Steps` section
>    → implemented: scoped stripping to Steps section only
> 2. [MINOR] Uppercase `[X]` not handled
>    → implemented: character class changed to `[xX]`
> 3. [MINOR] Blank line after `## Objective` lost during `--upgrade`
>    → implemented: fixed via section-boundary rewrite

---

### Task 6: Skill Definition + Inventory
**Depends on:** Task 1, Task 2, Task 4
**Review status:** APPROVED

Write `SKILL.md` with core concepts (everything is a task, `## Objective` planner-owned, `## Results` implementer-owned recursive, filesystem hierarchy, sibling-only deps, status rollup), directory structure, full command surface with examples including `--upgrade`, task file format template, auto-rebuild note. Update `CATEGORIES.md` and `README.md` skill inventory.

---

### Task 7: Test Suite
**Depends on:** Task 1, Task 2, Task 3, Task 4, Task 5
**Review status:** APPROVED

**Script:** `skills/task-system/scripts/test_task_system.py`

Build `test_task_system.py`: fixtures for flat and nested plan trees (v2 format), tests for frontmatter parsing, task CRUD, tree walking, status rollup, frontier computation, migration, dashboard generation, body section parsing (`TestParseBodySections`), auto-rebuild (`TestAutoRebuild`), and v1→v2 migration idempotency (`TestMigrateV2`). 53 tests total.
