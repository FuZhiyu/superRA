#!/usr/bin/env python3
"""Secure task-companion discovery, resolution, and standalone packing."""

from __future__ import annotations

import base64
import itertools
import mimetypes
import os
import stat
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import quote

from _task_io import ATTACHMENTS_DIRNAME, Task, collect_all_tasks

DIRECT_SOURCE_SUFFIXES = {".md", ".py", ".jl", ".r", ".ipynb"}
RESERVED_DIRECT_NAMES = {"task.md", "comments.yaml", ATTACHMENTS_DIRNAME}
ROOT_INFRASTRUCTURE_NAMES = {"superra"}
CACHE_NAMES = {
    "__pycache__",
    ".ipynb_checkpoints",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
}
CACHE_SUFFIXES = {".pyc", ".pyo"}


@dataclass(frozen=True)
class ArtifactLimits:
    """Resource ceilings for manifests, previews, and standalone exports.

    ``max_manifest_bytes`` charges each retained entry's UTF-8 path bytes plus
    ``manifest_entry_overhead``. Export byte limits count raw file bytes before
    base64 expansion.
    """

    max_files: int = 512
    max_manifest_bytes: int = 256 * 1024
    manifest_entry_overhead: int = 256
    max_traversal_entries: int = 4096
    max_preview_bytes: int = 2 * 1024 * 1024
    max_export_file_bytes: int = 2 * 1024 * 1024
    max_export_total_bytes: int = 20 * 1024 * 1024


DEFAULT_ARTIFACT_LIMITS = ArtifactLimits()


class ArtifactPathError(ValueError):
    """A requested artifact path is outside the task companion contract."""


class ArtifactSecurityError(PermissionError):
    """A requested artifact path violates containment or symlink policy."""


class ArtifactTooLargeError(OSError):
    """A bounded artifact read exceeded its byte ceiling."""


@dataclass(frozen=True)
class ArtifactFile:
    path: str
    name: str
    placement: str
    kind: str
    mime: str
    size: int
    mtime_ns: int
    previewable: bool
    download_only: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "name": self.name,
            "placement": self.placement,
            "kind": self.kind,
            "mime": self.mime,
            "size": self.size,
            "mtime_ns": self.mtime_ns,
            "previewable": self.previewable,
            "download_only": self.download_only,
        }


@dataclass
class _TraversalState:
    max_entries: int
    visited_entries: int = 0
    limit_hit: bool = False

    def scan(self, directory: Path) -> list[os.DirEntry[str]]:
        """Return a bounded, sorted snapshot without materializing the directory."""
        if self.limit_hit:
            return []
        entries: list[os.DirEntry[str]] = []
        try:
            with os.scandir(directory) as scanner:
                for entry in scanner:
                    if self.visited_entries >= self.max_entries:
                        self.limit_hit = True
                        break
                    self.visited_entries += 1
                    entries.append(entry)
        except OSError:
            return []
        entries.sort(key=lambda entry: entry.name)
        return entries


_TEXT_SUFFIXES = {
    ".csv",
    ".json",
    ".jsonl",
    ".log",
    ".rst",
    ".tex",
    ".toml",
    ".tsv",
    ".txt",
    ".yaml",
    ".yml",
}
_STATIC_IMAGE_SUFFIXES = {".gif", ".jpeg", ".jpg", ".png", ".webp"}
_ACTIVE_TEXT_SUFFIXES = {".htm", ".html", ".js", ".mjs", ".svg", ".xml"}
_MIME_OVERRIDES = {
    ".md": "text/markdown",
    ".py": "text/x-python",
    ".jl": "text/x-julia",
    ".r": "text/x-r-source",
    ".ipynb": "application/x-ipynb+json",
}


def _hidden_or_cache(name: str) -> bool:
    low = name.lower()
    return (
        not name
        or name.startswith(".")
        or low in CACHE_NAMES
        or Path(low).suffix in CACHE_SUFFIXES
    )


def _reserved_direct(name: str) -> bool:
    return name.lower() in RESERVED_DIRECT_NAMES


def _root_infrastructure(name: str) -> bool:
    return name.lower() in ROOT_INFRASTRUCTURE_NAMES


