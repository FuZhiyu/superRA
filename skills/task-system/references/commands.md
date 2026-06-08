# Task-Tree Command Surface

Load this reference when you are an orchestrator or planner mutating a `superRA/` tree — scaffolding new tasks, restructuring, re-wiring dependencies, or running bulk status operations.

All commands below run through the committed `./superRA/superra` wrapper. Bare `superra …` in the examples denotes that wrapper.

**Single-field edits go through direct edit, not these CLIs.** To set one field on one task — including `status` — edit its `task.md` directly with Read/Edit (see `using-superRA/SKILL.md §Task Interface`); the PostToolUse hook validates and propagates. The commands below are convenience scaffolding for creating tasks from a template and for bulk or scripted changes — reach for them when direct edit would be tedious or error-prone.

## Scaffold a new task

Creates the directory, fills the template with current dates, and sets frontmatter defaults (`status: not-started`):

```bash
superra task create 01-data/03-filter \
  --title "Filter Sample" \
  --objective "Apply standard filters: drop obs before 2000, require non-missing returns." \
  --guidance "Consider reusing Code/common_filters.py." \
  --depends-on 02-merge
```

`--guidance` is optional and seeds an advisory `## Planner Guidance` section.

## Bulk status operations

```bash
superra task status propagate
superra task status cascade 01-data --status approved
```

## Append a result programmatically

```bash
superra task result add 01-data/01-load \
  --finding "Loaded 4.7M rows across 12K funds"
```

## Manage dependencies

Also fixes a dangling `depends_on` after a manual move:

```bash
superra task dep add 01-data/03-filter 02-merge

superra task dep remove 01-data/03-filter 02-merge
```

## Rename / move a task

`superra task rename` is an atomic same-parent rename that cascades sibling `depends_on`:

```bash
superra task rename 01-data/01-load 01-data/01-load-raw
```

A plain `mv` of the task directory also works — it carries the `task.md`, `comments.yaml`, and whole subtree, and the PostToolUse hook revalidates and propagates status. For a **same-parent rename** (`mv superRA/a/x superRA/a/y`) the hook also auto-cascades sibling `depends_on: x` → `y` (surfaced in the hook feedback), so it needs no follow-up; `superra task rename` is just the explicit convenience for this case. A **cross-parent move** or a **delete** of a depended-on task is not auto-cascaded — both strand the reference, which validation flags as a dangling dependency to re-wire with `superra task dep add` / `dep remove` or a direct edit. Why the boundary stops at same-parent renames: `internals.md §Hook Architecture`.

## Comments

A researcher pins comments to `task.md` blocks via the dashboard. `superra task read <path>` already shows unresolved comments with their anchored blocks (see `using-superRA/SKILL.md §Task Interface`), so use these commands only for the standalone read/resolve loop:

```bash
superra task comment list <task>           # unresolved comments on a task, each with its full anchored block
superra task comment list <task> --all     # include resolved comments
superra task comment tree                  # unresolved-comment counts across the whole tree
superra task comment resolve <task> <id>   # toggle a comment's resolved state
```

A comment is **unresolved** until toggled; `resolve` flips it (and back). Comments whose anchored block was edited or moved away render `[ORPHANED]` with the stored preview instead of a live block. Add `--json` to `list` / `tree` for scripted consumption.
