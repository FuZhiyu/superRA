"""Commands take in the targets' producer chain, gate downloads, and report online-only data.

Fixtures run real shell steps; `run_times` shows which commands executed.
"""
from __future__ import annotations

import json
import re

import pytest

from _repro_state import DOWNLOAD_NOTES, OUTPUT_CAP, read_run_record
from _task_snapshot import frontier_rows
from test_repro_online import Offline, _clear_cache
from test_repro_runner import CHAIN, CONFIG, Project, project  # noqa: F401

SOURCES = """\
---
title: "Sources"
status: not-started
depends_on: []
---

## Objective

Three producers.

## Reproduction

```yaml
steps:
  - name: p-fresh
    cmd: sh Code/fresh.sh
    deps:
      - Code/fresh.sh
    outs:
      - output/fresh.txt
  - name: p-stale
    cmd: sh Code/stale.sh
    deps:
      - Code/stale.sh
    outs:
      - output/stale.txt
  - name: p-unv
    cmd: sh Code/unv.sh
    deps:
      - Code/unv.sh
    outs:
      - output/unv.txt
```
"""

USE = """\
---
title: "Use"
status: not-started
depends_on: []
---

## Objective

Combine them with an external input.

## Reproduction

```yaml
steps:
  - name: use
    cmd: sh Code/use.sh
    deps:
      - Code/use.sh
      - Data/ext.csv
      - output/fresh.txt
      - output/stale.txt
      - output/unv.txt
    outs:
      - output/use.txt
```
"""


@pytest.fixture
def fan(tmp_path, monkeypatch):
    """Three producers feeding one consumer, built once, with online-only state simulated."""
    proj = Project(tmp_path / "fan")
    proj.write("superRA/config.yaml", CONFIG)
    proj.write("superRA/01-src/task.md", SOURCES)
    proj.write("superRA/02-use/task.md", USE)
    proj.write("Data/ext.csv", "x,1\n")
    for name in ("fresh", "stale", "unv"):
        proj.write(f"Code/{name}.sh", f"mkdir -p output\necho {name} > output/{name}.txt\n")
    proj.write("Code/use.sh", "cat Data/ext.csv output/*.txt > output/use.txt.tmp\nmv output/use.txt.tmp output/use.txt\n")
    assert proj.run("build", "02-use") == 0
    proj.offline = Offline(monkeypatch, proj.root)
    return proj


def _changed(before: dict, after: dict) -> set[str]:
    return {name for name in after if before.get(name) != after[name]}


def _make_p_unv_unverified(fan) -> None:
    fan.offline.evict("Code/unv.sh")
    _clear_cache(fan)


def test_a_default_build_reruns_a_stale_producer_and_skips_fresh_and_unverified_ones(fan, capsys):
    _make_p_unv_unverified(fan)
    fan.write("Code/stale.sh", "mkdir -p output\necho stale2 > output/stale.txt\n")
    before = fan.run_times()
    capsys.readouterr()
    assert fan.run("build", "02-use") == 0
    assert _changed(before, fan.run_times()) == {"p-stale", "use"}
    out = capsys.readouterr().out
    assert re.search(r"Also building 1 producer\(s\) the targets read:\n  p-stale  \d+\.\ds\n", out)
    assert "p-fresh" not in out.split("Also building")[1]  # skipped producers are only counted
    assert "4 step(s): 2 executed, 1 unchanged, 1 unverified" in out


def test_force_reruns_the_targets_only(fan):
    fan.write("Code/stale.sh", "mkdir -p output\necho stale2 > output/stale.txt\n")
    before = fan.run_times()
    assert fan.run("build", "02-use", "--force") == 0
    assert _changed(before, fan.run_times()) == {"p-stale", "use"}  # p-fresh untouched
    before = fan.run_times()
    assert fan.run("build", "02-use", "--force") == 0
    assert _changed(before, fan.run_times()) == {"use"}


