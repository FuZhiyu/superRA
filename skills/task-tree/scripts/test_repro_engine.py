"""superRA's own build loop and `repro-lock.json`: scheduling, interruption, the
lock format and its merges, legacy `pytask.lock` projects, and the freshness
cases the pytask engine got wrong (symlinked data, a deleted lock, sidecar
reruns, scoped status)."""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

from _repro_acceptance import LEDGER, read_ledger, receipt_path
from _repro_builds import platform_name
from _repro_state import (
    LEGACY_BUILDS_FILENAME, LEGACY_LOCK_FILENAME, TOML_AVAILABLE, legacy_lock_id, read_lock,
    lock_text, read_lock_document, _write_lock_document,
)
from test_repro_acceptance import review
from test_repro_provenance import explain, git, head
from test_repro_runner import CHAIN, TASK_X, Project, _use_a_sidecar, project  # noqa: F401

SCRIPTS = Path(__file__).parent
# In process, a legacy lock needs tomllib; the CLI re-execs under uv instead.
needs_tomllib = pytest.mark.skipif(not TOML_AVAILABLE, reason="reading pytask.lock needs Python 3.11+")


# ---------------------------------------------------------------------------
# The lock file
# ---------------------------------------------------------------------------

def test_the_lock_holds_one_line_per_step_in_step_order_and_round_trips(project):
    assert project.run("build", ".") == 0
    text = project.read("repro-lock.json")
    document = json.loads(text)
    assert list(document) == ["steps", "version"] and document["version"] == 2
    assert list(document["steps"]) == sorted(document["steps"])
    entry = document["steps"]["build-b"]
    assert entry["spec"] and entry["deps"] == {
        "${OUT}/a.txt": entry["deps"]["${OUT}/a.txt"], "Code/b.sh": entry["deps"]["Code/b.sh"]}
    assert "build-b::spec" not in entry["deps"]
    entry_lines = [line for line in text.splitlines() if line.startswith('    "')]
    assert [json.loads("{" + line.rstrip(",") + "}") for line in entry_lines] == [
        {name: raw} for name, raw in sorted(document["steps"].items())]
    assert text == lock_text(document)
    # In memory the spec is the `<step>::spec` dependency acceptance records compare.
    assert read_lock(project.paths.lock_file)["build-b"].depends_on["build-b::spec"] == entry["spec"]

    _write_lock_document(project.paths, read_lock_document(project.paths.lock_file))
    assert project.read("repro-lock.json") == text
    umask = os.umask(0)
    os.umask(umask)
    assert project.paths.lock_file.stat().st_mode & 0o777 == 0o666 & ~umask  # not mkstemp's 0600


def test_status_and_build_agree_when_the_lock_is_deleted(project):
    assert project.run("build", ".") == 0
    project.paths.lock_file.unlink()  # the per-machine state directory stays
    assert set(project.states().values()) == {"missing"}
    before = project.run_times()
    assert project.run("build", ".") == 0
    after = project.run_times()
    assert all(after[name] != before[name] for name in before)
    assert set(project.states().values()) == {"fresh"}


def _merge_repo(project):
    project.write(".gitignore", "output/\n.superra-repro/\n")
    git(project.root, "init", "-q")
    git(project.root, "add", "-A")
    git(project.root, "commit", "-qm", "code")
    assert project.run("build", ".") == 0
    git(project.root, "add", "repro-lock.json")
    git(project.root, "commit", "-qm", "build")


@pytest.mark.parametrize("left,right", [
    (("01-a", "Code/a.sh"), ("02-b", "Code/b.sh")),     # adjacent entries: build-a, build-b
    (("02-b", "Code/b.sh"), ("03-x", "Code/x.sh")),     # adjacent entries: build-b, build-x
    (("01-a", "Code/a.sh"), ("03-x", "Code/x.sh")),
])
def test_branches_that_build_different_steps_merge_cleanly(project, left, right):
    _merge_repo(project)
    for branch, (task, script) in (("left", left), ("right", right)):
        git(project.root, "checkout", "-qb", branch, "main")
        project.write(script, project.read(script) + f"# {branch}\n")
        assert project.run("build", task) == 0
        git(project.root, "commit", "-qam", branch)
    git(project.root, "checkout", "-q", "left")
    git(project.root, "merge", "-q", "--no-edit", "right")  # raises on a conflict
    assert set(json.loads(project.read("repro-lock.json"))["steps"]) == {"build-a", "build-b", "check-b", "build-x"}
    assert project.status(".").ok


