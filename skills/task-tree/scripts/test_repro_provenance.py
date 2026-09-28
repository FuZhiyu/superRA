"""`repro explain` provenance: the two-clone staleness case from the 2026-09-23 report.

Clone A is the coauthor who builds and commits `repro-lock.json`; clone B shares
`output/` through a simulated Dropbox that lags. Each stale step in B has a
different true cause, and `explain` must name it with a runnable next command.
"""
from __future__ import annotations

import json
import shlex
import shutil
import subprocess

import pytest

import repro_run
from _repro_builds import platform_name
from test_repro_runner import CHAIN, CONFIG, Project, project  # noqa: F401


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
    git(a.root, "add", "repro-lock.json")
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
    parser = repro_run.build_parser()
    for line in out.splitlines():
        command = line.strip().removeprefix("next: ")
        if line.strip().startswith("next: superra repro "):
            parser.parse_args(shlex.split(command)[2:])  # every pointer parses as printed
    return out


def test_explain_names_each_cause_across_two_clones(clones, capsys):
    a, b, first = clones

    # A check passed only in the other clone: fresh on the lock's word, naming the revision and that it did not run here.
    reason = f"passed at these inputs in lock {first} on {platform_name()}; not run here"
    assert b.status(".").entry("check-paper").status == "fresh"
    assert b.status(".").entry("check-paper").reason == reason
    out = explain(b, capsys, "02-paper#check-paper")
    assert f"check-paper  [fresh]  {reason}" in out
    assert "input-changed" not in out and "other-build" not in out

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
    a.write("Code/robust.sh", emit("robust", "v2"))
    assert a.run("build", "05-robust") == 0
    git(a.root, "commit", "-qam", "rebuild robust")

    # B pulls code and lock; no output has synced yet.
    git(b.root, "pull", "-q", "--no-rebase")
    b.write("output/noise.txt", "hand edited\n")

    # Sync lag: the output holds the older build; source facts, no inferred direction.
    out = explain(b, capsys, "01-est")
    assert out.startswith("01-est: 1 of 1 step(s) not fresh")
    assert "other-build — the output holds bytes from another recorded build" in out
    assert f"recorded lock {rebuilt} (Co Author," in out and "; in HEAD's lock, entries est, paper)" in out
    assert f"current lock {first} (Co Author," in out and "; earlier commit, 5 behind HEAD)" in out
    assert f"next: git show --stat {first}" in out
    body = out.split("searched:")[0]
    assert "synced" not in body and "branch" not in body
    assert "searched: receipts in .superra-repro/baselines; acceptance ledger repro-acceptance.json; the lock at 5 revision(s) on local and remote-tracking branches and HEAD" in out

    # The consumer's dependency is an input; its output and the check's input follow the same roles.
    out = explain(b, capsys, "02-paper")
    assert out.startswith("02-paper: 2 of 2 step(s) not fresh")
    assert "input-changed — an input or the step definition differs from the last build" in out
    assert "next: superra repro explain '01-est#est'\n" in out and "next: superra repro explain '02-paper#paper'\n" in out
    assert "other-build" in out and f"next: git show --stat {first}" in out

    # A docstring edit to a tracked dependency.
    out = explain(b, capsys, "figure")  # a unique bare step name
    code_commit = git(b.root, "log", "--format=%h", "--reverse").split()[0]
    assert f"recorded git {code_commit}; current git {docstring}; 1 file changed, 1 insertion(+), 1 deletion(-)" in out
    assert "-Shared colors for every figure." in out and "+Shared colours for every figure." in out
    assert f"next: git diff {code_commit} {docstring} -- Code/style.py" in out
    assert "git history of Code/style.py (2 revision(s))" in out

    # A lock hash from a merged side branch: stated as a revision in HEAD's lock, no branch story.
    out = explain(b, capsys, "04-panel#panel")
    assert "other-build" in out
    assert f"recorded lock {side} (Co Author," in out and "; in HEAD's lock, entry panel)" in out
    assert f"current lock {first} (Co Author," in out
    assert "branch" not in out.split("searched:")[0] and "merge" not in out

    out = explain(b, capsys, "06-noise")
    assert "unknown-output — the output matches no recorded build" in out
    assert "current no known source" in out
    assert "next: superra repro explain output/noise.txt --json" in out

    # A file target: its provenance, producer, and readers.
    out = explain(b, capsys, "output/est.txt")
    assert out.startswith("output/est.txt  now ")
    assert f"lock {first} (Co Author," in out.splitlines()[0]
    assert "produced by 01-est#est" in out and "read by 02-paper#paper" in out
    assert "other-build" in out  # the reader records the same hash, so one row

    # JSON: full hashes, the same rows, and a closed cause key.
    capsys.readouterr()
    assert b.run("explain", "01-est#est", "--json") == 0
    data = json.loads(capsys.readouterr().out)
    row = data["rows"][0]
    assert row["cause"] == "other-build" and len(row["recorded"]) == 64
    assert row["current_sources"][0]["source"] == "lock" and row["current_sources"][0]["head"] is False
    assert row["current_sources"][0]["behind"] == 5 and row["current_sources"][0]["branches"] == []
    assert data["groups"][0]["commands"] == [f"git show --stat {first}"]
    assert first in data["searched"]["lock_revisions"]

    # The recorded bytes sitting in a Dropbox conflicted copy: a source fact.
    shutil.copy(a.root / "output/est.txt", b.root / "output/est (Co Author's conflicted copy 2026-09-23).txt")
    out = explain(b, capsys, "01-est#est")
    assert "also in conflicted copy output/est (Co Author's conflicted copy 2026-09-23).txt" in out
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
    assert "unknown-output" in out and "recorded reviewed " in out

    # An uncommitted edit to a tracked dependency.
    b.write("Code/style.py", STYLE + "# local\n")
    out = explain(b, capsys, "03-figure#figure")
    assert f"recorded git {code_commit}; current uncommitted" in out
    assert f"next: git diff {code_commit} -- Code/style.py" in out

    # Review finding: producer rebuilt and synced, consumer not rebuilt, in both clones.
    a.write("Code/est.sh", emit("est", "v3"))
    assert a.run("build", "01-est") == 0
    git(a.root, "commit", "-qam", "rebuild est only")
    producer = head(a.root)
    git(b.root, "pull", "-q", "--no-rebase")
    (b.root / "output/est (Co Author's conflicted copy 2026-09-23).txt").unlink()
    shutil.copy(a.root / "output/est.txt", b.root / "output/est.txt")
    for clone in (a, b):
        out = explain(clone, capsys, "02-paper#paper")
        dep = next(line for line in out.splitlines() if "dependency ${OUT}/est.txt" in line and "→" in line)
        assert f"current lock {producer} (Co Author," in dep and "; in HEAD's lock, entry est)" in dep
        assert "; in HEAD's lock, entry paper)" in dep  # the recorded side: this step's own entry
        assert "input-changed" in out and "next: superra repro build '02-paper#paper'" in out  # est is fresh
        assert "uncommitted" not in dep and "snapshot" not in dep


