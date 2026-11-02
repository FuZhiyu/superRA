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
    f"../other-project/{OLD}/x.csv",
    f"/abs/other-repo/{OLD}/x.csv",
    f"https://github.com/org/repo/blob/main/{OLD}/x.py",
    f"p2/{OLD}/x.csv",
    f"$ROOT/other/{OLD}/x.csv",
    f"https://dash.example/view?task={OLD}",
    f"https://dash.example/#{OLD}",
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
    (f"[out]({OLD}/x.csv)", f"[out]({NEW}/x.csv)"),
    (f"[out](../{OLD}/x.csv)", f"[out](../{NEW}/x.csv)"),
    (f"${{ROOT}}/{OLD}/x.csv", f"${{ROOT}}/{NEW}/x.csv"),
    (f'f"{{ROOT}}/{OLD}/x.csv"', f'f"{{ROOT}}/{NEW}/x.csv"'),
    (f"$(git rev-parse --show-toplevel)/{OLD}", f"$(git rev-parse --show-toplevel)/{NEW}"),
    (f'"$(@__DIR__)/../{OLD}/x.csv"', f'"$(@__DIR__)/../{NEW}/x.csv"'),
    (f"--out={OLD}/x.csv", f"--out={NEW}/x.csv"),
    (f"\\input{{{OLD}/t.tex}}", f"\\input{{{NEW}/t.tex}}"),
    (f"\\includegraphics[width=2cm]{{{OLD}/f.pdf}}", f"\\includegraphics[width=2cm]{{{NEW}/f.pdf}}"),
    (f"\\input{{../{OLD}/t.tex}}", f"\\input{{../{NEW}/t.tex}}"),
    (f"\\graphicspath{{{{../{OLD}/}}}}", f"\\graphicspath{{{{../{NEW}/}}}}"),
    (f"read({OLD}/x.csv)", f"read({NEW}/x.csv)"),
    (f"/{OLD}/big/", f"/{NEW}/big/"),
])
def test_each_spelling_of_the_task_path_moves(project, before, after):
    script = project.parent / "Code" / "other.py"
    script.write_text(f"{before}\n", encoding="utf-8")
    track(project)
    move(project)
    assert text(script) == f"{after}\n"


def test_an_absolute_path_into_this_project_moves(project):
    script = project.parent / "Code" / "other.py"
    script.write_text(f"'{project.parent.resolve()}/{OLD}/x.csv'\n", encoding="utf-8")
    track(project)
    move(project)
    assert text(script) == f"'{project.parent.resolve()}/{NEW}/x.csv'\n"


def test_a_relative_path_resolving_elsewhere_stays(project):
    script = project.parent / "Code" / "deep" / "other.py"
    script.parent.mkdir()
    script.write_text(f"../{OLD}/x.csv\n", encoding="utf-8")  # names Code/superRA/...
    track(project)
    move(project)
    assert text(script) == f"../{OLD}/x.csv\n"


def test_another_project_in_the_repo_is_left_alone(tmp_path):
    def tree(name):
        root = tmp_path / name / "superRA"
        (root / "data").mkdir(parents=True)
        (root / "grp").mkdir()
        _write_task_md(root / "task.md", "Root", "not-started")
        _write_task_md(root / "grp" / "task.md", "Grp", "not-started")
        _write_task_md(root / "data" / "task.md", "Data", "not-started",
                       objective="Reads superRA/data/in.csv.")
        code = root.parent / "Code"
        code.mkdir()
        (code / "run.py").write_text("'superRA/data/in.csv'\n", encoding="utf-8")
        return root

    ours, theirs = tree("p1"), tree("p2")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "add", "-A"], check=True)
    task_rename.rename_task(ours, "data", "grp/data")
    assert text(ours.parent / "Code" / "run.py") == "'superRA/grp/data/in.csv'\n"
    assert text(theirs.parent / "Code" / "run.py") == "'superRA/data/in.csv'\n"
    assert "superRA/data/in.csv" in text(theirs / "data" / "task.md")


def test_a_directory_named_like_the_task_root_is_not_a_project(project):
    helper = project.parent / "Code" / "superRA" / "h.py"
    helper.parent.mkdir()
    helper.write_text("HELPER = 1\n", encoding="utf-8")
    track(project)
    move(project)
    assert text(project.parent / "Code" / "read.py") == f"ROOT / '{NEW}/attachments/out.csv'\n"


