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
- [task-system/planning-redesign/planmd-sweep](task-system/planning-redesign/planmd-sweep/task.md): synced with `better-handoff` through `19457675bf570a079bc960765a1832736cddf918`, sync reviewed, integration reviewed, task-tree consolidation completed, and targeted tests passed (`uv run pytest skills/task-system/scripts/test_task_system.py skills/task-system/scripts/tests/test_state_preservation.py skills/codex-superra-setup/scripts/test_sync_codex_agents.py`, 205 passed).

## Sync Map

**Base branch:** `better-handoff`
**Pre-sync merge base:** `95a2a613a36e55fd63d674198baeafa3ba649ffd`
**Synced base head:** `aad548e35d8309d386ce9a6f68b1f4c820502276`
**Incoming range:** `95a2a613a36e55fd63d674198baeafa3ba649ffd..aad548e35d8309d386ce9a6f68b1f4c820502276`
**Sync commits:** `018a4f88b8512df34b8745b02311f8e1e8bfdbe3` (merge), plus this Sync Map / task-local impact commit.
**Sync review status:** `IMPLEMENTED`

### Branch Summary

**Incoming intent:** `better-handoff` advanced the task-system internals: a hook refactor (`task_hook.py` now also reconciles after Bash `mv`/`rm`/`cp` structural moves, propagating parent status across the whole tree and rebuilding the dashboard), revision-note lifecycle automation (`validate_revision_notes` warns when an `approved` task still carries a `## Revision Notes` section, fence-aware via `_has_nonempty_section`), `deprecate-planmd-refs`, task-results-as-primary doc changes (`.plan/` task `## Results` is now the primary researcher-facing record; the separate `RESULTS.md` / `final-form.md` maturation path was removed), the `task-edit-discipline` subtree work, and `.plan/` tree restructuring.

**Resolution thesis:** Both intents are preserved with no ours/theirs override. The incoming hook/doc/validation refactor and this branch's master-detail drill-down dashboard workspace are orthogonal — they touch disjoint code regions in the two shared files (`_task_io.py`, `test_task_system.py`) and the incoming side never touched `plan_dashboard.py`, `base.html`, the new `nav_*`/`node_body` templates, or `test_dashboard.py`. The hook's static rebuild path calls `plan_dashboard.generate_dashboard(plan_root)` and `_task_io.propagate_parent_status`/`walk_plan`/`is_leaf`, all of which still exist with matching signatures after the dashboard rewrite, so the two compose cleanly. The only forced follow-through was removing two now-stale `## Revision Notes` sections that the newly-merged `validate_revision_notes` rule flags.

### Sync Clusters

> **Sync cluster `timestamp-rollup` (2026-05-31):** commits `018a4f88`; paths `.plan/task.md`, `.plan/task-system/task.md`; affects Tasks root, `task-system`.
> **Incoming intent:** routine status-rollup `updated:` bumps plus incoming Integration Notes / results-as-primary objective bullet.
> **Sync resolution:** took incoming `updated: 2026-05-31` on both files (newer than our timestamp-only bump, which carried no intent); kept all incoming content additions.
> **Integration context:** None.
> **User decision:** None.

> **Sync cluster `task-io-additive` (2026-05-31):** commits `018a4f88`; paths `skills/task-system/scripts/_task_io.py`, `skills/task-system/scripts/test_task_system.py`; affects Tasks `dashboard/view-navigation`, `task-edit-discipline/revnote-warning`.
> **Incoming intent:** add `_has_nonempty_section` + `validate_revision_notes` and their tests/hook wiring.
> **Sync resolution:** auto-merged — disjoint regions. Ours kept `Task.has_child_dependency_graph()` and `TestMasterDetailPartials`; incoming kept its validator, `TestHasNonemptySection`/`TestValidateRevisionNotes`/`TestValidatePlanRevisionNotes`, and the Bash-move hook tests. All assertions on both sides preserved.
> **Integration context:** `Task.has_child_dependency_graph()` (our `_task_io.py`) is now dead code — its only caller was the per-subtree mermaid DAG panel removed in `main-panel`'s "remove mermaid" commit. Not removed during sync (codebase-coherence dead-code pruning belongs to Integrate). The `validate_revision_notes` rule is warn-only (the hook always exits 0); it does not gate any dashboard behavior.
> **User decision:** None.

> **Sync cluster `revnote-stale-cleanup` (2026-05-31):** commits `018a4f88`; paths `.plan/task-system/dashboard/view-navigation/task.md`, `.plan/task-system/dashboard/live-server/templates/task.md`; affects Tasks `dashboard/view-navigation`, `dashboard/live-server/templates`.
> **Incoming intent:** the merged-in `validate_revision_notes` rule says an `approved` task should not carry a `## Revision Notes` section (the reviewer removes it at approval); incoming dogfooded this by cleaning its own flagged notes.
> **Sync resolution:** removed the stale `## Revision Notes` section from both approved tasks the rule flags. `validate_plan(.plan)` now returns 0 warnings (was 2). Design history they recorded is already captured in each task's `## Objective` / `## Design Principles`. No code or result change.
> **Integration context:** None — purely task-doc cleanup forced by the new validation contract.
> **User decision:** None.
