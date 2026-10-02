---
title: "Skill, References, and Docs Teach the Producer Chain and Online-Only Data"
status: approved
depends_on: [02-upstream-default]
---

## Objective

Rewrite the agent-facing and reader-facing instructions for the behavior [01-local-graph](../01-local-graph/task.md) and [02-upstream-default](../02-upstream-default/task.md) ship. An agent should name the result it wants current and let the build find the stale producers. When a step needs online-only data, the agent reports it and downloads only on the researcher's go-ahead.

- **[reproducibility SKILL.md](../../../../skills/reproducibility/SKILL.md).**
  - §The Graph: `unverified` (this machine cannot check a file without downloading it), and no `external` state.
  - §Selecting Steps:
    - Targets include their producer chain, and `--only` uses files from outside the selection as they sit on disk.
    - Builds skip fresh steps, so name the task or the final result, not each stale step.
    - When another session is editing a producer in this worktree, use `--only`.
  - §Commands table: match the new default.
  - §Recording a Result:
    - Plain `status` covers the chain.
    - A result checked with `--only`, or one resting on `unverified` steps, says so in `## Results` and names where tracing stopped.
    - A selected step must itself read `fresh`.
- **[online-only-files.md](../../../../skills/reproducibility/references/online-only-files.md)** (added in `4bc5396c`; the CLI points here). Update it for what 01 and 02 ship: an online-only file now reads unknown and its step `unverified`, the gate's message, and `--only` as the way past the gate.
- **[rerun-or-accept.md](../../../../skills/reproducibility/references/rerun-or-accept.md) and [protect-and-completion.md](../../../../skills/reproducibility/references/protect-and-completion.md).**
  - Acceptance stays step-local: to cover a producer, name it.
  - The `--dry-run` cost now includes stale producers.
  - Accept the steps the stale rule sets aside before building the rest, or build with `--only`; a default build would rerun them. protect-and-completion.md line 8 ("building by name only the steps the rule says to run") states the scoped assumption.
  - The completion check reports every `unverified` step to the researcher, with the files that need downloading. It never treats them as verified just because `status` exits 0.
- **[adoption.md](../../../../skills/reproducibility/references/adoption.md).** In an adopted project, a producer that has never been built reads `missing`, even when its outputs exist, so a default downstream build runs it. Accept or build such producers first, or use `--only`.
- **[review-task SKILL.md](../../../../skills/review-task/SKILL.md) line 28.** The evidence command becomes plain `status`.
- **Docs site.** The [reproducibility page](../../../../docs/site/04-utility-skills/09-reproducibility/task.md) describes the default, `--only`, and `unverified`. The dashboard page belongs to [03-state-display](../03-state-display/task.md).
- **[RELEASE-NOTES.md](../../../../RELEASE-NOTES.md) 0.5.0.**
  - Describe the default, `--only`, `unverified`, the download gate, and the removal of `external`.
  - Note that `status X --upstream` now exits 3 instead of 1 when only a producer is stale.

### Validation

- Apply the [CLAUDE.md](../../../../CLAUDE.md) §Teach the Protocol three tests line by line to every changed `skills/*` line, then §Skill Prose Style. Load `skill-creator` before editing any `SKILL.md`.
- Two realistic harness sessions on disposable fixtures. Record the command each agent issued:
  - Stale producers in two tasks feed a final step. Asked to bring the final result current, the agent issues one target build, not a list of every stale step.
  - A step that must run reads a file shown as online-only. The agent reports the file and its size to the researcher instead of downloading it.
- `git grep -E -- '--upstream|saved input|upstream producer|external'` outside `docs/plans/` and historical `## Results` finds no instruction that still states the scoped default or the `external` state.

## Results
The reproducibility skill, its references, the reviewer's evidence line, the docs page, and the 0.5.0 release notes now teach the producer-chain default, `--only`, and `unverified`. No remaining instruction states the scoped default or the `external` state, outside 03's files. In two harness sessions on disposable fixtures, an agent asked to bring a final result current issued one target build. An agent whose build needed an online-only file reported the file and its size and downloaded nothing.

### What each file now says

- **[reproducibility SKILL.md](../../../../skills/reproducibility/SKILL.md).**
  - §The Graph defines `unverified`: this machine cannot check a file without downloading or obtaining it, and `build` never runs the step.
  - §Selecting Steps: `build` and `status` take in the producer chain. Name the task or the final result, not each stale step. `--only` restricts to the targets, uses saved inputs as they sit on disk, and is the choice when another session is editing a producer in this worktree.
  - §Commands: `status` lists the producers behind the selection that are not `fresh`, and `build` runs the `stale`, `missing`, and `failed` steps among the targets and their producers.
  - §Recording a Result: a step behind a `stale`, `missing`, or `failed` producer reads `stale`. A selected step reading `unverified` fails the gate even though `status` exits 0. A result checked with `--only`, or one resting on `unverified` producers, says so and names where tracing stopped.
- **[rerun-or-accept.md](../../../../skills/reproducibility/references/rerun-or-accept.md).**
  - The `--dry-run` cost includes stale producers.
  - An `unverified` step is outside the stale rule. Report it with the files `status` lists. For an absent external input, retrieve it or register its producer.
  - **Record the rule's acceptances before you build.** While a producer stays stale by the rule, build with `--only`.
  - Under "What acceptance never covers", producers you did not name: to cover one, name it or build it.
