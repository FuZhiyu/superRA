#!/usr/bin/env python3
"""PreToolUse gate: keep a session's mutations inside the checkout it was pointed at.

A session whose cwd sits in one checkout can reach a *different* checkout by
absolute path: write `## Results` into a task it was never dispatched to, and
commit that checkout's in-flight diff. This gate denies the two mutations that
carry the damage:

- an `Edit`/`Write`/`apply_patch` on a `task.md` under a task root that belongs
  to neither the session's repository nor its cwd;
- a `Bash` command that retargets git at such a directory (`git -C <dir>`,
  `cd <dir> && git commit ...`) with a history-writing verb.

Worktrees of the session's own repository are not foreign — superRA dispatches
implementers into sibling worktrees, and every worktree of one repository shares
a single git common dir, which is the membership test used here.

Fails open on every uncertainty (git unavailable, unreadable payload,
unresolvable path): a gate must never wedge a session.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path


# `cd`/`pushd` at the start of the command or of any shell segment, and the
# explicit `git -C <dir>` retarget. Both are how a command reaches a directory
# other than the session cwd.
_CD_RE = re.compile(
    r"""(?:\A|[;&|]|\bdo\b|\bthen\b)\s*(?:cd|pushd)\s+(?P<path>"[^"]+"|'[^']+'|[^\s;&|()]+)"""
)
_GIT_C_RE = re.compile(
    r"""\bgit\s+(?:-\S+\s+|--\S+=\S+\s+)*-C\s+(?P<path>"[^"]+"|'[^']+'|[^\s;&|()]+)"""
)
_GIT_WRITE_RE = re.compile(
    r"\bgit\s+(?:-\S+\s+|--\S+=\S+\s+|-C\s+\S+\s+)*"
    r"(?:commit|add|rm|mv|merge|rebase|cherry-pick|revert|reset|restore|checkout|"
    r"switch|stash|push|apply|am|clean|tag|branch|worktree|update-ref|notes)\b"
)


def _empty() -> None:
    print("{}")


def _deny(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            },
            separators=(",", ":"),
        )
    )


def _task_md_reason(path: Path, cwd: Path) -> str:
    return (
        f"Refusing to write {path}: that task tree belongs to a different checkout "
        f"than this session's ({cwd}). A session that resolves another checkout's "
        "task tree writes results into a task it was never dispatched to. Work the "
        "task tree under this session's own cwd, or start a session in that "
        "checkout if it is the one you mean to change."
    )


def _git_reason(target: Path, cwd: Path) -> str:
    return (
        f"Refusing to run a git history-writing command in {target}: it is a "
        f"different checkout than this session's ({cwd}), so its working tree may "
        "carry another agent's in-flight diff. Run git where this session is "
        "pointed, or start a session in that checkout."
    )


def _scripts_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "skills" / "task-tree" / "scripts"


def _ensure_scripts_on_path() -> None:
    scripts = str(_scripts_dir())
    if scripts not in sys.path:
        sys.path.insert(0, scripts)


def _resolve(raw: str, cwd: Path) -> Path:
    path = Path(raw.strip().strip("'\""))
    return path if path.is_absolute() else cwd / path


def _is_task_md(path: Path) -> bool:
    if path.name != "task.md":
        return False
    return any(
        part == "superRA" or part == ".plan" or part.startswith(".plan.")
        for part in path.parts
    )


def _nearest_existing_dir(path: Path) -> Path | None:
    """The closest existing directory at or above *path* — a new task.md has none."""
    current = path if path.is_dir() else path.parent
    for candidate in [current, *current.parents]:
        if candidate.is_dir():
            return candidate
    return None


def _git_common_dir(directory: Path) -> Path | None:
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


def _same_dir(left: Path | None, right: Path | None) -> bool:
    """Directory identity, tolerant of case-insensitive and symlinked paths."""
    if left is None or right is None:
        return False
    try:
        return os.path.samefile(left, right)
    except OSError:
        return left == right