def _new_step_task(project, name):
    project.write(f"superRA/04-{name}/task.md", TASK_X.replace("build-x", name).replace("x.sh", f"{name}.sh")
                  .replace("x.txt", f"{name}.txt"))
    project.write(f"Code/{name}.sh", f"mkdir -p output\necho {name} > output/{name}.txt\n")


def test_a_lock_conflicted_by_adjacent_new_steps_reads_both_and_the_next_build_rewrites_it(project, capsys):
    _merge_repo(project)
    for branch, name in (("left", "build-p"), ("right", "build-q")):  # sort next to each other
        git(project.root, "checkout", "-qb", branch, "main")
        _new_step_task(project, name)
        assert project.run("build", f"04-{name}") == 0
        git(project.root, "add", "-A")
        git(project.root, "commit", "-qm", branch)
    git(project.root, "checkout", "-q", "left")
    merge = subprocess.run(["git", "merge", "--no-edit", "right"], cwd=project.root, capture_output=True, text=True)
    assert merge.returncode != 0 and "<<<<<<<" in project.read("repro-lock.json")
    capsys.readouterr()

    assert set(project.states().values()) == {"fresh"}
    err = capsys.readouterr().err
    assert "conflict markers" in err and "dropped" not in err
    times = project.run_times()
    assert project.run("build", ".") == 0
    assert project.run_times() == times  # nothing reran
    text = project.read("repro-lock.json")
    assert "<<<<<<<" not in text
    assert {"build-p", "build-q"} <= set(json.loads(text)["steps"])


def test_a_version_1_lock_reads_and_the_next_build_rewrites_it_one_line_per_step(project):
    assert project.run("build", ".") == 0
    document = json.loads(project.read("repro-lock.json"))
    project.write("repro-lock.json", json.dumps(dict(document, version=1), indent=2, sort_keys=True) + "\n")
    assert set(project.states().values()) == {"fresh"}
    times = project.run_times()
    assert project.run("build", ".") == 0
    assert project.run_times() == times
    assert project.read("repro-lock.json") == lock_text(document)


def _mixed_check_repo(project, *, adjacent_new_steps):
    """The review's reproduction: each branch changes a different dep of one check and rebuilds it."""
    deps = [f"Code/m{i}.txt" for i in range(1, 5)]
    project.write("superRA/05-m/task.md", TASK_X.replace("build-x", "check-m").replace(
        "    cmd: sh Code/x.sh\n    deps:\n      - Code/x.sh\n    outs:\n      - \"${OUT}/x.txt\"\n",
        "    kind: check\n    cmd: sh -c '! { grep -qx L Code/m1.txt && grep -qx R Code/m4.txt; }'\n    deps:\n"
        + "".join(f"      - {dep}\n" for dep in deps)))
    for dep in deps:
        project.write(dep, "base\n")
    _merge_repo(project)
    for branch, dep, text, name in (("left", deps[0], "L", "build-p"), ("right", deps[3], "R", "build-q")):
        git(project.root, "checkout", "-qb", branch, "main")
        project.write(dep, text + "\n")
        if adjacent_new_steps:
            _new_step_task(project, name)
        assert project.run("build", ".") == 0
        git(project.root, "add", "-A")
        git(project.root, "commit", "-qm", branch)
    git(project.root, "checkout", "-q", "left")
    return subprocess.run(["git", "merge", "--no-edit", "right"], cwd=project.root, capture_output=True, text=True)


@pytest.mark.parametrize("adjacent_new_steps", [True, False])
def test_a_check_both_branches_rebuilt_never_reads_fresh_after_a_merge(project, capsys, adjacent_new_steps):
    merge = _mixed_check_repo(project, adjacent_new_steps=adjacent_new_steps)
    assert merge.returncode != 0 and "<<<<<<<" in project.read("repro-lock.json")
    capsys.readouterr()
    assert project.states()["check-m"] == "missing"
    assert "dropped 1 entry the two sides disagree on: check-m" in capsys.readouterr().err
    assert project.run("build", "05-m") == 1  # the merged tree really fails the check
    assert project.states()["check-m"] == "failed"
    assert "<<<<<<<" not in project.read("repro-lock.json")


