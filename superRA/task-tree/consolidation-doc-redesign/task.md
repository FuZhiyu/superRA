---
title: "Protection-Led Integration"
status: implemented
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

This task replaces the durable concern's former code-first ordering with the researcher's protection-led documentation and refactoring sequence.

Use the current `main` versions of [superintegrate](../../../skills/superintegrate/SKILL.md), [Protect](../../../skills/superintegrate/references/protect.md), [Mature & Consolidate](../../../skills/superintegrate/references/mature-consolidate.md), [Integrate](../../../skills/superintegrate/references/integrate.md), and [refactor-and-integrate](../../../skills/refactor-and-integrate/SKILL.md) as the baseline. Reorder and connect their existing mechanisms instead of rebuilding the discarded redesign.

The recovery branch `backup/pruning-redesign-before-restart-20260725` contains a generic safety-checked `task remove` implementation. Re-evaluate it independently and reuse it only if the new workflow needs mechanical subtree deletion; do not restore the surrounding workflow or task files.

Follow the instruction-authoring and generated-artifact rules in [CLAUDE.md](../../../CLAUDE.md). Prefer a small end-to-end workflow fixture over prose canaries or exhaustive protocol simulations.

## Results

Rebuilt INTEGRATE around a protected permanent record and one researcher-reviewed refactoring task:

- [superintegrate](../../../skills/superintegrate/SKILL.md) now orders Protect → Sync → Mature & Consolidate → Integrate → Finish. [Protect](../../../skills/superintegrate/references/protect.md) asks the researcher which provisional results to keep or drop, where the permanent documentation belongs, and whether each kept result needs documentation alone or an additional automated check.
- A documentation-only Protect decision proceeds directly to Sync and maturation without creating a protection task, dispatching a protection pair, or forcing a separate Protect commit. Protect commits only artifacts it actually creates.
- [Mature & Consolidate](../../../skills/superintegrate/references/mature-consolidate.md) writes the agreed user-facing documentation and result files before maturing task results and structure. It then creates one temporary task covering pruning plus consolidation, simplification, duplication removal, convention fit, stale-documentation repair, and final verification.
- [Integrate](../../../skills/superintegrate/references/integrate.md) executes that approved task against the permanent documentation, result files, and mature task results. A materially different outcome returns to the combined maturation review instead of expanding the proposal silently.
- [result-protection](../../../skills/result-protection/SKILL.md), [refactor-and-integrate](../../../skills/refactor-and-integrate/SKILL.md), the task-file contract, sync references, runtime routing, and user-facing workflow documentation now share the same ordering and ownership boundaries. Standalone result protection and task-tree consolidation remain available.
- The discarded redesign was not restored. Its independently useful subtree-removal implementation remains only on the recovery branch for future evaluation; this workflow does not require a special deletion command.
- Review follow-up removed duplicate domain confirmation prompts, corrected theory protection routing, scoped proposal-before-execution to standalone consolidation, reduced repeated dispatch instructions, and made every later approval durable even when it changes no files.

Verification completed on the implementation diff:

- `quick_validate.py` passed for all five modified skill packages.
- The Markdown checker passed for every changed Markdown file.
- `./superRA/superra task check` passed.
- `git diff --check` passed.
- The instruction-following contract suite passed (`14 passed`).
- Harness compatibility passed and confirmed generated agent files are current.
- The documentation site built successfully.
- A repository-wide search over active workflow, documentation, and task surfaces found no use of the prohibited term.
- Fix-round contract tests, harness compatibility, Markdown checks, task-tree checks, and `superintegrate` validation passed. The generic validator cannot validate the touched econ and theory packages because it rejects their pre-existing `user-invocable` frontmatter key; harness compatibility validates those packages successfully.

**Final diff self-check:** `git diff 329d6751..HEAD`; the surviving changes reorder existing workflow mechanisms, align their owning references, and update dependent user documentation. The obsolete parent task record was replaced by this task. No generated role artifact changed, no parallel result registry was introduced, and no unrelated implementation was restored from the recovery branch.

## Review Notes

