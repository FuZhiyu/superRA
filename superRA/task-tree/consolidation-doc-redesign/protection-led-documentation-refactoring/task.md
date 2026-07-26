---
title: "Protection-Led Documentation and Refactoring"
status: not-started
depends_on: []
---

## Objective

Starting from the current `main` workflow, make the minimum changes needed for result protection to guide documentation maturation and for one reviewed refactoring proposal to govern later cleanup.

- During Protect, before agents write permanent documentation, survey the provisional results and propose concrete options for the final documentation and its durable homes, which results to keep or drop, and how each kept result should be protected. Let the researcher choose whether permanent results documentation is sufficient or whether a drift test or another existing protection mechanism should also be created.
- Produce the agreed user-facing documentation and result files, then consolidate the task tree and mature its `## Results`. Those permanent artifacts and mature task results are the protected record.
- Before destructive cleanup, create one recognizably temporary refactoring task. It must document proposed pruning and other refactoring opportunities, including consolidation, simplification, duplication removal, convention fit, and stale-documentation cleanup. Treat in-scope work not justified by the protected record or its documented reproduction, validation, interpretation, and presentation paths as a candidate for removal.
- Give the researcher one later review of the completed permanent record, mature task tree, and temporary refactoring task together. Approval authorizes agents to execute that proposal mechanically. If execution would materially change the protected outcome or the approved proposal, return to maturation, revise the proposal, and present it again.
- Verify the workflow with realistic behavior-level coverage and update the user-facing and harness-facing descriptions that materially depend on the changed ordering.

### Constraints

- Do not use the term the researcher prohibited in any new workflow name, instruction, task, test, or documentation.
- Do not introduce input or result ID registries, lineage annexes, a second keep manifest, wording-driven readability proxies, or another parallel result-selection system.
- Preserve the original standalone consolidation and result-protection mechanisms except where the agreed ordering and user decisions require a change.
- Keep the two researcher touchpoints distinct: early protection and documentation choices, then one review of the completed record and proposed refactoring.

## Planner Guidance

The existing parent concern owns the post-Integrate consolidation and documentation behavior, but its current code-first ordering no longer matches the researcher’s decision. This child is a substantial update under that durable owner rather than a new top-level workflow concern.

Use the current `main` versions of [superintegrate](../../../../skills/superintegrate/SKILL.md), [Protect](../../../../skills/superintegrate/references/protect.md), [Mature & Consolidate](../../../../skills/superintegrate/references/mature-consolidate.md), [Integrate](../../../../skills/superintegrate/references/integrate.md), and [refactor-and-integrate](../../../../skills/refactor-and-integrate/SKILL.md) as the baseline. Reorder and connect their existing mechanisms instead of rebuilding the discarded redesign.

The recovery branch `backup/pruning-redesign-before-restart-20260725` contains a generic safety-checked `task remove` implementation. Re-evaluate it independently and reuse it only if the new workflow needs mechanical subtree deletion; do not restore the surrounding workflow or task files.

Follow the instruction-authoring and generated-artifact rules in [CLAUDE.md](../../../../CLAUDE.md). Prefer a small end-to-end workflow fixture over prose canaries or exhaustive protocol simulations.

## Results
