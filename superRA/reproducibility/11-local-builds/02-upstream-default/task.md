---
title: "Commands Include the Producer Chain, Gate Downloads, and Report Online-Only Data"
status: implemented
depends_on: [01-local-graph]
---

## Objective

Implement the parent's §Commands in the `superra repro` runner and the task CLI views, on the states [01-local-graph](../01-local-graph/task.md) produces.

- **Runner.**
  - Default producer-chain scope for `build`, `status`, and `build --dry-run`; `--only`; the hidden `--upstream` alias; and target-only `--force`.
  - The run rule, under which `unverified` steps never run.
  - The download gate, before scheduling and again at each step's start in `_missing_inputs`, with the message the parent specifies.
  - The build preview, and `accept`'s line naming non-fresh producers (text, `--dry-run`, JSON).
  - The `--only` refusal for a missing saved input names `--only`'s alternative, not `--upstream` ([repro_run.py:381](../../../../skills/task-tree/scripts/repro_run.py#L381)).
- **Default `status`.** Output and exit codes as the parent specifies, with this report shape:
  - `selected` holds the targets' steps only; the assessed producers are kept apart.
  - The exit code comes from the selected steps' own states and the producers' reported states, not `report.ok`.
  - JSON lists the selected steps under `steps` as today, and every assessed producer under `producers`, uncapped, with `status` and `local_status`.
  - `ok` is true only when every assessed step is `fresh` or `unverified`. `summary` counts selected steps and producers separately. `--only` mode keeps `behind`.
