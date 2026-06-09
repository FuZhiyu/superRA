---
title: "Extend Planning Review to Task-Tree Design"
status: not-started
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
