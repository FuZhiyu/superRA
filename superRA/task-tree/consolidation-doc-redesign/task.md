---
title: "Protection-Led Integration"
status: implemented
depends_on: []
---

## Objective

Starting from the current `main` workflow, make the minimum changes needed for result protection to guide documentation maturation and for one reviewed refactoring proposal to govern later cleanup.

- During Protect, before agents write permanent documentation, survey the provisional results and propose concrete options for the final documentation and its durable homes, which results to keep or drop, and how each kept result should be protected. Let the researcher choose whether permanent results documentation is sufficient or whether a drift test or another existing protection mechanism should also be created.
- Produce the agreed user-facing documentation and result files, then consolidate the task tree and mature its `## Results`. Those permanent artifacts and mature task results are the protected record.
- Before destructive cleanup, create one recognizably temporary refactoring task. Automatically place every in-scope change not justified by the protected record or an explicitly documented reproduction, validation, interpretation, or presentation path on its pruning list. The task also documents other opportunities, including consolidation, simplification, duplication removal, convention fit, and stale-documentation cleanup.
- Give the researcher one later review of the completed permanent record, mature task tree, and temporary refactoring task together. Approval authorizes agents to execute that proposal mechanically. If execution would materially change the protected outcome or the approved proposal, return to maturation, revise the proposal, and present it again.
- Verify the workflow with realistic behavior-level coverage and update the user-facing and harness-facing descriptions that materially depend on the changed ordering.

### Constraints

- Do not use the term the researcher prohibited in any new workflow name, instruction, task, test, or documentation.
- Do not introduce input or result ID registries, lineage annexes, a second keep manifest, wording-driven readability proxies, or another parallel result-selection system.
- Preserve the original standalone consolidation and result-protection mechanisms except where the agreed ordering and user decisions require a change.
- Keep the two researcher touchpoints distinct: early protection and documentation choices, then one review of the completed record and proposed refactoring.

## Planner Guidance

This task replaces the durable concern's former code-first ordering with the researcher's protection-led documentation and refactoring sequence.

Use the current `main` versions of [superintegrate](../../../skills/superintegrate/SKILL.md), [Protect](../../../skills/superintegrate/references/protect.md), [Mature & Consolidate](../../../skills/superintegrate/references/mature-consolidate.md), [Integrate](../../../skills/superintegrate/references/integrate.md), and [refactor-and-integrate](../../../skills/refactor-and-integrate/SKILL.md) as the baseline. Reorder and connect their existing mechanisms instead of rebuilding the discarded redesign.

The recovery branch `backup/pruning-redesign-before-restart-20260725` contains a generic safety-checked `task remove` implementation. Re-evaluate it independently and reuse it only if the new workflow needs mechanical subtree deletion; do not restore the surrounding workflow or task files.

Follow the instruction-authoring and generated-artifact rules in [CLAUDE.md](../../../CLAUDE.md). Prefer a small end-to-end workflow fixture over prose canaries or exhaustive protocol simulations.

## Results

Rebuilt INTEGRATE around a protected permanent record and one researcher-reviewed refactoring task:

- [superintegrate](../../../skills/superintegrate/SKILL.md) now orders Protect → Sync → Mature & Consolidate → Integrate → Finish. [Protect](../../../skills/superintegrate/references/protect.md) asks the researcher which provisional results to keep or drop, where the permanent documentation belongs, and whether each kept result needs documentation alone or an additional automated check.
- A documentation-only Protect decision proceeds directly to Sync and maturation without creating a protection task, dispatching a protection pair, or forcing a separate Protect commit. Protect commits only artifacts it actually creates.
- [Mature & Consolidate](../../../skills/superintegrate/references/mature-consolidate.md) writes the agreed user-facing documentation and result files before maturing task results and structure, then verifies those artifacts as the protected record. It performs no refactoring assessment.
- [Integrate](../../../skills/superintegrate/references/integrate.md) mechanically puts every unmatched in-scope change on one temporary task, adds other refactoring opportunities, presents that task with the protected record for the single later researcher review, then executes and independently reviews the approved work.
- [result-protection](../../../skills/result-protection/SKILL.md), [refactor-and-integrate](../../../skills/refactor-and-integrate/SKILL.md), the task-file contract, sync references, runtime routing, and user-facing workflow documentation now share the same ordering and ownership boundaries. Standalone result protection and task-tree consolidation remain available.
- The discarded redesign was not restored. Its independently useful subtree-removal implementation remains only on the recovery branch for future evaluation; this workflow does not require a special deletion command.
- Review follow-up removed duplicate domain confirmation prompts, corrected theory protection routing, scoped proposal-before-execution to standalone consolidation, reduced repeated dispatch instructions, and made every later approval durable even when it changes no files.

