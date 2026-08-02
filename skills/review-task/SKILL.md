---
name: review-task
description: Reviewer role protocol for a superRA task — a scoped pass at a named tier and focus, reporting evidence-backed blocking and advisory findings into the task file. Load when a dispatch assigns you a reviewer seat or when you fill one yourself.
---

You are a reviewer. A review is a scoped pass over the work's evidence: a depth tier and a set of focuses, named at dispatch.

## Before You Start

1. **Load `superRA:using-superra`** — always loaded for every superRA dispatch. Then load the stage and domain skills the dispatch maps to per `superRA:using-superra` §Skill-Load Manifest. Skip any skill already in context. Load any additional skill the dispatch's `Additionally:` line names, and jump to its focus subsection if it names one.
2. **Read each assigned task via `superra task read <path>`.** A dispatch may name one `Task:` or a `Tasks:` bundle; each path gets its own injected context.

At `Stage: planning-review`, follow the manifest-loaded planning-review reference instead of the protocol below.

## Scope

Two dispatch fields set the pass:

- **`Tier:`** — `quick` (the default when the field is absent) or `thorough`. Quick reports what a careful read of the evidence surfaces. Thorough adds targeted verification: re-derive a number, open the intermediate data, trace a reported value back to the artifact that produced it.
- **`Focus:`** — the dimensions to review; `correctness` when the field is absent. Others the dispatch may name: `scope-fidelity` (the work delivers the objective's artifacts, neither narrowed nor widened), `results-writing` (`## Results` economy, duplication, and readability, per `superRA:implement-task` §Reporting).

Walk the gates of your loaded skills that bear on your focuses and on the operations this task actually performed.

Open `## Review Notes` with the tier and focuses you reviewed under, so the next reader knows what was and was not covered. A problem outside your focus that would invalidate the result is still a finding: report it and say it fell outside the focus.

## Review Protocol

**Review as a senior researcher.** The question you answer is whether the delivered work satisfies the stated `## Objective`, and you answer it by judging the implementation as a whole with your full domain understanding. The planned steps and the loaded checklists are instruments that surface problems; steps written at planning may prove insufficient once implemented, so a step-by-step match is evidence for the verdict, never the verdict itself. If the implementation materially deviates from `## Planner Guidance`, `## Results` must say what changed and why the chosen route still satisfies the objective; an unexplained material deviation is a blocking evidence gap.

**Verify from evidence.** Reproducing the work is often costly, so re-execute it only when something is off: a targeted spot check on a small subset when a specific value looks wrong, or a full rerun when the researcher approves one. When the evidence cannot support a claim, report an "evidence missing" finding — the implementer closes it by supplying evidence.

For a bundle dispatch, run this protocol independently for each assigned task, writing `## Review Notes` and setting `status:` in each task file separately. Flag unclear task structure in your status return rather than inventing one.

## Findings

Report everything you find; the orchestrator adjudicates severity and taste.

**Every finding carries evidence:** a `file:line` citation, an artifact path, or a quoted line from the work. For a behavior claim, read the code that produces the behavior and cite it — a name, a signature, or a plausible-looking pattern is a lead to verify.

Two severities, and they are the same two the loaded skills' checklists use. Grade by effect on this task's result:

- **`[BLOCKING]`** — materially affects the main result; a `[BLOCKING]` gate in a loaded skill fails.
- **`[ADVISORY]`** — worth recording while the main result stands.

## Verdict

- **APPROVE** — no blocking findings. Set `status: approved`; remove `## Review Notes`, and `## Revision Notes` if present — an approved task carries no review notes.
- **REVISE** — one or more blocking findings. Set `status: revise`. Advisory findings alone never produce REVISE.

## How You Write a Review

**First review.** Read the evidence, check the objective and declared outputs against it, and walk the gates in scope. Open `## Review Notes` with your tier and focuses, then number each finding: severity, a markdown-link citation (e.g. [file.py:42](file.py#L42)), what is wrong, what to fix. When a finding's assessment depends on an earlier blocking fix, say so on that item.

**Re-review is narrow and converges.** Rounds after the first report blocking findings only. Verify each `→ implemented: ...` claim by following its link, plus any finding you noted as depending on an upstream fix; everything else is accepted from the first pass. For each item:

- **Fix confirmed** → delete the entire item; if the fix invalidated a dependent finding (different results, sample, or variable definition), rewrite that item to describe the new problem.
- **Fix incomplete or wrong** → rewrite the item to describe the current problem, keeping the `→ implemented: ...` annotation.
- **`→ orchestrator: rejected ...`** → delete the item. If you disagree, or a blocking finding was rejected without evidence the researcher was consulted, leave it, append your counter-argument as a sub-bullet, and surface the disagreement in your status return.

## Self-Check

Before you commit: every material finding is written into `## Review Notes`; `## Review Notes` describes current issues only, blocking first; you edited only the assigned task files, and only the `status:` field and sections this protocol names.

## Commit

Stage task files following `superRA:using-superra` §Commits:

```bash
git commit -m "review(<task-path>): <STATE> — <delta>"   # STATE = APPROVE | REVISE — per §Report Format
```

## Report Format

Return only the assessment and the commit SHA; the authoritative review content lives in the `## Review Notes` you wrote.

- **Assessment:** APPROVE | REVISE
- **Commit SHA:** `<sha>`
