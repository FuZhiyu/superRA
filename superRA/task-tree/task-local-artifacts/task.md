---
title: "Task Companion Files and Dashboard"
status: approved
depends_on: []
---

## Objective

Make each `superRA/<task>/` directory a flat, version-controlled workspace for small companion files that support one task without becoming permanent project code, and make those files legible in the dashboard.

- Distinguish ephemeral scratch, retained task-local companions, and permanent project artifacts; require retained files to be reproducible and linked from the owning task's `## Results`.
- Keep the visible layout and task model simple: Markdown notes, Python/Julia/R scripts, and Jupyter notebooks may sit directly beside `task.md`; generated outputs, supporting data, and other retained files go in `attachments/`. Immediate directories containing `task.md` are subtasks, while `attachments/` is always a non-task asset container.
- Promote shared, pipeline-critical, or promised deliverables into project-conventional paths during Integrate, before integration review. Mature & Consolidate must retain, relocate, or drop the companion files that remain task-local without breaking their links.
- Let the live and standalone dashboards browse direct companions and attachments, safely render Markdown, Python, Julia, R, and the common static subset of Jupyter notebooks, and open or download other files across worktrees and custom/rootless task roots. Files never become task-tree, DAG, status-rollup, frontier, or Kanban nodes.
- Verify instruction behavior with a realistic harness exercise and dashboard behavior with focused and full task-tree tests.

### Generated artifacts

Canonical role specs are outside the intended scope, so no generated role outputs should change. If implementation expands into `agents/*`, follow the generated-artifact protocol in the repo-root contributor guide: regenerate `skills/using-superra/references/direct-mode-implementer.md`, `skills/using-superra/references/direct-mode-reviewer.md`, `.codex/agents/superra_implementer.toml`, and `.codex/agents/superra_reviewer.toml` with `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project`; never hand-edit them.

## Planner Guidance

The repository already carries figures in task-local `attachments/`, moves the whole task directory, rewrites links in every Markdown file under a moved task, and runs Markdown integrity checks on sidecars. The missing capability is the lifecycle contract plus dashboard discovery, safe delivery, hot reload, rendering, and export.

Put first-class companion documents and code—`.md`, `.py`, `.jl`, `.r`/`.R`, and `.ipynb`—directly beside `task.md`. Put generated outputs, supporting data, and every other retained file in `attachments/`. The agent-facing contract should name that destination without teaching a nesting policy; the dashboard and file APIs should tolerate recursively generated attachment layouts as an implementation detail. Do not require a manifest file; the owning `## Results` is the concise provenance and entry-point record.

The existing [HTML Dashboard](../dashboard/task.md) concern covers dashboard behavior but not the cross-workflow storage and promotion contract, so this work is a sibling durable concern under Task Tree Skill. The contract lands first; the backend data path and user interface then follow in dependency order.

## Critical Files

- [using-superra/SKILL.md](../../../skills/using-superra/SKILL.md) — universal task interface loaded by main agents, implementers, reviewers, and direct mode
- [task-file-contract.md](../../../skills/task-tree/references/task-file-contract.md) — current task anatomy, results lifecycle, and figure-attachment contract
- [mature-consolidate.md](../../../skills/superintegrate/references/mature-consolidate.md) — durable-home and directory-fold decisions for retained evidence
- [plan_dashboard.py](../../../skills/task-tree/scripts/plan_dashboard.py) — task discovery, routes, watchers, search/export state, and standalone rendering
- [dashboard.js](../../../skills/task-tree/scripts/templates/dashboard.js) — active-task navigation and client-side Markdown rendering

## Results

Implemented the task-local companion-file lifecycle and dashboard canvas across three approved children:

- The [companion-file contract](01-artifact-contract/task.md#results) now distinguishes disposable scratch, retained task-local evidence, and permanent project artifacts. Markdown, Python, Julia, R, and Jupyter files may sit beside `task.md`; generated outputs, supporting data, and other retained files belong in `attachments/`. Retained files require result links and reproducibility metadata, while shared or maintained artifacts are promoted into project-conventional paths before Integrate closes.
- The [secure artifact data path](02-dashboard-artifact-data/task.md#results) discovers direct companions and recursively generated attachments without admitting files into task discovery, dependencies, status rollups, or mutations. Task-scoped live and standalone APIs enforce worktree/task containment, no-follow reads, bounded traversal and byte budgets, opaque `attachments/`, and transactional link rewriting across move failures.
- The [dashboard Files canvas](03-dashboard-artifact-ui/task.md#results) groups first-class companions, attachments, and neutrally labeled additional files inside the owning task view; task-tree infrastructure such as the root `superra` wrapper stays out of the manifest. It safely renders companion-relative Markdown, Python/Julia/R source, common static Jupyter cells and outputs, images, PDFs, and text; JavaScript, widgets, active MIME types, and unsupported notebook outputs never execute. Task-scoped hot reload preserves task routing and view state, and live/worktree/standalone behavior shares the same artifact payload.

Final verification from the approved branch passed all 773 task-tree tests with four known non-failing fixture/dependency warnings. Independent Chromium review covered keyboard and focus behavior, sanitization, notebook fallbacks, hot reload including oversized transitions, worktree switching, and standalone export. NotebookJS remains a pinned 8,102-byte vendored asset rather than a Jupyter or `nbconvert` dependency.
