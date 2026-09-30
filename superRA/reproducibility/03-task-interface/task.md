---
title: "Surface Reproduction State in the Task CLI"
status: approved
depends_on: [01-section-contract, 02-runner]
---

## Objective

Make the reproduction graph visible and checkable through the commands agents already use, so a task reader sees its steps' state without loading the runner.

- **`task read <path>`** appends a `Reproduction` block after the inherited context: one line per owned step with state, reason, and outs; then derived task-level edges (`feeds on: <task>`, `feeds: <task>`). State comes from `repro status --json` when pytask is available and degrades to "unknown (runner unavailable)" otherwise. JSON output gains the same fields.
- **`task check`** gains the `reproduction` category wired to the validation findings of [01-section-contract](../01-section-contract/task.md) and runs it by default; never-built steps are runner state, so a fresh clone checks clean.
- **Validation criteria:** CLI tests for each command on a fixture tree with registered and unregistered tasks; `task read` and `task tree` pass with pytask absent.

## Details

- Injection point: [task_read.py](../../../skills/task-tree/scripts/task_read.py) `render_human` / `render_json`; comments are injected the same way, so mirror that pattern.
- `task check` categories are enumerated in [task_check.py](../../../skills/task-tree/scripts/task_check.py) `parse_args`; the dashboard and hook read the same findings.

## Results

`task read` and `task check` surface the reproduction graph without calling the runner CLI or importing an engine — each imports `_repro` / `_repro_state` directly.

### What changed

- **`task read <path>`** appends a `=== Reproduction ===` block (JSON: a `task.reproduction` key) when the task's body carries a `## Reproduction` section: one line per owned step (`name: status — reason [outs: ...]`), then `feeds on:` / `feeds:` lines from `graph.task_edges`. A task with no section gets no block (JSON `null`) — the graph is never built for it, which keeps the read cheap on a tree with no `## Reproduction` sections at all. [03-readiness-model](../14-review-revisions/03-readiness-model/task.md) later added the prerequisites and not-fresh inputs above this block.
- **`task check --category reproduction`** wires `_repro.check_reproduction(plan_root, root)` into `run_checks`, reusing the walk `run_checks` already does; it also runs by default (no `--category`), per the objective.
- **`task tree`** carries no reproduction marker. Its `[canon]` badge and `--tier` filter were removed with the tier system in [task targets and lifecycle](../11-scoped-verification/task-targets-and-lifecycle/task.md).

### Deviation: state comes from a direct library call, not `repro status --json`

The objective gates state on `repro status --json` and pytask availability. `task_read._reproduction_view` instead calls `_repro.build_graph` and `_repro_state.compute_status` directly, which never needed an engine, and catches `ReproStateError` to degrade every owned step to `status: "unknown"`, `reason: "runner unavailable: <message>"`. Task edges (`feeds` / `feeds on`) come from the graph alone and survive the degradation. Shelling out to `superra repro status --json` would route through `repro_run.py`'s re-exec-under-`uv` machinery on every `task read`, which the "cheap" constraint rules out. The runner has since dropped pytask ([01-engine-freshness](../14-review-revisions/01-engine-freshness/task.md)); only a legacy `pytask.lock` still needs Python 3.11's `tomllib`.

### Validation

`TestTaskReadReproduction` and the reproduction-category cases in `TestTaskCheck` ([test_task_tree.py](../../../skills/task-tree/scripts/test_task_tree.py)), plus CLI-level tests in [test_cli.py](../../../skills/task-tree/scripts/test_cli.py). Coverage: no-section → no block / `null`; a registered, never-built step's status, reason, and outs; producer `feeds:` / consumer `feeds on:` edges; the `ReproStateError` degrade path (edges survive it); `import pytask` blocked via `sys.modules` while the read still succeeds; the `reproduction` check category (clean tree, duplicate-out `[ERROR]`, default-run inclusion, never-built-is-not-a-finding).

### Docs

[commands.md](../../../skills/task-tree/references/commands.md) (category list, the `task read` consumption note) and [internals.md](../../../skills/task-tree/references/internals.md) (script-inventory rows for `task_read.py` / `task_check.py`).