def _classify(path: Path) -> tuple[str, str, bool]:
    suffix = path.suffix.lower()
    mime = _MIME_OVERRIDES.get(suffix)
    if mime is None:
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"

    if suffix == ".md":
        kind = "markdown"
    elif suffix == ".py":
        kind = "python"
    elif suffix == ".jl":
        kind = "julia"
    elif suffix == ".r":
        kind = "r"
    elif suffix == ".ipynb":
        kind = "notebook"
    elif suffix in _STATIC_IMAGE_SUFFIXES or suffix == ".svg":
        kind = "image"
    elif suffix == ".pdf":
        kind = "pdf"
    elif suffix in _TEXT_SUFFIXES or mime.startswith("text/"):
        kind = "text"
    else:
        kind = "binary"

    safe_inline = (
        kind in {"markdown", "python", "julia", "r", "notebook", "pdf"}
        or suffix in _STATIC_IMAGE_SUFFIXES
        or (kind == "text" and suffix not in _ACTIVE_TEXT_SUFFIXES)
    )
    return kind, mime, safe_inline


def _task_dir_is_secure(plan_root: Path, task: Task) -> bool:
    """Return whether *task* is a real, symlink-free task inside *plan_root*."""
    task_md = task.dir_path / "task.md"
    if task_md.is_symlink() or not task_md.is_file():
        return False
    root_abs = plan_root.absolute()
    task_abs = task.dir_path.absolute()
    try:
        rel = task_abs.relative_to(root_abs)
    except ValueError:
        return False

    current = root_abs
    for part in rel.parts:
        current = current / part
        try:
            if current.is_symlink():
                return False
        except OSError:
            return False

    try:
        return task.dir_path.resolve().is_relative_to(plan_root.resolve())
    except OSError:
        return False


def _artifact_file(path: Path, relative: str, placement: str, limits: ArtifactLimits) -> ArtifactFile | None:
    try:
        info = path.lstat()
    except OSError:
        return None
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        return None
    kind, mime, safe_inline = _classify(path)
    return ArtifactFile(
        path=relative,
        name=path.name,
        placement=placement,
        kind=kind,
        mime=mime,
        size=info.st_size,
        mtime_ns=info.st_mtime_ns,
        previewable=safe_inline and info.st_size <= limits.max_preview_bytes,
        download_only=not safe_inline,
    )


def _attachment_candidates(
    task_dir: Path,
    limits: ArtifactLimits,
    traversal: _TraversalState,
):
    attachments = task_dir / ATTACHMENTS_DIRNAME
    try:
        if attachments.is_symlink() or not attachments.is_dir():
            return
    except OSError:
        return

    pending = [attachments]
    while pending and not traversal.limit_hit:
        current = pending.pop()
        child_dirs: list[Path] = []
        for entry in traversal.scan(current):
            if _hidden_or_cache(entry.name):
                continue
            try:
                if entry.is_symlink():
                    continue
                if entry.is_dir(follow_symlinks=False):
                    child_dirs.append(Path(entry.path))
                    continue
                if not entry.is_file(follow_symlinks=False):
                    continue
            except OSError:
                continue
            candidate = Path(entry.path)
            try:
                relative = candidate.relative_to(task_dir).as_posix()
            except ValueError:
                continue
            item = _artifact_file(candidate, relative, "attachment", limits)
            if item is not None:
                yield item
        pending.extend(reversed(child_dirs))


def build_manifest(
    plan_root: Path,
    task: Task,
    *,
    limits: ArtifactLimits | None = None,
) -> dict[str, object]:
    """Return the bounded companion-file manifest for one real task.

    Direct first-class sources are ordered first, recursive attachment contents
    second, and other unexpected direct files last. The task-tree root wrapper
    is infrastructure rather than a companion. Directories other than
    ``attachments/`` are never traversed.
    """
    active_limits = limits or DEFAULT_ARTIFACT_LIMITS
    traversal = _TraversalState(active_limits.max_traversal_entries)
    if not _task_dir_is_secure(plan_root, task):
        return {
            "task": task.path,
            "files": [],
            "truncated": False,
            "truncation_reason": None,
            "listed_bytes": 0,
            "manifest_bytes": 0,
            "traversal_entries": 0,
            "limits": _manifest_limits(active_limits),
            "unavailable_reason": "synthetic-or-insecure-task",
        }

    direct: list[ArtifactFile] = []
    other: list[ArtifactFile] = []
    for entry in traversal.scan(task.dir_path):
        child = Path(entry.path)
        if (
            _hidden_or_cache(child.name)
            or _reserved_direct(child.name)
            or (task.dir_path == plan_root and _root_infrastructure(child.name))
        ):
            continue
        try:
            if entry.is_symlink() or not entry.is_file(follow_symlinks=False):
                continue
        except OSError:
            continue
        placement = "direct" if child.suffix.lower() in DIRECT_SOURCE_SUFFIXES else "other"
        item = _artifact_file(child, child.name, placement, active_limits)
        if item is not None:
            (direct if placement == "direct" else other).append(item)

    ordered = itertools.chain(
        direct,
        _attachment_candidates(task.dir_path, active_limits, traversal),
        other,
    )
    files: list[dict[str, object]] = []
    manifest_bytes = 0
    listed_bytes = 0
    truncated = False
    truncation_reason: str | None = None
    for item in ordered:
        charge = len(item.path.encode("utf-8")) + active_limits.manifest_entry_overhead
        if len(files) >= active_limits.max_files:
            truncated = True
            truncation_reason = "file-count-limit"
            break
        if manifest_bytes + charge > active_limits.max_manifest_bytes:
            truncated = True
            truncation_reason = "manifest-byte-limit"
            break
        files.append(item.as_dict())
        manifest_bytes += charge
        listed_bytes += item.size

    if not truncated and traversal.limit_hit:
        truncated = True
        truncation_reason = "traversal-entry-limit"

    return {
        "task": task.path,
        "files": files,
        "truncated": truncated,
        "truncation_reason": truncation_reason,
        "listed_bytes": listed_bytes,
        "manifest_bytes": manifest_bytes,
        "traversal_entries": traversal.visited_entries,
        "limits": _manifest_limits(active_limits),
        "unavailable_reason": None,
    }


