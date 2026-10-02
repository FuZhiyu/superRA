"""File checks never download: online-only and unreadable files read unknown, never missing or changed.

Online-only state is simulated by monkeypatching `_repro_state.file_flags`
(`SF_DATALESS`, by inode) and `has_placeholder_xattr` (legacy Dropbox); every
open of a simulated online-only path fails the test.
"""
from __future__ import annotations

import builtins
import json
import os
from pathlib import Path

import pytest

import _repro_state
from _repro_acceptance import accept, inspect_baseline
from _repro_scope import _bytes_verified
from _repro_state import SF_DATALESS, HashCache, ReproStateError, Unread, read_lock, stamp_ref
from test_repro_acceptance import review
from test_repro_runner import CHAIN, TASK_A, Project, _use_a_sidecar, project  # noqa: F401

DIR_TASK = """\
---
title: "Agg"
status: not-started
depends_on: []
---

## Objective

Aggregate.

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


class Offline:
    """Marks paths online-only and fails any open of one."""

    def __init__(self, monkeypatch, root: Path):
        self.root = root
        self.dataless: set[tuple[int, int]] = set()
        self.placeholders: set[str] = set()
        self.listed: list[str] = []
        monkeypatch.setattr(_repro_state, "file_flags", self._flags)
        monkeypatch.setattr(_repro_state, "has_placeholder_xattr",
                            lambda path: os.path.realpath(path) in self.placeholders)
        real_path_open, real_open, real_scandir = Path.open, builtins.open, os.scandir

        def path_open(path, *args, **kwargs):
            self._refuse(path)
            return real_path_open(path, *args, **kwargs)

        def plain_open(file, *args, **kwargs):
            if isinstance(file, (str, os.PathLike)):
                self._refuse(file)
            return real_open(file, *args, **kwargs)

        def scandir(path="."):
            self._refuse(path)
            self.listed.append(os.path.realpath(path))
            return real_scandir(path)

        monkeypatch.setattr(Path, "open", path_open)
        monkeypatch.setattr(builtins, "open", plain_open)
        monkeypatch.setattr(os, "scandir", scandir)

    def _flags(self, info):
        return SF_DATALESS if (info.st_dev, info.st_ino) in self.dataless else 0

    def _online(self, path) -> bool:
        try:
            info = os.stat(path)
        except OSError:
            return False
        return (info.st_dev, info.st_ino) in self.dataless or os.path.realpath(path) in self.placeholders

    def _refuse(self, path):
        if self._online(path):
            raise AssertionError(f"read online-only {path}")

    def evict(self, relative: str) -> None:
        """`SF_DATALESS`: size and mtime stay, content is not on disk."""
        info = os.stat(self.root / relative)
        self.dataless.add((info.st_dev, info.st_ino))

    def placeholder(self, relative: str) -> None:
        """A legacy Dropbox placeholder: zero bytes with the placeholder xattr."""
        path = self.root / relative
        path.write_bytes(b"")
        self.placeholders.add(os.path.realpath(path))


def _clear_cache(project) -> None:
    project.paths.cache_file.unlink(missing_ok=True)


@pytest.fixture
def offline(monkeypatch, project):
    return Offline(monkeypatch, project.root)


# ---------------------------------------------------------------------------
# File outcomes
# ---------------------------------------------------------------------------

def test_a_cached_online_only_file_keeps_its_hash_and_an_uncached_one_is_never_opened(project, offline):
    assert project.run("build", *CHAIN) == 0
    offline.evict("output/a.txt")
    assert project.states(*CHAIN) == {"build-a": "fresh", "build-b": "fresh", "check-b": "fresh"}

    _clear_cache(project)
    report = project.status(*CHAIN)
    assert report.entry("build-a").status == "unverified"
    assert report.entry("build-a").reason == "output ${OUT}/a.txt is online-only here"
    row = next(r for r in report.entry("build-b").to_dict()["files"] if r["node"] == "${OUT}/a.txt")
    assert row == {"node": "${OUT}/a.txt", "role": "dependency", "outcome": "unknown",
                   "online_only": True, "size": (project.root / "output/a.txt").stat().st_size}
    assert report.entry("build-b").status == "unverified"  # its own evidence; nothing upstream blocks


def test_an_uncached_online_only_file_whose_size_differs_from_the_lock_reads_changed(project, offline):
    assert project.run("build", *CHAIN) == 0
    assert read_lock(project.paths.lock_file)["build-b"].sizes["${OUT}/a.txt"] == len("hello\n")
    project.write("output/a.txt", "a longer replacement\n")
    offline.evict("output/a.txt")
    _clear_cache(project)
    entry = project.status(*CHAIN).entry("build-b")
    assert entry.local_status == "stale"
    assert "dependency ${OUT}/a.txt changed" in entry.local_reason


def test_a_version_2_lock_without_sizes_still_reads(project, offline):
    assert project.run("build", *CHAIN) == 0
    document = json.loads(project.read("repro-lock.json"))
    assert document["version"] == 2
    for raw in document["steps"].values():
        raw.pop("sizes")
    project.write("repro-lock.json", json.dumps(document))
    assert project.states(*CHAIN) == {"build-a": "fresh", "build-b": "fresh", "check-b": "fresh"}
    project.write("output/a.txt", "a longer replacement\n")  # no recorded size: unknown, not changed
    offline.evict("output/a.txt")
    _clear_cache(project)
    assert project.status(*CHAIN).entry("build-b").local_status == "unverified"


def test_a_legacy_placeholder_never_hashes_as_empty_or_reads_changed_for_its_zero_size(project, offline):
    assert project.run("build", *CHAIN) == 0
    offline.placeholder("Code/a.sh")
    cache = HashCache()
    assert cache.file_hash(project.root / "Code/a.sh") == Unread("online-only")
    assert cache.probe(project.root / "Code/a.sh") == (True, None)
    entry = project.status(*CHAIN).entry("build-a")  # the persistent cache holds the real file's key
    assert entry.status == "unverified"
    assert entry.reason == "dependency Code/a.sh is online-only here"


def test_a_directory_is_checked_before_it_is_listed(tmp_path, monkeypatch):
    proj = Project(tmp_path / "dir")
    proj.write("superRA/01-agg/task.md", DIR_TASK)
    proj.write("Data/panel/y2020/p.csv", "1\n")
    proj.write("Data/panel/y2021/p.csv", "2\n")
    (proj.root / "output").mkdir()
    assert proj.run("build", ".") == 0
    offline = Offline(monkeypatch, proj.root)
    offline.evict("Data/panel/y2021")
    entry = proj.status(".").entry("agg")
    assert entry.status == "unverified"
    assert entry.reason == "dependency Data/panel is online-only here"
    assert os.path.realpath(proj.root / "Data/panel/y2021") not in offline.listed
    assert entry.files[0]["online_only"] is True and entry.files[0]["size"] is None


def test_a_read_error_on_an_existing_output_is_unverified_never_missing(project):
    assert project.run("build", *CHAIN) == 0
    _clear_cache(project)
    out = project.root / "output/b.txt"
    out.chmod(0)
    try:
        report = project.status(*CHAIN)
    finally:
        out.chmod(0o644)
    assert report.entry("build-b").status == "unverified"
    assert report.entry("build-b").reason == "output ${OUT}/b.txt is unreadable here"
    assert report.entry("check-b").status == "unverified"


def test_an_absent_output_makes_its_producer_missing(project):
    assert project.run("build", *CHAIN) == 0
    (project.root / "output/a.txt").unlink()
    report = project.status(*CHAIN)
    assert report.entry("build-a").status == "missing"
    assert report.entry("build-b").status == "stale"


# ---------------------------------------------------------------------------
# Precedence and the cascade
# ---------------------------------------------------------------------------

def test_failed_never_built_and_passed_elsewhere_outrank_an_online_only_input(project, offline):
    from _repro_state import write_run_record
    assert project.run("build", *CHAIN) == 0
    (project.root / stamp_ref("check-b")).unlink()
    offline.evict("output/b.txt")  # cached: check-b passed at these inputs on another machine
    assert project.status(*CHAIN).entry("check-b").status == "fresh"

    _clear_cache(project)
    assert project.status(*CHAIN).entry("check-b").status == "unverified"
    write_run_record(project.paths, "build-b", {"outcome": "failed", "log": "x.log"})
    assert project.status(*CHAIN).entry("build-b").status == "failed"
    write_run_record(project.paths, "build-b", {"outcome": "running", "pid": 999999})
    assert project.status(*CHAIN).entry("build-b").status == "failed"

    project.write("superRA/01-a/task.md", TASK_A.replace("build-a", "build-a2"))
    offline.evict("Code/a.sh")
    _clear_cache(project)
    entry = project.status(*CHAIN).entry("build-a2")
    assert (entry.status, entry.reason) == ("missing", "never built")
    assert entry.files[0]["outcome"] == "unknown" and entry.files[0]["online_only"] is True


def test_the_cascade_names_the_origin_step_two_levels_up(project):
    assert project.run("build", *CHAIN) == 0
    project.write("Code/a.sh", "mkdir -p output\necho changed > output/a.txt\n")
    report = project.status(*CHAIN)
    assert report.entry("build-a").status == "stale"
    check = report.entry("check-b")
    assert (check.status, check.local_status, check.origin) == ("stale", "fresh", "build-a")
    assert check.reason == "upstream step 'build-a' is stale"
    assert report.entry("build-b").origin == "build-a"


def test_an_unverified_producer_lifts_nothing_and_a_stale_one_lifts_an_unverified_step(project, offline):
    assert project.run("build", *CHAIN) == 0
    offline.evict("output/b.txt")
    _clear_cache(project)
    report = project.status(*CHAIN)
    assert report.entry("build-b").status == "unverified"
    assert report.entry("check-b").status == "unverified"  # reads b.txt itself; build-b lifts nothing

    project.write("Code/a.sh", "mkdir -p output\necho changed > output/a.txt\n")
    check = project.status(*CHAIN).entry("check-b")
    assert (check.status, check.local_status, check.origin) == ("stale", "unverified", "build-a")


def test_build_never_runs_an_unverified_step(project, offline, capsys):
    assert project.run("build", *CHAIN) == 0
    before = project.run_times()
    offline.evict("Code/a.sh")
    _clear_cache(project)
    capsys.readouterr()
    assert project.run("build", *CHAIN) == 0
    assert project.run_times() == before
    assert "3 step(s): 2 unchanged, 1 unverified" in capsys.readouterr().out


def test_a_stale_step_never_starts_on_an_online_only_input_even_a_cached_one(project, offline, capsys):
    assert project.run("build", *CHAIN) == 0
    project.write("Code/b.sh", "cat output/a.txt > output/b.txt\n")
    offline.evict("output/a.txt")  # still in the hash cache: hashable, yet reading it downloads it
    assert project.status(*CHAIN).entry("build-b").local_status == "stale"
    before = project.run_times()
    capsys.readouterr()
    assert project.run("build", "02-b#build-b") == 1
    assert "cannot start: input ${OUT}/a.txt is online-only here" in capsys.readouterr().out
    assert project.run_times()["build-b"] == before["build-b"]
    from _repro_state import read_run_record
    assert read_run_record(project.paths, "build-b").get("outcome") == "success"  # no failed run recorded


def test_forcing_an_unverified_step_refuses_and_runs_nothing(project, offline, capsys):
    assert project.run("build", *CHAIN) == 0
    before = project.run_times()
    offline.evict("Code/a.sh")
    _clear_cache(project)
    assert project.status("01-a").entry("build-a").status == "unverified"
    capsys.readouterr()
    assert project.run("build", "01-a#build-a", "--force") == 1
    assert "cannot start: input Code/a.sh is online-only here" in capsys.readouterr().out
    assert project.run_times() == before


def test_edit_detection_never_opens_an_online_only_file_or_lists_an_online_only_directory(tmp_path, monkeypatch):
    import _edit_detect
    import task_hook
    proj = Project(tmp_path / "dir")
    proj.write("superRA/01-agg/task.md", DIR_TASK)
    proj.write("Data/panel/y2020/p.csv", "1\n")
    proj.write("Data/panel/y2021/p.csv", "2\n")
    offline = Offline(monkeypatch, proj.root)
    offline.evict("Data/panel/y2021")
    offline.evict("Data/panel/y2020/p.csv")
    watch = task_hook._repro_watch(proj.plan_root)
    assert _edit_detect.detect(proj.plan_root, "s1", lambda: watch[0], lambda: watch[1]) == []
    assert os.path.realpath(proj.root / "Data/panel/y2021") not in offline.listed
    baseline = json.loads(next((proj.root / ".superra-repro/hook-baseline").glob("s1.json")).read_text())
    assert baseline["files"][str(proj.root / "Data/panel/y2020/p.csv")][2] is None  # kept, never hashed


def test_a_stale_step_never_starts_on_an_input_it_cannot_hash(project, offline, capsys):
    assert project.run("build", *CHAIN) == 0
    project.write("Code/b.sh", "cat output/a.txt > output/b.txt\n")
    offline.evict("output/a.txt")
    _clear_cache(project)
    assert project.status(*CHAIN).entry("build-b").local_status == "stale"
    capsys.readouterr()
    assert project.run("build", "02-b#build-b") == 1
    assert "cannot start: input ${OUT}/a.txt is online-only here" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Reads outside the hash cache
# ---------------------------------------------------------------------------

def test_explain_never_opens_an_online_only_file(project, offline, capsys):
    assert project.run("build", *CHAIN) == 0
    project.write("Code/a.sh", "mkdir -p output\necho changed > output/a.txt\n")
    assert project.states("01-a")["build-a"] == "stale"  # caches the new bytes
    offline.evict("Code/a.sh")
    capsys.readouterr()
    assert project.run("explain", "01-a#build-a") == 0
    out = capsys.readouterr().out
    assert "dependency Code/a.sh" in out and "snapshot" not in out

    _clear_cache(project)
    assert project.run("explain", "Code/a.sh") == 0
    assert capsys.readouterr().out.startswith("Code/a.sh  online-only here")


def test_accept_refuses_a_file_it_cannot_hash_and_its_preview_never_opens_one(project, offline):
    assert project.run("build", *CHAIN) == 0
    project.write("Code/a.sh", "mkdir -p output\necho hello > output/a.txt\n# comment\n")
    assert project.states("01-a")["build-a"] == "stale"
    offline.evict("Code/a.sh")
    with pytest.raises(ReproStateError, match=r"build-a: cannot record Code/a.sh, which is online-only here"):
        accept(project.graph(), project.paths, ["01-a#build-a"], "reviewed", {})
    details = inspect_baseline(project.graph(), project.graph().step("build-a"), project.paths)
    row = next(r for r in details["diffs"] if r["node"] == "Code/a.sh")
    assert row["diff"] is None and row["history"] == "unavailable"


def test_an_acceptance_over_uncached_online_only_files_reads_unverified_not_invalid(project, offline):
    assert project.run("build", *CHAIN) == 0
    project.write("Code/a.sh", "mkdir -p output\necho hello > output/a.txt\n# comment\n")
    review(project)
    assert project.status(*CHAIN).entry("build-a").reason == "reviewed baseline"
    offline.evict("Code/a.sh")
    _clear_cache(project)
    entry = project.status(*CHAIN).entry("build-a")
    assert entry.status == "unverified" and entry.acceptance_invalid is None
    assert entry.reason == "reviewed baseline; Code/a.sh is online-only here"


def test_a_sidecar_read_never_opens_an_online_only_sidecar(project, offline):
    _use_a_sidecar(project)
    assert project.run("build", *CHAIN) == 0
    offline.evict("output/a.txt.sha256")
    item = {"digest": HashCache().file_hash(project.root / "output/a.txt"), "provenance": "",
            "resolved": "output/a.txt"}
    assert _bytes_verified(project.graph(), project.paths, item) is False
