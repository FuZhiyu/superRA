# Task-Tree Command Surface

Load this reference when you are an orchestrator or planner mutating a `superRA/` tree — scaffolding new tasks, restructuring, re-wiring dependencies, or running bulk status operations.

All commands below use the packaged `superra` CLI. The `--root` flag is optional — auto-detected from the current working directory.

**Single-field edits go through direct edit, not these CLIs.** To set one field on one task — including `status` — edit its `task.md` directly with Read/Edit (see `using-superRA/SKILL.md §Task Interface`); the PostToolUse hook validates and propagates. The commands below are convenience scaffolding for creating tasks from a template and for bulk or scripted changes — reach for them when direct edit would be tedious or error-prone.

## Scaffold a new task

Creates the directory, fills the template with current dates, and sets frontmatter defaults (`status: not-started`):

```bash
superra task create 01-data/03-filter \
  --root superRA \
  --title "Filter Sample" \
  --objective "Apply standard filters: drop obs before 2000, require non-missing returns." \
  --guidance "Consider reusing Code/common_filters.py." \
  --depends-on 02-merge
```

`--guidance` is optional and seeds an advisory `## Planner Guidance` section.

## Bulk status operations

```bash
superra task status propagate --root superRA
superra task status cascade 01-data --root superRA --status approved
```

## Append a result programmatically

```bash
superra task result add 01-data/01-load \
  --root superRA \
  --finding "Loaded 4.7M rows across 12K funds"
```

## Manage dependencies

Also fixes a dangling `depends_on` after a manual move:

```bash
superra task dep add 01-data/03-filter 02-merge --root superRA

superra task dep remove 01-data/03-filter 02-merge --root superRA
```

## Rename / move a task

`superra task rename` is an atomic same-parent rename that cascades sibling `depends_on`:

```bash
superra task rename 01-data/01-load 01-data/01-load-raw --root superRA
```

A plain `mv` of the task directory also works — it carries the `task.md`, `comments.yaml`, and whole subtree, and the PostToolUse hook revalidates the tree, propagates status, and rebuilds the dashboard. One caveat: `depends_on` references sibling slugs, so a move that crosses a dependency boundary strands the reference — validation flags the now-dangling dependency and you re-wire it with `superra task dep add` / `superra task dep remove` or a direct edit (the hook does not auto-cascade). `superra task rename` is no longer required to keep the tree consistent after a manual move; it is the convenience for the atomic same-parent case.
