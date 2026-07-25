---
title: "Task Companion Files and Dashboard"
status: not-started
depends_on: []
---

## Objective

Make each `superRA/<task>/` directory a flat, version-controlled workspace for small companion files that support one task without becoming permanent project code, and make those files legible in the dashboard.

- Distinguish ephemeral scratch, retained task-local companions, and permanent project artifacts; require retained files to be reproducible and linked from the owning task's `## Results`.
- Keep the layout flat and the task model unchanged: immediate regular files other than reserved task metadata are companions; immediate directories containing `task.md` are subtasks. Keep `attachments/` as the one backward-compatible non-task directory for existing assets or coherent generated bundles; new work creates no other non-task directories.
- Promote shared, pipeline-critical, or promised deliverables into project-conventional paths during Integrate, before integration review. Mature & Consolidate must retain, relocate, or drop the companion files that remain task-local without breaking their links.
- Let the live and standalone dashboards browse direct companions and backward-compatible attachments, safely render Markdown, source files, and the common static subset of Jupyter notebooks, and open or download other files across worktrees and custom/rootless task roots. Files never become task-tree, DAG, status-rollup, frontier, or Kanban nodes.
- Verify instruction behavior with a realistic harness exercise and dashboard behavior with focused and full task-tree tests.

### Generated artifacts

Canonical role specs are outside the intended scope, so no generated role outputs should change. If implementation expands into `agents/*`, follow the generated-artifact protocol in the repo-root contributor guide: regenerate `skills/using-superra/references/direct-mode-implementer.md`, `skills/using-superra/references/direct-mode-reviewer.md`, `.codex/agents/superra_implementer.toml`, and `.codex/agents/superra_reviewer.toml` with `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project`; never hand-edit them.

## Planner Guidance

The repository already carries figures in task-local `attachments/`, moves the whole task directory, rewrites links in every Markdown file under a moved task, and runs Markdown integrity checks on sidecars. The missing capability is the lifecycle contract plus dashboard discovery, safe delivery, hot reload, rendering, and export.

Put new companion files directly beside `task.md`. Continue to discover and render existing `attachments/` content, and allow that directory for a tool-generated bundle, but do not make agents choose between two normal destinations: flat placement is the default and no other ancillary directory is supported. Do not require a manifest file; the owning `## Results` is the concise provenance and entry-point record.

The existing [HTML Dashboard](../dashboard/task.md) concern covers dashboard behavior but not the cross-workflow storage and promotion contract, so this work is a sibling durable concern under Task Tree Skill. The contract lands first; the backend data path and user interface then follow in dependency order.

## Revision Notes

On 2026-07-25 the researcher chose a flat companion-file model. `attachments/` remains supported for backward compatibility and generated bundles, not as the required destination. The same decision keeps companion files out of the semantic task tree. A dependency review found that a small vendored browser renderer can cover common static `.ipynb` cells and outputs without adding the Jupyter Python or JupyterLab dependency stacks; JavaScript, widgets, and full interactive-output fidelity remain out of scope.

## Critical Files

- [using-superra/SKILL.md](../../../skills/using-superra/SKILL.md) — universal task interface loaded by main agents, implementers, reviewers, and direct mode
- [task-file-contract.md](../../../skills/task-tree/references/task-file-contract.md) — current task anatomy, results lifecycle, and figure-attachment contract
- [mature-consolidate.md](../../../skills/superintegrate/references/mature-consolidate.md) — durable-home and directory-fold decisions for retained evidence
- [plan_dashboard.py](../../../skills/task-tree/scripts/plan_dashboard.py) — task discovery, routes, watchers, search/export state, and standalone rendering
- [dashboard.js](../../../skills/task-tree/scripts/templates/dashboard.js) — active-task navigation and client-side Markdown rendering

## Results
