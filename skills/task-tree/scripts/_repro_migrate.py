#!/usr/bin/env python3
"""`superra repro migrate`: move root-level reproduction records and state into the task root.

The layouts are `_repro_layout`'s. Everything that can refuse is checked
before anything changes. The records are staged as copies and published in one
rename, then the state moves, then the root-level originals go. The staging
folder stays from the first change to the last, and a status computed while
it exists refuses (`RunnerPaths.settled`), so no reader mixes two layouts. An
interrupted run keeps the marker and leaves root-level originals that equal
what is published; running it again finishes the move. Nothing here touches git: the moves are plain
renames, and the closing lines name the commands that stage them.
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
from contextlib import ExitStack
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
        try:
            normalized = _normalize(record)
            records[name] = json.loads(json.dumps(portable_record(normalized))) if normalized is not None else None
        except (AttributeError, KeyError, TypeError, ValueError):  # a sealed record whose inner rows are malformed
            records[name] = None
        if records[name] is None:
            del records[name]
            bad.append(name)
    if bad:
        raise ReproStateError(f"{ledger.name} holds {len(bad)} record(s) that cannot be converted: "
                              f"{', '.join(sorted(bad))}. Remove them from the file, then rerun. Nothing was moved.")
    return records


def _discard_lock_only(directory: Path) -> None:
    """Remove a state folder that holds nothing but its lock. Call it with that lock held.

    A process that opened the lock file before this removes it then finds, on taking
    the lock, that it holds a file no longer at that path, and stops (`mutation_lock`).
    """
    try:
        names = set(os.listdir(directory))
    except OSError:
        return
    if names <= {"mutation.lock", ".gitignore"}:
        for name in names:
            (directory / name).unlink(missing_ok=True)
        try:
            directory.rmdir()
        except OSError:
            pass


def migrate(project_root: Path, plan_root: Path, dry_run: bool = False) -> tuple[list[str], int]:
    """Move the lock, the acceptance records, and this machine's state; the lines to print and the exit code."""
    root = Path(project_root)
    home = layout.repro_home(root, plan_root)
    old = RunnerPaths(project_root=root, state_dir=root / layout.ROOT_STATE_DIRNAME)
    new = RunnerPaths(project_root=root, state_dir=home / layout.LOCAL_DIRNAME, records_dir=home)
    root_layout = layout.records_dir(root, plan_root) is None
    had = (old.state_dir.is_dir(), new.state_dir.is_dir())
    if not had[0] and not any(os.path.lexists(root / name) for name in layout.ROOT_RECORDS):
        return ["Nothing to migrate: no reproduction records or state at the project root."], 0
    if dry_run:
        return _migrate(root, home, old, new, root_layout, *had, dry_run=True)
    # A writer locks the state folder its layout resolves to; that folder is locked first, made if need be,
    # so a writer starting now waits. The other one is locked when it exists. Neither is made only for its
    # lock in a place a reader would then take for the state.
    active = old if layout.state_dir(root, plan_root) == old.state_dir else new
    other = new if active is old else old
    with ExitStack() as locks:
        locks.enter_context(mutation_lock(active))  # refuses while a build or an acceptance runs
        if other.state_dir.is_dir():
            locks.enter_context(mutation_lock(other))
        return _migrate(root, home, old, new, root_layout, *had, dry_run=False)


