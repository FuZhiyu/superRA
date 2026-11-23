#!/usr/bin/env python3
"""`superra repro migrate`: move root-level reproduction records and state into the task root.

The layouts are `_repro_layout`'s. Everything that can refuse is checked
before the first move, and a move that fails part-way is undone, so readers
never stay on half a record set. Nothing here touches git: the moves are plain
renames, and the closing lines name the commands that stage them.
"""

from __future__ import annotations

import json
import os
import shlex
from contextlib import nullcontext
from pathlib import Path

import _repro_layout as layout
from _repro_acceptance import LEGACY_LEDGER, _normalize, atomic_json, atomic_text, mutation_lock, portable_record
from _repro_state import ReproStateError, RunnerPaths, ensure_state_dir, lock_text, read_lock_document


def _ledger_records(ledger: Path) -> dict[str, dict]:
    """The legacy single-file ledger as one committed record per step; refuses what it cannot convert."""
    if not ledger.is_file():
        return {}
    try:
        value = json.loads(ledger.read_text(encoding="utf-8"))
        if not isinstance(value, dict) or value.get("version") != 1 or not isinstance(value.get("steps"), dict):
            raise ValueError("unsupported or malformed ledger")
    except (OSError, ValueError) as exc:
        raise ReproStateError(f"{ledger.name} cannot be read ({exc}); repair or remove it, then rerun. "
                              "Nothing was moved.") from None
    records, bad = {}, []
    for name, record in value["steps"].items():
        normalized = _normalize(record)
        if normalized is None:
            bad.append(name)
        else:
            records[name] = portable_record(normalized)
    if bad:
        raise ReproStateError(f"{ledger.name} holds {len(bad)} record(s) that cannot be converted: "
                              f"{', '.join(sorted(bad))}. Remove them from the file, then rerun. Nothing was moved.")
    return records


def migrate(project_root: Path, plan_root: Path, dry_run: bool = False) -> tuple[list[str], int]:
    """Move the lock, the acceptance records, and this machine's state; the lines to print and the exit code."""
    root = Path(project_root)
    home = layout.repro_home(root, plan_root)
    old = RunnerPaths(project_root=root, state_dir=root / layout.ROOT_STATE_DIRNAME)
    new = RunnerPaths(project_root=root, state_dir=home / layout.LOCAL_DIRNAME, records_dir=home)
    ledger = root / LEGACY_LEDGER
    ref = new.ref

    lock = old.lock_file if old.lock_file.is_file() else old.legacy_lock_file if old.legacy_lock_file.is_file() else None
    converted = lock is not None and lock != old.lock_file
    records = sorted(old.acceptance_dir.glob("*.json")) if old.acceptance_dir.is_dir() else []
    state = old.state_dir.is_dir() and not new.state_dir.exists()
    stray_state = old.state_dir.is_dir() and new.state_dir.exists()

    # Everything that can refuse, before the first move.
    document = read_lock_document(old.lock_file) if converted else None
    ledger_records = _ledger_records(ledger)
    clash = [ref(new.lock_file)] if lock is not None and new.lock_file.exists() else []
    same = [record for record in records if (new.acceptance_dir / record.name).is_file()
            and (new.acceptance_dir / record.name).read_bytes() == record.read_bytes()]
    clash += [ref(new.acceptance_dir / record.name) for record in records
              if (new.acceptance_dir / record.name).exists() and record not in same]
    if clash:
        return [f"Error: {', '.join(sorted(clash))} already exists and differs from the root-level copy. "
                "Merge the two by hand, remove the root-level copy, and rerun. Nothing was moved."], 1

    rows = []  # (source, target, note)
    if lock is not None:
        rows.append((ref(lock), ref(new.lock_file), "converted" if converted else ""))
    if records:
        rows.append((ref(old.acceptance_dir) + "/", ref(new.acceptance_dir) + "/", f"{len(records)} record(s)"))
    if ledger_records or ledger.is_file():
        rows.append((ref(ledger), ref(new.acceptance_dir) + "/", "converted to one record per step"))
    if state:
        rows.append((ref(old.state_dir) + "/", ref(new.state_dir) + "/", "this machine only; git ignores it"))
    if not rows and not stray_state:
        return ["Nothing to migrate: no reproduction records or state at the project root."], 0
    width = max((len(row[0]) for row in rows), default=0)
    lines = [f"{'Would move' if dry_run else 'Moved'} into {ref(home)}/:"] if rows else []
    lines += [f"  {source:<{width}}  ->  {target}" + (f"  ({note})" if note else "") for source, target, note in rows]
    if stray_state:
        lines.append(f"Left in place: {ref(old.state_dir)}/, since {ref(new.state_dir)}/ already holds this "
                     "machine's state. It is no longer used; remove it.")
    if dry_run:
        return lines, 0

    undo: list = []  # run in reverse when a move fails, so the root-level layout reads whole again

    def move(source: Path, target: Path) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        os.rename(source, target)
        undo.append(lambda: os.rename(target, source))

    def create(target: Path, write) -> None:
        write(target)
        undo.append(lambda: target.unlink(missing_ok=True))

    with mutation_lock(old) if old.state_dir.is_dir() else nullcontext():  # refuses while a build runs
        try:
            if converted:
                create(new.lock_file, lambda target: atomic_text(target, lock_text(document)))
            elif lock is not None:
                move(lock, new.lock_file)
            for record in records:
                if record not in same:
                    move(record, new.acceptance_dir / record.name)
            for name, record in ledger_records.items():
                if not (new.acceptance_dir / f"{name}.json").exists():
                    create(new.acceptance_dir / f"{name}.json", lambda target, record=record: atomic_json(target, record))
            if state:
                move(old.state_dir, new.state_dir)
        except BaseException:
            for step in reversed(undo):
                try:
                    step()
                except OSError:
                    pass
            for emptied in (new.acceptance_dir, home):
                try:
                    emptied.rmdir()
                except OSError:
                    pass
            raise
    # Every move held: drop what they superseded.
    for record in same:
        record.unlink(missing_ok=True)
    if old.acceptance_dir.is_dir() and not any(old.acceptance_dir.iterdir()):
        old.acceptance_dir.rmdir()
    ledger.unlink(missing_ok=True)
    if new.state_dir.is_dir():
        ensure_state_dir(new)

    gone = [name for name, moved in ((ref(old.lock_file), lock is not None and not converted),
                                     (ref(old.acceptance_dir), bool(records)),
                                     (ref(ledger), bool(rows) and any(row[0] == ref(ledger) for row in rows))) if moved]
    if rows and (gone or converted):
        staging = f"git add -- {shlex.quote(ref(home))}"
        if gone:
            staging = (f"git rm -r -q --cached --ignore-unmatch -- {' '.join(shlex.quote(name) for name in gone)} "
                       f"&& {staging}")
        lines.append(f"Commit the move: `{staging}`.")
        lines.append(f"Every checkout and coauthor then needs a superRA that reads {ref(home)}/; "
                     "an older one finds no records there.")
    if converted:
        leftovers = [p.name for p in (old.legacy_lock_file, old.legacy_builds_file) if p.is_file()]
        lines.append(f"No longer read: {', '.join(leftovers)}. Remove them, with "
                     f"`git rm -- {' '.join(shlex.quote(name) for name in leftovers)}` where git tracks them.")
    return lines, 0


__all__ = ["ReproStateError", "migrate"]
