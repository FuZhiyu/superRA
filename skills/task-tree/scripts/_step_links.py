"""Validate Markdown citations of named reproduction steps."""

from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from _task_io import _iter_contained_markdown, _MARKDOWN_LINK_RE
from _task_validate import Finding


def check_step_links(plan_root: Path, graph) -> list[Finding]:
    root = plan_root.resolve()
    owners = {}
    for step in [*graph.steps, *graph.archived_steps]:
        owners.setdefault((root / step.task_path / "task.md").resolve(), set()).add(step.name)
    findings = []
    for source in _iter_contained_markdown(root, root):
        fence = None
        for number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
            marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
            if marker:
                value = marker.group(1)
                if fence is None:
                    fence = value
                elif value[0] == fence[0] and len(value) >= len(fence):
                    fence = None
                continue
            if fence:
                continue
            line = re.sub(r"(`+).*?\1", "", line)
            for match in _MARKDOWN_LINK_RE.finditer(line):
                if match.group(1).startswith("!"):
                    continue
                target = match.group(2).strip("<>")
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc or not parsed.fragment.startswith("step-"):
                    continue
                path = unquote(parsed.path)
                destination = (source.parent / path).resolve() if path else source.resolve()
                if destination.name != "task.md" or not destination.is_relative_to(root):
                    continue
                name = unquote(parsed.fragment[5:])
                if name not in owners.get(destination, set()):
                    findings.append(Finding(
                        task_path=source.parent.relative_to(root).as_posix(),
                        category="links", severity="error",
                        message=f"{source.name}:{number}: step {name!r} is not declared in {destination.relative_to(root)}",
                    ))
    return findings
