#!/usr/bin/env python3
"""Shared internals for the task-tree skill.

Provides parsing, serialization, tree walking, frontier computation,
and status rollup for the directory-tree task tree.
"""

from __future__ import annotations

import heapq
import os
import re
import stat
import warnings
from dataclasses import dataclass, field
from pathlib import Path


FRONTMATTER_RE = re.compile(r"\A---\n(.*?\n)---\n(.*)", re.DOTALL)
BOM = "﻿"

VALID_STATUSES = ("not-started", "in-progress", "implemented", "revise", "approved", "archived", "postponed")
TASK_ROOT_DIRNAME = "superRA"
LEGACY_TASK_ROOT_DIRNAME = ".plan"
TASK_ROOT_DIRNAMES = (TASK_ROOT_DIRNAME, LEGACY_TASK_ROOT_DIRNAME)
ATTACHMENTS_DIRNAME = "attachments"


def is_opaque_task_path(path: Path, plan_root: Path) -> bool:
    """Return whether *path* lexically or canonically enters ``attachments/``."""
    try:
        lexical_relative = path.absolute().relative_to(plan_root.absolute())
    except ValueError:
        return False
    if ATTACHMENTS_DIRNAME in lexical_relative.parts:
        return True
    try:
        canonical_relative = path.resolve().relative_to(plan_root.resolve())
    except (OSError, ValueError):
        return False
    return ATTACHMENTS_DIRNAME in canonical_relative.parts


def has_symlink_task_component(path: Path, plan_root: Path) -> bool:
    """Return whether a task-root-relative component of *path* is a symlink."""
    try:
        relative = path.absolute().relative_to(plan_root.absolute())
    except ValueError:
        return False
    current = plan_root.absolute()
    for part in relative.parts:
        current /= part
        try:
            if current.is_symlink():
                return True
        except OSError:
            return True
    return False


def iter_child_task_dirs(directory: Path) -> list[Path]:
    """Return immediate structural child task directories in stable order."""
    try:
        if directory.is_symlink():
            return []
        children = directory.iterdir()
        return sorted(
            (
                child
                for child in children
                if (
                    child.name != ATTACHMENTS_DIRNAME
                    and not child.is_symlink()
                    and child.is_dir()
                    and not (child / "task.md").is_symlink()
                    and (child / "task.md").exists()
                )
            ),
            key=lambda child: child.name,
        )
    except OSError:
        return []


def iter_task_markdown_files(plan_root: Path) -> list[Path]:
    """Return structural ``task.md`` files without entering ancillary directories."""
    if plan_root.is_symlink():
        return []
    task_files: list[Path] = []
    pending = [plan_root]
    while pending:
        directory = pending.pop()
        task_md = directory / "task.md"
        if not task_md.is_symlink() and task_md.is_file():
            task_files.append(task_md)
        children = iter_child_task_dirs(directory)
        pending.extend(reversed(children))
    return task_files


def default_plan_root() -> Path:
    return Path(TASK_ROOT_DIRNAME)


def _has_child_task_dir(directory: Path) -> bool:
    """True if *directory* holds at least one immediate subdir with a ``task.md``."""
    return any(
        (child / "task.md").is_file()
        for child in iter_child_task_dirs(directory)
    )


def _is_task_root_dir(directory: Path) -> bool:
    """True if *directory* is a valid task root: a ``TASK_ROOT_DIRNAMES`` member
    that either holds an umbrella ``task.md`` (single tree) or at least one child
    task dir (a rootless forest). A forest needs no umbrella ``task.md``."""
    if directory.name not in TASK_ROOT_DIRNAMES:
        return False
    task_md = directory / "task.md"
    return (
        not directory.is_symlink()
        and (
            (not task_md.is_symlink() and task_md.is_file())
            or _has_child_task_dir(directory)
        )
    )


def autodetect_plan_root(start: Path | None = None) -> Path | None:
    """Walk up from *start* and find the active task root.

    Recognizes both layouts: an umbrella ``<root>/task.md`` (single tree) and a
    rootless forest (a ``superRA``/``.plan`` dir holding top-level task dirs with
    no umbrella ``task.md``). Prefers ``superRA/`` over the legacy ``.plan/`` when
    both are visible, and also works when called from inside a task root.
    """
    current = (start or Path.cwd()).resolve()
    while True:
        for dirname in TASK_ROOT_DIRNAMES:
            candidate = current / dirname
            if _is_task_root_dir(candidate):
                return candidate
        if _is_task_root_dir(current):
            return current
        if (current / "task.md").exists():
            parent = current.parent
            # Keep climbing toward a task-root-dir ancestor (e.g. a forest root
            # with no umbrella task.md); only stop here when there is none above.
            if not (parent / "task.md").exists() and parent.name not in TASK_ROOT_DIRNAMES:
                return current
        parent = current.parent
        if parent == current:
            return None
        current = parent


def resolve_plan_root_arg(plan_root: str | Path | None, start: Path | None = None) -> Path | None:
    """Resolve an optional CLI task-root argument, auto-detecting when omitted."""
    if plan_root is not None:
        return Path(plan_root)
    return autodetect_plan_root(start)


