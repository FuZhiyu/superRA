---
title: "CLI Scripts"
status: approved
depends_on:
  - core-data-layer
tags: []
created: 2026-05-23
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
- Preserve compatibility for existing direct script invocations during the transition; existing tests and skill instructions should not break before documentation is migrated.
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

### Validation

- New task trees do not generate `superRA/serve`, and the checked-in `superRA/serve` is removed or deliberately deprecated.
- `uv run --script skills/task-tree/scripts/plan_dashboard.py dashboard --root superRA --no-open` reaches the dashboard from the live local checkout (no install, no caller venv).
- `./superRA/superra task frontier` self-resolves this checkout's task-tree source and this repo's `superRA/` task tree.
- Existing direct script tests continue to pass during the transition.
- Active docs and role references stop teaching agents to depend on `<skill-dir>/scripts/...` for normal task-tree operations.

## Results

**Final diff self-check:** `git diff 9ca25479f7cb588aec3d758f0bb27d66e4c8aded..HEAD`; surviving-change classes are package metadata/version/entry point, unified task/dashboard CLI, dashboard package-data paths, no-serve hook/wrapper migration, packaged-CLI docs/tests, generated Codex/direct-mode reference refresh, and task-tree implementation/review records. Suspicious hunks are justified as follows: `skills/*` and `agents/*` instruction edits replace flat script / generated `serve` guidance with the approved `superra task ...` and `superra dashboard` command surface while preserving incoming `postponed` and focused-read semantics; `.codex/agents/*.toml` and `skills/using-superra/references/direct-mode-*.md` are generated from the canonical role specs and verified by `sync_codex_agents.py --scope project --check`; `superRA/serve` deletion implements the researcher decision to drop the wrapper; synced task-record edits under `superRA/task-tree/status-model/11-postponed-core-semantics`, `superRA/task-tree/status-model/12-postponed-rendering-surfaces`, `superRA/task-tree/status-model/13-postponed-docs`, `superRA/task-tree/planning-redesign/review-planning-protocol/**`, and `superRA/task-tree/agent-interface/integ-workflow/**` remove stale command wording or stale sync-impact residue after preserving incoming base intent. No unrelated cleanup hunks identified.

**Local development follow-up:** root `CLAUDE.md §Local Task-Tree CLI Development` instructs agents to run the loose entry scripts via `uv run --script skills/task-tree/scripts/cli.py …` for this checkout — script-scoped, so it never provisions the repo environment and reflects source edits on the next run with no cache-bust. The repo-local `superRA/superra` wrapper self-resolves its repo root and dispatches through that same `uv run --script` path (`python3` fallback). The `uv run --project` / `uvx` framing was superseded by the `cli-source-resolution` child's `uv run --script` model.

**Task move command:** `superra task move FROM TO` is now the canonical path for intentional task path changes, while `superra task rename FROM TO` remains a same-parent compatibility alias. The move implementation carries the task directory, rewrites local Markdown links using pre-move context, cascades same-parent sibling `depends_on` rewrites, and rejects cross-parent moves that would strand old-sibling or moved-task dependencies. User guidance in `skills/task-tree/SKILL.md` and `skills/task-tree/references/commands.md` now teaches raw `mv` / `git mv` as recovery-only, with the PostToolUse hook documented as a guardrail rather than the canonical move mechanism. Focused CLI tests cover cross-parent link rewriting, dependency-stranding rejection, rootless forest destination moves, same-parent rename dependency cascading, and cross-parent rename rejection.

### Key Findings
- The shipped surface is the packaged `superra` command in [cli.py](../../../../skills/task-tree/scripts/cli.py), which routes to ~18 focused entry/helper modules under `skills/task-tree/scripts/` (e.g. `task_create.py`, `task_update.py`, `task_link.py`, `task_rename.py`, `task_query.py`, `task_read.py`, `task_add_result.py`, `task_comment.py`, `task_check.py`, `plan_migrate.py`, `plan_dashboard.py`, `task_hook.py`, `wrapper_resolver.py`), with shared internals in `_task_io.py`, `_comments.py`, `_worktree_discovery.py`.
- Mutation invariants live in the mutator functions (single enforcement point regardless of entry surface): `resolve_path` containment + redundant-root-prefix tolerance, sibling-only dependency validation, cycle detection (`_has_transitive_dep`), and same-parent / cross-parent move invariants in `task_rename.py`.
- Source resolution and run-line are single-sourced in `wrapper_resolver.py` (`uv run --script` + `python3` fallback), rendered into the committed `superRA/superra` wrapper and `hooks/task-hook` shim, both pinned by byte-identity tests.