def test_acceptance_records_of_one_step_never_line_merge_into_a_trusted_record(project, monkeypatch):
    import _repro_acceptance
    monkeypatch.setattr(_repro_acceptance, "_WARNED", set())  # leave later tests their first warning
    _merge_repo(project)
    script = project.read("Code/a.sh")
    for branch, edited in (("left", "# left\n" + script), ("right", script + "# right\n")):  # merges cleanly
        git(project.root, "checkout", "-qb", branch, "main")
        project.write("Code/a.sh", edited)
        assert project.run("accept", "01-a", "--reason", f"reviewed on {branch}") == 0
        git(project.root, "add", "-A")
        git(project.root, "commit", "-qm", branch)
    git(project.root, "checkout", "-q", "left")
    subprocess.run(["git", "merge", "--no-edit", "right"], cwd=project.root, capture_output=True, text=True)
    assert "<<<<<<<" not in project.read("Code/a.sh")
    assert project.states()["build-a"] != "fresh"
    assert read_ledger(project.paths)["set_aside"] == ["build-a"]


@pytest.mark.parametrize("style", [[], ["--diff3"]])
def test_a_lock_entry_both_sides_changed_is_dropped_so_its_step_reads_missing(project, capsys, style):
    assert project.run("build", ".") == 0
    base = project.read("repro-lock.json")
    sides = []
    for text in ("left", "right"):
        project.write("Code/a.sh", f"# {text}\nmkdir -p output\necho hello > output/a.txt\n")
        assert project.run("build", "01-a") == 0
        sides.append(project.read("repro-lock.json"))
    files = [project.write(f"lock-{label}.json", body) for label, body in zip(("ours", "base", "theirs"),
                                                                             (sides[0], base, sides[1]))]
    merged = subprocess.run(["git", "merge-file", "-p", *style, *map(str, files)],
                            capture_output=True, text=True).stdout
    assert "<<<<<<<" in merged
    project.write("repro-lock.json", merged)
    capsys.readouterr()

    assert set(read_lock(project.paths.lock_file)) == {"build-b", "check-b", "build-x"}
    assert "dropped 1 entry the two sides disagree on: build-a" in capsys.readouterr().err
    assert project.states()["build-a"] == "missing"
    assert project.run("build", "01-a") == 0
    assert "<<<<<<<" not in project.read("repro-lock.json")
    assert project.states()["build-a"] == "fresh"


# ---------------------------------------------------------------------------
# Scheduling
# ---------------------------------------------------------------------------

def test_parallel_build_orders_steps_skips_after_failure_and_keeps_every_entry(project):
    project.write("Code/b.sh", "sleep 0.3\necho boom >&2\nexit 3\n")
    project.write("superRA/04-y/task.md", TASK_X.replace("build-x", "build-y").replace("x.sh", "y.sh")
                  .replace("x.txt", "y.txt"))
    project.write("Code/x.sh", "sleep 0.2\nmkdir -p output\necho x > output/x.txt\n")
    project.write("Code/y.sh", "mkdir -p output\necho y > output/y.txt\n")
    assert project.run("build", ".", "-j", "3") == 1
    times = project.run_times()
    b = json.loads(project.paths.run_file("build-b").read_text())
    assert times["build-a"] <= b["ended_at"] - b["duration"]  # a producer finishes before its consumer starts
    assert "check-b" not in times  # a failed producer skips its descendants
    assert {"build-x", "build-y"} <= set(times)  # unrelated branches still run
    assert set(read_lock(project.paths.lock_file)) == {"build-a", "build-x", "build-y"}
    assert project.states()["build-b"] == "failed"


def test_build_exit_codes(project, capsys):
    assert project.run("build", "02-b") == 1   # cannot start: a saved input is missing
    assert "missing saved inputs" in capsys.readouterr().err
    assert project.run("build", "nope") == 1
    assert project.run("build", *CHAIN) == 0
    project.write("Code/b.sh", "exit 2\n")
    assert project.run("build", *CHAIN) == 1
    assert project.run("build") == 2           # argparse usage error