@dataclass
class Task:
    """A single task parsed from a task.md file."""

    path: str
    dir_path: Path
    title: str = ""
    status: str = "not-started"
    depends_on: list[str] = field(default_factory=list)
    body: str = ""
    objective: str = ""
    results: str = ""
    decisions: str = ""        # legacy; prefer revision_notes
    revision_notes: str = ""
    review_notes: str = ""
    children: list[Task] = field(default_factory=list)
    # Transient, never round-tripped to disk: set by the dashboard watcher when a
    # rebuild's re-parse of this task's task.md raises, so the node can render a
    # visible error state instead of silently reusing the last-good parse with no
    # signal.  Empty for every task built by the normal parse path.
    parse_error: str = ""

    @property
    def is_leaf(self) -> bool:
        return len(self.children) == 0

    @property
    def is_root(self) -> bool:
        return self.path == ""

    @property
    def slug(self) -> str:
        if not self.path:
            return ""
        return self.path.rsplit("/", 1)[-1]

    def effective_status(self) -> str:
        """Return status for leaves, rolled-up status for branches."""
        if self.is_leaf:
            return self.status
        return compute_status(self)


def _parse_yaml_value(raw: str) -> str | list[str]:
    """Parse a simple YAML value: scalar string, inline list, or multi-line list.

    ``~`` (YAML null) is normalized to an empty string at the scalar level so
    that ``title: ~`` yields ``Task.title == ""`` (falsy) rather than the
    literal string ``"~"`` (truthy) which would round-trip as a bogus value.
    """
    raw = raw.strip()
    if not raw or raw == "~":
        return ""

    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1]
        if not inner.strip():
            return []
        return [v.strip().strip("\"'") for v in _split_inline_list(inner)]

    return raw.strip("\"'")


def _split_inline_list(inner: str) -> list[str]:
    """Split an inline-list body on commas outside quotes.

    ``"a, b", c`` yields two items, not three: a comma inside a single- or
    double-quoted span is item content, not a separator.
    """
    items: list[str] = []
    buf: list[str] = []
    quote: str | None = None
    for ch in inner:
        if quote is not None:
            if ch == quote:
                quote = None
            buf.append(ch)
        elif ch in "\"'":
            quote = ch
            buf.append(ch)
        elif ch == ",":
            items.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    items.append("".join(buf))
    return items


def _parse_yaml_list_continuation(lines: list[str], start: int) -> tuple[list[str], int]:
    """Parse continuation lines of a YAML list (lines starting with '  - ')."""
    result = []
    i = start
    while i < len(lines):
        line = lines[i]
        if line.startswith("  - "):
            result.append(line[4:].strip().strip("\"'"))
            i += 1
        else:
            break
    return result, i


def _normalize_text(text: str) -> str:
    """Strip a UTF-8 BOM and normalize CRLF to LF so FRONTMATTER_RE matches."""
    if text.startswith(BOM):
        text = text[len(BOM):]
    return text.replace("\r\n", "\n").replace("\r", "\n")


def parse_frontmatter(text: str) -> tuple[dict[str, str | list[str]], str]:
    """Parse YAML frontmatter and body from a task.md file.

    Returns (frontmatter_dict, body_string).  Normalizes CRLF line endings
    and a leading BOM before matching so hand-edited files on Windows or
    editors that insert a BOM are handled correctly.
    """
    text = _normalize_text(text)
    match = FRONTMATTER_RE.match(text)
    if not match:
        if text.startswith("---"):
            warnings.warn(
                "task.md has a '---' line but could not be parsed as frontmatter "
                "(possible CRLF/BOM mismatch or malformed fence); "
                "treating as body-only.",
                stacklevel=3,
            )
        return {}, text

    fm_text = match.group(1)
    body = match.group(2)

    fm: dict[str, str | list[str]] = {}
    lines = fm_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or ":" not in line:
            i += 1
            continue

        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()

        if not value:
            list_items, i = _parse_yaml_list_continuation(lines, i + 1)
            if list_items:
                fm[key] = list_items
            else:
                fm[key] = ""
            continue

        fm[key] = _parse_yaml_value(value)
        i += 1

    return fm, body


_SECTION_ALIASES = {"Planner Guidance": "Details"}


def parse_body_sections(body: str) -> dict[str, str]:
    """Split a task body on ``## `` headers into {section_name: content} pairs.

    Fence-aware: a ``## `` line inside a ``` ``` ``` / ``~~~`` fenced code block is
    treated as body content, not a section header, so a header quoted inside an
    Objective/Results template does not start a spurious section (mirrors
    ``_has_nonempty_section``).

    Legacy heading names in ``_SECTION_ALIASES`` parse to their current name, so
    a task file written under the old vocabulary reads as the same section. When
    a legacy heading and its current name both appear, their bodies merge with a
    blank line between rather than the later one overwriting the earlier.
    """
    sections: dict[str, str] = {}
    current_name: str | None = None
    current_lines: list[str] = []
    in_fence = False

    def _store(name: str, lines: list[str]) -> None:
        # An alias collision (e.g. legacy ## Planner Guidance beside ## Details)
        # merges both bodies with a blank line between — never drop planner text.
        content = "\n".join(lines)
        existing = sections.get(name)
        if existing is None:
            sections[name] = content
        elif not existing.strip():
            sections[name] = content
        elif content.strip():
            sections[name] = existing.rstrip("\n") + "\n\n" + content.lstrip("\n")

    for line in body.split("\n"):
        if re.match(r"^[ \t]*(```|~~~)", line):
            in_fence = not in_fence
            if current_name is not None:
                current_lines.append(line)
            continue
        m = None if in_fence else re.match(r"^## (.+)$", line)
        if m:
            if current_name is not None:
                _store(current_name, current_lines)
            current_name = _SECTION_ALIASES.get(m.group(1), m.group(1))
            current_lines = []
        elif current_name is not None:
            current_lines.append(line)
    if current_name is not None:
        _store(current_name, current_lines)
    return sections