def _manifest_limits(limits: ArtifactLimits) -> dict[str, int]:
    return {
        "max_files": limits.max_files,
        "max_manifest_bytes": limits.max_manifest_bytes,
        "max_traversal_entries": limits.max_traversal_entries,
        "max_preview_bytes": limits.max_preview_bytes,
    }


def _validated_parts(requested_path: str) -> tuple[str, ...]:
    if not requested_path or "\x00" in requested_path or "\\" in requested_path:
        raise ArtifactPathError("Invalid artifact path")
    pure = PurePosixPath(requested_path)
    if pure.is_absolute():
        raise ArtifactPathError("Absolute artifact paths are not allowed")
    parts = pure.parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise ArtifactPathError("Artifact traversal is not allowed")
    if any(_hidden_or_cache(part) for part in parts):
        raise ArtifactSecurityError("Hidden and cache paths are not available")

    if parts[0] == ATTACHMENTS_DIRNAME:
        if len(parts) < 2:
            raise ArtifactPathError("An attachment file path is required")
    elif len(parts) != 1:
        raise ArtifactPathError("Only direct companions and attachments are available")
    elif _reserved_direct(parts[0]):
        raise ArtifactSecurityError("Reserved task metadata is not an artifact")
    return parts


def resolve_artifact(plan_root: Path, task: Task, requested_path: str) -> Path:
    """Resolve one artifact without following a symlink or leaving its task."""
    if not _task_dir_is_secure(plan_root, task):
        raise ArtifactSecurityError("Owning task is unavailable")
    parts = _validated_parts(requested_path)
    candidate = task.dir_path.joinpath(*parts)

    current = task.dir_path
    for part in parts:
        current = current / part
        try:
            is_symlink = current.is_symlink()
        except OSError as exc:
            raise FileNotFoundError(requested_path) from exc
        if is_symlink:
            raise ArtifactSecurityError("Symlink artifacts are not available")

    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise FileNotFoundError(requested_path) from exc
    task_resolved = task.dir_path.resolve()
    root_resolved = plan_root.resolve()
    if not resolved.is_relative_to(task_resolved) or not resolved.is_relative_to(root_resolved):
        raise ArtifactSecurityError("Artifact escapes its owning task")
    try:
        info = resolved.stat()
    except OSError as exc:
        raise FileNotFoundError(requested_path) from exc
    if not stat.S_ISREG(info.st_mode):
        raise FileNotFoundError(requested_path)
    return resolved


def describe_resolved(path: Path, relative: str, limits: ArtifactLimits | None = None) -> ArtifactFile:
    """Describe an already-secure artifact for response headers and limits."""
    active_limits = limits or DEFAULT_ARTIFACT_LIMITS
    placement = "attachment" if relative.startswith(f"{ATTACHMENTS_DIRNAME}/") else (
        "direct" if path.suffix.lower() in DIRECT_SOURCE_SUFFIXES else "other"
    )
    item = _artifact_file(path, relative, placement, active_limits)
    if item is None:
        raise FileNotFoundError(relative)
    return item


def read_artifact_bytes(path: Path, *, max_bytes: int) -> bytes:
    """Read at most *max_bytes* without following a final-component symlink."""
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags)
    try:
        with os.fdopen(fd, "rb", closefd=False) as handle:
            raw = handle.read(max_bytes + 1)
    finally:
        os.close(fd)
    if len(raw) > max_bytes:
        raise ArtifactTooLargeError(f"Artifact exceeds {max_bytes} bytes")
    return raw


