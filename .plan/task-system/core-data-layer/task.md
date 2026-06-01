---
title: "Core Data Layer"
status: approved
depends_on: []
tags: []
script: skills/task-system/scripts/_task_io.py
created: 2026-05-23
---

## Objective

Build `_task_io.py`: `Task` dataclass (path, title, status, review/integration status, depends_on, tags, script, input, output, timestamps, body, children + computed properties). YAML frontmatter parser (stdlib-only, no PyYAML). Serializer with canonical field order. Tree walker (`walk_plan`). Frontier computation (`compute_frontier`). Status rollup (`compute_status`). Body section parsing (`parse_body_sections`) populating `objective`, `results`, `decisions`, `review_notes` fields.

## Results

### Key Findings
- 400+ line module, stdlib-only (no PyYAML dependency)
- `Task` dataclass with 18 fields + 4 computed properties (`is_leaf`, `is_root`, `slug`, `effective_status`)
- Custom YAML frontmatter parser handles scalars, inline lists, multi-line lists, and tilde values
- `walk_plan()` builds full task tree by recursively scanning sorted subdirectories
- `compute_frontier()` handles nested DAGs — checks sibling deps at each level, propagates ancestor readiness
- Status rollup: all-approved → any-revise → any-in-progress/implemented → not-started
- `parse_body_sections()` splits on `## ` headers into `{name: content}` dict; fields are read-only views derived from `body`
