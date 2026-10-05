"""What each step was built on — `built_on` in `repro-lock.json` — and its place in `repro explain` rows."""
from __future__ import annotations

import getpass
import json
import socket

from _repro_builds import platform_name
from test_repro_provenance import clones, explain, git, head  # noqa: F401
from test_repro_runner import CHAIN, project  # noqa: F401

def test_record_is_written_on_success_only(project):
    assert project.run("build", *CHAIN) == 0
    text = project.read("repro-lock.json")
    lock = json.loads(text)
    for name in ("build-a", "build-b", "check-b"):
        assert set(lock["steps"][name]) == {"spec", "deps", "outs", "built_on", "sizes"}
        assert lock["steps"][name]["built_on"] == {"platform": platform_name()}
    assert getpass.getuser() not in text and socket.gethostname() not in text

    # An identical rebuild leaves the lock byte-identical: no timestamp churn.
    assert project.run("build", *CHAIN, "--force") == 0
    assert project.read("repro-lock.json") == text

    before = lock["steps"]["build-a"]
    project.write("Code/a.sh", "exit 3\n")
    assert project.run("build", "01-a") != 0
    assert json.loads(project.read("repro-lock.json"))["steps"]["build-a"] == before


def test_explain_compares_the_lock_builders_environment(clones, capsys, monkeypatch):
    import _repro_builds
    a, b, first = clones
    here = platform_name()

    # The check-stamp reason names the builder's platform from the committed lock.
    reason = b.status(".").entry("check-paper").reason
    assert reason == f"passed at these inputs in lock {first} on {here}; not run here"

    a.write("Code/est.sh", "mkdir -p output\necho v2 > output/est.txt\n")
    assert a.run("build", "01-est") == 0
    git(a.root, "commit", "-qam", "rebuild est")
    rebuilt = head(a.root)
    git(b.root, "pull", "-q", "--no-rebase")

    # Lookup at the lock revision the row names.
    out = explain(b, capsys, "01-est#est")
    assert f"recorded lock {rebuilt} " in out and "env: same as lock builder" in out
    capsys.readouterr()
    assert b.run("explain", "01-est#est", "--json") == 0
    env = json.loads(capsys.readouterr().out)["rows"][0]["env"]
    assert env["status"] == "same" and env["where"] == f"lock {rebuilt}"
    assert env["record"]["platform"] == here

    monkeypatch.setattr(_repro_builds, "platform_name", lambda: "Linux x86_64")
    out = explain(b, capsys, "01-est#est")
    assert f"env: differs — platform ({here} there, Linux x86_64 here)" in out

    # A source-file input has no build behind it, so its row carries no environment.
    b.write("Code/style.py", b.read("Code/style.py") + "# local\n")
    out = explain(b, capsys, "03-figure#figure")
    assert "input-changed" in out and "env:" not in out
