---
title: "reproducibility"
status: not-started
depends_on: []
---

## Objective

You change a helper, a coauthor pushes a fix to the panel builder, or an agent reruns part of the analysis interactively. Afterwards you need to know which tables and figures still come from the code in the repo. superRA tracks this per result: each task declares the commands that produce its results, and superRA records what each command read and wrote at its last successful run. Any later change to those files shows up as a result that is out of date, along with everything downstream of it.

Ask the agent in plain language:

```text
Which results does this edit to the panel builder affect?
Rebuild the GRS table.
What is out of date, and how long would it take to rebuild?
Accept the panel as it is; I checked the row counts against last week's run.
```

The agent answers from those records: it lists the affected steps with their last run times, rebuilds what is cheap, and asks you before a costly rerun. The rest of this page explains the mechanics behind those answers, so you can predict them.

## How superRA decides a result is current

A **step** is one command that reads files (its inputs) and writes files (its outputs). A step is `fresh` when its inputs, its definition (the command and any declared parameters), and its outputs have the same content as at its last successful run. Those content hashes live in `repro-lock.json` at the repo root, which is committed with the work.

- **Content decides, timestamps never do.** A Dropbox re-sync or a `touch` leaves every step fresh, and restoring a file's original bytes restores freshness.
- **Any byte change makes the step stale, even an edited comment.** The hash cannot tell that a comment does not move a result. Whether the step needs a rerun is a separate decision, covered under *What stays your call* below.
- **Staleness flows downstream.** A step reading the output of a stale step is stale too, until its producer is rebuilt.
- **Identical output stops the cascade.** When a rerun writes the same bytes as before, the steps that read those bytes stay fresh and are skipped.
- **Your coauthor's clone sees the same freshness**, because the lock is in git. A check step that passed at the same inputs on another machine reads `fresh` there, with the reason "passed at these inputs … not run here". Outputs you keep out of git are absent from a fresh clone, so their steps read `missing` until built.
- **A merge conflict in the lock does not break it.** Entries both sides agree on still read; the entries they disagree on drop to `missing`, and the next build rewrites the file without conflict markers.

The full list of what invalidates a step, including how Julia `include`s are followed, is in [the task-file contract](skills/task-tree/references/task-file-contract.md#what-invalidates-a-step).

Each step is in one of five states:

| State | Meaning |
|---|---|
| `fresh` | Inputs, definition, and outputs match the last successful run, or a reviewed acceptance. |
| `stale` | An input, an output, the definition, or an upstream step changed. |
| `missing` | Never built, or an output is gone. |
| `failed` | The last run exited non-zero; the status line names the log. Restoring the inputs it last succeeded on can clear it. |
| `external` | An input that no step produces is not on disk, so the step cannot run. |

## A stale cascade on the showcase study

The [showcase study](#/07-showcase) compares CAPM and the Fama-French three-factor model on 25 size/book-to-market portfolios. Its graph has three build steps and one check:

```text
data/download.py  ->  analysis/01_build_panel.py  ->  analysis/02_analysis.py  ->  GRS check
   raw CSVs              ff_panel.parquet             grs_results.csv, figures
   (01-data)             (01-data)                    (02-analysis)
```

Suppose you edit `01_build_panel.py` to start the sample in 1970 instead of July 1963. Then:

| Step | State after the edit | `build showcase-analysis` |
|---|---|---|
| download | `fresh` | skipped |
| build the panel | `stale`: its script changed | reruns |
| analysis | `stale`: upstream step changed | reruns, on the new panel |
| GRS check | `stale`: upstream step changed | reruns, on the new GRS results |

The download does not rerun, because nothing it reads changed. Had the edit only fixed a comment, the same three steps would read `stale`. Accepting the panel step, with the comment-only diff as the reason, returns all three to `fresh`, since the panel file itself did not change. Rebuilding the panel instead also ends there if the new file is byte-identical: the analysis and the check are skipped.

Building only `showcase-analysis/02-analysis` after the 1970 edit reruns nothing: the analysis reads the panel file that is on disk, which still covers 1963 onward. `status` on that selection reports the panel step as a producer behind it that is not fresh, and `--upstream` brings it into the build.

## What runs, and when

**Nothing reruns on its own.** `status` reports states and never runs anything; `build` runs steps, and only when you or the agent asks.

- **`build <target>` runs only the selected steps that are not fresh**, in dependency order. A target is a task path (the task and its subtasks), one step as `task#step`, or `.` for the whole tree.
- **Files written by steps outside the selection are used as they sit on disk.** `--upstream` adds the steps that produce them, back to the external inputs.
- **The cost comes first if you ask for it.** `build --dry-run` lists what would run with each step's last run time; `impact <file>` lists which steps a change to that file would make stale.
- **A failure stays local.** A failed step skips the steps below it while unrelated steps continue. A missing input fails only the build that reads it; tasks that read it still appear on the frontier, with the input flagged.

## What stays your call

**Acceptance records a result as reviewed instead of rerunning it.** It marks the selected steps `fresh` at their current files, requires a reason, and writes one committed record per step under `repro-acceptance/`. It never claims the step ran: `status` shows "reviewed baseline", and the last actual run stays on record. The acceptance lapses as soon as any input, output, or the definition changes again.

Use it for an expensive result you already produced from the same committed code, for example in an interactive session, or for a change you have read and know cannot move the result.

For every step that is not fresh, the agent rebuilds cheap steps, accepts on its own only when the diff proves the change cannot move a result (a comment, whitespace, a logging line), and asks you before a costly rerun, with a recommendation. The rule is in [rerun-or-accept.md](skills/reproducibility/references/rerun-or-accept.md).

## The `## Reproduction` section

Each task declares its steps in a `## Reproduction` section. The agent writes it; you read it to see what produces what. One step from the showcase's data task, for example:

```yaml
steps:
  - name: build-panel
    cmd: uv run --script superRA/showcase-analysis/analysis/01_build_panel.py
    deps:
      - superRA/showcase-analysis/analysis/01_build_panel.py
      - superRA/showcase-analysis/data/raw
    outs:
      - superRA/showcase-analysis/data/ff_panel.parquet
```

`deps` are the inputs, `outs` the outputs; a step with `kind: check` has no outputs and reruns when its inputs change. The schema is in [the task-file contract](skills/task-tree/references/task-file-contract.md#reproduction-section).

## Commands

The agent runs these. You can run them yourself through `./superRA/superra` to inspect or drive the graph:

```bash
./superRA/superra repro status .                                  # every step's state
./superRA/superra repro impact superRA/showcase-analysis/analysis/01_build_panel.py
./superRA/superra repro build showcase-analysis --dry-run         # what would run, and its last cost
./superRA/superra repro build showcase-analysis/02-analysis --upstream
./superRA/superra repro explain showcase-analysis/01-data         # what changed, and what to run next
./superRA/superra repro accept showcase-analysis/01-data --reason 'Comment-only edit; diff reviewed'
```

The [dashboard](#/04-utility-skills/01-task-tree/04-dashboard) shows each step's state and last run in its graph view. Flags and output formats are in [commands.md](skills/task-tree/references/commands.md#reproduction); when to register a step, rerun, or accept is in the [reproducibility skill](skills/reproducibility/SKILL.md).
