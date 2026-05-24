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

### Task 1: Core Data Layer (`_task_io.py`)
**Depends on:** *(none)*
**Review status:** IMPLEMENTED

**Script:** `skills/task-system/scripts/_task_io.py`

- [x] **Step 1: Define `Task` dataclass** — fields: path, dir_path, title, status, review_status, integration_status, depends_on, tags, script, input, output, created, updated, body, children. Properties: is_leaf, is_root, slug, effective_status.

- [x] **Step 2: YAML frontmatter parser** — stdlib-only (`re`), no PyYAML. Handles scalars, inline lists `[a, b]`, multi-line lists (`  - item`), tilde `~`. Regex: `FRONTMATTER_RE = r"\A---\n(.*?\n)---\n(.*)"`.

- [x] **Step 3: Serializer** — `serialize_frontmatter()` with canonical field order (title, status, review_status, ..., updated). `write_task()` wraps frontmatter + body.

- [x] **Step 4: Tree walker** — `walk_plan(plan_root)` recursively discovers `task.md` files in sorted subdirectories, builds `Task` tree. `_find_plan_root()` walks up from any task to the root.

- [x] **Step 5: Frontier computation** — `compute_frontier(root)` returns leaf tasks where: own status is `not-started`/`in-progress`, all sibling `depends_on` targets are `approved`, and all ancestor sibling deps are met (recursive).

- [x] **Step 6: Status rollup** — `compute_status(task)` for branch tasks: all approved → approved, any revise → revise, any in-progress/implemented → in-progress, else not-started.

---

### Task 2: CLI Scripts (CRUD)
**Depends on:** Task 1
**Review status:** IMPLEMENTED

**Scripts:** `task_create.py`, `task_update.py`, `task_add_result.py`, `task_link.py`, `task_rename.py`, `task_query.py`

- [x] **Step 1: `task_create.py`** — `create_task(plan_root, path, title, depends_on, script, input, output)`. Validates parent exists, no duplicates, deps are existing siblings. Template with frontmatter + empty body sections.

- [x] **Step 2: `task_update.py`** — `update_task(plan_root, path, status, review_status, integration_status, title, add_tags, remove_tags, script)`. Validates enums. Bumps `updated` timestamp.

- [x] **Step 3: `task_add_result.py`** — `add_result(plan_root, path, finding, figure, note)`. Ensures `## Results` section exists, appends findings under `### Key Findings`, figures as `![caption](path)`, notes under `### Notes`.

- [x] **Step 4: `task_link.py`** — `link_task(plan_root, path, depends_on, remove)`. Validates sibling exists when adding. Warns on remove of non-existent dep.

- [x] **Step 5: `task_rename.py`** — `rename_task(plan_root, from_path, to_path)`. Must stay in same parent. Cascades `depends_on` updates to all siblings.

- [x] **Step 6: `task_query.py`** — `--tree` (indented with status icons), `--frontier` (dispatchable leaves), `--dag [subtree]` (Mermaid format with classDef color-coding). Filter by `--status`, `--tag`. `--json` output. `tree_to_json()` serializes full tree for dashboard.

---

### Task 3: Migration Script
**Depends on:** Task 1
**Review status:** IMPLEMENTED

**Script:** `skills/task-system/scripts/plan_migrate.py`

- [x] **Step 1: Parse PLAN.md** — extract header (everything before `### Task 1:`), extract task blocks via `TASK_BLOCK_RE = r"^###\s+Task\s+(\d+):\s+(.+?)$"`. Per block: extract `**Depends on:**`, `**Review status:**`, `**Integration status:**`, `**Script:**`, `**Input:**`, `**Output:**` via field-specific regexes.

- [x] **Step 2: Parse RESULTS.md** — extract per-task results via `RESULTS_SECTION_RE = r"^##\s+Task\s+(\d+):\s+(.+?)$"`. Skip stubs (`Not started`).

