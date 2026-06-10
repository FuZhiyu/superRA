---
title: "Rename Legacy Task-System Surface to Task Tree"
status: approved
depends_on:  []
tags: []
created: 2026-06-10
---

## Objective

Rename the superRA tree-tooling surface from `task-system` to `task-tree` across source, docs, hooks, wrappers, tests, and the task-tree record. Preserve existing task-tree history and compatibility for installed or generated wrappers that may still resolve `skills/task-system` during transition. Update the owning skill metadata, inventory/category surfaces, contributor docs, generated hook/wrapper artifacts, and tests so the new canonical name is `task-tree`. Generated artifacts touched by this task: `superRA/superra` and `hooks/task-hook`, regenerated from `skills/task-tree/scripts/wrapper_resolver.py` after the skill directory rename.

## Planner Guidance

Prefer a compatibility resolver that probes `skills/task-tree` first and falls back to `skills/task-system` where needed. Keep implementation as a focused rename; do not redesign task semantics.

## Results

### Key Findings
- Renamed the canonical tree-tooling skill from `skills/task-system` to `skills/task-tree`, including the skill frontmatter name (`task-tree`), inventories, contributor docs, workflow references, hook docs, and generated project Codex agent output.
- Renamed the repository task-tree workstream from `superRA/task-system` to `superRA/task-tree`, preserving the existing history subtree and updating active task references.
- Updated `skills/task-tree/scripts/wrapper_resolver.py` and regenerated `superRA/superra` plus `hooks/task-hook`. The generated resolver now prefers `skills/task-tree` and keeps `skills/task-system` as a legacy fallback for installed or already-generated wrappers.
- Renamed the main script test module to `skills/task-tree/scripts/test_task_tree.py` and updated command examples to use the new path.

### Verification
- `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts -q` -> 610 passed, 2 skipped, 3 warnings.
- `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts/test_cli.py -q` -> 35 passed.
- `superRA/superra task check` -> all checks passed.
- `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check` -> generated agent files and direct-mode references are up to date.
- `python3 skills/task-tree/scripts/wrapper_resolver.py render-hook | diff -u - hooks/task-hook` -> no diff.
- `superRA/superra` matches `wrapper_resolver.render_wrapper()`.
- Integration rerun after no-op sync: `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts -q` -> 610 passed, 2 skipped, 3 warnings.
- Integration rerun after no-op sync: `uv run --with pytest --with pyyaml python -m pytest skills/codex-superra-setup/scripts/test_sync_codex_agents.py -q` -> 7 passed.
- Integration checks: `superRA/superra task check`, `superRA/superra task check --category placement`, generated-agent check, generated wrapper/hook identity checks, and `git diff --check` all passed.

**Final diff self-check:** `git diff 6e88cd51771acf4e34da475bf396eabab6e5ded0..HEAD`; surviving-change classes are the approved rename surface (`skills/task-tree`, `superRA/task-tree`, inventories/docs), generated wrapper/hook/agent refreshes, and task-tree integration records. Suspicious instruction hunks are scoped to replacing the canonical utility skill name/path from `task-system` to `task-tree`; legacy `skills/task-system` strings survive only in resolver fallback code and this task's rename record.
