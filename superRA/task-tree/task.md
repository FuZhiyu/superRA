---
title: "Task Tree Skill"
status: revise
depends_on: []
---

## Objective

Add a `task-tree` skill to superRA that replaces flat PLAN.md/RESULTS.md task tracking with a filesystem-based hierarchy where each task is a self-contained `task.md` with planner-owned `## Objective` and implementer-owned `## Results` (recursive at every level), and a generated HTML dashboard provides human-friendly visualization.

**Methodology:** Build as a standalone skill (`skills/task-tree/`) with Python CLI scripts for task CRUD, frontier computation, migration, and dashboard generation.

**Conventions:**
- Scripts follow existing `skills/*/scripts/` patterns: stdlib-only where feasible, argparse CLI, `from __future__ import annotations`, type-annotated functions.
- Task file body sections: `## Objective` (planner-owned), `## Results` (implementer-owned), `## Review Notes`.
- Everything is a task — leaf tasks are directories without subdirectories.
- Dependencies are sibling-only; parent status rolls up from children automatically.
- Hook does validation/status propagation only; the dashboard renders on demand (`superra dashboard`) or via explicit export (`superra dashboard export`).
- Dashboard: live SSE server (FastAPI + htmx + markdown-it + KaTeX); Google Fonts CDN for typography; vendored render libraries for offline export.

## Results

The `task-tree` skill ships as `skills/task-tree/` — a routing `SKILL.md` over the references (`commands.md`, `task-file-contract.md`, `internals.md`), a Python script package under `skills/task-tree/scripts/`, and a full test suite. The task tree is now the primary researcher-facing record and handoff mechanism, replacing the separate PLAN.md / RESULTS.md / final-form maturation path.

What the subtree delivered, one durable concern per surviving child:

- **Core mechanics** — the stdlib data layer (`_task_io.py`, `_task_validate.py`), the packaged `superra` CLI, the migration script (`plan_migrate.py`), the status model (single `status` field, sibling-only deps, automatic rollup), and the test suite.
- **Dashboard** — a FastAPI live SSE server with a master-detail workspace, DAG and kanban views, multi-worktree serving, and a self-contained static export.
- **Agent interface** — the task tree as the workflow handoff surface: the universal interface in `using-superra`, comment surfacing in `task read`, and the planning / integration workflow redesigns.
- **Later refinements** — Codex task-hook parity, frontmatter narrowed to `title`/`status`/`depends_on`, the consolidation + maturation stage redesign, task-edit discipline, and the dep-rewire restructuring hook.

**Top-level tasks are unprivileged.** A `superRA/task.md` umbrella is optional, added only when a shared `## Objective` / `### Context` genuinely spans every top-level task (`task-file-contract.md` §Tree Shape); a top-level task carries no scope requirement, the same as any nested task. "Root-level task" was reworded to "top-level task" throughout skills, agents, and docs, and the `task_check.py` placement smells that encoded the old privilege (single-child-root wrapper, root-leaf-beside-branch) were dropped along with the now-empty `check_placement` function and `placement` check category. The dep-rewire hook (see [restructuring-tooling](restructuring-tooling/task.md)) is unaffected.

The full test suite passes and `superra task check` is clean.
