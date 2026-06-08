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
superra task tree

# List dispatchable leaf tasks (the frontier)
superra task frontier

# Render dependency DAG for a subtree (Mermaid format)
superra task dag 01-data

# JSON output
superra task tree --json
```

The `superra` command resolves the task-system package from the installed plugin at runtime via `uvx` — it installs nothing and never creates a venv in your project. A task tree carries a generated `superra` wrapper (`./superRA/superra task tree`); create or refresh it with `superra wrapper init`. Never run bare `uv run superra` from a research project: `uv` would try to provision that project's environment, which is wrong and can fail.

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
| Read or resolve task comments (the read/resolve loop; comments also surface via `superra task read`) | `references/commands.md §Comments` |
| Objective writing, task splitting, placement, results shape, stale-content, retroactive plans | `references/planning.md` |
| Migrate legacy `PLAN.md` + `RESULTS.md`, or upgrade `superRA/` v1 → v2 | `references/internals.md §Migration` |
| View the dashboard | `superra dashboard` runs the server in the background and returns (reuses a running one; `--foreground` to block in this terminal; `superra dashboard stop` to stop it). Local checkout: `uv run --project skills/task-system superra dashboard`; mechanics in `references/internals.md §Dashboard` |
| Modify the skill itself (data layer, hooks, scripts) | `references/internals.md`; hook coverage details live in `§Hook Architecture` |

A plain `mv` of a task directory carries the whole subtree. A **same-parent rename** auto-cascades sibling `depends_on` (the hook re-points dependents — expect this silent edit, surfaced in its feedback); a **cross-parent move** or a **delete** of a depended-on task strands the reference instead, which validation flags for re-wiring. See `references/commands.md` for the full mutation surface.
<!-- no need to route back to using superra -->
