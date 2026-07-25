---
title: "Task-Local Artifact Workspace and Dashboard"
status: not-started
depends_on: []
---

## Objective

Make `superRA/<task>/attachments/` the version-controlled workspace for small artifacts that support one task without becoming permanent project code, and make that workspace legible in the dashboard.

- Distinguish ephemeral scratch, retained task-local evidence, and permanent project artifacts; require retained evidence to be reproducible and linked from the owning task's `## Results`.
- Keep the task model unchanged: no new task type, status, frontmatter, or registry. `attachments/` is the only non-task workspace directly under a task; directories beneath it group files and never represent tasks.
- Promote shared, pipeline-critical, or promised deliverables into project-conventional paths during Integrate, before integration review. Mature & Consolidate must retain, relocate, or drop the attachments that remain task-local without breaking their links.
- Let the live and standalone dashboards browse the workspace, render Markdown sidecars safely, and open or download other files across worktrees and custom/rootless task roots without turning artifacts into task-tree, DAG, or Kanban nodes.
- Verify instruction behavior with a realistic harness exercise and dashboard behavior with focused and full task-tree tests.

### Generated artifacts

Canonical role specs are outside the intended scope, so no generated role outputs should change. If implementation expands into `agents/*`, follow the generated-artifact protocol in the repo-root contributor guide: regenerate `skills/using-superra/references/direct-mode-implementer.md`, `skills/using-superra/references/direct-mode-reviewer.md`, `.codex/agents/superra_implementer.toml`, and `.codex/agents/superra_reviewer.toml` with `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project`; never hand-edit them.

## Planner Guidance

The repository already carries figures in task-local `attachments/`, moves the whole task directory, rewrites links in every Markdown file under a moved task, and runs Markdown integrity checks on sidecars. The missing capability is the lifecycle contract plus dashboard discovery, safe delivery, hot reload, and export.

Use `attachments/` rather than adding sibling `scripts/`, `notes/`, or `artifacts/` conventions. Prefer a flat workspace; allow subdirectories only for a coherent generated bundle. Do not require a manifest file: the owning `## Results` is the concise provenance and entry-point record.

The existing [HTML Dashboard](../dashboard/task.md) concern covers dashboard behavior but not the cross-workflow storage and promotion contract, so this work is a sibling durable concern under Task Tree Skill. The contract lands first; the backend data path and user interface then follow in dependency order.

## Critical Files

- [using-superra/SKILL.md](../../../skills/using-superra/SKILL.md) — universal task interface loaded by main agents, implementers, reviewers, and direct mode
- [task-file-contract.md](../../../skills/task-tree/references/task-file-contract.md) — current task anatomy, results lifecycle, and figure-attachment contract
- [mature-consolidate.md](../../../skills/superintegrate/references/mature-consolidate.md) — durable-home and directory-fold decisions for retained evidence
- [plan_dashboard.py](../../../skills/task-tree/scripts/plan_dashboard.py) — task discovery, routes, watchers, search/export state, and standalone rendering
- [dashboard.js](../../../skills/task-tree/scripts/templates/dashboard.js) — active-task navigation and client-side Markdown rendering

## Results
