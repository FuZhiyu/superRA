# Task-Tree Command Surface

Load this reference when you are an orchestrator or planner mutating a `superRA/` tree — scaffolding new tasks, restructuring, re-wiring dependencies, or running bulk status operations.

All commands below run through the committed `./superRA/superra` wrapper. Bare `superra …` in the examples denotes that wrapper.

**Single-field edits go through direct edit, not these CLIs.** To set one field on one task — including `status` — edit its `task.md` directly with Read/Edit (see `using-superra/SKILL.md §Task Interface`); the PostToolUse hook validates and propagates. The commands below are convenience scaffolding for creating tasks from a template and for bulk or scripted changes — reach for them when direct edit would be tedious or error-prone.

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
superra task status fix
```

`status propagate` — walks the tree and flips stale branch statuses to match their computed rollup. `status cascade` — sets all descendant leaves to the given status (allowed values: `approved`, `not-started`, `archived`, `postponed`). `status fix` — rewrites branch task frontmatter `status` fields in place to match `compute_status()` from their children, fixing any stored-vs-computed mismatches without touching leaf tasks.

## Append a result programmatically

```bash
superra task result add 01-data/01-load \
  --finding "Loaded 4.7M rows across 12K funds"
```

## Manage dependencies

Use this for explicit dependency edits:

```bash
superra task dep add 01-data/03-filter 02-merge

superra task dep remove 01-data/03-filter 02-merge
```

## Move / rename a task

Intentional task path changes use the task-tree CLI, not raw `mv` / `git mv`:

```bash
superra task move 01-data/01-load 01-data/01-load-raw
superra task move 01-data/03-filter 02-analysis/01-filtered-sample
```

`superra task rename FROM TO` remains as a compatibility alias for same-parent renames.

The move command carries the whole task directory — `task.md`, `comments.yaml`, attachments, and descendants — and resolves relative paths and `depends_on` edges itself. Run the move directly; do not rewrite links or rewire dependencies by hand first.

It rewrites every relative Markdown link that the move would otherwise break: links inside the moved files, and links anywhere else in the task tree that point into the moved subtree, all re-pointed to the new location.

`depends_on` is sibling-only, so a cross-parent move cannot carry an edge that crosses the move. A same-parent rename cascades sibling `depends_on: old-slug` to `new-slug`. A cross-parent move drops each edge that no longer resolves under the new parent — an old sibling's edge to the moved slug, or the moved task's edge to a slug absent from the destination — and prints a warning per drop. If a dropped edge should still hold in the new location, re-add it afterward with `superra task dep add`.

The PostToolUse hook still revalidates raw filesystem moves and preserves the old same-parent auto-cascade guardrail, but it is not the canonical move mechanism. Use raw `mv` / `git mv` only for recovery from tool failure, then run `superra task check`.

## Diagnostics

`superra task check` is the tree's validation entry point. Run it after any bulk operation or raw filesystem change to audit status validity, dependency integrity, and cycle-free ordering:

```bash
superra task check                    # validate full tree; prints findings grouped by task
superra task check --category status  # limit to one category: status, dependency, rollup, sync-impact
superra task status fix               # repair branch status fields to match child rollups
superra task status propagate         # re-run parent status rollup after bulk edits
```

Findings are prefixed `[ERROR]` (blocking; tree is inconsistent), `[WARNING]` (advisory), or `[INFO]` (informational). After recovering from a raw `mv` / `git mv`, run `superra task check` before the next agent dispatch.

## Comments

A researcher pins comments to `task.md` blocks via the dashboard. `superra task read <path>` already shows unresolved comments with their anchored blocks (see `using-superra/SKILL.md §Task Interface`), so use these commands only for the standalone read/resolve loop:

```bash
superra task comment list <task>           # unresolved comments on a task, each with its full anchored block
superra task comment list <task> --all     # include resolved comments
superra task comment tree                  # unresolved-comment counts across the whole tree
superra task comment resolve <task> <id>   # toggle a comment's resolved state
```

A comment is **unresolved** until toggled; `resolve` flips it (and back). Comments whose anchored block was edited or moved away render `[ORPHANED]` with the stored preview instead of a live block. Add `--json` to `list` / `tree` for scripted consumption.
