---
title: "CLI Commands"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

The `superra` CLI is the shell interface for reading and operating on your task tree.
This page covers the commands a researcher reaches for day-to-day.
The full mutation command surface — scaffolding, renaming, dependency wiring, bulk status operations, and diagnostics — lives in [skills/task-tree/references/commands.md](skills/task-tree/references/commands.md).

## Reading the tree

```bash
./superRA/superra task tree             # tree with status badges
./superRA/superra task frontier         # dispatchable leaf tasks ready to work on
./superRA/superra task dag 01-data      # dependency DAG for a subtree (Mermaid output)
./superRA/superra task read 01-data/02-merge  # a single task with its full inherited context
```

`task read` is the recommended way to hand context to an agent: it injects the ancestor chain, sibling dependency statuses, and any unresolved comments pinned to the task.

## The dashboard

```bash
./superRA/superra dashboard             # open the live tree/DAG/kanban dashboard (background)
./superRA/superra dashboard stop        # shut the server down
```

The dashboard launches in the background and reuses an already-running server.
See [How-to: See Your Work](#/04-how-to/04-see-your-work) for a guided walkthrough.

## Scaffolding a new task

```bash
./superRA/superra task create 01-data/03-filter \
  --title "Filter Sample" \
  --objective "Apply standard filters: drop obs before 2000, require non-missing returns." \
  --depends-on 02-merge
```

## Moving and renaming

```bash
./superRA/superra task move 01-data/01-load 01-data/01-load-raw
./superRA/superra task move 01-data/03-filter 02-analysis/01-filtered-sample
```

Use `task move` rather than raw `mv`; the CLI carries markdown links and sibling `depends_on` edges through the rename.

## Comments

```bash
./superRA/superra task comment list 01-data/02-merge      # unresolved comments
./superRA/superra task comment resolve 01-data/02-merge 3 # toggle resolved state
```

Comments are also shown inline when you run `task read`.

## Diagnostics

```bash
./superRA/superra task check                  # audit status, dependency integrity, cycles
./superRA/superra task check --fix-status     # auto-fix legacy status values
./superRA/superra task check --propagate-all  # re-run parent status rollup
```

Run `task check` after any bulk operation or raw filesystem change.

For the complete command surface including bulk status operations and result-append commands, see [skills/task-tree/references/commands.md](skills/task-tree/references/commands.md).
