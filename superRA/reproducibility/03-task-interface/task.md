---
title: "Surface Reproduction State in the Task CLI"
status: approved
depends_on: [01-section-contract, 02-runner]
---

## Objective

Make the reproduction graph visible and checkable through the commands agents already use, so a task reader sees its steps' state without loading the runner.

- **`task read <path>`** appends a `Reproduction` block after the inherited context: the task's tier, then one line per owned step with state, reason, and outs; then derived task-level edges (`feeds on: <task>`, `feeds: <task>`). State comes from `repro status --json` when pytask is available and degrades to "unknown (runner unavailable)" otherwise. JSON output gains the same fields.
- **`task check`** gains the `reproduction` category wired to the validation findings of [01-section-contract](../01-section-contract/task.md) and runs it by default; never-built steps are runner state, so a fresh clone checks clean.
- **`task tree`** marks `canon` tasks with a badge and accepts `--tier canon|local` to filter.
- **Validation criteria:** CLI tests for each command on a fixture tree with registered and unregistered tasks; `task read` and `task tree` pass with pytask absent.

## Details

- Injection point: [task_read.py](../../../skills/task-tree/scripts/task_read.py) `render_human` / `render_json`; comments are injected the same way, so mirror that pattern.
- `task check` categories are enumerated in [task_check.py](../../../skills/task-tree/scripts/task_check.py) `parse_args`; the dashboard and hook read the same findings.

## Results

`task read`, `task check`, and `task tree` all surface the reproduction graph now, none of them calling the runner CLI or importing pytask — each imports `_repro` / `_repro_state` directly.

### What changed

- **`task read <path>`** appends a `=== Reproduction ===` block (JSON: a `task.reproduction` key) when the task's body carries a `## Reproduction` section: tier, one line per owned step (`name: status — reason [outs: ...]`), then `feeds on:` / `feeds:` lines from `graph.task_edges`. A task with no section gets no block (JSON `null`) — the graph is never built for it, since an unregistered task owns no steps and cannot appear in a task edge, which is what keeps the read cheap on a tree with no `## Reproduction` sections at all.
- **`task check --category reproduction`** wires `_repro.check_reproduction(plan_root, root)` into `run_checks`, reusing the walk `run_checks` already does; it also runs by default (no `--category`), per the objective.
- **`task tree`** marks a canon-registered task `[canon]` (`print_tree`, and `tree_to_json`'s new `tier` field) and accepts `--tier canon|local` to filter. The graph builds with `resolve_vars=False` since only `graph.tiers` is needed — no `${VAR}`/shell evaluation runs just to print a tree.

### Deviation: state comes from a direct library call, not `repro status --json`

The objective names `repro status --json` / pytask availability as the gate; the actual gate is Python's `tomllib` (3.11+), which `_repro_state.read_lock` needs to read `pytask.lock` — `build_graph` and `compute_status` never import pytask (per [02-runner](../02-runner/task.md)'s own results, only `build` needs the engine). `task_read._reproduction_view` calls `_repro.build_graph` and `_repro_state.compute_status` directly, catching `ReproStateError` to degrade every owned step to `status: "unknown"`, `reason: "runner unavailable: <message>"`; task edges (`feeds` / `feeds on`) are unaffected by the degradation, since they come from the graph alone, never from runner state. Shelling out to `superra repro status --json` would route through `repro_run.py`'s re-exec-under-`uv` machinery on every `task read`, which the "no pytask" and "cheap" constraints rule out.

### Validation

17 new tests: `TestTaskReadReproduction`, plus reproduction-category and tier-badge cases added to `TestTaskCheck` / `TestTaskQuery` in [test_task_tree.py](../../../skills/task-tree/scripts/test_task_tree.py), plus 4 CLI-level tests in [test_cli.py](../../../skills/task-tree/scripts/test_cli.py). Coverage: no-section → no block / `null`; a registered, never-built step's tier/status/reason/outs; producer `feeds:` / consumer `feeds on:` edges; the `ReproStateError` degrade path (edges survive it); `import pytask` blocked via `sys.modules` while the read still succeeds; the `reproduction` check category (clean tree, duplicate-out `[ERROR]`, default-run inclusion, never-built-is-not-a-finding); the `[canon]` badge, the JSON `tier` field, and `--tier` filtering.

Suite: 957 passed / 28 skipped under the pytask-free baseline command (940/28 in this worktree before this task); 985 passed with pytask installed too (the runner's own gated tests are unaffected).

### Docs

[commands.md](../../../skills/task-tree/references/commands.md) (category list, a `task read` / `task tree` consumption note), [SKILL.md](../../../skills/task-tree/SKILL.md) (`--tier` example), and [internals.md](../../../skills/task-tree/references/internals.md) (script-inventory rows for `task_read.py` / `task_query.py` / `task_check.py`).
