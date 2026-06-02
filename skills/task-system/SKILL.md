---
name: task-system
description: >
  Directory-tree task tooling — operate on a superRA/ task tree: query the
  frontier/DAG/tree, create and restructure tasks, run bulk status ops,
  serve the dashboard, or migrate legacy PLAN.md + RESULTS.md. Load on
  demand by orchestrators, planners, and contributors. Triggers include
  "show the frontier", "show the task DAG", "create a task tree",
  "generate the dashboard", "migrate the plan".
user-invocable: true
---

# Task System

## Core Concepts

The mental model for reasoning about the tree:

- Everything is a **task**. A leaf task is a directory with `task.md` but no subdirectories containing `task.md`.
- The **filesystem hierarchy is the task hierarchy**. `walk_plan()` discovers children by scanning subdirectories.
- **Dependencies are sibling-only.** `depends_on` values are sibling directory names within the same parent.
- **Parent task status rolls up** from children automatically — a parent is `approved` only when all children are `approved`.
- **DAG-derived ordering vs. display order.** The dependency DAG controls execution order. Numeric prefixes on directory names (e.g. `01-load`, `02-merge`) control display order only — these are independent.

## Reading the Tree

The common on-demand path is inspecting tree state. Use `superra task`:

```bash
# Print tree with status badges
superra task tree --root superRA

# List dispatchable leaf tasks (the frontier)
superra task frontier --root superRA

# Render dependency DAG for a subtree (Mermaid format)
superra task dag 01-data --root superRA

# JSON output
superra task tree --root superRA --json
```

The `--root` flag is optional — auto-detected from the current working directory.

## Task File Format

```yaml
---
title: "Merge with Fund Characteristics"
status: not-started
depends_on:
  - 01-load-raw-data
tags: [data-merge]            # both inline [x] and multi-line list forms are accepted
script: Code/03_merge_chars.py
input: [Data/holdings.parquet]
output: [Data/merged.parquet]
created: 2026-05-24
---

## Objective

Left join holdings with fund characteristics on fund_id x date.
Use CRSP-style merge conventions. Validate row counts post-merge.

## Results

### Key Findings
- Merge preserved all 4.7M rows

### Notes
- Used fuzzy date matching for quarterly vs monthly frequency mismatch

## Review Notes
> [MAJOR] Inner join used instead of left join
```

Field-by-field anatomy and body-section ownership live in `references/planning.md §Field-by-Field Notes`.

## Routing — operate on the tree

| To do X | See |
|---|---|
| Create / rename / link / move tasks; bulk status propagation; append results programmatically | `references/commands.md` |
| Objective writing, task splitting, placement, results shape, stale-content, retroactive plans | `references/planning.md` |
| Migrate legacy `PLAN.md` + `RESULTS.md`, or upgrade `superRA/` v1 → v2 | `references/internals.md §Migration` |
| View the dashboard | `superra dashboard --root superRA` (local checkout: `uv run --project skills/task-system superra dashboard --root superRA`); mechanics in `references/internals.md §Dashboard` |
| Modify the skill itself (data layer, hooks, scripts) | `references/internals.md`; hook coverage details live in `§Hook Architecture` |

A plain `mv` of a task directory carries the whole subtree; a move that crosses a dependency boundary strands a sibling `depends_on` reference, which validation flags for re-wiring. See `references/commands.md` for the full mutation surface.
<!-- no need to route back to using superra -->
