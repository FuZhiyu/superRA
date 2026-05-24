---
name: task-system
description: >
  Directory-tree task system — filesystem hierarchy as task hierarchy.
  Use when creating, querying, or visualizing a .plan/ task tree; when
  migrating from PLAN.md + RESULTS.md to the tree format; or when
  generating an HTML dashboard. Triggers include "create a task tree",
  "show the frontier", "generate the dashboard", "migrate the plan",
  "what tasks are ready", "show the task DAG".
user-invocable: true
---

# Task System

A directory-tree task system where the filesystem hierarchy is the task hierarchy. Each task is a self-contained `task.md` file with planner-owned and implementer-owned sections, and a generated HTML dashboard provides visualization with tree, DAG, and kanban views.

## Core Concepts

- Everything is a **task**. A leaf task is a directory with `task.md` but no subdirectories containing `task.md`.
- **`## Objective`** is planner-owned: the goal, methodology, and conventions for this task. One flat section, no subsections.
- **`## Results`** is implementer-owned: key findings, notes. Present at every level — branch tasks summarize their children's results at a higher level of abstraction.
- The **filesystem hierarchy is the task hierarchy**. `walk_plan()` discovers children by scanning subdirectories.
- **Numeric prefix** on directory names (`01-load`, `02-merge`) controls display order. The DAG via `depends_on` controls execution order. These are independent.
- **Dependencies are sibling-only.** `depends_on` values are sibling directory names within the same parent.
- **Parent task status rolls up** from children automatically — a parent is `approved` only when all children are `approved`.

## Directory Structure

```
.plan/
  task.md                    # root task (project objective, methodology, conventions)
  dashboard.html             # generated HTML visualization
  01-data-preparation/
    task.md                  # branch task (has subtasks)
    01-load-raw-data/
      task.md                # leaf task (no subdirectories)
      attachments/
    02-merge/
      task.md
  02-estimation/
    task.md
```

## Command Surface

All scripts are in `<skill-dir>/scripts/`. `<skill-dir>` is the directory containing this `SKILL.md`.

### Create a task

```bash
python3 <skill-dir>/scripts/task_create.py \
  --plan-root .plan --path 01-data/03-filter \
  --title "Filter Sample" \
  --objective "Apply standard filters: drop obs before 2000, require non-missing returns." \
  --depends-on 02-merge
```

### Update task status

```bash
python3 <skill-dir>/scripts/task_update.py \
  --plan-root .plan --path 01-data/03-filter \
  --status approved --review-status approved
```

### Query the task tree

```bash
# Print tree with status badges
python3 <skill-dir>/scripts/task_query.py --plan-root .plan --tree

# List dispatchable leaf tasks (the frontier)
python3 <skill-dir>/scripts/task_query.py --plan-root .plan --frontier

# Render dependency DAG for a subtree (Mermaid format)
python3 <skill-dir>/scripts/task_query.py --plan-root .plan --dag 01-data

# JSON output
python3 <skill-dir>/scripts/task_query.py --plan-root .plan --tree --json
```

### Add results to a task

```bash
python3 <skill-dir>/scripts/task_add_result.py \
  --plan-root .plan --path 01-data/01-load \
  --finding "Loaded 4.7M rows across 12K funds"
```

### Manage dependencies

```bash
python3 <skill-dir>/scripts/task_link.py \
  --plan-root .plan --path 01-data/03-filter --depends-on 02-merge

python3 <skill-dir>/scripts/task_link.py \
  --plan-root .plan --path 01-data/03-filter --depends-on 02-merge --remove
```

### Rename a task (cascades to sibling depends_on)

```bash
python3 <skill-dir>/scripts/task_rename.py \
  --plan-root .plan --from 01-data/01-load --to 01-data/01-load-raw
```

### Migrate from PLAN.md + RESULTS.md

```bash
python3 <skill-dir>/scripts/plan_migrate.py \
  --plan-md PLAN.md --results-md RESULTS.md --output .plan
```

### Upgrade existing .plan/ from v1 to v2 format

```bash
python3 <skill-dir>/scripts/plan_migrate.py --upgrade --plan-root .plan
```

Converts `## Steps` (checkboxes) to `## Objective` (prose), removes redundant `# Title` headings. Idempotent.

### Generate HTML dashboard

```bash
python3 <skill-dir>/scripts/plan_dashboard.py --plan-root .plan
# Writes .plan/dashboard.html — single-file, opens locally (requires internet for full rendering)
```

The dashboard is automatically regenerated after every mutation command (`task_create`, `task_update`, `task_add_result`, `task_link`, `task_rename`). Manual generation is only needed for the initial dashboard or after `plan_migrate`.

## Task File Format

```yaml
---
title: "Merge with Fund Characteristics"
status: not-started           # not-started | in-progress | implemented | revise | approved
review_status: ~              # ~ | implemented | revise | approved
integration_status: ~         # ~ | implemented | revise | approved
depends_on:                   # sibling directory names only
  - 01-load-raw-data
tags: [data-merge]            # both inline [x] and multi-line list forms are accepted
script: Code/03_merge_chars.py
input: [Data/holdings.parquet]
output: [Data/merged.parquet]
created: 2026-05-24
updated: 2026-05-24
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
