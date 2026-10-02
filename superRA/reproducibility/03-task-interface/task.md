---
title: "Surface Reproduction State in the Task CLI"
status: approved
depends_on: [01-section-contract, 02-runner]
---

## Objective

Make the reproduction graph visible and checkable through the commands agents already use, so a task reader sees its prerequisites, the inputs whose producer needs a build, and its own steps' state without running a build.

- **`task read <path>`** shows prerequisites (`depends_on`, own or inherited) apart from file inputs, a `Not ready:` line naming the blockers or the reason, the inputs whose producer is `stale`, `missing`, or `failed`, and one line per owned step with state, reason, its own state when a producer lifts it, and outs. JSON carries the same under `readiness` and `task.reproduction`.
- **`task frontier`** lists ready leaves with those inputs. An input from an `unverified` producer is not flagged, because a build never runs that producer.
- **`task check`** runs the `reproduction` category by default. Never-built steps are runner state, so a fresh clone checks clean.

## Results

`task read`, `task frontier`, and `task check` read the graph and step states directly from [_repro.py](../../../skills/task-tree/scripts/_repro.py) and [_repro_state.py](../../../skills/task-tree/scripts/_repro_state.py), with one status pass per command; they never call the runner CLI. Output shapes are documented in [commands.md §Reproduction](../../../skills/task-tree/references/commands.md#reproduction).

- **`task read`** ([task_read.py](../../../skills/task-tree/scripts/task_read.py)) lists only the flagged inputs, one line per file and producer with the hint `superra repro build <task>`, then a count of the rest (`CURRENT` in [_task_snapshot.py](../../../skills/task-tree/scripts/_task_snapshot.py)). A task with no `## Reproduction` section gets no step block and never builds the graph. If state cannot be computed, every owned step reads `unknown` with the reason, and the edges survive.
- **`task check --category reproduction`** ([task_check.py](../../../skills/task-tree/scripts/task_check.py)) reports the graph findings from [01-section-contract](../01-section-contract/task.md), plus one `[WARNING]` per file a task's `## Results` links that looks generated and that no active step writes or reads ([_repro_signals.py](../../../skills/task-tree/scripts/_repro_signals.py)).
  - **Generated** means a data or exhibit extension (`.csv`, `.parquet`, `.png`, `.pdf`, and similar) or a `.tex` inside a directory a step writes. Links to prose or source, scratch-named and dotted paths, missing files, and trees with no reproduction config stay silent.
  - Known misses, all in the quiet direction: a generated `.txt`, `.json`, `.html`, or `.log`, and a generated `.tex` outside every out directory.
  - A legitimately producer-less file, such as a hand-captured screenshot, warns on every `task check` with no way to acknowledge it.
- **`task tree`** carries no reproduction marker; `task tree --json` reports `effective_depends_on` without resolving variables.

Tests: the reproduction cases in [test_task_tree.py](../../../skills/task-tree/scripts/test_task_tree.py) and [test_cli.py](../../../skills/task-tree/scripts/test_cli.py), and the readiness cases in [test_task_dependencies.py](../../../skills/task-tree/scripts/test_task_dependencies.py).