def test_a_missing_input_fails_the_step_before_its_command_runs(project, capsys):
    project.write("superRA/01-a/task.md", project.read("superRA/01-a/task.md").replace(
        "      - Code/a.sh\n", "      - Code/a.sh\n      - output/produced-by-nobody.txt\n"))
    capsys.readouterr()
    assert project.run("build", "01-a") == 1
    out = capsys.readouterr().out
    assert "cannot start: external input output/produced-by-nobody.txt is missing" in out
    assert not project.paths.run_file("build-a").exists()


def test_an_out_the_command_did_not_write_fails_the_step(project):
    project.write("Code/a.sh", "true\n")
    assert project.run("build", "01-a") == 1
    assert json.loads(project.paths.run_file("build-a").read_text())["outcome"] == "failed"
    assert "build-a" not in read_lock(project.paths.lock_file)


def test_dry_run_writes_no_lock_record_receipt_or_acceptance(project):
    assert project.run("build", *CHAIN) == 0
    project.write("Code/a.sh", project.read("Code/a.sh") + "# harmless\n")
    review(project)
    project.write("Code/b.sh", project.read("Code/b.sh") + "# edited\n")
    watched = [project.paths.lock_file, project.root / LEDGER / "build-a.json", *project.paths.runs_dir.iterdir(),
               *(receipt_path(project.paths, name) for name in ("build-a", "build-b", "check-b"))]
    before = {path: path.read_bytes() for path in watched}
    assert project.run("build", ".", "--dry-run", "--force", "-j", "2") == 0
    assert {path: path.read_bytes() for path in watched} == before
    assert sorted(p.name for p in project.paths.runs_dir.iterdir()) == ["build-a.json", "build-b.json", "check-b.json"]


def _interrupt_build(project, sig, *argv):
    """Start `build` in its own process group, signal the group once a step runs, and wait."""
    command = [sys.executable, str(SCRIPTS / "repro_run.py"), "--plan-root", str(project.plan_root),
               "build", *argv]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                               start_new_session=True)
    deadline = time.time() + 20
    while not (project.root / "pid.txt").exists() and time.time() < deadline:
        time.sleep(0.05)
    assert (project.root / "pid.txt").exists()
    time.sleep(0.2)  # the step's pid lands before the build finishes registering it
    started = time.time()
    os.killpg(process.pid, sig)  # how a closed terminal or a harness timeout ends a command
    _, err = process.communicate(timeout=15)
    assert process.returncode == 1
    assert time.time() - started < 10
    assert "Interrupted" in err
    step_pid = int(project.read("pid.txt"))
    with pytest.raises(ProcessLookupError):
        os.kill(step_pid, 0)


@pytest.mark.parametrize("sig", [signal.SIGINT, signal.SIGTERM, signal.SIGHUP])
def test_an_interrupt_stops_running_steps_and_records_them_failed(project, sig):
    project.write("Code/x.sh", "echo $$ > pid.txt\nsleep 30\n")
    _interrupt_build(project, sig, "03-x")
    assert json.loads(project.paths.run_file("build-x").read_text())["outcome"] == "failed"
    assert project.states()["build-x"] == "failed"


def test_an_interrupt_leaves_queued_steps_and_their_acceptance_untouched(project):
    assert project.run("build", ".") == 0
    project.write("Code/x.sh", project.read("Code/x.sh") + "# harmless\n")
    review(project, ("03-x#build-x",))
    assert project.states()["build-x"] == "fresh"
    record = project.paths.run_file("build-x").read_bytes()
    project.write("Code/a.sh", "echo $$ > pid.txt\nsleep 30\n")
    _interrupt_build(project, signal.SIGINT, ".", "--force", "-j", "1")  # build-x waits behind build-a
    assert project.paths.run_file("build-x").read_bytes() == record
    assert project.states()["build-x"] == "fresh"  # the acceptance still stands
    assert project.states()["build-a"] == "failed"


