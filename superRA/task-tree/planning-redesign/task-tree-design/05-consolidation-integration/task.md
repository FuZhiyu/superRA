---
title: "Redesign Consolidation and Integration Cleanup"
status: approved
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

- `postponed-status` should be treated as a task-tree status-model update, not a durable root-level workstream.
- A prior `status-consolidation` action parent should either merge into the durable status-design owner or be reframed/renamed as the durable status-model concern.

### Validation

- The integration Consolidation Gate cannot report clean-enough while an approved temporary update task survives as a misplaced durable subtree.
- Consolidation instructions explicitly include objective rewrites and status invalidation for scope expansion.
- The final path into `Document` assumes the tree already represents latest state.

## Results

Implemented the consolidation/integration cleanup redesign on the owned surfaces.

- [consolidation.md](../../../../../skills/superplan/references/consolidation.md#L12) now treats surviving temporary update scaffolding and action-verb parents as integration-blocking consolidation symptoms, with `status-consolidation` covered as a mature-or-merge example.
- [consolidation.md](../../../../../skills/superplan/references/consolidation.md#L26) now runs `superra task check --category placement` as advisory evidence, then applies the superplan durable-home and update-task lifecycle rules whole-tree across task and subtree levels.
- [consolidation.md](../../../../../skills/superplan/references/consolidation.md#L40) adds **Mature/Rename** for action-verb tasks that become stable durable concerns, and [consolidation.md](../../../../../skills/superplan/references/consolidation.md#L47) adds **Scope Expansion Rewrite** for current-state objective rewrites, scope-defining `script` / `input` / `output` updates, downstream status invalidation, and stale delta cleanup.
- [consolidation.md](../../../../../skills/superplan/references/consolidation.md#L104) preserves the approval gate for material merge, prune, restructure, mature/rename, and status-invalidating scope-expansion changes, with the approved proposal as authority over advisory placement warnings.
- [SKILL.md](../../../../../skills/superintegrate/SKILL.md#L244) routes the Consolidation Gate through `superplan/references/task-tree-design.md`, checks approved and in-flight update tasks across the affected tree, and makes a clean-enough verdict invalid while temporary update scaffolding or unmatured action-verb parents survive before Document.

Verification:

- `python3 skills/report-in-markdown/scripts/check_markdown.py skills/superplan/references/consolidation.md skills/superintegrate/SKILL.md` passed with both files reported clean.
- `./superRA/superra task check --category placement` passed with no issues in the current task tree.
- Targeted `rg` confirmed the required behaviors are present: `Mature/Rename`, `Scope Expansion Rewrite`, `task check --category placement`, `approved or in-flight`, `clean-enough verdict is invalid`, `latest state`, and `status-consolidation`.

## Review Notes

*Retrospective audit note (user-requested). MINOR-only; status left `approved` — this deviation from notes-removed-at-approve is intentional.*

1. **[MINOR]** [consolidation.md:20](../../../../../skills/superplan/references/consolidation.md#L20) — the "status-consolidation" example is superRA-repo-internal, baked into a generic skill shipped to downstream research projects where the name means nothing. Fix: replace with a domain-neutral illustration (the objective asked to cover the example in reasoning, not necessarily verbatim in the shipped prose).
