---
title: "Extend Planning Review to Task-Tree Design"
status: revise
depends_on: 
  - 02-tree-design-protocol

tags: []
created: 2026-06-09
---

## Objective

Update planning-review instructions so reviewers critique the task tree as a design artifact before implementation.

Planning review should evaluate both handoff clarity and tree design quality. Update the owning planning-review surfaces:

- `skills/superplan/references/planning-review.md`
- `skills/superplan/references/thorough-planning.md` planning-review dispatch context
- any concise pointers in `skills/superplan/SKILL.md`
- role-spec or generated surfaces only if the canonical planning-review contract must change there

### Review Dimensions

Teach planning reviewers to evaluate:

- **Durable ownership:** each task or subtree lives under the concern that should own its result after integration.
- **Depth vs breadth:** existing scopes are widened when that preserves a durable concern; new siblings/root tasks carry a clear durable-home justification.
- **Branching quality:** children are independently reviewable units, not checklist steps; parent tasks carry shared context rather than deliverable work.
- **Dependency quality:** `depends_on` edges express real prerequisites among sibling review units, and serial branches are acceptable when each node has review value.
- **Parent/sibling context:** inherited parent context carries subtree-wide conventions and constraints; downstream sibling objectives name any upstream results they need.
- **Update-task lifecycle:** temporary update tasks are under the durable owner and have an expected merge/maturation path.
- **Action-verb durability:** action-named parents that are meant to persist are reframed as durable concerns.
- **Task clarity:** objectives are self-sufficient, current-state contracts with binding deliverables in `## Objective` and optional route suggestions in `## Planner Guidance`.

### Validation

- `Stage: planning-review` can return blocking findings for poor tree design, not only unclear prose.
- The reviewer writes findings in the assigned planning target's `## Review Notes` per the existing planning-review ownership model.
- The instructions stay concise and point to `task-tree-design.md` for the full design policy instead of duplicating it.

## Results

Updated the planning-review surfaces so a `Stage: planning-review` reviewer may block on task-tree design defects, not only handoff prose.

- [planning-review.md](../../../../../skills/superplan/references/planning-review.md) now points reviewers to the superplan-owned task-tree design policy and names the design dimensions they should cover.
- [thorough-planning.md](../../../../../skills/superplan/references/thorough-planning.md) now makes the planner-facing mode descriptions cover parent/sibling context, durable ownership, depth vs. breadth, branching quality, update-task lifecycle, action-verb durability, and the `task-tree-design.md` policy pointer.
- No role specs or generated surfaces changed: [reviewer.md](../../../../../agents/reviewer.md) already delegates `Stage: planning-review` to the manifest-loaded planning-review reference.

Verification:

- `python3 skills/report-in-markdown/scripts/check_markdown.py skills/superplan/references/planning-review.md skills/superplan/references/thorough-planning.md superRA/task-tree/planning-redesign/task-tree-design/04-planning-review/task.md`
- `./superRA/superra task check`

## Review Notes

1. **[MAJOR]** DRY drift introduced by this task's edits: the design-review dimension list is enumerated in both [thorough-planning.md:95](../../../../../skills/superplan/references/thorough-planning.md#L95) and [planning-review.md:11](../../../../../skills/superplan/references/planning-review.md#L11), and the two lists already disagree (assumptions / artifact pipeline / domain reasoning / unresolved tradeoffs appear only in the planner-facing copy; parent-sibling context / dependency quality / objective-guidance split only in the reviewer-facing copy). Both defer to `task-tree-design.md` "for the full policy", so neither enumeration is authoritative — the exact paraphrase-drift the CLAUDE.md prose gate blocks. Compounding it, the reviewer's own mode definitions live in the planner-facing file: [planning-review.md:9](../../../../../skills/superplan/references/planning-review.md#L9) sends the dispatched reviewer to thorough-planning.md §Planning Review, which the `Stage: planning-review` manifest row does not load. Fix: move "what each mode evaluates" into planning-review.md (it is reviewer mechanics per the Ownership Boundaries row); reduce both dimension enumerations to a single pointer at [task-tree-design.md](../../../../../skills/superplan/references/task-tree-design.md); leave thorough-planning.md carrying only the planner-side trigger and context-provisioning.
