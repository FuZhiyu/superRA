---
title: "Runner, CLI Views, and Dashboard Include Producers by Default"
status: not-started
depends_on: []
---

## Objective

Implement the parent's decisions in the `superra repro` runner, the task CLI views, and the dashboard, and update the task-tree mechanics docs to match.

- **Runner.** Default producer-chain scope for `build`, `status`, and `build --dry-run`; `--only`; the hidden `--upstream` alias; target-only `--force`; the build preview; and the line naming non-fresh producers on `accept` (text, `--dry-run`, JSON).
- **Default status output and exit codes** as the parent specifies. Status JSON keeps `upstream` true when the chain was assessed and carries `behind` in `--only` mode.
- **Bounded saved-input lists.** Cap the saved-input list in `status` ([_repro_state.py:1160](../../../../skills/task-tree/scripts/_repro_state.py#L1160)) and the per-file `Saved input:` lines in `build` ([repro_run.py:378](../../../../skills/task-tree/scripts/repro_run.py#L378)) under `OUTPUT_CAP`, with a count line pointing to `--json`.
- **Views.** The frontier and `task read` hint drops `--upstream` ([_task_snapshot.py:95](../../../../skills/task-tree/scripts/_task_snapshot.py#L95)). The dashboard Build menu offers build (with producers), only this, and force ([plan_dashboard.py `_build_args`](../../../../skills/task-tree/scripts/plan_dashboard.py#L1849), [dashboard.js:2277](../../../../skills/task-tree/scripts/templates/dashboard.js#L2277)).
- **Mechanics docs.** [commands.md §Reproduction](../../../../skills/task-tree/references/commands.md#reproduction), [internals.md](../../../../skills/task-tree/references/internals.md) graph actions, and [task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md) wherever they state the scope default.

### Validation

- Regression tests on disposable shell-step fixtures assert which commands actually executed:
  - A default build of a consumer reruns a stale producer and skips fresh ones.
  - `--only` reproduces today's scoped behavior, including a missing saved input blocking and naming its producer.
  - `--force` reruns the targets only; stale producers still build, and fresh producers stay untouched.
  - With a stale producer, `accept` records the consumer and names the producer; the next default `status` exits 3.
  - Accepted consumer, then its producer rebuilt: identical bytes leave the consumer unchanged, and changed bytes rerun it.
  - `--upstream` behaves exactly like the default.
  - Default `status` and `build` output stays within the cap on a chain longer than `OUTPUT_CAP`.
- The full script suite passes.
- A script-level run on a disposable fixture shows default build, `--only`, `--force`, and `accept` from the command line.

## Details

- **Selection.** `select_steps(..., include_ancestors=...)` in [_repro_state.py](../../../../skills/task-tree/scripts/_repro_state.py) is the one resolver. The flip happens at the CLI layer in [repro_run.py](../../../../skills/task-tree/scripts/repro_run.py) (`args.upstream` becomes `not args.only`). `_behind_selection` ([repro_run.py:610](../../../../skills/task-tree/scripts/repro_run.py#L610)) already computes the non-fresh producers that `--only` mode and the `accept` line need.
- **Force.** Today `--force` covers the resolved scope (`force_names` passed to `run_build`). It must now cover the resolved targets without ancestors.
- **Tests to update.** [test_repro_scope.py](../../../../skills/task-tree/scripts/test_repro_scope.py), [test_repro_runner.py](../../../../skills/task-tree/scripts/test_repro_runner.py), [test_repro_acceptance.py](../../../../skills/task-tree/scripts/test_repro_acceptance.py), [test_repro_engine.py](../../../../skills/task-tree/scripts/test_repro_engine.py), [test_task_dependencies.py](../../../../skills/task-tree/scripts/test_task_dependencies.py), [test_dashboard.py](../../../../skills/task-tree/scripts/test_dashboard.py), and [tests/test_dag_workspace_browser.py](../../../../skills/task-tree/scripts/tests/test_dag_workspace_browser.py) all exercise `--upstream` or scoped defaults.
- **In-flight edits.** On 2026-10-01 the working tree held uncommitted, unrelated edits that add a `task check --all` cap: `commands.md`, `internals.md`, `task_check.py`, `task_hook.py`, `_task_validate.py`, `cli.py`, `test_task_tree.py`, and `CLAUDE.md`. Leave them out of this task's commits unless they have landed by then.
