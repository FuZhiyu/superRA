#!/usr/bin/env python3
"""Validation suite for the task-tree skill."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from _task_io import (
    VALID_STATUSES,
    Task,
    _has_nonempty_section,
    parse_task,
)


@dataclass(frozen=True)
class ValidationFinding:
    """A validation rule result with presentation-independent operands."""

    code: str
    subject: str
    actual: Any = None
    path: str = ""
    related_nodes: tuple[str, ...] = ()

    @property
    def message(self) -> str:
        if self.code == "status.invalid":
            return invalid_status_message(str(self.actual))
        if self.code == "frontmatter.invalid-type":
            return f"{self.subject} must be a list of strings"
        if self.code == "frontmatter.empty":
            return f"{self.subject} must be a non-empty string"
        if self.code == "revision-notes.stale":
            return (
                "approved task still carries a ## Revision Notes section; "
                "the reviewer should remove it at approval"
            )
        if self.code == "dependency.missing-sibling":
            return f"depends_on {self.actual!r} does not match any sibling task"
        if self.code == "dependency.cycle":
            return "cycle detected: " + " -> ".join(self.related_nodes)
        if self.code == "task.parse-error":
            return f"parse error: {self.actual}"
        return self.code

    def __str__(self) -> str:
        prefix = self.path or "(root)"
        return f"{prefix}: {self.message}"


def invalid_status_message(status: str) -> str:
    """The single message source for the status-validity rule."""
    return f"invalid status {status!r}; expected one of {list(VALID_STATUSES)}"


def validate_frontmatter(task: Task) -> list[ValidationFinding]:
    """Validate frontmatter fields of a Task.

    Returns structured findings for any violations.
    """
    findings: list[ValidationFinding] = []

    if task.status not in VALID_STATUSES:
        findings.append(ValidationFinding(
            code="status.invalid",
            subject="status",
            actual=task.status,
            path=task.path,
        ))
    if not isinstance(task.depends_on, list) or not all(
        isinstance(v, str) for v in task.depends_on
    ):
        findings.append(ValidationFinding(
            code="frontmatter.invalid-type",
            subject="depends_on",
            actual=task.depends_on,
            path=task.path,
        ))
    if not task.title or not task.title.strip():
        findings.append(ValidationFinding(
            code="frontmatter.empty",
            subject="title",
            actual=task.title,
            path=task.path,
        ))

    return findings


def validate_revision_notes(task: Task) -> list[ValidationFinding]:
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
    return [ValidationFinding(
        code="revision-notes.stale",
        subject="Revision Notes",
        actual=task.status,
        path=task.path,
    )]


def validate_dependencies(
    task: Task, siblings: list[str]
) -> list[ValidationFinding]:
    """Check that all depends_on entries reference existing sibling directory names.

    siblings: list of sibling directory names at the same level as task.
    Returns structured findings for missing references.
    """
    sibling_set = set(siblings)
    findings: list[ValidationFinding] = []
    for dep in task.depends_on:
        if dep not in sibling_set:
            findings.append(ValidationFinding(
                code="dependency.missing-sibling",
                subject="depends_on",
                actual=dep,
                path=task.path,
                related_nodes=(dep,),
            ))
    return findings


def detect_cycles(
    tasks: list[Task], *, path: str | None = None
) -> list[ValidationFinding]:
    """Detect circular dependencies among a list of sibling Tasks using DFS.

    Returns structured cycle findings.
    """
    slug_to_deps: dict[str, list[str]] = {}
    slug_set = {t.slug for t in tasks}
    for t in tasks:
        # Only include deps that exist within this sibling group
        slug_to_deps[t.slug] = [d for d in t.depends_on if d in slug_set]

    findings: list[ValidationFinding] = []
    if path is None and tasks:
        parent = Path(tasks[0].path).parent
        path = "" if str(parent) == "." else str(parent)
    path = path or ""
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
                findings.append(ValidationFinding(
                    code="dependency.cycle",
                    subject="depends_on",
                    actual=True,
                    path=path,
                    related_nodes=tuple(cycle),
                ))
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

    return findings


def validate_plan(plan_root: Path) -> list[ValidationFinding]:
    """Walk the entire plan tree and run all validations at each level.

    Returns aggregated structured findings.
    """
    findings: list[ValidationFinding] = []

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
                rel = subdir.resolve().relative_to(plan_root.resolve())
                findings.append(ValidationFinding(
                    code="task.parse-error",
                    subject="task.md",
                    actual=str(exc),
                    path=str(rel),
                ))
                continue
            tasks_at_level.append(task)

        sibling_names = [t.slug for t in tasks_at_level]

        for task in tasks_at_level:
            findings.extend(validate_frontmatter(task))
            findings.extend(validate_revision_notes(task))
            findings.extend(validate_dependencies(task, sibling_names))

        rel = directory.resolve().relative_to(plan_root.resolve())
        level_path = "" if str(rel) == "." else str(rel)
        findings.extend(detect_cycles(tasks_at_level, path=level_path))

        for subdir in subdirs:
            _validate_level(subdir)

    # Validate root task if present
    root_task_md = plan_root / "task.md"
    if root_task_md.exists():
        try:
            root_task = parse_task(root_task_md, plan_root)
            findings.extend(validate_frontmatter(root_task))
            findings.extend(validate_revision_notes(root_task))
        except Exception as exc:
            findings.append(ValidationFinding(
                code="task.parse-error",
                subject="task.md",
                actual=str(exc),
                path="",
            ))

    _validate_level(plan_root)
    return findings