@pytest.mark.parametrize("loss", ["online-only", "absent"])
def test_the_gate_runs_nothing_when_a_step_that_must_run_reads_a_file_not_on_disk(fan, capsys, loss):
    fan.write("Code/stale.sh", "mkdir -p output\necho stale2 > output/stale.txt\n")
    fan.write("Code/use.sh", fan.read("Code/use.sh") + "# edited\n")
    if loss == "online-only":
        fan.offline.evict("Data/ext.csv")
    else:
        (fan.root / "Data/ext.csv").unlink()
    before = fan.run_times()
    capsys.readouterr()
    assert fan.run("build", "02-use") == 1
    assert fan.run_times() == before  # not even the stale producer ran
    err = capsys.readouterr().err
    assert "1 file(s) the build reads are not on this machine, so nothing was run:" in err
    line = (r"Data/ext.csv\s+4 B\s+online-only here" if loss == "online-only"
            else r"Data/ext.csv\s+-\s+not on disk, and no step produces it")
    assert re.search(line + r"  \(read by use\)", err)
    assert "To build the steps that do not read them, select those steps with --only." in err
    assert (DOWNLOAD_NOTES in err) == (loss == "online-only")
    assert fan.run("build", "01-src", "--only") == 0  # the rest still builds
    assert _changed(before, fan.run_times()) == {"p-stale"}


def test_a_gated_dry_run_prints_its_plan_with_costs_then_the_files_and_exits_1(fan, capsys):
    fan.write("Code/stale.sh", "mkdir -p output\necho stale2 > output/stale.txt\n")
    fan.write("Code/use.sh", fan.read("Code/use.sh") + "# edited\n")
    (fan.root / "Data/ext.csv").unlink()
    before = fan.run_times()
    capsys.readouterr()
    assert fan.run("build", "02-use", "--dry-run") == 1
    assert fan.run_times() == before
    out = capsys.readouterr().out
    assert re.search(r"Would execute 2 step\(s\):\n  p-stale  \d+\.\ds\n  use      \d+\.\ds\n"
                     r"Last recorded cost: .*\n.*\n"
                     r"1 file\(s\) the build reads are not on this machine, so the build would run nothing:\n"
                     r"\s+Data/ext.csv\s+-\s+not on disk, and no step produces it  \(read by use\)\n"
                     r"To build the steps that do not read them, select those steps with --only.$", out.strip())
    assert "cannot run" not in out


def test_under_only_the_gate_names_downloading_or_narrowing_the_targets(fan, capsys):
    fan.write("Code/use.sh", fan.read("Code/use.sh") + "# edited\n")
    fan.offline.evict("Data/ext.csv")
    capsys.readouterr()
    assert fan.run("build", "02-use", "--only") == 1
    err = capsys.readouterr().err
    assert "Download them first, or narrow the targets to steps that do not read them." in err
    assert "--only" not in err


def test_steps_that_did_not_run_are_only_counted(fan, capsys):
    capsys.readouterr()
    assert fan.run("build", "02-use") == 0
    out = capsys.readouterr().out
    assert "unchanged" not in out.replace("4 step(s): 4 unchanged", "")
    assert out.strip().endswith("4 step(s): 4 unchanged")


def test_a_step_stale_only_after_its_producer_ran_is_stopped_at_its_start(fan, capsys):
    fan.offline.evict("Data/ext.csv")  # cached: `use` still reads fresh, so the gate lets the build start
    fan.write("Code/stale.sh", "mkdir -p output\necho stale2 > output/stale.txt\n")
    before = fan.run_times()
    capsys.readouterr()
    assert fan.run("build", "02-use") == 1  # Offline fails the test if anything opens Data/ext.csv
    assert _changed(before, fan.run_times()) == {"p-stale"}
    out = capsys.readouterr().out
    assert re.search(r"✗ use  failed\n  ReproStateError: step 'use' cannot start: 1 input\(s\) not on this machine:\n"
                     r"  \s+Data/ext.csv\s+4 B\s+online-only here\n  " + re.escape(DOWNLOAD_NOTES), out)
    assert read_run_record(fan.paths, "use")["outcome"] == "success"  # no failed run recorded