def test_tracked_output_edits_are_output_causes(clones, capsys):
    a, b, first = clones
    a.write("superRA/07-table/task.md", _task("07-table", _step("table", "sh Code/table.sh", ["Code/table.sh"], ["tables/t.txt"])))
    a.write("Code/table.sh", "mkdir -p tables\necho t1 > tables/t.txt\n")
    assert a.run("build", "07-table") == 0
    git(a.root, "add", "-A")
    git(a.root, "commit", "-qm", "tracked table")
    a.write("tables/t.txt", "hand edit\n")
    out = explain(a, capsys, "07-table#table")
    assert "unknown-output" in out and "current uncommitted" in out
    assert "dependency" not in out.split("unknown-output", 1)[1]
    git(a.root, "commit", "-qam", "commit the edit")
    out = explain(a, capsys, "07-table#table")
    assert "other-build" in out and f"current git {head(a.root)}" in out
    assert f"next: git show --stat {head(a.root)}" in out  # the revision the row prints
    assert "input-changed" not in out


def test_a_lock_off_heads_history_names_its_branches(clones, capsys):
    a, b, _ = clones
    git(a.root, "checkout", "-qb", "wip")
    a.write("Code/noise.sh", emit("noise", "v2"))
    assert a.run("build", "06-noise") == 0
    git(a.root, "commit", "-qam", "noise on wip")
    wip = head(a.root)
    git(a.root, "checkout", "-q", "main")  # output/ is untracked, so the wip bytes stay
    out = explain(a, capsys, "06-noise#noise")
    assert "other-build" in out
    assert f"current lock {wip} (Co Author," in out and "; not in HEAD's history; on wip)" in out

    # A coauthor's pushed branch that is not checked out here: matched through remote-tracking refs.
    git(b.root, "fetch", "-q")
    shutil.copy(a.root / "output/noise.txt", b.root / "output/noise.txt")
    out = explain(b, capsys, "06-noise#noise")
    assert f"current lock {wip} (Co Author," in out and "; not in HEAD's history; on origin/wip)" in out
    assert "on local and remote-tracking branches and HEAD" in out


