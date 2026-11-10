"""Tests for output cleaners and the fixed build date (_repro_normalize.py, `repro normalize`)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys

import pytest

import _repro_normalize
from _repro_normalize import SOURCE_DATE_EPOCH
from test_repro_runner import CONFIG, Project

needs_uv = pytest.mark.skipif(shutil.which("uv") is None, reason="the PDF cleaner runs through uv")

# A valid one-page PDF whose creation date and trailer ID change on every run,
# as a plotting library's would.
MKPDF = """\
import sys, time
stamp = str(time.time_ns()).encode()
content = b"0 0 m 100 100 l S"
objs = [b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 100 100] /Contents 4 0 R >>",
        b"<< /Length %d >>\\nstream\\n%s\\nendstream" % (len(content), content),
        b"<< /Title (Fig) /CreationDate (D:%s) /Producer (mkpdf) >>" % stamp[:14]]
out, offsets = b"%PDF-1.4\\n", []
for i, obj in enumerate(objs, 1):
    offsets.append(len(out))
    out += b"%d 0 obj\\n" % i + obj + b"\\nendobj\\n"
xref = len(out)
out += b"xref\\n0 %d\\n0000000000 65535 f \\n" % (len(objs) + 1)
out += b"".join(b"%010d 00000 n \\n" % o for o in offsets)
out += (b"trailer\\n<< /Size %d /Root 1 0 R /Info 5 0 R /ID [<%s><%s>] >>\\nstartxref\\n%d\\n%%%%EOF\\n"
        % (len(objs) + 1, stamp.hex().encode()[:32], stamp.hex().encode()[:32], xref))
open(sys.argv[1], "wb").write(out)
"""


def task(name: str, steps: str) -> str:
    return f"""\
---
title: "{name}"
status: not-started
depends_on: []
---

## Objective

{name}.

## Reproduction

```yaml
steps:
{steps}
```
"""


FIG = task("Fig", f"""\
  - name: make-fig
    cmd: mkdir -p output && {sys.executable} Code/mkpdf.py output/fig.pdf && date +%N > output/stamp.txt
    deps:
      - Code/mkpdf.py
    outs:
      - "${{OUT}}/fig.pdf"
      - "${{OUT}}/stamp.txt\"""")

USE = task("Use", """\
  - name: use-fig
    cmd: cat output/fig.pdf output/stamp.txt > output/use.bin
    deps:
      - "${OUT}/fig.pdf"
      - "${OUT}/stamp.txt"
    outs:
      - "${OUT}/use.bin\"""")

STRIP_DIGITS = '"*.txt": "tr -d 0-9 < {path} > {path}.tmp && mv {path}.tmp {path}"'


def configure(proj: Project, *normalize: str) -> None:
    proj.write("superRA/config.yaml", CONFIG + ("  normalize:\n" + "".join(f"    {n}\n" for n in normalize)
                                                if normalize else ""))


@pytest.fixture
def fig_project(tmp_path) -> Project:
    proj = Project(tmp_path / "figproj")
    configure(proj, STRIP_DIGITS)
    proj.write("superRA/01-fig/task.md", FIG)
    proj.write("superRA/02-use/task.md", USE)
    proj.write("Code/mkpdf.py", MKPDF)
    return proj


def fig_bytes(proj: Project) -> bytes:
    return (proj.root / "output" / "fig.pdf").read_bytes()


@needs_uv
def test_a_rerun_that_changes_nothing_visible_reproduces_its_bytes(fig_project):
    assert fig_project.run("build", ".") == 0
    first = fig_bytes(fig_project)
    assert b"mkpdf" not in first and b"CreationDate" not in first and b"/Title" in first
    before = fig_project.run_times()

    assert fig_project.run("build", "01-fig", "--force") == 0
    assert fig_bytes(fig_project) == first
    after = fig_project.run_times()
    assert after["make-fig"] != before["make-fig"]
    assert after["use-fig"] == before["use-fig"]
    assert fig_project.states(".") == {"make-fig": "fresh", "use-fig": "fresh"}


@needs_uv
def test_cleaning_a_direct_run_returns_its_step_to_fresh(fig_project):
    fig_project.run("build", ".")
    subprocess.run([sys.executable, "Code/mkpdf.py", "output/fig.pdf"], cwd=fig_project.root, check=True)
    assert fig_project.states(".")["make-fig"] == "stale"

    assert fig_project.run("normalize", str(fig_project.root / "output" / "fig.pdf")) == 0
    assert fig_project.states(".") == {"make-fig": "fresh", "use-fig": "fresh"}


