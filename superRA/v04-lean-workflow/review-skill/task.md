---
title: "Review Skill and Checklist Recalibration"
status: implemented
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

`skills/review-task/SKILL.md` is rewritten around a scoped pass. `Tier:` is `quick` or `thorough`; `Focus:` names dimensions (`correctness`, `scope-fidelity`, `results-writing`). Both are optional dispatch fields — absent `Tier:` means quick, absent `Focus:` means correctness, per researcher decision, so the skill stays usable standalone and no call site is forced to carry them. The reviewer opens `## Review Notes` with the tier and focuses it worked under, and a problem outside its focus that would invalidate the result is still reported, marked as out-of-focus.

The protocol is evidence-first. The committed diff, outputs, logs, figures, and `## Results` are the evidence; re-executing the work's code path is a bounded exception — a targeted spot check when a value looks wrong, or a full rerun only with researcher approval. Evidence the reviewer cannot close cheaply is an "evidence missing" finding for the implementer, not a prompt to rerun.

Findings are reported, not pre-filtered: severity and taste are adjudicated downstream. Every finding carries a `file:line`, an artifact path, or a quoted line — this replaces "when uncertain whether something is a problem, flag it," which is gone. Re-review reports blocking findings only and opens no new advisory classes.

**One severity vocabulary repo-wide.** CRITICAL/MAJOR/MINOR is retired; `[BLOCKING]`/`[ADVISORY]` spans task findings, every checklist, and planning review. Converted: the ten `writing` reference headers and their per-class severity sentences (a main-spec mismatch is blocking, a secondary-spec difference advisory; a sign error in a main identifying equation is blocking, appendix notation drift advisory), `slide-design`, `refactor-and-integrate`, `semantic-merge`, `result-protection/references/drift-test-quality.md`, `theory-modeling`, `econ-data-analysis`, plus the worked examples in `implement-task` and `task-tree`. `grep -rn "MINOR\|MAJOR\|CRITICAL" skills/` returns nothing outside `task-tree/scripts`.

**Full-sweep instructions retired.** `semantic-merge` and `drift-test-quality` said "walk every item" for implementer and reviewer alike; the implementer still walks the whole list as a pre-handoff self-check, the reviewer walks what its focus covers. `workflow-sync-reviewer.md`'s "top to bottom" is gone, as is `superimplement`'s "one comprehensive task-local pass" — its Step 2 now names the tier and focuses the work warrants.

**Convergence.** Deleted `superimplement` Step 3's deferred-MINOR resurrection sweep (Step 3 is three checks now, not four) and Step 2's rerun-the-reviewer-on-a-citation-less-APPROVE rule; the evidence bar on the first pass is what replaces it. `agent-orchestration`'s "adversarial first-pass review" model-tier trigger is now "thorough-tier first-pass review," and its CRITICAL-override escalation reads as a blocking-finding override.

### Checklist prune

294 → 259 blocking, 76 → 68 advisory. Per file: `econ-data-analysis` 58→45, `theory-modeling` 43→37, `theory-modeling/references/integration.md` 25→21, `refactor-and-integrate` 16→13, `writing/references/refactor-and-compile.md` 16→13, `econ-data-analysis/references/integration.md` 14→11, `semantic-merge` 21→20.

What came out: items duplicating another skill (`## Results` updated in place, deviation reporting, focused diff, clean commits — all owned by `using-superra` or `implement-task`); generic hygiene no frontier model needs told (no dangling TODO/XXX, no debug artifacts, self-contained work); and collapsible families — the four multi-source validation checks became one external-reference item, three visualization advisories became one, five theory survivorship items and four econ survivorship items each became one "every artifact survives, reorganize freely, delete nothing."

**This is a 12% cut, not the 40–50% the question estimated.** The estimate was wrong about where the weight sits. After the duplication came out, what remains in the large files is operation-conditional silent-error traps (merge validation, panel gaps before shifting, aggregation function-vs-content, transformation order) and per-dimension detection targets in the eight `writing/consistency` lanes. Those are the domain-substantive gates the objective protects, and cutting further would have meant deleting them. Rather than pad the number, I stopped where the DRY and Necessity tests stopped biting. If you want a deeper cut, the honest lever is a design decision about how much of the Pitfalls catalog a frontier model still needs — a different question from this task's.

### Validation

`125 passed` for `tests/harness-instruction-following`; `tests/check-harness-compatibility.sh` clean. `grep` for the retired stances — flag-on-uncertainty, comprehensive-pass, walk-top-to-bottom, "note 'not applicable' with reasoning" — returns nothing across `skills/`.
