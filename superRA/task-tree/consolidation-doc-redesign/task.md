---
title: "Protection-Led Integration"
status: approved
depends_on: []
---

## Objective

Starting from the current `main` workflow, make the minimum changes needed for result protection to guide documentation maturation and for one reviewed refactoring proposal to govern later cleanup.

- During Protect, before agents write permanent documentation, survey the provisional results and propose concrete options for the final documentation and its durable homes, which results to keep or drop, how the affected task tree should consolidate, and how each kept result should be protected. Record the confirmed specification in a decision commit so the drafter, reviewer, and resumed sessions share one source of truth.
- Use one drafter seat to produce the agreed user-facing documentation and result files, consolidate the task tree, and mature its `## Results`. Those permanent artifacts and mature task results are the protected record.
- Use one reviewer seat to verify the protected record, compare every in-scope change against it, and create one recognizably temporary refactoring task. The task automatically lists every change not justified by the protected record or an explicitly documented reproduction, validation, interpretation, or presentation path as a pruning target and proposes other consolidation, simplification, duplication-removal, convention-fit, and stale-documentation actions.
- Give the researcher one later review of the completed permanent record, mature task tree, and temporary refactoring task together. Approval authorizes agents to execute that proposal mechanically. If execution would materially change the protected outcome or the approved proposal, return to maturation, revise the proposal, and present it again.
- Make the workflow resumable from the Protect decision commit before the temporary task exists, then from the temporary task, its status, and the approval commit; do not add another progress artifact or researcher gate.
- Verify the workflow with realistic behavior-level coverage and update the user-facing and harness-facing descriptions that materially depend on the changed ordering.

### Constraints

- Do not use the term the researcher prohibited in any new workflow name, instruction, task, test, or documentation.
- Do not introduce input or result ID registries, lineage annexes, a second keep manifest, wording-driven readability proxies, or another parallel result-selection system.
- Preserve the original standalone consolidation and result-protection mechanisms except where the agreed ordering and user decisions require a change.
- Keep the two researcher touchpoints distinct: early protection and documentation choices, then one review of the completed record and proposed refactoring.

## Details

This task replaces the durable concern's former code-first ordering with the researcher's protection-led documentation and refactoring sequence.

Use the current `main` versions of [superintegrate](../../../skills/superintegrate/SKILL.md), [Protect](../../../skills/superintegrate/references/protect.md), [Mature & Consolidate](../../../skills/superintegrate/references/mature-consolidate.md), [Integrate](../../../skills/superintegrate/references/integrate.md), and [refactor-and-integrate](../../../skills/refactor-and-integrate/SKILL.md) as the baseline. Reorder and connect their existing mechanisms instead of rebuilding the discarded redesign.

The recovery branch `backup/pruning-redesign-before-restart-20260725` contains a generic safety-checked `task remove` implementation. Re-evaluate it independently and reuse it only if the new workflow needs mechanical subtree deletion; do not restore the surrounding workflow or task files.

Follow the instruction-authoring and generated-artifact rules in [CLAUDE.md](../../../CLAUDE.md). Prefer a small end-to-end workflow fixture over prose canaries or exhaustive protocol simulations.

The maturation-only ownership change touches the reviewer role spec; regenerate the Codex reviewer agent with `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project`.

## Results

Rebuilt INTEGRATE around a protected permanent record, one maturation drafter, one reviewer seat, and one researcher-reviewed refactoring task:

