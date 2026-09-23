"""`repro explain` provenance: the two-clone staleness case from the 2026-09-23 report.

Clone A is the coauthor who builds and commits `pytask.lock`; clone B shares
`output/` through a simulated Dropbox that lags. Each stale step in B has a
different true cause, and `explain` must name it with a runnable next command.
"""
from __future__ import annotations

import json
import shutil
import subprocess

import pytest

from test_repro_runner import CHAIN, CONFIG, Project, needs_pytask, project  # noqa: F401


def _task(title, steps):
    return f"""---
title: "{title}"
status: not-started
depends_on: []
---

## Objective

{title}.

## Reproduction

```yaml
steps:
{steps}```
"""


def _step(name, script, deps=(), outs=(), kind=None):
    lines = [f"  - name: {name}"]
    if kind:
        lines.append(f"    kind: {kind}")
    lines.append(f"    cmd: {script}")
    lines.append("    deps:")
    lines += [f'      - "{d}"' for d in deps]
    if outs:
        lines.append("    outs:")
        lines += [f'      - "{o}"' for o in outs]
    return "\n".join(lines) + "\n"


TASKS = {
    "01-est": _step("est", "sh Code/est.sh", ["Code/est.sh"], ["${OUT}/est.txt"]),
    "02-paper": _step("paper", "sh Code/paper.sh", ["Code/paper.sh", "${OUT}/est.txt"], ["${OUT}/paper.txt"])
    + _step("check-paper", "test -s output/paper.txt", ["${OUT}/paper.txt"], kind="check"),
    "03-figure": _step("figure", "sh Code/figure.sh", ["Code/figure.sh", "Code/style.py"], ["${OUT}/figure.txt"]),
    "04-panel": _step("panel", "sh Code/panel.sh", ["Code/panel.sh"], ["${OUT}/panel.txt"]),
    "05-robust": _step("robust", "sh Code/robust.sh", ["Code/robust.sh"], ["${OUT}/robust.txt"]),
    "06-noise": _step("noise", "sh Code/noise.sh", ["Code/noise.sh"], ["${OUT}/noise.txt"]),
}

STYLE = '"""Plot style.\n\nShared colors for every figure.\n"""\nCOLOR = "navy"\n'


def git(root, *args, author="Co Author"):
    return subprocess.run(
        ["git", "-c", f"user.name={author}", "-c", "user.email=a@example.com",
         "-c", "commit.gpgsign=false", "-c", "init.defaultBranch=main", *args],
        cwd=root, check=True, capture_output=True, text=True,
    ).stdout.strip()


def head(root):
    return git(root, "rev-parse", "--short", "HEAD")


def emit(name, value):
    return f"mkdir -p output\necho {value} > output/{name}.txt\n"


@pytest.fixture
def clones(tmp_path):
    a = Project(tmp_path / "a")
    a.write("superRA/config.yaml", CONFIG)
    for task, steps in TASKS.items():
        a.write(f"superRA/{task}/task.md", _task(task, steps))
    for name in ("est", "panel", "robust", "noise"):
        a.write(f"Code/{name}.sh", emit(name, "v1"))
    a.write("Code/paper.sh", "cat output/est.txt > output/paper.txt\n")
    a.write("Code/figure.sh", "mkdir -p output\ncat Code/style.py > /dev/null\necho fig > output/figure.txt\n")
    a.write("Code/style.py", STYLE)
    a.write(".gitignore", "output/\n.superra-repro/\n")
    git(a.root, "init", "-q")
    git(a.root, "add", "-A")
    git(a.root, "commit", "-qm", "code")
    assert a.run("build", ".") == 0
    git(a.root, "add", "pytask.lock")
    git(a.root, "commit", "-qm", "first build")
    first = head(a.root)

    git(tmp_path, "clone", "-q", str(a.root), str(tmp_path / "b"))
    b = Project(tmp_path / "b")
    shutil.copytree(a.root / "output", b.root / "output")  # Dropbox syncs the first build
    return a, b, first


