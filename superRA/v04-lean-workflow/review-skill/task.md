---
title: "Review Skill and Checklist Recalibration"
status: approved
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

## Details

- The exact pedantry-driving lines to rewrite are quoted with `file:line` in the [review-architecture map](../attachments/map-review-architecture.md) §4; checklist inventory with per-file `[BLOCKING]` counts: §3c (largest: econ-data-analysis 66 items, theory-modeling 45).
- Prompting techniques with sources (find-then-filter, two-severity semantics, convergence, evidence bar) and the Opus 5 over-verification findings: [review-prompting research](../attachments/research-review-prompting.md) §B, §D.
- Calibrate with the evidence bar and severity semantics, not enumerated "what not to flag" lists (a rejected design option — see the top-level contract).
- The read-first reviewer default already exists as domain discipline in `econ-data-analysis`; this task generalizes it to the review skill itself.
- The results-writing focus applies the `reporting-contract` sibling's rules (landing in `using-superra`); reference them rather than restating.

## Results

[review-task/SKILL.md](../../../skills/review-task/SKILL.md) is rewritten around a scoped pass, and one severity vocabulary now spans the repo.

**A review is scoped by two optional dispatch fields.** `Tier:` is `quick` or `thorough`, `Focus:` names dimensions (`correctness`, `scope-fidelity`, `results-writing`); absent, they default to quick and correctness, so the skill stays usable standalone and no call site is forced to carry them. The reviewer opens `## Review Notes` with the tier and focuses it worked under, and still reports an out-of-focus problem that would invalidate the result, marked as such.

**The protocol is evidence-first.** The committed diff, outputs, logs, figures, and `## Results` are the evidence; re-executing the work's code path is a bounded exception — a targeted spot check when a value looks wrong, a full rerun only with researcher approval. Evidence the reviewer cannot close cheaply becomes an "evidence missing" finding for the implementer rather than a reason to rerun.

**Findings are reported, not pre-filtered**, with severity adjudicated downstream. Every finding carries a `file:line`, an artifact path, or a quoted line — replacing "when uncertain whether something is a problem, flag it," which is gone. Re-review reports blocking findings only.

**An advisory finding always reaches the orchestrator.** At REVISE it sits in `## Review Notes`; at APPROVE the reviewer clears the section and carries the items in its return, one line each with its citation, and [agent-orchestration §Handling Reviewer Feedback](../../../skills/agent-orchestration/SKILL.md) adjudicates them there — the `Defer` path keys on `status: revise` and would never see them. The task file keeps only what must be preserved; the advisory delta rides the return.

**One severity vocabulary repo-wide.** CRITICAL/MAJOR/MINOR is retired for `[BLOCKING]`/`[ADVISORY]` across task findings, every checklist, and planning review, including the ten academic-writing reference headers with their per-class severity sentences. Full-sweep instructions went with it: the implementer still walks the whole checklist as a pre-handoff self-check, the reviewer walks what its focus covers. `superimplement` lost its deferred-MINOR resurrection sweep and its rerun-on-a-citation-less-APPROVE rule, since the evidence bar on the first pass replaces both.

**Two `Stage: integration` reviewer specializations were deleted rather than re-homed.** The branch-wide surviving-diff sweep now lives in [refactor-and-integrate §Final Diff Self-Check](../../../skills/refactor-and-integrate/SKILL.md); the five-field Sync-impact review-item template is gone on purpose — it prescribed a per-finding report form the generic evidence bar and the task's own `## Sync Impact` section already carry, and the sync vocabulary has a home at `Stage: sync`.

`docs/site` taught the adversarial-reviewer stance this task retired; its three pages now describe an independent scoped pass while keeping the blind-spot argument for independence.

### The checklist cut is 12%, not the 40–50% the question estimated

294 → 259 blocking and 76 → 68 advisory, concentrated in `econ-data-analysis` (58→45), `theory-modeling` (43→37 plus 25→21 in its integration reference), `refactor-and-integrate` (16→13), and academic-writing's refactor reference (16→13).

What came out: items duplicating another skill's rule (results updated in place, deviation reporting, focused diff, clean commits — all owned by `using-superra` or `implement-task`), generic hygiene no frontier model needs told, and collapsible families such as four multi-source validation checks becoming one external-reference item and nine survivorship items across two skills becoming one "every artifact survives, reorganize freely, delete nothing."

The estimate was wrong about where the weight sits. What remains in the large files is operation-conditional silent-error traps — merge validation, panel gaps before shifting, aggregation function versus content, transformation order — and per-dimension detection targets in the eight consistency lanes. Those are the domain-substantive gates the objective protects, so the pass stopped where the DRY and Necessity tests stopped biting. A deeper cut is a design decision about how much of the Pitfalls catalog a frontier model still needs, which is a different question.

**One promotion, not a cut:** the chained-filter item in [econ-data-analysis](../../../skills/econ-data-analysis/SKILL.md) became `[BLOCKING]`. A chained filter with an unintended cumulative effect changes sample composition, which is result-material — the same class as `&` versus `|` and as the two blocking items above it.

### Notes

Three surviving "top to bottom" lines are not gate-walks and were left alone: the academic-writing edit-heuristic lists in [structure.md](../../../skills/academic-writing/references/structure.md) and [style.md](../../../skills/academic-writing/references/style.md), and the reader-order derivation read in [theory-modeling/references/integration.md](../../../skills/theory-modeling/references/integration.md).
