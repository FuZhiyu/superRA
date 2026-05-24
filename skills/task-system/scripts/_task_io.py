#!/usr/bin/env python3
"""Shared internals for the task-system skill.

Provides parsing, serialization, tree walking, frontier computation,
and status rollup for the directory-tree task system.
"""

from __future__ import annotations

import re
import warnings
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


FRONTMATTER_RE = re.compile(r"\A---\n(.*?\n)---\n(.*)", re.DOTALL)

VALID_STATUSES = ("not-started", "in-progress", "implemented", "revise", "approved")
VALID_REVIEW_STATUSES = ("~", "implemented", "revise", "approved")
VALID_INTEGRATION_STATUSES = ("~", "implemented", "revise", "approved")


@dataclass
class Task:
    """A single task parsed from a task.md file."""

    path: str
    dir_path: Path
    title: str = ""
    status: str = "not-started"
    review_status: str = "~"
    integration_status: str = "~"
    depends_on: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    script: str = ""
    input: list[str] = field(default_factory=list)
    output: list[str] = field(default_factory=list)
    created: str = ""
    updated: str = ""
    body: str = ""
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
    """Parse a simple YAML value: scalar string, inline list, or multi-line list."""
    raw = raw.strip()
    if not raw or raw == "~":
        return raw

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


def parse_frontmatter(text: str) -> tuple[dict[str, str | list[str]], str]:
    """Parse YAML frontmatter and body from a task.md file.

    Returns (frontmatter_dict, body_string).
    """
    match = FRONTMATTER_RE.match(text)
    if not match:
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
        "title", "status", "review_status", "integration_status",
        "depends_on", "tags", "script", "input", "output",
        "created", "updated",
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


def parse_task(task_md_path: Path) -> Task:
    """Parse a task.md file into a Task object."""
    text = task_md_path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)

    plan_root = _find_plan_root(task_md_path.parent)
    if plan_root:
        rel = task_md_path.parent.relative_to(plan_root)
        path = str(rel) if str(rel) != "." else ""
    else:
        path = ""

    title = str(fm.get("title", ""))
    status = str(fm.get("status", "not-started"))
    review_status = str(fm.get("review_status", "~"))
    integration_status = str(fm.get("integration_status", "~"))

    if status not in VALID_STATUSES:
        raise ValueError(
            f"Invalid status {status!r} in {task_md_path}. "
            f"Valid values: {VALID_STATUSES}"
        )
    if review_status not in VALID_REVIEW_STATUSES:
        raise ValueError(
            f"Invalid review_status {review_status!r} in {task_md_path}. "
            f"Valid values: {VALID_REVIEW_STATUSES}"
        )
    if integration_status not in VALID_INTEGRATION_STATUSES:
        raise ValueError(
            f"Invalid integration_status {integration_status!r} in {task_md_path}. "
            f"Valid values: {VALID_INTEGRATION_STATUSES}"
        )

    return Task(
        path=path,
        dir_path=task_md_path.parent,
        title=title,
        status=status,
        review_status=review_status,
        integration_status=integration_status,
        depends_on=_to_list(fm.get("depends_on", [])),
        tags=_to_list(fm.get("tags", [])),
        script=str(fm.get("script", "")),
        input=_to_list(fm.get("input", [])),
        output=_to_list(fm.get("output", [])),
        created=str(fm.get("created", "")),
        updated=str(fm.get("updated", "")),
        body=body,
    )


def write_task(task: Task) -> None:
    """Write a Task back to its task.md file, preserving body content."""
    fm: dict[str, str | list[str]] = {}
    if task.title:
        fm["title"] = task.title
    fm["status"] = task.status
    fm["review_status"] = task.review_status
    fm["integration_status"] = task.integration_status
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
    if task.updated:
        fm["updated"] = task.updated

    fm_text = serialize_frontmatter(fm)
    content = f"---\n{fm_text}---\n{task.body}"

    task_md = task.dir_path / "task.md"
    task_md.write_text(content, encoding="utf-8")


def _find_plan_root(task_dir: Path) -> Path | None:
    """Walk up from a task directory to find the plan root.

    The plan root is the directory that contains the top-level task.md
    and is itself named with a dot-prefix (e.g., .plan) or is explicitly
    passed. We detect it by walking up until we find a directory whose
    parent does not contain a task.md.
    """
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
        root = parse_task(root_task_md)
    else:
        root = Task(path="", dir_path=plan_root, title="(no root task.md)")

    root.children = _walk_children(plan_root, plan_root)
    return root


def _walk_children(directory: Path, plan_root: Path) -> list[Task]:
    """Find and parse child task directories, sorted by name."""
    children = []
    subdirs = sorted(
        [d for d in directory.iterdir() if d.is_dir() and (d / "task.md").exists()],
        key=lambda d: d.name,
    )
    for subdir in subdirs:
        child = parse_task(subdir / "task.md")
        child.children = _walk_children(subdir, plan_root)
        children.append(child)
    return children


def resolve_path(plan_root: Path, task_path: str) -> Path:
    """Resolve a task ID (relative path) to its directory on disk.

    Raises ValueError if the resolved path escapes the plan root.
    """
    if not task_path:
        return plan_root
    resolved = (plan_root / task_path).resolve()
    root_resolved = plan_root.resolve()
    if not resolved.is_relative_to(root_resolved):
        raise ValueError(
            f"Task path {task_path!r} escapes plan root {plan_root}"
        )
    return resolved


def compute_status(task: Task) -> str:
    """Compute rolled-up status for a branch task from its children.

    Rules:
    - If all children are approved -> approved
    - If any child is revise -> revise
    - If any child is in-progress or implemented -> in-progress
    - Otherwise -> not-started
    """
    if task.is_leaf:
        return task.status

    child_statuses = [c.effective_status() for c in task.children]

    if not child_statuses:
        return task.status

    if all(s == "approved" for s in child_statuses):
        return "approved"
    if any(s == "revise" for s in child_statuses):
        return "revise"
    if any(s in ("in-progress", "implemented") for s in child_statuses):
        return "in-progress"
    if any(s == "approved" for s in child_statuses):
        return "in-progress"
    return "not-started"


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
        if ancestors_ready and task.status in ("not-started", "in-progress"):
            frontier.append(task)
        return

    sibling_map = {c.slug: c for c in task.children}

    for child in task.children:
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
            if dep_task.effective_status() != "approved":
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