def explain(project, capsys, *argv):
    capsys.readouterr()
    code = project.run("explain", *argv)
    out = capsys.readouterr().out
    assert code == 0, out
    return out


@needs_pytask
def test_explain_names_each_cause_across_two_clones(clones, capsys):
    a, b, first = clones

    # A check passed only in the other clone: non-fresh, with the lock revision named.
    states = {e.step.name: e for e in b.status(".").reported}
    assert states["check-paper"].status == "missing"
    assert states["check-paper"].reason == f"passed at these inputs in lock {first}; not run here"
    out = explain(b, capsys, "02-paper#check-paper")
    assert "check passed elsewhere, not run here" in out
    assert f"passed at lock {first} (Co Author," in out
    assert "next: superra repro build '02-paper#check-paper'" in out

    # Coauthor: rebuild est, edit a docstring, build panel on a merged side branch, rebuild robust.
    a.write("Code/est.sh", emit("est", "v2"))
    assert a.run("build", ".") == 0
    git(a.root, "commit", "-qam", "rebuild est")
    rebuilt = head(a.root)
    a.write("Code/style.py", STYLE.replace("Shared colors", "Shared colours"))
    git(a.root, "commit", "-qam", "docstring")
    docstring = head(a.root)
    git(a.root, "checkout", "-qb", "side")
    a.write("Code/panel.sh", emit("panel", "v2"))
    assert a.run("build", "04-panel") == 0
    git(a.root, "commit", "-qam", "panel on side")
    side = head(a.root)
    git(a.root, "checkout", "-q", "main")
    git(a.root, "merge", "-q", "--no-ff", "side", "-m", "merge side")
    merge = head(a.root)
    a.write("Code/robust.sh", emit("robust", "v2"))
    assert a.run("build", "05-robust") == 0
    git(a.root, "commit", "-qam", "rebuild robust")

    # B pulls code and lock; no output has synced yet.
    git(b.root, "pull", "-q", "--no-rebase")
    b.write("output/noise.txt", "hand edited\n")

    out = explain(b, capsys, "01-est")
    assert out.startswith("01-est: 1 of 1 step(s) not fresh")
    assert "older build synced here — the newer build recorded in the lock has not synced here yet" in out
    assert f"recorded lock {rebuilt} (Co Author," in out and f"current superseded lock {first} (Co Author," in out
    assert "next: superra repro status '01-est#est'" in out
    assert f"searched: receipts in .superra-repro/baselines; acceptance ledger repro-acceptance.json; pytask.lock at 5 revision(s)" in out
    assert "on local branch(es) main; HEAD is main" in out

    out = explain(b, capsys, "02-paper")
    assert out.startswith("02-paper: 2 of 2 step(s) not fresh")
    assert "next: superra repro status '02-paper#paper' '02-paper#check-paper'" in out
    assert out.count("older build synced here") == 1  # one group across both steps

    out = explain(b, capsys, "figure")  # a unique bare step name
    assert f"dependency edited in commit {docstring}" in out
    assert "Code/style.py" in out and "1 file changed, 1 insertion(+), 1 deletion(-)" in out
    assert "-Shared colors for every figure." in out and "+Shared colours for every figure." in out
    code_commit = git(b.root, "log", "--format=%h", "--reverse").split()[0]
    assert f"git {code_commit} → {docstring}" in out
    assert f"next: git diff {code_commit} {docstring} -- Code/style.py" in out
    assert "git history of Code/style.py (2 revision(s))" in out

    out = explain(b, capsys, "04-panel#panel")
    assert "recorded build from another branch" in out
    assert f"recorded lock {side} (Co Author," in out and f"via merge {merge}" in out
    assert "next: superra repro build '04-panel#panel'" in out

    out = explain(b, capsys, "06-noise")
    assert "no known source" in out and "current no known source" in out
    assert "next: superra repro build '06-noise#noise'" in out

    # A file target: its provenance, producer, and readers.
    out = explain(b, capsys, "output/est.txt")
    assert out.startswith(f"output/est.txt  now ")
    assert f"matches superseded lock {first}" in out
    assert "produced by 01-est#est" in out and "read by 02-paper#paper" in out
    assert "older build synced here" in out

    # JSON: full hashes, the same rows, and a closed cause key.
    capsys.readouterr()
    assert b.run("explain", "01-est#est", "--json") == 0
    data = json.loads(capsys.readouterr().out)
    row = data["rows"][0]
    assert row["cause"] == "older-build" and len(row["recorded"]) == 64
    assert data["groups"][0]["command"] == "superra repro status '01-est#est'"
    assert first in data["searched"]["lock_revisions"]

    # The recorded bytes sitting in a Dropbox conflicted copy.
    shutil.copy(a.root / "output/est.txt", b.root / "output/est (Co Author's conflicted copy 2026-09-23).txt")
    out = explain(b, capsys, "01-est#est")
    assert "recorded bytes in a Dropbox conflicted copy" in out
    assert "next: ls -l output/est.txt 'output/est (Co Author'\"'\"'s conflicted copy 2026-09-23).txt'" in out
    assert "conflicted copies beside output/est.txt" in out

    # §4: accept the older bytes, then the locked build syncs in.
    assert b.run("accept", "05-robust", "--reason", "older build reviewed") == 0
    assert b.states("05-robust") == {"robust": "fresh"}
    shutil.copy(a.root / "output/robust.txt", b.root / "output/robust.txt")
    robust = b.status("05-robust").entry("robust")
    assert robust.status == "fresh"
    assert "acceptance no longer valid (reviewed state changed)" in robust.reason
    assert "superra repro revoke '05-robust#robust'" in robust.reason
    b.write("output/robust.txt", "third bytes\n")
    out = explain(b, capsys, "05-robust#robust")
    assert "reviewed bytes replaced" in out and "recorded reviewed " in out
    assert "next: superra repro accept '05-robust#robust' --dry-run" in out

    # An uncommitted edit to a tracked dependency.
    b.write("Code/style.py", STYLE + "# local\n")
    out = explain(b, capsys, "03-figure#figure")
    assert "dependency edited, not committed" in out
    assert f"git {code_commit} → working copy" in out
    assert f"next: git diff {code_commit} -- Code/style.py" in out


