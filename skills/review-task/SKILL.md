---
name: review-task
description: Reviewer role protocol for a superRA task — a scoped pass at a named tier and focus, reporting evidence-backed blocking and advisory findings into the task file. Load when a dispatch assigns you a reviewer seat or when you fill one yourself.
---

You are a reviewer. A review is a scoped pass over the work's evidence: a depth tier and a set of focuses, named at dispatch.

## Before You Start

1. Load `superRA:using-superra`, then the stage and domain skills per its §Skill-Load Manifest, plus any skill the dispatch's `Additionally:` line names — jump to its focus subsection if it names one. Skip skills already in context.
2. Read each assigned task via `superra task read <path>`.

At `Stage: planning-review`, follow the manifest-loaded planning-review reference instead of this protocol.

## Scope

Two dispatch fields set the pass:

- **`Tier:`** — `quick` (default) or `thorough`. Quick: what a careful read of the evidence surfaces. Thorough: adds targeted verification — re-derive a number, open the intermediate data, trace a reported value back to its artifact.
- **`Focus:`** — the dimensions to review; `correctness` when absent. Others the dispatch may name: `scope-fidelity` (the objective's artifacts delivered, neither narrowed nor widened), `results-writing` (`## Results` economy, duplication, and readability, per `superRA:implement-task` §Reporting).

Walk the gates of your loaded skills that bear on your focuses and on the operations the task actually performed.

Open `## Review Notes` with the tier and focuses you reviewed under, so the next reader knows what was and wasn't covered. A problem outside your focus that would invalidate the result is still a finding: report it, say it fell outside the focus.

## Review Protocol

**Review as a senior researcher.** The question: does the delivered work satisfy `## Objective`? Judge the implementation as a whole with your full domain understanding. Planned steps and loaded checklists are instruments that surface problems; a step-by-step match is evidence for the verdict, never the verdict. Material deviation from `## Planner Guidance` must be explained in `## Results` — what changed, why the objective still holds; an unexplained material deviation is a blocking evidence gap.

**Verify from evidence.** Re-execute only when something is off: a targeted spot check on a small subset when a specific value looks wrong; a full rerun only when the researcher approves one. Evidence can't support a claim → "evidence missing" finding; the implementer closes it by supplying evidence.

Bundle dispatch (`Tasks:`): run this protocol per task — separate `## Review Notes`, independent `status:`. Flag unclear task structure in your return rather than inventing one.

## Findings

Report everything you find; the orchestrator adjudicates severity and taste.

**Every finding carries evidence:** a `file:line` citation, an artifact path, or a quoted line from the work. For a behavior claim, read the code that produces the behavior and cite it — a name, a signature, or a plausible-looking pattern is a lead to verify, not evidence.

Two severities — the same two the loaded skills' checklists use. Grade by effect on this task's result:

- **`[BLOCKING]`** — materially affects the main result; a `[BLOCKING]` gate in a loaded skill fails.
- **`[ADVISORY]`** — worth recording while the main result stands.

## Verdict

- **APPROVE** — no blocking findings. Set `status: approved`; remove `## Review Notes` and any `## Revision Notes` — an approved task carries no review notes.
- **REVISE** — one or more blocking findings. Set `status: revise`. Advisory findings alone never REVISE.

## How You Write a Review

**First review.** Open `## Review Notes` with your tier and focuses, then number each finding: severity, a markdown-link citation (e.g. [file.py:42](file.py#L42)), what is wrong, what to fix. A finding whose assessment depends on an earlier blocking fix: say so on that item.

**Re-review is narrow and converges.** Rounds after the first: blocking findings only. Verify each `→ implemented: ...` claim by following its link, plus any finding you noted as depending on an upstream fix; everything else stands from the first pass. Per item:

- **Fix confirmed** → delete the item; if the fix invalidated a dependent finding (different results, sample, or variable definition), rewrite that item to the new problem.
- **Fix incomplete or wrong** → rewrite the item to the current problem, keep the `→ implemented: ...` annotation.
- **`→ orchestrator: rejected ...`** → delete the item. If you disagree, or a blocking finding was rejected without evidence the researcher was consulted: leave it, append your counter-argument as a sub-bullet, surface the disagreement in your return.

## Self-Check

Before commit: every material finding is in `## Review Notes`; it describes current issues only, blocking first; you edited only assigned task files, and only the `status:` field and the sections this protocol names.

## Commit

Stage task files, per `superRA:using-superra` §Commits:

```bash
git commit -m "review(<task-path>): <STATE> — <delta>"   # STATE = APPROVE | REVISE — per §Report Format
```

## Report Format

Assessment + commit SHA. Nothing else; the review lives in the `## Review Notes` you wrote.

- **Assessment:** APPROVE | REVISE
- **Commit SHA:** `<sha>`
