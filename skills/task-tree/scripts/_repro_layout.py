#!/usr/bin/env python3
"""Where a project keeps its reproduction records and this machine's state.

Stdlib only, and light enough for the hooks to import.

- **In the task root** (default): `<task root>/.repro/` holds the committed
  lock and acceptance records, and `local/` inside it this machine's state.
- **At the project root** (where they sat before): `repro-lock.json`,
  `repro-acceptance/`, and `.superra-repro/`. A project whose records sit
  there keeps reading and writing them there until `superra repro migrate`.

The state follows the records: root-level records use the root-level state,
so an older superRA sharing the checkout reads the same run records and stamps.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

TASK_ROOT_DIRNAME = "superRA"
TASK_ROOT_DIRNAMES = (TASK_ROOT_DIRNAME, ".plan")
REPRO_DIRNAME = ".repro"
LOCAL_DIRNAME = "local"
TREE_LOCK_FILENAME = "lock.json"
TREE_ACCEPTANCE_DIRNAME = "acceptance"

ROOT_STATE_DIRNAME = ".superra-repro"
ROOT_LOCK_FILENAME = "repro-lock.json"
ROOT_ACCEPTANCE_DIRNAME = "repro-acceptance"
ROOT_LEGACY_FILENAMES = ("repro-acceptance.json", "pytask.lock", "repro-builds.json")
# Any of these at the project root keeps the committed records there.
ROOT_RECORDS = (ROOT_LOCK_FILENAME, ROOT_ACCEPTANCE_DIRNAME, *ROOT_LEGACY_FILENAMES)


def _holds_tasks(directory: Path) -> bool:
    """Whether a directory is a task root as `_task_io` finds one: an umbrella `task.md` or a child task."""
    try:
        if directory.is_symlink() or not directory.is_dir():
            return False
        task_md = directory / "task.md"
        if not task_md.is_symlink() and task_md.is_file():
            return True
        return any(child.name != "attachments" and not child.is_symlink() and child.is_dir()
                   and not (child / "task.md").is_symlink() and (child / "task.md").exists()
                   for child in directory.iterdir())
    except OSError:
        return False


def task_root(project_root) -> Path:
    """The project's task root when none is given: the `superRA/` or legacy `.plan/` that holds tasks.

    With neither holding tasks, the one that exists; `superRA/` first each time, as the runner prefers it.
    """
    candidates = [Path(project_root) / name for name in TASK_ROOT_DIRNAMES]
    return (next((d for d in candidates if _holds_tasks(d)), None)
            or next((d for d in candidates if d.is_dir()), candidates[0]))


def repro_home(project_root, plan_root=None) -> Path:
    """`<task root>/.repro`, spelled below *project_root* when the task root is its child."""
    root = Path(project_root)
    if plan_root is None:
        return task_root(root) / REPRO_DIRNAME
    plan = Path(plan_root)
    if plan.parent != root and os.path.realpath(plan.parent) == os.path.realpath(root):
        plan = root / plan.name
    return plan / REPRO_DIRNAME


def staging_dir(project_root, plan_root=None) -> Path:
    """`<task root>/.repro.migrating`: where `superra repro migrate` stages records, and its marker.

    It exists from a migration's first change to its last. A status computed
    meanwhile would mix two layouts, so readers refuse while it is there.
    """
    home = repro_home(project_root, plan_root)
    return home.with_name(home.name + ".migrating")


def records_dir(project_root, plan_root=None) -> Path | None:
    """`<task root>/.repro` when the committed records live in the task root; None while they sit at the project root."""
    home = repro_home(project_root, plan_root)
    if (home / TREE_LOCK_FILENAME).is_file() or (home / TREE_ACCEPTANCE_DIRNAME).is_dir():
        return home
    root = Path(project_root)
    return None if any(os.path.lexists(root / name) for name in ROOT_RECORDS) else home


def root_leftovers(project_root, plan_root=None) -> list[str]:
    """Root-level records a project whose records live in the task root still carries; they are never read."""
    if records_dir(project_root, plan_root) is None:
        return []
    return [name for name in ROOT_RECORDS if os.path.lexists(Path(project_root) / name)]


def state_dir(project_root, plan_root=None) -> Path:
    """This machine's state directory, which follows the records.

    Root-level records: the root-level directory, whatever else exists. Records
    in the task root: `local/` there, or a root-level directory the runner has
    yet to move in (`adopt_root_state`).
    """
    home = records_dir(project_root, plan_root)
    legacy = Path(project_root) / ROOT_STATE_DIRNAME
    if home is None:
        return legacy
    local = home / LOCAL_DIRNAME
    return local if local.is_dir() or not legacy.is_dir() else legacy


def dropbox_ignore(path) -> None:
    """Set Dropbox's ignore flag, so each machine keeps its own copy; inert outside Dropbox."""
    try:
        if hasattr(os, "setxattr"):  # Linux
            try:
                if os.getxattr(path, "user.com.dropbox.ignored") == b"1":
                    return
            except OSError:
                pass
            os.setxattr(path, "user.com.dropbox.ignored", b"1")
        elif sys.platform == "darwin":
            import ctypes
            libc = ctypes.CDLL(None, use_errno=True)
            args = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint32, ctypes.c_int]
            libc.getxattr.argtypes, libc.getxattr.restype = args, ctypes.c_ssize_t
            libc.setxattr.argtypes, libc.setxattr.restype = args, ctypes.c_int
            name, raw = b"com.dropbox.ignored", os.fsencode(path)
            if libc.getxattr(raw, name, None, 0, 0, 0) < 0:
                libc.setxattr(raw, name, b"1", 1, 0, 0)
    except (OSError, AttributeError):  # no xattr support: nothing to sync away from
        pass


def self_ignore(directory) -> None:
    """Create a state directory that git and Dropbox both leave alone.

    Every writer that may create the directory calls this. The Dropbox flag is
    set before the `.gitignore` is written, so an existing `.gitignore` means
    the flag was set too.
    """
    directory = Path(directory)
    try:
        directory.mkdir(parents=True, exist_ok=True)
        ignore = directory / ".gitignore"
        if not ignore.exists():
            dropbox_ignore(directory)
            ignore.write_text("*\n", encoding="utf-8")
    except OSError:  # a read-only checkout
        pass


def project_ref(project_root, path) -> str:
    """*path* relative to the project root, as reports and records carry it."""
    return Path(os.path.relpath(path, project_root)).as_posix()


def stamps_ref(project_root, plan_root=None) -> str:
    """Project-relative directory holding the check stamps."""
    return project_ref(project_root, state_dir(project_root, plan_root) / "stamps")
