---
title: "Worktree Selector Tests"
status: approved
depends_on:
  - discovery
  - server-routes
tags: []
created: 2026-05-26
updated: 2026-05-26
---

## Objective

Test suite for the worktree discovery and server switching features. Create `skills/task-system/scripts/test_worktree_selector.py`. Use pytest, consistent with the existing `test_task_system.py` patterns.

**Discovery module tests:**
- Parse a realistic `git worktree list --porcelain` output (multi-worktree with mixed states: normal, locked, prunable, detached HEAD, agent worktrees). Verify all `WorktreeInfo` fields are populated correctly.
- Filter function: verify default filter excludes prunable and no-plan worktrees but keeps agent worktrees. Verify `include_prunable=True` override.
- Sort function: verify worktrees are ordered by `last_activity` descending, with None values last.
- Edge cases: empty output (not a git repo), single worktree, worktree with `.plan/` but broken `task.md` (plan_root set, plan_title None), worktree with `last_activity = None`.
- `get_git_common_dir()` returns None when not in a git repo.

**Server route tests (using FastAPI TestClient):**
- `GET /api/worktrees` returns valid JSON with expected fields
- `POST /api/worktree/switch` with a valid plan root returns success and tree is rebuilt
- `POST /api/worktree/switch` with an invalid path returns 400
- `POST /api/worktree/switch` with a path that has no `.plan/` returns 404
- After a successful switch, SSE clients receive a `full-reload` event

**Port derivation tests:**
- `_default_port` with a git common dir produces a consistent port across different plan roots in the same repo
- `_default_port` without a git common dir falls back to plan-root hashing (backward compatible)

**Test infrastructure:** Mock `subprocess.run` for git commands (no actual git repo required). Create temporary directories with `.plan/task.md` fixtures for filesystem checks. Use `fastapi.testclient.TestClient` for route tests.

## Results

Test file created at [`skills/task-system/scripts/test_worktree_selector.py`](skills/task-system/scripts/test_worktree_selector.py). 53 tests, all passing (`uv run pytest skills/task-system/scripts/test_worktree_selector.py -v`).

**Coverage by test class:**

| Class | Tests | Covers |
|---|---|---|
| `TestParsePorcelain` | 9 | Multi-worktree parsing, paths, HEAD, branches, detached, locked, prunable with reason, empty output, single worktree |
| `TestParsePlanTitle` | 6 | Normal/quoted titles, no frontmatter, no title field, nonexistent file, broken file |
| `TestGetGitCommonDir` | 5 | Resolved path return, failure/empty/missing-git/timeout all return None |
| `TestDiscoverWorktrees` | 9 | Full discovery with plans, non-git/missing-git, prunable skip, no-plan, broken task.md, agent detection (branch + path), detached HEAD |
| `TestFilterWorktrees` | 6 | Default excludes prunable/no-plan, keeps agents, `include_prunable` override, `require_plan=False`, empty |
| `TestSortWorktrees` | 5 | Descending by activity, None sorts last, all-None, single, empty |
| `TestDefaultPort` | 4 | Consistent port from git common dir across plan roots, fallback to plan-root hashing, valid range, different repos different ports |
| `TestWorktreeRoutes` | 8 | GET /api/worktrees JSON + fields + fallback, POST switch: missing field 400, no-git 404, nonexistent worktree 404, valid switch 200, missing task.md 400 |
| `TestSSEBroadcastOnSwitch` | 1 | Verifies full-reload SSE event after successful switch |
