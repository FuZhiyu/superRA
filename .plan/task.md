---
title: "Better Handoff"
status: in-progress
depends_on: []
tags: []
created: 2026-05-23
updated: 2026-05-31
---

## Objective

Improve the superRA handoff system — task tracking, planning artifacts, and human-readable visualization.

## Integration Notes

- [task-system/planning-redesign/planmd-sweep](task-system/planning-redesign/planmd-sweep/task.md): researcher chose manual integration checks rather than drift/static tests for the protocol-level results; integration base for this worktree is `better-handoff`.
- [task-system/planning-redesign/planmd-sweep](task-system/planning-redesign/planmd-sweep/task.md): synced with `better-handoff` through `a73e1c2461f7de38494ed682e769ea648e30b13e`, sync reviewed, integration reviewed, and targeted tests passed (`uv run pytest skills/task-system/scripts/test_task_system.py skills/task-system/scripts/tests/test_state_preservation.py skills/codex-superra-setup/scripts/test_sync_codex_agents.py`, 200 passed).

## Sync Map

**Base branch:** `better-handoff`
**Pre-sync merge base:** `a73e1c2461f7de38494ed682e769ea648e30b13e`
**Synced base head:** `5b518470d17657bcbfe482cb0766dde9eadaa949`
**Incoming range:** `a73e1c2461f7de38494ed682e769ea648e30b13e..5b518470d17657bcbfe482cb0766dde9eadaa949`
**Sync commits:** `6efc4ea1` plus this Sync Map commit
**Sync review status:** `IMPLEMENTED`

### Branch Summary

**Incoming intent:** Base-current task-edit-discipline work abandons the earlier revision-note auto-mutation / reviewer-doc cleanup track and collapses it into a single warn-only `revnote-warning` task. The code removes hook auto-mutation, adds a non-destructive `validate_plan` warning for approved tasks that still carry real `## Revision Notes`, and updates tests and task-system docs for that narrower behavior.
**Resolution thesis:** The sync accepts the base-current warn-only pivot wholesale while preserving this branch's task-results migration under [task-system/planning-redesign/planmd-sweep](task-system/planning-redesign/planmd-sweep/task.md). The two workstreams are compatible: base owns revision-note warning behavior; this branch owns task-result primacy, parent rollups, and final-form removal.

### Sync Clusters

> **Sync cluster `revnote-warning-pivot` (2026-05-31):** commits `49804721`, `5b518470`; paths `.plan/task-system/task-edit-discipline/**`, `skills/task-system/SKILL.md`, `skills/task-system/references/planning.md`, `skills/task-system/scripts/_task_io.py`, `skills/task-system/scripts/task_hook.py`, `skills/task-system/scripts/test_task_system.py`; affects Tasks `task-system/task-edit-discipline`.
> **Incoming intent:** Replace the risky revision-note auto-mutation design with a warning-only validation rule and collapse the previous `revnote-status-sync` / `revnote-docs` task split into `revnote-warning`.
> **Sync resolution:** Accepted the incoming task-tree collapse, hook/test rewrite, and docs wording. Preserved the branch's consolidated task-results record and parent/root pointers to `planning-redesign/planmd-sweep`.
> **Integration context:** Integration review should treat `revnote-warning` as the base-current task-edit-discipline frontier and should not expect reviewer-spec regeneration for the abandoned `revnote-docs` path.
> **User decision:** None during this sync; incoming commits already record the researcher's warn-only decision.
