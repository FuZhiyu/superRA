#!/usr/bin/env python3
"""Where a project keeps its reproduction records and this machine's state.

Stdlib only, and light enough for the hooks to import.

- **In the task root** (default): `<task root>/.repro/` holds the committed
  lock and acceptance records, and `local/` inside it this machine's state.
- **At the project root** (where they sat before): `repro-lock.json`,
  `repro-acceptance/`, and `.superra-repro/`. A project whose records sit
  there keeps reading and writing them there until `superra repro migrate`.
"""

from __future__ import annotations

import os
from pathlib import Path

TASK_ROOT_DIRNAME = "superRA"
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


def repro_home(project_root, plan_root=None) -> Path:
    """`<task root>/.repro`, spelled below *project_root* when the task root is its child."""
    root = Path(project_root)
    if plan_root is None:
        return root / TASK_ROOT_DIRNAME / REPRO_DIRNAME
    plan = Path(plan_root)
    if plan.parent != root and os.path.realpath(plan.parent) == os.path.realpath(root):
        plan = root / plan.name
    return plan / REPRO_DIRNAME


def records_dir(project_root, plan_root=None) -> Path | None:
    """`<task root>/.repro` when the committed records live in the task root; None while they sit at the project root."""
    home = repro_home(project_root, plan_root)
    if (home / TREE_LOCK_FILENAME).is_file() or (home / TREE_ACCEPTANCE_DIRNAME).is_dir():
        return home
    root = Path(project_root)
    return None if any(os.path.lexists(root / name) for name in ROOT_RECORDS) else home


def state_dir(project_root, plan_root=None) -> Path:
    """This machine's state directory: in the task root, or the root-level one the project still carries."""
    local = repro_home(project_root, plan_root) / LOCAL_DIRNAME
    legacy = Path(project_root) / ROOT_STATE_DIRNAME
    if local.is_dir():
        return local
    if legacy.is_dir() or records_dir(project_root, plan_root) is None:
        return legacy
    return local


def project_ref(project_root, path) -> str:
    """*path* relative to the project root, as reports and records carry it."""
    return Path(os.path.relpath(path, project_root)).as_posix()


def stamps_ref(project_root, plan_root=None) -> str:
    """Project-relative directory holding the check stamps."""
    return project_ref(project_root, state_dir(project_root, plan_root) / "stamps")