def artifact_owner_for_change(
    plan_root: Path,
    task_index: dict[str, Task],
    changed_path: str | Path,
) -> str | None:
    """Return the owning task path for a watcher event, or ``None`` if ignored."""
    root_abs = plan_root.absolute()
    path_abs = Path(changed_path).absolute()
    try:
        rel = path_abs.relative_to(root_abs)
    except ValueError:
        return None
    parts = rel.parts
    if not parts or any(_hidden_or_cache(part) for part in parts):
        return None

    if ATTACHMENTS_DIRNAME in parts:
        marker = parts.index(ATTACHMENTS_DIRNAME)
        if marker == len(parts) - 1:
            return None
        owner_path = PurePosixPath(*parts[:marker]).as_posix() if marker else ""
    else:
        if _reserved_direct(parts[-1]):
            return None
        owner_path = PurePosixPath(*parts[:-1]).as_posix() if len(parts) > 1 else ""

    owner = task_index.get(owner_path)
    if owner is None or not _task_dir_is_secure(plan_root, owner):
        return None

    current = root_abs
    for part in parts:
        current = current / part
        try:
            if current.exists() and current.is_symlink():
                return None
        except OSError:
            return None
    return owner_path


def build_standalone_artifacts(
    plan_root: Path,
    scoped_root: Task,
    *,
    repo_file_base: str = "",
    repo_root_prefix: str = "",
    image_artifact_keys: dict[tuple[str, str], str] | None = None,
    limits: ArtifactLimits | None = None,
) -> dict[str, object]:
    """Pack scoped manifests and bounded bytes for a single-file export."""
    active_limits = limits or DEFAULT_ARTIFACT_LIMITS
    image_keys = image_artifact_keys or {}
    manifests: dict[str, dict[str, object]] = {}
    contents: dict[str, dict[str, dict[str, str]]] = {}
    embedded_bytes = 0

    for task in [scoped_root, *collect_all_tasks(scoped_root)]:
        manifest = build_manifest(plan_root, task, limits=active_limits)
        manifests[task.path] = manifest
        task_contents: dict[str, dict[str, str]] = {}
        try:
            original_task_rel = task.dir_path.resolve().relative_to(plan_root.resolve()).as_posix()
        except (OSError, ValueError):
            original_task_rel = ""
        if original_task_rel == ".":
            original_task_rel = ""

        for entry in manifest["files"]:
            assert isinstance(entry, dict)
            relative = str(entry["path"])
            repo_parts = [p for p in (repo_root_prefix.strip("/"), original_task_rel, relative) if p]
            if repo_file_base:
                entry["repo_url"] = (
                    repo_file_base.rstrip("/") + "/" + quote("/".join(repo_parts), safe="/")
                )
            else:
                entry["repo_url"] = None

            image_key = image_keys.get((task.path, relative))
            if image_key is not None:
                entry["export"] = {
                    "status": "figure",
                    "image_key": image_key,
                    "bytes": int(entry["size"]),
                }
                continue

            size = int(entry["size"])
            if size > active_limits.max_export_file_bytes:
                entry["export"] = {
                    "status": "omitted",
                    "reason": "per-file-byte-limit",
                    "bytes": size,
                }
                continue
            if embedded_bytes + size > active_limits.max_export_total_bytes:
                entry["export"] = {
                    "status": "omitted",
                    "reason": "total-byte-limit",
                    "bytes": size,
                }
                continue

            try:
                resolved = resolve_artifact(plan_root, task, relative)
                raw = read_artifact_bytes(
                    resolved,
                    max_bytes=active_limits.max_export_file_bytes,
                )
            except (
                OSError,
                ArtifactPathError,
                ArtifactSecurityError,
                ArtifactTooLargeError,
            ):
                entry["export"] = {
                    "status": "omitted",
                    "reason": "unreadable",
                    "bytes": size,
                }
                continue
            embedded_bytes += len(raw)
            task_contents[relative] = {
                "encoding": "base64",
                "data": base64.b64encode(raw).decode("ascii"),
                "mime": str(entry["mime"]),
            }
            entry["export"] = {
                "status": "embedded",
                "bytes": len(raw),
            }

        if task_contents:
            contents[task.path] = task_contents

    return {
        "limits": {
            "max_files_per_task": active_limits.max_files,
            "max_manifest_bytes_per_task": active_limits.max_manifest_bytes,
            "max_traversal_entries_per_task": active_limits.max_traversal_entries,
            "max_preview_bytes_per_file": active_limits.max_preview_bytes,
            "max_export_bytes_per_file": active_limits.max_export_file_bytes,
            "max_export_bytes_total": active_limits.max_export_total_bytes,
        },
        "embedded_bytes": embedded_bytes,
        "manifests": manifests,
        "contents": contents,
    }
