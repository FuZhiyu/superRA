# Task-Tree Command Surface

Load when mutating a `superRA/` tree — scaffolding tasks, restructuring, re-wiring dependencies, bulk status operations.

Bare `superra …` below denotes the committed `./superRA/superra` wrapper.

**Single-field edits go through direct edit, not these CLIs.** One field on one task — including `status` — edit its `task.md` with Read/Edit (`using-superra/SKILL.md §Task Interface`); the PostToolUse hook validates and propagates. Reach for the commands below when direct edit would be tedious or error-prone: template scaffolding, bulk or scripted changes.

## Scaffold a new task

Creates the directory, fills the template with current dates, sets frontmatter defaults (`status: not-started`):

```bash
superra task create 01-data/03-filter \
  --title "Filter Sample" \
  --objective "Apply standard filters: drop obs before 2000, require non-missing returns." \
  --guidance "Consider reusing Code/common_filters.py." \
  --depends-on 02-merge
```

`--details` is optional — seeds a `## Details` section. `--guidance` is a working alias.

## Bulk status operations

```bash
superra task status propagate
superra task status cascade 01-data --status approved
superra task status fix
```

- `status propagate` — flips stale branch statuses to their computed rollup.
- `status cascade` — sets all descendant leaves to the given status (`approved`, `not-started`, `archived`, `postponed`).
- `status fix` — rewrites branch frontmatter `status` in place to match `compute_status()` from children, leaving leaves untouched.

## Append a result programmatically

```bash
superra task result add 01-data/01-load \
  --finding "Loaded 4.7M rows across 12K funds"
```

## Manage dependencies

Explicit dependency edits:

```bash
superra task dep add 01-data/03-filter 02-merge

superra task dep remove 01-data/03-filter 02-merge
```

## Move / rename a task

Intentional path changes use the CLI, not raw `mv` / `git mv`:

```bash
superra task move 01-data/01-load 01-data/01-load-raw
superra task move 01-data/03-filter 02-analysis/01-filtered-sample
```

`superra task rename FROM TO` is a compatibility alias for same-parent renames.

`move` carries the whole task directory — `task.md`, `comments.yaml`, attachments, descendants — and resolves relative paths and `depends_on` edges itself. Run it directly rather than rewriting links or rewiring dependencies by hand first.

It re-points every relative Markdown link the move would break: links inside the moved files, and links anywhere else in the tree pointing into the moved subtree.

`depends_on` is sibling-only, so no edge crossing the move survives. Same-parent rename: sibling `depends_on: old-slug` cascades to `new-slug`. Cross-parent move: each edge that no longer resolves under the new parent is dropped with a warning — an old sibling's edge to the moved slug, or the moved task's edge to a slug absent from the destination. Re-add a dropped edge that should still hold with `superra task dep add`.

The PostToolUse hook still revalidates raw filesystem moves and keeps the same-parent auto-cascade guardrail, but is not the canonical move mechanism. Raw `mv` / `git mv` only for recovery from tool failure, then `superra task check`.

## Diagnostics

`superra task check` is the tree's validation entry point. Run it after any bulk operation or raw filesystem change — it audits status validity, dependency integrity, and cycle-free ordering:

```bash
superra task check                    # validate full tree; prints findings grouped by task
superra task check --category status  # limit to one category: status, dependency, rollup, sync-impact, reproduction
superra task status fix               # repair branch status fields to match child rollups
superra task status propagate         # re-run parent status rollup after bulk edits
```

Findings are prefixed `[ERROR]` (blocking; tree inconsistent), `[WARNING]` (advisory), or `[INFO]`. After recovering from a raw `mv` / `git mv`, run the check before the next dispatch.

## Reproduction

`superra repro` runs the build graph the `## Reproduction` sections declare (schema: [task-file-contract.md](task-file-contract.md) §Reproduction Section).

```bash
superra repro status                      # every required step's freshness; exits 1 unless all are fresh
superra repro status 02-merge check-panel # explicit tasks/steps and their producer ancestors
superra repro status --tier all --json    # the shape `task read` and the dashboard consume
superra repro build                       # rebuild the stale required steps
superra repro build 02-merge -j 4         # a step name or a task path, plus its stale ancestors
superra repro build --dry-run             # what would run, and why
superra repro build check-panel --force   # force the target; rebuild ancestors only when stale or missing
superra repro build check-panel --force-all # force the target and every producer ancestor
superra repro build --tier all --force-all # rerun every registered step
superra repro explain build-panel         # one step: state, changed nodes, upstream, log
superra repro dag --mermaid               # the step graph
superra repro tier 02-merge required      # set a task's tier
```

`--tier` defaults to `required` for `build` and `status`; `on-demand` and `all` are also accepted. Legacy `canon` / `local` arguments alias `required` / `on-demand`. Explicit task or step targets override the tier for both commands and include producer ancestors across tiers; task targets include descendant tasks. Unknown targets fail. Status JSON records `targets` and reports the selected steps; an empty default selection returns success but explicitly verifies no result.

`--force` and `--force-all` are mutually exclusive. Without explicit targets, `--force` forces the tier's steps; `--force-all` also forces their ancestors across tiers. Add `--dry-run` to preview either selection without executing or changing build evidence; downstream execution remains conditional on regenerated content.

`task read <path>` shows a registered task's owned-step states and derived `feeds` / `feeds on` task edges, computed the same way as `repro status --json` but without pytask. `task tree --tier required|on-demand` filters to one tier, accepting the legacy aliases; a registered `required` task gets a `[required]` badge.

| State | Meaning |
|---|---|
| `fresh` | Every recorded input and output still matches. |
| `stale` | A dep, an out, the step definition, or an upstream step changed. |
| `missing` | Never built, or an out is gone. |
| `failed` | The last run exited non-zero and the step still has work to do; the reason names its log. Restoring inputs can clear an ordinary failure. A failed forced rerun requires a successful retry, which the next build attempts even with unchanged inputs. |
| `external` | A dep no step produces is not on disk, so the step cannot run. |

`pytask.lock` at the project root is committed: its ids are the logical `${VAR}` paths, so it reads the same on every checkout. `.superra-repro/` is not — the hash cache, per-step logs, run records, and check stamps live there, and `repro` creates it and adds it to `.gitignore` on first run.

A step's state also moves when a `${VAR}` resolves differently — including one that reaches only `cmd`, such as a mode flag — so a rerun under a changed environment is reported rather than skipped. Lock ids stay in `${VAR}` form throughout.

Only `build` needs pytask, and it re-execs itself under `uv` to get it; nothing has to be installed first.

The dashboard's **Reproduction** view renders the same graph for review: swimlanes by owner task, columns by dependency depth, each step coloured by its state, with a click opening the step's command, files, and log tail. A task page carrying a `## Reproduction` section shows its steps' current state as a table above the declaration, and the section's comment gutter is where a researcher pins graph feedback.

## Comments

Researchers pin comments to `task.md` blocks via the dashboard. `superra task read <path>` already shows unresolved comments with their anchored blocks (`using-superra/SKILL.md §Task Interface`), so use these only for the standalone read/resolve loop:

```bash
superra task comment list <task>           # unresolved comments on a task, each with its full anchored block
superra task comment list <task> --all     # include resolved comments
superra task comment tree                  # unresolved-comment counts across the whole tree
superra task comment resolve <task> <id>   # toggle a comment's resolved state
```

A comment stays **unresolved** until toggled; `resolve` flips it both ways. A comment whose anchored block was edited or moved away renders `[ORPHANED]` with the stored preview. `--json` on `list` / `tree` for scripted consumption.