Verification completed on the implementation diff:

- `quick_validate.py` passed for `superintegrate`, `result-protection`, `refactor-and-integrate`, `semantic-merge`, `superplan`, and `using-superra`.
- The Markdown checker passed for every changed Markdown file.
- `./superRA/superra task check` passed.
- `git diff --check` passed.
- The instruction-following contract suite passed (`14 passed`).
- Harness compatibility passed and confirmed generated agent files are current.
- The documentation site built successfully.
- A repository-wide search over active workflow, documentation, and task surfaces found no use of the prohibited term.
- Fix-round contract tests, harness compatibility, Markdown checks, task-tree checks, and the applicable package validators passed. The generic validator cannot validate the touched econ, theory, or task-tree packages because it rejects their pre-existing `user-invocable` frontmatter key; harness compatibility validates those packages successfully.

**Final diff self-check:** `git diff 329d6751..HEAD`; the surviving changes reorder existing workflow mechanisms, align their owning references, and update dependent user documentation. The obsolete parent task record was replaced by this task. No generated role artifact changed, no parallel result registry was introduced, and no unrelated implementation was restored from the recovery branch.

## Review Notes

1. **MAJOR — the documentation-only path has no coherent handoff into maturation.** Protect now correctly skips task edits, agent dispatch, and a separate commit when it creates no artifact ([protect.md:25-26](../../../skills/superintegrate/references/protect.md#L25-L26)), but the top-level workflow still says every step is recovered from its commit and task status ([superintegrate:36-42](../../../skills/superintegrate/SKILL.md#L36-L42)), while maturation requires a Protect commit and affected-task working results as inputs ([mature-consolidate.md:7-9](../../../skills/superintegrate/references/mature-consolidate.md#L7-L9)). In the documentation-only walkthrough, neither input exists, so an uninterrupted agent can carry the conversation forward but the written protocol cannot consume or resume that decision consistently. Make the no-change Protect path an explicit exception to commit-based progress, let maturation consume the confirmed in-session choices plus an optional protection-artifact commit, and state that an interruption before maturation re-enters Protect because the researcher explicitly chose no intermediate record. Keep the later approval distinct: the mandatory `integrate(mature)` approval commit at [mature-consolidate.md:60-68](../../../skills/superintegrate/references/mature-consolidate.md#L60-L68) is correct.
   → implemented: [superintegrate](../../../skills/superintegrate/SKILL.md) now defines the no-record recovery exception, and [Mature & Consolidate](../../../skills/superintegrate/references/mature-consolidate.md) consumes in-session choices plus optional protection artifacts.

2. **MAJOR — the Protect fix introduced a duplicate instruction under the blocking DRY / Necessity gate.** The reference says to run the existing protection suite both as a free-standing invariant and again as the final numbered step ([protect.md:3-26](../../../skills/superintegrate/references/protect.md#L3-L26)). The numbered step already fixes the execution point and is sufficient; retain the artifact-scope rule near the top but remove the repeated suite command.
   → implemented: [Protect](../../../skills/superintegrate/references/protect.md) now states the suite command only in its numbered execution step.
