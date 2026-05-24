---
title: "Context-Aware Task Reading"
status: implemented
review_status: ~
integration_status: ~
depends_on:  []
tags: []
created: 2026-05-24
updated: 2026-05-24
---

## Objective

Create `skills/task-system/scripts/task_read.py` — the primary way agents understand a task before working on it. Reads a task and injects ancestor context as a chain.

### Output format (human-readable, default)

```
=== Ancestor Context ===

# [Root title]
[Root body — first section or first paragraph]

## [Parent title]  (status: approved)
[Parent body — first section or first paragraph]

=== Task: [Current title] ===
[Full task.md content — frontmatter rendered as readable key: value lines + all body sections]

=== Sibling Dependencies ===
- load-raw-data (approved) — "Load CRSP mutual fund holdings"
- clean-data (in-progress) — "Apply standard filters"
```

### CLI interface

```bash
python3 task_read.py --plan-root .plan --path data-preparation/merge [--no-ancestors] [--json]
```

### Behavior

- Walk from the plan root to the target task, collecting the first body section (or first paragraph if long) from each ancestor's task.md
- Display ancestor chain as progressive context with hierarchical headers
- Show the full current task.md content: frontmatter rendered as readable key-value pairs (not raw YAML), plus all `##` body sections
- Show sibling dependency status: for each entry in `depends_on`, show the sibling's title and effective status
- `--no-ancestors` flag: skip the ancestor chain, show only the current task
- `--json` flag: structured JSON output with `ancestors` array, `task` object (frontmatter + body sections dict), and `dependencies` array
- Auto-detect plan root if `--plan-root` not given: walk up from cwd looking for a directory containing `task.md` whose parent does not contain `task.md`
- Uses `walk_plan()`, `parse_frontmatter()`, and `parse_body_sections()` from `_task_io.py`

## Results

Created `skills/task-system/scripts/task_read.py` (stdlib-only, argparse CLI). Supports `--plan-root`, `--path`, `--no-ancestors`, and `--json` flags. Auto-detects plan root from cwd when `--plan-root` is omitted. Ancestor chain uses hierarchical `#`/`##`/`###` headers with first-section excerpts (10-line cap). Full task frontmatter rendered as human-readable key-value pairs. Sibling dependencies listed with effective status. JSON mode emits `ancestors`, `task`, and `dependencies` keys. All 53 existing tests pass.
