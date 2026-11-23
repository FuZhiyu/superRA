#!/usr/bin/env python3
"""`superra repro migrate`: move root-level reproduction records and state into the task root.

The layouts are `_repro_layout`'s. Nothing here touches git: the moves are
plain renames, and the closing line names the command that stages them.
"""

from __future__ import annotations

import os
from contextlib import nullcontext
from pathlib import Path

import _repro_layout as layout
from _repro_acceptance import LEGACY_LEDGER, _normalize, _read_legacy, atomic_json, atomic_text, mutation_lock, portable_record
from _repro_state import ReproStateError, RunnerPaths, ensure_state_dir, lock_text, read_lock_document


def migrate(project_root: Path, plan_root: Path, dry_run: bool = False) -> tuple[list[str], int]:
    """Move the lock, the acceptance records, and this machine's state; the lines to print and the exit code."""
    root = Path(project_root)
    home = layout.repro_home(root, plan_root)
    old = RunnerPaths(project_root=root, state_dir=root / layout.ROOT_STATE_DIRNAME)
    new = RunnerPaths(project_root=root, state_dir=home / layout.LOCAL_DIRNAME, records_dir=home)
    ledger = root / LEGACY_LEDGER
    lock = old.lock_file if old.lock_file.is_file() else old.legacy_lock_file if old.legacy_lock_file.is_file() else None
    moves = []  # (source, target, note)
    if lock is not None:
        moves.append((lock, new.lock_file, "" if lock == old.lock_file else "converted"))
    if old.acceptance_dir.is_dir():
        moves.append((old.acceptance_dir, new.acceptance_dir, ""))
    if ledger.is_file():
        moves.append((ledger, new.acceptance_dir, "converted to one record per step"))
    if old.state_dir.is_dir():
        moves.append((old.state_dir, new.state_dir, "this machine only; git ignores it"))
    if not moves:
        return ["Nothing to migrate: no reproduction records or state at the project root."], 0
    clash = sorted({new.ref(target) for source, target, _ in moves if target.exists() and source != ledger})
    if clash:
        return [f"Error: {', '.join(clash)} already exists. Merge the root-level copy into it by hand, "
                "remove the root-level copy, and rerun."], 1

    def shown(path: Path) -> str:
        return new.ref(path) + ("/" if path.is_dir() or path in (new.acceptance_dir, new.state_dir) else "")

    rows = [(shown(source), shown(target), note) for source, target, note in moves]
    width = max(len(row[0]) for row in rows)
    lines = [f"{'Would move' if dry_run else 'Moved'} into {new.ref(home)}/:",
             *(f"  {source:<{width}}  ->  {target}" + (f"  ({note})" if note else "") for source, target, note in rows)]
    leftovers = [p.name for p in (old.legacy_lock_file, old.legacy_builds_file) if p.is_file() and lock != old.lock_file]
    if dry_run:
        return lines, 0

    with mutation_lock(old) if old.state_dir.is_dir() else nullcontext():
        if lock == old.lock_file:
            new.lock_file.parent.mkdir(parents=True, exist_ok=True)
            os.rename(lock, new.lock_file)
        elif lock is not None:
            atomic_text(new.lock_file, lock_text(read_lock_document(old.lock_file)))
        if old.acceptance_dir.is_dir():
            new.acceptance_dir.parent.mkdir(parents=True, exist_ok=True)
            os.rename(old.acceptance_dir, new.acceptance_dir)
        if ledger.is_file():
            for name, record in (_read_legacy(old) or {}).items():
                normalized = _normalize(record)
                if normalized is not None and not (new.acceptance_dir / f"{name}.json").exists():
                    atomic_json(new.acceptance_dir / f"{name}.json", portable_record(normalized))
            ledger.unlink()
    if old.state_dir.is_dir():
        new.state_dir.parent.mkdir(parents=True, exist_ok=True)
        os.rename(old.state_dir, new.state_dir)
        ensure_state_dir(new)

    staged = [shown(source).rstrip("/") for source, _, _ in moves if source != old.state_dir]
    if staged:
        lines.append(f"Commit the move: `git add -A -- {' '.join([*staged, new.ref(home)])}`.")
        lines.append(f"Every checkout and coauthor then needs a superRA that reads {new.ref(home)}/; "
                     "an older one finds no records there.")
    if leftovers:
        lines.append(f"No longer read: {', '.join(leftovers)}. Remove with `git rm {' '.join(leftovers)}`.")
    return lines, 0


__all__ = ["ReproStateError", "migrate"]
