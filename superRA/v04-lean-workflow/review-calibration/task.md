---
title: "Review Skill: Tiers, Focuses, Calibrated Findings"
status: not-started
depends_on: [role-skills]
---

## Objective

Rewrite the review protocol in the new review role skill so a review is an explicitly scoped pass — a depth tier and one or more focuses — that reports calibrated, evidence-backed findings instead of exhaustive pedantic ones.

- Parameterize the review skill by **tier** (depth: quick pass vs thorough) and **focus** (dimensions chosen at dispatch): at minimum correctness, scope fidelity, and results-writing quality (economy, duplication, readability per the writing contract). Dispatch names the tier and focuses; unfocused "review everything" is no longer the default shape.
- Evidence-first verification, no reruns by default: reviewers verify from recorded evidence — committed outputs, logs, diffs, figures — and never re-execute the work's code path by default. Re-execution is a bounded exception: a targeted spot check on a small subset, or a full rerun only when the researcher approves it; an evidence gap the reviewer cannot close cheaply is reported as a finding, not closed by rerunning an expensive pipeline.
- Two severities with verdict force: **blocking** (must fix before approval) and **advisory** (recorded, never blocks). Retire CRITICAL/MAJOR/MINOR; unify with the checklist `[BLOCKING]`/`[ADVISORY]` vocabulary so one severity model spans task findings, checklists, and planning review.
- Find-then-filter: the reviewer reports what it finds; severity thresholds and taste filtering happen at adjudication, never as "only report serious issues" instructions in the reviewer prompt (literal compliance reduces recall).
- Findings need evidence: a behavior claim cites `file:line` or an artifact; replace the "when uncertain whether something is a problem, flag it" stance with an evidence bar.
- Convergence: re-review rounds report blocking findings only — no new advisory classes on round 2+; iterate-to-approval applies to blocking findings only. Delete the deferred-MINOR resurrection sweep (`superimplement` Step 3) and the rerun-on-generic-APPROVE rule (first pass carries citations instead).
- Validation: review skill, `planning-review.md`, and `agent-orchestration` adjudication share one severity vocabulary; no surviving instruction tells a reviewer to flag on uncertainty or to walk every gate top-to-bottom regardless of focus.

## Planner Guidance

- The exact pedantry-driving lines to rewrite are quoted with `file:line` in the [review-architecture map](../attachments/map-review-architecture.md) §4.
- Prompting techniques with sources (find-then-filter, two-severity semantics, convergence rules, evidence bar): [review-prompting research](../attachments/research-review-prompting.md) §B.
- Calibrate with the evidence bar and severity semantics, not enumerated "what not to flag" exclusion lists (a rejected design option — see the top-level contract).
- The results-writing focus applies the contract from the `writing-contract` sibling; reference its rules rather than restating them (it may land after this task — point at `report-in-markdown` as the stable home).
- The read-first reviewer default already exists in `econ-data-analysis` (see the approved `econ-data-efficiency` task); this task generalizes it to the review skill itself, and reconciles the current reviewer instruction that unreproducible outputs are a MAJOR finding with the no-rerun default (the finding becomes "evidence missing," resolvable by the implementer supplying evidence, not by the reviewer rerunning).

## Results
