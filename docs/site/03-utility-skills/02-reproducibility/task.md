---
title: "reproducibility"
status: not-started
depends_on: []
---

## Objective

superRA tells you which tables and figures still come from the code in your repo. Each task declares the commands that produce its results, and superRA records what each command read and wrote at its last successful run. After you edit a helper, pull a coauthor's fix, or rerun part of the analysis by hand, any result whose files changed shows as out of date, along with everything downstream of it.

Ask the agent in plain language:

```text
Which results does this edit to the panel builder affect?
Rebuild the GRS table.
What is out of date, and how long would it take to rebuild?
Accept the panel as it is; I checked the row counts against last week's run.
```

The agent lists the affected steps with their last run times, rebuilds what is cheap, and asks you before a costly rerun.

## A result is current when its files match its last run

A **step** is one command that reads files (its inputs) and writes files (its outputs). Its state:

| State | Meaning |
|---|---|
| `fresh` | Inputs, definition (the command and any declared parameters), and outputs match the last successful run, or a reviewed acceptance |
| `stale` | An input, an output, the definition, or an upstream step changed |
| `missing` | Never built, or an output is gone |
| `failed` | The last run exited non-zero; the status line names the log |
| `unverified` | This machine cannot check one of its files without downloading or obtaining it; a build never runs it |

- **Content decides, timestamps never do.** A Dropbox re-sync or a `touch` leaves a step fresh; restoring a file's original bytes restores freshness.
- **Any byte change makes the step stale, even an edited comment.** Whether it needs a rerun is your call or the agent's (see *Accepting a result* below).
- **Staleness flows downstream** until the producer is rebuilt. A rerun that writes byte-identical output stops the cascade.
- **An external input is a file no step produces,** such as a vendor download or a frozen data release. Replacing it makes every step that reads it stale.
- **Your coauthors see the same states.** The content hashes live in `repro-lock.json` at the repo root, committed with the work. Outputs kept out of git read `missing` in a fresh clone until built.

The full list of what invalidates a step, including how Julia `include`s are followed, is in [the task-file contract](skills/task-tree/references/task-file-contract.md#what-invalidates-a-step).

## Example: an edit to the showcase panel builder

The [showcase study](#/06-showcase) has two build steps and one check, all reading two committed Ken French CSVs (an external input):

```text
data/raw/*.csv  ->  build-panel       ->  estimate-test-plot        ->  check-grs-headline
external input      ff_panel.parquet      grs_results.csv, figures      kind: check
                    (01-data)             (02-analysis)                 (02-analysis)
```

Edit `01_build_panel.py` to start the sample in 1970 instead of July 1963:

| Step | State after the edit | `build showcase-analysis` |
|---|---|---|
| `build-panel` | `stale`: its script changed | reruns |
| `estimate-test-plot` | `stale`: upstream step changed | reruns on the new panel |
| `check-grs-headline` | `stale`: upstream step changed | reruns on the new GRS results |

Had the edit only fixed a comment, the same three steps would read `stale`. Two ways end it:

- **Accept** the panel step, with the comment-only diff as the reason: all three return to `fresh`.
- **Rebuild** the panel: the new file is byte-identical, so the analysis and the check are skipped.

## Builds run only when asked

`status` reports states and never runs anything. `build` runs steps, and only when you or the agent asks.

- **Name the result you want; the build brings its inputs current first.** `build <target>` runs the steps that are not fresh among the target and the steps producing its inputs, back to the external inputs. A target is a task path (with its subtasks), one step as `task#step`, or `.` for the whole tree.
  - `--only` keeps the build to the target and uses upstream files as they sit on disk.
- **See the cost first.** `build --dry-run` lists what would run with each step's last run time; `impact <file>` lists the steps a change to that file would make stale.
- **Nothing is downloaded.** superRA never opens an online-only file (Dropbox, Google Drive, Box, OneDrive, iCloud). A build that needs one runs nothing and names it, and the agent asks you before downloading.

## Accepting a result instead of rerunning it

`accept` marks steps `fresh` at their current files without running them. It requires a reason and writes one committed record per step under `repro-acceptance/`.

- **Use it** for an expensive result already produced from the same committed code, such as in an interactive session, or for a change you have read and know cannot move the result.
- **It never claims a run.** `status` shows "reviewed baseline" and keeps the last actual run on record.
- **It lapses** as soon as an input, an output, or the definition changes again.

The agent accepts on its own only when the diff proves the change cannot move a result (a comment, whitespace, a logging line). Otherwise it rebuilds cheap steps, asks you before costly ones, and leaves a script private to one task's `attachments/` stale and tells you. The rule is in [rerun-or-accept.md](skills/reproducibility/references/rerun-or-accept.md).

## Reading the `## Reproduction` section

The agent writes each task's steps in its `## Reproduction` section; read it to see what produces what. The showcase's data task:

```yaml
steps:
  - name: build-panel
    runner: uv
    script: superRA/showcase-analysis/analysis/01_build_panel.py
    deps:
      - superRA/showcase-analysis/data/raw/F-F_Research_Data_Factors.csv
      - superRA/showcase-analysis/data/raw/25_Portfolios_5x5.csv
    outs:
      - superRA/showcase-analysis/data/ff_panel.parquet
```

- `runner: uv` names a command template in `superRA/config.yaml`, here `uv run --script {script}`; the script counts as an input automatically.
- `deps` are the other inputs, `outs` the outputs. A `kind: check` step has no outputs and reruns when its inputs change.

The schema is in [the task-file contract](skills/task-tree/references/task-file-contract.md#reproduction-section).

## Commands

The agent runs these; you can run them through `./superRA/superra` to inspect or drive the graph:

```bash
./superRA/superra repro status .                                  # every step's state
./superRA/superra repro impact superRA/showcase-analysis/analysis/01_build_panel.py
./superRA/superra repro build showcase-analysis --dry-run         # what would run, and its last cost
./superRA/superra repro build showcase-analysis/02-analysis --only  # the analysis alone, on the panel as it is
./superRA/superra repro explain showcase-analysis/01-data         # what changed, and what to run next
./superRA/superra repro accept showcase-analysis/01-data --reason 'Comment-only edit; diff reviewed'
```

The [dashboard](#/03-utility-skills/01-task-tree) graph view shows each step's state and last run. Flags are in [commands.md](skills/task-tree/references/commands.md#reproduction); when to register, rerun, or accept a step is in the [reproducibility skill](skills/reproducibility/SKILL.md).
