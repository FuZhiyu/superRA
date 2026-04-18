#!/usr/bin/env python3
"""Discovery helpers for syncing non-git data between git worktrees."""

from __future__ import annotations

import subprocess
from pathlib import Path


def _run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def list_worktrees(cwd: Path) -> list[Path]:
    """List worktrees for the git repository containing cwd."""
    result = _run_git(["worktree", "list", "--porcelain"], cwd)
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        raise RuntimeError(stderr or "Not inside a git worktree")

    worktrees: list[Path] = []
    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            worktrees.append(Path(line.split(" ", 1)[1]).resolve())

    if not worktrees:
        raise RuntimeError("Could not discover worktrees for this repository")

    return worktrees


def get_main_worktree(cwd: Path) -> Path:
    """Return the main worktree path for the repository containing cwd."""
    return list_worktrees(cwd)[0]


def resolve_endpoints(cwd: Path, to_path: str, from_path: str | None) -> tuple[Path, Path]:
    """Resolve and validate source/destination worktree endpoints."""
    known = list_worktrees(cwd)
    known_map = {path.resolve(): path.resolve() for path in known}

    resolved_to = Path(to_path).expanduser().resolve()
    if resolved_to not in known_map:
        raise ValueError(f"--to must be an existing git worktree in this repository: {resolved_to}")

    if from_path:
        resolved_from = Path(from_path).expanduser().resolve()
        if resolved_from not in known_map:
            raise ValueError(f"--from must be an existing git worktree in this repository: {resolved_from}")
    else:
        resolved_from = get_main_worktree(cwd)

    if resolved_from == resolved_to:
        raise ValueError("--from and --to must be different worktrees")

    return resolved_from, resolved_to


def normalize_annotation_pattern(pattern: str) -> str:
    """Normalize .gitignore annotation patterns to a concrete repo path."""
    normalized = pattern.strip().rstrip("/")
    if "/**" in normalized:
        normalized = normalized.split("/**")[0]
    elif "/*" in normalized:
        normalized = normalized.split("/*")[0]
    return normalized


def parse_data_sync_annotations(repo_root: Path) -> set[str]:
    """Parse annotation roots from .gitignore.

    Supported tags:
    - # data-sync:symlink (preferred)
    - # worktree:symlink (legacy)
    """
    symlink_paths: set[str] = set()
    gitignore_path = repo_root / ".gitignore"
    if not gitignore_path.exists():
        return symlink_paths

    for line in gitignore_path.read_text().splitlines():
        if "# data-sync:symlink" not in line and "# worktree:symlink" not in line:
            continue

        pattern = line.split("#", 1)[0].strip()
        if not pattern:
            continue

        normalized = normalize_annotation_pattern(pattern)
        if normalized:
            symlink_paths.add(normalized)

    return symlink_paths