def _migrate(root: Path, home: Path, old: RunnerPaths, new: RunnerPaths, root_layout: bool, had_root_state: bool,
             had_local_state: bool, *, dry_run: bool) -> tuple[list[str], int]:
    """`migrate` under its locks: what to move is read, checked, and moved with nothing else writing records."""
    ledger = root / LEGACY_LEDGER
    ref = new.ref

    lock = old.lock_file if old.lock_file.is_file() else old.legacy_lock_file if old.legacy_lock_file.is_file() else None
    converted = lock is not None and lock != old.lock_file
    records = sorted(old.acceptance_dir.glob("*.json")) if old.acceptance_dir.is_dir() else []
    both_states = had_root_state and had_local_state
    moves_state = had_root_state and not had_local_state

    # Everything that can refuse, before anything changes.
    document = read_lock_document(old.lock_file) if converted else None
    ledger_records = _ledger_records(ledger)
    if both_states and root_layout:
        return [f"Error: both {ref(old.state_dir)}/ and {ref(new.state_dir)}/ hold this machine's state. The root-level "
                f"one belongs to the records being moved. {ref(new.state_dir)}/ holds the run records, logs, and check "
                "stamps of the branches whose records are already in the task root: move it aside, rerun, and put it "
                "back only to return to one of those branches unmigrated. Nothing was moved."], 1
    # A task-root lock equal to the root-level one, or to its conversion, is what an interrupted run left.
    lock_same = (lock is not None and new.lock_file.is_file() and new.lock_file.read_text(encoding="utf-8")
                 == (lock_text(document) if converted else old.lock_file.read_text(encoding="utf-8")))
    clash = [ref(new.lock_file)] if lock is not None and new.lock_file.exists() and not lock_same else []
    same = [record for record in records if (new.acceptance_dir / record.name).is_file()
            and (new.acceptance_dir / record.name).read_bytes() == record.read_bytes()]
    clash += [ref(new.acceptance_dir / record.name) for record in records
              if (new.acceptance_dir / record.name).exists() and record not in same]
    for name, record in list(ledger_records.items()):
        target = new.acceptance_dir / f"{name}.json"
        if (old.acceptance_dir / f"{name}.json").is_file():
            del ledger_records[name]  # in the root layout a per-step record already wins over the ledger's
        elif target.exists():
            try:
                differs = json.loads(target.read_text(encoding="utf-8")) != record
            except (OSError, ValueError):
                differs = True
            if differs:
                clash.append(ref(target))
            else:
                del ledger_records[name]
    if clash:
        return [f"Error: {', '.join(sorted(set(clash)))} already exists and differs from the root-level copy. "
                "Merge the two by hand, remove the root-level copy, and rerun. Nothing was moved."], 1

    rows = []  # (source, target, note)
    if lock is not None:
        rows.append((ref(lock), ref(new.lock_file), "converted" if converted else ""))
    if records:
        rows.append((ref(old.acceptance_dir) + "/", ref(new.acceptance_dir) + "/", f"{len(records)} record(s)"))
    if ledger.is_file():
        rows.append((ref(ledger), ref(new.acceptance_dir) + "/", "converted to one record per step"))
    if moves_state:
        rows.append((ref(old.state_dir) + "/", ref(new.state_dir) + "/", "this machine only; git ignores it"))
    if not rows and not both_states:
        return ["Nothing to migrate: no reproduction records or state at the project root."], 0
    width = max((len(row[0]) for row in rows), default=0)
    lines = [f"{'Would move' if dry_run else 'Moved'} into {ref(home)}/:"] if rows else []
    lines += [f"  {source:<{width}}  ->  {target}" + (f"  ({note})" if note else "") for source, target, note in rows]
    if both_states:
        lines.append(f"Left in place: {ref(old.state_dir)}/, the state of branches whose records are still at the "
                     "project root.")
    if dry_run:
        return lines, 0

    # 1. Stage copies of the records beside their destination. The staging folder is also the marker
    #    readers refuse on (`RunnerPaths.settled`): it stays until the last change below is made.
    staging = layout.staging_dir(root, home.parent)
    staged = staging / "records"
    shutil.rmtree(staging, ignore_errors=True)
    published = False
    try:
        staged.mkdir(parents=True)
        if lock is not None and not lock_same:
            if converted:
                atomic_text(staged / layout.TREE_LOCK_FILENAME, lock_text(document))
            else:
                shutil.copyfile(lock, staged / layout.TREE_LOCK_FILENAME)
        moved_records = [record for record in records if record not in same]
        if moved_records or ledger_records:
            (staged / layout.TREE_ACCEPTANCE_DIRNAME).mkdir()
        for record in moved_records:
            shutil.copyfile(record, staged / layout.TREE_ACCEPTANCE_DIRNAME / record.name)
        for name, record in ledger_records.items():
            atomic_json(staged / layout.TREE_ACCEPTANCE_DIRNAME / f"{name}.json", record)
        # 2. Publish them: one rename when `.repro` does not exist yet, file by file into one that does.
        if not home.exists():
            os.rename(staged, home)
            published = True
        else:
            published = True  # from here a failure leaves some of them in place
            if (staged / layout.TREE_LOCK_FILENAME).is_file():
                os.rename(staged / layout.TREE_LOCK_FILENAME, new.lock_file)
            if (staged / layout.TREE_ACCEPTANCE_DIRNAME).is_dir():
                new.acceptance_dir.mkdir(exist_ok=True)
                for record in sorted((staged / layout.TREE_ACCEPTANCE_DIRNAME).iterdir()):
                    os.rename(record, new.acceptance_dir / record.name)
    except BaseException:
        if not published:  # nothing changed: no reason to hold readers off
            shutil.rmtree(staging, ignore_errors=True)
        raise
    # 3. The state follows; a root-level folder made only to hold the lock goes instead.
    if old.state_dir.is_dir() and not new.state_dir.exists():
        os.rename(old.state_dir, new.state_dir)
    elif not had_root_state:
        _discard_lock_only(old.state_dir)
    # 4. The root-level originals, now copies of what is published.
    if lock == old.lock_file:
        old.lock_file.unlink(missing_ok=True)
    for record in records:
        record.unlink(missing_ok=True)
    if old.acceptance_dir.is_dir() and not any(old.acceptance_dir.iterdir()):
        old.acceptance_dir.rmdir()
    ledger.unlink(missing_ok=True)
    if new.state_dir.is_dir():
        ensure_state_dir(new)
    shutil.rmtree(staging, ignore_errors=True)  # the migration is whole: readers may read again

    gone = [name for name, moved in ((ref(old.lock_file), lock is not None and not converted),
                                     (ref(old.acceptance_dir), bool(records)),
                                     (ref(ledger), any(row[0] == ref(ledger) for row in rows))) if moved]
    if gone or converted:
        staging_command = f"git add -- {shlex.quote(ref(home))}"
        if gone:
            staging_command = (f"git rm -r -q --cached --ignore-unmatch -- "
                               f"{' '.join(shlex.quote(name) for name in gone)} && {staging_command}")
        lines.append(f"Commit the move: `{staging_command}`.")
        lines.append(f"Every checkout and coauthor then needs a superRA that reads {ref(home)}/; "
                     "an older one finds no records there.")
    if converted:
        leftovers = [p.name for p in (old.legacy_lock_file, old.legacy_builds_file) if p.is_file()]
        lines.append(f"No longer read: {', '.join(leftovers)}. Remove them, with "
                     f"`git rm -- {' '.join(shlex.quote(name) for name in leftovers)}` where git tracks them.")
    return lines, 0


__all__ = ["ReproStateError", "migrate"]