def test_a_stop_after_the_check_leaves_the_steps_acceptance_standing(project, monkeypatch):
    import repro_run
    assert project.run("build", ".") == 0
    project.write("Code/x.sh", project.read("Code/x.sh") + "# harmless\n")
    review(project, ("03-x#build-x",))
    ledger = project.root / LEDGER / "build-x.json"
    accepted = ledger.read_bytes()
    boundary, run_step = repro_run.boundary_inputs, repro_run._run_step

    def stop_after_the_check(build, step, entry):
        def late(*args, **kwargs):
            build.stopping.set()  # the interrupt lands after the pre-start check
            return boundary(*args, **kwargs)
        monkeypatch.setattr(repro_run, "boundary_inputs", late)
        return run_step(build, step, entry)

    monkeypatch.setattr(repro_run, "_run_step", stop_after_the_check)
    project.run("build", "03-x", "--force")
    assert ledger.read_bytes() == accepted  # supersede waits for the step to actually start


# ---------------------------------------------------------------------------
# Freshness fixes
# ---------------------------------------------------------------------------

DIR_TASK = """\
---
title: "Agg"
status: not-started
depends_on: []
---

## Objective

Aggregate a directory.

## Reproduction

```yaml
steps:
  - name: agg
    cmd: cat Data/panel/*/p.csv > output/agg.csv
    deps:
      - Data/panel
    outs:
      - output/agg.csv
```
"""


def test_a_symlinked_subdirectory_inside_a_directory_dependency_is_hashed(tmp_path):
    proj = Project(tmp_path / "sym")
    proj.write("superRA/01-agg/task.md", DIR_TASK)
    proj.write("extdata/y2020/p.csv", "1\n")
    (proj.root / "Data/panel").mkdir(parents=True)
    (proj.root / "Data/panel/y2020").symlink_to(proj.root / "extdata/y2020")
    (proj.root / "output").mkdir()
    assert proj.run("build", ".") == 0
    assert proj.read("output/agg.csv") == "1\n"
    proj.write("extdata/y2020/p.csv", "2\n")
    assert proj.states()["agg"] == "stale"
    assert proj.run("build", ".") == 0
    assert proj.read("output/agg.csv") == "2\n"

    (proj.root / "Data/panel/loop").symlink_to(proj.root / "Data/panel")  # a cycle is walked once
    assert proj.states()["agg"] == "fresh"
    (proj.root / "Data/panel/broken").symlink_to(proj.root / "nowhere")
    entry = proj.status().entry("agg")
    assert entry.status == "stale" and entry.reason == "dependency Data/panel missing"


def test_a_targeted_build_keeps_a_sidecar_saved_inputs_consumer_fresh(project):
    _use_a_sidecar(project)
    assert project.run("build", *CHAIN) == 0
    before = project.run_times()
    assert project.run("status", "02-b") == 0
    assert project.run("build", "02-b") == 0
    assert project.run_times() == before

    # A fresh clone has no receipts: the sidecar's digest vouches for the bytes.
    for receipt in (project.paths.state_dir / "baselines").iterdir():
        receipt.unlink()
    assert project.run("status", "02-b") == 0
    assert project.run("build", "02-b") == 0
    assert project.run_times() == before


def test_scoped_status_exits_3_for_a_fresh_selection_behind_a_producer_that_is_not(project, capsys):
    assert project.run("build", *CHAIN) == 0
    assert project.run("status", "02-b") == 0
    project.write("Code/a.sh", project.read("Code/a.sh") + "# edited\n")
    capsys.readouterr()
    assert project.run("status", "02-b") == 3
    assert "1 producer(s) behind the selection not fresh: build-a (stale)" in capsys.readouterr().out
    assert project.run("status", "02-b", "--json") == 3
    assert json.loads(capsys.readouterr().out)["behind"] == [{"name": "build-a", "task": "01-a", "status": "stale"}]
    assert project.run("status", "02-b", "--upstream") == 1
    assert project.run("status", "01-a") == 1
    assert project.run("status", "02-b", "--no-such-flag") == 2
    capsys.readouterr()
    project.run("status", ".")
    out = capsys.readouterr().out
    assert "for every registered step:" in out and "selected steps only" not in out
    (project.root / "output/a.txt").unlink()
    assert project.run("status", "02-b#check-b") == 3  # build-a missing; build-b still fresh


