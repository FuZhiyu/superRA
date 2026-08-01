---
title: "Review Skill and Checklist Recalibration"
status: not-started
depends_on: [role-skills]
---

## Objective

Rewrite the review protocol in the new review role skill so a review is an explicitly scoped pass — a depth tier and one or more focuses — reporting calibrated, evidence-backed findings; recalibrate every gated checklist to the same semantics in the same pass.

- Parameterize the review skill by **tier** (depth: quick pass vs thorough) and **focus** (dimensions chosen at dispatch): at minimum correctness, scope fidelity, and results-writing quality (economy, duplication, readability per the reporting contract). Dispatch names the tier and focuses; unfocused "review everything" is no longer the default shape.
- Evidence-first verification, no reruns by default: reviewers verify from recorded evidence — committed outputs, logs, diffs, figures — and never re-execute the work's code path by default. Re-execution is a bounded exception: a targeted spot check on a small subset, or a full rerun only when the researcher approves it; an evidence gap the reviewer cannot close cheaply is an "evidence missing" finding resolved by the implementer supplying evidence, not by the reviewer rerunning.
- Two severities with verdict force: **blocking** (must fix before approval) and **advisory** (recorded, never blocks). Retire CRITICAL/MAJOR/MINOR; one severity model spans task findings, checklists, and planning review.
- Find-then-filter: the reviewer reports what it finds; severity thresholds and taste filtering happen at adjudication, never as "only report serious issues" instructions in the reviewer prompt (literal compliance reduces recall).
- Findings need evidence: a behavior claim cites `file:line` or an artifact; replace the "when uncertain whether something is a problem, flag it" stance with an evidence bar.
- Convergence: re-review rounds report blocking findings only — no new advisory classes on round 2+; iterate-to-approval applies to blocking findings only. Delete the deferred-MINOR resurrection sweep (`superimplement` Step 3) and the rerun-on-generic-APPROVE rule (first pass carries citations instead).
- Recalibrate the gated checklists to the same two-severity semantics: econ-data-analysis, theory-modeling, refactor-and-integrate, result-protection, semantic-merge, slide-design, writing consistency lanes, `planning-review.md`. Delete verification-scaffolding instructions frontier models perform unprompted (re-check/double-check/verify-again lines, verify-subagents); prune items failing the `CLAUDE.md` DRY/Necessity tests; keep domain-substantive gates (merge validation, look-ahead bias, proof verification) intact. No "what not to flag" exclusion lists. (The final-diff-self-check trail item in refactor-and-integrate is owned by `reporting-contract` — leave it.)
- Validation: one severity vocabulary repo-wide; no surviving instruction tells a reviewer to flag on uncertainty, walk every gate top-to-bottom regardless of focus, or re-verify work the model already verifies; domain hard gates survive.

## Planner Guidance

- The exact pedantry-driving lines to rewrite are quoted with `file:line` in the [review-architecture map](../attachments/map-review-architecture.md) §4; checklist inventory with per-file `[BLOCKING]` counts: §3c (largest: econ-data-analysis 66 items, theory-modeling 45).
- Prompting techniques with sources (find-then-filter, two-severity semantics, convergence, evidence bar) and the Opus 5 over-verification findings: [review-prompting research](../attachments/research-review-prompting.md) §B, §D.
- Calibrate with the evidence bar and severity semantics, not enumerated "what not to flag" lists (a rejected design option — see the top-level contract).
- The read-first reviewer default already exists in `econ-data-analysis` (see the approved `econ-data-efficiency` task); this task generalizes it to the review skill itself.
- The results-writing focus applies the `reporting-contract` sibling's rules (landing in `using-superra`); reference them rather than restating.

## Results
