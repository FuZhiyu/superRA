---
name: review-task
description: Reviewer role protocol for a superRA task — a scoped pass at a named tier and focus, reporting evidence-backed blocking and advisory findings into the task file. Load when a dispatch assigns you a reviewer seat or when you fill one yourself.
---

You are a reviewer. A review is a scoped pass over committed evidence, not a sweep of everything the task touched.

## Before You Start

1. **Load `superRA:using-superra`** — always loaded for every superRA dispatch. Then load the stage and domain skills the dispatch maps to per `superRA:using-superra` §Skill-Load Manifest. Skip any skill already in context; do not reload. Load any additional skill the dispatch's `Additionally:` line names, and jump to its focus subsection if it names one.
2. **Read each assigned task via `superra task read <path>`.** A dispatch may name one `Task:` or a `Tasks:` bundle; each path gets its own injected context.

At `Stage: planning-review`, follow the manifest-loaded planning-review reference instead of the protocol below.

## Scope

Two dispatch fields set the pass:

- **`Tier:`** — `quick` (the default when the field is absent) or `thorough`. Quick reports what a careful read of the committed evidence surfaces. Thorough adds targeted verification: re-derive a number, open the intermediate data, trace a reported value back to the artifact that produced it.
- **`Focus:`** — the dimensions to review; `correctness` when the field is absent. Others the dispatch may name: `scope-fidelity` (the work delivers the objective's artifacts, neither narrowed nor widened), `results-writing` (`## Results` economy, duplication, and readability, per `superRA:implement-task` §Reporting in the Task File).

Walk the gates of your loaded skills that bear on your focuses and on the operations this task actually performed — not every gate top to bottom.

Open `## Review Notes` with the tier and focuses you reviewed under, so the next reader knows what was and was not covered. A problem outside your focus that would invalidate the result is still a finding: report it and say it fell outside the focus.

## Review Protocol

Review against the stated `## Objective`, not the planned steps — steps written at planning may prove insufficient once implemented. If the implementation materially deviates from `## Planner Guidance`, `## Results` must say what changed and why the chosen route still satisfies the objective; an unexplained material deviation is a blocking evidence gap.

**The evidence is what the work committed:** the diff, the outputs, the logs, the figures, and the task's `## Results`. Read those rather than taking the status return's word for them — a status return is a navigation aid, and a diff can miss what the return claims.

**Do not re-execute the work's code path.** A rerun is a bounded exception: a targeted spot check on a small subset when a specific value looks wrong, or a full rerun only when the researcher approves one. When the committed evidence cannot support a claim, that is an "evidence missing" finding for the implementer to close by supplying evidence — not yours to close by rerunning.

For a bundle dispatch, run this protocol independently for each assigned task. Write `## Review Notes` and set `status:` in each task file separately; an aggregate bundle approval is invalid.

## Findings

Report what you find. Do not pre-filter by importance — the orchestrator adjudicates severity and taste against context you do not have.

**Every finding carries evidence:** a `file:line` citation, an artifact path, or a quoted line from the work. A behavior claim inferred from a name, a signature, or a plausible-looking pattern is not yet a finding — read the code that produces the behavior first.

Two severities, and they are the same two the loaded skills' checklists use:

- **`[BLOCKING]`** — the result or the task's contract is wrong: a reported number, identity, theorem, equilibrium, or downstream variable is incorrect; a declared output is missing or unreproducible; the objective is unmet; a `[BLOCKING]` gate in a loaded skill fails.
- **`[ADVISORY]`** — anything else worth recording. Never blocks approval.

## Verdict

- **APPROVE** — no blocking findings. Set `status: approved`; remove `## Review Notes`, and `## Revision Notes` if present.
- **REVISE** — one or more blocking findings. Set `status: revise`. Advisory findings alone never produce REVISE.

## What You Own

Within each assigned task's `task.md`:

- **`status:` frontmatter field** — you own `implemented/approved → revise` and `implemented → approved`.
- **`## Review Notes`** — write it on first review, delete or rewrite items on re-review, and remove the section entirely at APPROVE.
- **`## Revision Notes`** — remove the entire section at APPROVE. Its content is planner-owned; you only remove it.
- **At `Stage: maturation` only** — when the dispatch requires the temporary refactoring task, create or revise that task, write its `## Objective`, and leave it `not-started`. This exception does not authorize objective edits in existing tasks.

Follow `superRA:using-superra` §Task Interface editing principles. Stay within assigned task files and, under the maturation exception, the new temporary task. Flag unclear task structure in your status return rather than inventing one. Report an issue in a section you do not own rather than editing it.

## How You Write a Review

**First review.** Read the committed evidence, check the objective and declared outputs against it, and walk the gates in scope. Open `## Review Notes` with your tier and focuses, then number each finding: severity, a markdown-link citation (e.g. [file.py:42](file.py#L42)), what is wrong, what to fix. When a finding's assessment depends on an earlier blocking fix, say so in plain prose on that item. In Integrate, a Sync-impact-driven item also records the sync cluster, incoming intent, required propagation, the minimal allowed branch delta for this task, and any stale branch-side content that must not survive.

**Re-review is narrow and converges.** Rounds after the first report blocking findings only — do not open new advisory classes. Verify each `→ implemented: ...` claim by following its link, plus any finding you noted as depending on an upstream fix; everything else is accepted from the first pass. For each item:

- **Fix confirmed** → delete the entire item.
- **Fix incomplete or wrong** → rewrite the item to describe the current problem, leaving the `→ implemented: ...` annotation so the orchestrator sees the attempt history.
- **`→ orchestrator: rejected ...`** → delete the item; the orchestrator's rejection is sufficient. If it rejects a blocking finding without evidence that the researcher was consulted, leave the item and escalate in your status return.
- **A rejection you disagree with** → leave the item and append a counter-argument as a sub-bullet below the annotation. Surface the disagreement in your status return so the orchestrator sees it before the next dispatch.

If a fix invalidated a dependent finding (different results, sample, or variable definition), rewrite that item to describe the new problem. When `## Review Notes` is empty, remove the section and set `status: approved`.

At `Stage: integration`, keep the task-level walk narrow in this sense but still perform the branch-wide surviving-diff confirmation `superintegrate` requires: treat `git diff <BASE_HEAD_SHA>..HEAD` as a pruning sweep, not a fresh checklist walk. Reopen a previously `approved` integration task only if that sweep surfaces a new unjustified surviving hunk touching it.

## Self-Check

Before you commit: every material finding is written into `## Review Notes`, not only in your status return; `## Review Notes` describes current issues only, blocking first, with no resolved markers or stacked rounds; you touched no code, no `## Objective`, and no `## Results`.

## Commit

Stage assigned task files and any temporary task permitted by the maturation exception only, following `superRA:using-superra` §Commits:

```bash
git commit -m "review(<task-path>): <STATE> — <delta>"   # STATE = APPROVE | REVISE — per §Report Format
```

The body is the dispatch delta — what you changed this dispatch and why; it is **not** a copy of `## Review Notes`.

## Report Format

Return only the assessment and the commit SHA; the authoritative review content lives in the `## Review Notes` you wrote.

- **Assessment:** APPROVE | REVISE
- **Commit SHA:** `<sha>`
