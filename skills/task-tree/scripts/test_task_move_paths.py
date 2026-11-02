"""`task move` re-points root-relative task paths in `## Reproduction` and project files."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import _task_io
import task_rename
from _repro import build_graph
from conftest import _write_task_md
from _task_validate import OUTPUT_CAP

OLD = "superRA/01-group/01-mover"
NEW = "superRA/02-other/01-mover"
OUT = f"{OLD}/attachments/out.csv"


@pytest.fixture
def project(tmp_path):
    """A tree whose moved task writes an attachment that a task elsewhere reads."""
    root = tmp_path / "superRA"
    (root / "01-group" / "01-mover" / "attachments").mkdir(parents=True)
    (root / "02-other").mkdir()
    (root / "03-reader").mkdir()
    _write_task_md(root / "task.md", "Root", "not-started")
    _write_task_md(root / "01-group" / "task.md", "Group", "not-started")
    _write_task_md(root / "02-other" / "task.md", "Other", "not-started")
    _write_task_md(
        root / "01-group" / "01-mover" / "task.md", "Mover", "not-started",
        reproduction=f"""
steps:
  - name: build  # keep this comment
    cmd: python {OLD}/attachments/build.py
    deps:
      - {OLD}/attachments/build.py
    outs:
      - "{OUT}"
""",
    )
    _write_task_md(
        root / "03-reader" / "task.md", "Reader", "not-started",
        reproduction=f"""
steps:
  - name: read
    cmd: python Code/read.py
    deps: [Code/read.py, "{OUT}"]
