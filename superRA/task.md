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

## Integration Notes

- [task-system/task-root-rename](task-system/task-root-rename/task.md): researcher confirmed `better-handoff` as the Sync base for the task-root rename integration.
- [task-system/task-root-rename](task-system/task-root-rename/task.md): synced with `better-handoff` through `981715dbb01eb99085d664778a121ce1a0d09f2c` (merge `104d96f3`, sync-map commit `35ba610e`, sync review `083c2d20`), post-sync integration reviewed APPROVED at `1bfed861`, and final checks passed (`uv run pytest skills/task-system/scripts/test_task_system.py skills/task-system/scripts/test_dashboard.py skills/task-system/scripts/test_worktree_selector.py skills/task-system/scripts/tests/test_state_preservation.py`, 369 passed; `uv run pytest skills/codex-superra-setup/scripts/test_sync_codex_agents.py`, 6 passed; `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check`; `python3 skills/task-system/scripts/task_check.py`; `git diff --check 981715dbb01eb99085d664778a121ce1a0d09f2c..HEAD`).
- [task-system/planning-redesign/planmd-sweep](task-system/planning-redesign/planmd-sweep/task.md): researcher chose manual integration checks rather than drift/static tests for the protocol-level results; integration base for this worktree is `better-handoff`.
- [task-system/planning-redesign/planmd-sweep](task-system/planning-redesign/planmd-sweep/task.md): synced with `better-handoff` through `19457675bf570a079bc960765a1832736cddf918`, sync reviewed, integration reviewed, task-tree consolidation completed, and targeted tests passed (`uv run pytest skills/task-system/scripts/test_task_system.py skills/task-system/scripts/tests/test_state_preservation.py skills/codex-superra-setup/scripts/test_sync_codex_agents.py`, 205 passed).
- [task-system/dashboard/view-navigation](task-system/dashboard/view-navigation/task.md): synced onto `better-handoff` through `aad548e35d8309d386ce9a6f68b1f4c820502276` (merge `018a4f88`), sync reviewed APPROVED, integration reviewed APPROVED; pruned the now-dead `Task.has_child_dependency_graph()` and added card-flow tests (244 passing).
- [task-system/codex-task-hooks](task-system/codex-task-hooks/task.md): merged `plan/codex-task-hooks` into `better-handoff` from base `66693ccf`. Conflict resolution kept the base branch's committed template-backed standalone dashboard exporter and applied the incoming `updated` metadata removal through the shared task data layer and `templates/summary_bar.html`; unrelated in-flight subtree Share/export work was stashed out before verification and is not part of this sync. `.plan/**/task.md` frontmatter now omits `updated`. Verification passed on a clean tree: `uv run pytest skills/task-system/scripts/test_task_system.py skills/task-system/scripts/test_dashboard.py skills/task-system/scripts/tests/test_state_preservation.py` (288 passed) and `python3 skills/task-system/scripts/task_check.py --plan-root .plan`.