def test_accept_names_the_stale_producer_and_the_next_status_exits_3(fan, capsys):
    fan.write("Code/stale.sh", "mkdir -p output\necho stale2 > output/stale.txt\n")
    fan.write("Code/use.sh", fan.read("Code/use.sh") + "# comment only\n")
    capsys.readouterr()
    assert fan.run("accept", "02-use", "--reason", "reviewed", "--dry-run", "--json") == 0
    assert json.loads(capsys.readouterr().out)["behind"] == [{"name": "p-stale", "task": "01-src", "status": "stale"}]
    assert fan.run("accept", "02-use", "--reason", "reviewed") == 0
    out = capsys.readouterr().out
    assert "Accepted 1 step(s)" in out
    assert ("1 producer(s) behind the accepted step(s) are not fresh; the accepted step(s) read stale "
            "until they are built or accepted:\n  p-stale (stale)") in out
    assert fan.run("status", "02-use") == 3


def test_an_accepted_consumer_reruns_only_when_its_rebuilt_producer_changes_bytes(fan):
    fan.write("Code/use.sh", fan.read("Code/use.sh") + "# comment only\n")
    assert fan.run("accept", "02-use", "--reason", "reviewed") == 0
    fan.write("Code/stale.sh", fan.read("Code/stale.sh") + "# comment only\n")
    before = fan.run_times()
    assert fan.run("build", "02-use") == 0
    assert _changed(before, fan.run_times()) == {"p-stale"}  # identical bytes: the acceptance stands
    fan.write("Code/stale.sh", "mkdir -p output\necho stale2 > output/stale.txt\n")
    before = fan.run_times()
    assert fan.run("build", "02-use") == 0
    assert _changed(before, fan.run_times()) == {"p-stale", "use"}


def test_the_frontier_flags_a_stale_producer_but_not_an_unverified_one(project, monkeypatch):
    assert project.run("build", *CHAIN) == 0
    project.write("Code/a.sh", project.read("Code/a.sh").replace("hello", "HELLO"))  # same size
    rows = {row["path"]: row for row in frontier_rows(project.graph(), project.plan_root)}
    assert [(i["producer"], i["state"], i["build"]) for i in rows["02-b"]["inputs"]] == [
        ("01-a#build-a", "stale", "superra repro build 02-b")]
    Offline(monkeypatch, project.root).evict("Code/a.sh")
    _clear_cache(project)
    assert project.status("01-a").entry("build-a").status == "unverified"
    rows = {row["path"]: row for row in frontier_rows(project.graph(), project.plan_root)}
    assert rows["02-b"]["inputs"] == []


def test_upstream_behaves_exactly_like_the_default(fan, capsys):
    fan.write("Code/stale.sh", "mkdir -p output\necho stale2 > output/stale.txt\n")
    outputs = {}
    for flags in ((), ("--upstream",)):
        capsys.readouterr()
        codes = [fan.run("status", "02-use", *flags), fan.run("status", "02-use", "--json", *flags),
                 fan.run("build", "02-use", "--dry-run", *flags)]
        outputs[flags] = codes, capsys.readouterr().out
    assert outputs[()] == outputs[("--upstream",)]
    assert outputs[()][0] == [3, 3, 0]
    assert fan.run("status", "02-use", "--only", "--upstream") == 2  # contradictory


def test_status_reports_unverified_producers_on_one_line_with_size_and_boundary(project, monkeypatch, capsys):
    assert project.run("build", *CHAIN) == 0
    Offline(monkeypatch, project.root).evict("Code/a.sh")
    _clear_cache(project)
    size = (project.root / "Code/a.sh").stat().st_size
    capsys.readouterr()
    assert project.run("status", "02-b#check-b") == 0
    out = capsys.readouterr().out
    assert "2 producer(s) behind them: 1 fresh, 1 unverified" in out
    assert f"○ 1 producer(s) unverified, {size} B online-only here; tracing stops at build-a" in out
    assert re.search(rf"Files this machine cannot check \(1\):\n\s+Code/a.sh\s+{size} B\s+online-only here\n"
                     + re.escape(DOWNLOAD_NOTES), out)
    assert project.run("status", "02-b#check-b", "--json") == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert [p["name"] for p in payload["producers"]] == ["build-a", "build-b"]