@needs_uv
def test_normalize_by_target_cleans_the_steps_declared_outputs(fig_project, capsys):
    fig_project.run("build", ".")
    subprocess.run([sys.executable, "Code/mkpdf.py", "output/fig.pdf"], cwd=fig_project.root, check=True)
    capsys.readouterr()
    assert fig_project.run("normalize", "01-fig", "--json") == 0
    result = json.loads(capsys.readouterr().out)
    assert result["changed"] == ["${OUT}/fig.pdf"]
    assert result["unchanged"] == ["${OUT}/stamp.txt"]


def test_off_leaves_pdfs_as_written(fig_project):
    configure(fig_project, '"*.pdf": off')
    assert fig_project.run("build", "01-fig") == 0
    assert b"CreationDate" in fig_bytes(fig_project)


def test_star_off_turns_every_cleaner_off(fig_project):
    configure(fig_project, '"*": off', STRIP_DIGITS)
    assert fig_project.run("build", "01-fig") == 0
    assert b"CreationDate" in fig_bytes(fig_project)
    assert any(c.isdigit() for c in fig_project.read("output/stamp.txt"))


def test_a_project_command_cleans_matching_outputs(fig_project):
    configure(fig_project, '"*.pdf": off', STRIP_DIGITS)
    fig_project.run("build", ".")
    assert fig_project.read("output/stamp.txt") == "\n"
    before = fig_project.run_times()
    fig_project.run("build", "01-fig", "--force")
    assert fig_project.run_times()["use-fig"] == before["use-fig"]


def test_a_failing_project_command_fails_the_step(fig_project, capsys):
    configure(fig_project, '"*.pdf": off', '"stamp.txt": "test -z"')
    assert fig_project.run("build", "01-fig") == 1
    out = capsys.readouterr().out
    assert "exited 1 on ${OUT}/stamp.txt" in out
    assert fig_project.states("01-fig")["make-fig"] != "fresh"


def test_cleaners_reach_files_inside_a_directory_output(tmp_path):
    proj = Project(tmp_path / "dirproj")
    configure(proj, '"*.txt": "tr -d 0-9 < {path} > {path}.tmp && mv {path}.tmp {path}"')
    proj.write("superRA/01-gen/task.md", task("Gen", """\
  - name: gen
    cmd: mkdir -p output/parts && date +%N > output/parts/a.txt
    outs:
      - "${OUT}/parts\""""))
    assert proj.run("build", ".") == 0
    assert proj.read("output/parts/a.txt") == "\n"


def test_a_missing_uv_warns_and_keeps_the_step(fig_project, monkeypatch, capsys):
    monkeypatch.setattr(_repro_normalize.shutil, "which", lambda name: None)
    assert fig_project.run("build", "01-fig") == 0
    assert "1 output(s) left as written (uv not found" in capsys.readouterr().out
    assert b"CreationDate" in fig_bytes(fig_project)
    assert fig_project.states("01-fig")["make-fig"] == "fresh"


@needs_uv
@pytest.mark.skipif(shutil.which("qpdf") is None, reason="encrypting the fixture needs qpdf")
def test_an_encrypted_pdf_is_left_as_written(fig_project, capsys):
    fig_project.write("Code/mkpdf.py", MKPDF + "import subprocess; subprocess.run(['qpdf', '--encrypt', 'u', 'o', '256', "
                      "'--', '--replace-input', sys.argv[1]], check=True)\n")
    assert fig_project.run("build", "01-fig") == 0
    assert "1 output(s) left as written (encrypted)" in capsys.readouterr().out


def test_steps_see_a_fixed_build_date_unless_one_is_set(fig_project, monkeypatch):
    fig_project.write("superRA/03-date/task.md", task("Date", """\
  - name: date
    cmd: mkdir -p output && echo $SOURCE_DATE_EPOCH > output/date.txt
    outs:
      - "${OUT}/date.txt\""""))
    configure(fig_project)
    monkeypatch.delenv("SOURCE_DATE_EPOCH", raising=False)
    fig_project.run("build", "03-date")
    assert fig_project.read("output/date.txt") == f"{SOURCE_DATE_EPOCH}\n"

    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1700000000")
    fig_project.run("build", "03-date", "--force")
    assert fig_project.read("output/date.txt") == "1700000000\n"


