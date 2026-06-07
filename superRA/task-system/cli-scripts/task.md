---
title: "CLI Scripts"
status: in-progress
depends_on:
  - core-data-layer
tags: []
created: 2026-05-23
---

## Objective

Provide a path-independent task-system CLI that users and agents can invoke through `uv`, without baking local skill or plugin paths into committed task trees.

### Context

The existing flat scripts under `skills/task-system/scripts/` work in this repository because `superRA/` and `skills/` move together. They are not robust when a task tree is created from an installed plugin or synced across machines, because `task_create.py` generates `superRA/serve` with a relative path from the task root to the generation-time `plan_dashboard.py` location.

The redesign should make `uv` the resolver. The task-system code should be package-addressable, and dashboard launch should be a first-class CLI command rather than a committed task-tree wrapper.

### Scope

- House the task-system Python package under `skills/task-system/`, not at repo root, so the superRA plugin repo remains primarily a skills/hooks distribution while the task-system utility can be installed or run independently.
- Expose `superra dashboard` as the human-facing dashboard command.
- Expose a stable `superra task ...` command surface for task read/query/create/update/result/dependency/rename/comment/check/migrate/hook operations.
- Preserve compatibility for existing direct script invocations during the transition; existing tests and skill instructions should not break before documentation is migrated.
- Include `templates/` and `vendor/` dashboard assets as package data instead of relying on `Path(__file__).parent` pointing at the source checkout.
- Remove generated `superRA/serve` wrappers; do not compute or commit generation-time paths to `skills/task-system/scripts`.
- Keep this checkout's optional `superRA/superra` CLI wrapper pinned to its own repo root with `uv run --project skills/task-system`; it is for local development convenience, not dashboard generation.
- Use runtime uv/package resolution for hook entry points where feasible, while preserving harness hook install behavior.
- Preserve the task-system rule that single-field task edits are usually direct `task.md` edits, with CLI mutation commands used for scaffolding, bulk updates, or operations that are easier to validate programmatically.

### Command Target

The target command shape is:

```text
superra dashboard [--root superRA] [--port N] [--no-open]
superra dashboard export [--root superRA] [--output PATH] [--subtree PATH]

superra task read <path> [--root superRA] [--no-ancestors] [--json]
superra task tree [--root superRA] [--status S] [--tag T] [--json]
superra task frontier [--root superRA] [--json]
superra task dag [subtree] [--root superRA]
superra task check [--root superRA] [--json]
superra task create <path> --title TITLE [--objective TEXT] [--guidance TEXT] [...]
superra task update <path> [...]
superra task status cascade <path> --status STATUS
superra task status propagate [--root superRA]
superra task result add <path> [...]
superra task dep add <path> <sibling-slug>
superra task dep remove <path> <sibling-slug>
superra task rename <from-path> <to-path>
superra task comment list <path> [--all] [--json]
superra task comment resolve <path> <comment-id>
superra task comment tree [--json]
superra task migrate from-plan --plan-md PLAN.md [--results-md RESULTS.md] [--output superRA]
superra task migrate upgrade [--root superRA]
superra task hook post-tool-use
```

### Validation

- New task trees do not generate `superRA/serve`, and the checked-in `superRA/serve` is removed or deliberately deprecated.
- `uv run --project skills/task-system superra dashboard --root superRA --no-open` reaches the dashboard CLI from the live local checkout; `uvx --refresh --from ./skills/task-system ...` remains the install-style smoke path.
- `./superRA/superra task frontier` resolves this repo's own task-system package and this repo's `superRA/` task tree.
- Existing direct script tests continue to pass during the transition.
- Active docs and role references stop teaching agents to depend on `<skill-dir>/scripts/...` for normal task-system operations.

## Results

**Final diff self-check:** `git diff 9ca25479f7cb588aec3d758f0bb27d66e4c8aded..HEAD`; surviving-change classes are package metadata/version/entry point, unified task/dashboard CLI, dashboard package-data paths, no-serve hook/wrapper migration, packaged-CLI docs/tests, generated Codex/direct-mode reference refresh, and task-tree implementation/review records. Suspicious hunks are justified as follows: `skills/*` and `agents/*` instruction edits replace flat script / generated `serve` guidance with the approved `superra task ...` and `superra dashboard` command surface while preserving incoming `postponed` and focused-read semantics; `.codex/agents/*.toml` and `skills/using-superRA/references/direct-mode-*.md` are generated from the canonical role specs and verified by `sync_codex_agents.py --scope project --check`; `superRA/serve` deletion implements the researcher decision to drop the wrapper; synced task-record edits under `superRA/postponed-status/**`, `superRA/review-planning-protocol/**`, and `superRA/task-system/agent-interface/integ-workflow/**` remove stale command wording or stale sync-impact residue after preserving incoming base intent. No unrelated cleanup hunks identified.

**Local development follow-up:** root `CLAUDE.md` now instructs agents to use `uv run --project skills/task-system ...` for this checkout, with `uvx --refresh --from ./skills/task-system ...` reserved for install-style smoke tests. The repo-local `superRA/superra` wrapper resolves its own repo root and dispatches through that local `uv run --project` path.

### Key Findings
- 6 scripts, each 65–210 lines, all following argparse + function pattern
- `task_create.py` validates parent exists, no duplicates, deps are existing siblings
- `task_link.py` includes `_has_transitive_dep()` for cycle detection
- `task_rename.py` uses parse-first approach (validate all siblings before renaming)
- `task_query.py` provides tree (Unicode status icons), frontier (dispatch-ready leaves), DAG (Mermaid with classDef)
- `tree_to_json()` includes `objective`, `results`, `decisions`, `review_notes` parsed from body sections