@needs_pytask
def test_bare_names_stay_rejected_for_build_accept_and_revoke(clones, capsys):
    _, b, _ = clones
    for command in (["build", "est"], ["accept", "est", "--reason", "x"], ["revoke", "est"]):
        capsys.readouterr()
        assert b.run(*command) == 1
        assert "'01-est#est'" in capsys.readouterr().err


@needs_pytask
def test_lock_index_is_cached_per_revision(clones, capsys):
    _, b, first = clones
    explain(b, capsys, "01-est")
    full = git(b.root, "rev-parse", first)
    assert (b.paths.state_dir / "lock-index" / f"{full}.json").is_file()


@needs_pytask
def test_check_stamp_lost_outside_git_names_the_working_lock(project):
    assert project.run("build", *CHAIN) == 0
    shutil.rmtree(project.paths.stamps_dir)
    check = project.status(*CHAIN).entry("check-b")
    assert (check.status, check.reason) == ("missing", "passed at these inputs in the working lock; not run here")
    project.write("output/b.txt", "changed\n")
    assert project.status(*CHAIN).entry("check-b").reason == "output .superra-repro/stamps/check-b.stamp is missing"


@needs_pytask
def test_upstream_and_definition_causes_without_git(project, capsys):
    assert project.run("build", *CHAIN) == 0
    project.write("superRA/01-a/task.md", project.read("superRA/01-a/task.md").replace("sh Code/a.sh", "sh Code/a.sh && true"))
    out = explain(project, capsys, "02-b#build-b")
    assert "upstream step not fresh" in out and "upstream step 'build-a' is stale" in out
    assert "next: superra repro explain '01-a#build-a'" in out
    out = explain(project, capsys, "01-a")
    assert "step definition changed" in out
    assert "next: git diff -- superRA/01-a/task.md superRA/config.yaml" in out
    assert "no git history (not a git checkout)" in out
