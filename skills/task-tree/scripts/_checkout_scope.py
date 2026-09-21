"""Which checkout a path belongs to: the session's own, or a foreign one.

One membership rule, shared by the `guard-foreign-checkout` PreToolUse gate
(`hooks/checkout_isolation_gate.py`) and the PostToolUse edit detector
(`_edit_detect.py`), so a path the gate would prompt about is also a path the
hook declines to touch.

A path is the session's own when it sits under the session cwd, or in a checkout
sharing the cwd's git common dir — every worktree of one repository shares that
dir, and superRA dispatches implementers into sibling worktrees. Everything else
is foreign.

Stdlib only.
"""

from __future__ import annotations

import os
import subprocess
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=64)
def git_common_dir(directory: Path) -> Path | None:
    """Resolved git common dir for *directory*, shared by every worktree of a repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            cwd=str(directory),
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    raw = result.stdout.strip()
    if not raw:
        return None
    # git prints a path relative to the invocation dir when inside a worktree.
    common = Path(raw)
    if not common.is_absolute():
        common = directory / common
    try:
        return common.resolve()
    except OSError:
        return None


def same_dir(left: Path | None, right: Path | None) -> bool:
    """Directory identity, tolerant of case-insensitive and symlinked paths."""
    if left is None or right is None:
        return False
    try:
        return os.path.samefile(left, right)
    except OSError:
        return left == right


def within(path: Path, root: Path) -> bool:
    """Is *path* at or under *root*? Walks with samefile so /tmp vs /private/tmp,
    case-insensitive volumes, and symlinked checkouts all compare correctly."""
    try:
        current = path.absolute()
    except OSError:
        return False
    for candidate in [current, *current.parents]:
        if same_dir(candidate, root):
            return True
    return False


def nearest_existing_dir(path: Path) -> Path | None:
    """The closest existing directory at or above *path* — a new task.md has none."""
    current = path if path.is_dir() else path.parent
    for candidate in [current, *current.parents]:
        if candidate.is_dir():
            return candidate
    return None


def is_foreign(path: Path, cwd: Path) -> bool:
    """True when *path* belongs to neither the session's cwd nor its repository."""
    if within(path, cwd):
        return False
    anchor = nearest_existing_dir(path)
    if anchor is None:
        return False
    session_repo = git_common_dir(cwd)
    if session_repo is None:
        # A session with no repository of its own owns only its cwd, and every
        # worktree pattern this rule must not break requires git.
        return True
    return not same_dir(git_common_dir(anchor), session_repo)
