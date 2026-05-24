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

A directory-tree task system where the filesystem hierarchy is the task hierarchy. Each task is a self-contained `task.md` file with YAML frontmatter and free-form body sections. A generated HTML dashboard provides tree, DAG, and kanban views.

**Role-scoped references:**
- Planners and orchestrators: load `references/planning.md` for objective writing, task splitting, hierarchy management, and retroactive plan creation.
- Contributors modifying the task-system skill itself: load `references/internals.md` for data layer, hook architecture, and migration details.

## Core Concepts

- Everything is a **task**. A leaf task is a directory with `task.md` but no subdirectories containing `task.md`.
- The **filesystem hierarchy is the task hierarchy**. `walk_plan()` discovers children by scanning subdirectories.
- **Dependencies are sibling-only.** `depends_on` values are sibling directory names within the same parent.
- **Parent task status rolls up** from children automatically — a parent is `approved` only when all children are `approved`.
- **DAG-derived ordering.** The dependency DAG controls execution order. Numeric prefixes on directory names (e.g. `01-load`, `02-merge`) control display order only — these are independent.

## How to Read a Task

Use `task_read.py` to read a task with its full ancestor context injected:

```bash
# Read a task with ancestor chain and dependency status
python3 <skill-dir>/scripts/task_read.py --path task-system/agent-interface/skill-restructure

# Without ancestor context (just the task itself)
python3 <skill-dir>/scripts/task_read.py --path task-system/agent-interface/skill-restructure --no-ancestors

# Structured JSON output
python3 <skill-dir>/scripts/task_read.py --path 01-data/03-filter --json
```

The `--plan-root` flag is optional — auto-detected from the current working directory.

Or read `task.md` directly with the Read tool — the file is self-contained. To understand a task in context, read its ancestor `task.md` files up to the root `.plan/task.md`.

Use `task_query.py` for tree-level views:

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

## How to Edit a Task

Edit `task.md` directly with Read/Edit tools. The file has two parts:

1. **Frontmatter** (YAML between `---` delimiters) — structured metadata
2. **Body** (everything after the closing `---`) — free-form markdown sections

### Frontmatter fields

| Field | Type | Values | Owner |
|---|---|---|---|
| `title` | string | descriptive name | planner |
| `status` | enum | `not-started` \| `in-progress` \| `implemented` \| `revise` \| `approved` | implementer |
| `review_status` | enum | `~` \| `implemented` \| `revise` \| `approved` | reviewer |
| `integration_status` | enum | `~` \| `implemented` \| `revise` \| `approved` | reviewer |
| `depends_on` | list | sibling directory names | planner |
| `tags` | list | free-form | planner |
| `script` | string | path to primary script | planner |
| `input` | list | input file paths | planner |
| `output` | list | output file paths | planner |
| `created` | date | ISO 8601 | auto |
| `updated` | date | ISO 8601 | auto |

### Body sections

Any `## Heading` is valid. Recommended defaults:

| Section | Purpose | Owner |
|---|---|---|
| `## Objective` | What success looks like — the goal, constraints, and validation criteria | planner |
| `## Results` | Key findings and notes | implementer |
| `## Decisions` | User decisions that shaped the work | implementer |
| `## Review Notes` | Reviewer feedback | reviewer |

## Ownership Model

You own the **body sections** of your assigned task (`## Results`, `## Decisions`, and status/review_status frontmatter). You do not own:

- **Other tasks' content** — steps, status, review notes, results.
- **Scope-defining frontmatter** — `title`, `depends_on`, `script`, `input`, `output`. These are planner-owned.
- **The `## Objective` section** — planner-owned; read it, do not rewrite it.

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

## Command Surface

All scripts are in `<skill-dir>/scripts/`. `<skill-dir>` is the directory containing this `SKILL.md`.

### Query the task tree

```bash
python3 <skill-dir>/scripts/task_query.py --plan-root .plan --tree
python3 <skill-dir>/scripts/task_query.py --plan-root .plan --frontier
python3 <skill-dir>/scripts/task_query.py --plan-root .plan --dag 01-data
```

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

### Rename a task

```bash
python3 <skill-dir>/scripts/task_rename.py \
  --plan-root .plan --from 01-data/01-load --to 01-data/01-load-raw
```

### Generate HTML dashboard

```bash
python3 <skill-dir>/scripts/plan_dashboard.py --plan-root .plan
# Writes .plan/dashboard.html
```

The dashboard is automatically regenerated after every mutation command (`task_create`, `task_update`, `task_add_result`, `task_link`, `task_rename`).

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
