---
title: "Better Handoff"
status: in-progress
depends_on: []
tags: []
created: 2026-05-23
---

## Objective

Improve the superRA handoff system — task tracking, planning artifacts, and human-readable visualization.

## Conventions

Walk date: 2026-06-01.

`AGENTS.md` / `CLAUDE.md` at repo root is the contributor-facing authority for superRA internals. When modifying skills, hooks, agents, harness adapters, or internal docs, treat the work as skill creation: read owning files before editing, load `skill-creator` before editing `skills/*/SKILL.md`, keep changes focused, verify behavior rather than prose alone, preserve the README/user-facing vs AGENTS/internal separation, and apply the DRY + Necessity gate line by line. Ownership boundaries matter: workflow choreography belongs to `superplan` / `superimplement` / `superintegrate`; dispatch and reviewer-feedback adjudication belong to `agent-orchestration`; task anatomy belongs to `task-system/references/planning.md`; canonical role behavior belongs to `agents/implementer.md` and `agents/reviewer.md`; generated Codex/direct-mode artifacts must be regenerated from sources rather than hand-edited.

`README.md` is the user-facing product overview. It describes superRA as a PLAN -> IMPLEMENT -> INTEGRATE workflow with an implementer-reviewer pair, domain skills layered onto domain-neutral workflow phases, durable `superRA/` task files, and generated Codex named agents installed through `codex-superra-setup`. Keep product framing there; internal contributor rules stay in `AGENTS.md` / `CLAUDE.md`.

No additional `AGENTS.md`, `CLAUDE.md`, or `README.md` files were found under the touched implementation paths (`agents/`, `skills/task-system/`, `skills/superplan/`, `skills/using-superRA/`, `.codex/`, `superRA/review-planning-protocol/`). The walk intentionally did not load unrelated guidance under `skills/theory-modeling/`, `skills/writing/`, or `tests/claude-code/` because this task does not touch those directories.

## Sync Map

**Base branch:** `better-handoff`
**Pre-sync merge base:** `75a86ccebd0ec37a0a9e904f0fd5b824752cf6f1`
**Synced base head:** `876178e32d22ef2643424a584809d782fce4dde9`
**Incoming range:** `75a86ccebd0ec37a0a9e904f0fd5b824752cf6f1..876178e32d22ef2643424a584809d782fce4dde9`
**Sync commits:** `76c2a9af14f93df2612fd34a6c6569ffb57870f2`, `48e5143b7bb2a752c02bdc4f0422e4bec087c1a8`, `7f4535c4cc663b0d995760163be05d986f9ecd82`
**Sync review status:** `APPROVED`

### Branch Summary

**Incoming intent:** The base branch added the PR #29 review-planning follow-up plans (`b36d563f`: not-started `path-containment` plan plus a not-started `review-planning-protocol` plan nested under `planning-redesign/`, with `cli-scripts` and `planning-redesign` status set back to reflect the new pending child) and moved the `dynamic-workflows` workstream off the base branch (`876178e3`: deletes `superRA/dynamic-workflows/*` and removes its mentions from `tree-cleanup`).
**Resolution thesis:** This branch already implemented and approved the same PR #29 follow-up work — `path-containment` and the recursive-context piece — but placed the latter at the top-level `superRA/review-planning-protocol/` tree rather than nested under `planning-redesign/`. The merge keeps this branch's implemented superset for the overlapping plans, accepts the incoming `dynamic-workflows` deletions and `tree-cleanup` edit wholesale, removes the incoming not-started nested `review-planning-protocol` duplicate, and restores the `cli-scripts` / `planning-redesign` statuses to this branch's approved rollup.

### Sync Clusters

> **Sync cluster `pr29-followup-plans` (2026-06-01):** commits `76c2a9af`; paths `superRA/task-system/cli-scripts/path-containment/task.md`, `superRA/task-system/cli-scripts/task.md`, `superRA/task-system/planning-redesign/task.md`, `superRA/task-system/planning-redesign/review-planning-protocol/task.md`; affects Tasks `task-system/cli-scripts/path-containment`, `task-system/cli-scripts`, `task-system/planning-redesign`.
> **Incoming intent:** Seed the PR #29 follow-ups as not-started plans and mark `cli-scripts` (not-started) and `planning-redesign` (in-progress) as having pending follow-up work.
> **Sync resolution:** Kept this branch's implemented superset of `path-containment` (`status: approved` + full `## Results`; Objective/Scope/Validation already identical to incoming, so only frontmatter + Results conflicted, resolved to ours). Verified the incoming nested `review-planning-protocol` objective/scope carried no refinement absent from this branch's top-level `05-recursive-context-conventions` task; removed the not-started nested duplicate. Restored `cli-scripts` and `planning-redesign` to `approved` since this branch completed and rolled up the work the incoming statuses treated as pending.
> **Integration context:** None — no source-code change; task-record reconciliation only.
> **User decision:** None.