def test_a_check_passed_at_these_inputs_elsewhere_reads_fresh(project):
    assert project.run("build", *CHAIN) == 0
    for stamp in project.paths.stamps_dir.iterdir():  # a fresh clone: the lock, not the stamp, travels
        stamp.unlink()
    check = project.status(*CHAIN).entry("check-b")
    assert (check.status, check.reason) == (
        "fresh", f"passed at these inputs in the working lock on {platform_name()}; not run here")
    assert project.run("status", *CHAIN) == 0
    before = project.run_times()
    assert project.run("build", *CHAIN) == 0
    assert project.run_times() == before  # build and status share the rule

    project.write("superRA/02-b/task.md", project.read("superRA/02-b/task.md").replace(
        "cmd: test -s output/b.txt", "cmd: test -s output/b.txt && true"))
    assert project.status(*CHAIN).entry("check-b").status == "missing"  # a spec change: must run here


def test_a_check_that_failed_here_outweighs_its_pass_elsewhere(project, monkeypatch):
    project.write("Code/check.sh", 'test "$CHECK_OK" = yes\n')
    project.write("superRA/02-b/task.md", project.read("superRA/02-b/task.md").replace(
        "cmd: test -s output/b.txt", "cmd: sh Code/check.sh"))
    monkeypatch.setenv("CHECK_OK", "yes")
    assert project.run("build", *CHAIN) == 0
    for stamp in project.paths.stamps_dir.iterdir():
        stamp.unlink()
    assert project.status(*CHAIN).entry("check-b").status == "fresh"
    monkeypatch.setenv("CHECK_OK", "no")  # this machine disagrees
    assert project.run("build", "02-b#check-b", "--force") == 1
    check = project.status(*CHAIN).entry("check-b")
    assert check.status == "failed" and check.reason.startswith("forced rerun required; last run failed")
    assert project.run("status", *CHAIN) == 1


def test_a_check_that_failed_here_unforced_reads_rerun_required(project, monkeypatch):
    project.write("Code/check.sh", 'test "$CHECK_OK" = yes\n')
    project.write("superRA/02-b/task.md", project.read("superRA/02-b/task.md").replace(
        "cmd: test -s output/b.txt", "cmd: sh Code/check.sh"))
    monkeypatch.setenv("CHECK_OK", "yes")
    assert project.run("build", *CHAIN) == 0
    elsewhere = read_lock_document(project.paths.lock_file)  # the pass another machine committed
    for stamp in project.paths.stamps_dir.iterdir():
        stamp.unlink()
    local = read_lock_document(project.paths.lock_file)
    del local["steps"]["check-b"]
    _write_lock_document(project.paths, local)
    monkeypatch.setenv("CHECK_OK", "no")
    assert project.run("build", "02-b#check-b") == 1  # never built here: runs unforced and fails
    _write_lock_document(project.paths, elsewhere)
    check = project.status(*CHAIN).entry("check-b")
    assert check.status == "failed" and check.reason.startswith("rerun required; last run failed")


# ---------------------------------------------------------------------------
# Legacy pytask.lock projects
# ---------------------------------------------------------------------------

def _as_legacy(project, *, record=True):
    """Rewrite the project's lock as the pytask engine left it: pytask.lock + repro-builds.json."""
    document = read_lock_document(project.paths.lock_file)
    blocks, builds = [], {}
    for name, entry in sorted(read_lock(project.paths.lock_file).items()):
        deps = "\n".join(f'"{k}" = "{v}"' for k, v in entry.depends_on.items())
        outs = "\n".join(f'"{k}" = "{v}"' for k, v in entry.produces.items())
        blocks.append(f'[[task]]\nid = "{name}"\nsignature = "x"\nstate = "1"\n\n'
                      f'[task.depends_on]\n{deps}\n\n[task.produces]\n{outs}\n')
        builds[name] = {"lock_id": legacy_lock_id(entry.depends_on, entry.produces), "built_at": 1.0,
                        "platform": document["steps"][name]["built_on"]["platform"], "env": {"deps": {}}}
    project.write(LEGACY_LOCK_FILENAME, 'lock-version = "1"\n\n' + "\n".join(blocks))
    if record:
        project.write(LEGACY_BUILDS_FILENAME, json.dumps(builds))
    project.paths.lock_file.unlink()


