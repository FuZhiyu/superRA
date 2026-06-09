---
title: "Author Superplan Task-Tree Design Protocol"
status: not-started
depends_on: 
  - 01-reference-ownership

tags: []
created: 2026-06-09
---

## Objective

Author the superplan-owned task-tree design protocol.

The reference should teach mechanisms, not a scenario tree. Use positive instructions that guide what the planner does:

- **Find the durable home.** Place work where the result should live after integration, using implementation surface, artifact ownership, and future maintenance concern as the main signals.
- **Prefer depth over breadth.** Test whether an existing child concern can widen before adding a sibling. A child covers new work when it owns the durable concern even if its current objective names only a narrower slice.
- **Rewrite current-state objectives.** When scope expands, rewrite the owning objective so it is self-sufficient with the widened scope, and add `## Revision Notes` when the change is non-obvious.
- **Branch for review value.** Create children when each child has a meaningful objective, evidence trail, and review verdict. Keep tightly coupled steps in one task when correctness is judged as one unit.
- **Use dependencies for prerequisites.** A branch may be serial, parallel, or mixed. `depends_on` expresses execution order among sibling review units; it does not justify or reject a split by itself.
- **Model parent vs sibling context.** Put durable shared assumptions, conventions, and constraints on the lowest parent whose subtree inherits them. Use sibling dependencies for ordered peer work; have downstream objectives name the upstream output or finding they consume.
- **Choose direct revision vs temporary update task.** For simple changes, reopen the existing owning task(s), rewrite objectives, add revision notes, and set affected approved tasks to `revise`. For complex changes, create a temporary child under the durable home for implementation/review.
- **Expire update tasks at integration.** Mature temporary update tasks into the durable owning task(s), preserving validated findings in `## Results` and leaving the tree as latest-state structure.
- **Mature action-verb parents.** When an action-named task becomes the long-lived owner of a concern, rewrite or rename it to the durable concern it now represents.
- **Create a broader parent when needed.** When existing and new work are peers under a broader concern that is not represented, create that parent and move both under it.

### Inputs

Incorporate the motivating examples as evidence without making them special-case rules:

- `postponed-status` is a niche task-system status-model update that should not survive as a level-1 workstream.
- A semantic `task move` command belongs to the CLI command surface that will own it, while restructuring provenance belongs in context.

### Validation

- `skills/superplan/SKILL.md` points to this reference for entry placement, task splitting, context distillation, user-driven task-tree changes, and retroactive task-tree creation.
- The reference gives enough guidance for a planner to decide between direct edits, temporary subtasks, new durable parents, and sibling/root additions.
- The wording is mostly positive, concise, and owner-local under the AGENTS.md DRY/Necessity gate.

## Results
