---
title: "Task Tree Skill"
status: approved
depends_on: []
---

## Objective

Add a `task-tree` skill to superRA that replaces flat PLAN.md/RESULTS.md task tracking with a filesystem-based hierarchy where each task is a self-contained `task.md` with planner-owned `## Objective` and implementer-owned `## Results` (recursive at every level), and a generated HTML dashboard provides human-friendly visualization.

**Methodology:** Build as a standalone skill (`skills/task-tree/`) with Python CLI scripts for task CRUD, frontier computation, migration, and dashboard generation. Defer workflow integration to a follow-up PR.

**Conventions:**
- Scripts follow existing `skills/*/scripts/` patterns: stdlib-only Python, argparse CLI, `from __future__ import annotations`, type-annotated functions
- Task file body sections: `## Objective` (planner-owned), `## Results` (implementer-owned), `## Decisions`, `## Review Notes`
- Everything is a task — leaf tasks are directories without subdirectories
- Dependencies are sibling-only; parent status rolls up from children automatically
- Hook does validation/status propagation only; dashboard renders on demand (`superra dashboard`) or via explicit export (`superra dashboard export`)
- Dashboard: live SSE server (FastAPI + htmx + markdown-it + KaTeX); Google Fonts CDN for typography; vendored render libraries for offline export

**Output (see `skills/task-tree/references/internals.md §Script Inventory` for the full table):**
- `skills/task-tree/SKILL.md` — skill definition + routing docs
- `skills/task-tree/scripts/` — 19 production scripts (4 data-layer modules + 15 entry scripts, including the hook and wrapper resolver) + 7 test modules
- Key entry scripts: `cli.py` (command router), `task_read.py`, `task_create.py`, `task_update.py`, `task_query.py`, `task_check.py`, `task_hook.py`, `plan_dashboard.py`, `plan_migrate.py`, `dashboard_artifact_workflow.py`

**Pipeline:** `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts`

## Results

### Key Findings
- 19 production scripts (4 data-layer modules + 15 entry scripts) + 7 test modules; 689 tests passing
- Eliminated task/step distinction: everything is a task, leaf = no subdirectories
- Structured ownership: `## Objective` (planner) / `## Results` (implementer, recursive)
- Hook does validation/status propagation only — no auto-rebuild; dashboard renders on demand (live SSE server) or via explicit `superra dashboard export`
- Dashboard: live SSE server (FastAPI/htmx/markdown-it/KaTeX), multi-worktree support, vendored offline export; Source Serif 4 + IBM Plex Mono typography
- `superRA/` task files are now the primary researcher-facing results record: implementers write substantive task `## Results`, reviewers verify result substance, orchestrators selectively summarize approved child results into parent `## Results`, and the old separate `RESULTS.md` / `final-form.md` maturation path has been removed ([planning-redesign/planmd-sweep/task.md](planning-redesign/planmd-sweep/task.md)).
- **Top-level tasks are unprivileged** (formerly `top-level-task-shape`): a `superRA/task.md` umbrella is optional, added only when a shared `## Objective` / `### Context` genuinely spans every top-level task (`task-file-contract.md` §Tree Shape); a top-level task carries no scope requirement, same as any nested task. "Root-level task" was reworded to "top-level task" throughout skills/agents/docs, and the `task_check.py` placement smells that encoded the old privilege (single-child-root wrapper, root-leaf-beside-branch) were dropped along with the now-empty `check_placement` function and `placement` check category (the dep-rewire hook under [restructuring-tooling](restructuring-tooling/task.md) is unaffected). Full suite: 689 passed; `task check` clean.

## Revision Notes

- 2026-07-01 — Researcher-approved consolidation (Mature & Consolidate): collapse this subtree to the second level. Keep this `task.md` plus exactly one `task.md` per current second-level child; delete all deeper task directories, their attachments, and the resolved `comments.yaml` sidecars. Each surviving file's `## Results` distils to a short matured narrative of what shipped. Surviving files must be self-contained: name shipped artifacts as plain inline-code repo paths only — no markdown links to files outside `superRA/`, and no links to deleted descendants. Normalize frontmatter to `title`/`status`/`depends_on`.
