---
name: reproducibility
description: Register and verify task-declared reproduction graphs. Use when planning, producing, changing, recording, or reviewing retained results that depend on executable steps, writing drift tests or validation scripts, adopting reproduction, deciding external inputs at Protect, or judging whether to rerun or accept a stale result.
---

# Reproducibility

Every retained result reruns from committed code through a graph of declared steps. After any change, the graph shows which results are out of date, and [the stale rule](references/rerun-or-accept.md#the-stale-rule) decides whether to rerun, accept, or report each one.

## The Graph

- **A step is one command that reads files (`deps`) and writes files (`outs`).** Each task declares its steps in its `## Reproduction` section ([schema and invalidation rules](../task-tree/references/task-file-contract.md#reproduction-section)).
  - **Producer** — a step whose `outs` include another step's `deps`.
  - **External input** — a dep no step produces: a licensed data extract, a frozen upstream artifact, a hand-curated file. The researcher agrees which inputs are external.
- **A step is `fresh` when its deps, definition (command and `params`), and outs still match the hashes recorded at its last successful run** in the committed `repro-lock.json`. A step accepted with `superra repro accept` is also `fresh`, without rerunning.
  - Any byte change makes a step stale, even an edited comment that cannot move the result. The stale rule, not the hash, decides whether it needs a rerun.
- **A step is `unverified` when this machine cannot check one of its files without downloading or obtaining it:** online-only and not yet hashed here, unreadable, or an absent external input. `build` never runs it and uses its outputs as they are.

## Selecting Steps

Every command acts on the steps its targets select:

- a task path — that task's steps and its subtasks' steps;
- `task#step` — one step;
- `.` — every step in the tree.

**`build` and `status` also take in the targets' producer chain:** the step that writes each file a selected step reads, the steps that write its deps, and so on back to the external inputs. Suppose `03-table` reads `panel.parquet`, which a step in `02-merge` writes: `build 03-table` first rebuilds `panel.parquet` when its producer is stale.

- **Name the task or the final result, not each stale step.**
- **`--only` restricts a command to its targets.** A file written by a step outside them is a saved input, used as it sits on disk. Use `--only` when another session is editing a producer in this worktree.

## Commands

| Command | Does |
|---|---|
| `superra task check` | Validates every `## Reproduction` declaration, including cycles. |
| `superra repro status <targets>` | Each selected step's state (`fresh`, `stale`, `missing`, `failed`, `unverified`), the producers behind them that are not `fresh`, and `outside readers`: how many steps in other tasks read its outs. |
| `superra repro build <targets>` | Runs the `stale`, `missing`, and `failed` steps among the targets and their producers. `--dry-run` lists what would run and how long each step last took. |
| `superra repro explain <target>` | For each changed hash, what changed and the command to run next. |
| `superra repro impact <path...>` | Which steps a change to these paths would make stale, and how long each last took. |
| `superra repro accept <targets> --reason '...'` | Records the current results as reviewed, without running anything. |

Other flags: `superra repro <command> --help`.

## Recording a Result

`[BLOCKING]` **Record a result in `## Results` only after `superra repro status <targets>` shows every selected step `fresh`.** A step behind a `stale`, `missing`, or `failed` producer reads `stale`. A selected step reading `unverified` fails this gate, though `status` exits 0.

1. **Produce the result through the graph:** `superra repro build <targets>`, or [accept](references/rerun-or-accept.md#accept) a result already produced from the same committed code, such as by an interactive run.
2. **In `## Results`, state what the evidence covers:** the targets, the external inputs they read, the outcome of each check step, and which steps ran versus which were accepted. A result checked with `--only`, or resting on `unverified` producers, says so and names where tracing stopped: the saved inputs, or the `unverified` boundary `status` prints.
3. **Commit the changed `repro-lock.json` and `repro-acceptance/` records with the work.**

## Where to Go Next

| Load | When |
|---|---|
| [designing-the-graph.md](references/designing-the-graph.md) | Writing or registering retained code, including drift tests and validation scripts; planning, moving, or retiring steps. |
| [rerun-or-accept.md](references/rerun-or-accept.md) | A step is not `fresh`, including an input that `task read` or `task frontier` flags before you build on it. |
| [protect-and-completion.md](references/protect-and-completion.md) | The IMPLEMENT completion check, or `Stage: protection`. |
| [diagnosing.md](references/diagnosing.md) | A state you did not expect. |
| [adoption.md](references/adoption.md) | Adopting reproduction: a whole existing project, or a first one-task trial. |
| [online-only-files.md](references/online-only-files.md) | A file a step reads or writes is online-only on this machine (Dropbox, Google Drive, Box, iCloud), or you are about to download one. |