@needs_tomllib
def test_a_legacy_lock_reads_unchanged_and_the_first_build_migrates_it(project, capsys, monkeypatch):
    assert project.run("build", *CHAIN) == 0
    expected = read_lock(project.paths.lock_file)
    _as_legacy(project)
    import _repro_state
    parses = []
    real = _repro_state.convert_legacy
    monkeypatch.setattr(_repro_state, "convert_legacy", lambda *a: parses.append(1) or real(*a))
    monkeypatch.setattr(_repro_state, "_LEGACY_DOCUMENTS", {})
    assert read_lock(project.paths.lock_file) == expected
    assert read_lock(project.paths.lock_file)["build-a"].built_on == {"platform": platform_name()}
    assert len(parses) == 1  # converted once per process, not once per reader
    assert project.status(*CHAIN).ok
    before = project.run_times()
    capsys.readouterr()
    assert project.run("build", *CHAIN) == 0
    out = capsys.readouterr().out
    assert project.run_times() == before
    assert "`git rm pytask.lock repro-builds.json`" in out
    assert (project.root / LEGACY_LOCK_FILENAME).exists() and (project.root / LEGACY_BUILDS_FILENAME).exists()
    assert read_lock(project.paths.lock_file) == expected
    assert not (project.root / ".pytask").exists()


@needs_tomllib
def test_explain_names_lock_revisions_across_the_switch_to_repro_lock(project, capsys, monkeypatch):
    project.write(".gitignore", "output/\n.superra-repro/\n")
    git(project.root, "init", "-q")
    git(project.root, "add", "-A")
    git(project.root, "commit", "-qm", "code")
    assert project.run("build", *CHAIN) == 0
    _as_legacy(project, record=False)
    git(project.root, "add", LEGACY_LOCK_FILENAME)
    git(project.root, "commit", "-qm", "the pytask engine's lock")
    legacy = head(project.root)
    project.write("Code/a.sh", "mkdir -p output\necho other > output/a.txt\n")
    assert project.run("build", "01-a") == 0
    git(project.root, "add", "repro-lock.json")
    git(project.root, "commit", "-qam", "rebuild a on the new engine")
    rebuilt = head(project.root)
    project.write("output/a.txt", "hello\n")  # the old bytes come back, as a lagging sync would
    import _repro_provenance
    with monkeypatch.context() as patch:  # Python 3.10: no tomllib to read the legacy revision
        patch.setattr(_repro_provenance, "tomllib", None)
        explain(project, capsys, "01-a#build-a")
    assert len(list((project.paths.state_dir / "lock-index").iterdir())) == 1  # only the readable revision
    out = explain(project, capsys, "01-a#build-a")
    assert f"recorded lock {rebuilt} " in out
    assert f"current lock {legacy} " in out


def test_explain_names_lock_revisions_across_the_switch_to_one_line_entries(project, capsys):
    project.write(".gitignore", "output/\n.superra-repro/\n")
    git(project.root, "init", "-q")
    git(project.root, "add", "-A")
    git(project.root, "commit", "-qm", "code")
    assert project.run("build", *CHAIN) == 0
    document = json.loads(project.read("repro-lock.json"))
    project.write("repro-lock.json", json.dumps(dict(document, version=1), indent=2, sort_keys=True) + "\n")
    git(project.root, "add", "repro-lock.json")
    git(project.root, "commit", "-qm", "a version 1 lock")
    version_1 = head(project.root)
    project.write("Code/a.sh", "mkdir -p output\necho other > output/a.txt\n")
    assert project.run("build", "01-a") == 0
    assert json.loads(project.read("repro-lock.json"))["version"] == 2
    git(project.root, "commit", "-qam", "rebuild a")
    rebuilt = head(project.root)
    project.write("output/a.txt", "hello\n")  # the old bytes come back
    out = explain(project, capsys, "01-a#build-a")
    assert f"recorded lock {rebuilt} " in out
    assert f"current lock {version_1} " in out


def test_a_legacy_lock_on_python_310_re_execs_through_uv(project, monkeypatch, capsys):
    import repro_run
    assert project.run("build", *CHAIN) == 0
    _as_legacy(project)
    calls = []
    monkeypatch.setattr(repro_run, "TOML_AVAILABLE", False)
    monkeypatch.setattr(repro_run, "_reexec", lambda argv, command: calls.append(command) or 0)
    assert project.run("status", *CHAIN) == 0
    assert calls == ["status"]
    project.paths.legacy_lock_file.unlink()
    assert project.run("status", *CHAIN) == 1  # never built: nothing to convert, no re-exec
    assert calls == ["status"]
