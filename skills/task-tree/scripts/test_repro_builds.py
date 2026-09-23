"""The committed build record `repro-builds.json` and its place in `repro explain` rows."""
from __future__ import annotations

import getpass
import json
import socket

from _repro_builds import lock_id, platform_name
from _repro_state import read_lock
from test_repro_provenance import clones, explain, git, head  # noqa: F401
from test_repro_runner import CHAIN, CONFIG, needs_pytask, project  # noqa: F401

PROBE_CONFIG = CONFIG + '  env_probe: "cat probe.txt"\n'


@needs_pytask
def test_record_is_written_on_success_only(project):
    assert project.run("build", *CHAIN) == 0
    text = project.read("repro-builds.json")
    builds, lock = json.loads(text), read_lock(project.paths.lock_file)
    for name in ("build-a", "build-b", "check-b"):
        assert set(builds[name]) == {"lock_id", "built_at", "platform", "env"}
        assert builds[name]["lock_id"] == lock_id(lock[name].depends_on, lock[name].produces)
        assert builds[name]["platform"] == platform_name()
    assert getpass.getuser() not in text and socket.gethostname() not in text

    before = builds["build-a"]
    project.write("Code/a.sh", "exit 3\n")
    assert project.run("build", "01-a") != 0
    assert json.loads(project.read("repro-builds.json"))["build-a"] == before


@needs_pytask
def test_explain_compares_the_lock_builders_environment(clones, capsys):
    a, b, first = clones
    a.write("superRA/config.yaml", PROBE_CONFIG)
    a.write(".gitignore", "output/\n.superra-repro/\nprobe.txt\n")
    for clone, blas in ((a, "openblas"), (b, "accelerate")):
        clone.write("probe.txt", f"blas: {blas}\nthreads: 8\n")

    # The check-stamp reason names the builder's platform once the record is committed.
    git(a.root, "add", "repro-builds.json", "superRA/config.yaml", ".gitignore")
    git(a.root, "commit", "-qm", "build record and env probe")
    git(b.root, "pull", "-q", "--no-rebase")
    reason = b.status(".").entry("check-paper").reason
    assert reason == f"passed at these inputs in lock {first} on {platform_name()}; not run here"

    # A rebuilds est with the probe, then forces an identical rebuild under another probe:
    # the lock keeps the first revision, and the record at HEAD moves on.
    a.write("Code/est.sh", "mkdir -p output\necho v2 > output/est.txt\n")
    assert a.run("build", "01-est") == 0
    git(a.root, "commit", "-qam", "rebuild est")
    rebuilt = head(a.root)
    a.write("probe.txt", "blas: mkl\nthreads: 8\n")
    assert a.run("build", "01-est", "--force") == 0
    git(a.root, "commit", "-qam", "force est under mkl")
    assert json.loads(a.read("repro-builds.json"))["est"]["env"]["probe"].startswith("blas: mkl")

    # A panel record that no longer matches its lock entry.
    a.write("Code/panel.sh", "mkdir -p output\necho v2 > output/panel.txt\n")
    assert a.run("build", "04-panel") == 0
    builds = json.loads(a.read("repro-builds.json"))
    builds["panel"]["lock_id"] = "0" * 16
    a.write("repro-builds.json", json.dumps(builds))
    git(a.root, "commit", "-qam", "panel with a stale record")
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

    out = explain(b, capsys, "04-panel#panel")
    assert "has a build record for panel that does not match its lock entry" in out

    # A source-file input has no build behind it, so its row carries no environment.
    b.write("Code/style.py", b.read("Code/style.py") + "# local\n")
    out = explain(b, capsys, "03-figure#figure")
    assert "input-changed" in out and "env:" not in out