def test_a_repo_inside_a_directory_named_like_the_task_root_is_swept(tmp_path):
    outer = tmp_path / "superRA" / "repo"
    root = outer / "superRA"
    (root / "data").mkdir(parents=True)
    (root / "grp").mkdir()
    _write_task_md(root / "task.md", "Root", "not-started")
    _write_task_md(root / "data" / "task.md", "Data", "not-started")
    _write_task_md(root / "grp" / "task.md", "Grp", "not-started")
    (outer / "shared").mkdir()
    (outer / "shared" / "x.py").write_text("'superRA/data/in.csv'\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(outer)], check=True)
    subprocess.run(["git", "-C", str(outer), "add", "-A"], check=True)
    task_rename.rename_task(root, "data", "grp/data")
    assert text(outer / "shared" / "x.py") == "'superRA/grp/data/in.csv'\n"


def test_a_citation_the_move_cannot_resolve_is_named(project, capsys):
    script = project.parent / "Code" / "deep.py"
    script.write_text(f"cd_relative = '../../{OLD}/x.csv'\n", encoding="utf-8")
    track(project)
    move(project)
    assert text(script) == f"cd_relative = '../../{OLD}/x.csv'\n"
    out = capsys.readouterr().out
    assert f"Left {OLD} in 1 file(s), where it leads elsewhere or could not be resolved: Code/deep.py" in out


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


def test_an_online_only_source_is_skipped_without_opening_it(project, monkeypatch, capsys):
    script = project.parent / "Code" / "read.py"
    track(project)
    monkeypatch.setattr(task_rename, "is_online_only", lambda path, _info: path.resolve() == script.resolve())
    move(project)
    assert text(script) == f"ROOT / '{OUT}'\n"
    assert f"1 tracked source file(s) are online-only or not UTF-8, so search them by hand for {OLD}" in capsys.readouterr().out


def test_an_online_only_tree_markdown_file_is_not_named_for_a_hand_search(project, monkeypatch, capsys):
    track(project)
    monkeypatch.setattr(task_rename, "is_online_only", lambda path, _info: path.name == "task.md")
    move(project)
    assert "online-only" not in capsys.readouterr().out


def test_a_source_that_is_not_utf8_is_left_alone_and_named(project, capsys):
    data = project.parent / "Code" / "blob.m"
    data.write_bytes(b"\xff\xfe" + OLD.encode())
    other = project.parent / "Code" / "unrelated.m"
    other.write_bytes(b"\xff\xfe")
    track(project)
    move(project)
    assert data.read_bytes() == b"\xff\xfe" + OLD.encode()
    assert "1 tracked source file(s) are online-only or not UTF-8" in capsys.readouterr().out


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
    assert "changed 2 step(s), so they and anything downstream read stale" in out
    assert out.rstrip().endswith("build, read")


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


def test_a_moved_files_own_prefix_follows_a_change_of_depth(project):
    mover = project / "01-group" / "01-mover"
    (mover / "attachments" / "use.py").write_text(
        f"A = '../../../../{OLD}/attachments/x.csv'\nB = 'other/../{OLD}/y.csv'\n",
        encoding="utf-8",
    )
    with (mover / "task.md").open("a", encoding="utf-8") as handle:
        handle.write(f"\nSee ../../../{OLD}/attachments/x.csv\n")
    track(project)

    task_rename.rename_task(project, "01-group/01-mover", "01-mover")

    moved = project / "01-mover"
    assert "See ../../superRA/01-mover/attachments/x.csv" in text(moved / "task.md")
    assert text(moved / "attachments" / "use.py").splitlines()[0] == (
        "A = '../../../superRA/01-mover/attachments/x.csv'"
    )
    assert (moved / ".." / ".." / "superRA" / "01-mover" / "attachments").resolve() == (
        moved / "attachments"
    ).resolve()


def test_a_dot_prefix_is_rebuilt_and_a_mixed_one_is_named(project, capsys):
    mover = project / "01-group" / "01-mover"
    (mover / "attachments" / "use.py").write_text(
        f"A = './../../../../{OLD}/a.csv'\nB = 'x/../../../../../{OLD}/b.csv'\n",
        encoding="utf-8",
    )
    track(project)

    task_rename.rename_task(project, "01-group/01-mover", "01-mover")

    moved = project / "01-mover" / "attachments" / "use.py"
    lines = text(moved).splitlines()
    assert lines[0] == "A = '../../../superRA/01-mover/a.csv'"
    assert lines[1] == "B = 'x/../../../../../superRA/01-mover/b.csv'"
    left = [line for line in capsys.readouterr().out.splitlines() if "Left " in line]
    assert left and "01-mover/attachments/use.py" in left[0]
    assert "01-mover/attachments/build.py" not in left[0]