> **Sync cluster `dynamic-workflows-move` (2026-06-01):** commits `76c2a9af`; paths `superRA/dynamic-workflows/*`, `superRA/task-system/tree-cleanup/task.md`; affects Tasks `task-system/tree-cleanup`.
> **Incoming intent:** Move the `dynamic-workflows` workstream off `better-handoff` (delete its task files) and drop its mentions from the `tree-cleanup` survey objective/results.
> **Sync resolution:** Accepted the incoming deletions and `tree-cleanup` edit unchanged (this branch did not touch either). Stale-reference sweep: the only remaining `dynamic-workflows` mention is in `review-planning-protocol/task.md` §Integration Status prose, which accurately describes the incoming move and is not a dangling link.
> **Integration context:** None.
> **User decision:** None.

## Integration Notes

- [task-system/task-root-rename](task-system/task-root-rename/task.md): researcher confirmed `better-handoff` as the Sync base for the task-root rename integration.
- [task-system/task-root-rename](task-system/task-root-rename/task.md): synced with `better-handoff` through `981715dbb01eb99085d664778a121ce1a0d09f2c` (merge `104d96f3`, sync-map commit `35ba610e`, sync review `083c2d20`), post-sync integration reviewed APPROVED at `1bfed861`, and final checks passed (`uv run pytest skills/task-system/scripts/test_task_system.py skills/task-system/scripts/test_dashboard.py skills/task-system/scripts/test_worktree_selector.py skills/task-system/scripts/tests/test_state_preservation.py`, 369 passed; `uv run pytest skills/codex-superra-setup/scripts/test_sync_codex_agents.py`, 6 passed; `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check`; `python3 skills/task-system/scripts/task_check.py`; `git diff --check 981715dbb01eb99085d664778a121ce1a0d09f2c..HEAD`).
- [task-system/planning-redesign/planmd-sweep](task-system/planning-redesign/planmd-sweep/task.md): researcher chose manual integration checks rather than drift/static tests for the protocol-level results; integration base for this worktree is `better-handoff`.
- [task-system/planning-redesign/planmd-sweep](task-system/planning-redesign/planmd-sweep/task.md): synced with `better-handoff` through `19457675bf570a079bc960765a1832736cddf918`, sync reviewed, integration reviewed, task-tree consolidation completed, and targeted tests passed (`uv run pytest skills/task-system/scripts/test_task_system.py skills/task-system/scripts/tests/test_state_preservation.py skills/codex-superra-setup/scripts/test_sync_codex_agents.py`, 205 passed).
- [task-system/dashboard/view-navigation](task-system/dashboard/view-navigation/task.md): synced onto `better-handoff` through `aad548e35d8309d386ce9a6f68b1f4c820502276` (merge `018a4f88`), sync reviewed APPROVED, integration reviewed APPROVED; pruned the now-dead `Task.has_child_dependency_graph()` and added card-flow tests (244 passing).
- [task-system/codex-task-hooks](task-system/codex-task-hooks/task.md): merged `plan/codex-task-hooks` into `better-handoff` from base `66693ccf`. Conflict resolution kept the base branch's committed template-backed standalone dashboard exporter and applied the incoming `updated` metadata removal through the shared task data layer and `templates/summary_bar.html`; unrelated in-flight subtree Share/export work was stashed out before verification and is not part of this sync. `.plan/**/task.md` frontmatter now omits `updated`. Verification passed on a clean tree: `uv run pytest skills/task-system/scripts/test_task_system.py skills/task-system/scripts/test_dashboard.py skills/task-system/scripts/tests/test_state_preservation.py` (288 passed) and `python3 skills/task-system/scripts/task_check.py --plan-root .plan`.
- [review-planning-protocol](review-planning-protocol/task.md): synced with `better-handoff` through `75a86ccebd0ec37a0a9e904f0fd5b824752cf6f1` (merge `1d14b1f1`), integration review initially requested DRY/Necessity and task-root evidence fixes (`865f5ed0`), fixes landed in `2afde1d2`, and narrow integration re-review approved at `59d1ee4`. Final validation passed: `uv run pytest skills/task-system/scripts/test_task_system.py skills/task-system/scripts/test_dashboard.py skills/task-system/scripts/test_worktree_selector.py skills/task-system/scripts/tests/test_state_preservation.py skills/codex-superra-setup/scripts/test_sync_codex_agents.py` (379 passed), `python3 skills/task-system/scripts/task_check.py --plan-root superRA`, `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check`, and `git diff --check 75a86ccebd0ec37a0a9e904f0fd5b824752cf6f1..HEAD`.
