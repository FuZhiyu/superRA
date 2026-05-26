---
title: "Consolidate to a single status field"
status: not-started
review_status: ~
integration_status: ~
depends_on:
  - agent-interface
tags:
  - status
  - simplification
created: 2026-05-26
updated: 2026-05-26
---

## Objective

Drop `review_status` and `integration_status` from task frontmatter. Merge both into the single `status` field. Today, implementers set both `status: implemented` and `review_status: implemented` on commit — two writes for one event. Frontier computation and rollup only consume `status`, so the other fields are tracked but never auto-consumed. This makes auto-computation fragile and the protocol confusing.

**Target state:** A single `status` field with a clear state machine:

```
not-started → in-progress → implemented → revise → approved
```

- **Implementer** owns transitions up to `implemented` (and `revise → implemented` on fix rounds).
- **Reviewer** owns `implemented → revise` and `implemented → approved`.
- **Workflow phase is inferred** from the subtree's status distribution, not stored.
- Frontier computation, rollup, and dashboard rendering all use `status` directly.

No `## Workflow Status` section in task files. Phase inference is recursive — any subtree is a self-contained workflow.

**Deferred:** Rearchitecting the integration workflow to be scope-flexible (single task, subtree, or branch-wide) and to reuse `status` for its revise cycle. Tracked separately under `agent-interface`. This task focuses on removing the redundant fields from the data model and updating all consumers.

**Scope:** task-system data layer, CLI scripts, SKILL.md, agent specs, workflow skills (implementation-workflow, agent-orchestration, planning-workflow), dashboard rendering, migration of existing `.plan/` trees, and tests.

## Review Notes

1. **[MAJOR] Task 01 vs task 10 contradiction on `task_check.py` scope.**
   → implemented: Aligned both to read-only. Removed `--fix` from task 01 item 9, updated item 4 to reference `task_check.py` reports (not `--fix`).

2. **[MAJOR] Task 06 omits `integration-workflow/SKILL.md`.**
   → implemented: Added `skills/integration-workflow/SKILL.md` to task 06 with section-level references for all `integration_status` occurrences.

3. **[MAJOR] `archived` status data-layer changes have no clear owner.**
   → implemented: Added `archived` implementation to task 02 (new §Add archived status section: `VALID_STATUSES`, `compute_status()`, `compute_frontier()`). Fixed task 03 to note frontier/rollup logic lives in `_task_io.py`, not `task_query.py`.

4. **[MAJOR] Task 07 (dashboard) contains a contradictory line.**
   → implemented: Rewrote task 07 as verification-first. Removed "integration_status stays unchanged." Added `archived` badge/color to scope.

5. **[MINOR] Task 06 references specific line numbers in workflow skills.**
   → implemented: Replaced all line numbers with section heading references (e.g., "§Step 2 (Execute Tasks)").

6. **[MINOR] Task 02 title/objective mismatch with full scope.**
   → implemented: Title now "Update core data layer: remove stale fields, add archived status".

## Results
