#!/usr/bin/env python3
"""Sync non-git data between existing git worktrees."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal

from worktree_data_discovery import discover_managed_entries, resolve_endpoints

Action = Literal["overwrite", "rename"]
Status = Literal["new", "modified", "unchanged"]
SeedSyncMode = Literal["auto", "force-symlink", "force-cow"]

# SF_DATALESS flag indicating cloud-only file (Dropbox, iCloud, etc.)
SF_DATALESS = 0x40000000


@dataclass
class FileChange:
    """Represents a file delta from source to destination worktree."""

    status: Status
    source_path: str
    destination_path: str
    target_path: str
    relative_path: str
    directory: str
    size_source: int
    size_destination: int | None
    mtime_source: float
    mtime_destination: float | None


@dataclass
class SeedSummary:
    copied: int = 0
    symlinked: int = 0
    skipped_existing: int = 0
    errors: int = 0


def is_dataless(path: Path) -> bool:
    """Check whether file is a cloud placeholder file."""
    try:
        flags = os.stat(path).st_flags
        return bool(flags & SF_DATALESS)
    except (OSError, AttributeError):
        return False


def file_hash(path: Path, chunk_size: int = 65536) -> str:
    """Compute MD5 hash for content comparison."""
    hasher = hashlib.md5()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def compare_files(source_file: Path, destination_file: Path, use_hash: bool = False) -> bool:
    """Return True when source and destination files are equivalent."""
    if source_file.is_symlink() or destination_file.is_symlink():
        return False

    source_stat = source_file.stat()
    destination_stat = destination_file.stat()

    if source_stat.st_size != destination_stat.st_size:
        return False

    if not use_hash:
        return abs(source_stat.st_mtime - destination_stat.st_mtime) <= 1

    return file_hash(source_file) == file_hash(destination_file)


def cow_copy_file(source_file: Path, destination_file: Path, dry_run: bool = False) -> bool:
    """Copy file using COW when available, fallback to regular copy."""
    if dry_run:
        return True

    destination_file.parent.mkdir(parents=True, exist_ok=True)

    if destination_file.exists() or destination_file.is_symlink():
        destination_file.unlink()

    try:
        subprocess.run(["cp", "-c", str(source_file), str(destination_file)], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        try:
            shutil.copy2(source_file, destination_file)
            return True
        except (OSError, shutil.Error):
            return False


def _progress(message: str) -> None:
    """Write a progress message to stderr."""
    print(message, file=sys.stderr, flush=True)


def copy_missing_tree(
    source_dir: Path,
    destination_dir: Path,
    summary: SeedSummary,
    dry_run: bool = False,
) -> None:
    """Recursively copy only missing content from source_dir into destination_dir."""
    if not source_dir.exists():
        return

    if not destination_dir.exists() and not dry_run:
        destination_dir.mkdir(parents=True, exist_ok=True)

    for item in source_dir.iterdir():
        destination_item = destination_dir / item.name

        if item.is_symlink():
            if destination_item.exists() or destination_item.is_symlink():
                summary.skipped_existing += 1
                continue
            if not dry_run:
                try:
                    destination_item.parent.mkdir(parents=True, exist_ok=True)
                    destination_item.symlink_to(os.readlink(item))
                except OSError:
                    summary.errors += 1
                    continue
            summary.symlinked += 1
            continue

        if item.is_dir():
            if destination_item.exists() and (destination_item.is_file() or destination_item.is_symlink()):
                summary.skipped_existing += 1
                continue
            if not destination_item.exists() and not dry_run:
                destination_item.mkdir(parents=True, exist_ok=True)
            copy_missing_tree(item, destination_item, summary, dry_run=dry_run)
            continue

        if not item.is_file():
            continue

        if destination_item.exists() or destination_item.is_symlink():
            summary.skipped_existing += 1
            continue

        if is_dataless(item):
            if not dry_run:
                try:
                    destination_item.parent.mkdir(parents=True, exist_ok=True)
                    destination_item.symlink_to(item.resolve())
                except OSError:
                    summary.errors += 1
                    continue
            summary.symlinked += 1
            continue

        if cow_copy_file(item, destination_item, dry_run=dry_run):
            summary.copied += 1
        else:
            summary.errors += 1


def symlink_missing_entry(
    source_path: Path,
    destination_path: Path,
    summary: SeedSummary,
    dry_run: bool = False,
) -> None:
    """Create one symlink for a managed entry without replacing existing content."""
    if destination_path.exists() or destination_path.is_symlink():
        summary.skipped_existing += 1
        return

    if not source_path.exists():
        summary.errors += 1
        return

    if not dry_run:
        try:
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            destination_path.symlink_to(source_path.resolve())
        except OSError:
            summary.errors += 1
            return

    summary.symlinked += 1


def run_seed(
    entries: list[dict],
    destination_root: Path,
    dry_run: bool = False,
    seed_sync_mode: SeedSyncMode = "auto",
    verbose: bool = True,
) -> SeedSummary:
    """Materialize missing managed files into destination worktree."""
    summary = SeedSummary()
    total = len(entries)

    for idx, entry in enumerate(entries, 1):
        source_path = Path(entry["source"])
        destination_path = destination_root / entry["path"]
        entry_kind = entry.get("entry_kind", "directory")

        if verbose:
            _progress(f"  Seeding [{idx}/{total}] {entry['path']} ...")

        if seed_sync_mode == "auto" and entry.get("symlink_only", False):
            symlink_missing_entry(source_path, destination_path, summary, dry_run=dry_run)
            continue

        if seed_sync_mode == "force-symlink":
            symlink_missing_entry(source_path, destination_path, summary, dry_run=dry_run)
            continue

        if entry_kind == "directory":
            copy_missing_tree(source_path, destination_path, summary, dry_run=dry_run)
            continue

        if destination_path.exists() or destination_path.is_symlink():
            summary.skipped_existing += 1
            continue

        if not source_path.exists():
            summary.errors += 1
            continue

        if is_dataless(source_path):
            if not dry_run:
                try:
                    destination_path.parent.mkdir(parents=True, exist_ok=True)
                    destination_path.symlink_to(source_path.resolve())
                except OSError:
                    summary.errors += 1
                    continue
            summary.symlinked += 1
            continue

        if cow_copy_file(source_path, destination_path, dry_run=dry_run):
            summary.copied += 1
        else:
            summary.errors += 1

    return summary


def diff_file(
    source_file: Path,
    destination_file: Path,
    rel_path: str,
    dir_name: str,
    include_unmodified: bool = False,
    use_hash: bool = False,
) -> FileChange | None:
    """Compare one source file against destination counterpart."""
    if not source_file.exists() or source_file.is_symlink():
        return None

    source_stat = source_file.stat()

    if destination_file.is_symlink():
        return None

    if not destination_file.exists():
        return FileChange(
            status="new",
            source_path=str(source_file),
            destination_path=str(destination_file),
            target_path=str(destination_file),
            relative_path=rel_path,
            directory=dir_name,
            size_source=source_stat.st_size,
            size_destination=None,
            mtime_source=source_stat.st_mtime,
            mtime_destination=None,
        )

    if not destination_file.is_file():
        return FileChange(
            status="modified",
            source_path=str(source_file),
            destination_path=str(destination_file),
            target_path=str(destination_file),
            relative_path=rel_path,
            directory=dir_name,
            size_source=source_stat.st_size,
            size_destination=None,
            mtime_source=source_stat.st_mtime,
            mtime_destination=None,
        )

    destination_stat = destination_file.stat()

    if not compare_files(source_file, destination_file, use_hash=use_hash):
        return FileChange(
            status="modified",
            source_path=str(source_file),
            destination_path=str(destination_file),
            target_path=str(destination_file),
            relative_path=rel_path,
            directory=dir_name,
            size_source=source_stat.st_size,
            size_destination=destination_stat.st_size,
            mtime_source=source_stat.st_mtime,
            mtime_destination=destination_stat.st_mtime,
        )

    if include_unmodified:
        return FileChange(
            status="unchanged",
            source_path=str(source_file),
            destination_path=str(destination_file),
            target_path=str(destination_file),
            relative_path=rel_path,
            directory=dir_name,
            size_source=source_stat.st_size,
            size_destination=destination_stat.st_size,
            mtime_source=source_stat.st_mtime,
            mtime_destination=destination_stat.st_mtime,
        )

    return None


def diff_directory(
    source_dir: Path,
    destination_dir: Path,
    dir_name: str,
    include_unmodified: bool = False,
    use_hash: bool = False,
) -> list[FileChange]:
    """Diff source directory against destination directory by walking source files."""
    changes: list[FileChange] = []

    for root, dirs, files in os.walk(source_dir, followlinks=False):
        dirs[:] = [d for d in dirs if d != ".git"]
        root_path = Path(root)
        rel_root = root_path.relative_to(source_dir)
        destination_root = destination_dir / rel_root

        for filename in files:
            if filename == ".git":
                continue

            source_file = root_path / filename
            if source_file.is_symlink():
                continue

            destination_file = destination_root / filename
            rel_path = str(rel_root / filename)

            change = diff_file(
                source_file,
                destination_file,
                rel_path,
                dir_name,
                include_unmodified=include_unmodified,
                use_hash=use_hash,
            )
            if change:
                changes.append(change)

    return changes


def collect_changes(
    entries: list[dict],
    destination_root: Path,
    include_unmodified: bool = False,
    use_hash: bool = False,
    verbose: bool = True,
) -> list[FileChange]:
    """Collect source->destination change records for managed entries."""
    all_changes: list[FileChange] = []
    diffable = [e for e in entries if not e.get("symlink_only", False)]
    total = len(diffable)

    for idx, entry in enumerate(diffable, 1):
        entry_path = entry["path"]

        if verbose:
            _progress(f"  Scanning [{idx}/{total}] {entry_path} ...")
        source_path = Path(entry["source"])
        destination_item = destination_root / entry_path
        entry_kind = entry.get("entry_kind", "directory")

        if entry_kind == "directory":
            if source_path.exists() and source_path.is_dir():
                all_changes.extend(
                    diff_directory(
                        source_path,
                        destination_item,
                        entry_path,
                        include_unmodified=include_unmodified,
                        use_hash=use_hash,
                    )
                )
            continue

        if entry_kind == "file":
            change = diff_file(
                source_path,
                destination_item,
                "",
                entry_path,
                include_unmodified=include_unmodified,
                use_hash=use_hash,
            )
            if change:
                all_changes.append(change)

    return sorted(all_changes, key=lambda c: (c.directory, c.relative_path, c.source_path))


def summarize_changes(changes: list[FileChange]) -> dict[str, int]:
    """Return summary counts by status."""
    return {
        "new": len([change for change in changes if change.status == "new"]),
        "modified": len([change for change in changes if change.status == "modified"]),
        "unchanged": len([change for change in changes if change.status == "unchanged"]),
    }


def format_size(size: int | None) -> str:
    """Format bytes for display."""
    if size is None:
        return "n/a"

    value = float(size)
    for unit in ["B", "KB", "MB", "GB"]:
        if value < 1024:
            return f"{value:.1f}{unit}"
        value /= 1024
    return f"{value:.1f}TB"


def _is_within(base: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(base)
        return True
    except ValueError:
        return False


def _normalize_user_relative_path(path_text: str) -> Path:
    candidate = Path(path_text)
    if candidate.is_absolute():
        raise ValueError(f"Path must be relative: {path_text}")
    if any(part == ".." for part in candidate.parts):
        raise ValueError(f"Parent directory traversal is not allowed: {path_text}")

    normalized = Path(os.path.normpath(str(candidate)))
    if normalized == Path(".") or str(normalized) == "":
        raise ValueError("Path must not be empty")
    if normalized.is_absolute() or any(part == ".." for part in normalized.parts):
        raise ValueError(f"Path must stay within worktree roots: {path_text}")
    return normalized


def _safe_join_under(base: Path, relative: Path) -> Path:
    base_abs = Path(os.path.abspath(base))
    joined = Path(os.path.abspath(base_abs / relative))
    if not _is_within(base_abs, joined):
        raise ValueError(f"Resolved path escapes base root: {joined}")
    return joined


def _allowed_source_roots(entries: list[dict]) -> list[Path]:
    roots: list[Path] = []
    for entry in entries:
        if entry.get("symlink_only", False):
            continue
        roots.append(Path(entry["source"]).resolve(strict=False))
    return roots


def _validate_source_path(source_path: Path, allowed_roots: list[Path] | None) -> None:
    if not allowed_roots:
        return

    resolved_source = source_path.resolve(strict=False)
    if not any(_is_within(root, resolved_source) for root in allowed_roots):
        raise ValueError(f"Source path is outside managed roots: {resolved_source}")


def _build_target_path_from_change(change: dict, destination_root: Path | None) -> Path:
    if destination_root is None:
        target_path = change.get("target_path") or change.get("destination_path")
        if not target_path:
            raise ValueError("Each change record must include target_path or destination_path")
        return Path(target_path)

    directory = change.get("directory")
    if not directory:
        raise ValueError("Each change record must include directory when --to is provided")

    rel_target = _normalize_user_relative_path(str(directory))
    relative_path = change.get("relative_path")
    if relative_path:
        rel_target = rel_target / _normalize_user_relative_path(str(relative_path))

    return _safe_join_under(destination_root, rel_target)


def rename_path(path: Path, suffix: str) -> Path:
    """Add suffix before extension."""
    return path.with_name(f"{path.stem}{suffix}{path.suffix}")


def process_file(
    source_file: Path,
    target_file: Path,
    action: Action,
    suffix: str,
    dry_run: bool = False,
    verbose: bool = True,
) -> bool:
    """Apply selected sync action to a single file."""
    if source_file.is_symlink() or not source_file.exists() or not source_file.is_file():
        if verbose:
            print(f"  SKIP: not a regular source file: {source_file}")
        return False

    destination = target_file if action == "overwrite" else rename_path(target_file, suffix)

    if verbose:
        print(f"  {action.upper()}: {source_file} -> {destination}")

    return cow_copy_file(source_file, destination, dry_run=dry_run)


def process_changes(
    changes: list[dict],
    action: Action,
    suffix: str,
    destination_root: Path | None = None,
    allowed_source_roots: list[Path] | None = None,
    status_filter: set[str] | None = None,
    dry_run: bool = False,
    verbose: bool = True,
) -> tuple[int, int]:
    """Apply overwrite/rename actions from JSON-like change records."""
    success = 0
    failure = 0

    filtered = changes
    if status_filter:
        filtered = [change for change in filtered if change.get("status") in status_filter]

    total = len(filtered)
    for idx, change in enumerate(filtered, 1):
        source_path_value = change.get("source_path")
        if not source_path_value:
            raise ValueError("Each change record must include source_path")

        if verbose and total > 1:
            display = change.get("directory", "")
            rel = change.get("relative_path")
            if rel:
                display = f"{display}/{rel}"
            _progress(f"  Applying [{idx}/{total}] {display} ...")

        source_path = Path(source_path_value).resolve(strict=False)
        _validate_source_path(source_path, allowed_source_roots)
        target_path = _build_target_path_from_change(change, destination_root)

        if process_file(source_path, target_path, action, suffix, dry_run=dry_run, verbose=verbose):
            success += 1
        else:
            failure += 1

    return success, failure


def process_from_json(
    json_path: Path,
    action: Action,
    suffix: str,
    source_root: Path | None = None,
    destination_root: Path | None = None,
    entries: list[dict] | None = None,
    status_filter: set[str] | None = None,
    dry_run: bool = False,
    verbose: bool = True,
) -> tuple[int, int]:
    """Process actions from diff JSON output."""
    with open(json_path, encoding="utf-8") as handle:
        data = json.load(handle)

    if source_root is not None and data.get("from_worktree"):
        json_source = Path(data["from_worktree"]).resolve(strict=False)
        if json_source != source_root.resolve(strict=False):
            raise ValueError(
                f"JSON from_worktree does not match --from endpoint: {json_source} != {source_root}"
            )

    if destination_root is not None and data.get("to_worktree"):
        json_destination = Path(data["to_worktree"]).resolve(strict=False)
        if json_destination != destination_root.resolve(strict=False):
            raise ValueError(
                f"JSON to_worktree does not match --to endpoint: {json_destination} != {destination_root}"
            )

    changes = data.get("changes", [])
    allowed_roots = _allowed_source_roots(entries) if entries else None
    return process_changes(
        changes,
        action,
        suffix,
        destination_root=destination_root,
        allowed_source_roots=allowed_roots,
        status_filter=status_filter,
        dry_run=dry_run,
        verbose=verbose,
    )


def _find_entry_for_relative_path(entries: list[dict], rel_path: Path) -> dict | None:
    candidates = sorted(
        [entry for entry in entries if not entry.get("symlink_only", False)],
        key=lambda entry: len(Path(entry["path"]).parts),
        reverse=True,
    )
    for entry in candidates:
        base = Path(entry["path"])
        if rel_path == base or base in rel_path.parents:
            return entry
    return None


def process_files(
    entries: list[dict],
    destination_root: Path,
    files: list[str],
    action: Action,
    suffix: str,
    dry_run: bool = False,
    verbose: bool = True,
) -> tuple[int, int]:
    """Apply actions for explicit relative paths from source worktree."""
    success = 0
    failure = 0

    for file_arg in files:
        try:
            rel_path = _normalize_user_relative_path(file_arg)
        except ValueError as error:
            if verbose:
                print(f"  SKIP: {error}", file=sys.stderr)
            failure += 1
            continue

        entry = _find_entry_for_relative_path(entries, rel_path)
        if not entry:
            if verbose:
                print(f"  SKIP: not in managed entries: {file_arg}", file=sys.stderr)
            failure += 1
            continue

        entry_rel = Path(entry["path"])
        source_base = Path(entry["source"]).resolve(strict=False)
        try:
            rel_inside_entry = rel_path.relative_to(entry_rel) if rel_path != entry_rel else Path(".")
        except ValueError:
            if verbose:
                print(f"  SKIP: file is outside managed entry: {file_arg}", file=sys.stderr)
            failure += 1
            continue

        try:
            source_target = source_base if rel_inside_entry == Path(".") else _safe_join_under(source_base, rel_inside_entry)
            target_file = _safe_join_under(destination_root, rel_path)
        except ValueError as error:
            if verbose:
                print(f"  SKIP: {error}", file=sys.stderr)
            failure += 1
            continue

        if source_target.is_dir():
            for root, _, file_names in os.walk(source_target, followlinks=False):
                root_path = Path(root)
                rel_from_requested = root_path.relative_to(source_target)
                for file_name in file_names:
                    source_file = root_path / file_name
                    if source_file.is_symlink():
                        continue
                    rel_to_repo = rel_path / rel_from_requested / file_name
                    try:
                        target_file = _safe_join_under(destination_root, rel_to_repo)
                    except ValueError as error:
                        if verbose:
                            print(f"  SKIP: {error}", file=sys.stderr)
                        failure += 1
                        continue
                    if process_file(source_file, target_file, action, suffix, dry_run=dry_run, verbose=verbose):
                        success += 1
                    else:
                        failure += 1
            continue

        if process_file(source_target, target_file, action, suffix, dry_run=dry_run, verbose=verbose):
            success += 1
        else:
            failure += 1

    return success, failure


def interactive_mode(
    json_path: Path,
    suffix: str,
    source_root: Path | None = None,
    destination_root: Path | None = None,
    entries: list[dict] | None = None,
    dry_run: bool = False,
) -> None:
    """Interactive apply mode from diff JSON output."""
    with open(json_path, encoding="utf-8") as handle:
        data = json.load(handle)

    if source_root is not None and data.get("from_worktree"):
        json_source = Path(data["from_worktree"]).resolve(strict=False)
        if json_source != source_root.resolve(strict=False):
            raise ValueError(
                f"JSON from_worktree does not match --from endpoint: {json_source} != {source_root}"
            )

    if destination_root is not None and data.get("to_worktree"):
        json_destination = Path(data["to_worktree"]).resolve(strict=False)
        if json_destination != destination_root.resolve(strict=False):
            raise ValueError(
                f"JSON to_worktree does not match --to endpoint: {json_destination} != {destination_root}"
            )

    changes = [change for change in data.get("changes", []) if change.get("status") in ("new", "modified")]
    if not changes:
        print("No new or modified files to process.")
        return

    print(f"Found {len(changes)} changed files.\n")
    print("Actions: [o]verwrite, [r]ename, [s]kip, [q]uit")
    print("         [O]verwrite all, [R]ename all, [S]kip all\n")

    batch_action: str | None = None

    for index, change in enumerate(changes, start=1):
        display_path = change.get("directory", "")
        if change.get("relative_path"):
            display_path = f"{display_path}/{change['relative_path']}"

        print(f"[{index}/{len(changes)}] {change.get('status', '').upper()}: {display_path}")

        if batch_action:
            action = batch_action
            print(f"  -> {action} (batch)")
        else:
            while True:
                choice = input("  Action [o/r/s/q/O/R/S]: ").strip()
                if choice == "O":
                    action = "overwrite"
                    batch_action = "overwrite"
                    break
                if choice == "R":
                    action = "rename"
                    batch_action = "rename"
                    break
                if choice == "S":
                    action = "skip"
                    batch_action = "skip"
                    break

                lowered = choice.lower()
                if lowered in ("o", "overwrite"):
                    action = "overwrite"
                    break
                if lowered in ("r", "rename"):
                    action = "rename"
                    break
                if lowered in ("s", "skip", ""):
                    action = "skip"
                    break
                if lowered == "q":
                    print("Quit.")
                    return
                print("  Invalid choice. Try again.")

        if action == "skip":
            continue

        source_path_value = change.get("source_path")
        if not source_path_value:
            raise ValueError("Each change record must include source_path")

        source_path = Path(source_path_value).resolve(strict=False)
        allowed_roots = _allowed_source_roots(entries) if entries else None
        _validate_source_path(source_path, allowed_roots)
        target_path = _build_target_path_from_change(change, destination_root)

        process_file(source_path, target_path, action, suffix, dry_run=dry_run, verbose=True)

    print("\nDone.")


def print_diff_report(source_root: Path, destination_root: Path, changes: list[FileChange]) -> None:
    """Print human-readable diff report."""
    summary = summarize_changes(changes)
    print(f"From: {source_root}")
    print(f"To:   {destination_root}\n")

    new_files = [change for change in changes if change.status == "new"]
    modified_files = [change for change in changes if change.status == "modified"]

    if new_files:
        print(f"NEW FILES ({len(new_files)}):")
        for change in new_files:
            display = change.directory if not change.relative_path else f"{change.directory}/{change.relative_path}"
            print(f"  + {display} ({format_size(change.size_source)})")
        print()

    if modified_files:
        print(f"MODIFIED FILES ({len(modified_files)}):")
        for change in modified_files:
            display = change.directory if not change.relative_path else f"{change.directory}/{change.relative_path}"
            size_info = f"{format_size(change.size_destination)} -> {format_size(change.size_source)}"
            print(f"  M {display} ({size_info})")
        print()

    if not new_files and not modified_files:
        print("No new or modified files found.")

    print(
        "Summary: "
        f"{summary['new']} new, {summary['modified']} modified, {summary['unchanged']} unchanged"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sync non-git data between existing git worktrees",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Seed missing managed files from main worktree into a target worktree
  python sync_worktree_data.py --to ../MyRepo-feature --mode seed

  # Diff from worktree A to worktree B
  python sync_worktree_data.py --from ../MyRepo-a --to ../MyRepo-b --mode diff --json

  # Apply overwrite actions from diff JSON
  python sync_worktree_data.py --to ../MyRepo-feature --mode apply --from-json changes.json --action overwrite
        """,
    )

    parser.add_argument("--from", dest="from_path", help="Source worktree path (default: main worktree)")
    parser.add_argument("--to", dest="to_path", required=True, help="Destination worktree path")
    parser.add_argument("--mode", choices=["seed", "diff", "apply"], required=True)
    parser.add_argument(
        "--seed-sync-mode",
        choices=["auto", "force-symlink", "force-cow"],
        default="auto",
        help="Seed-only materialization mode override (default: auto)",
    )

    parser.add_argument("--action", choices=["overwrite", "rename"], help="Action for apply mode")
    parser.add_argument("--from-json", type=Path, help="Path to diff JSON output")
    parser.add_argument("--files", nargs="+", help="Relative source paths to process (apply mode)")
    parser.add_argument("--status", nargs="+", choices=["new", "modified", "unchanged"], help="Filter statuses")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive apply mode (requires --from-json)")

    parser.add_argument("--json", action="store_true", help="Output JSON (diff mode only)")
    parser.add_argument("--include-unmodified", action="store_true", help="Include unchanged files in diff output")
    parser.add_argument("--use-hash", action="store_true", help="Use content hash in diff (slower, more accurate)")

    parser.add_argument("--suffix", default="_synced", help="Suffix for rename action")
    parser.add_argument("--timestamp-suffix", action="store_true", help="Use timestamp suffix for rename action")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Show actions without writing files")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress verbose output")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.mode != "diff" and args.json:
        parser.error("--json is only valid with --mode diff")

    if args.mode != "seed" and args.seed_sync_mode != "auto":
        parser.error("--seed-sync-mode is only valid with --mode seed")

    if args.mode == "seed" and (args.action or args.from_json or args.files or args.interactive):
        parser.error("--mode seed does not support apply options")

    if args.mode == "diff" and (args.action or args.from_json or args.files or args.interactive):
        parser.error("--mode diff does not support apply options")

    if args.mode == "apply":
        if args.interactive and not args.from_json:
            parser.error("--interactive requires --from-json")
        if args.interactive and args.action:
            parser.error("--interactive cannot be combined with --action")
        if not args.interactive and not args.action:
            parser.error("--mode apply requires --action unless --interactive is used")

    suffix = args.suffix
    if args.timestamp_suffix:
        suffix = f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    try:
        source_root, destination_root = resolve_endpoints(Path.cwd(), args.to_path, args.from_path)
    except (RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    entries = discover_managed_entries(source_root, dest_worktree=destination_root)

    verbose = not args.quiet

    if args.mode == "seed":
        summary = run_seed(
            entries,
            destination_root,
            dry_run=args.dry_run,
            seed_sync_mode=args.seed_sync_mode,
            verbose=verbose,
        )
        print(f"From: {source_root}")
        print(f"To:   {destination_root}")
        print(f"Seed mode: {args.seed_sync_mode}")
        print(
            "Seed summary: "
            f"copied={summary.copied}, symlinked={summary.symlinked}, "
            f"skipped_existing={summary.skipped_existing}, errors={summary.errors}"
        )
        return

    if args.mode == "diff":
        changes = collect_changes(
            entries,
            destination_root,
            include_unmodified=args.include_unmodified,
            use_hash=args.use_hash,
            verbose=verbose,
        )
        if args.json:
            print(
                json.dumps(
                    {
                        "from_worktree": str(source_root),
                        "to_worktree": str(destination_root),
                        "discovered_entries": entries,
                        "changes": [asdict(change) for change in changes],
                        "summary": summarize_changes(changes),
                    },
                    indent=2,
                )
            )
        else:
            print_diff_report(source_root, destination_root, changes)
        return

    if args.dry_run:
        print("DRY RUN - no changes will be written\n")

    status_filter = set(args.status) if args.status else None
    allowed_roots = _allowed_source_roots(entries)

    if args.interactive:
        interactive_mode(
            args.from_json,
            suffix,
            source_root=source_root,
            destination_root=destination_root,
            entries=entries,
            dry_run=args.dry_run,
        )
        return

    if args.from_json:
        success, failure = process_from_json(
            args.from_json,
            args.action,
            suffix,
            source_root=source_root,
            destination_root=destination_root,
            entries=entries,
            status_filter=status_filter,
            dry_run=args.dry_run,
            verbose=verbose,
        )
    elif args.files:
        success, failure = process_files(
            entries,
            destination_root,
            args.files,
            args.action,
            suffix,
            dry_run=args.dry_run,
            verbose=verbose,
        )
    else:
        changes = [
            asdict(change)
            for change in collect_changes(
                entries,
                destination_root,
                include_unmodified=args.include_unmodified,
                use_hash=args.use_hash,
                verbose=verbose,
            )
        ]
        success, failure = process_changes(
            changes,
            args.action,
            suffix,
            destination_root=destination_root,
            allowed_source_roots=allowed_roots,
            status_filter=status_filter or {"new", "modified"},
            dry_run=args.dry_run,
            verbose=verbose,
        )

    print(f"\nProcessed: {success} success, {failure} failed")


if __name__ == "__main__":
    main()
