#!/usr/bin/env python3
"""Shared internals for the task-tree skill.

Provides parsing, serialization, tree walking, frontier computation,
and status rollup for the directory-tree task tree.
"""

from __future__ import annotations

import heapq
import re
import warnings
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


FRONTMATTER_RE = re.compile(r"\A---\n(.*?\n)---\n(.*)", re.DOTALL)
BOM = "﻿"

VALID_STATUSES = ("not-started", "in-progress", "implemented", "revise", "approved", "archived", "postponed")
TASK_ROOT_DIRNAME = "superRA"
LEGACY_TASK_ROOT_DIRNAME = ".plan"
TASK_ROOT_DIRNAMES = (TASK_ROOT_DIRNAME, LEGACY_TASK_ROOT_DIRNAME)


def default_plan_root() -> Path:
    return Path(TASK_ROOT_DIRNAME)


def _has_child_task_dir(directory: Path) -> bool:
    """True if *directory* holds at least one immediate subdir with a ``task.md``."""
    try:
        # Materialize inside the guard: `iterdir()` is lazy, so a missing/racing
        # directory raises FileNotFoundError (an OSError) only on consumption,
        # which would escape a bare `try` wrapping just the `iterdir()` call.
        children = list(directory.iterdir())
    except OSError:
        return False
    return any(d.is_dir() and (d / "task.md").is_file() for d in children)


