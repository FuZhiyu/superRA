---
title: "Task Companion Files and Dashboard"
status: approved
depends_on: []
---

## Objective

Give every task one version-controlled `attachments/` workspace for small companion files that support the task without becoming permanent project code, and make those files first-class reading surfaces in the dashboard.

- Distinguish ephemeral scratch, retained task-local companions, and permanent project artifacts; require retained files to be reproducible and linked from the owning task's `## Results`.
- Keep the storage boundary simple: every retained task-local file goes under `attachments/`. Immediate directories containing `task.md` are subtasks, while `attachments/` is always a non-task asset container.
- Promote shared, pipeline-critical, or promised deliverables into project-conventional paths during Integrate, before integration review. Mature & Consolidate must retain, relocate, or drop the companion files that remain task-local without breaking their links.
- Let the live and standalone dashboards expose a collapsed Attachments pseudo-branch beneath the owning task and render selected Markdown, Python, Julia, R, notebook, image, PDF, and text files in the normal full-width detail pane. Attachment nodes participate in navigation only; they never become task-tree, DAG, status-rollup, frontier, or Kanban nodes.
- Verify instruction behavior with a realistic harness exercise and dashboard behavior with focused and full task-tree tests.

### Generated artifacts

Canonical role specs are outside the intended scope, so no generated role outputs should change. If implementation expands into `agents/*`, follow the generated-artifact protocol in the repo-root contributor guide: regenerate `skills/using-superra/references/direct-mode-implementer.md`, `skills/using-superra/references/direct-mode-reviewer.md`, `.codex/agents/superra_implementer.toml`, and `.codex/agents/superra_reviewer.toml` with `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project`; never hand-edit them.

## Planner Guidance

The repository already carries figures in task-local `attachments/`, moves the whole task directory, rewrites links in every Markdown file under a moved task, and runs Markdown integrity checks on sidecars. The missing capability is the lifecycle contract plus dashboard discovery, safe delivery, hot reload, rendering, and export.

Put every retained task-local file in `attachments/`. The agent-facing contract should name that destination without teaching a nesting policy; the dashboard and file APIs should tolerate recursively generated attachment layouts as an implementation detail. Do not require a manifest file; the owning `## Results` is the concise provenance and entry-point record.

The existing [HTML Dashboard](../dashboard/task.md) concern covers dashboard behavior but not the cross-workflow storage and promotion contract, so this work is a sibling durable concern under Task Tree Skill. The contract lands first; the backend data path and user interface then follow in dependency order.

## Critical Files

- [using-superra/SKILL.md](../../../skills/using-superra/SKILL.md) — universal task interface loaded by main agents, implementers, reviewers, and direct mode
- [task-file-contract.md](../../../skills/task-tree/references/task-file-contract.md) — current task anatomy, results lifecycle, and figure-attachment contract
- [mature-consolidate.md](../../../skills/superintegrate/references/mature-consolidate.md) — durable-home and directory-fold decisions for retained evidence
- [plan_dashboard.py](../../../skills/task-tree/scripts/plan_dashboard.py) — task discovery, routes, watchers, search/export state, and standalone rendering
- [dashboard.js](../../../skills/task-tree/scripts/templates/dashboard.js) — active-task navigation and client-side Markdown rendering

## Results

The approved companion-file lifecycle and dashboard now use one storage boundary
and one reading surface:

- The [companion-file contract](01-artifact-contract/task.md#results) requires every retained task-local file under `attachments/`; only `task.md` and child-task directories occupy the task directory itself. It distinguishes scratch, retained evidence, and permanent project artifacts; requires reproducibility metadata; and promotes shared or maintained artifacts before Integrate closes.
- The [attachment-only data path](02-dashboard-artifact-data/task.md#results) recursively discovers and serves only `attachments/`, with bounded no-follow descriptor reads shared by previews, downloads, and standalone attachment images. Direct files are excluded, and attachment nodes remain outside task discovery and status semantics.
- The [tree-native attachment UI](03-dashboard-artifact-ui/task.md#results) removes the Files modal. A collapsed Attachments pseudo-branch lives beneath each owning task, while selected Markdown, highlighted source, notebooks, images, PDFs, and text render in the normal full-width detail pane with URL/history, live refresh, standalone, worktree, and unified keyboard-tree behavior.

Independent review approved all three children. The full task-tree suite passed
`772` tests with four known non-failing warnings; dedicated installed-Chromium
regressions cover rendering, sanitization, hot reload, worktree isolation, and
the unified attachment/task navigation model.