def test_status_reuses_the_lock_commit_without_git(clones, monkeypatch):
    import _repro_provenance

    _, b, first = clones
    b.paths.state_dir.mkdir()  # caches persist only into an existing state directory
    assert b.status(".").entry("check-paper").reason.endswith(f"lock {first} on {platform_name()}; not run here")

    def no_git(*args, **kwargs):
        raise AssertionError("status spawned git")

    monkeypatch.setattr(_repro_provenance.Git, "raw", no_git)
    assert b.status(".").entry("check-paper").reason.endswith(f"lock {first} on {platform_name()}; not run here")


def test_unique_bare_names_select_their_step_for_every_command(clones, capsys):
    _, b, _ = clones
    assert b.status("est").entry("est") is not None
    assert b.run("build", "est") == 0
    assert b.run("accept", "est", "--reason", "reviewed") == 0
    assert b.run("revoke", "est") == 0

    # An archived step sharing the name does not block the active one.
    b.write("superRA/08-old/task.md", b.read("superRA/01-est/task.md").replace("status: not-started", "status: archived")
            .replace("${OUT}/est.txt", "${OUT}/old-est.txt"))
    assert b.status("est").entry("est").step.task_path == "01-est"


def test_lock_index_is_cached_per_revision(clones, capsys):
    _, b, first = clones
    explain(b, capsys, "01-est")
    full = git(b.root, "rev-parse", first)
    assert (b.paths.state_dir / "lock-index" / f"{full}.json").is_file()


def test_check_stamp_lost_outside_git_names_the_working_lock(project):
    assert project.run("build", *CHAIN) == 0
    shutil.rmtree(project.paths.stamps_dir)
    check = project.status(*CHAIN).entry("check-b")
    assert (check.status, check.reason) == ("fresh", f"passed at these inputs in the working lock on {platform_name()}; not run here")
    project.write("output/b.txt", "changed\n")
    assert project.status(*CHAIN).entry("check-b").reason == "output .superra-repro/stamps/check-b.stamp is missing"


def test_upstream_is_a_status_and_a_definition_change_an_input_without_git(project, capsys):
    assert project.run("build", *CHAIN) == 0
    project.write("superRA/01-a/task.md", project.read("superRA/01-a/task.md").replace("sh Code/a.sh", "sh Code/a.sh && true"))
    out = explain(project, capsys, "02-b#build-b")
    assert "build-b  [stale]  upstream step 'build-a' is stale" in out
    assert "input-changed" not in out and "next:" not in out
    out = explain(project, capsys, "01-a")
    assert "input-changed" in out and "spec" in out
    assert "next: git diff -- superRA/01-a/task.md superRA/config.yaml" in out
    assert "no git history (not a git checkout)" in out