""",
    )
    (root / "01-group" / "01-mover" / "attachments" / "build.py").write_text(
        f"OUT = '{OUT}'\n", encoding="utf-8"
    )
    (tmp_path / "Code").mkdir()
    (tmp_path / "Code" / "read.py").write_text(f"ROOT / '{OUT}'\n", encoding="utf-8")
    return root


def track(root: Path) -> None:
    subprocess.run(["git", "init", "-q", str(root.parent)], check=True)
    subprocess.run(["git", "-C", str(root.parent), "add", "-A"], check=True)


def move(root: Path) -> None:
    task_rename.rename_task(root, "01-group/01-mover", "02-other/01-mover")


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_reproduction_paths_follow_the_task_across_the_tree(project):
    move(project)
    moved = text(project / "02-other" / "01-mover" / "task.md")
    assert f"cmd: python {NEW}/attachments/build.py" in moved
    assert f'- "{NEW}/attachments/out.csv"' in moved
    assert "name: build  # keep this comment" in moved
    assert OLD not in moved
    assert OLD not in text(project / "03-reader" / "task.md")

    graph = build_graph(project, env={})
    assert not [f for f in graph.findings if f.severity == "error"]
    assert ("build", "read", f"{NEW}/attachments/out.csv") in graph.step_edges


def test_tracked_sources_follow_the_task_and_evidence_does_not(project):
    top = project.parent
    (top / "repro-lock.json").write_text(f'{{"steps": {{"{OUT}": 1}}}}\n', encoding="utf-8")
    attachments = project / "01-group" / "01-mover" / "attachments"
    (attachments / "run.log").write_text(f"wrote {OUT}\n", encoding="utf-8")
    (attachments / "manifest.json").write_text(f'["{OUT}"]\n', encoding="utf-8")
    (project / "01-group" / "01-mover" / "comments.yaml").write_text(
        f"- body: see {OUT}\n", encoding="utf-8"
    )
    (top / "Makefile").write_text(f"all:\n\tpython {OLD}/run.py\n", encoding="utf-8")
    (top / ".gitignore").write_text(f"{OLD}/attachments/big.parquet\n", encoding="utf-8")
    (top / "README.md").write_text(f"[out]({OUT})\n", encoding="utf-8")
    track(project)
    (top / "Code" / "untracked.py").write_text(f"'{OUT}'\n", encoding="utf-8")

    move(project)

    moved = project / "02-other" / "01-mover"
    assert text(top / "Code" / "read.py") == f"ROOT / '{NEW}/attachments/out.csv'\n"
    assert text(moved / "attachments" / "build.py") == f"OUT = '{NEW}/attachments/out.csv'\n"
    assert OLD not in text(top / "Makefile")
    assert OLD not in text(top / ".gitignore")
    assert OLD not in text(top / "README.md")
    assert OLD in text(top / "repro-lock.json")
    assert OLD in text(moved / "attachments" / "run.log")
    assert OLD in text(moved / "attachments" / "manifest.json")
    assert OLD in text(moved / "comments.yaml")
    assert OLD in text(top / "Code" / "untracked.py")


@pytest.mark.parametrize("line", [
    f"{OLD}-v2/data.csv",
    f"{OLD}2/data.csv",
    f"{OLD}.md",
    f"x{OLD}/data.csv",
    f"my-{OLD}/data.csv",
    "01-group/01-mover/data.csv",  # not rooted at the task root
])
def test_a_path_that_only_resembles_the_task_stays(project, line):
    script = project.parent / "Code" / "other.py"
    script.write_text(f"{line}\n", encoding="utf-8")
    track(project)
    move(project)
    assert text(script) == f"{line}\n"


@pytest.mark.parametrize("before, after", [
    (f"'{OLD}'", f"'{NEW}'"),
    (f"{OLD}/", f"{NEW}/"),
    (f"$ROOT/{OLD}/x.csv", f"$ROOT/{NEW}/x.csv"),
    (f"../{OLD}/x.csv", f"../{NEW}/x.csv"),
    (f"./{OLD}/x.csv", f"./{NEW}/x.csv"),
    (f"lives in {OLD}.", f"lives in {NEW}."),
    (f"{OLD}/01-child/x.csv", f"{NEW}/01-child/x.csv"),
])
def test_each_spelling_of_the_task_path_moves(project, before, after):
    script = project.parent / "Code" / "other.py"
    script.write_text(f"{before}\n", encoding="utf-8")
    track(project)
    move(project)
    assert text(script) == f"{after}\n"


def test_a_rename_into_a_longer_slug_is_not_applied_twice(project):
    script = project.parent / "Code" / "other.py"
    script.write_text(f"{OLD}/x.csv\n", encoding="utf-8")
    track(project)
    task_rename.rename_task(project, "01-group/01-mover", "01-group/01-mover-v2")
    assert text(script) == f"{OLD}-v2/x.csv\n"


def test_a_failed_project_write_rolls_the_whole_move_back(project):
    script = project.parent / "Code" / "read.py"
    track(project)
    before = text(project / "03-reader" / "task.md")
    script.chmod(0o444)
    try:
        with pytest.raises(SystemExit):
            move(project)
    finally:
        script.chmod(0o644)
    assert (project / "01-group" / "01-mover" / "task.md").exists()
    assert not (project / "02-other" / "01-mover").exists()
    assert text(project / "03-reader" / "task.md") == before
    assert text(script) == f"ROOT / '{OUT}'\n"


def test_an_online_only_source_is_skipped_without_opening_it(project, monkeypatch):
    script = project.parent / "Code" / "read.py"
    track(project)
    monkeypatch.setattr(task_rename, "is_online_only", lambda path, _info: path == script)
    move(project)
    assert text(script) == f"ROOT / '{OUT}'\n"


def test_a_binary_source_is_left_alone(project):
    data = project.parent / "Code" / "blob.m"
    data.write_bytes(b"\xff\xfe" + OLD.encode())
    track(project)
    move(project)
    assert data.read_bytes() == b"\xff\xfe" + OLD.encode()


def test_outside_git_the_tree_moves_and_the_search_is_named(project, capsys):
    move(project)
    assert f"project files were not searched for {OLD}" in capsys.readouterr().out
    assert text(project.parent / "Code" / "read.py") == f"ROOT / '{OUT}'\n"
    assert OLD not in text(project / "03-reader" / "task.md")


def test_output_names_rewritten_files_and_stale_steps(project, capsys):
    track(project)
    move(project)
    out = capsys.readouterr().out
    assert "in 2 project file(s): Code/read.py," in out
    assert "leave 2 step(s) stale until rebuilt or accepted: build, read" in out


def test_output_stays_bounded(project, capsys):
    for index in range(OUTPUT_CAP + 3):
        (project.parent / "Code" / f"s{index}.py").write_text(f"'{OUT}'\n", encoding="utf-8")
    track(project)
    move(project)
    # The 13 scripts above, plus the fixture's Code/read.py and attachments/build.py.
    assert "and 5 more (`git diff --name-only` lists them)" in capsys.readouterr().out


def test_a_move_naming_no_paths_reports_none(tmp_path, capsys):
    root = tmp_path / "superRA"
    (root / "01-a").mkdir(parents=True)
    _write_task_md(root / "task.md", "Root", "not-started")
    _write_task_md(root / "01-a" / "task.md", "A", "not-started")
    track(root)
    task_rename.rename_task(root, "01-a", "01-b")
    out = capsys.readouterr().out
    assert "Rewrote" not in out
    assert "stale" not in out


def test_the_hook_rewrite_core_covers_reproduction_after_a_raw_rename(project):
    source = project / "01-group" / "01-mover"
    renamed = project / "01-group" / "01-renamed"
    source.rename(renamed)
    rewrites = _task_io.compute_move_link_rewrites(project, source, renamed, moved_root=renamed)
    _task_io.apply_move_link_rewrites(project, rewrites)
    assert OLD not in text(renamed / "task.md")
    assert "superRA/01-group/01-renamed/attachments/out.csv" in text(project / "03-reader" / "task.md")
