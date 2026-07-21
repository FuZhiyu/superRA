---
name: task-tree
description: Operate on superRA/ task trees. Use to query frontier, DAG, or tree views; create or restructure tasks; edit statuses; serve dashboards; or migrate legacy PLAN.md/RESULTS.md.
user-invocable: true
---

# Task Tree

## Core Concepts

- Every subdirectory under `./superRA` with a `task.md` file is a **task**. A leaf task is a directory with `task.md` but no subdirectories containing `task.md`.
- The **filesystem hierarchy is the task hierarchy**. `walk_plan()` discovers children by scanning subdirectories.
- **Dependencies are sibling-only.** `depends_on` values are sibling directory names within the same parent.
- **Parent task status rolls up** from children automatically — a parent is `approved` only when all active (non-parked) children are `approved`; `archived` and `postponed` children are excluded from the rollup computation.
- **DAG-derived ordering vs. display order.** The dependency DAG controls execution order. Numeric prefixes on directory names (e.g. `01-load`, `02-merge`) control display order only — these are independent.

## CLI Setup

In a fresh project, bootstrap the wrapper with the loaded skill directory (`<skill-dir>` = the directory containing this `SKILL.md`; substitute the real path), then use the wrapper for everything after:

```bash
uv run --script <skill-dir>/scripts/cli.py wrapper init   # writes superRA/superra (planner/main bootstrap)
./superRA/superra wrapper init                             # refresh an existing wrapper; idempotent
```

## Reading the Tree

Run the committed `./superRA/superra` wrapper (created above; contributors in the superRA checkout substitute `uv run --script skills/task-tree/scripts/cli.py`). Every `superra …` example below and in the references denotes this wrapper:

```bash
./superRA/superra task tree            # tree with status badges
./superRA/superra task frontier        # dispatchable leaf tasks
./superRA/superra task dag 01-data     # dependency DAG for a subtree (Mermaid)
./superRA/superra task tree --json     # JSON output
./superRA/superra dashboard --no-open  # idempotent; starts or reuses a server and prints this worktree's scoped URL
```

**Deep-linking a task in the dashboard:** append `#/<task-path>` to the scoped URL emitted by `dashboard --no-open`. `<task-path>` is the same locator as `task read` (no `superRA/` prefix, empty for the tree root). Use the emitted URL as-is because its URL-encoded `?wt=` selector handles worktree-name collisions.

## Task File Format

```yaml
---
title: "Merge with Fund Characteristics"
status: not-started
depends_on:
  - 01-load-raw-data
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

Field-by-field anatomy and body-section ownership live in `references/task-file-contract.md` §Task Anatomy.

## Routing — operate on the tree

| To do X | See |
|---|---|
| Create / rename / link / move tasks; bulk status propagation; append results programmatically | `references/commands.md` |
| Read or resolve task comments (the read/resolve loop; comments also surface via `superra task read`) | `references/commands.md §Comments` |
| Validate tree structure, fix status inconsistencies, diagnose orphaned `depends_on` entries | `references/commands.md §Diagnostics` |
| Task-file anatomy, fields, status/dependencies, inherited context, results shape, stale-content, figure embedding | `references/task-file-contract.md` |
| Objective writing, task splitting, placement, durable homes, update-task lifecycle, retroactive task-tree creation | `../superplan/references/task-tree-design.md` |
| Migrate legacy `PLAN.md` + `RESULTS.md`, or upgrade `superRA/` v1 → v2 | `references/internals.md §Migration` |
| Dashboard server mechanics (idempotent ensure-running, task URLs, artifact export) | `references/internals.md §Dashboard` |
| Modify the skill itself (data layer, hooks, scripts) | `references/internals.md`; hook coverage details live in `§Hook Architecture` |

Intentional task path changes go through `superra task move` (or `task rename` for same-parent compatibility), not raw `mv` / `git mv`. It resolves the move's fallout for you — relative Markdown links across the tree and sibling-only `depends_on` edges — so run the move directly; do not rewrite links or rewire dependencies by hand first. Mechanics and the cross-parent dependency rules are in `references/commands.md §Move / rename a task`.
