---
title: "CLI Scripts"
status: approved
depends_on:
  - core-data-layer
---

## Objective

Provide a path-independent task-tree CLI that users and agents can invoke through `uv`, without baking local skill or plugin paths into committed task trees.

### Context

The existing flat scripts under `skills/task-tree/scripts/` work in this repository because `superRA/` and `skills/` move together. They are not robust when a task tree is created from an installed plugin or synced across machines, because `task_create.py` generates `superRA/serve` with a relative path from the task root to the generation-time `plan_dashboard.py` location.

The redesign should make `uv` the resolver. The task-tree code should be package-addressable, and dashboard launch should be a first-class CLI command rather than a committed task-tree wrapper.

### Scope

- House the task-tree Python package under `skills/task-tree/`, not at repo root, so the superRA plugin repo remains primarily a skills/hooks distribution while the task-tree utility can be installed or run independently.
- Expose `superra dashboard` as the human-facing dashboard command.
- Expose a stable `superra task ...` command surface for task read/query/create/update/result/dependency/rename/comment/check/migrate/hook operations.
- Include `templates/` and `vendor/` dashboard assets as package data instead of relying on `Path(__file__).parent` pointing at the source checkout.
- Remove generated `superRA/serve` wrappers; do not compute or commit generation-time paths to `skills/task-tree/scripts`.
- Keep this checkout's `superRA/superra` CLI wrapper self-resolving to its own repo root and running the loose entry scripts via `uv run --script` (with a `python3` fallback); it is for local development convenience, not dashboard generation.
- Use runtime uv/package resolution for hook entry points where feasible, while preserving harness hook install behavior.
- Preserve the task-tree rule that single-field task edits are usually direct `task.md` edits, with CLI mutation commands used for scaffolding, bulk updates, or operations that are easier to validate programmatically.

### Command Surface (shipped)

The shipped `superra` surface (`<path>` is task-root-relative; `--root` auto-detects, preferring `superRA/`):

```text
superra dashboard [--root superRA] [--port N] [--no-open] [--foreground]
superra dashboard export [--root superRA] [--output PATH] [--subtree PATH]
superra dashboard artifact setup [...]
superra dashboard stop [--root superRA]

superra task read <path> [--no-ancestors] [--json]
superra task tree [--status S] [--tag T] [--json]
superra task frontier [--json]
superra task dag [subtree]
superra task check [--category C] [--json]
superra task create <path> --title TITLE [--objective TEXT] [--guidance TEXT] [...]
superra task update <path> [--status S] [--title T] [--add-tag T] [--remove-tag T] [--script S]
superra task status cascade <path> --status STATUS
superra task status propagate
superra task status fix
superra task result add <path> [--finding ...] [--figure ...] [--note ...]
superra task dep add <path> <sibling-slug>
superra task dep remove <path> <sibling-slug>
superra task move <from-path> <to-path>
superra task rename <from-path> <to-path>  # same-parent compatibility alias
superra task comment list <path> [--all] [--json]
superra task comment resolve <path> <comment-id>
superra task comment tree [--json]
superra task migrate from-plan --plan-md PLAN.md [--results-md RESULTS.md] [--output superRA]
superra task migrate upgrade [--root superRA]
superra task migrate upgrade-status [--dry-run] [--root superRA]
superra task hook

superra wrapper init [--root superRA]
superra wrapper render-hook [--output PATH]
```

## Results

A path-independent `superra` CLI is shipped as a package under `skills/task-tree/`, with `uv` as the resolver so committed task trees carry no local skill or plugin paths and no generated `superRA/serve` wrappers.

- **Command surface.** The packaged `superra` command routes through `skills/task-tree/scripts/cli.py` to ~18 focused entry/helper modules under `skills/task-tree/scripts/` (`task_create.py`, `task_update.py`, `task_link.py`, `task_rename.py`, `task_query.py`, `task_read.py`, `task_add_result.py`, `task_comment.py`, `task_check.py`, `plan_migrate.py`, `plan_dashboard.py`, `task_hook.py`, `wrapper_resolver.py`), with shared internals in `_task_io.py`, `_comments.py`, `_worktree_discovery.py`. `superra dashboard` is the human-facing dashboard command; `superra task ...` is the read/query/create/update/result/dependency/rename/comment/check/migrate/hook surface.
- **Mutation invariants** live in the mutator functions (one enforcement point regardless of entry surface): `resolve_path` containment plus redundant-root-prefix tolerance, sibling-only dependency validation, cycle detection (`_has_transitive_dep`), and the same-parent / cross-parent move invariants in `task_rename.py`.
- **Source resolution** is single-sourced in `wrapper_resolver.py` (`uv run --script` with a `python3` fallback), rendered into the committed `superRA/superra` wrapper and the `hooks/task-hook` shim, both pinned by byte-identity tests. Root `CLAUDE.md §Local Task-Tree CLI Development` instructs running the loose entry scripts via `uv run --script skills/task-tree/scripts/cli.py …`, which is script-scoped and never provisions the repo environment.
- **Task move.** `superra task move FROM TO` is the canonical path for intentional task path changes (`superra task rename FROM TO` remains a same-parent compatibility alias). Move carries the task directory, rewrites local Markdown links from pre-move context, cascades same-parent sibling `depends_on` rewrites, and rejects cross-parent moves that would strand dependencies. Raw `mv` / `git mv` is documented as recovery-only, with the PostToolUse hook as a guardrail. Focused CLI tests cover cross-parent link rewriting, dependency-stranding rejection, rootless forest destination moves, same-parent rename cascading, and cross-parent rename rejection.
