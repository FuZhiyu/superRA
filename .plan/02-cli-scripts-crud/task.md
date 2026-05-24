---
title: "CLI Scripts (CRUD)"
status: implemented
review_status: implemented
integration_status: ~
depends_on:
  - 01-core-data-layer-task-iopy

tags: []
created: 2026-05-23
updated: 2026-05-23
---

# CLI Scripts (CRUD)

## Steps

- [x] **Step 1: `task_create.py`** — `create_task(plan_root, path, title, depends_on, script, input, output)`. Validates parent exists, no duplicates, deps are existing siblings. Template with frontmatter + empty body sections.

- [x] **Step 2: `task_update.py`** — `update_task(plan_root, path, status, review_status, integration_status, title, add_tags, remove_tags, script)`. Validates enums. Bumps `updated` timestamp.

- [x] **Step 3: `task_add_result.py`** — `add_result(plan_root, path, finding, figure, note)`. Ensures `## Results` section exists, appends findings under `### Key Findings`, figures as `![caption](path)`, notes under `### Notes`.

- [x] **Step 4: `task_link.py`** — `link_task(plan_root, path, depends_on, remove)`. Validates sibling exists when adding. Warns on remove of non-existent dep.

- [x] **Step 5: `task_rename.py`** — `rename_task(plan_root, from_path, to_path)`. Must stay in same parent. Cascades `depends_on` updates to all siblings.

- [x] **Step 6: `task_query.py`** — `--tree` (indented with status icons), `--frontier` (dispatchable leaves), `--dag [subtree]` (Mermaid format with classDef color-coding). Filter by `--status`, `--tag`. `--json` output. `tree_to_json()` serializes full tree for dashboard.

---

## Results

**Status:** Completed (Task 2 approved 2026-05-23)

### Key Findings
- 6 scripts, each 65–195 lines, all following argparse + function pattern
- `task_create.py` validates: parent exists, no duplicate, deps are existing sibling directories with `task.md`
- `task_update.py` validates enum values against `VALID_STATUSES`, `VALID_REVIEW_STATUSES`, `VALID_INTEGRATION_STATUSES`
- `task_add_result.py` uses `_ensure_section()` to create `## Results` / `### Key Findings` / `### Notes` on demand
- `task_rename.py` enforces same-parent constraint, cascades `depends_on` updates to all siblings
- `task_query.py` provides 3 output modes: `--tree` (indented with Unicode status icons ○◐◑✗●), `--frontier` (dispatch-ready leaves), `--dag` (Mermaid with classDef color-coding)

---