- [x] **Step 3: Generate tree** — slugify titles (`re.sub` chain → lowercase, strip non-word, hyphenate). Map `Task N` numbers to `NN-slug/` directories. Convert `Task N` depends-on references to slug names. Infer status from checkbox states and review status. Build `task.md` with frontmatter + Steps + Results body sections.

- [x] **Step 4: Write root task.md** — header content → root `.plan/task.md` with `title: "Project Plan"` frontmatter.

---

### Task 4: HTML Dashboard
**Depends on:** Task 1, Task 2
**Review status:** IMPLEMENTED

**Script:** `skills/task-system/scripts/plan_dashboard.py`

- [x] **Step 1: Dashboard generator** — `generate_dashboard(plan_root, output_path)`. Walks plan tree via `_task_io.walk_plan()`, serializes to JSON via `tree_to_json()`, embeds as `__TASK_DATA_JSON__` in HTML template string.

- [x] **Step 2: HTML template — layout** — summary bar (title, stats, view buttons, status filter, theme toggle), sidebar (search + tree), main content area (detail/DAG/kanban views). CSS custom properties for dark/light mode.

- [x] **Step 3: Tree view** — collapsible hierarchy with status badges (color-coded), progress counts on branch nodes (`approved/total`), click to select.

- [x] **Step 4: Task detail panel** — rendered markdown body via markdown-it (CDN), progressive disclosure via `<details>` for Steps (with completion count), Results, Review Notes. Meta bar with status badge, path, depends_on, script, tags.

- [x] **Step 5: DAG view** — Mermaid.js (CDN) dependency graph for selected subtree's children. Nodes colored by effective status. `mermaid.run()` for dynamic rendering.

- [x] **Step 6: Kanban view** — columns by status (Not Started, In Progress, Implemented, Revise, Approved). Cards show title + path, click navigates to tree view.

- [x] **Step 7: Search/filter** — text search across titles and paths, status filter dropdown. Filters apply to tree sidebar.

---

### Task 5: Test Suite
**Depends on:** Task 1, Task 2, Task 3, Task 4
**Review status:** IMPLEMENTED

**Script:** `skills/task-system/scripts/test_task_system.py`

- [x] **Step 1: Fixtures** — `plan_root` (flat 3-task chain: 01-first → 02-second → 03-third), `plan_with_branches` (nested: 01-data-prep/{01-load, 02-merge} → 02-estimation).

- [x] **Step 2: `_task_io` tests** — `TestParseTask` (leaf, deps, root), `TestWalkPlan` (flat, nested), `TestComputeStatus` (leaf, partial rollup, all-approved rollup), `TestComputeFrontier` (linear chain, nested, all-approved, no-deps forest), `TestWriteTask` (roundtrip), `TestFrontmatterParsing` (inline list, multiline list, empty list, tilde).

- [x] **Step 3: CLI tests** — `TestTaskCreate` (basic, with deps, duplicate fails, bad dep fails), `TestTaskUpdate` (status, add tag, remove tag), `TestTaskLink` (add dep, remove dep), `TestTaskRename` (cascade), `TestTaskAddResult` (finding), `TestTaskQuery` (tree_to_json, render_dag).

- [x] **Step 4: Migration test** — `TestPlanMigrate.test_slugify`, `test_migrate_basic` (synthetic PLAN.md + RESULTS.md → verify tree structure, field extraction, dependency mapping, results merging).

- [x] **Step 5: Dashboard test** — `TestDashboard.test_generate_dashboard` (verify HTML output contains title, TASK_DATA, task names, mermaid).

---

### Task 6: Skill Definition + Inventory Updates
**Depends on:** Task 1, Task 2, Task 3, Task 4
**Review status:** IMPLEMENTED

- [x] **Step 1: `SKILL.md`** — frontmatter (name, description with trigger phrases, user-invocable: true). Body: core concepts (tasks vs steps, siblings-only deps), directory structure, command surface with examples, task file format template.

- [x] **Step 2: `CATEGORIES.md`** — add `task-system` row to Utility table.

- [x] **Step 3: `README.md`** — add `task-system` row to Utility Skills table.
