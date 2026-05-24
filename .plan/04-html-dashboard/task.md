---
title: "HTML Dashboard"
status: implemented
review_status: implemented
integration_status: ~
depends_on:
  - 01-core-data-layer-task-iopy
  - 02-cli-scripts-crud

tags: []
script: skills/task-system/scripts/plan_dashboard.py
created: 2026-05-23
updated: 2026-05-23
---

# HTML Dashboard

## Steps

- [x] **Step 1: Dashboard generator** — `generate_dashboard(plan_root, output_path)`. Walks plan tree via `_task_io.walk_plan()`, serializes to JSON via `tree_to_json()`, embeds as `__TASK_DATA_JSON__` in HTML template string.

- [x] **Step 2: HTML template — layout** — summary bar (title, stats, view buttons, status filter, theme toggle), sidebar (search + tree), main content area (detail/DAG/kanban views). CSS custom properties for dark/light mode.

- [x] **Step 3: Tree view** — collapsible hierarchy with status badges (color-coded), progress counts on branch nodes (`approved/total`), click to select.

- [x] **Step 4: Task detail panel** — rendered markdown body via markdown-it (CDN), progressive disclosure via `<details>` for Steps (with completion count), Results, Review Notes. Meta bar with status badge, path, depends_on, script, tags.

- [x] **Step 5: DAG view** — Mermaid.js (CDN) dependency graph for selected subtree's children. Nodes colored by effective status. `mermaid.run()` for dynamic rendering.

- [x] **Step 6: Kanban view** — columns by status (Not Started, In Progress, Implemented, Revise, Approved). Cards show title + path, click navigates to tree view.

- [x] **Step 7: Search/filter** — text search across titles and paths, status filter dropdown. Filters apply to tree sidebar.

---

## Results

**Status:** Completed (Task 4 approved 2026-05-23)

### Key Findings
- Self-contained 445-line HTML template embedded as Python string constant in `plan_dashboard.py`
- CDN dependencies: markdown-it v14 (render task bodies), Mermaid v11 (DAG visualization)
- CSS custom properties enable dark/light mode with 12 theme variables each
- 5 views: summary bar, tree sidebar, task detail, DAG, kanban
- Tree view shows collapsible hierarchy with status badges (5 colors) and branch progress counts
- Task detail uses `<details>/<summary>` for progressive disclosure with step completion counts
- DAG view renders Mermaid `graph LR` with status-colored nodes per subtree's children
- Kanban shows leaf tasks only (the actionable units), grouped by status, read-only
- Search filters tree items by title and path; status dropdown filters by effective status
- Dashboard data embedded as JSON blob replacing `__TASK_DATA_JSON__` placeholder at generation time

---

