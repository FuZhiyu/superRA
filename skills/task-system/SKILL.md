---
name: task-system
description: >
  Directory-tree task system for managing plans as filesystem hierarchies.
  Use when creating, querying, or visualizing a .plan/ task tree; when
  migrating from PLAN.md + RESULTS.md to the tree format; or when
  generating an HTML dashboard. Triggers include "create a task tree",
  "show the frontier", "generate the dashboard", "migrate the plan",
  "what tasks are ready", "show the task DAG".
user-invocable: true
---

# Task System

A directory-tree task system where the filesystem hierarchy is the task hierarchy. Each task is a self-contained `task.md` file (plan + results unified), and a generated HTML dashboard provides visualization with tree, DAG, and kanban views.

## Core Concepts

### Tasks are objectives. Steps are procedures.

- A **task** (`task.md`) states an objective — *what* to achieve. It has its own review cycle, status, dependencies, and results. It maps to an agent dispatch boundary.
- A **step** (checkbox inside a task) states a procedure — *how* to achieve the objective. It's an atomic action within a single script, reviewed together with the task.

**When to nest:** Decompose into subtasks when the objective breaks into sub-objectives (each independently reviewable). Decompose into steps when it breaks into procedures. Only **leaf tasks** have steps. Branch tasks (with subdirectories) have no steps — their subtask tree is the decomposition.

**Ownership:** The orchestrator owns the task tree (objectives, dependencies). For leaf tasks, the orchestrator may write initial steps as guidance, but the **implementer owns the steps** and may deviate. The reviewer evaluates whether the objective was achieved.

### Dependencies are siblings-only

`depends_on` values are sibling directory names within the same parent. A parent task's status rolls up from its children — it is `approved` only when all children are `approved`. Cross-branch dependencies are expressed at the parent level.

## Directory Structure

```
.plan/
  task.md                    # root task (project objective, methodology, conventions)
  dashboard.html             # generated HTML visualization
  01-data-preparation/
    task.md                  # branch task (no steps, has subtasks)
    01-load-raw-data/
      task.md                # leaf task (has steps, no subdirectories)
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
  --title "Filter Sample" --depends-on 02-merge
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

### Generate HTML dashboard

```bash
python3 <skill-dir>/scripts/plan_dashboard.py --plan-root .plan
# Opens .plan/dashboard.html — self-contained, works offline
```

## Task File Format

```yaml
---
title: "Merge with Fund Characteristics"
status: not-started           # not-started | in-progress | implemented | revise | approved
review_status: ~              # ~ | implemented | revise | approved
integration_status: ~         # ~ | implemented | revise | approved
depends_on:                   # sibling directory names only
  - 01-load-raw-data
tags: [data-merge]
script: Code/03_merge_chars.py
input: [Data/holdings.parquet]
output: [Data/merged.parquet]
created: 2026-05-24
updated: 2026-05-24
---

# Merge with Fund Characteristics

## Steps
- [ ] Step 1: Describe inputs
- [ ] Step 2: Left join
- [ ] Step 3: Validate

## Results
### Key Findings
- (populated during execution)

## Decisions
> (task-scoped user decisions)

## Review Notes
> (present only during active REVISE rounds, removed on APPROVED)
```
