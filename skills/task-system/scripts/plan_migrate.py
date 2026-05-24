#!/usr/bin/env python3
"""Migrate a PLAN.md + RESULTS.md pair into a .plan/ directory tree."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _task_io import today_str


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
    "script": re.compile(r"^\*\*Script:\*\*\s*`?([^`\n]+)`?\s*$", re.MULTILINE),
    "input": re.compile(r"^\*\*Input:\*\*\s*(.+)$", re.MULTILINE),
    "output": re.compile(r"^\*\*Output:\*\*\s*(.+)$", re.MULTILINE),
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Migrate PLAN.md + RESULTS.md into a .plan/ directory tree."
    )
    parser.add_argument("--plan-md", required=True, help="Path to PLAN.md")
    parser.add_argument("--results-md", default="", help="Path to RESULTS.md (optional)")
    parser.add_argument("--output", required=True, help="Output directory (e.g., .plan)")
    return parser.parse_args(argv)


def slugify(text: str) -> str:
    """Convert a task title to a directory slug."""
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")[:60]


def _extract_file_list(raw: str) -> list[str]:
    """Parse a comma-separated or backtick-delimited file list."""
    raw = raw.strip()
    if not raw or raw == "*(none)*":
        return []
    parts = re.findall(r"`([^`]+)`", raw)
    if parts:
        return parts
    return [p.strip() for p in raw.split(",") if p.strip()]


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


def _compute_status_from_steps(body: str) -> str:
    """Infer task status from checkbox states and review status."""
    review = _extract_field(body, "review_status").upper()
    if "APPROVED" in review:
        return "approved"
    if "REVISE" in review:
        return "revise"
    if "IMPLEMENTED" in review:
        return "implemented"

    checked = len(re.findall(r"- \[x\]", body))
    unchecked = len(re.findall(r"- \[ \]", body))
    if checked > 0 and unchecked == 0:
        return "implemented"
    if checked > 0:
        return "in-progress"
    return "not-started"


def _normalize_review_status(raw: str) -> str:
    raw = raw.strip().upper()
    if "APPROVED" in raw:
        return "approved"
    if "REVISE" in raw:
        return "revise"
    if "IMPLEMENTED" in raw:
        return "implemented"
    return "~"


def _build_task_md(
    title: str,
    status: str,
    review_status: str,
    integration_status: str,
    depends_on: list[str],
    script: str,
    input_files: list[str],
    output_files: list[str],
    steps_body: str,
    results_body: str,
    review_notes: str = "",
    sync_impact: str = "",
) -> str:
    """Build a task.md file content string."""
    deps = "\n" + "".join(f"  - {d}\n" for d in depends_on) if depends_on else " []"
    today = today_str()
    escaped_title = title.replace('"', '\\"')

    fm_lines = [
        "---",
        f'title: "{escaped_title}"',
        f"status: {status}",
        f"review_status: {review_status}",
        f"integration_status: {integration_status}",
        f"depends_on:{deps}",
        "tags: []",
    ]
    if script:
        fm_lines.append(f"script: {script}")
    if input_files:
        fm_lines.append("input:")
        for f in input_files:
            fm_lines.append(f"  - {f}")
    if output_files:
        fm_lines.append("output:")
        for f in output_files:
            fm_lines.append(f"  - {f}")
    fm_lines.extend([
        f"created: {today}",
        f"updated: {today}",
        "---",
    ])

    sections = ["\n".join(fm_lines), "", f"# {title}", ""]

    if steps_body:
        sections.extend(["## Steps", "", steps_body, ""])

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
    root_content = f"---\ntitle: \"{escaped_plan_title}\"\nstatus: not-started\nreview_status: ~\nintegration_status: ~\ndepends_on: []\ntags: []\ncreated: {today_str()}\nupdated: {today_str()}\n---\n\n{header}\n"
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

        review_raw = _extract_field(body, "review_status")
        integration_raw = _extract_field(body, "integration_status")
        script = _extract_field(body, "script")
        input_files = _extract_file_list(_extract_field(body, "input"))
        output_files = _extract_file_list(_extract_field(body, "output"))

        status = _compute_status_from_steps(body)
        review_status = _normalize_review_status(review_raw)
        integration_status = _normalize_review_status(integration_raw)

        _, steps_body, review_notes, sync_impact = _extract_steps_and_rest(body)

        results_body = results_sections.get(task_num, "")

        task_content = _build_task_md(
            title=title,
            status=status,
            review_status=review_status,
            integration_status=integration_status,
            depends_on=depends_on_slugs,
            script=script,
            input_files=input_files,
            output_files=output_files,
            steps_body=steps_body,
            results_body=results_body,
            review_notes=review_notes,
            sync_impact=sync_impact,
        )

        task_md = task_dir / "task.md"
        task_md.write_text(task_content, encoding="utf-8")
        print(f"Created {task_md}")

    print(f"\nMigrated {len(task_blocks)} tasks to {output_dir}")


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    results_path = Path(args.results_md) if args.results_md else None
    try:
        migrate(Path(args.plan_md), results_path, Path(args.output))
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