1. **MAJOR — the mixed-results walkthrough still produces extra researcher prompts and misses the theory-specific drift-test discipline.** Protect already owns the single early selection gate before it dispatches the protection creator ([protect.md:9-26](../../../skills/superintegrate/references/protect.md#L9-L26)), but both domain add-ons tell that dispatched agent to confirm the candidate list again ([econ drift tests:13-26](../../../skills/econ-data-analysis/references/integrate-drift-tests.md#L13-L26), [theory drift tests:9-24](../../../skills/theory-modeling/references/integrate-drift-tests.md#L9-L24)). In the walkthrough—one documentation-only result, one drift-tested result, and one dropped result—the creator therefore stops for a second early confirmation instead of implementing the choices already made. Theory modeling also still routes its add-on through a removed stage name and phase label ([theory-modeling:15-20](../../../skills/theory-modeling/SKILL.md#L15-L20)), so a `Stage: protection` dispatch does not reliably load it. Make Protect the sole owner of result selection, remove the duplicate domain prompts, and route the theory add-on at `protection` only when a drift test was selected.
   → implemented: removed the duplicate confirmations from both [domain drift-test references](../../../skills/econ-data-analysis/references/integrate-drift-tests.md) and routed the [theory add-on](../../../skills/theory-modeling/SKILL.md) at `protection` only when selected.

2. **MAJOR — the consolidation owner still states the superseded approval order.** Its integration-specific sections correctly say that structural folds land recoverably before the combined review ([consolidation.md:71-73](../../../skills/superplan/references/consolidation.md#L71-L73), [consolidation.md:105-115](../../../skills/superplan/references/consolidation.md#L105-L115)), but the concluding rule says both entry paths use `propose, approve, execute` ([consolidation.md:117-123](../../../skills/superplan/references/consolidation.md#L117-L123)). An agent applying that shared rule can insert a standalone-style approval before maturation, creating an additional researcher gate and reversing the requested documentation-first flow. Scope the proposal-before-execution protocol to standalone use; let Mature & Consolidate remain the sole integration choreography.
   → implemented: removed the shared-order sentence so [consolidation](../../../skills/superplan/references/consolidation.md) states proposal-before-execution only for standalone use and delegates integration ordering.

3. **MAJOR — several new instruction lines fail the repository’s blocking DRY / Necessity gate.** Protect tells the protection reviewer to apply the drift-test-quality reference ([protect.md:25-26](../../../skills/superintegrate/references/protect.md#L25-L26)), although the always-loaded result-protection skill already owns that conditional load ([result-protection:10-18](../../../skills/result-protection/SKILL.md#L10-L18)). The Integrate reviewer prompt likewise restates the loaded refactor skill’s protected-record, approved-task, hunk-triage, and final-self-check gates ([integrate.md:34-46](../../../skills/superintegrate/references/integrate.md#L34-L46), [refactor-and-integrate:108-136](../../../skills/refactor-and-integrate/SKILL.md#L108-L136)). Delete these echoes and keep only task-specific context not supplied by the task, dispatch fields, or loaded skills.
   → implemented: reduced [Protect](../../../skills/superintegrate/references/protect.md) and the [Integrate reviewer dispatch](../../../skills/superintegrate/references/integrate.md) to their owning stage mechanics and dispatch fields.

4. **MAJOR — an unchanged researcher approval has no unambiguous durable completion record.** The maturation gate says to commit “any incorporated changes” on approval and put the reviewed SHA and decision in that commit body ([mature-consolidate.md:60-68](../../../skills/superintegrate/references/mature-consolidate.md#L60-L68)). When the researcher approves without requesting edits, there are no incorporated changes to commit, while the temporary task intentionally remains `not-started`; after a restart, neither status nor history proves the gate passed. Require an `integrate(mature)` approval commit for every approval, including the no-content-change case, so Integrate cannot rerun or bypass the sole later review.
   → implemented: [Mature & Consolidate](../../../skills/superintegrate/references/mature-consolidate.md) now requires an approval commit for every decision, including an empty commit when no files change.
