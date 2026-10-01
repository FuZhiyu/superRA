---
title: "Commands Include the Producer Chain, Gate Downloads, and Report Online-Only Data"
status: not-started
depends_on: [01-local-graph]
---

## Objective

Implement the parent's §Commands in the `superra repro` runner and the task CLI views, on the states [01-local-graph](../01-local-graph/task.md) produces.

- **Runner.**
  - Default producer-chain scope for `build`, `status`, and `build --dry-run`; `--only`; the hidden `--upstream` alias; and target-only `--force`.
  - The run rule, under which `unverified` steps never run.
  - The download gate, the build preview, and `accept`'s line naming non-fresh producers (text, `--dry-run`, JSON).
- **Default `status`.** Output and exit codes as the parent specifies, with this report shape:
  - `selected` holds the targets' steps only; the assessed producers are kept apart.
  - The exit code comes from the selected steps' own states and the producers' reported states, not `report.ok`.
  - JSON lists the selected steps under `steps` as today, and every assessed producer under `producers`, uncapped, with `status` and `local_status`.
  - `ok` is true only when every assessed step is `fresh` or `unverified`. `summary` counts selected steps and producers separately. `--only` mode keeps `behind`.
- **Online-only reporting.** Wherever a command names files it cannot check here (the gate, the `unverified` summary line, `accept`'s refusal), list them with sizes under `OUTPUT_CAP`, add a count line pointing to `--json`, and point once to the download notes in the [reproducibility skill](../../../../skills/reproducibility/SKILL.md).
- **Bounded saved-input lists.** Cap the saved-input list in `status` ([_repro_state.py:1160](../../../../skills/task-tree/scripts/_repro_state.py#L1160)) and the per-file `Saved input:` lines in `build` ([repro_run.py:378](../../../../skills/task-tree/scripts/repro_run.py#L378)) the same way.
- **Views.**
  - The frontier and `task read` hint drops `--upstream` ([_task_snapshot.py:95](../../../../skills/task-tree/scripts/_task_snapshot.py#L95)).
  - `task read` shows a step's own state under that name, not "for saved inputs" ([task_read.py:258](../../../../skills/task-tree/scripts/task_read.py#L258)).
  - The `MODEL` help text describes the new default ([repro_run.py:479](../../../../skills/task-tree/scripts/repro_run.py#L479)).
- **Mechanics docs.** [commands.md §Reproduction](../../../../skills/task-tree/references/commands.md#reproduction).

### Validation

- Regression tests on disposable shell-step fixtures assert which commands actually executed:
  - A default build of a consumer reruns a stale producer and skips fresh and `unverified` ones.
  - `--only` reproduces today's scoped behavior, including a missing saved input blocking and naming its producer.
  - `--force` reruns the targets only; stale producers still build, and fresh producers stay untouched.
  - With a stale producer, `accept` records the consumer and names the producer; the next default `status` exits 3.
  - Accepted consumer, then its producer rebuilt: identical bytes leave the consumer unchanged, and changed bytes rerun it.
  - The gate: a step that must run but reads an online-only file, or an absent file no step produces, runs nothing anywhere in the build, and lists the file with its size.
  - `--upstream` behaves exactly like the default.
  - Default `status` and `build` output stays within the cap on a chain longer than `OUTPUT_CAP`.
  - Default `status --json` separates `steps` from `producers`, and its `ok` and exit code agree with the text output.
- The full script suite passes.
- A script-level run on a disposable fixture shows default build, `--only`, `--force`, the gate, and `accept` from the command line.

## Details

- **Selection.** `select_steps(..., include_ancestors=...)` in [_repro_state.py](../../../../skills/task-tree/scripts/_repro_state.py) is the one resolver. The flip happens at the CLI layer in [repro_run.py](../../../../skills/task-tree/scripts/repro_run.py) (`args.upstream` becomes `not args.only`). `_behind_selection` ([repro_run.py:610](../../../../skills/task-tree/scripts/repro_run.py#L610)) already computes the non-fresh producers that `--only` mode and the `accept` line need.
- **Force.** Today `--force` covers the resolved scope (`force_names` passed to `run_build`, [repro_run.py:743](../../../../skills/task-tree/scripts/repro_run.py#L743)). It must now cover the resolved targets without ancestors.
- **Gate placement.** `run_build` already checks saved inputs before `_schedule` ([repro_run.py:375-382](../../../../skills/task-tree/scripts/repro_run.py#L375-L382)). The gate runs at the same point over the steps that will run, so a blocked build writes no run records.
- **Tests to update.** [test_repro_scope.py](../../../../skills/task-tree/scripts/test_repro_scope.py), [test_repro_runner.py](../../../../skills/task-tree/scripts/test_repro_runner.py), [test_repro_acceptance.py](../../../../skills/task-tree/scripts/test_repro_acceptance.py), [test_repro_engine.py](../../../../skills/task-tree/scripts/test_repro_engine.py), and [test_task_dependencies.py](../../../../skills/task-tree/scripts/test_task_dependencies.py) exercise `--upstream` or scoped defaults.
- **In-flight edits.** On 2026-10-01 the working tree held uncommitted, unrelated edits that add a `task check --all` cap: `commands.md`, `internals.md`, `task_check.py`, `task_hook.py`, `_task_validate.py`, `cli.py`, `test_task_tree.py`, and `CLAUDE.md`. Leave them out of this task's commits unless they have landed by then.
