---
title: "Worktree Discovery Module"
status: approved
depends_on: []
tags: []
created: 2026-05-26
---

## Objective

Create `skills/task-tree/scripts/_worktree_discovery.py` — a module that discovers all worktrees of the current git repo and identifies which ones have valid `.plan/` directories.

**Core function:** `discover_worktrees(plan_dirname: str = ".plan") -> list[WorktreeInfo]`

`WorktreeInfo` dataclass fields:
- `path: str` — absolute path to the worktree root
- `branch: str | None` — branch name (None for detached HEAD)
- `head: str` — HEAD commit SHA (abbreviated)
- `plan_root: str | None` — absolute path to `.plan/` if it exists and contains a valid `task.md`, else None
- `plan_title: str | None` — root task title from `.plan/task.md` frontmatter, if parseable
- `is_current: bool` — whether this worktree is the one the server was launched from
- `is_locked: bool` — whether `git worktree list --porcelain` reports `locked`
- `is_prunable: bool` — whether the worktree is marked prunable
- `is_agent: bool` — heuristic: branch name matches `worktree-agent-*` or path contains `.claude/worktrees/agent-`

**Parsing:** Run `git worktree list --porcelain` via `subprocess.run` and parse the output. Each worktree block starts with `worktree <path>` and includes `HEAD`, `branch`, optional `locked`/`prunable` lines. For each non-prunable worktree with a reachable path, check for `<path>/<plan_dirname>/task.md` and parse the YAML frontmatter `title:` field.

**Ordering:** Add a `last_activity: float | None` field to `WorktreeInfo` — the Unix timestamp of the last commit on the worktree's branch, obtained via `git log -1 --format=%ct <branch>`. For detached HEAD, use `git log -1 --format=%ct <HEAD>`. None if the command fails.

**Sorting function:** `sort_worktrees(worktrees: list[WorktreeInfo]) -> list[WorktreeInfo]` — sort by `last_activity` descending (most recent first). Worktrees with `last_activity = None` sort last.

**Filtering function:** `filter_worktrees(worktrees: list[WorktreeInfo], include_prunable: bool = False, require_plan: bool = True) -> list[WorktreeInfo]`
Default: exclude prunable, require `.plan/` with valid `task.md`. Agent worktrees are included (the `is_agent` flag is available for UI labeling but does not filter by default).

**Repo-root helper:** `get_git_common_dir() -> str | None` — runs `git rev-parse --git-common-dir` and returns the resolved absolute path, or None if not in a git repo.

**Error handling:**
- Not in a git repo → return empty list (dashboard falls back to single-plan mode)
- `git` not on PATH → return empty list
- Worktree path doesn't exist on disk (prunable) → mark `is_prunable`, skip `.plan/` check
- `.plan/task.md` exists but is unparseable → set `plan_root` but `plan_title = None`

**Constraints:** stdlib-only (subprocess for git). Follow existing `_task_io.py` patterns: `from __future__ import annotations`, type-annotated, dataclasses. Importable from `plan_dashboard.py`.

## Results

Implemented [`_worktree_discovery.py`](../../../../../skills/task-tree/scripts/_worktree_discovery.py) with all specified components:

- `WorktreeInfo` dataclass with all 10 fields (`path`, `branch`, `head`, `plan_root`, `plan_title`, `is_current`, `is_locked`, `is_prunable`, `is_agent`, `last_activity`).
- `discover_worktrees(plan_dirname=".plan")` — parses `git worktree list --porcelain`, resolves paths, detects plan roots and titles, computes `is_agent` heuristic, fetches `last_activity` timestamps. Returns empty list when not in a git repo or git is unavailable.
- `sort_worktrees()` — descending by `last_activity`, None sorts last.
- `filter_worktrees()` — keyword-only `include_prunable` and `require_plan` parameters.
- `get_git_common_dir()` — resolves to absolute path, returns None outside git.
- Minimal frontmatter title parser (regex-based, avoids `_task_io` import to stay decoupled).

Verified against the live repo with 15 worktrees: correctly identifies 1 current, 6 agent, 4 prunable, 8 with valid `.plan/`. Sort and filter edge cases (None activity, empty lists) confirmed.