- **Online-only reporting.** Wherever a command names files it cannot check here (the gate, the `unverified` summary line, `accept`'s refusal), list them with sizes under `OUTPUT_CAP`, add a count line pointing to `--json`, and point once to the download notes in the [reproducibility skill](../../../../skills/reproducibility/SKILL.md).
- **Bounded saved-input lists.** Cap the saved-input list in `status` ([_repro_state.py:1160](../../../../skills/task-tree/scripts/_repro_state.py#L1160)) and the per-file `Saved input:` lines in `build` ([repro_run.py:378](../../../../skills/task-tree/scripts/repro_run.py#L378)) the same way.
- **Views.**
  - The frontier and `task read` flag inputs per the parent's §Frontier (`CURRENT` at [_task_snapshot.py:11](../../../../skills/task-tree/scripts/_task_snapshot.py#L11)), and the hint drops `--upstream` ([_task_snapshot.py:95](../../../../skills/task-tree/scripts/_task_snapshot.py#L95)).
  - `task read` shows a step's own state under that name, not "for saved inputs" ([task_read.py:258](../../../../skills/task-tree/scripts/task_read.py#L258)).
  - The `MODEL` help text describes the new default ([repro_run.py:479](../../../../skills/task-tree/scripts/repro_run.py#L479)).
- **Mechanics docs.** [commands.md §Reproduction](../../../../skills/task-tree/references/commands.md#reproduction), apart from the state table (01), and the frontier hint in [task-file-contract.md:103](../../../../skills/task-tree/references/task-file-contract.md#L103).

### Validation

- Regression tests on disposable shell-step fixtures assert which commands actually executed:
  - A default build of a consumer reruns a stale producer and skips fresh and `unverified` ones.
  - `--only` reproduces today's scoped behavior, including a missing saved input blocking and naming its producer.
  - `--force` reruns the targets only; stale producers still build, and fresh producers stay untouched.
  - With a stale producer, `accept` records the consumer and names the producer; the next default `status` exits 3.
  - Accepted consumer, then its producer rebuilt: identical bytes leave the consumer unchanged, and changed bytes rerun it.
  - The gate: a step that must run but reads an online-only file, or an absent file no step produces, runs nothing anywhere in the build, and lists the file with its size. A step that turns stale only after its producer ran is stopped at its start, and never reads the file.
  - The frontier does not flag an input whose producer is `unverified`.
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

## Results

`build`, `status`, and `build --dry-run` now take in the targets' producer chain by default, `--only` restores the old scoped behavior, and a build that would read a file not on this machine runs nothing and lists the file with its size. A command-line run on a disposable fixture showed each path, including the gate stopping a build on a real online-only Box file without materializing it.

### Commands

- **Scope.** `build` and `status` resolve targets with `select_steps(..., include_ancestors=not args.only)`. `--upstream` is a hidden alias for the default, and combining it with `--only` is a usage error ([repro_run.py:607](../../../../skills/task-tree/scripts/repro_run.py#L607)).
- **Force covers the targets only.** `--force` passes the targets' own steps (`requested`). An added producer runs only when its state calls for it.
- **What runs.** Unchanged from 01: `stale`, `missing`, `failed`, and forced steps run, and `unverified` steps never do. Added producers that do not run are counted in the closing line, not printed one per line.
- **Build preview.** Before executing, `build` prints the added producers that will run, with their last durations, capped ([repro_run.py:422](../../../../skills/task-tree/scripts/repro_run.py#L422)). The `Execution scope:` line and the `Saved input:` lines are capped too.
- **`--only` refusal.** A missing saved input now ends with `build without --only to include their producers`.
- **`accept`.** After recording, and in `--dry-run`, `accept` names the producers behind the accepted steps that are `stale`, `missing`, or `failed`. It says the accepted steps read stale until those are built or accepted. JSON adds `behind` and `targets`.

### Download gate

- **Placement.** Inside the mutation lock and before `_schedule`, `_will_run` takes every step whose own state is `stale`, `missing`, or `failed`, or that is forced ([repro_run.py:397](../../../../skills/task-tree/scripts/repro_run.py#L397)). `_gate` then refuses the whole build when one of those steps reads a file not on disk ([repro_run.py:404](../../../../skills/task-tree/scripts/repro_run.py#L404)). A refused build writes no run records.
  - Not on disk: online-only, even if cached, or absent with no producer.
  - Exempt: an input that a step running in this build writes first.
- **One check, two call sites.** `_unreadable_inputs` ([repro_run.py:139](../../../../skills/task-tree/scripts/repro_run.py#L139)) is 01's step-start refusal, factored out. `_gate` uses it before scheduling, and `_missing_inputs` uses it again when each step starts. A step that turns stale only after its producer ran is stopped at its start, and records no run.
- **Message.** One shared formatter, `unread_file_lines` ([_repro_state.py:1443](../../../../skills/task-tree/scripts/_repro_state.py#L1443)), writes the gate message, the step-start refusal, `accept`'s refusal, and the `status` file list:
  - each file with its size, capped;
  - a count line naming the `status … --json` command that lists every file;
  - for the gate, the `--only` line;
  - the pointer to `references/online-only-files.md` in `superRA:reproducibility`, once, when any file is online-only.

  On the fixture:

  ```
  Error: 1 file(s) the build reads are not on this machine, so nothing was run:
    Data/box.xlsx        5.1 MB  online-only here  (read by box)
  To build the steps that do not read them, select those steps with --only.
  Before downloading, read references/online-only-files.md in the superRA:reproducibility skill.
  ```

### Status report shape

- **`selected` holds the targets' own steps.** `compute_status(upstream=True)` keeps the producers in `entries`, and `StatusReport.producers` returns them ([_repro_state.py:947](../../../../skills/task-tree/scripts/_repro_state.py#L947)).
- **Exit code.** `StatusReport.exit_code` ([_repro_state.py:963](../../../../skills/task-tree/scripts/_repro_state.py#L963)) returns:
  - 1 for a graph error, or a selected step whose own state is `stale`, `missing`, or `failed`;
  - 3 when only a producer's reported state is;
  - 0 otherwise.

  With `--only`, the CLI still exits 3 when `behind` is non-empty. `report.ok` now means every assessed step is `fresh` or `unverified`.
- **JSON.**
  - `steps`: the selected steps.
  - `producers`: every assessed producer, uncapped, with `status` and `local_status`.
  - `summary`: the selected-step counts at top level, as before, and producer counts under `summary.producers`.
  - `behind`: emitted only under `--only`.
  - `external_inputs`: now covers producers' external inputs too.
- **Text** ([_repro_state.py:1504](../../../../skills/task-tree/scripts/_repro_state.py#L1504)).
  - One line per selected step, then the producers' counts per state.
  - Each `stale`, `missing`, or `failed` producer by name: the steps whose own state blocks first, then the ones they lift. Capped.
  - One line for `unverified` producers: their count, their total online-only size, and the boundary from `unverified_boundary`.
  - The files of every `unverified` step that are online-only or unreadable here, with sizes.
  - Saved inputs and missing external inputs, each capped. Every elided list has a count line naming `--json`.

### Views and docs

- **Frontier.** `CURRENT` now includes `unverified`, so the frontier and `task read` flag only inputs whose producer is `stale`, `missing`, or `failed`. The hint is `superra repro build <task>`.
- **`task read`.** It prints `own state: …` where it printed `for saved inputs: …`.
- **Help text.** `MODEL` and the subcommand help describe the producer-chain default, `--only`, target-only `--force`, and `unverified`.
- **Mechanics docs.**
  - [commands.md §Reproduction](../../../../skills/task-tree/references/commands.md#reproduction): the default, `--only`, the run rule, the preview, the gate, status output, an exit-code table, the JSON shape, and `accept`'s producer line and refusal. The state table was left alone.
  - The frontier hint in [task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md#effective-dependencies).

### Deviations and decisions

- **`OUTPUT_CAP` is defined in `_repro_state.py` (10), not imported.** `_task_validate.OUTPUT_CAP` exists only in the uncommitted `task check --all` edit, so importing it would break this commit on its own. Once that edit lands, replace the local constant with the import.
- **`build --dry-run` applies the gate as well.** It prints the gate message ("the build would run nothing") and exits 1, instead of listing per-step costs that the real build would never incur.
- **The gate skips inputs that a running step writes first.** This includes an online-only output that its producer will overwrite. An absent file that a step produces is not gated, because its producer reads `missing` and runs.
- **The status file list covers selected `unverified` steps too, not only producers.** Absent external inputs stay under "Missing external inputs", so no file is listed twice.
- **Changed step-start message.** The step-start refusal now reads `step 'x' cannot start: N input(s) not on this machine:`, followed by the file list. It replaces 01's single-line `input X is …`.
- **Status column width.** The status column is 10 characters wide, so `unverified` aligns.

### Left for siblings

- **03-state-display.** The dashboard's Build menu still sends `--upstream`, now a no-op. Its plain "Build" therefore includes the producer chain until 03 adds `only` to `_build_args` and the menu. The dashboard status payload carries an all-zero `summary.producers`, because it marks every step selected.
- **04-discipline.** [reproducibility/SKILL.md](../../../../skills/reproducibility/SKILL.md), [review-task/SKILL.md](../../../../skills/review-task/SKILL.md), and [internals.md §Graph actions](../../../../skills/task-tree/references/internals.md) still describe `--upstream` as the way to include producers.

### Verification

- **Regression tests.** [test_repro_upstream.py](../../../../skills/task-tree/scripts/test_repro_upstream.py) has 11 tests, one or more per Validation bullet:
  - default build;
  - target-only `--force`;
  - the gate, online-only and absent;
  - the step-start stop;
  - `accept`, then `status` exiting 3;
  - an accepted consumer rebuilt with identical and with changed producer bytes;
  - the frontier;
  - `--upstream` equal to the default;
  - the `unverified` line;
  - caps and JSON on a 15-step chain.

  The `--only` scoped cases are the existing tests in [test_repro_scope.py](../../../../skills/task-tree/scripts/test_repro_scope.py) and [test_repro_engine.py](../../../../skills/task-tree/scripts/test_repro_engine.py), switched to `--only`. They include a missing saved input that blocks and names its producer.
- **Full suite.** `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts`: 1097 passed, 10 skipped. The run included the uncommitted `task check --all` edits in the working tree.
- **Command-line run on OlinStudio.** A disposable fixture outside the repo had two producers, a consumer, and a step whose dependency is a symlink to the `SF_DATALESS` Box file `~/Library/CloudStorage/Box-Box/ois_historical_data_extended.xlsx`. Results:
  - Default `build 02-use` ran both producers after the preview.
  - After a producer edit, `status 02-use` exited 3 and named it.
  - `build --only --dry-run` had nothing to execute.
  - `build --force` ran the stale producer and the target, but not the fresh producer.
  - `--force --only` ran the target alone.
  - `accept 02-use` named `p-stale (stale)`, and the next `status` exited 3.
  - `build 03-box` and `build 03-box --dry-run` printed the gate shown above and ran nothing.
  - Afterwards the Box file still had `SF_DATALESS` set, with the same size (5,123,878 bytes) and mtime.

