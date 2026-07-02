#!/usr/bin/env python3
"""Migrate a legacy PLAN.md + RESULTS.md pair into a task directory tree."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _task_io import TASK_ROOT_DIRNAME, parse_frontmatter, serialize_frontmatter


TASK_BLOCK_RE = re.compile(
    r"^###\s+Task\s+(\d+):\s+(.+?)$",
    re.MULTILINE,
)

RESULTS_SECTION_RE = re.compile(
    r"^##\s+Task\s+(\d+):\s+(.+?)$",
    re.MULTILINE,
)

FIELD_RE = {
    "depends_on": re.compile(r"^\*\*Depends on:\*\*\s*(.+)$", re.MULTILINE),
    "review_status": re.compile(r"^\*\*Review status:\*\*\s*(.+)$", re.MULTILINE),
    "integration_status": re.compile(r"^\*\*Integration status:\*\*\s*(.+)$", re.MULTILINE),
}

# Fields that are removed during status consolidation upgrade
STALE_STATUS_FIELDS = {"review_status", "integration_status"}

# Regex to match ## Workflow Status sections in task bodies
WORKFLOW_STATUS_SECTION_RE = re.compile(
    r"^## Workflow Status\s*\n(?:(?!^## ).)*",
    re.MULTILINE | re.DOTALL,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Migrate legacy PLAN.md + RESULTS.md into a {TASK_ROOT_DIRNAME}/ task tree, "
        "or upgrade existing task files."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--plan-md", help=f"Path to PLAN.md (PLAN.md -> {TASK_ROOT_DIRNAME}/ migration)")
    group.add_argument(
        "--upgrade", action="store_true", default=False,
        help="Upgrade existing task files from v1 to v2 format (headings, checkboxes)",
    )
    group.add_argument(
        "--upgrade-status", action="store_true", default=False,
        help="Consolidate review_status/integration_status into single status field",
    )
    parser.add_argument("--results-md", default="", help="Path to RESULTS.md (optional, for --plan-md)")
    parser.add_argument(
        "--output",
        default="",
        help=f"Output directory (for --plan-md; default: {TASK_ROOT_DIRNAME})",
    )
    parser.add_argument("--plan-root", default="", help="Plan root directory (for --upgrade/--upgrade-status)")
    parser.add_argument("--dry-run", action="store_true", default=False,
                        help="Show what would change without writing files (for --upgrade-status)")
    return parser.parse_args(argv)


def slugify(text: str) -> str:
    """Convert a task title to a directory slug."""
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")[:60]


def _parse_depends_on(raw: str) -> list[str]:
    """Parse depends-on field: 'Task 1, Task 3' or '*(none)*'."""
    raw = raw.strip()
    if not raw or raw == "*(none)*":
        return []
    return [t.strip() for t in raw.split(",") if t.strip()]


def _extract_header(plan_text: str) -> str:
    """Extract the header portion of PLAN.md (everything before the first task block)."""
    match = TASK_BLOCK_RE.search(plan_text)
    if match:
        return plan_text[: match.start()].rstrip()
    return plan_text.rstrip()


def _extract_task_blocks(plan_text: str) -> list[tuple[int, str, str]]:
    """Extract task blocks from PLAN.md.

    Returns list of (task_number, title, body) tuples.
    """
    matches = list(TASK_BLOCK_RE.finditer(plan_text))
    blocks = []
    for i, match in enumerate(matches):
        task_num = int(match.group(1))
        title = match.group(2).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(plan_text)
        body = plan_text[start:end].strip()
        blocks.append((task_num, title, body))
    return blocks


def _extract_results_sections(results_text: str) -> dict[int, str]:
    """Extract per-task results from RESULTS.md.

    Returns {task_number: results_body}.
    """
    if not results_text:
        return {}

    matches = list(RESULTS_SECTION_RE.finditer(results_text))
    sections = {}
    for i, match in enumerate(matches):
        task_num = int(match.group(1))
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(results_text)
        body = results_text[start:end].strip()
        body_stripped = body.strip()
        if body_stripped and "Not started" not in body_stripped.split("\n")[0]:
            sections[task_num] = body
    return sections


def _extract_field(body: str, field_name: str) -> str:
    """Extract a field value from a task block body."""
    pattern = FIELD_RE.get(field_name)
    if not pattern:
        return ""
    match = pattern.search(body)
    return match.group(1).strip() if match else ""


def _extract_steps_and_rest(body: str) -> tuple[str, str, str, str]:
    """Split the task body into metadata, steps, review notes, and sync impact.

    Returns (meta, steps_body, review_notes, sync_impact).
    """
    lines = body.split("\n")
    meta_end = 0
    for i, line in enumerate(lines):
        if line.startswith("- [") or line.startswith("```"):
            meta_end = i
            break
        if line.startswith("**") and ":**" in line:
            meta_end = i + 1

    # Collect non-field, non-step content between metadata and steps
    review_notes_lines: list[str] = []
    sync_impact_lines: list[str] = []
    extra_lines: list[str] = []
    in_sync_impact = False

    for line in lines[meta_end:]:
        # Detect sync impact section
        if re.match(r"^##\s+Sync\s+[Ii]mpact", line):
            in_sync_impact = True
            continue
        if in_sync_impact:
            if line.startswith("## ") or line.startswith("- [") or line.startswith("```"):
                in_sync_impact = False
            else:
                sync_impact_lines.append(line)
                continue

        # Steps and code blocks go to steps
        if line.startswith("- [") or line.startswith("```"):
            extra_lines.append(line)
        elif line.startswith("> "):
            review_notes_lines.append(line)
        else:
            extra_lines.append(line)

    meta = "\n".join(lines[:meta_end]).strip()
    rest = "\n".join(extra_lines).strip()
    review_notes = "\n".join(review_notes_lines).strip()
    sync_impact = "\n".join(sync_impact_lines).strip()
    return meta, rest, review_notes, sync_impact


def _normalize_status_value(raw: str) -> str:
    """Normalize a raw status string from PLAN.md to a canonical status value."""
    raw = raw.strip().upper()
    if "APPROVED" in raw:
        return "approved"
    if "REVISE" in raw:
        return "revise"
    if "IMPLEMENTED" in raw:
        return "implemented"
    return ""


def _compute_status_from_steps(body: str) -> str:
    """Infer unified task status from PLAN.md fields and checkbox states.

    Applies the migration mapping: integration_status > review_status > checkboxes.
    """
    # Most-recent lifecycle field takes precedence (migration mapping)
    integration_raw = _extract_field(body, "integration_status")
    integration = _normalize_status_value(integration_raw)
    if integration:
        return integration

    review_raw = _extract_field(body, "review_status")
    review = _normalize_status_value(review_raw)
    if review:
        return review

    # Fall back to checkbox-based inference
    checked = len(re.findall(r"- \[[xX]\]", body))
    unchecked = len(re.findall(r"- \[ \]", body))
    if checked > 0 and unchecked == 0:
        return "implemented"
    if checked > 0:
        return "in-progress"
    return "not-started"


def _strip_checkboxes(text: str) -> str:
    """Strip checkbox syntax from step text, converting to plain bullets."""
    return re.sub(r"^- \[[xX ]\] ", "- ", text, flags=re.MULTILINE)


def _build_task_md(
    title: str,
    status: str,
    depends_on: list[str],
    steps_body: str,
    results_body: str,
    review_notes: str = "",
    sync_impact: str = "",
) -> str:
    """Build a task.md file content string."""
    deps = "\n" + "".join(f"  - {d}\n" for d in depends_on) if depends_on else " []"
    escaped_title = title.replace('"', '\\"')

    fm_lines = [
        "---",
        f'title: "{escaped_title}"',
        f"status: {status}",
        f"depends_on:{deps}",
        "---",
    ]

    # No # Title heading (redundant with frontmatter title)
    sections = ["\n".join(fm_lines), ""]

    if steps_body:
        objective_body = _strip_checkboxes(steps_body)
        sections.extend(["## Objective", "", objective_body, ""])

    if results_body:
        sections.extend(["## Results", "", results_body, ""])

    if review_notes:
        sections.extend(["## Review Notes", "", review_notes, ""])

    if sync_impact:
        sections.extend(["## Sync Impact", "", sync_impact, ""])

    return "\n".join(sections) + "\n"


def migrate(plan_md_path: Path, results_md_path: Path | None, output_dir: Path) -> None:
    """Run the migration."""
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError(f"output directory is not empty: {output_dir}")

    plan_text = plan_md_path.read_text(encoding="utf-8")
    results_text = ""
    if results_md_path and results_md_path.exists():
        results_text = results_md_path.read_text(encoding="utf-8")

    header = _extract_header(plan_text)
    task_blocks = _extract_task_blocks(plan_text)
    results_sections = _extract_results_sections(results_text)

    # Extract plan title from header heading, fallback to "Project Plan"
    title_match = re.match(r"^#\s+(.+?)$", header, re.MULTILINE)
    plan_title = title_match.group(1).strip() if title_match else "Project Plan"
    escaped_plan_title = plan_title.replace('"', '\\"')

    output_dir.mkdir(parents=True, exist_ok=True)

    root_task_md = output_dir / "task.md"
    root_content = f"---\ntitle: \"{escaped_plan_title}\"\nstatus: not-started\ndepends_on: []\n---\n\n{header}\n"
    root_task_md.write_text(root_content, encoding="utf-8")
    print(f"Created {root_task_md}")

    task_num_to_slug: dict[int, str] = {}
    for task_num, title, _ in task_blocks:
        slug = f"{task_num:02d}-{slugify(title)}"
        task_num_to_slug[task_num] = slug

    for task_num, title, body in task_blocks:
        slug = task_num_to_slug[task_num]
        task_dir = output_dir / slug
        task_dir.mkdir()

        raw_deps = _parse_depends_on(_extract_field(body, "depends_on"))
        depends_on_slugs = []
        for dep_str in raw_deps:
            dep_match = re.match(r"Task\s+(\d+)", dep_str)
            if dep_match:
                dep_num = int(dep_match.group(1))
                if dep_num in task_num_to_slug:
                    depends_on_slugs.append(task_num_to_slug[dep_num])

        # Unified status: migration mapping applied inside _compute_status_from_steps
        status = _compute_status_from_steps(body)

        _, steps_body, review_notes, sync_impact = _extract_steps_and_rest(body)

        results_body = results_sections.get(task_num, "")

        task_content = _build_task_md(
            title=title,
            status=status,
            depends_on=depends_on_slugs,
            steps_body=steps_body,
            results_body=results_body,
            review_notes=review_notes,
            sync_impact=sync_impact,
        )

        task_md = task_dir / "task.md"
        task_md.write_text(task_content, encoding="utf-8")
        print(f"Created {task_md}")

    print(f"\nMigrated {len(task_blocks)} tasks to {output_dir}")


def _upgrade_task_body(body: str) -> tuple[str, bool]:
    """Upgrade a single task body from v1 to v2 format.

    Returns (new_body, changed) where changed indicates whether any
    modifications were made.
    """
    changed = False
    lines = body.split("\n")

    # Remove leading # Title heading (redundant with frontmatter title)
    new_lines: list[str] = []
    skip_blank_after_title = False
    for i, line in enumerate(lines):
        if i == 0 and line == "":
            # Leading blank line before potential title — keep it for now
            new_lines.append(line)
            continue
        if not changed and skip_blank_after_title and line == "":
            # Skip one blank line after removed title
            skip_blank_after_title = False
            continue
        if re.match(r"^# .+$", line) and not changed:
            # Only remove the first # heading (the title)
            # Check it's at the start of the body (after optional blank lines)
            preceding = "\n".join(new_lines).strip()
            if preceding == "":
                # This is the leading title heading — remove it
                changed = True
                skip_blank_after_title = True
                # Also remove any preceding blank lines we already added
                while new_lines and new_lines[-1] == "":
                    new_lines.pop()
                continue
        skip_blank_after_title = False
        new_lines.append(line)

    body = "\n".join(new_lines)

    # Rename ## Steps to ## Objective and strip checkboxes only within that section
    steps_match = re.search(r"^## Steps\s*$", body, re.MULTILINE)
    if steps_match:
        steps_start = steps_match.start()
        next_section = re.search(r"^## ", body[steps_match.end():], re.MULTILINE)
        if next_section:
            steps_end = steps_match.end() + next_section.start()
            steps_content = body[steps_match.end():steps_end]
            body = body[:steps_start] + "## Objective\n" + _strip_checkboxes(steps_content) + body[steps_end:]
        else:
            steps_content = body[steps_match.end():]
            body = body[:steps_start] + "## Objective\n" + _strip_checkboxes(steps_content)
        changed = True

    return body, changed


def upgrade_v1_to_v2(plan_root: Path) -> list[Path]:
    """Walk a task-tree directory and upgrade all v1 task files to v2 format.

    Returns the list of files that were modified.
    """
    modified: list[Path] = []

    for task_md in sorted(plan_root.rglob("task.md")):
        text = task_md.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)

        new_body, changed = _upgrade_task_body(body)

        if changed:
            fm_text = serialize_frontmatter(fm)
            content = f"---\n{fm_text}---\n{new_body}"
            task_md.write_text(content, encoding="utf-8")
            modified.append(task_md)
            print(f"Upgraded {task_md}")

    if not modified:
        print("All task files are already in v2 format.")
    else:
        print(f"\nUpgraded {len(modified)} file(s).")

    return modified


def _apply_migration_mapping(
    status: str, review_status: str, integration_status: str,
) -> str:
    """Apply the status consolidation migration mapping.

    Precedence: integration_status > review_status > status.
    Returns the unified status value.
    """
    if integration_status and integration_status != "~":
        return integration_status
    if review_status and review_status != "~":
        return review_status
    return status


def upgrade_status(plan_root: Path, dry_run: bool = False) -> list[Path]:
    """Consolidate review_status/integration_status into the single status field.

    Walks all task.md files under plan_root and for each:
    - Reads the (status, review_status, integration_status) triple from frontmatter
    - Applies migration mapping to determine the unified status
    - Removes review_status and integration_status lines from frontmatter
    - Removes any ## Workflow Status sections from the body
    - Writes the file back (unless dry_run is True)

    Returns the list of files that were (or would be) modified.
    """
    modified: list[Path] = []

    for task_md in sorted(plan_root.rglob("task.md")):
        text = task_md.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)

        changed = False

        # Read the triple
        old_status = str(fm.get("status", "not-started"))
        old_review = str(fm.get("review_status", "~"))
        old_integration = str(fm.get("integration_status", "~"))

        # Apply migration mapping
        new_status = _apply_migration_mapping(old_status, old_review, old_integration)
        if new_status != old_status:
            changed = True

        # Check for stale fields to remove
        has_stale = any(k in fm for k in STALE_STATUS_FIELDS)
        if has_stale:
            changed = True

        # Check for ## Workflow Status section in body
        if WORKFLOW_STATUS_SECTION_RE.search(body):
            changed = True

        if not changed:
            continue

        # Apply changes
        fm["status"] = new_status
        for stale_key in STALE_STATUS_FIELDS:
            fm.pop(stale_key, None)

        new_body = WORKFLOW_STATUS_SECTION_RE.sub("", body)
        # Clean up any double blank lines left by section removal
        while "\n\n\n" in new_body:
            new_body = new_body.replace("\n\n\n", "\n\n")

        label = "[dry-run] " if dry_run else ""
        source = ""
        if old_review != "~" and old_review:
            source = f" (from review_status={old_review!r})"
        if old_integration != "~" and old_integration:
            source = f" (from integration_status={old_integration!r})"
        print(f"{label}{'Would update' if dry_run else 'Updated'} {task_md}: "
              f"status={old_status!r} -> {new_status!r}{source}")

        if not dry_run:
            fm_text = serialize_frontmatter(fm)
            content = f"---\n{fm_text}---\n{new_body}"
            task_md.write_text(content, encoding="utf-8")

        modified.append(task_md)

    if not modified:
        print("All task files already use the unified status field.")
    else:
        verb = "Would update" if dry_run else "Updated"
        print(f"\n{verb} {len(modified)} file(s).")

    return modified


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    if args.upgrade:
        if not args.plan_root:
            print("Error: --plan-root is required with --upgrade", file=sys.stderr)
            sys.exit(1)
        upgrade_v1_to_v2(Path(args.plan_root))
    elif args.upgrade_status:
        if not args.plan_root:
            print("Error: --plan-root is required with --upgrade-status", file=sys.stderr)
            sys.exit(1)
        upgrade_status(Path(args.plan_root), dry_run=args.dry_run)
    else:
        output = args.output or TASK_ROOT_DIRNAME
        results_path = Path(args.results_md) if args.results_md else None
        try:
            migrate(Path(args.plan_md), results_path, Path(output))
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
