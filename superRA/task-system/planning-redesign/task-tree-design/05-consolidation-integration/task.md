---
title: "Redesign Consolidation and Integration Cleanup"
status: not-started
depends_on: 
  - 02-tree-design-protocol

tags: []
created: 2026-06-09
---

## Objective

Redesign consolidation and integration cleanup so the task tree is matured into durable latest-state structure before documentation.

### Required Behavior

- Update `skills/superplan/references/consolidation.md` so consolidation applies the superplan task-tree design protocol whole-tree, comparing tasks and subtrees across levels against their durable owners.
- Update `skills/superintegrate/SKILL.md` Consolidation Gate so it routes through the superplan tree-design owner and checks approved or in-flight update tasks across the affected tree, not only update tasks in the current frontier.
- Add a consolidation action or classification for **mature/rename**: an action-verb task that has become a durable concern is rewritten and optionally renamed to the stable concern it now owns.
- Tighten scope-expansion rewrites: when a task's scope widens, the objective is rewritten as a current-state contract, `script` / `input` / `output` fields are updated when they define scope, affected downstream statuses are invalidated, and stale delta prose is removed.
- Keep temporary update tasks as implementation scaffolding during active work, then fold validated results into the durable owning task(s) during consolidation/integration.
- Use `superra task check --category placement` as an advisory signal alongside the manual whole-tree survey; the human-approved consolidation proposal remains the authority for structural changes.
- Preserve the user approval gate for material restructures, including merge, prune, restructure, mature/rename, and status-invalidating scope expansion.

### Examples to Cover in Reasoning

- `postponed-status` should be treated as a task-system status-model update, not a durable root-level workstream.
- A prior `status-consolidation` action parent should either merge into the durable status-design owner or be reframed/renamed as the durable status-model concern.

### Validation

- The integration Consolidation Gate cannot report clean-enough while an approved temporary update task survives as a misplaced durable subtree.
- Consolidation instructions explicitly include objective rewrites and status invalidation for scope expansion.
- The final path into `Document` assumes the tree already represents latest state.

## Results
