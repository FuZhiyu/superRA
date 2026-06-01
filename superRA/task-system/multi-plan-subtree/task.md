---
title: "Multi-plan support and subtree-scoped dashboard"
status: not-started
depends_on:
  - core-data-layer
  - dashboard
tags: []
created: 2026-05-24
---

## Objective

Treat depth-1 children of `.plan/` as independent "plans" and add subtree-scoped display to the dashboard. Drop the root `task.md` as a requirement.

### Data layer changes

- `walk_plan()` returns a forest (list of trees) when no root `task.md` exists, or treats root as a silent container when it does. Backward-compatible: an existing root `task.md` still works, it just isn't required.
- Remove root-level status rollup — aggregating unrelated plans is misleading. Per-plan rollup stays.
- Project-level metadata (name, notes) comes from a lightweight source (directory name or optional `.plan/config.md`) rather than root `task.md` frontmatter.

### Dashboard changes

- Add a **focus/zoom** mechanism: clicking a branch node scopes all three views (tree, DAG, kanban) to that subtree. A breadcrumb trail lets the user zoom back out.
- When no subtree is focused, show a plan-selector view listing depth-1 children with per-plan progress.
- **DAG fix:** current `renderDag()` flattens the whole tree and uses bare `depends_on` slugs as edge sources but full paths as node IDs, so cross-level edges don't connect. Fix: scope DAG to the focused subtree's immediate children (matching what the CLI `--dag SUBTREE` already does correctly).
- Kanban and summary bar scope to the focused plan when one is selected.

### CLI changes

- `task_query.py --tree` and `--frontier` gain an optional `--subtree PATH` filter (analogous to existing `--dag SUBTREE`).
- Summary/progress output scoped to the selected subtree when `--subtree` is provided.
