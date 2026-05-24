---
title: "Core Data Layer (`_task_io.py`)"
status: implemented
review_status: implemented
integration_status: ~
depends_on: []
tags: []
script: skills/task-system/scripts/_task_io.py
created: 2026-05-23
updated: 2026-05-23
---

## Objective
- **Step 1: Define `Task` dataclass** — fields: path, dir_path, title, status, review_status, integration_status, depends_on, tags, script, input, output, created, updated, body, children. Properties: is_leaf, is_root, slug, effective_status.

- **Step 2: YAML frontmatter parser** — stdlib-only (`re`), no PyYAML. Handles scalars, inline lists `[a, b]`, multi-line lists (`  - item`), tilde `~`. Regex: `FRONTMATTER_RE = r"\A---\n(.*?\n)---\n(.*)"`.

- **Step 3: Serializer** — `serialize_frontmatter()` with canonical field order (title, status, review_status, ..., updated). `write_task()` wraps frontmatter + body.

- **Step 4: Tree walker** — `walk_plan(plan_root)` recursively discovers `task.md` files in sorted subdirectories, builds `Task` tree. `_find_plan_root()` walks up from any task to the root.

- **Step 5: Frontier computation** — `compute_frontier(root)` returns leaf tasks where: own status is `not-started`/`in-progress`, all sibling `depends_on` targets are `approved`, and all ancestor sibling deps are met (recursive).

- **Step 6: Status rollup** — `compute_status(task)` for branch tasks: all approved → approved, any revise → revise, any in-progress/implemented → in-progress, else not-started.

---

## Results

**Status:** Completed (Task 1 approved 2026-05-23)

### Key Findings
- 383-line module, stdlib-only (no PyYAML dependency)
- `Task` dataclass with 14 fields + 4 computed properties (`is_leaf`, `is_root`, `slug`, `effective_status`)
- Custom YAML frontmatter parser handles scalars, inline lists, multi-line lists, and tilde values via regex
- `walk_plan()` builds full task tree by recursively scanning sorted subdirectories for `task.md` files
- `compute_frontier()` correctly handles nested DAGs — checks sibling deps at each level and propagates ancestor readiness
- Status rollup uses priority ordering: all-approved → any-revise → any-in-progress/implemented → not-started

---