def _is_task_root_dir(directory: Path) -> bool:
    """True if *directory* is a valid task root: a ``TASK_ROOT_DIRNAMES`` member
    that either holds an umbrella ``task.md`` (single tree) or at least one child
    task dir (a rootless forest). A forest needs no umbrella ``task.md``."""
    if directory.name not in TASK_ROOT_DIRNAMES:
        return False
    return (directory / "task.md").is_file() or _has_child_task_dir(directory)


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
    tags: list[str] = field(default_factory=list)
    script: str = ""
    input: list[str] = field(default_factory=list)
    output: list[str] = field(default_factory=list)
    created: str = ""
    body: str = ""
    objective: str = ""
    results: str = ""
    decisions: str = ""        # legacy; prefer revision_notes
    revision_notes: str = ""
    review_notes: str = ""
    children: list[Task] = field(default_factory=list)

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
    that ``script: ~`` yields ``Task.script == ""`` (falsy) rather than the
    literal string ``"~"`` (truthy) which would round-trip as a bogus value.
    """
    raw = raw.strip()
    if not raw or raw == "~":
        return ""

    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1]
        if not inner.strip():
            return []
        return [v.strip().strip("\"'") for v in inner.split(",")]

    return raw.strip("\"'")


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


def parse_body_sections(body: str) -> dict[str, str]:
    """Split a task body on ``## `` headers into {section_name: content} pairs.

    Fence-aware: a ``## `` line inside a ``` ``` ``` / ``~~~`` fenced code block is
    treated as body content, not a section header, so a header quoted inside an
    Objective/Results template does not start a spurious section (mirrors
    ``_has_nonempty_section``).
    """
    sections: dict[str, str] = {}
    current_name: str | None = None
    current_lines: list[str] = []
    in_fence = False
    for line in body.split("\n"):
        if re.match(r"^[ \t]*(```|~~~)", line):
            in_fence = not in_fence
            if current_name is not None:
                current_lines.append(line)
            continue
        m = None if in_fence else re.match(r"^## (.+)$", line)
        if m:
            if current_name is not None:
                sections[current_name] = "\n".join(current_lines)
            current_name = m.group(1)
            current_lines = []
        elif current_name is not None:
            current_lines.append(line)
    if current_name is not None:
        sections[current_name] = "\n".join(current_lines)
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
    """Serialize a frontmatter dict back to YAML text (without --- delimiters)."""
    lines = []
    field_order = [
        "title", "status",
        "depends_on", "tags", "script", "input", "output",
        "created",
    ]

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

    for key, value in fm.items():
        if key not in field_order:
            _serialize_field(key, value)

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
    text = task_md_path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)

    task_dir = task_md_path.parent
    root = plan_root if plan_root is not None else _find_plan_root(task_dir)
    path = ""
    if root is not None:
        try:
            rel = task_dir.resolve().relative_to(root.resolve())
        except ValueError:
            rel = Path(".")
        path = str(rel) if str(rel) != "." else ""

    title = str(fm.get("title", ""))
    status = str(fm.get("status", "not-started"))

    # Tolerate unknown status values: keep the raw string so readers (dashboard,
    # query, read) degrade gracefully instead of crashing the whole tree walk on
    # one malformed file. `task_check` is the strict validator that reports an
    # invalid status as a finding; downstream rollup/icon lookups already fall
    # back safely on unrecognized values.
    if status not in VALID_STATUSES:
        warnings.warn(
            f"Invalid status {status!r} in {task_md_path}; "
            f"expected one of {list(VALID_STATUSES)}. "
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
        tags=_to_list(fm.get("tags", [])),
        script=str(fm.get("script", "")),
        input=_to_list(fm.get("input", [])),
        output=_to_list(fm.get("output", [])),
        created=str(fm.get("created", "")),
        body=body,
        objective=sections.get("Objective", ""),
        results=sections.get("Results", ""),
        decisions=sections.get("Decisions", ""),
        revision_notes=sections.get("Revision Notes", ""),
        review_notes=sections.get("Review Notes", ""),
    )


def write_task(task: Task) -> None:
    """Write a Task back to its task.md file, preserving body content."""
    fm: dict[str, str | list[str]] = {}
    if task.title:
        fm["title"] = task.title
    fm["status"] = task.status
    if task.depends_on:
        fm["depends_on"] = task.depends_on
    else:
        fm["depends_on"] = []
    if task.tags:
        fm["tags"] = task.tags
    else:
        fm["tags"] = []
    if task.script:
        fm["script"] = task.script
    if task.input:
        fm["input"] = task.input
    if task.output:
        fm["output"] = task.output
    if task.created:
        fm["created"] = task.created

    fm_text = serialize_frontmatter(fm)
    content = f"---\n{fm_text}---\n{task.body}"

    task_md = task.dir_path / "task.md"
    task_md.write_text(content, encoding="utf-8")


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
        d for d in parent_dir.iterdir()
        if d.is_dir() and (d / "task.md").exists() and d.name != new_slug
    ]
    for sibling_dir in siblings:
        task = parse_task(sibling_dir / "task.md")
        if old_slug in task.depends_on:
            task.depends_on = [new_slug if d == old_slug else d for d in task.depends_on]
            write_task(task)
            updated.append(sibling_dir.name)
    return updated


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


def walk_plan(plan_root: Path) -> Task:
    """Recursively walk a plan directory and build the task tree.

    Returns the root Task with children populated.
    """
    root_task_md = plan_root / "task.md"
    if root_task_md.exists():
        root = parse_task(root_task_md, plan_root)
    else:
        root = Task(path="", dir_path=plan_root, title="(no root task.md)")

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
    subdirs = sorted(
        [d for d in directory.iterdir() if d.is_dir() and (d / "task.md").exists()],
        key=lambda d: d.name,
    )
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


def resolve_path(plan_root: Path, task_path: str) -> Path:
    """Resolve a task ID (relative path) to its directory on disk.

    Task paths are relative to the task root and omit the root prefix (e.g.
    ``task-tree/planning-redesign``). As an ergonomic tolerance, a redundant
    leading segment equal to the task-root basename (``superRA``, or legacy
    ``.plan``) is stripped before joining, so an agent that passes the
    fully-prefixed form (``superRA/task-tree/planning-redesign``) resolves to
    the same task instead of a doubled ``superRA/superRA/...`` path.

    Raises ValueError if the resolved path escapes the plan root.
    """
    if not task_path:
        return plan_root
    segments = task_path.strip("/").split("/")
    if len(segments) > 1 and segments[0] == plan_root.name and segments[0] in TASK_ROOT_DIRNAMES:
        task_path = "/".join(segments[1:])
    resolved = (plan_root / task_path).resolve()
    root_resolved = plan_root.resolve()
    if not resolved.is_relative_to(root_resolved):
        raise ValueError(
            f"Task path {task_path!r} escapes plan root {plan_root}"
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
    4. Any child in-progress or implemented -> in-progress
    5. Any child approved (but not all) -> in-progress
    6. Otherwise -> not-started
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
    if any(s in ("in-progress", "implemented") for s in child_statuses):
        return "in-progress"
    if any(s == "approved" for s in child_statuses):
        return "in-progress"
    return "not-started"


def propagate_parent_status(plan_root: Path, task_path: str) -> int:
    """Walk from task_path up to the root, recomputing parent statuses.

    For each ancestor that is not a leaf, computes rolled-up status from
    children via compute_status() and writes back if changed.

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

        if ancestor_task.status != rolled_status:
            ancestor_task.status = rolled_status
            changed = True

        if changed:
            write_task(ancestor_task)
            updated += 1

    return updated