def test_an_unknown_builtin_is_a_config_error(fig_project):
    configure(fig_project, '"*.png": builtin:png')
    messages = [f.message for f in fig_project.graph().findings if f.severity == "error"]
    assert any("unknown cleaner 'builtin:png'" in m for m in messages)


def test_normalize_never_downloads_an_online_only_file(fig_project, monkeypatch, capsys):
    fig_project.write("output/fig.pdf", "placeholder")
    monkeypatch.setattr(_repro_normalize, "_online_only", lambda path: True)
    assert fig_project.run("normalize", str(fig_project.root / "output" / "fig.pdf")) == 0
    assert "online-only; download to clean" in capsys.readouterr().err
    assert fig_project.read("output/fig.pdf") == "placeholder"


def test_normalize_by_path_matches_globs_on_the_declared_path(fig_project, tmp_path):
    outside = tmp_path / "ext"
    configure(fig_project, '"*.pdf": off', '"${EXT}/*.txt": "tr -d 0-9 < {path} > {path}.tmp && mv {path}.tmp {path}"')
    fig_project.write("superRA/config.yaml", fig_project.read("superRA/config.yaml").replace(
        "    OUT: output\n", f"    OUT: output\n    EXT: {outside}\n"))
    fig_project.write("superRA/03-ext/task.md", task("Ext", f"""\
  - name: ext
    cmd: mkdir -p {outside} && date +%N > {outside}/n.txt
    outs:
      - "${{EXT}}/n.txt\""""))
    assert fig_project.run("build", "03-ext") == 0
    assert (outside / "n.txt").read_text() == "\n"
    subprocess.run(f"date +%N > {outside}/n.txt", shell=True, check=True)
    assert fig_project.states("03-ext")["ext"] == "stale"

    assert fig_project.run("normalize", str(outside / "n.txt")) == 0
    assert fig_project.states("03-ext")["ext"] == "fresh"

    subprocess.run(f"date +%N > {outside}/n.txt", shell=True, check=True)
    assert fig_project.run("normalize", str(outside)) == 0  # a directory holding the out
    assert fig_project.states("03-ext")["ext"] == "fresh"


def test_normalize_reports_a_running_build_without_a_traceback(fig_project, monkeypatch, capsys):
    import repro_run
    from contextlib import contextmanager

    @contextmanager
    def held(paths):
        raise repro_run.ReproStateError("another build holds the runner lock")
        yield
    monkeypatch.setattr(repro_run, "mutation_lock", held)
    fig_project.write("output/stamp.txt", "1\n")
    assert fig_project.run("normalize", str(fig_project.root / "output" / "stamp.txt")) == 1
    assert "Error: another build holds the runner lock" in capsys.readouterr().err


def test_normalize_refuses_an_invalid_config(fig_project, capsys):
    configure(fig_project, '"*.txt": builtin:txt')
    fig_project.write("output/stamp.txt", "1\n")
    assert fig_project.run("normalize", str(fig_project.root / "output" / "stamp.txt")) == 1
    assert "unknown cleaner 'builtin:txt'" in capsys.readouterr().err


@needs_uv
def test_a_malformed_xmp_packet_skips_one_file_not_the_batch(tmp_path):
    good, bad = tmp_path / "good.pdf", tmp_path / "bad.pdf"
    for path in (good, bad):
        subprocess.run([sys.executable, "-c", MKPDF, str(path)], check=True)
    script = _repro_normalize.BUILTINS["builtin:pdf"]
    # Give bad.pdf a /Metadata stream that is not XML, through the cleaner's own pikepdf.
    subprocess.run(["uv", "run", "-q", "--no-project", "--with", "pikepdf==10.13.0.post1", "python", "-c",
                    "import pikepdf, sys; pdf = pikepdf.open(sys.argv[1], allow_overwriting_input=True); "
                    "pdf.Root.Metadata = pdf.make_stream(b'<not xml'); pdf.save(sys.argv[1], fix_metadata_version=False)", str(bad)], check=True)
    result = subprocess.run(["uv", "run", "-q", "--script", str(script), "--json", str(bad), str(good)],
                            check=True, capture_output=True, text=True)
    records = {r["path"]: r for r in json.loads(result.stdout)}
    assert records[str(bad)] == {"path": str(bad), "result": "skipped", "reason": "malformed XMP metadata"}
    assert records[str(good)]["result"] == "normalized"