def _has_nonempty_section(body: str, section: str) -> bool:
    """True if ``body`` has a non-empty ``## <section>`` header outside fenced code.

    Delegates to ``parse_body_sections`` so header matching is identical in
    both places: exact ``^## (.+)$`` regex outside a fence, same fence toggle
    rules.  A section is non-empty when its parsed content has at least one
    non-blank character.
    """
    return bool(parse_body_sections(body).get(section, "").strip())


def _quote_yaml_scalar(key: str, value: str) -> str:
    """Quote a YAML scalar value if needed for safe serialization."""
    if key == "title":
        escaped = value.replace('"', '\\"')
        return f'"{escaped}"'
    return value


def serialize_frontmatter(fm: dict[str, str | list[str]]) -> str:
    """Serialize a frontmatter dict back to YAML text (without --- delimiters).

    The frontmatter field set is closed (see
    ``references/task-file-contract.md`` §Task Anatomy): only the
    canonical fields below are serialized, so unknown keys a hand edit adds
    are dropped on the next CLI mutation.
    """
    lines = []
    field_order = ["title", "status", "depends_on"]

    def _serialize_field(key: str, value: str | list[str]) -> None:
        if isinstance(value, list):
            if not value:
                lines.append(f"{key}: []")
            elif len(value) == 1:
                lines.append(f"{key}:")
                lines.append(f"  - {value[0]}")
            else:
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
        else:
            lines.append(f"{key}: {_quote_yaml_scalar(key, value)}")

    for key in field_order:
        if key not in fm:
            continue
        _serialize_field(key, fm[key])

    return "\n".join(lines) + "\n"


def _to_list(val: str | list[str]) -> list[str]:
    if isinstance(val, list):
        return val
    if not val or val == "~":
        return []
    return [val]


def parse_task(task_md_path: Path, plan_root: Path | None = None) -> Task:
    """Parse a task.md file into a Task object.

    ``path`` is always relative to the *resolved task root*. Pass ``plan_root``
    when the caller already resolved it (every tree walk and CLI command does) so
    the path is computed as ``task_dir.relative_to(plan_root)`` — never re-derived
    by descending the directory tree. When ``plan_root`` is omitted (a bare-path
    parse), it is inferred via ``_find_plan_root``, which returns the nearest
    task-root directory so a standalone parse agrees with a known-root walk.
    """
    task_dir = task_md_path.parent
    root = plan_root if plan_root is not None else _find_plan_root(task_dir)
    path = ""
    if root is not None:
        if task_md_path.is_symlink() or has_symlink_task_component(task_dir, root):
            raise ValueError(
                f"Task path {task_md_path} contains a symlink; "
                "refusing to parse external task content"
            )
        try:
            rel = task_dir.resolve().relative_to(root.resolve())
        except ValueError:
            raise ValueError(
                f"Task dir {task_dir} is outside the supplied plan root {root}; "
                f"refusing to parse it as the root task"
            ) from None
        if ATTACHMENTS_DIRNAME in rel.parts:
            raise ValueError(
                f"Task dir {task_dir} is inside reserved {ATTACHMENTS_DIRNAME}/; "
                "refusing to parse asset content as a task"
            )
        path = str(rel) if str(rel) != "." else ""

    text = task_md_path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)

    title = str(fm.get("title", ""))
    status = str(fm.get("status", "not-started"))

    # Tolerate unknown status values: keep the raw string so readers (dashboard,
    # query, read) degrade gracefully instead of crashing the whole tree walk on
    # one malformed file. `task_check` is the strict validator that reports an
    # invalid status as a finding; downstream rollup/icon lookups already fall
    # back safely on unrecognized values.
    if status not in VALID_STATUSES:
        # Lazy import: _task_validate imports from this module at top level,
        # so the message source is pulled in at call time to avoid a cycle.
        from _task_validate import invalid_status_message
        warnings.warn(
            f"{task_md_path}: {invalid_status_message(status)}. "
            f"Treating as-is; run `superra task check` to fix.",
            stacklevel=2,
        )
    # Silently ignore review_status / integration_status if present in old files

    sections = parse_body_sections(body)

    return Task(
        path=path,
        dir_path=task_md_path.parent,
        title=title,
        status=status,
        depends_on=_to_list(fm.get("depends_on", [])),
        body=body,
        objective=sections.get("Objective", ""),
        results=sections.get("Results", ""),
        decisions=sections.get("Decisions", ""),
        revision_notes=sections.get("Revision Notes", ""),
        review_notes=sections.get("Review Notes", ""),
    )