def get_gitignored_paths(repo_root: Path) -> list[tuple[Path, bool]]:
    """Get ignored paths from git with directory hints."""
    result = _run_git(
        ["ls-files", "--others", "--ignored", "--exclude-standard", "--directory"],
        repo_root,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []

    paths: list[tuple[Path, bool]] = []
    for line in result.stdout.strip().splitlines():
        is_dir = line.endswith("/")
        paths.append((Path(line.rstrip("/")), is_dir))
    return paths


def is_within_repo(target: Path, repo_root: Path) -> bool:
    """Return True when target resolves under repo_root."""
    try:
        target.resolve().relative_to(repo_root.resolve())
        return True
    except ValueError:
        return False


def _is_under(base: str, maybe_child: str) -> bool:
    return maybe_child == base or maybe_child.startswith(base + "/")


def _is_symlink_only(path: str, shared_roots: set[str]) -> bool:
    return any(_is_under(root, path) for root in shared_roots)


def _entry_kind_for_source(source: Path) -> str | None:
    if source.is_dir():
        return "directory"
    if source.is_file():
        return "file"
    return None


def promote_ignored_path_to_symlink_dir_root(repo_root: Path, rel_path: Path) -> tuple[Path, bool]:
    """Promote ignored descendants under symlinked dirs to the symlink directory root."""
    current = rel_path
    seen: set[Path] = set()

    while True:
        if current in seen:
            break
        seen.add(current)

        item = repo_root / current
        if item.is_symlink():
            try:
                resolved = item.resolve()
            except (OSError, RuntimeError):
                break
            if resolved.exists() and resolved.is_dir():
                return current, True

        parent = current.parent
        if parent == current or str(parent) in ("", "."):
            break
        current = parent

    return rel_path, False


def _tracked_external_symlink_paths(repo_root: Path) -> list[str]:
    """Return repo-relative paths that are tracked symlinks."""
    result = _run_git(["ls-files", "-s"], repo_root)
    if result.returncode != 0:
        return []

    paths: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        meta, rel_path = line.split("\t", 1)
        mode = meta.split(" ", 1)[0]
        if mode == "120000":
            paths.append(rel_path)
    return paths


def _contains(ancestor: Path, target: Path) -> bool:
    try:
        target.relative_to(ancestor)
        return True
    except ValueError:
        return False


def discover_managed_entries(source_worktree: Path, dest_worktree: Path | None = None) -> list[dict]:
    """Discover managed non-git entries from source worktree state.

    When `dest_worktree` is provided, entries whose resolved source path
    contains it are skipped to avoid creating a self-referential link or
    recursive copy when the destination worktree is nested inside a
    gitignored directory of the source (e.g., `/repo/.worktrees/foo`
    seeded from `/repo` where `.worktrees/` is gitignored).
    """
    shared_roots = parse_data_sync_annotations(source_worktree)
    by_path: dict[str, dict] = {}
    priority: dict[str, int] = {}
    dest_resolved = dest_worktree.resolve() if dest_worktree is not None else None

    def add_entry(path: str, source: Path, origin_priority: int) -> None:
        if not path:
            return
        kind = _entry_kind_for_source(source)
        if kind is None:
            return
        if dest_resolved is not None and _contains(source, dest_resolved):
            return
        if path in priority and priority[path] > origin_priority:
            return

        by_path[path] = {
            "path": path,
            "source": str(source),
            "entry_kind": kind,
            "symlink_only": _is_symlink_only(path, shared_roots),
        }
        priority[path] = origin_priority

    ignored_candidates = sorted(
        get_gitignored_paths(source_worktree),
        key=lambda x: (len(x[0].parts), 0 if x[1] else 1, str(x[0])),
    )
    ignored_dir_roots: list[str] = []

    for rel_path, is_dir_hint in ignored_candidates:
        promoted_path, promoted_dir_hint = promote_ignored_path_to_symlink_dir_root(source_worktree, rel_path)
        rel_str = str(promoted_path)
        is_dir_hint = is_dir_hint or promoted_dir_hint
        if any(_is_under(root, rel_str) for root in ignored_dir_roots):
            continue

        src_item = source_worktree / promoted_path
        if not (src_item.exists() or src_item.is_symlink()):
            continue

        try:
            resolved = src_item.resolve()
        except (OSError, RuntimeError):
            continue

        if not resolved.exists():
            continue

        add_entry(rel_str, resolved, origin_priority=30)
        if is_dir_hint:
            ignored_dir_roots.append(rel_str)

    for rel_path in _tracked_external_symlink_paths(source_worktree):
        src_item = source_worktree / rel_path
        if not src_item.is_symlink():
            continue

        try:
            resolved = src_item.resolve()
        except (OSError, RuntimeError):
            continue

        if not resolved.exists() or is_within_repo(resolved, source_worktree):
            continue

        add_entry(rel_path, resolved, origin_priority=20)

    for item in source_worktree.iterdir():
        if item.name == ".git" or not item.is_symlink():
            continue
        try:
            resolved = item.resolve()
        except (OSError, RuntimeError):
            continue
        if resolved.exists():
            add_entry(item.name, resolved, origin_priority=10)

    for root in sorted(shared_roots):
        src_item = source_worktree / root
        if not (src_item.exists() or src_item.is_symlink()):
            continue
        try:
            resolved = src_item.resolve()
        except (OSError, RuntimeError):
            continue
        if not resolved.exists():
            continue
        add_entry(root, resolved, origin_priority=40)
        if root in by_path:
            by_path[root]["symlink_only"] = True

    return [by_path[path] for path in sorted(by_path)]
