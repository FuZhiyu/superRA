#!/usr/bin/env python3
"""Worktree discovery for the task-system dashboard.

Discovers all git worktrees of the current repo, identifies which ones
have valid task-tree directories, and provides sorting/filtering helpers.
"""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from _task_io import LEGACY_TASK_ROOT_DIRNAME, TASK_ROOT_DIRNAME

# Minimal frontmatter title extraction keeps discovery independent of full task
# parsing.
_FRONTMATTER_RE = re.compile(r"\A---\n(.*?\n)---\n", re.DOTALL)
_TITLE_RE = re.compile(r'^title:\s*"?([^"\n]+)"?\s*$', re.MULTILINE)


@dataclass
class WorktreeInfo:
    """Metadata for a single git worktree."""

    path: str
    branch: str | None
    head: str
    plan_root: str | None
    plan_title: str | None
    is_current: bool
    is_locked: bool
    is_prunable: bool
    is_agent: bool
    last_activity: float | None


def get_git_common_dir() -> str | None:
    """Return the resolved absolute path to the git common dir, or None."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    raw = result.stdout.strip()
    if not raw:
        return None
    return str(Path(raw).resolve())


def _get_current_worktree_path() -> str | None:
    """Return the resolved absolute path of the current worktree root."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    raw = result.stdout.strip()
    if not raw:
        return None
    return str(Path(raw).resolve())


def _parse_plan_title(task_md_path: Path) -> str | None:
    """Extract the title from a task.md's YAML frontmatter."""
    try:
        text = task_md_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    fm_match = _FRONTMATTER_RE.match(text)
    if not fm_match:
        return None
    title_match = _TITLE_RE.search(fm_match.group(1))
    if not title_match:
        return None
    return title_match.group(1).strip()


def _get_last_activity(ref: str) -> float | None:
    """Return the Unix timestamp of the last commit on *ref*, or None."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", ref],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        return float(result.stdout.strip())
    except ValueError:
        return None


def _is_agent_worktree(path: str, branch: str | None) -> bool:
    """Heuristic: branch matches worktree-agent-* or path contains .claude/worktrees/agent-."""
    if branch is not None and branch.startswith("worktree-agent-"):
        return True
    if ".claude/worktrees/agent-" in path:
        return True
    return False


def _parse_porcelain(output: str) -> list[dict[str, str]]:
    """Parse ``git worktree list --porcelain`` into a list of attribute dicts.

    Each worktree block is separated by a blank line.  Within a block,
    lines are ``key value`` or bare ``key`` (for boolean flags like
    ``locked`` or ``prunable``).  The ``locked`` line may carry an
    optional reason after the keyword.
    """
    blocks: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in output.splitlines():
        if not line.strip():
            if current:
                blocks.append(current)
                current = {}
            continue
        if line.startswith("worktree "):
            current["worktree"] = line[len("worktree ") :]
        elif line.startswith("HEAD "):
            current["HEAD"] = line[len("HEAD ") :]
        elif line.startswith("branch "):
            current["branch"] = line[len("branch ") :]
        elif line == "detached":
            current["detached"] = ""
        elif line.startswith("locked"):
            current["locked"] = line[len("locked") :].strip()
        elif line.startswith("prunable"):
            current["prunable"] = line[len("prunable") :].strip()
    if current:
        blocks.append(current)
    return blocks


def _is_task_root(candidate: Path) -> bool:
    """True if *candidate* is a valid task root: it holds an umbrella ``task.md``
    (single tree) or at least one immediate child task dir (a rootless forest)."""
    if (candidate / "task.md").is_file():
        return True
    try:
        children = candidate.iterdir()
    except OSError:
        return False
    return any(d.is_dir() and (d / "task.md").is_file() for d in children)


def _find_plan_root(worktree_path: str, preferred_dirname: str) -> tuple[Path, str | None] | tuple[None, None]:
    dirnames = [preferred_dirname]
    for dirname in (TASK_ROOT_DIRNAME, LEGACY_TASK_ROOT_DIRNAME):
        if dirname not in dirnames:
            dirnames.append(dirname)
    for dirname in dirnames:
        candidate = Path(worktree_path) / dirname
        if _is_task_root(candidate):
            return candidate, dirname
    return None, None


def discover_worktrees(plan_dirname: str = TASK_ROOT_DIRNAME) -> list[WorktreeInfo]:
    """Discover all worktrees of the current git repo.

    Returns a list of ``WorktreeInfo`` for every worktree reported by
    ``git worktree list --porcelain``.  Returns an empty list when not
    inside a git repo or when git is not available.
    """
    try:
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []
    if result.returncode != 0:
        return []

    current_path = _get_current_worktree_path()
    blocks = _parse_porcelain(result.stdout)
    worktrees: list[WorktreeInfo] = []

    for block in blocks:
        wt_path = block.get("worktree", "")
        if not wt_path:
            continue

        resolved_path = str(Path(wt_path).resolve())
        head_sha = block.get("HEAD", "")[:12]
        is_prunable = "prunable" in block
        is_locked = "locked" in block

        # Branch: strip refs/heads/ prefix
        raw_branch = block.get("branch")
        branch: str | None = None
        if raw_branch is not None:
            branch = raw_branch.removeprefix("refs/heads/")

        # Task-root check — skip for paths that don't exist on disk
        plan_root: str | None = None
        plan_title: str | None = None
        if not is_prunable and os.path.isdir(wt_path):
            task_root, _ = _find_plan_root(wt_path, plan_dirname)
            if task_root is not None:
                plan_root = str(task_root.resolve())
                plan_title = _parse_plan_title(task_root / "task.md")

        # Activity timestamp
        ref = branch if branch is not None else head_sha
        last_activity = _get_last_activity(ref) if ref else None

        worktrees.append(
            WorktreeInfo(
                path=resolved_path,
                branch=branch,
                head=head_sha,
                plan_root=plan_root,
                plan_title=plan_title,
                is_current=(current_path is not None and resolved_path == current_path),
                is_locked=is_locked,
                is_prunable=is_prunable,
                is_agent=_is_agent_worktree(resolved_path, branch),
                last_activity=last_activity,
            )
        )

    return worktrees


def sort_worktrees(worktrees: list[WorktreeInfo]) -> list[WorktreeInfo]:
    """Sort worktrees by last_activity descending (most recent first).

    Worktrees with ``last_activity = None`` sort last.
    """
    return sorted(
        worktrees,
        key=lambda w: (w.last_activity is not None, w.last_activity or 0.0),
        reverse=True,
    )


def filter_worktrees(
    worktrees: list[WorktreeInfo],
    *,
    include_prunable: bool = False,
    require_plan: bool = True,
) -> list[WorktreeInfo]:
    """Filter worktrees by prunable status and plan availability.

    Default: exclude prunable, require a valid task root with ``task.md``.
    Agent worktrees are never filtered out — the ``is_agent`` flag is
    available for UI labeling.
    """
    out: list[WorktreeInfo] = []
    for w in worktrees:
        if not include_prunable and w.is_prunable:
            continue
        if require_plan and w.plan_root is None:
            continue
        out.append(w)
    return out
