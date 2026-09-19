from pathlib import Path

from task_check import run_checks
from _task_io import compute_move_link_rewrites


def task(root: Path, name: str, step: str, prose: str = ""):
    path = root / name / "task.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\ntitle: {name}\nstatus: in-progress\n---\n\n## Objective\n\n{prose}\n\n## Reproduction\n\n```yaml\nsteps:\n  - name: {step}\n    cmd: echo ok\n```\n")
    return path


def test_step_citations_check_owner_and_ignore_examples(tmp_path):
    root = tmp_path / "superRA"
    task(root, "data", "build-panel", "[same](#step-build-panel)")
    source = task(root, "report", "write-report", """
[valid](../data/task.md#step-build-panel)
[wrong owner](task.md#step-build-panel)
[missing step](../data/task.md#step-absent)
[missing task](../gone/task.md#step-build-panel)
`[example](../data/task.md#step-fake)`
```markdown
[example](../data/task.md#step-fake)
```
[external](https://example.com/task.md#step-fake)
""")
    findings = run_checks(root, "links")
    assert len(findings) == 3
    assert all(f.category == "links" and f.severity == "error" for f in findings)
    assert any("gone/task.md" in f.message for f in findings)
    assert any("'absent'" in f.message for f in findings)
    assert any("report/task.md" in f.message for f in findings)


def test_task_move_preserves_step_fragment(tmp_path):
    root = tmp_path / "superRA"
    old = task(root, "data", "build-panel")
    source = task(root, "report", "write-report", "[build](../data/task.md#step-build-panel)")
    rewrites = compute_move_link_rewrites(root, old.parent, root / "renamed", moved_root=old.parent)
    assert any("../renamed/task.md#step-build-panel" in text for text in rewrites.values())
