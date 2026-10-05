---
title: "The CLI"
status: not-started
depends_on:  []
---

## Objective

The agent runs these commands for you; run them yourself through `./superRA/superra` to inspect the tree, scaffold a few tasks, or repair it after a messy edit.

## Inspect the tree

```bash
./superRA/superra task tree                      # the whole tree with status badges
./superRA/superra task frontier                  # ready tasks, each with inputs whose producer is stale, missing, or failed
./superRA/superra task dag 01-data               # dependency DAG of a subtree, as Mermaid
./superRA/superra task read 01-data/02-merge     # one task as an agent sees it on arrival
```

`task read` prints the task with its ancestors' objectives, its prerequisites, its out-of-date inputs, and unresolved comments.

## Create and move tasks

```bash
./superRA/superra task create 01-data/03-filter \
  --title "Filter Sample" \
  --objective "Drop obs before 2000, require non-missing returns." \
  --depends-on 01-sample-design

./superRA/superra task move 01-data/03-filter 02-analysis/01-filtered-sample
```

Use `task move` rather than `mv` to move or rename a task: it repairs links and refuses a move that would create a dependency error. Moving to a new parent drops `depends_on` edges that no longer resolve, with a warning; re-add any that should still hold with `task dep add`.

## Read and resolve comments

```bash
./superRA/superra task comment list 01-data/02-merge        # unresolved comments
./superRA/superra task comment resolve 01-data/02-merge 3   # toggle resolved state
```

## Repair after bulk edits

```bash
./superRA/superra task check       # audit statuses, dependencies, and cycles
./superRA/superra task status fix  # reset parent statuses to match their children
```

## Elsewhere

- `repro` commands, which rebuild and inspect results: the [reproducibility page](#/04-utility-skills/09-reproducibility).
- `dashboard` commands: the [dashboard page](#/04-utility-skills/01-task-tree/04-dashboard).
- Every flag and bulk status operation: [commands.md](skills/task-tree/references/commands.md). Migrating a legacy `PLAN.md`: [internals.md §Migration](skills/task-tree/references/internals.md).
