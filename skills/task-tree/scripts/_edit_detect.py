"""Tool-agnostic edit detection for the PostToolUse hook.

A per-session rolling baseline of `(size, mtime_ns, sha256)` over the watched
files of one task tree. `detect()` returns the files whose content differs from
the baseline and refreshes it, so the hook's consumers fire for an edit made
through any tool — a Bash heredoc, `sed -i`, or a `git checkout` included —
without parsing the command.

Stdlib only. State lives beside the reminder markers in the project's
gitignored `.superra-repro/` directory.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import time
from pathlib import Path
from typing import Callable, Iterable

from _checkout_scope import is_foreign

TASK_ROOT_DIRNAME = "superRA"
STATE_DIRNAME = ".superra-repro"
BASELINE_SUBDIR = "hook-baseline"
BASELINE_VERSION = 1

# Script files watched under a task root: a retained task companion is code.
SCRIPT_SUFFIXES = frozenset({".jl", ".py", ".r", ".do", ".sh", ".ipynb", ".sql", ".m"})
_TREE_SUFFIXES = SCRIPT_SUFFIXES | {".md"}
_STRUCTURE_NAMES = frozenset({"task.md", "config.yaml"})
_SKIP_DIRS = frozenset({"__pycache__", "node_modules"})

# Above this size a file is compared by stat alone: a large data dep is not
# read on every seed.
HASH_MAX_BYTES = 4 << 20
# Bytes hashed in one call; past it, files are compared by stat alone, so a
# tree registering many mid-sized data deps does not stall a session's first call.
HASH_BUDGET_BYTES = 64 << 20
# A tree this large is not a task tree (a mis-resolved root); stay silent.
MAX_TREE_FILES = 5000
BASELINE_MAX_AGE_SECONDS = 7 * 86400

_ABS_PATH_RE = re.compile(r"(?<![\w.~$])(/[^\s'\"`;|&<>()$*?\\]+)")
_MAX_PATH_HINTS = 16


def is_script(path: Path) -> bool:
    return path.suffix.lower() in SCRIPT_SUFFIXES


# ---------------------------------------------------------------------------
# Locating the task trees a tool call may have touched
# ---------------------------------------------------------------------------

def _plan_root_above(start: Path) -> Path | None:
    """The `superRA/` beside or above `start`, never crossing a repository top."""
    home = Path.home()
    current = start
    while True:
        try:
            names = set(os.listdir(current))
        except OSError:
            names = set()
        if TASK_ROOT_DIRNAME in names and (current / TASK_ROOT_DIRNAME).is_dir():
            return current / TASK_ROOT_DIRNAME
        if ".git" in names or current == home or current.parent == current:
            return None
        current = current.parent


def plan_roots(cwd: Path, tool_paths: Iterable[Path], command: str) -> list[Path]:
    """Task roots to check: the session cwd's, the tool-supplied paths', and
    those of absolute paths the command names (an agent working in a sibling
    worktree addresses it by absolute path). The command is read only to learn
    where to look, never what changed.

    A root in a foreign checkout is dropped: detection leads to a reconcile, and
    a session must not rewrite task files in a checkout it was not pointed at.
    Membership is the `guard-foreign-checkout` gate's own test
    (`_checkout_scope.is_foreign`), so every worktree of the session's own
    repository stays in reach.
    """
    starts: list[Path] = [cwd]
    starts.extend(p.parent for p in tool_paths)
    for match in list(_ABS_PATH_RE.finditer(command))[:_MAX_PATH_HINTS]:
        hinted = Path(match.group(1))
        while not hinted.exists() and hinted.parent != hinted:
            hinted = hinted.parent
        starts.append(hinted if hinted.is_dir() else hinted.parent)

    roots: list[Path] = []
    seen: set[Path] = set()
    for start in starts:
        try:
            root = _plan_root_above(start.resolve())
        except OSError:
            continue
        if root is None or root in seen:
            continue
        seen.add(root)
        if not is_foreign(root, cwd):
            roots.append(root)
    return roots


# ---------------------------------------------------------------------------
# Baseline
# ---------------------------------------------------------------------------

def _tree_files(plan_root: Path) -> list[str] | None:
    """Markdown, scripts, and `config.yaml` under the task root; None when the
    directory is too large to be a task tree."""
    found: list[str] = []
    config = plan_root / "config.yaml"
    if config.is_file():
        found.append(str(config))
    for parent, dirnames, filenames in os.walk(plan_root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in _SKIP_DIRS]
        for name in filenames:
            if os.path.splitext(name)[1].lower() in _TREE_SUFFIXES:
                found.append(os.path.join(parent, name))
        if len(found) > MAX_TREE_FILES:
            return None
    return found


def _content_hash(path: str, size: int) -> str | None:
    if size > HASH_MAX_BYTES:
        return None
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _load(state_path: Path) -> dict | None:
    try:
        loaded = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if (
        not isinstance(loaded, dict)
        or loaded.get("version") != BASELINE_VERSION
        or not isinstance(loaded.get("files"), dict)
        or not isinstance(loaded.get("extra"), list)
    ):
        return None
    return loaded


def _save(state_path: Path, payload: dict) -> None:
    """Atomic replace: a concurrent hook reads the old or the new baseline whole."""
    state_dir = state_path.parent.parent
    state_path.parent.mkdir(parents=True, exist_ok=True)
    ignore = state_dir / ".gitignore"
    if not ignore.exists():
        ignore.write_text("*\n", encoding="utf-8")
    tmp = state_path.with_name(f"{state_path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    os.replace(tmp, state_path)


def _prune(baseline_dir: Path) -> None:
    cutoff = time.time() - BASELINE_MAX_AGE_SECONDS
    try:
        for entry in baseline_dir.iterdir():
            if entry.is_file() and entry.stat().st_mtime < cutoff:
                entry.unlink()
    except OSError:
        pass


def detect(
    plan_root: Path,
    session_key: str,
    extra_files: Callable[[], list[str]],
) -> list[Path]:
    """Files under watch whose content changed since this session's baseline.

    The first call of a session seeds the baseline and reports nothing.
    `extra_files` supplies the watched files outside the task root (reproduction
    deps); it is called only when no cached list exists or a `task.md` or
    `config.yaml` changed, since only those can alter the list. A file newly
    added to that list is seeded, not reported; a new file under the task root
    is reported.
    """
    plan_root = plan_root.resolve()
    tree = _tree_files(plan_root)
    if tree is None:
        return []
    baseline_dir = plan_root.parent / STATE_DIRNAME / BASELINE_SUBDIR
    state_path = baseline_dir / f"{session_key}.json"
    old = _load(state_path)
    seeding = old is None
    old_files: dict = {} if seeding else old["files"]

    files: dict[str, list] = {}
    changed: list[str] = []
    hashed_bytes = 0

    def visit(path: str, *, new_counts: bool) -> None:
        try:
            info = os.stat(path)
        except OSError:
            return
        if not stat.S_ISREG(info.st_mode):
            return
        previous = old_files.get(path)
        if previous and previous[0] == info.st_size and previous[1] == info.st_mtime_ns:
            files[path] = previous
            return
        nonlocal hashed_bytes
        try:
            if hashed_bytes + info.st_size > HASH_BUDGET_BYTES:
                digest = None
            else:
                digest = _content_hash(path, info.st_size)
                hashed_bytes += info.st_size
        except OSError:
            return
        files[path] = [info.st_size, info.st_mtime_ns, digest]
        if seeding or (previous is None and not new_counts):
            return
        if previous is None or digest is None or previous[2] != digest:
            changed.append(path)

    for path in tree:
        visit(path, new_counts=True)

    tree_set = set(tree)
    tree_prefix = str(plan_root) + os.sep
    removed = [p for p in old_files if p.startswith(tree_prefix) and p not in tree_set]
    structure_moved = seeding or any(
        os.path.basename(path) in _STRUCTURE_NAMES for path in changed + removed
    )
    extra = sorted(set(extra_files())) if structure_moved else list(old["extra"])
    for path in extra:
        if path not in files:
            visit(path, new_counts=False)

    if seeding:
        _prune(baseline_dir)
    if seeding or files != old_files or extra != old["extra"]:
        _save(state_path, {"version": BASELINE_VERSION, "files": files, "extra": extra})
    return [Path(path) for path in changed]