def test_unverified_producers_without_a_known_size_say_so(project, monkeypatch, capsys):
    assert project.run("build", *CHAIN) == 0
    Offline(monkeypatch, project.root).placeholder("Code/a.sh")
    _clear_cache(project)
    capsys.readouterr()
    assert project.run("status", "02-b#check-b") == 0
    assert ("○ 1 producer(s) unverified, 1 online-only file(s) of unknown size here; tracing stops at build-a"
            in capsys.readouterr().out)


# ---------------------------------------------------------------------------
# Output stays bounded on a chain longer than the cap
# ---------------------------------------------------------------------------

def _long_chain(tmp_path, length: int) -> Project:
    """s01 → … → s<length>: the last step in its own task, the rest in 01-chain."""
    steps = ["  - name: s01\n    cmd: sh Code/seed.sh\n    deps:\n      - Code/seed.sh\n"
             "    outs:\n      - output/s01.txt\n"]
    for i in range(2, length):
        steps.append(f"  - name: s{i:02}\n    cmd: cp output/s{i - 1:02}.txt output/s{i:02}.txt\n"
                     f"    deps:\n      - output/s{i - 1:02}.txt\n    outs:\n      - output/s{i:02}.txt\n")
    head = '---\ntitle: "{t}"\nstatus: not-started\ndepends_on: []\n---\n\n## Objective\n\n{t}.\n\n## Reproduction\n\n```yaml\nsteps:\n'
    proj = Project(tmp_path / "long")
    proj.write("superRA/config.yaml", CONFIG)
    proj.write("superRA/01-chain/task.md", head.format(t="Chain") + "".join(steps) + "```\n")
    proj.write("superRA/02-end/task.md", head.format(t="End") + (
        f"  - name: s{length:02}\n    cmd: cp output/s{length - 1:02}.txt output/s{length:02}.txt\n"
        f"    deps:\n      - output/s{length - 1:02}.txt\n    outs:\n      - output/s{length:02}.txt\n```\n"))
    proj.write("Code/seed.sh", "mkdir -p output\necho seed > output/s01.txt\n")
    return proj


def test_default_status_and_build_output_stays_within_the_cap(tmp_path, capsys):
    length = OUTPUT_CAP + 5
    chain = _long_chain(tmp_path, length)
    assert chain.run("build", "02-end") == 0
    out = capsys.readouterr().out
    scope = next(line for line in out.splitlines() if line.startswith("Execution scope:"))
    assert scope.endswith(f"and {length - OUTPUT_CAP} more (`superra repro status 02-end --json` lists them)")
    preview = out.split("Also building")[1].split("✓")[0].strip().splitlines()
    assert preview[0] == f"{length - 1} producer(s) the targets read:"
    assert len(preview) == OUTPUT_CAP + 2
    assert preview[-1] == (f"  … and {length - 1 - OUTPUT_CAP} more producer(s); "
                           "`superra repro build 02-end --dry-run` lists them")

    chain.write("Code/seed.sh", "mkdir -p output\necho changed > output/s01.txt\n")
    assert chain.run("status", "02-end") == 3
    text = capsys.readouterr().out
    assert len(text.strip().splitlines()) <= OUTPUT_CAP + 6
    assert f"{length - 1} producer(s) behind them: {length - 1} stale" in text
    assert re.search(r"~ s01\s+stale\s+dependency Code/seed.sh changed", text)  # where staleness starts, first
    assert (f"  … and {length - 1 - OUTPUT_CAP} more producer(s) not fresh; "
            "`superra repro status 02-end --json` lists them") in text

    assert chain.run("status", "02-end", "--json") == 3
    payload = json.loads(capsys.readouterr().out)
    assert [s["name"] for s in payload["steps"]] == [f"s{length:02}"]
    assert len(payload["producers"]) == length - 1
    assert {(p["status"], p["local_status"]) for p in payload["producers"]} == {("stale", "stale"), ("stale", "fresh")}
    assert payload["ok"] is False
    assert payload["summary"]["total"] == 1 and payload["summary"]["stale"] == 1
    assert payload["summary"]["producers"]["total"] == length - 1

    capsys.readouterr()
    assert chain.run("build", "02-end") == 0  # only s01 reruns; identical copies downstream rerun as inputs change
    out = capsys.readouterr().out
    assert "Also building 1 producer(s)" in out
