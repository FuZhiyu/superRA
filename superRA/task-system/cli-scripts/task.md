---
title: "CLI Scripts"
status: not-started
depends_on:
  - core-data-layer
tags: []
created: 2026-05-23
---

## Objective

Build 6 CLI scripts for task CRUD: `task_create.py` (template with `## Objective` / `## Results`, `--objective` arg), `task_update.py` (frontmatter field updates), `task_add_result.py` (append findings/figures/notes), `task_link.py` (add/remove sibling deps with cycle detection), `task_rename.py` (rename with sibling cascade), `task_query.py` (tree/frontier/DAG queries, `tree_to_json()` with structured section fields).

## Results

### Key Findings
- 6 scripts, each 65–210 lines, all following argparse + function pattern
- `task_create.py` validates parent exists, no duplicates, deps are existing siblings
- `task_link.py` includes `_has_transitive_dep()` for cycle detection
- `task_rename.py` uses parse-first approach (validate all siblings before renaming)
- `task_query.py` provides tree (Unicode status icons), frontier (dispatch-ready leaves), DAG (Mermaid with classDef)
- `tree_to_json()` includes `objective`, `results`, `decisions`, `review_notes` parsed from body sections
