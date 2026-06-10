---
title: "Update task-tree skill docs"
status: implemented
depends_on:
  - 01-design
tags:
  - docs
script: 
input: []
output: []
created: 2026-05-26
---

## Objective

Update the task-tree skill's own documentation to reflect the unified status model.

**`skills/task-tree/SKILL.md`:**
- Remove `review_status` and `integration_status` rows from the frontmatter field table
- Update ownership note — `status` is co-owned by implementer and reviewer
- Update the task file format example — remove both fields
- Update the `task_update.py` example to not pass `--review-status` or `--integration-status`

**`skills/task-tree/references/planning.md`:**
- Remove both fields from field anatomy, defaults, and ownership sections
- Update the "who sets what" ownership rules to reflect single `status` field with reviewer as co-owner
- Remove `## Workflow Status` documentation — phase is inferred, not stored

**`skills/task-tree/references/internals.md`:**
- Remove both fields from dataclass field documentation
- Remove `VALID_REVIEW_STATUSES` and `VALID_INTEGRATION_STATUSES` from constants documentation
- Update migration normalization docs to reflect unified status path

## Results

All three task-tree documentation files updated to reflect the unified status model.

**`skills/task-tree/SKILL.md`** ([SKILL.md](skills/task-tree/SKILL.md)):
- Removed `review_status` and `integration_status` rows from frontmatter field table; `status` now shows `archived` and owner `implementer / reviewer`
- Updated ownership note to explain co-ownership (implementer owns up to `implemented`, reviewer owns `implemented → revise/approved`)
- Removed both fields from the task file format YAML example; added `archived` to the status comment
- Removed `--review-status approved` from the `task_update.py` CLI example
- Updated migration section: `**Review status:**` and `**Integration status:**` annotated as legacy fields; status inference rewritten to describe the priority-based mapping

**`skills/task-tree/references/planning.md`** ([planning.md](skills/task-tree/references/planning.md)):
- Removed `review_status` and `integration_status` bullets from Field-by-Field Notes; consolidated into a single `status` entry with `archived` in the valid values and co-ownership documented
- Removed `task_create.py` defaults mentioning `review_status: ~, integration_status: ~`
- Removed `## Workflow Status Checkboxes` section entirely (phase is inferred, not stored)

**`skills/task-tree/references/internals.md`** ([internals.md](skills/task-tree/references/internals.md)):
- Removed `review_status` and `integration_status` fields from the Task dataclass documentation; added `archived` to the status comment
- Removed `VALID_REVIEW_STATUSES` and `VALID_INTEGRATION_STATUSES` from enum constants; added `archived` to `VALID_STATUSES`
- Updated migration status inference to describe the unified mapping: `integration_status` → `review_status` → checkbox inference priority chain

## Review Notes

Retrospective audit of the task-tree doc surfaces this task owns (current findings; some arose after this task's original approval as the docs evolved).

1. **MAJOR** — [task-file-contract.md:19](../../../../skills/task-tree/references/task-file-contract.md#L19), the CLAUDE.md-designated owner of the status enum/lifecycle, omits the `approved → revise` transition that the parent [Design Spec](../task.md), [agents/reviewer.md:83](../../../../agents/reviewer.md#L83) ("you own `implemented/approved → revise`"), and [direct-mode-reviewer.md:87](../../../../skills/using-superRA/references/direct-mode-reviewer.md#L87) all carry. The owner copy is the incomplete one, so consumers of the authoritative doc get a narrower reviewer ownership than the agents actually exercise. Fix: add the integration-round `approved → revise` (reviewer-owned) to the contract's status line.
   → implemented: added `approved` to `revise` (integration round, reviewer-owned) to task-file-contract.md line 19 ([task-file-contract.md:19](../../../../skills/task-tree/references/task-file-contract.md#L19)).
2. **MAJOR** — [task-file-contract.md:19](../../../../skills/task-tree/references/task-file-contract.md#L19) says re-entry "tasks in the transitive downstream closure of a modified task have their status *cleared* by default" — cleared to what is undefined, and the other surfaces disagree concretely: [superplan/SKILL.md:215](../../../../skills/superplan/SKILL.md#L215) resets to `not-started` "by orchestrator judgment," while [task-tree-design.md:89](../../../../skills/superplan/references/task-tree-design.md#L89) and [consolidation.md:68](../../../../skills/superplan/references/consolidation.md#L68) set affected tasks to `revise`. `not-started` re-enters the frontier; `revise` awaits adjudication — materially different orchestrator behavior. Fix: pick one target status and one default-vs-judgment rule, state it in the contract, and have the superplan surfaces point to it (superplan-side fix tracked in [06-protocol-updates](../06-protocol-updates/task.md) `## Review Notes`).
   → implemented: contract now says "orchestrator resets…to `not-started` by judgment" ([task-file-contract.md:19](../../../../skills/task-tree/references/task-file-contract.md#L19)); task-tree-design.md:89 and consolidation.md:68 updated to use `not-started` ([task-tree-design.md:89](../../../../skills/superplan/references/task-tree-design.md#L89), [consolidation.md:68](../../../../skills/superplan/references/consolidation.md#L68)).
3. **MINOR** — [SKILL.md:20](../../../../skills/task-tree/SKILL.md#L20) "a parent is `approved` only when all children are `approved`" is false under parked-child exclusion: `compute_status` returns `approved` for 2 approved + 1 archived ([_task_io.py:578](../../../../skills/task-tree/scripts/_task_io.py#L578)). Fix: "all *active* (non-parked) children," or point to the contract instead of restating.
   → implemented: rewrote SKILL.md:20 to "all active (non-parked) children are `approved`; `archived` and `postponed` children are excluded from the rollup computation" ([SKILL.md:20](../../../../skills/task-tree/SKILL.md#L20)).
4. **MINOR** — [commands.md §Bulk status operations](../../../../skills/task-tree/references/commands.md) documents `status propagate` and `status cascade` but not `superra task status fix` ([cli.py:530](../../../../skills/task-tree/scripts/cli.py#L530)), despite commands.md owning the full mutation command surface per CLAUDE.md. Fix: add a one-line `status fix` entry.
   → implemented: added `superra task status fix` to commands.md §Bulk status operations with a one-line description ([commands.md §Bulk status operations](../../../../skills/task-tree/references/commands.md)).
