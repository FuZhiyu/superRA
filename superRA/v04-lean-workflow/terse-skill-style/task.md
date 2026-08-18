---
title: "Terse Skill Style: Teachable Spec, Repo Sweep, Stage Coverage"
status: approved
depends_on: []
---

## Objective

Skill prose repo-wide matches the terse style of the restyled role skills, the style is taught well enough that agents reproduce it unaided, and every workflow stage's written output respects it.

The style, from the accepted exemplars: bolded imperative + short elaboration; definition bullets over framing sentences; fragments for enumerable actions; no derivation or rationale clauses; cut any clause whose content an adjacent bullet already carries. Target density: implement-task / review-task after their restyles.

Exemplar record: commit `f525b63e` (review-task cut to level) with predecessor `daea6ae3` as the named failure mode — style changed, density unchanged, file length identical. Diffing the pair shows the concrete moves.

## Results

Skill prose across the repo is 13% shorter with no protocol loss, and the style now has a home that teaches it well enough to reproduce.

- **The spec is [CLAUDE.md §Skill Prose Style](../../../CLAUDE.md)** — two passes in order (the DRY/Necessity gate deletes lines, then compression tightens the survivors), plus six concrete moves extracted from the `daea6ae3..f525b63e` exemplar diff, and the rule that a pass is measured in words rather than lines. See [style-spec](style-spec/task.md).
- **The sweep restyled 80 files** across five groups, 61,638 prose words down to 53,551, with the harness suite green at every group. See [repo-sweep](repo-sweep/task.md).
- **Maturation is bound to the same bar.** [mature-consolidate.md](../../../skills/superintegrate/references/mature-consolidate.md) names rewriting surviving task files down to the terse style as part of the drafter's job and gives its reviewer `Focus: correctness, results-writing`; on the planning side, `task-tree-design.md` §Writing Objectives states that objectives and planning artifacts are written to the same standard. See [stage-coverage](stage-coverage/task.md).

**The sweep was also the spec's test, and it found the failure mode.** Three REVISE rounds showed what the density target costs unreviewed: a DRY deletion resting on a premise false on this branch, protocol facts dropped as if they were wording, decision-carrying hedges cut as filler, and twice the imperative verb itself removed instead of the clause around it. The settled rule — a hedge that carries a decision branch is protocol content, not filler — went back into the spec.