---
title: "Author Superplan Task-Tree Design Protocol"
status: approved
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

- `postponed-status` is a niche task-tree status-model update that should not survive as a level-1 workstream.
- A semantic `task move` command belongs to the CLI command surface that will own it, while restructuring provenance belongs in context.

### Validation

- `skills/superplan/SKILL.md` points to this reference for entry placement, task splitting, context distillation, user-driven task-tree changes, and retroactive task-tree creation.
- The reference gives enough guidance for a planner to decide between direct edits, temporary subtasks, new durable parents, and sibling/root additions.
- The wording is mostly positive, concise, and owner-local under the AGENTS.md DRY/Necessity gate.

## Results

### Key Findings
- Authored the superplan-owned task-tree design protocol in [task-tree-design.md](../../../../../skills/superplan/references/task-tree-design.md#L36-L108). It now covers durable-home placement, widening existing concerns before adding breadth, review-value task splits, prerequisite-only dependency semantics, direct objective revision versus temporary update tasks, parent/sibling context, broader-parent creation, update-task expiry at integration, and action-verb parent maturation.
- Incorporated the motivating cases as examples of durable-home placement without special-case branching: semantic `task move` belongs to the CLI command surface, and a niche `postponed-status` update belongs under the task-tree status-model concern ([task-tree-design.md:65](../../../../../skills/superplan/references/task-tree-design.md#L65)).
- Repointed `superplan` to the reference for task-tree design judgment, entry placement, context distillation, splitting, revision notes, user-driven tree changes, and retroactive task-tree creation while removing duplicated mechanics from the top-level skill file ([SKILL.md:18](../../../../../skills/superplan/SKILL.md#L18), [SKILL.md:28](../../../../../skills/superplan/SKILL.md#L28), [SKILL.md:78](../../../../../skills/superplan/SKILL.md#L78), [SKILL.md:86](../../../../../skills/superplan/SKILL.md#L86), [SKILL.md:190](../../../../../skills/superplan/SKILL.md#L190), [SKILL.md:214](../../../../../skills/superplan/SKILL.md#L214)).

### Verification
- `python3 skills/report-in-markdown/scripts/check_markdown.py skills/superplan/SKILL.md skills/superplan/references/task-tree-design.md superRA/task-tree/planning-redesign/task-tree-design/02-tree-design-protocol/task.md` passed: all three files reported `clean`.
- `./superRA/superra task check` passed: `All checks passed. No issues found.`
- `rg -n "task-tree/references/planning|references/planning\\.md" skills/superplan skills/task-tree skills/using-superra agents README.md AGENTS.md -g '*.md' -g '*.toml'` returned no matches for the old task-tree planning reference in the active ownership surfaces checked.

## Review Notes

*Retrospective audit notes (user-requested). MINOR-only; status left `approved` — this deviation from notes-removed-at-approve is intentional.*

1. **[MINOR]** [task-tree-design.md:32](../../../../../skills/superplan/references/task-tree-design.md#L32) restates "the tree is recursive / the top task is not a special semantic owner", already carried by [task-file-contract.md:9](../../../../../skills/task-tree/references/task-file-contract.md#L9). One owner; the other points.
2. **[MINOR]** [task-tree-design.md:65](../../../../../skills/superplan/references/task-tree-design.md#L65) bakes superRA-repo-internal motivating examples (`task move`, `postponed-status`) into a generic skill shipped to downstream research projects, where these names mean nothing. Fix: translate to domain-neutral illustrations.
3. **[MINOR]** [task-tree-design.md:28](../../../../../skills/superplan/references/task-tree-design.md#L28) — "Existing task files without `## Planner Guidance` remain valid" duplicates the contract's optional-section rule; keep only the do-not-bulk-migrate behavior. [task-tree-design.md:121](../../../../../skills/superplan/references/task-tree-design.md#L121) — retroactive step 7 ("Run `superra dashboard`") fails the Necessity test: it shapes no tree-creation behavior.
