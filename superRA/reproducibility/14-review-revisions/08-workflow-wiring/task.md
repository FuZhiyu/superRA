---
title: "Workflow Call Sites Apply the Reproduction Gates Consistently"
status: approved
depends_on:
  - 07-instruction-rewrite
---

## Objective

Every workflow step that touches reproduction points to the reproducibility skill for the rule, applies its gates in the right order, and uses 07's terms. An agent loading only what the Skill-Load Manifest names then acts correctly in both interactive and autonomous mode. The steps in scope are planning, the IMPLEMENT completion check, INTEGRATE, and the implementer and reviewer roles.

### The completion check asks before costly reruns

- **Status first, then the stale rule, then build.** [completion.md:18](../../../../skills/superimplement/references/completion.md#L18), [integrate.md:9](../../../../skills/superintegrate/references/integrate.md#L9), and [finish.md:39](../../../../skills/superintegrate/references/finish.md#L39) run `repro build <targets> --upstream` first, which executes every stale producer, including costly ones the stale rule says to ask the researcher about. In autonomous mode, a subagent correctly escalates a costly rerun, and the completion check then runs it anyway.
  - Order the check: `status`; the stale rule, with cost from `build --dry-run`'s recorded durations; then `build`.
  - Run it over the whole tree (`.`), not a target list ([07](../07-instruction-rewrite/task.md) drops completion targets).
  - Add the costly-rerun question to `main-agent.md` §Proceeding and Pausing.
  - One file holds the commands; the other two point to it.
- **Trees with no reproduction steps pass.** `repro status` and `build` exit 1 with "selects no steps", and `completion.md` treats that as a failure, so a theory or prose-only tree cannot finish. State the condition and its fallback once, in `protect-and-completion.md`. Today it is worded three ways: [main-agent.md:10](../../../../skills/using-superra/references/main-agent.md#L10), `using-superra/SKILL.md` §Task Interface, and `finish.md:39`.

### Planning produces valid steps

- [build-and-review.md:13](../../../../skills/superplan/references/build-and-review.md#L13) tells the planner to seed each producing task's `## Reproduction` section with its outputs only. A step without `cmd` is an error, so `task check`, `task frontier`, and `task create` then fail. Either seed name, command, and outputs, or keep the planned artifacts in `## Details` for the implementer; reconcile with [task-file-contract.md:29](../../../../skills/task-tree/references/task-file-contract.md#L29), which makes the section implementer-owned.

### Every role loads and applies the gates

- **The manifest carries the load trigger.** The trigger to load `reproducibility` is a prose sentence in `using-superra/SKILL.md` §Task Interface; the Skill-Load Manifest, CLAUDE.md §Agent Load Surface, and the harness load contract do not list it. Add a Domain row: load when a task produces, changes, or reviews a result from executable code.
- **Interactive self-review applies the gates.** In the default interactive mode, [interactive-mode.md:17](../../../../skills/using-superra/references/interactive-mode.md#L17) self-reviews against "active domain skills" only, so the reproducibility gates are skipped.
- **Role skills point instead of restating.** [implement-task:50](../../../../skills/implement-task/SKILL.md#L50) and [review-task:28](../../../../skills/review-task/SKILL.md#L28) paraphrase the gates.
- **Reviewers check evidence.** `review-task` drops the stale-step gate and names no evidence. A review item covers every gate and names the evidence: `status <targets> --upstream` output and the committed `repro-lock.json` and acceptance records.
- **One escalation status** for a costly stale step a subagent cannot resolve. Today it could be BLOCKED or DONE_WITH_CONCERNS.

### Parallel work, Sync, and Protect handle the records

- **Merges of the committed records have guidance.** [parallel-dispatch.md:15](../../../../skills/agent-orchestration/references/parallel-dispatch.md#L15) promises parallel branches "typically merge cleanly", but every branch writes the same root records. `semantic-merge` gets resolution guidance for `repro-lock.json` and for the acceptance format [02](../02-portable-records/task.md) settles, and implement-task's commit guidance names the records.
- **A conflicted `repro-lock.json` resolves itself.** Two branches that each register a new step whose names sort next to each other conflict in the lock (merging 02 and 06 did, on `layout-equivalence-check` and `portable-records-check`). Entries are per step, so the union is the resolution. `superra repro` reads a lock holding conflict markers by keeping every entry that is on one side or identical on both, dropping entries that differ so their steps read `missing`, and warning; `semantic-merge` then only says to rebuild what reads missing and commit the lock.
- **Protect keeps no target list.** Today [protect-and-completion.md](../../../../skills/reproducibility/references/protect-and-completion.md) has Protect name completion targets and record them in the `integrate(protect)` commit body, the only place they live. With the completion check covering the whole tree, nothing needs recording: selected checks are registered check steps, and `status` reports external inputs as `external`. The researcher still agrees at Protect which inputs are external.

### One name per concept, and a current harness contract

- **Terminology.** A result's importance is its position in the task DAG, so no call site names a class of important results. "Completion targets" and "final deliverable tasks" go from [completion.md](../../../../skills/superimplement/references/completion.md) and `protect.md`. The results the researcher picks for drift tests at Protect keep one name, "key result", as in `result-protection`; `protect.md` and [result-protection/SKILL.md:23](../../../../skills/result-protection/SKILL.md#L23) say "kept result" instead. "Retained" keeps its separate meaning of a file that is not scratch.
- **Harness contract.**
  - `load_contract.json` anchors are two lines off since `3a548e98`, so LC008 lands on the planning-review row.
  - LC008 cites model text instead of routing.
  - `ALL_STAGE_SKILLS` counts a correct conditional load of `reproducibility` at `Stage: implementation` as an over-load.
  - The protection row is not yet verified in a live run.

### Validation

A realistic harness session walks the three scenarios in [wiring.md](../attachments/wiring.md):

1. An implementer on an econ task produces a regression table from a new script.
2. A subagent edits a shared helper that fans out to a costly estimation.
3. The main agent runs the completion check and Protect on a tree with a check step.

The harness-instruction-following tests pass.

Owning task: [unified-dependency-workflow](../../07-workflow-integration/unified-dependency-workflow/task.md).

## Details

From 07's review, for this task:

- `protect.md:30`'s commit-body list does not name external inputs, so the researcher's agreement on them is recorded nowhere; add it.
- CLAUDE.md §Ownership Boundaries still says "boundary inputs"; use 07's terms (saved input, external input).
- 07's call-site leftovers: `implement-task/SKILL.md:50` and `review-task/SKILL.md:28` point to the removed `reproducibility` §Gates; `load_contract.json:220` cites `SKILL.md#L12-L18`; `using-superra` restates "registration follows placement".
- Point `implement-task`'s reproduction line at 07's [claiming-results.md](../../../../skills/reproducibility/references/claiming-results.md).
- From 07's harness run: `implement-task` limits edits to `task.md` files, yet a registered step's outputs and `repro-lock.json` are committed with the work; and no Skill-Load Manifest domain row clearly covers tabulating an existing script's output.

Smaller prose fixes from [wiring.md](../attachments/wiring.md):

- `completion.md` §Verify Pipeline and Reproducibility still says "Pipeline", and `econ-data-analysis/SKILL.md:151` cites it.
- `integrate.md:9` "among them" has no clear referent.
- `CATEGORIES.md:52` states the load trigger more narrowly than `using-superra`.
- `changing-the-tree.md:42` points to §What earns a step for moves and removals, which §Step lifecycle covers.
- `result-protection/SKILL.md:8` counts "a registered step with its committed lock" as protection; only a check step guards values.
- `completion.md:19` "not ad-hoc REPL state" sits against accepting results from interactive runs.
- `main-agent.md:10` routes the session-start status through the stale rule, implying builds before the first response.

## Results

Every workflow step that touches reproduction now points to the one reference that owns its rule, and the completion check asks before costly reruns. Three live sessions walked the [wiring.md](../attachments/wiring.md) scenarios and each applied the gates in order. The lock now holds one line per step, so a merge can no longer mix two builds into one entry, and a conflicted lock reads instead of failing.

### The completion gate has one home and asks first

- [protect-and-completion.md §The completion gate](../../../../skills/reproducibility/references/protect-and-completion.md#the-completion-gate) holds the commands: `status .`, then the whole [rerun-or-accept.md](../../../../skills/reproducibility/references/rerun-or-accept.md) (its dry-run cost and `explain` pre-step, then the stale rule), then `status .` again.
  - [completion.md](../../../../skills/superimplement/references/completion.md), [integrate.md](../../../../skills/superintegrate/references/integrate.md) Step 1, and [finish.md](../../../../skills/superintegrate/references/finish.md) Step 2 only point to it. None runs `build <targets> --upstream` any more.
  - [main-agent.md §Proceeding and Pausing](../../../../skills/using-superra/references/main-agent.md#proceeding-and-pausing-in-the-autonomous-mode) lists "a costly rerun the stale rule sends to the researcher" among the pre-set gates.
- **Trees with no steps** are stated once, in the gate: they pass only when no `## Results` rests on retained code; otherwise register the producers. The three other wordings are gone. The session-start line in `main-agent.md` reports the steps that are not `fresh` and reads "selects no steps" as nothing to report.
- **Protect keeps no target list.** [protect.md](../../../../skills/superintegrate/references/protect.md) asks which inputs are external, adds an `External inputs:` line to the researcher template, and records "agreed external inputs" in the `integrate(protect)` commit body.

### Planning names artifacts; the implementer registers steps

[build-and-review.md](../../../../skills/superplan/references/build-and-review.md) now has the planner name each artifact and its planned script in the producing task's `## Details`, and self-review item 3 checks that each artifact is named. No seeded step can then lack `cmd`, and [task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md#task-anatomy) keeps `## Reproduction` implementer-owned without an exception.

- **Why not seed `name`, `cmd`, `outs`:** seeded steps read `missing` before any work. The session-start report and the stale rule would then treat unbuilt plans as steps to resolve.
- The econ and theory planning references are rewritten to match, with "retained output" as the threshold.

### Every role loads and applies the gates

- **Manifest row.** [using-superra](../../../../skills/using-superra/SKILL.md#domain) has a `reproducibility` Domain row: a task that "plans, produces, changes, records, or reviews a result computed by code — a new script, an edited one, or an existing script's output". The §Task Interface prose trigger and its "registration follows placement" restatement are removed.
  - CLAUDE.md §Agent Load Surface needed no edit: its "Domain skill(s) per the manifest" row now covers the load.
  - [CATEGORIES.md](../../../../skills/CATEGORIES.md) points to the manifest instead of its narrower trigger.
- **Interactive self-review.** [interactive-mode.md](../../../../skills/using-superra/references/interactive-mode.md) step 2 now walks every loaded skill's gates, not just domain skills'.
- **Implementer.**
  - [implement-task](../../../../skills/implement-task/SKILL.md) Self-Check 4 points to `claiming-results.md`.
  - Hygiene limits only *task-file* edits to assigned tasks.
  - The `git add` template names tracked outputs and changed `repro-lock.json` / `repro-acceptance/`.
- **Reviewer.** [review-task](../../../../skills/review-task/SKILL.md) names all three gates by their references and the evidence: read-only `status <targets> --upstream` and the committed records.
- **One escalation status.** [rerun-or-accept.md](../../../../skills/reproducibility/references/rerun-or-accept.md#the-stale-rule) says a subagent returns `DONE_WITH_CONCERNS` with the question in `## Results`; `implement-task` §Escalation and `superimplement` §Autonomy and Stop Points name that exception and point there. The status keeps the finished work committed, where `BLOCKED` would drop it.

### A merge cannot make a lock entry read falsely fresh

- **One line per step.** [_repro_state.py](../../../../skills/task-tree/scripts/_repro_state.py) writes `repro-lock.json` as version 2: each step's entry on one line with sorted keys, steps in name order, a blank line between entries.
  - Git merges whole lines, so an entry both branches changed always conflicts; a clean merge can only take each entry whole from one side.
  - The blank lines let changes to neighbouring entries merge cleanly, so branches that rebuild different steps still merge without conflict.
  - A version 1 lock (one key per line) still reads, and the next real build rewrites it; `explain`'s lock history reads both layouts.
- **Conflicted lock.** The reader keeps each entry on one side or identical on both and drops entries the sides disagree on, so their steps read `missing`, with a warning. Any real build rewrites the lock without markers.
- **Acceptance records need no change.** Every accept rewrites the record's sealing `id` line, so two branches accepting one step conflict on it, or line-merge into a record whose `id` no longer matches. Either way the record is set aside.
- **Tests** in [test_repro_engine.py](../../../../skills/task-tree/scripts/test_repro_engine.py), run by `engine-freshness-check`:
  - The review's reproduction through a real `git merge`: `check-m` reads four deps, and the branches edit `m1` and `m4` and rebuild it. It is run once with adjacent new steps (a conflicted merge) and once without (a would-be-clean merge). `check-m` reads `missing`, and building it fails as the merged tree warrants. Both cases read `fresh` under the old layout.
  - The adjacent-new-steps conflict, the changed-on-both-sides case through `git merge-file` (merge and diff3 styles), the version 1 read-and-rewrite, `explain` across the layout switch, and two same-step acceptances merged.
- **Guidance.** [semantic-merge](../../../../skills/semantic-merge/SKILL.md) gains a "Reproduction records" role that states what the reader keeps and drops. It says to resolve the `missing` steps by the stale rule and commit the lock a build rewrites; a conflicted acceptance record accepts nothing and is removed. [parallel-dispatch.md](../../../../skills/agent-orchestration/references/parallel-dispatch.md) no longer promises clean merges and points there. [internals.md](../../../../skills/task-tree/references/internals.md#the-lock) records the layout and both merge guarantees.

### Terms and small fixes

- **Terms.**
  - "Completion targets" and "final deliverable tasks" are gone from every call site.
  - `protect.md` and [result-protection](../../../../skills/result-protection/SKILL.md) say "key result".
  - CLAUDE.md and CATEGORIES.md say external (and saved) inputs, not "boundary inputs".
- **Result protection.** `result-protection` counts drift tests "registered as check steps", not a lock, as protection.
- **Completion check.** In `completion.md`, "Verify Pipeline and Reproducibility" is now "Verify the Work", and `econ-data-analysis` cites the new name. The "ad-hoc REPL" line and a restated failure rule are removed.
- **Step lifecycle pointers.** [changing-the-tree.md](../../../../skills/superplan/references/changing-the-tree.md), [consolidation.md](../../../../skills/superplan/references/consolidation.md) §Prune, and the [mature-consolidate](../../../../skills/superintegrate/references/mature-consolidate.md) prompt point to §Step lifecycle instead of restating it.
- **Word count.** The edited instruction files total 18,852 → 18,910 words (+58) before the revise round. The new manifest row, the no-steps condition, and the semantic-merge role outweigh the cut restatements.

### The harness contract is current

- **Anchors.** Removing the §Task Interface paragraph restores the `load_contract.json` anchors that were off by two, LC008 included. LC003 and LC004 are re-anchored.
- **LC008** cites the protection routing row in `reproducibility/SKILL.md` instead of model text.
- **LC024** is added for the `reproducibility` Domain row:
  - a `DOMAIN_ROWS` entry and its expected-artifact fixture;
  - `ALL_STAGE_SKILLS` minus the domain skills, so a `reproducibility` load at `Stage: implementation` is not an over-load, with a green test for that case.
- **Live runs, 2026-09-29, Sonnet via the SDK harness:**
  - The protection row loaded both `result-protection` and `reproducibility`. The LC008 note and the README now record this.
  - The reproducibility-worded domain fixture loaded `reproducibility` before its first edit.
- **Tests.** Harness tests: 130 passed. Task-tree suite: 1,336 passed; the 2 failures are the step-reader browser cases in `test_dag_workspace_browser.py`, which fail identically without this change.

### Three live sessions walked the wiring scenarios

The scratch project, `Firm Size and Leverage`, is rebuildable from this description:

- **Data:** `Data/raw.csv` holds 8 firms in 3 industries; firm `g` has negative size and is dropped.
- **01-data** (`approved`) owns `build-panel`, which builds the panel from `Code/build_panel.py`, `Code/helpers.py` (`winsorize`), and `Data/raw.csv`.
- **02-estimation** (`approved`) owns two steps:
  - `estimate`, which sleeps 150 s and writes `beta_size`;
  - `check-estimates`, a `kind: check` step asserting `beta_size` = −0.000734.
- **Starting state:** everything built and committed.

Sessions 1 and 2 dispatched a Sonnet implementer with `Load superRA:using-superra and superRA:implement-task`. Session 3 ran a Sonnet main agent through the Agent SDK, which had to write each researcher question into its report and continue on its own recommendation.

| Scenario | Setup | Outcome |
|---|---|---|
| 1. New table script | `03-table` asks for per-industry slopes from a new script | Loaded `econ-data-analysis` and `reproducibility` from the manifest. Read `designing-the-graph.md`, `claiming-results.md`, `rerun-or-accept.md`. Registered and built `reg-by-industry`; `## Results` names `build-panel` as a saved input and the step as executed. |
| 2. Shared-helper fan-out | `04-helper-fix`: `winsorize` rounds to 4 decimals | Rebuilt the cheap `build-panel`. Left `estimate` (150 s) and `check-estimates` stale. Returned `DONE_WITH_CONCERNS` with the rebuild-or-accept question and a recommendation in `## Results`. |
| 3. Completion and Protect | A commit tightens the leverage clip in `estimate.py` and adds a header comment to `build_panel.py` | Ran `status .`, `explain`, then `build --dry-run`. Accepted `build-panel` under the comment-only exception with the reason recorded. Raised the costly `estimate` rerun as a researcher question before building. The `integrate(protect)` body records `External inputs: Data/raw.csv` and no target list. |

- **Session 2** reached the right status although no tool call in its transcript opens `rerun-or-accept.md`; its own report lists the file as read.
- **Sessions 1 and 2** committed their work with `repro-lock.json` (`e509369`, `bd83801` in their scratch copies), after a long wait on a `git commit` permission prompt.

### Left open

- **Failing checks outside this task:** `unified-dependency-workflow-check` (its frontier fixture expects file edges to gate readiness, which [03](../03-readiness-model/task.md) removed) and `dashboard-dag-design-interaction-check` (the two browser cases) fail with or without this change. They were not rebuilt in this round; a parallel fix owns them.
- **For [09](../09-upgrade-and-records/task.md):** wiring.md's M6 (release notes on `tier:`) and its stale task-tree content were not part of this task.

Owning task for the fold-back: [unified-dependency-workflow](../../07-workflow-integration/unified-dependency-workflow/task.md).