def _within(path: Path, root: Path) -> bool:
    """Is *path* at or under *root*? Walks with samefile so /tmp vs /private/tmp,
    case-insensitive volumes, and symlinked checkouts all compare correctly."""
    try:
        current = path.absolute()
    except OSError:
        return False
    for candidate in [current, *current.parents]:
        if _same_dir(candidate, root):
            return True
    return False


def _is_foreign(path: Path, cwd: Path) -> bool:
    """True when *path* belongs to neither the session's cwd nor its repository."""
    if _within(path, cwd):
        return False
    anchor = _nearest_existing_dir(path)
    if anchor is None:
        return False
    session_repo = _git_common_dir(cwd)
    if session_repo is None:
        # A session with no repository of its own owns only its cwd, and every
        # worktree pattern this gate must not break requires git.
        return True
    return not _same_dir(_git_common_dir(anchor), session_repo)


def _git_toplevel(directory: Path) -> Path | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(directory),
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    raw = result.stdout.strip()
    if result.returncode != 0 or not raw:
        return None
    try:
        return Path(raw).resolve()
    except OSError:
        return None


def _holds_task_root(directory: Path) -> bool:
    """Does *directory*, or the checkout it sits in, carry a task tree?"""
    candidates = [directory]
    toplevel = _git_toplevel(directory)
    if toplevel is not None:
        candidates.append(toplevel)
    return any(
        (candidate / dirname).is_dir()
        for candidate in candidates
        for dirname in ("superRA", ".plan")
    )


def _edit_write_reason(tool_input: dict, cwd: Path) -> str | None:
    raw = tool_input.get("file_path", "")
    if not isinstance(raw, str) or not raw:
        return None
    path = _resolve(raw, cwd)
    if _is_task_md(path) and _is_foreign(path, cwd):
        return _task_md_reason(path, cwd)
    return None


def _apply_patch_reason(command: str, cwd: Path) -> str | None:
    try:
        _ensure_scripts_on_path()
        from _apply_patch import patch_paths
    except Exception:
        return None
    for raw in patch_paths(command):
        path = _resolve(raw, cwd)
        if _is_task_md(path) and _is_foreign(path, cwd):
            return _task_md_reason(path, cwd)
    return None


def _bash_reason(command: str, cwd: Path) -> str | None:
    if "git" not in command or not _GIT_WRITE_RE.search(command):
        return None
    for match in list(_CD_RE.finditer(command)) + list(_GIT_C_RE.finditer(command)):
        target = _resolve(match.group("path"), cwd)
        if not target.is_dir():
            continue
        # Scoped to superRA checkouts: an ordinary cross-repo git command is the
        # researcher's business, a commit into another task-tree checkout is the
        # escape this gate exists for.
        if _is_foreign(target, cwd) and _holds_task_root(target):
            return _git_reason(target, cwd)
    return None


def deny_reason(tool_name: str, tool_input: dict, cwd: Path) -> str | None:
    """The reason this tool call escapes *cwd*'s checkout, or None to allow.

    The live Agent-SDK trace harness registers this as an in-process PreToolUse
    hook so a traced session is confined by the same rule as a plugin session.
    """
    if not isinstance(tool_input, dict):
        return None
    if tool_name in ("Edit", "Write"):
        return _edit_write_reason(tool_input, cwd)
    command = tool_input.get("command", "")
    if not isinstance(command, str) or not command:
        return None
    if tool_name == "apply_patch":
        return _apply_patch_reason(command, cwd)
    if tool_name == "Bash":
        return _bash_reason(command, cwd)
    return None


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        _empty()
        return
    tool_input = data.get("tool_input", {}) or {}
    # The project dir the session was started in, which a `cd` earlier in the
    # session cannot move; the payload cwd is the fallback for harnesses that do
    # not set it.
    try:
        cwd = Path(
            os.environ.get("CLAUDE_PROJECT_DIR", "")
            or data.get("cwd", "")
            or os.getcwd()
        )
    except (TypeError, ValueError):
        _empty()
        return

    reason = deny_reason(data.get("tool_name", "") or data.get("tool", ""), tool_input, cwd)
    if reason is None:
        _empty()
        return
    _deny(reason)


if __name__ == "__main__":
    main()