def compute_frontier(root: Task) -> list[Task]:
    """Compute the dispatch frontier: leaf tasks ready to be worked on.

    A leaf task is on the frontier when:
    1. Its own status is 'not-started' or 'in-progress'
    2. All sibling dependencies have effective_status 'approved'
    3. All ancestor tasks' sibling dependencies are met (recursively)
    """
    frontier: list[Task] = []
    _collect_frontier(root, frontier, ancestors_ready=True)
    return frontier


def _collect_frontier(task: Task, frontier: list[Task], ancestors_ready: bool) -> None:
    """Recursively collect frontier tasks."""
    if task.is_leaf:
        if task.status in ("archived", "postponed"):
            return  # parked tasks never appear on the frontier
        if ancestors_ready and task.status in ("not-started", "in-progress"):
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
            # Archived dependencies are treated as satisfied; postponed ones
            # are NOT — postponing a task deliberately blocks its dependents
            # until it is resumed and approved.
            dep_status = dep_task.effective_status()
            if dep_status not in ("approved", "archived"):
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


def today_str() -> str:
    return date.today().isoformat()


# ---------------------------------------------------------------------------
# Validation functions
# ---------------------------------------------------------------------------


def validate_frontmatter(task: Task) -> list[str]:
    """Validate frontmatter fields of a Task.

    Returns a list of warning strings for any violations.
    """
    warnings_out: list[str] = []

    if task.status not in VALID_STATUSES:
        warnings_out.append(
            f"invalid status {task.status!r}; expected one of {VALID_STATUSES}"
        )
    if not isinstance(task.depends_on, list) or not all(
        isinstance(v, str) for v in task.depends_on
    ):
        warnings_out.append("depends_on must be a list of strings")
    if not isinstance(task.tags, list) or not all(
        isinstance(v, str) for v in task.tags
    ):
        warnings_out.append("tags must be a list of strings")
    if not task.title or not task.title.strip():
        warnings_out.append("title must be a non-empty string")

    return warnings_out


def validate_revision_notes(task: Task) -> list[str]:
    """Warn when an ``approved`` task still carries a ``## Revision Notes`` section.

    The reviewer owns revision-note removal at approval, so an approved task
    holding a non-empty note is a stale leak. Only ``approved`` warns:
    ``implemented`` + a note is a legitimate mid-state (a reopened, reworked
    task awaiting re-review), and earlier states never carry one. Detection is
    fence-aware so a header quoted inside a code block does not trigger it.
    """
    if task.status != "approved":
        return []
    if not _has_nonempty_section(task.body, "Revision Notes"):
        return []
    return [
        "approved task still carries a ## Revision Notes section; "
        "the reviewer should remove it at approval"
    ]