def write_task(task: Task) -> None:
    """Write a Task back to its task.md file, preserving body content.

    The write is atomic (temp file + ``os.replace``) so a concurrent reader —
    e.g. the live dashboard's file watcher — never sees a half-written file,
    and an interrupted multi-file update never leaves a truncated task.md.
    """
    fm: dict[str, str | list[str]] = {}
    if task.title:
        fm["title"] = task.title
    fm["status"] = task.status
    if task.depends_on:
        fm["depends_on"] = task.depends_on
    else:
        fm["depends_on"] = []

    fm_text = serialize_frontmatter(fm)
    content = f"---\n{fm_text}---\n{task.body}"

    task_md = task.dir_path / "task.md"
    tmp = task_md.with_suffix(".md.tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, task_md)


def cascade_depends_on_rename(parent_dir: Path, old_slug: str, new_slug: str) -> list[str]:
    """Re-point every sibling `depends_on: old_slug` to `new_slug` in ``parent_dir``.

    This is the lossless same-parent rename cascade shared by ``task_rename.py``
    (explicit CLI) and ``task_hook.py`` (post-hoc raw ``mv``). It rewrites only
    the ``depends_on`` YAML metadata — never task content — and only for siblings
    in the directory that holds both the old and new slug, which is what makes it
    safe to auto-apply: the rename is fully expressible in the sibling-only model.

    Returns the slugs of the siblings whose ``depends_on`` was updated.
    """
    updated: list[str] = []
    siblings = [
        directory
        for directory in iter_child_task_dirs(parent_dir)
        if directory.name != new_slug
    ]
    for sibling_dir in siblings:
        task = parse_task(sibling_dir / "task.md")
        if old_slug in task.depends_on:
            task.depends_on = [new_slug if d == old_slug else d for d in task.depends_on]
            write_task(task)
            updated.append(sibling_dir.name)
    return updated


_MARKDOWN_LINK_RE = re.compile(r"(!?\[[^\]\n]*\]\()(<[^>\n]+>|[^)\s\n]+)(\))")
_FENCE_RE = re.compile(r"^\s*(```|~~~)")


def _is_local_markdown_target(target: str) -> bool:
    if not target or target.startswith(("#", "/")):
        return False
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
        return False
    return True


def _split_link_target(target: str) -> tuple[str, str, bool]:
    angle_wrapped = target.startswith("<") and target.endswith(">")
    inner = target[1:-1] if angle_wrapped else target
    split_at = len(inner)
    for marker in ("#", "?"):
        pos = inner.find(marker)
        if pos != -1:
            split_at = min(split_at, pos)
    return inner[:split_at], inner[split_at:], angle_wrapped


def _rewrite_relative_links(
    text: str,
    old_md: Path,
    new_md: Path,
    from_dir: Path,
    to_dir: Path,
    *,
    only_into_subtree: bool = False,
) -> str:
    """Rewrite relative Markdown links in ``text`` so they survive a move.

    ``old_md``/``new_md`` are the file's location before/after the move. For a
    moved file (it changes location) every local link is re-expressed from
    ``new_md``. For a file that stays put, ``only_into_subtree`` keeps the rewrite
    surgical: only links resolving into the moved subtree are re-pointed; every
    other link is left byte-for-byte. Path math is lexical (``resolve()`` does not
    require existence), so this works whether computed before or after the rename.
    """
    in_fence = False
    from_dir_resolved = from_dir.resolve()

    def replace(match: re.Match[str]) -> str:
        target = match.group(2)
        path_part, suffix, angle_wrapped = _split_link_target(target)
        if not _is_local_markdown_target(path_part):
            return match.group(0)

        old_target = (old_md.parent / path_part).resolve()
        try:
            within = old_target.relative_to(from_dir_resolved)
        except ValueError:
            if only_into_subtree:
                return match.group(0)
            target_after_move = old_target
        else:
            target_after_move = to_dir / within

        rel = os.path.relpath(target_after_move, new_md.parent)
        rel = Path(rel).as_posix()
        if rel == ".":
            rel = ""
        new_target = f"{rel}{suffix}"
        if angle_wrapped:
            new_target = f"<{new_target}>"
        return f"{match.group(1)}{new_target}{match.group(3)}"

    rewritten_lines: list[str] = []
    for line in text.splitlines(keepends=True):
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            rewritten_lines.append(line)
        elif in_fence:
            rewritten_lines.append(line)
        else:
            rewritten_lines.append(_MARKDOWN_LINK_RE.sub(replace, line))
    return "".join(rewritten_lines)


def _contained_regular_relative(path: Path, plan_root: Path) -> Path:
    """Return a safe root-relative path or raise without following symlinks."""
    root = plan_root.resolve(strict=True)
    candidate = path.absolute()
    try:
        relative = candidate.relative_to(root)
    except ValueError:
        raise ValueError(f"Markdown rewrite target escapes task root: {path}") from None
    if not relative.parts:
        raise ValueError(f"Markdown rewrite target is not a file: {path}")

    current = root
    for index, part in enumerate(relative.parts):
        current /= part
        try:
            info = current.lstat()
        except OSError as exc:
            raise ValueError(f"Markdown rewrite target is unavailable: {path}") from exc
        if stat.S_ISLNK(info.st_mode):
            raise ValueError(
                f"Markdown rewrite target contains a symlink component: {path}"
            )
        if index < len(relative.parts) - 1 and not stat.S_ISDIR(info.st_mode):
            raise ValueError(
                f"Markdown rewrite target has a non-directory component: {path}"
            )
    if not stat.S_ISREG(info.st_mode):
        raise ValueError(f"Markdown rewrite target is not a regular file: {path}")
    return relative


def _open_contained_regular(
    path: Path, plan_root: Path, flags: int
) -> int:
    """Open a contained regular file without following any path symlink."""
    root = plan_root.resolve(strict=True)
    relative = _contained_regular_relative(path, root)
    if (
        flags & os.O_ACCMODE
        and not path.lstat().st_mode
        & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
    ):
        raise PermissionError(f"Markdown rewrite target is read-only: {path}")
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    no_follow = getattr(os, "O_NOFOLLOW", 0)
    directory_fd = os.open(root, directory_flags | no_follow)
    try:
        for part in relative.parts[:-1]:
            child_fd = os.open(
                part,
                directory_flags | no_follow,
                dir_fd=directory_fd,
            )
            os.close(directory_fd)
            directory_fd = child_fd
        file_fd = os.open(
            relative.parts[-1],
            flags | no_follow,
            dir_fd=directory_fd,
        )
    finally:
        os.close(directory_fd)

    if not stat.S_ISREG(os.fstat(file_fd).st_mode):
        os.close(file_fd)
        raise ValueError(f"Markdown rewrite target is not a regular file: {path}")
    return file_fd


def _read_contained_bytes(path: Path, plan_root: Path) -> bytes:
    fd = _open_contained_regular(path, plan_root, os.O_RDONLY)
    with os.fdopen(fd, "rb") as handle:
        return handle.read()


def _read_contained_markdown(path: Path, plan_root: Path) -> str:
    return _read_contained_bytes(path, plan_root).decode("utf-8")


def _write_fd_bytes(fd: int, payload: bytes) -> None:
    """Replace an opened regular file's bytes, retaining its descriptor."""
    os.lseek(fd, 0, os.SEEK_SET)
    os.ftruncate(fd, 0)
    remaining = memoryview(payload)
    while remaining:
        written = os.write(fd, remaining)
        if written <= 0:
            raise OSError("short write while applying Markdown rewrite")
        remaining = remaining[written:]


def _close_rewrite_fd(fd: int) -> None:
    """Close one rewrite descriptor (seamed for failure-order testing)."""
    os.close(fd)


def _close_rewrite_fds(fds: list[int]) -> list[tuple[int, Exception]]:
    """Attempt every close in order and return failures without short-circuiting."""
    failures: list[tuple[int, Exception]] = []
    for fd in fds:
        try:
            _close_rewrite_fd(fd)
        except Exception as exc:
            failures.append((fd, exc))
    return failures


def _restore_rewrite_paths(
    plan_root: Path, prepared: list[tuple[Path, bytes, bytes]]
) -> list[str]:
    """Best-effort restoration through fresh descriptors after finalization fails."""
    restore_fds: list[tuple[int, Path, bytes]] = []
    errors: list[str] = []
    for path, _new_bytes, original_bytes in prepared:
        try:
            fd = _open_contained_regular(path, plan_root, os.O_WRONLY)
        except Exception as exc:
            errors.append(f"reopen {path}: {exc}")
            continue
        restore_fds.append((fd, path, original_bytes))

    for fd, path, original_bytes in restore_fds:
        try:
            _write_fd_bytes(fd, original_bytes)
        except Exception as exc:
            errors.append(f"restore {path}: {exc}")

    close_failures = _close_rewrite_fds([fd for fd, _path, _bytes in restore_fds])
    if close_failures:
        retry_failures = _close_rewrite_fds([fd for fd, _exc in close_failures])
        errors.extend(f"close restored fd {fd}: {exc}" for fd, exc in close_failures)
        errors.extend(f"retry restored fd {fd}: {exc}" for fd, exc in retry_failures)
    return errors


def _iter_contained_markdown(root: Path, plan_root: Path):
    """Yield regular Markdown files without entering symlinked directories."""
    task_root = plan_root.resolve(strict=True)
    scan_root = root.absolute()
    try:
        scan_root.relative_to(task_root)
    except ValueError:
        return
    if has_symlink_task_component(scan_root, task_root) or not scan_root.is_dir():
        return

    for directory, dirnames, filenames in os.walk(scan_root, followlinks=False):
        current = Path(directory)
        dirnames[:] = sorted(
            name for name in dirnames if not (current / name).is_symlink()
        )
        for name in sorted(filenames):
            candidate = current / name
            if candidate.suffix.lower() != ".md":
                continue
            try:
                _contained_regular_relative(candidate, task_root)
            except ValueError:
                continue
            yield candidate


def compute_move_link_rewrites(
    plan_root: Path, from_dir: Path, to_dir: Path, *, moved_root: Path
) -> dict[Path, str]:
    """Compute every relative-link rewrite a move from ``from_dir`` to ``to_dir``
    needs so links keep resolving. Shared by the ``task move`` CLI and the
    post-move hook; the only difference is where the moved subtree is readable —
    ``moved_root`` is ``from_dir`` when computed before the rename (CLI) and
    ``to_dir`` when computed after it (hook).

    Returns ``{post_move_path: new_text}``: the moved subtree's own files (keyed by
    their destination paths, outbound links re-expressed from the new depth) plus
    every other file in ``plan_root`` whose links point into the moved subtree
    (keyed by their unchanged paths). Files whose links are unaffected are omitted.
    """
    plan_root = plan_root.resolve(strict=True)
    rewrites: dict[Path, str] = {}
    from_dir_resolved = from_dir.resolve()
    to_dir_resolved = to_dir.resolve()

    for src_md in _iter_contained_markdown(moved_root, plan_root):
        rel = src_md.relative_to(moved_root)
        original = _read_contained_markdown(src_md, plan_root)
        rewritten = _rewrite_relative_links(
            original, from_dir / rel, to_dir / rel, from_dir, to_dir
        )
        if rewritten != original:
            rewrites[to_dir / rel] = rewritten

    for md in _iter_contained_markdown(plan_root, plan_root):
        md_resolved = md.resolve()
        in_subtree = False
        for boundary in (from_dir_resolved, to_dir_resolved):
            try:
                md_resolved.relative_to(boundary)
            except ValueError:
                continue
            in_subtree = True
            break
        if in_subtree:
            continue  # part of the moved subtree (pre- or post-move) — handled above
        original = _read_contained_markdown(md, plan_root)
        rewritten = _rewrite_relative_links(
            original, md, md, from_dir, to_dir, only_into_subtree=True
        )
        if rewritten != original:
            rewrites[md] = rewritten
    return rewrites


def apply_move_link_rewrites(
    plan_root: Path, rewrites: dict[Path, str]
) -> None:
    """Apply a rewrite queue transactionally through contained regular files."""
    ordered = sorted(rewrites.items(), key=lambda item: str(item[0]))
    prepared: list[tuple[Path, bytes, bytes]] = []
    for path, content in ordered:
        _contained_regular_relative(path, plan_root)
        prepared.append(
            (path, content.encode("utf-8"), _read_contained_bytes(path, plan_root))
        )

    write_fds: list[int] = []
    touched: list[tuple[int, Path, bytes]] = []
    primary_error: Exception | None = None
    rollback_errors: list[str] = []

    try:
        # Open every destination before changing bytes. Permission/path failures
        # therefore leave the whole queue untouched.
        for path, _new_bytes, _original_bytes in prepared:
            write_fds.append(_open_contained_regular(path, plan_root, os.O_WRONLY))
        for fd, (path, new_bytes, original_bytes) in zip(write_fds, prepared):
            touched.append((fd, path, original_bytes))
            _write_fd_bytes(fd, new_bytes)
    except Exception as exc:
        primary_error = exc
        for fd, path, original_bytes in reversed(touched):
            try:
                _write_fd_bytes(fd, original_bytes)
            except Exception as rollback_exc:
                rollback_errors.append(f"restore {path}: {rollback_exc}")

    close_failures = _close_rewrite_fds(write_fds)
    if close_failures and touched:
        # A close error means the new bytes were never fully committed. Some
        # original descriptors may already be closed, so restore every path
        # through a fresh no-follow descriptor before reporting the failure.
        rollback_errors.extend(_restore_rewrite_paths(plan_root, prepared))

    # A failed close may have left its descriptor open. Retry only after byte
    # restoration, while still attempting every failed descriptor in order.
    retry_failures = _close_rewrite_fds([fd for fd, _exc in close_failures])

    if primary_error is not None or close_failures or rollback_errors:
        details: list[str] = []
        if primary_error is not None:
            details.append(str(primary_error))
        details.extend(f"close fd {fd}: {exc}" for fd, exc in close_failures)
        details.extend(rollback_errors)
        details.extend(f"retry close fd {fd}: {exc}" for fd, exc in retry_failures)
        raise OSError("Markdown rewrite transaction failed: " + "; ".join(details))


def _find_plan_root(task_dir: Path) -> Path | None:
    """Walk up from a task directory to find the resolved task root.

    The task root is the nearest ancestor (or ``task_dir`` itself) whose basename
    is a ``TASK_ROOT_DIRNAMES`` member (``superRA`` / ``.plan``). For such a root a
    bare-path parse agrees with a tree walk rooted at that same ``TASK_ROOT_DIRNAMES``
    directory — including a forest root with no umbrella ``task.md``. It does **not**
    agree with a walk rooted at a *nested* ``--root`` whose basename is not a
    ``TASK_ROOT_DIRNAMES`` member (e.g. ``--root superRA/01-intermediary-cost``): a
    bare parse climbs past it to ``superRA/`` and keeps the extra prefix, while the
    known-root walk drops it. That divergence is harmless today because every
    path-sensitive consumer threads ``plan_root`` into ``parse_task``/``walk_plan``
    rather than relying on a bare parse.

    Falls back to the legacy heuristic (topmost task-bearing ancestor) only when
    the directory is not nested under a task-root dir at all, so trees built
    outside a ``superRA``/``.plan`` container (e.g. ad-hoc fixtures) still resolve.
    """
    current = task_dir
    while True:
        if current.name in TASK_ROOT_DIRNAMES:
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent

    # No task-root container ancestor: fall back to the topmost task-bearing dir.
    current = task_dir
    while True:
        parent = current.parent
        if (parent / "task.md").exists() and parent != current:
            current = parent
        else:
            return current


SYNTHETIC_ROOT_TITLE = "(no root task.md)"


def walk_plan(plan_root: Path) -> Task:
    """Recursively walk a plan directory and build the task tree.

    Returns the root Task with children populated. A rootless forest (no
    umbrella ``task.md``) gets a synthetic placeholder root carrying
    ``SYNTHETIC_ROOT_TITLE``.
    """
    root_task_md = plan_root / "task.md"
    if not root_task_md.is_symlink() and root_task_md.exists():
        root = parse_task(root_task_md, plan_root)
    else:
        root = Task(path="", dir_path=plan_root, title=SYNTHETIC_ROOT_TITLE)

    root.children = _walk_children(plan_root, plan_root)
    return root


def _topological_sort(tasks: list[Task]) -> list[Task]:
    """Sort tasks topologically using Kahn's algorithm on depends_on edges.

    Tasks with no dependencies come first; dependents come after their
    dependencies. Ties are broken alphabetically by slug.
    If a cycle is detected or a dependency is missing, falls back to
    alphabetical order for the affected tasks.
    """
    slug_to_task: dict[str, Task] = {t.slug: t for t in tasks}

    in_degree: dict[str, int] = {t.slug: 0 for t in tasks}
    dependents: dict[str, list[str]] = {t.slug: [] for t in tasks}

    for task in tasks:
        for dep in task.depends_on:
            if dep in slug_to_task:
                in_degree[task.slug] += 1
                dependents[dep].append(task.slug)

    ready: list[str] = []
    for slug, deg in in_degree.items():
        if deg == 0:
            heapq.heappush(ready, slug)

    result: list[Task] = []
    while ready:
        slug = heapq.heappop(ready)
        result.append(slug_to_task[slug])
        for dependent_slug in sorted(dependents[slug]):
            in_degree[dependent_slug] -= 1
            if in_degree[dependent_slug] == 0:
                heapq.heappush(ready, dependent_slug)

    # If cycle detected, append remaining tasks alphabetically
    if len(result) < len(tasks):
        remaining = sorted(
            [t for t in tasks if t.slug not in {r.slug for r in result}],
            key=lambda t: t.slug,
        )
        result.extend(remaining)

    return result


def _walk_children(directory: Path, plan_root: Path) -> list[Task]:
    """Find and parse child task directories, sorted topologically by depends_on.

    Per-file errors (``OSError``, ``UnicodeDecodeError``) are caught, warned,
    and skipped so one unreadable or undecodable ``task.md`` does not abort the
    whole walk for all readers (dashboard, ``task query``, ``task read``).
    Mirrors the leniency design used for unknown status values.
    """
    subdirs = iter_child_task_dirs(directory)
    parsed: list[Task] = []
    for subdir in subdirs:
        try:
            child = parse_task(subdir / "task.md", plan_root)
        except (OSError, UnicodeDecodeError) as exc:
            warnings.warn(
                f"Skipping {subdir / 'task.md'}: {exc}; "
                f"run `superra task check` to diagnose.",
                stacklevel=2,
            )
            continue
        child.children = _walk_children(subdir, plan_root)
        parsed.append(child)

    return _topological_sort(parsed)


def strip_root_prefix(plan_root: Path, task_path: str) -> str:
    """Drop a redundant leading task-root segment from a task path.

    Task paths are relative to the task root and omit the root prefix (e.g.
    ``task-tree/planning-redesign``). As an ergonomic tolerance, a leading
    segment equal to the task-root basename (``superRA``, or legacy ``.plan``)
    is stripped, so the fully-prefixed form an agent naturally has in hand
    (``superRA/task-tree/planning-redesign``) collapses to the canonical
    task-root-relative form instead of doubling to ``superRA/superRA/...``.

    Returns the canonical task-root-relative path string. Pure string op: no
    filesystem access, no escape check — callers that join the result still
    enforce containment via :func:`resolve_path`.
    """
    if not task_path:
        return task_path
    segments = task_path.strip("/").split("/")
    if len(segments) > 1 and segments[0] == plan_root.name and segments[0] in TASK_ROOT_DIRNAMES:
        return "/".join(segments[1:])
    return task_path


def resolve_path(plan_root: Path, task_path: str) -> Path:
    """Resolve a task ID (relative path) to its directory on disk.

    Tolerates a redundant leading task-root segment via
    :func:`strip_root_prefix` before joining, so the fully-prefixed form
    (``superRA/task-tree/planning-redesign``) resolves to the same task as the
    canonical task-root-relative form.

    Raises ValueError if the resolved path escapes the plan root.
    """
    if not task_path:
        return plan_root
    task_path = strip_root_prefix(plan_root, task_path)
    requested = Path(task_path)
    if requested.is_absolute() or ".." in requested.parts:
        raise ValueError(
            f"Task path {task_path!r} escapes plan root {plan_root}"
        )
    if ATTACHMENTS_DIRNAME in requested.parts:
        raise ValueError(
            f"Task path {task_path!r} enters reserved {ATTACHMENTS_DIRNAME}/"
        )
    candidate = plan_root / requested
    if has_symlink_task_component(candidate, plan_root):
        raise ValueError(f"Task path {task_path!r} contains a symlink component")
    resolved = candidate.resolve()
    root_resolved = plan_root.resolve()
    try:
        canonical_relative = resolved.relative_to(root_resolved)
    except ValueError:
        raise ValueError(
            f"Task path {task_path!r} escapes plan root {plan_root}"
        ) from None
    if ATTACHMENTS_DIRNAME in canonical_relative.parts:
        raise ValueError(
            f"Task path {task_path!r} resolves inside reserved "
            f"{ATTACHMENTS_DIRNAME}/"
        )
    return resolved


def compute_status(task: Task) -> str:
    """Compute rolled-up status for a branch task from its children.

    Parked children (archived and postponed) are excluded from rollup.
    Rules checked in order:
    1. No active children remain (all parked) -> postponed if any child is
       postponed, else archived (a deferred child dominates an abandoned one)
    2. All children approved -> approved
    3. Any child revise -> revise
    4. All children implemented or approved -> implemented (the subtree's
       work product exists; review is still open)
    5. Any child in-progress or implemented -> in-progress
    6. Any child approved (but not all) -> in-progress
    7. Otherwise -> not-started
    """
    if task.is_leaf:
        return task.status

    all_statuses = [c.effective_status() for c in task.children]
    child_statuses = [s for s in all_statuses if s not in ("archived", "postponed")]

    if not child_statuses:
        return "postponed" if any(s == "postponed" for s in all_statuses) else "archived"

    if all(s == "approved" for s in child_statuses):
        return "approved"
    if any(s == "revise" for s in child_statuses):
        return "revise"
    if all(s in ("implemented", "approved") for s in child_statuses):
        return "implemented"
    if any(s in ("in-progress", "implemented") for s in child_statuses):
        return "in-progress"
    if any(s == "approved" for s in child_statuses):
        return "in-progress"
    return "not-started"


def propagate_parent_status(
    plan_root: Path, task_path: str, feedback: list[str] | None = None
) -> int:
    """Walk from task_path up to the root, recomputing parent statuses.

    For each ancestor that is not a leaf, computes rolled-up status from
    children via compute_status() and writes back if changed. An ``approved``
    rollup is never written onto a parent whose ``## Review Notes`` still carry
    ``[BLOCKING]``: the current status is held and a warning is appended to
    ``feedback`` when a list is passed.

    Returns the number of ancestor tasks updated.
    """
    updated = 0
    # Walk up from task_path to root
    parts = task_path.strip("/").split("/") if task_path else []

    # Build list of ancestor paths from immediate parent to root
    ancestors: list[str] = []
    for i in range(len(parts) - 1, -1, -1):
        ancestors.append("/".join(parts[:i]) if i > 0 else "")

    for ancestor_path in ancestors:
        ancestor_dir = plan_root / ancestor_path if ancestor_path else plan_root
        task_md = ancestor_dir / "task.md"
        if not task_md.exists():
            continue

        # Re-walk this subtree to get current children
        ancestor_task = parse_task(task_md, plan_root)
        ancestor_task.children = _walk_children(ancestor_dir, plan_root)

        if ancestor_task.is_leaf:
            continue

        changed = False
        rolled_status = compute_status(ancestor_task)

        if rolled_status == "approved" and ancestor_task.status != "approved":
            from _task_validate import _review_notes_block_approval

            if _review_notes_block_approval(rolled_status, ancestor_task.review_notes):
                if feedback is not None:
                    prefix = ancestor_task.path if ancestor_task.path else "(root)"
                    feedback.append(
                        f"{prefix}: children approved but parent Review Notes still "
                        "carry [BLOCKING]; clear or re-review"
                    )
                continue

        if ancestor_task.status != rolled_status:
            ancestor_task.status = rolled_status
            changed = True

        if changed:
            write_task(ancestor_task)
            updated += 1

    return updated


def compute_frontier(root: Task) -> list[Task]:
    """Compute the dispatch frontier: leaf tasks that have actionable work now.

    A leaf task is on the frontier when:
    1. Its own status is actionable — 'not-started' or 'in-progress' (ready to
       implement), 'implemented' (approval decision open), or 'revise' (ready
       to fix).
       Each entry carries its status, so a caller reads the next action from it.
    2. All sibling dependencies have effective_status 'approved', 'archived',
       'implemented', or 'revise' — i.e. the dependency's work product exists,
       even if review or a fix round is still open. Only 'not-started',
       'in-progress', and 'postponed' dependencies block dependents.
    3. All ancestor tasks' sibling dependencies are met (recursively)
    """
    frontier: list[Task] = []
    _collect_frontier(root, frontier, ancestors_ready=True)
    return frontier


# Leaf statuses that represent actionable, not-yet-done work. 'approved' is done;
# 'archived'/'postponed' are parked. The caller distinguishes implement vs review
# vs fix work by reading each task's status.
_ACTIONABLE_STATUSES = ("not-started", "in-progress", "implemented", "revise")


def _collect_frontier(task: Task, frontier: list[Task], ancestors_ready: bool) -> None:
    """Recursively collect frontier tasks."""
    if task.is_leaf:
        if task.is_root and task.title == SYNTHETIC_ROOT_TITLE:
            return  # synthetic placeholder for a rootless forest, not real work
        if task.status in ("archived", "postponed"):
            return  # parked tasks never appear on the frontier
        if ancestors_ready and task.status in _ACTIONABLE_STATUSES:
            frontier.append(task)
        return

    sibling_map = {c.slug: c for c in task.children}

    for child in task.children:
        # Skip parked (archived/postponed) children entirely
        if child.effective_status() in ("archived", "postponed"):
            continue

        deps_met = True
        for dep in child.depends_on:
            dep_task = sibling_map.get(dep)
            if dep_task is None:
                warnings.warn(
                    f"Task {child.path!r} depends on {dep!r} which does not "
                    f"match any sibling task",
                    stacklevel=2,
                )
                deps_met = False
                break
            # A dependency is satisfied once its work product exists —
            # 'implemented' and 'revise' count, so dependents can proceed while
            # review or a deferred fix round is open. Postponed dependencies
            # are NOT satisfied — postponing a task deliberately blocks its
            # dependents until it is resumed.
            dep_status = dep_task.effective_status()
            if dep_status not in ("approved", "archived", "implemented", "revise"):
                deps_met = False
                break

        child_ready = ancestors_ready and deps_met
        _collect_frontier(child, frontier, ancestors_ready=child_ready)


def collect_all_tasks(root: Task) -> list[Task]:
    """Flatten the task tree into a list (depth-first, excluding root)."""
    result: list[Task] = []
    _collect_all(root, result)
    return result


def _collect_all(task: Task, result: list[Task]) -> None:
    for child in task.children:
        result.append(child)
        _collect_all(child, result)
