#!/usr/bin/env python3
"""Read-only diagnostic tool for task tree integrity.

Checks:
1. Status validity — all status values in valid enum, flags stale
   review_status / integration_status fields still in frontmatter.
2. Dependency integrity — all depends_on resolve to existing siblings,
   no cycles, flags dependencies on archived tasks.
3. Rollup consistency — stored parent status matches compute_status()
   from children.

Exit code 0 if clean, 1 if issues found.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _task_io import (
    TASK_ROOT_DIRNAME,
    VALID_STATUSES,
    Task,
    compute_status,
    detect_cycles,
    parse_frontmatter,
    parse_task,
    resolve_plan_root_arg,
)


# ---------------------------------------------------------------------------
# Finding data model
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    """A single diagnostic finding."""

    task_path: str
    category: str  # "status" | "dependency" | "rollup" | "placement"
    severity: str  # "error" | "warning"
    message: str

    def to_text(self) -> str:
        prefix = self.task_path or "(root)"
        return f"[{self.severity.upper()}] [{self.category}] {prefix}: {self.message}"

    def to_dict(self) -> dict:
        return {
            "task_path": self.task_path,
            "category": self.category,
            "severity": self.severity,
            "message": self.message,
        }


# ---------------------------------------------------------------------------
# Check 1: Status validity
# ---------------------------------------------------------------------------

def check_status_validity(root: Task, plan_root: Path) -> list[Finding]:
    """Check all tasks have valid status values and no stale fields."""
    findings: list[Finding] = []
    _check_status_recursive(root, plan_root, findings)
    return findings


def _check_status_recursive(
    task: Task, plan_root: Path, findings: list[Finding]
) -> None:
    # Check the status value itself
    if task.status not in VALID_STATUSES:
        findings.append(Finding(
            task_path=task.path,
            category="status",
            severity="error",
            message=(
                f"invalid status {task.status!r}; "
                f"expected one of {list(VALID_STATUSES)}"
            ),
        ))

    # Check for stale review_status / integration_status in raw frontmatter
    task_md = task.dir_path / "task.md"
    if task_md.exists():
        text = task_md.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        stale_fields = {"review_status", "integration_status"}
        for field_name in sorted(stale_fields & fm.keys()):
            value = fm[field_name]
            if value and value != "~":
                findings.append(Finding(
                    task_path=task.path,
                    category="status",
                    severity="warning",
                    message=(
                        f"stale field '{field_name}' still present "
                        f"with value {value!r}; should be removed"
                    ),
                ))
            else:
                findings.append(Finding(
                    task_path=task.path,
                    category="status",
                    severity="warning",
                    message=(
                        f"stale field '{field_name}' still present "
                        f"in frontmatter (value: {value!r}); should be removed"
                    ),
                ))

    for child in task.children:
        _check_status_recursive(child, plan_root, findings)


# ---------------------------------------------------------------------------
# Check 2: Dependency integrity
# ---------------------------------------------------------------------------

def check_dependency_integrity(root: Task) -> list[Finding]:
    """Check dependency resolution, cycles, and archived dependencies."""
    findings: list[Finding] = []
    _check_deps_recursive(root, findings)
    return findings


def _check_deps_recursive(task: Task, findings: list[Finding]) -> None:
    if not task.children:
        return

    sibling_map = {c.slug: c for c in task.children}

    # Check each child's depends_on references
    for child in task.children:
        for dep in child.depends_on:
            if dep not in sibling_map:
                findings.append(Finding(
                    task_path=child.path,
                    category="dependency",
                    severity="error",
                    message=f"depends_on '{dep}' does not resolve to any sibling task",
                ))
            else:
                dep_task = sibling_map[dep]
                if dep_task.effective_status() == "archived":
                    findings.append(Finding(
                        task_path=child.path,
                        category="dependency",
                        severity="warning",
                        message=f"depends on archived task '{dep}'",
                    ))
                elif dep_task.effective_status() == "postponed":
                    findings.append(Finding(
                        task_path=child.path,
                        category="dependency",
                        severity="warning",
                        message=f"depends on postponed task '{dep}' (blocked until resumed)",
                    ))

    # Cycle detection at this sibling level
    cycle_warnings = detect_cycles(task.children)
    for warning in cycle_warnings:
        findings.append(Finding(
            task_path=task.path,
            category="dependency",
            severity="error",
            message=warning,
        ))

    # Recurse into children that have their own children
    for child in task.children:
        _check_deps_recursive(child, findings)


# ---------------------------------------------------------------------------
# Check 3: Rollup consistency
# ---------------------------------------------------------------------------

def check_rollup_consistency(root: Task) -> list[Finding]:
    """Check that stored parent status matches computed rollup."""
    findings: list[Finding] = []
    _check_rollup_recursive(root, findings)
    return findings


def _check_rollup_recursive(task: Task, findings: list[Finding]) -> None:
    if not task.children:
        return

    computed = compute_status(task)
    stored = task.status

    if stored != computed:
        findings.append(Finding(
            task_path=task.path,
            category="rollup",
            severity="warning",
            message=(
                f"stored status is '{stored}' but computed rollup "
                f"from children is '{computed}'"
            ),
        ))

    for child in task.children:
        _check_rollup_recursive(child, findings)


# ---------------------------------------------------------------------------
# Check 4: Placement / structure (advisory)
# ---------------------------------------------------------------------------

def check_placement(root: Task) -> list[Finding]:
    """Advisory structural smells the placement ladder forbids.

    All findings are ``warning`` severity — surfaced, never auto-corrected, per
    the "hooks warn, not auto-mutate" principle. These encode the positive
    root-task definition (root = whole workstream; branches carry no
    script/input/output) and the misplacement signal from the placement task in
    `task-system/references/planning.md §Placing Work in the Tree`.
    """
    findings: list[Finding] = []

    # Smell 1: the root carries leaf-only frontmatter (a leaf masquerading as
    # the project). A root frames a whole workstream and holds no deliverable
    # work of its own, so script/input/output belong on its leaves.
    leaf_fields = [
        name for name in ("script", "input", "output")
        if getattr(root, name)
    ]
    if leaf_fields:
        findings.append(Finding(
            task_path=root.path,
            category="placement",
            severity="warning",
            message=(
                f"root carries leaf-only field(s) {leaf_fields}; a root frames a "
                f"whole workstream and holds no deliverable work — move "
                f"script/input/output down to a leaf task"
            ),
        ))

    # Smell 2: a single-child root is a wrapper around one narrow task — the
    # child should be the root, or the root should host the broader workstream.
    if len(root.children) == 1:
        findings.append(Finding(
            task_path=root.path,
            category="placement",
            severity="warning",
            message=(
                "single-child root wraps one narrow task; promote the child to "
                "root or broaden the root to a whole workstream"
            ),
        ))

    # Smell 3: a root-level leaf sitting beside root-level branches — a narrow
    # feature hoisted to root instead of nesting under the workstream it relates
    # to. Only smells when branches coexist (an all-leaf root is a flat plan).
    root_leaves = [c for c in root.children if c.is_leaf]
    root_branches = [c for c in root.children if not c.is_leaf]
    if root_leaves and root_branches:
        for leaf in root_leaves:
            findings.append(Finding(
                task_path=leaf.path,
                category="placement",
                severity="warning",
                message=(
                    "root-level leaf sits beside root-level branch(es); a narrow "
                    "feature should nest under the workstream it relates to, not "
                    "hoist to root"
                ),
            ))

    # Smell 4: substantial concern overlap across subtrees — a misplacement /
    # duplicate candidate. Detectable signal: two tasks in different top-level
    # subtrees declare an identical output artifact, meaning one concern is
    # split across two places. Conservative (exact output match only) to keep
    # false positives low; deeper objective overlap is left to the human survey.
    _check_cross_subtree_output_overlap(root, findings)

    return findings


# Ubiquitous output filenames that many unrelated tasks legitimately produce —
# a shared basename here signals "common file", not "split concern", so they are
# excluded from the cross-subtree overlap signal to keep false positives low.
_GENERIC_OUTPUT_BASENAMES = frozenset({
    "readme.md", "readme", "skill.md", "index.html", "dashboard.html",
    "task.md", "__init__.py", "notes.md", "summary.md", "output.csv",
})


def _is_generic_output(artifact: str) -> bool:
    return Path(artifact).name.lower() in _GENERIC_OUTPUT_BASENAMES


def _check_cross_subtree_output_overlap(
    root: Task, findings: list[Finding]
) -> None:
    """Flag identical declared outputs owned by tasks in different subtrees.

    Generic basenames (README.md, SKILL.md, ...) are excluded — a shared common
    filename is not a split-concern signal, only a shared specific artifact is.
    """
    # Map each output artifact -> list of (top_subtree_slug, task_path) owning it.
    output_owners: dict[str, list[tuple[str, str]]] = {}

    def _collect(task: Task, top_slug: str) -> None:
        for artifact in task.output:
            if _is_generic_output(artifact):
                continue
            output_owners.setdefault(artifact, []).append((top_slug, task.path))
        for child in task.children:
            _collect(child, top_slug)

    for child in root.children:
        _collect(child, child.slug)

    for artifact, owners in output_owners.items():
        subtrees = {top_slug for top_slug, _ in owners}
        if len(subtrees) > 1:
            paths = ", ".join(sorted(path for _, path in owners))
            for _, path in owners:
                findings.append(Finding(
                    task_path=path,
                    category="placement",
                    severity="warning",
                    message=(
                        f"output {artifact!r} is also produced by another subtree "
                        f"({paths}); one concern may be split across subtrees — "
                        f"consider consolidating"
                    ),
                ))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Diagnostic tool for task tree integrity (read-only)."
    )
    parser.add_argument(
        "--plan-root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    parser.add_argument(
        "--json", action="store_true", dest="as_json",
        help="Output findings as JSON",
    )
    parser.add_argument(
        "--category",
        choices=["status", "dependency", "rollup", "placement"],
        help="Only run a specific check category",
    )
    return parser.parse_args(argv)


def _walk_plan_tolerant(plan_root: Path) -> Task:
    """Walk plan tree, catching parse errors so checks can still run.

    Tasks with invalid status values are included with their raw status
    preserved so that check_status_validity can report them.
    """

    def _tolerant_parse(task_md: Path) -> Task | None:
        try:
            return parse_task(task_md)
        except ValueError as exc:
            # Build a partial task from raw frontmatter so the tree walk
            # can continue.  The status check will flag the bad value.
            text = task_md.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(text)

            parent = task_md.parent
            # Compute path relative to plan_root
            try:
                rel = parent.relative_to(plan_root)
                path = str(rel) if str(rel) != "." else ""
            except ValueError:
                path = parent.name

            raw_status = str(fm.get("status", "not-started"))
            # Don't report here — check_status_validity will flag the
            # invalid enum value in its own pass.

            deps_raw = fm.get("depends_on", [])
            if isinstance(deps_raw, str):
                deps = [deps_raw] if deps_raw and deps_raw != "~" else []
            else:
                deps = deps_raw

            tags_raw = fm.get("tags", [])
            if isinstance(tags_raw, str):
                tags = [tags_raw] if tags_raw and tags_raw != "~" else []
            else:
                tags = tags_raw

            return Task(
                path=path,
                dir_path=parent,
                title=str(fm.get("title", "")),
                status=raw_status,
                depends_on=deps,
                tags=tags,
                body=body,
            )

    def _walk_children(directory: Path) -> list[Task]:
        subdirs = sorted(
            [d for d in directory.iterdir()
             if d.is_dir() and (d / "task.md").exists()],
            key=lambda d: d.name,
        )
        children: list[Task] = []
        for subdir in subdirs:
            child = _tolerant_parse(subdir / "task.md")
            if child is not None:
                child.children = _walk_children(subdir)
                children.append(child)
        return children

    root_task_md = plan_root / "task.md"
    if root_task_md.exists():
        root = _tolerant_parse(root_task_md)
        if root is None:
            root = Task(path="", dir_path=plan_root, title="(parse error)")
    else:
        root = Task(path="", dir_path=plan_root, title="(no root task.md)")

    root.children = _walk_children(plan_root)
    return root


def run_checks(
    plan_root: Path,
    category: str | None = None,
) -> list[Finding]:
    """Run all (or filtered) checks and return findings."""
    root = _walk_plan_tolerant(plan_root)
    findings: list[Finding] = []

    if category is None or category == "status":
        findings.extend(check_status_validity(root, plan_root))
    if category is None or category == "dependency":
        findings.extend(check_dependency_integrity(root))
    if category is None or category == "rollup":
        findings.extend(check_rollup_consistency(root))
    if category is None or category == "placement":
        findings.extend(check_placement(root))

    return findings


def format_text(findings: list[Finding]) -> str:
    """Format findings as human-readable text."""
    if not findings:
        return "All checks passed. No issues found."

    lines: list[str] = []
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]

    lines.append(f"Found {len(findings)} issue(s): {len(errors)} error(s), {len(warnings)} warning(s).")
    lines.append("")

    for finding in findings:
        lines.append(finding.to_text())

    return "\n".join(lines)


def format_json(findings: list[Finding]) -> str:
    """Format findings as JSON."""
    return json.dumps(
        {
            "ok": len(findings) == 0,
            "total": len(findings),
            "errors": sum(1 for f in findings if f.severity == "error"),
            "warnings": sum(1 for f in findings if f.severity == "warning"),
            "findings": [f.to_dict() for f in findings],
        },
        indent=2,
    )


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    plan_root = resolve_plan_root_arg(args.plan_root)
    if plan_root is None:
        print("Error: could not auto-detect task root. Use --plan-root.", file=sys.stderr)
        sys.exit(1)

    if not plan_root.exists():
        print(f"Error: plan root not found: {plan_root}", file=sys.stderr)
        sys.exit(1)

    findings = run_checks(plan_root, category=args.category)

    if args.as_json:
        print(format_json(findings))
    else:
        print(format_text(findings))

    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
