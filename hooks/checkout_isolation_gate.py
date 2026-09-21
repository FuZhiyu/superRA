#!/usr/bin/env python3
"""PreToolUse gate: keep a session's mutations inside the checkout it was pointed at.

A session whose cwd sits in one checkout can reach a *different* checkout by
absolute path: write `## Results` into a task it was never dispatched to, and
commit that checkout's in-flight diff. This gate stops the two mutations that
carry the damage:

- an `Edit`/`Write`/`apply_patch` on a `task.md` under a task root that belongs
  to neither the session's repository nor its cwd;
- a `Bash` command that retargets git at such a directory (`git -C <dir>`,
  `cd <dir> && git commit ...`, `git --work-tree=<dir> commit`) with a
  history-writing verb.

Worktrees of the session's own repository are not foreign — superRA dispatches
implementers into sibling worktrees, and every worktree of one repository shares
a single git common dir, which is the membership test used here. The rule itself
lives in `skills/task-tree/scripts/_checkout_scope.py`, shared with the
PostToolUse edit detector so the hook writes nowhere this gate would prompt about.

The decision is `ask`, not `deny`: cross-checkout work the researcher deliberately
set up is legitimate, so an interactive session can approve while an unattended one
still cannot proceed. The live Agent-SDK trace harness imports :func:`deny_reason`
and hard-denies instead, because a traced session has no approver.

Fails open on every uncertainty (git unavailable, unreadable payload,
unresolvable path): a gate must never wedge a session.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


# The three ways a command reaches a directory other than the session cwd: a
# `cd`/`pushd`, and git's own `-C` / `--git-dir` / `--work-tree` retargets. The
# `cd` boundary admits every shell opener a segment can start with — command
# start, separators, subshell and group parens, `do`/`then`, and the quote that
# opens a `bash -c "..."` payload.
_PATH = r"""(?P<path>"[^"]+"|'[^']+'|[^\s;&|(){}"']+)"""
_CD_RE = re.compile(
    r"""(?:\A|[;&|(){}"']|\bdo\b|\bthen\b)\s*(?:cd|pushd)\s+""" + _PATH
)
_GIT_C_RE = re.compile(r"""\bgit\s+(?:-\S+\s+|--\S+=\S+\s+)*-C\s+""" + _PATH)
_GIT_DIR_RE = re.compile(r"""--(?:git-dir|work-tree)[=\s]\s*""" + _PATH)
_GIT_WRITE_RE = re.compile(
    r"\bgit\s+(?:-\S+\s+|--\S+=\S+\s+|-C\s+\S+\s+)*"
    r"(?:commit|add|rm|mv|merge|rebase|cherry-pick|revert|reset|restore|checkout|"
    r"switch|stash|push|apply|am|clean|tag|branch|worktree|update-ref|notes)\b"
)


def _empty() -> None:
    print("{}")


def _ask(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "ask",
                    "permissionDecisionReason": reason,
                }
            },
            separators=(",", ":"),
        )
    )


def _task_md_reason(path: Path, cwd: Path) -> str:
    return (
        f"{path} is a task tree in a different checkout than this session's ({cwd}). "
        "Approve if you pointed this session at that checkout on purpose. Reject if "
        "you did not: a session that resolves a checkout it was not given writes "
        "results into a task nobody dispatched it to, and those results read as "
        "genuine afterwards."
    )


def _git_reason(target: Path, cwd: Path) -> str:
    return (
        f"This command writes git history in {target}, a different checkout than "
        f"this session's ({cwd}). Approve if you meant this session to commit there. "
        "Reject if you did not: that checkout's working tree may hold another "
        "agent's in-flight diff, which this command would commit under this "
        "session's message."
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


def _scope():
    """The shared checkout-scope module, or None when it cannot be imported —
    an uncertainty like any other, so every caller fails open on None."""
    try:
        _ensure_scripts_on_path()
        import _checkout_scope
    except Exception:
        return None
    return _checkout_scope


def _is_foreign(path: Path, cwd: Path) -> bool:
    """True when *path* belongs to neither the session's cwd nor its repository."""
    scope = _scope()
    return scope.is_foreign(path, cwd) if scope is not None else False


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


def _retargeted_dirs(command: str, cwd: Path):
    """Every directory *command* points a shell or git at, outside the session cwd."""
    for pattern in (_CD_RE, _GIT_C_RE, _GIT_DIR_RE):
        for match in pattern.finditer(command):
            target = _resolve(match.group("path"), cwd)
            # `--git-dir` names the repository dir; the checkout is its parent.
            if target.name == ".git":
                target = target.parent
            if target.is_dir():
                yield target


def _bash_reason(command: str, cwd: Path) -> str | None:
    if "git" not in command or not _GIT_WRITE_RE.search(command):
        return None
    for target in _retargeted_dirs(command, cwd):
        # Scoped to superRA checkouts: an ordinary cross-repo git command is the
        # researcher's business, a commit into another task-tree checkout is the
        # escape this gate exists for.
        if _is_foreign(target, cwd) and _holds_task_root(target):
            return _git_reason(target, cwd)
    return None


def deny_reason(tool_name: str, tool_input: dict, cwd: Path) -> str | None:
    """The reason this tool call escapes *cwd*'s checkout, or None to allow.

    The live Agent-SDK trace harness registers this as an in-process PreToolUse
    hook and hard-denies on it: a traced session has no approver, so the plugin
    gate's `ask` would fail open there.
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
    scope = _scope()
    cwd = scope.session_anchor(data) if scope is not None else None
    if cwd is None:
        _empty()
        return

    reason = deny_reason(data.get("tool_name", "") or data.get("tool", ""), tool_input, cwd)
    if reason is None:
        _empty()
        return
    _ask(reason)


if __name__ == "__main__":
    main()