- [superintegrate](../../../skills/superintegrate/SKILL.md) now orders Protect → Sync → Mature & Consolidate → Integrate → Finish. [Protect](../../../skills/superintegrate/references/protect.md) asks the researcher which provisional results to keep or drop, where the permanent documentation and mature task results belong, how each affected subtree should consolidate, and whether each kept result needs documentation alone or an additional automated check.
- Protect records the approved scope, result dispositions, permanent paths, task-tree dispositions, and protection mechanisms in an `integrate(protect)` decision commit. Documentation-only choices skip the protection-agent pair but still use an empty decision commit, so maturation can resume without conversation context.
- [Mature & Consolidate](../../../skills/superintegrate/references/mature-consolidate.md) assigns one drafter seat to write the agreed user-facing documentation, result files, and mature tree from that commit. One reviewer seat then verifies the same decision against the named artifacts, compares `BASE_HEAD_SHA..HEAD` under [refactor-and-integrate](../../../skills/refactor-and-integrate/SKILL.md), and writes the temporary refactoring task.
- The temporary task stays `not-started`, links the Protect decision and protected-record paths, records `BASE_HEAD_SHA`, names bounded pruning and refactoring actions, and carries the required verification. It does not duplicate result prose or create a separate keep manifest.
- [Integrate](../../../skills/superintegrate/references/integrate.md) recovers first from the Protect decision commit, then from the temporary task, its status, and the `integrate(mature)` approval commit: missing or incomplete task returns to maturation review; an unapproved task reaches the researcher gate; `not-started`, `implemented`/`revise`, and `approved` resume at execution, review/fix, and closeout respectively.
- The researcher still sees one combined review surface. After approval, the existing implementer/reviewer loop executes and verifies the task; a materially changed record or action returns to the corresponding maturation step and repeats the gate.
- [result-protection](../../../skills/result-protection/SKILL.md), [refactor-and-integrate](../../../skills/refactor-and-integrate/SKILL.md), the task-file contract, sync references, runtime routing, and user-facing workflow documentation now share the same ordering and ownership boundaries. Standalone result protection and task-tree consolidation remain available.
- The discarded redesign was not restored. Its independently useful subtree-removal implementation remains only on the recovery branch for future evaluation; this workflow does not require a special deletion command.
- Review follow-up removed duplicate domain confirmation prompts, corrected theory protection routing, scoped proposal-before-execution to standalone consolidation, reduced repeated dispatch instructions, and made every later approval durable even when it changes no files.
- The loaded refactoring discipline now uses the protected record as the sole workflow exemption from the automatic pruning list; its broader justification sources remain available only in standalone use.
- The reviewer role spec carries the narrow maturation-only task-creation ownership exception; it lived in `agents/reviewer.md` and its generated Codex agent, both retired by [v04-lean-workflow/role-skills](../../v04-lean-workflow/role-skills/task.md) in favor of [review-task](../../../skills/review-task/SKILL.md).
- Main-seat review removed a duplicate refactoring-protocol echo and aligned the reviewer’s edit, self-check, and commit boundaries with its temporary-task ownership.

Verification completed on the implementation diff:

- `quick_validate.py` passed for the changed `superintegrate` and `superplan` skills.
- The Markdown checker passed for every changed Markdown file.
- `./superRA/superra task check` passed.
- `git diff --check` passed.
- The focused instruction-following and generator contract suite passed (`17 passed`).
- Harness compatibility passed, including canonical-to-generated reviewer synchronization.
- The documentation site built successfully.
- The skill validator passed for `superintegrate`; `task-tree` retains its pre-existing `user-invocable` frontmatter incompatibility with the generic validator.
- A repository-wide search over active workflow, documentation, and task surfaces found no use of the prohibited term.
- A five-state recovery walkthrough covered missing task, unapproved `not-started`, approved `not-started`, `implemented`/`revise`, and `approved` task states without another progress artifact.
- The recovery walkthrough now begins from an `integrate(protect)` decision commit and verifies that both maturation seats receive its SHA.

**Final diff self-check:** `git diff 329d6751..HEAD`; the surviving changes establish the protection-led workflow, preserve consolidation choice inside the existing Protect gate, and make the decision available to both maturation seats through the existing commit mechanism. Temporary-task derivation remains in the maturation reviewer seat, and task-status/approval-commit recovery remains explicit. No parallel result registry, separate keep manifest, extra researcher gate, or unrelated recovery-branch implementation was introduced.