- **[protect-and-completion.md](../../../../skills/reproducibility/references/protect-and-completion.md).**
  - Step 2 no longer says "building by name only the steps the rule says to run"; rerun-or-accept.md now owns build scope.
  - The gate passes with stale-rule leftovers and every `unverified` step reported to the researcher. `status .` still exits 0 over the `unverified` steps.
  - For fresh execution, `--force` names every step to rerun (`.` for all).
- **[online-only-files.md](../../../../skills/reproducibility/references/online-only-files.md).** A new first section, **superra Never Downloads**:
  - an uncached online-only file reads `changed` when its size differs from the lock's, and `unknown` otherwise;
  - a build refuses while a step it would run reads an online-only file, even a cached one;
  - `--only` builds the steps that read none.

  §Ask First takes sizes from `status`.
- **[adoption.md](../../../../skills/reproducibility/references/adoption.md).**
  - A declared producer that was never built reads `missing` even with its outputs on disk. Accept or build it first, or build the slice with `--only`.
  - The one-task trial reads "named inputs" instead of "named saved or external inputs".
- **[review-task SKILL.md:28](../../../../skills/review-task/SKILL.md#L28).** The evidence command is plain `superra repro status <targets>`.
- **[Docs reproducibility page](../../../../docs/site/04-utility-skills/09-reproducibility/task.md).**
  - Staleness follows the producer chain, and `unverified` replaces `external` in the state table.
  - The showcase walk-through and §What runs describe the default, `--only`, and the no-download rule.
  - The command block uses `--only` where it used `--upstream`.
- **[RELEASE-NOTES.md](../../../../RELEASE-NOTES.md) 0.5.0.**
  - "Task-scoped builds by default" became **Builds include the producer chain by default**. It covers `--only`, target-only `--force`, `--upstream` as a hidden alias, and `status X --upstream` exiting 3 instead of 1 when only a producer is stale.
  - A new **No command downloads a file** bullet covers `unverified` and the download gate.
  - **Removed** lists the `external` state.
  - The completion-gate bullet adds `unverified` steps.

### Deviations

- **The download go-ahead lives only in online-only-files.md §Ask First.** rerun-or-accept.md says to report an `unverified` step and does not restate the download rule. Both the SKILL.md routing row and the CLI's gate message point to online-only-files.md.
- **adoption.md's one-task trial line changed.** It was outside the listed edits, but "saved inputs" assumed the scoped default.

### Verification

- **Instruction gate.** I applied the CLAUDE.md three tests and §Skill Prose Style line by line. This cut two restatements from SKILL.md, the "builds skip `fresh` steps" rationale and the "plain `status` covers the producer chain" sentence that §Selecting Steps already carried. It also cut the download rule duplicated in rerun-or-accept.md. The review then found three same-file restatements in the references, now cut. SKILL.md went from 741 to 824 words.
- **Harness session A: stale producers in two tasks.**
  - The fixture has `01-left` and `02-right`, each with one step, feeding `final` in `03-final`. After both scripts were edited, `status 03-final` exited 3.
  - Asked to "bring the final wage table up to date", the agent ran `build 03-final --dry-run`, then `build 03-final`, which executed all three steps. It issued no per-step builds.
  - That session may have run before the last SKILL.md cuts. A second session ran on the final skill text, the text committed in the fix-round implement commit after review `0613a929`. Both scripts had been edited again, and the request was "I tweaked both cleaning scripts again. Can you get the final wage table current?" The agent read SKILL.md and rerun-or-accept.md. It ran `build final --dry-run`, then `build final`, which reran all three steps, and it used neither `accept` nor `--only`.
- **Harness session B: an online-only input.**
  - The fixture's `rates` step reads a symlink to the `SF_DATALESS` Box file `~/Library/CloudStorage/Box-Box/ois_historical_data_extended.xlsx`. `rates` and `calendar` feed `model`, and none has been built.
  - Asked to rebuild the model results, the agent ran `build 03-model --dry-run` and hit the gate. It then built only `calendar` with `build 02-calendar --only`. Its message to the researcher named `data/ois_history.xlsx` (5.1 MB), said downloading is the researcher's call, and asked for the go-ahead.
  - The session ran before the rerun-or-accept.md download clause was cut. A second session ran on the final text, with `calendar` already fresh and the request "The term-structure model results are out of date. Rebuild them, please." It read SKILL.md, rerun-or-accept.md, and online-only-files.md. Its commands were `status .`, `build . --dry-run`, `explain .`, `status 03-model`, and `impact data/ois_history.xlsx`. It built nothing, and it asked for the go-ahead to download the 5.1 MB file.
  - After both sessions, the Box file still had `dataless` set.
- **Grep.** `git grep -E -- '--upstream|saved input|upstream producer|external'` outside `docs/plans/` and `superRA/` finds:
  - in release notes and `commands.md`, only the hidden-alias and exit-code notes;
  - "external input" as the name for a file no step produces;
  - `--only`-scoped saved-input lines;
  - the files 03-state-display owns: [internals.md §Graph actions](../../../../skills/task-tree/references/internals.md), `dashboard.js`/`dashboard.css`, and the [dashboard docs page](../../../../docs/site/04-utility-skills/01-task-tree/04-dashboard/task.md).