def validate_dependencies(task: Task, siblings: list[str]) -> list[str]:
    """Check that all depends_on entries reference existing sibling directory names.

    siblings: list of sibling directory names at the same level as task.
    Returns a list of warning strings for missing references.
    """
    sibling_set = set(siblings)
    warnings_out: list[str] = []
    for dep in task.depends_on:
        if dep not in sibling_set:
            warnings_out.append(
                f"depends_on {dep!r} does not match any sibling task"
            )
    return warnings_out


def detect_cycles(tasks: list[Task]) -> list[str]:
    """Detect circular dependencies among a list of sibling Tasks using DFS.

    Returns a list of cycle description strings.
    """
    slug_to_deps: dict[str, list[str]] = {}
    slug_set = {t.slug for t in tasks}
    for t in tasks:
        # Only include deps that exist within this sibling group
        slug_to_deps[t.slug] = [d for d in t.depends_on if d in slug_set]

    warnings_out: list[str] = []
    # DFS state: WHITE=0 (unvisited), GRAY=1 (in stack), BLACK=2 (done)
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {slug: WHITE for slug in slug_to_deps}
    stack: list[str] = []

    def dfs(node: str) -> bool:
        """Return True if a cycle was found from node."""
        color[node] = GRAY
        stack.append(node)
        for neighbor in slug_to_deps.get(node, []):
            if color[neighbor] == GRAY:
                # Found a cycle — extract the cycle portion from the stack
                cycle_start = stack.index(neighbor)
                cycle = stack[cycle_start:] + [neighbor]
                warnings_out.append("cycle detected: " + " -> ".join(cycle))
                stack.pop()
                color[node] = BLACK
                return True
            if color[neighbor] == WHITE:
                if dfs(neighbor):
                    stack.pop()
                    color[node] = BLACK
                    return True
        stack.pop()
        color[node] = BLACK
        return False

    for slug in sorted(slug_to_deps):
        if color[slug] == WHITE:
            dfs(slug)

    return warnings_out


def validate_plan(plan_root: Path) -> list[str]:
    """Walk the entire plan tree and run all validations at each level.

    Returns aggregated list of warning strings, each prefixed with the task path.
    """
    warnings_out: list[str] = []

    def _validate_level(directory: Path) -> None:
        subdirs = [
            d for d in directory.iterdir()
            if d.is_dir() and (d / "task.md").exists()
        ]

        tasks_at_level: list[Task] = []
        for subdir in subdirs:
            try:
                task = parse_task(subdir / "task.md", plan_root)
            except Exception as exc:
                warnings_out.append(f"{subdir.name}: parse error: {exc}")
                continue
            tasks_at_level.append(task)

        sibling_names = [t.slug for t in tasks_at_level]

        for task in tasks_at_level:
            prefix = task.path if task.path else task.slug

            for w in validate_frontmatter(task):
                warnings_out.append(f"{prefix}: {w}")

            for w in validate_revision_notes(task):
                warnings_out.append(f"{prefix}: {w}")

            for w in validate_dependencies(task, sibling_names):
                warnings_out.append(f"{prefix}: {w}")

        for w in detect_cycles(tasks_at_level):
            warnings_out.append(f"{directory.name}: {w}")

        for subdir in subdirs:
            _validate_level(subdir)

    # Validate root task if present
    root_task_md = plan_root / "task.md"
    if root_task_md.exists():
        try:
            root_task = parse_task(root_task_md, plan_root)
            for w in validate_frontmatter(root_task):
                warnings_out.append(f"(root): {w}")
            for w in validate_revision_notes(root_task):
                warnings_out.append(f"(root): {w}")
        except Exception as exc:
            warnings_out.append(f"(root): parse error: {exc}")

    _validate_level(plan_root)
    return warnings_out
