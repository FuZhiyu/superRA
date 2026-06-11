---
title: "Task Tree Consolidation"
status: approved
depends_on: []
tags: []
created: 2026-05-25
---

## Objective

Create `skills/planning-workflow/references/consolidation.md` — a protocol for proactively cleaning up messy task trees that have accumulated overlapping, redundant, or poorly-structured tasks over interactive work sessions. Also add a routing hook in the integration-workflow so consolidation can be triggered during integration.

### When consolidation is needed

Over time, as researchers work interactively — adding tasks ad hoc, pivoting scope, doing quick updates between sessions — the task tree can accumulate structural debt:
- **Overlapping tasks** — two tasks with substantially similar objectives or overlapping outputs
- **Hidden dependencies** — task A uses output from task B but doesn't declare `depends_on`
- **Stale tasks** — objectives superseded by another task's results or a scope change, not cleaned up
- **Granularity mismatch** — tasks too large (should split) or too small (should merge with siblings)
- **Orphan tasks** — disconnected from the dependency graph when they should be connected
- **Redundant nesting** — a parent with a single child where the parent adds no context

### What the reference must cover

**1. Survey Protocol**

How to systematically assess the tree:
- Read all `task.md` files and map objectives, dependencies, statuses, inputs/outputs
- Build a relationship matrix: shared inputs, shared outputs, sequential logic, overlapping scope
- Identify which issues from the list above apply

**2. Classification**

For each identified issue, classify the appropriate action:
- **Merge** — combine overlapping tasks: rewrite objective to cover both scopes, update dependencies, cascade status changes (use the more conservative status of the two)
- **Link** — add missing dependencies: update `depends_on` frontmatter
- **Prune** — remove stale/superseded tasks: delete directory, update siblings that referenced them
- **Split** — adjust granularity: create subtasks from a too-large task, or promote subtasks to siblings
- **Restructure** — move tasks to a better location in the tree (change parent), using the placement pecking order from the entry-and-placement task as guidance
- **Flatten** — remove redundant nesting: if a parent has a single child and adds no context, absorb the child's content into the parent

**3. User Approval Gate**

Consolidation is a structural change to the tree. Present a consolidation proposal before executing:
- Show current tree structure (via `task_query.py --tree`)
- Show proposed tree structure
- For each change: what's being consolidated and why
- Wait for user approval before executing

**4. Execution Mechanics**

- Apply changes using `task_create.py`, `task_rename.py`, `task_link.py`, or direct file edits
- Status cascading: when merging, use the more conservative status; when restructuring, preserve statuses where possible
- Run `task_query.py --tree` after changes to verify: no cycles, no broken `depends_on`, no orphans, structure is clean
- Commit atomically — all changed task files in one commit

**5. Relationship to Existing Mechanisms**

Consolidation complements (does not replace) these existing mechanisms:
- `§User Feedback and Changing the Task Tree` — handles individual reactive changes; consolidation is a proactive sweep
- `§Splitting Tasks` / `§Placing Work in the Tree` — structural heuristics applied during planning; consolidation applies them retroactively
- `§Stale Content Checklist` — content-level cleanup; consolidation is structure-level cleanup

### Integration-workflow hook

Add a brief section or note in `skills/integration-workflow/SKILL.md` (likely in §When to Lighten or as a new subsection between Sync and Integrate) that routes to consolidation when the tree has grown complex. Consolidation during integration is optional and triggered by the orchestrator's assessment or the user's request — it's not a mandatory step.

### Files to create/modify

- `skills/planning-workflow/references/consolidation.md` (NEW)
- `skills/integration-workflow/SKILL.md` — small addition routing to consolidation

### Validation criteria

- The protocol can run standalone (user asks to clean up) or as part of integration
- User approval is required before destructive changes (prune, merge)
- Actions are reversible via git (atomic commit provides undo)
- No DRY violations with §User Feedback and Changing the Task Tree or §Stale Content Checklist
- The consolidation reference is loadable without loading the full planning-workflow skill
- Integration-workflow hook is minimal — a routing pointer, not duplicated protocol

## Results

### Deliverables

1. **Created** [skills/superplan/references/consolidation.md](../../../../skills/superplan/references/consolidation.md) (formerly `skills/planning-workflow/references/consolidation.md` — renamed at skill-rename) — standalone consolidation protocol covering: symptom identification, survey protocol (using `task_query.py --tree` and `--dag`), issue classification table (merge/link/prune/split/flatten/restructure), user approval gate with proposal format example, execution mechanics with dependency-ordered application and post-verification, stale content sweep, and atomic commit discipline.

2. **Modified** [skills/superintegrate/SKILL.md](../../../../skills/superintegrate/SKILL.md) (formerly `skills/integration-workflow/SKILL.md` — renamed at skill-rename) — added one bullet in §When to Lighten routing to the consolidation reference when tree structural debt is noticed during integration. Minimal pointer, no duplicated protocol.

### Validation Against Criteria

- Standalone and integration use: the reference has a §Standalone vs Integration Use section explicitly covering both paths.
- User approval required: §User Approval Gate requires explicit confirmation before any destructive changes, with a concrete proposal format example.
- Git reversibility: §Execution Mechanics prescribes atomic commits so `git revert` undoes the full consolidation.
- No DRY violations: the reference explicitly states it complements (does not replace) §User Feedback and Changing the Task Tree, §Splitting Tasks, and §Stale Content Checklist — it points to them rather than restating their content.
- Standalone loadable: the reference opens with its own load condition and context; it does not require the full planning-workflow skill to be loaded first.
- Integration-workflow hook is minimal: one bullet in §When to Lighten, routing to the reference by path.