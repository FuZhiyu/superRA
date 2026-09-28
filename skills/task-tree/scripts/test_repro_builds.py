"""What each step was built on — `built_on` in `repro-lock.json` — and its place in `repro explain` rows."""
from __future__ import annotations

import getpass
import json
import socket

from _repro_builds import platform_name
from test_repro_provenance import clones, explain, git, head  # noqa: F401
from test_repro_runner import CHAIN, CONFIG, project  # noqa: F401

PROBE_CONFIG = CONFIG + '  env_probe: "cat probe.txt"\n'


def test_record_is_written_on_success_only(project):
    assert project.run("build", *CHAIN) == 0
    text = project.read("repro-lock.json")
    lock = json.loads(text)
    for name in ("build-a", "build-b", "check-b"):
        assert set(lock["steps"][name]) == {"spec", "deps", "outs", "built_on"}
        assert lock["steps"][name]["built_on"] == {"platform": platform_name()}
    assert getpass.getuser() not in text and socket.gethostname() not in text

    # An identical rebuild leaves the lock byte-identical: no timestamp churn.
    assert project.run("build", *CHAIN, "--force") == 0
    assert project.read("repro-lock.json") == text

    before = lock["steps"]["build-a"]
    project.write("Code/a.sh", "exit 3\n")
    assert project.run("build", "01-a") != 0
    assert json.loads(project.read("repro-lock.json"))["steps"]["build-a"] == before


def test_probe_runs_once_per_build_and_its_text_is_stored_once(project):
    project.write("superRA/config.yaml", CONFIG + '  env_probe: "echo run >> probe-runs.txt; echo blas: accelerate"\n')
    assert project.run("build", *CHAIN, "-j", "3") == 0
    assert project.read("probe-runs.txt") == "run\n"
    lock = json.loads(project.read("repro-lock.json"))
    digests = {lock["steps"][name]["built_on"]["probe"] for name in ("build-a", "build-b", "check-b")}
    assert len(digests) == 1 and lock["probes"] == {digests.pop(): "blas: accelerate"}
    assert project.read("repro-lock.json").count("blas: accelerate") == 1


def test_probe_output_holding_an_absolute_path_is_refused(project, capsys):
    project.write("superRA/config.yaml", CONFIG + '  env_probe: "echo blas: accelerate; echo prefix: $PWD/lib"\n')
    assert project.run("build", "01-a") == 0
    text = project.read("repro-lock.json")
    assert json.loads(text)["steps"]["build-a"]["built_on"]["probe_error"] == "line 2 holds an absolute path"
    assert str(project.root) not in text and "accelerate" not in text
    err = capsys.readouterr().err
    assert "env_probe output line 2 holds an absolute path; not recorded" in err


def test_explain_compares_the_lock_builders_environment(clones, capsys):
    a, b, first = clones
    a.write("superRA/config.yaml", PROBE_CONFIG)
    a.write(".gitignore", "output/\n.superra-repro/\nprobe.txt\n")
    for clone, blas in ((a, "openblas"), (b, "accelerate")):
        clone.write("probe.txt", f"blas: {blas}\nthreads: 8\n")

    # The check-stamp reason names the builder's platform from the committed lock.
    git(a.root, "add", "superRA/config.yaml", ".gitignore")
    git(a.root, "commit", "-qm", "env probe")
    git(b.root, "pull", "-q", "--no-rebase")
    reason = b.status(".").entry("check-paper").reason
    assert reason == f"passed at these inputs in lock {first} on {platform_name()}; not run here"

    # A rebuilds est with the probe, then forces an identical rebuild under another probe:
    # the hashes keep the first revision, and `built_on` at HEAD moves on.
    a.write("Code/est.sh", "mkdir -p output\necho v2 > output/est.txt\n")
    assert a.run("build", "01-est") == 0
    git(a.root, "commit", "-qam", "rebuild est")
    rebuilt = head(a.root)
    a.write("probe.txt", "blas: mkl\nthreads: 8\n")
    assert a.run("build", "01-est", "--force") == 0
    git(a.root, "commit", "-qam", "force est under mkl")
    lock = json.loads(a.read("repro-lock.json"))
    assert lock["probes"][lock["steps"]["est"]["built_on"]["probe"]] == "blas: mkl\nthreads: 8"
    assert "blas: openblas" not in json.dumps(lock)  # an unreferenced probe text is dropped
    git(b.root, "pull", "-q", "--no-rebase")

    # Lookup at the lock revision the row names, not at HEAD.
    out = explain(b, capsys, "01-est#est")
    assert f"recorded lock {rebuilt} " in out
    assert "env: differs — env_probe line 1: 'blas: openblas' there, 'blas: accelerate' here" in out
    b.write("probe.txt", "blas: openblas\nthreads: 8\n")
    out = explain(b, capsys, "01-est#est")
    assert "env: same as lock builder" in out and "differs" not in out
    capsys.readouterr()
    assert b.run("explain", "01-est#est", "--json") == 0
    env = json.loads(capsys.readouterr().out)["rows"][0]["env"]
    assert env["status"] == "same" and env["where"] == f"lock {rebuilt}"
    assert env["record"]["platform"] == platform_name()

    # A source-file input has no build behind it, so its row carries no environment.
    b.write("Code/style.py", b.read("Code/style.py") + "# local\n")
    out = explain(b, capsys, "03-figure#figure")
    assert "input-changed" in out and "env:" not in out
