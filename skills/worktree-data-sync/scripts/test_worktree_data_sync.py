#!/usr/bin/env python3
"""Tests for worktree-data-sync scripts."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

import sync_worktree_data
import worktree_data_discovery


@pytest.fixture
def repo_with_worktrees(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()

    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True, capture_output=True)

    (repo / "README.md").write_text("# Test\n", encoding="utf-8")
    (repo / ".gitignore").write_text("output/\ndata/\ndata/  # data-sync:symlink\n", encoding="utf-8")

    subprocess.run(["git", "add", "README.md", ".gitignore"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True)

    (repo / "output").mkdir()
    (repo / "output" / "result.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    (repo / "output" / "new.csv").write_text("x,y\n7,8\n", encoding="utf-8")

    shared_data = tmp_path / "shared-data"
    shared_data.mkdir()
    (shared_data / "shared.txt").write_text("shared\n", encoding="utf-8")
    (repo / "data").symlink_to(shared_data)

    wt_a = tmp_path / "repo-a"
    wt_b = tmp_path / "repo-b"

    subprocess.run(["git", "worktree", "add", str(wt_a), "-b", "feat-a"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "worktree", "add", str(wt_b), "-b", "feat-b"], cwd=repo, check=True, capture_output=True)

    return {"main": repo, "a": wt_a, "b": wt_b}


@pytest.fixture
def second_repo_worktree(tmp_path):
    repo = tmp_path / "repo2"
    repo.mkdir()

    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True, capture_output=True)

    (repo / "README.md").write_text("# Repo2\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True)

    wt = tmp_path / "repo2-a"
    subprocess.run(["git", "worktree", "add", str(wt), "-b", "feat-a"], cwd=repo, check=True, capture_output=True)

    return wt


class TestEndpointResolution:
    def test_defaults_from_to_cwd_worktree_when_omitted(self, repo_with_worktrees):
        source, destination = worktree_data_discovery.resolve_endpoints(
            repo_with_worktrees["a"],
            to_path=str(repo_with_worktrees["b"]),
            from_path=None,
        )

        assert source == repo_with_worktrees["a"].resolve()
        assert destination == repo_with_worktrees["b"].resolve()

    def test_defaults_from_to_main_worktree_when_cwd_is_main(self, repo_with_worktrees):
        source, destination = worktree_data_discovery.resolve_endpoints(
            repo_with_worktrees["main"],
            to_path=str(repo_with_worktrees["b"]),
            from_path=None,
        )

        assert source == repo_with_worktrees["main"].resolve()
        assert destination == repo_with_worktrees["b"].resolve()

    def test_rejects_cwd_outside_any_worktree(self, repo_with_worktrees, monkeypatch, tmp_path):
        # A cwd inside the repo's git checkout always resolves under some known
        # worktree root, so the "outside" branch is reached by making
        # list_worktrees report roots that do not cover cwd (e.g. stale
        # worktree metadata git has not pruned yet).
        monkeypatch.setattr(
            worktree_data_discovery,
            "list_worktrees",
            lambda cwd: [repo_with_worktrees["main"].resolve(), repo_with_worktrees["b"].resolve()],
        )
        outside = tmp_path / "not-a-worktree"
        outside.mkdir()

        with pytest.raises(RuntimeError, match="not inside any worktree"):
            worktree_data_discovery.resolve_endpoints(
                outside,
                to_path=str(repo_with_worktrees["b"]),
                from_path=None,
            )

    def test_worktree_containing_returns_deepest_match(self, tmp_path):
        root = tmp_path / "repo-a"
        nested = root / "sub" / "dir"
        nested.mkdir(parents=True)

        result = worktree_data_discovery.get_worktree_containing(nested, [root])

        assert result == root.resolve()

    def test_accepts_explicit_from_to_worktrees(self, repo_with_worktrees):
        source, destination = worktree_data_discovery.resolve_endpoints(
            repo_with_worktrees["a"],
            to_path=str(repo_with_worktrees["b"]),
            from_path=str(repo_with_worktrees["a"]),
        )

        assert source == repo_with_worktrees["a"].resolve()
        assert destination == repo_with_worktrees["b"].resolve()

    def test_rejects_missing_to_worktree(self, repo_with_worktrees, tmp_path):
        with pytest.raises(ValueError, match="--to"):
            worktree_data_discovery.resolve_endpoints(
                repo_with_worktrees["a"],
                to_path=str(tmp_path / "not-a-worktree"),
                from_path=None,
            )

    def test_rejects_different_repo_endpoint(self, repo_with_worktrees, second_repo_worktree):
        with pytest.raises(ValueError, match="--to"):
            worktree_data_discovery.resolve_endpoints(
                repo_with_worktrees["a"],
                to_path=str(second_repo_worktree),
                from_path=None,
            )

    def test_rejects_same_from_to(self, repo_with_worktrees):
        with pytest.raises(ValueError, match="must be different"):
            worktree_data_discovery.resolve_endpoints(
                repo_with_worktrees["a"],
                to_path=str(repo_with_worktrees["a"]),
                from_path=str(repo_with_worktrees["a"]),
            )


class TestSeedDiffApply:
    def test_seed_copies_missing_without_overwrite(self, repo_with_worktrees):
        main = repo_with_worktrees["main"]
        target = repo_with_worktrees["a"]

        (target / "output").mkdir(parents=True, exist_ok=True)
        (target / "output" / "result.csv").write_text("local,keep\n", encoding="utf-8")

        entries = worktree_data_discovery.discover_managed_entries(main)
        summary = sync_worktree_data.run_seed(entries, target, verbose=False)

        assert summary.copied >= 1
        assert (target / "output" / "new.csv").exists()
        assert (target / "output" / "result.csv").read_text(encoding="utf-8") == "local,keep\n"
        assert (target / "data").is_symlink()
        assert (target / "data").resolve() == (main / "data").resolve()

    def test_seed_force_cow_copies_symlink_only_roots(self, repo_with_worktrees):
        main = repo_with_worktrees["main"]
        target = repo_with_worktrees["a"]

        entries = worktree_data_discovery.discover_managed_entries(main)
        summary = sync_worktree_data.run_seed(entries, target, seed_sync_mode="force-cow", verbose=False)

        assert summary.copied >= 1
        assert (target / "data").is_dir()
        assert not (target / "data").is_symlink()
        assert (target / "data" / "shared.txt").read_text(encoding="utf-8") == "shared\n"

    def test_seed_force_symlink_creates_shared_root_symlink(self, repo_with_worktrees):
        main = repo_with_worktrees["main"]
        target = repo_with_worktrees["a"]

        entries = worktree_data_discovery.discover_managed_entries(main)
        summary = sync_worktree_data.run_seed(entries, target, seed_sync_mode="force-symlink", verbose=False)

        assert summary.symlinked >= 1
        assert (target / "data").is_symlink()
        assert (target / "data").resolve() == (main / "data").resolve()

    def test_seed_force_symlink_creates_regular_root_symlink(self, repo_with_worktrees):
        main = repo_with_worktrees["main"]
        target = repo_with_worktrees["a"]

        entries = worktree_data_discovery.discover_managed_entries(main)
        summary = sync_worktree_data.run_seed(entries, target, seed_sync_mode="force-symlink", verbose=False)

        assert summary.symlinked >= 1
        assert (target / "output").is_symlink()
        assert (target / "output").resolve() == (main / "output").resolve()

    def test_seed_force_symlink_skips_existing_root(self, repo_with_worktrees):
        main = repo_with_worktrees["main"]
        target = repo_with_worktrees["a"]

        (target / "output").mkdir(parents=True, exist_ok=True)
        (target / "output" / "local.txt").write_text("keep\n", encoding="utf-8")

        entries = worktree_data_discovery.discover_managed_entries(main)
        summary = sync_worktree_data.run_seed(entries, target, seed_sync_mode="force-symlink", verbose=False)

        assert summary.skipped_existing >= 1
        assert (target / "output").is_dir()
        assert not (target / "output").is_symlink()
        assert (target / "output" / "local.txt").read_text(encoding="utf-8") == "keep\n"

    def test_diff_outputs_stable_change_records(self, repo_with_worktrees):
        main = repo_with_worktrees["main"]
        target = repo_with_worktrees["a"]

        (target / "output").mkdir(parents=True, exist_ok=True)
        (target / "output" / "result.csv").write_text("a,b\n9,9\n", encoding="utf-8")

        entries = worktree_data_discovery.discover_managed_entries(main)
        changes = sync_worktree_data.collect_changes(
            entries,
            target,
            include_unmodified=True,
            use_hash=True,
            verbose=False,
        )

        assert any(change.status == "modified" for change in changes)

        first = asdict(changes[0])
        assert "source_path" in first
        assert "destination_path" in first
        assert "target_path" in first
        assert "directory" in first

    def test_apply_overwrite_copies_source_to_target(self, repo_with_worktrees):
        main = repo_with_worktrees["main"]
        target = repo_with_worktrees["a"]

        (target / "output").mkdir(parents=True, exist_ok=True)
        (target / "output" / "result.csv").write_text("old\n", encoding="utf-8")

        entries = worktree_data_discovery.discover_managed_entries(main)
        changes = [
            asdict(change)
            for change in sync_worktree_data.collect_changes(entries, target, include_unmodified=False, use_hash=True, verbose=False)
        ]

        success, failure = sync_worktree_data.process_changes(changes, "overwrite", "_unused")

        assert success >= 1
        assert failure == 0
        assert (target / "output" / "result.csv").read_text(encoding="utf-8") == "a,b\n1,2\n"

    def test_apply_rename_keeps_existing_target_and_writes_copy(self, repo_with_worktrees):
        main = repo_with_worktrees["main"]
        target = repo_with_worktrees["a"]

        (target / "output").mkdir(parents=True, exist_ok=True)
        (target / "output" / "result.csv").write_text("old\n", encoding="utf-8")

        entries = worktree_data_discovery.discover_managed_entries(main)
        changes = [
            asdict(change)
            for change in sync_worktree_data.collect_changes(entries, target, include_unmodified=False, use_hash=True, verbose=False)
        ]

        success, failure = sync_worktree_data.process_changes(changes, "rename", "_copy")

        assert success >= 1
        assert failure == 0
        assert (target / "output" / "result.csv").read_text(encoding="utf-8") == "old\n"
        assert (target / "output" / "result_copy.csv").read_text(encoding="utf-8") == "a,b\n1,2\n"

    def test_diff_json_round_trip_with_apply_from_json(self, repo_with_worktrees, tmp_path):
        main = repo_with_worktrees["main"]
        target = repo_with_worktrees["a"]

        (target / "output").mkdir(parents=True, exist_ok=True)
        (target / "output" / "result.csv").write_text("old\n", encoding="utf-8")

        entries = worktree_data_discovery.discover_managed_entries(main)
        changes = [asdict(change) for change in sync_worktree_data.collect_changes(entries, target, use_hash=True, verbose=False)]

        payload = {
            "from_worktree": str(main),
            "to_worktree": str(target),
            "changes": changes,
            "summary": sync_worktree_data.summarize_changes([
                sync_worktree_data.FileChange(**change) for change in changes
            ]),
        }
        json_path = tmp_path / "changes.json"
        json_path.write_text(json.dumps(payload), encoding="utf-8")

        success, failure = sync_worktree_data.process_from_json(json_path, "overwrite", "_unused")
        assert success >= 1
        assert failure == 0
        assert (target / "output" / "result.csv").read_text(encoding="utf-8") == "a,b\n1,2\n"

    def test_apply_files_rejects_parent_traversal(self, repo_with_worktrees):
        main = repo_with_worktrees["main"]
        target = repo_with_worktrees["a"]
        entries = worktree_data_discovery.discover_managed_entries(main)

        success, failure = sync_worktree_data.process_files(
            entries,
            target,
            ["output/../escape.txt"],
            "overwrite",
            "_unused",
            verbose=False,
        )
        assert success == 0
        assert failure == 1
        assert not (target.parent / "escape.txt").exists()

    def test_apply_from_json_rejects_endpoint_mismatch(self, repo_with_worktrees, tmp_path):
        main = repo_with_worktrees["main"]
        target_a = repo_with_worktrees["a"]
        target_b = repo_with_worktrees["b"]
        entries = worktree_data_discovery.discover_managed_entries(main)

        payload = {
            "from_worktree": str(main),
            "to_worktree": str(target_a),
            "changes": [],
            "summary": {"new": 0, "modified": 0, "unchanged": 0},
        }
        json_path = tmp_path / "mismatch.json"
        json_path.write_text(json.dumps(payload), encoding="utf-8")

        with pytest.raises(ValueError, match="to_worktree"):
            sync_worktree_data.process_from_json(
                json_path,
                "overwrite",
                "_unused",
                source_root=main,
                destination_root=target_b,
                entries=entries,
            )

    def test_apply_from_json_ignores_external_target_path_and_re_roots_to_to(self, repo_with_worktrees, tmp_path):
        main = repo_with_worktrees["main"]
        target = repo_with_worktrees["a"]
        entries = worktree_data_discovery.discover_managed_entries(main)

        (target / "output").mkdir(parents=True, exist_ok=True)
        (target / "output" / "result.csv").write_text("old\n", encoding="utf-8")

        outside_target = tmp_path / "outside.csv"
        payload = {
            "from_worktree": str(main),
            "to_worktree": str(target),
            "changes": [
                {
                    "status": "modified",
                    "source_path": str(main / "output" / "result.csv"),
                    "target_path": str(outside_target),
                    "destination_path": str(outside_target),
                    "relative_path": "result.csv",
                    "directory": "output",
                    "size_source": 8,
                    "size_destination": 4,
                    "mtime_source": 0,
                    "mtime_destination": 0,
                }
            ],
            "summary": {"new": 0, "modified": 1, "unchanged": 0},
        }
        json_path = tmp_path / "reroot.json"
        json_path.write_text(json.dumps(payload), encoding="utf-8")

        success, failure = sync_worktree_data.process_from_json(
            json_path,
            "overwrite",
            "_unused",
            source_root=main,
            destination_root=target,
            entries=entries,
            verbose=False,
        )

        assert success == 1
        assert failure == 0
        assert not outside_target.exists()
        assert (target / "output" / "result.csv").read_text(encoding="utf-8") == "a,b\n1,2\n"

    def test_apply_from_json_rejects_source_outside_managed_roots(self, repo_with_worktrees, tmp_path):
        main = repo_with_worktrees["main"]
        target = repo_with_worktrees["a"]
        entries = worktree_data_discovery.discover_managed_entries(main)

        outside_source = tmp_path / "outside-source.txt"
        outside_source.write_text("bad\n", encoding="utf-8")

        payload = {
            "from_worktree": str(main),
            "to_worktree": str(target),
            "changes": [
                {
                    "status": "modified",
                    "source_path": str(outside_source),
                    "target_path": str(target / "output" / "result.csv"),
                    "destination_path": str(target / "output" / "result.csv"),
                    "relative_path": "result.csv",
                    "directory": "output",
                    "size_source": 4,
                    "size_destination": 4,
                    "mtime_source": 0,
                    "mtime_destination": 0,
                }
            ],
            "summary": {"new": 0, "modified": 1, "unchanged": 0},
        }
        json_path = tmp_path / "outside-source.json"
        json_path.write_text(json.dumps(payload), encoding="utf-8")

        with pytest.raises(ValueError, match="outside managed roots"):
            sync_worktree_data.process_from_json(
                json_path,
                "overwrite",
                "_unused",
                source_root=main,
                destination_root=target,
                entries=entries,
                verbose=False,
            )


class TestSeedFastPath:
    def test_fresh_clean_root_seeds_via_single_clone(self, monkeypatch, repo_with_worktrees):
        main = repo_with_worktrees["main"]
        target = repo_with_worktrees["a"]

        entries = worktree_data_discovery.discover_managed_entries(main)

        real_run = subprocess.run
        cp_calls: list[list[str]] = []

        def spy(cmd, *args, **kwargs):
            if isinstance(cmd, (list, tuple)) and cmd and cmd[0] == "cp":
                cp_calls.append([str(c) for c in cmd])
            return real_run(cmd, *args, **kwargs)

        monkeypatch.setattr(sync_worktree_data.subprocess, "run", spy)
        summary = sync_worktree_data.run_seed(entries, target, verbose=False)

        # The clean `output` root clones in a single recursive cp; `data` is symlinked (no cp).
        recursive_clones = [cmd for cmd in cp_calls if "-R" in cmd]
        assert len(recursive_clones) == 1
        assert len(cp_calls) == 1
        assert summary.errors == 0
        assert not summary.failures
        assert (target / "output" / "new.csv").exists()
        assert (target / "output" / "result.csv").read_text(encoding="utf-8") == "a,b\n1,2\n"
        assert (target / "data").is_symlink()

    def test_nested_dataless_yields_dirs_symlink_clones_and_batches(self, monkeypatch, repo_with_worktrees):
        main = repo_with_worktrees["main"]
        target = repo_with_worktrees["a"]
        out = main / "output"

        (out / "loose.txt").write_text("loose\n", encoding="utf-8")
        (out / "clean").mkdir()
        (out / "clean" / "keep.csv").write_text("k\n", encoding="utf-8")
        (out / "deep" / "mid").mkdir(parents=True)
        (out / "deep" / "mid" / "placeholder.bin").write_text("cloud\n", encoding="utf-8")
        (out / "deep" / "mid" / "other.txt").write_text("real\n", encoding="utf-8")

        monkeypatch.setattr(
            sync_worktree_data,
            "is_dataless",
            lambda path: Path(path).name == "placeholder.bin",
        )

        entries = worktree_data_discovery.discover_managed_entries(main)
        summary = sync_worktree_data.run_seed(entries, target, verbose=False)

        dst = target / "output"
        # Real directories along the contaminated path.
        assert dst.is_dir() and not dst.is_symlink()
        assert (dst / "deep").is_dir() and not (dst / "deep").is_symlink()
        assert (dst / "deep" / "mid").is_dir() and not (dst / "deep" / "mid").is_symlink()
        # Symlink for the dataless file; no materialization.
        assert (dst / "deep" / "mid" / "placeholder.bin").is_symlink()
        # Clean sibling cloned wholesale.
        assert (dst / "clean").is_dir()
        assert (dst / "clean" / "keep.csv").read_text(encoding="utf-8") == "k\n"
        # Loose files copied (batched) at both the root and the contaminated dir.
        assert (dst / "loose.txt").read_text(encoding="utf-8") == "loose\n"
        assert (dst / "result.csv").read_text(encoding="utf-8") == "a,b\n1,2\n"
        assert (dst / "deep" / "mid" / "other.txt").read_text(encoding="utf-8") == "real\n"
        assert summary.errors == 0

    def test_mostly_dataless_root_suggests_annotation_and_seeds_per_file(
        self, monkeypatch, capsys, repo_with_worktrees
    ):
        main = repo_with_worktrees["main"]
        target = repo_with_worktrees["a"]
        out = main / "output"

        for name in ("dl_1.csv", "dl_2.csv", "dl_3.csv"):
            (out / name).write_text("cloud\n", encoding="utf-8")

        monkeypatch.setattr(
            sync_worktree_data,
            "is_dataless",
            lambda path: Path(path).name.startswith("dl_"),
        )

        entries = worktree_data_discovery.discover_managed_entries(main)
        summary = sync_worktree_data.run_seed(entries, target, verbose=True)

        stderr = capsys.readouterr().err
        assert "data-sync:symlink" in stderr
        assert "output" in stderr

        dst = target / "output"
        assert dst.is_dir() and not dst.is_symlink()
        assert (dst / "dl_1.csv").is_symlink()
        assert (dst / "new.csv").is_file() and not (dst / "new.csv").is_symlink()
        assert (dst / "new.csv").read_text(encoding="utf-8") == "x,y\n7,8\n"
        assert summary.errors == 0

    def test_injected_copy_failure_records_per_path_reason(self, monkeypatch, repo_with_worktrees):
        main = repo_with_worktrees["main"]
        target = repo_with_worktrees["a"]

        # Existing destination routes through the merge walk, whose loose copies batch.
        (target / "output").mkdir(parents=True, exist_ok=True)
        (target / "output" / "result.csv").write_text("local\n", encoding="utf-8")

        entries = worktree_data_discovery.discover_managed_entries(main)

        def fail_cp(cmd, *args, **kwargs):
            raise subprocess.CalledProcessError(1, cmd)

        monkeypatch.setattr(sync_worktree_data.subprocess, "run", fail_cp)
        monkeypatch.setattr(sync_worktree_data, "cow_copy_file", lambda *a, **k: False)

        summary = sync_worktree_data.run_seed(entries, target, verbose=False)

        assert summary.errors >= 1
        assert summary.failures
        assert summary.errors == len(summary.failures)
        assert any("new.csv" in path for path, _reason in summary.failures)

    def test_seed_failure_emits_capped_listing(self, capsys):
        summary = sync_worktree_data.SeedSummary()
        for idx in range(25):
            summary.record_failure(f"output/file_{idx}.csv", "copy failed")

        sync_worktree_data.emit_seed_failures(summary, limit=20)

        err = capsys.readouterr().err
        assert "Seed encountered 25 error(s):" in err
        assert "output/file_0.csv: copy failed" in err
        assert "output/file_19.csv" in err
        assert "output/file_20.csv" not in err
        assert "and 5 more" in err

    def test_cli_seed_nonzero_exit_on_failure(self, monkeypatch, capsys, repo_with_worktrees):
        main = repo_with_worktrees["main"]
        target = repo_with_worktrees["a"]

        failing = sync_worktree_data.SeedSummary()
        failing.record_failure(str(main / "output" / "new.csv"), "copy failed")
        monkeypatch.setattr(sync_worktree_data, "run_seed", lambda *a, **k: failing)
        monkeypatch.setattr(
            sync_worktree_data.sys,
            "argv",
            ["sync_worktree_data.py", "--to", str(target), "--mode", "seed"],
        )
        monkeypatch.chdir(main)

        with pytest.raises(SystemExit) as excinfo:
            sync_worktree_data.main()

        assert excinfo.value.code == 1
        err = capsys.readouterr().err
        assert "new.csv" in err
        assert "copy failed" in err


class TestCliSurface:
    def test_cli_rejects_delete_action(self, repo_with_worktrees):
        script = SCRIPTS_DIR / "sync_worktree_data.py"
        proc = subprocess.run(
            [
                sys.executable,
                str(script),
                "--to",
                str(repo_with_worktrees["a"]),
                "--mode",
                "apply",
                "--action",
                "delete",
            ],
            cwd=repo_with_worktrees["main"],
            capture_output=True,
            text=True,
        )
        assert proc.returncode != 0

    def test_cli_has_no_sandbox_option(self, repo_with_worktrees):
        script = SCRIPTS_DIR / "sync_worktree_data.py"
        proc = subprocess.run(
            [
                sys.executable,
                str(script),
                "--to",
                str(repo_with_worktrees["a"]),
                "--mode",
                "diff",
                "--deny-sandbox-bypass",
            ],
            cwd=repo_with_worktrees["main"],
            capture_output=True,
            text=True,
        )
        assert proc.returncode != 0
        assert "unrecognized arguments" in proc.stderr

    def test_cli_rejects_seed_sync_mode_with_diff(self, repo_with_worktrees):
        script = SCRIPTS_DIR / "sync_worktree_data.py"
        proc = subprocess.run(
            [
                sys.executable,
                str(script),
                "--to",
                str(repo_with_worktrees["a"]),
                "--mode",
                "diff",
                "--seed-sync-mode",
                "force-cow",
            ],
            cwd=repo_with_worktrees["main"],
            capture_output=True,
            text=True,
        )
        assert proc.returncode != 0
        assert "--seed-sync-mode is only valid with --mode seed" in proc.stderr

    def test_cli_rejects_seed_sync_mode_with_apply(self, repo_with_worktrees):
        script = SCRIPTS_DIR / "sync_worktree_data.py"
        proc = subprocess.run(
            [
                sys.executable,
                str(script),
                "--to",
                str(repo_with_worktrees["a"]),
                "--mode",
                "apply",
                "--action",
                "overwrite",
                "--seed-sync-mode",
                "force-symlink",
            ],
            cwd=repo_with_worktrees["main"],
            capture_output=True,
            text=True,
        )
        assert proc.returncode != 0
        assert "--seed-sync-mode is only valid with --mode seed" in proc.stderr

    def test_cli_seed_dry_run_reports_seed_mode_without_mutation(self, repo_with_worktrees):
        script = SCRIPTS_DIR / "sync_worktree_data.py"
        target = repo_with_worktrees["a"]
        proc = subprocess.run(
            [
                sys.executable,
                str(script),
                "--to",
                str(target),
                "--mode",
                "seed",
                "--seed-sync-mode",
                "force-symlink",
                "--dry-run",
            ],
            cwd=repo_with_worktrees["main"],
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0
        assert "Seed mode: force-symlink" in proc.stdout
        assert not (target / "output").exists()
        assert not (target / "data").exists()

    def test_cli_seed_defaults_from_cwd_worktree_without_from_flag(self, repo_with_worktrees):
        script = SCRIPTS_DIR / "sync_worktree_data.py"
        wt_a = repo_with_worktrees["a"]
        wt_b = repo_with_worktrees["b"]

        (wt_a / "output").mkdir(parents=True, exist_ok=True)
        (wt_a / "output" / "from_a.csv").write_text("a-only\n", encoding="utf-8")

        proc = subprocess.run(
            [sys.executable, str(script), "--to", str(wt_b), "--mode", "seed"],
            cwd=wt_a,
            capture_output=True,
            text=True,
        )

        assert proc.returncode == 0
        assert f"From: {wt_a.resolve()}" in proc.stdout
        assert (wt_b / "output" / "from_a.csv").exists()
        assert not (wt_b / "output" / "result.csv").exists()


class TestAnnotationCompatibility:
    def test_supports_new_and_legacy_annotation_tags(self, tmp_path):
        repo = tmp_path / "repo"
        repo.mkdir()
        (repo / ".gitignore").write_text(
            "data/\n"
            "data/  # data-sync:symlink\n"
            "cache/**\n"
            "cache/**  # worktree:symlink\n",
            encoding="utf-8",
        )

        annotations = worktree_data_discovery.parse_data_sync_annotations(repo)
        assert "data" in annotations
        assert "cache" in annotations


class TestDiscoveryPrecision:
    """Built-in denylist and tracked-symlink exclusion for managed-path discovery."""

    @staticmethod
    def _init_repo(repo: Path) -> None:
        repo.mkdir()
        subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True, capture_output=True)

    def test_denylisted_entries_excluded_data_dir_kept(self, tmp_path):
        repo = tmp_path / "repo"
        self._init_repo(repo)

        (repo / "README.md").write_text("# Test\n", encoding="utf-8")
        (repo / ".gitignore").write_text(
            ".venv/\n__pycache__/\n.DS_Store\ndata/\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "README.md", ".gitignore"], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True)

        (repo / ".venv").mkdir()
        (repo / ".venv" / "pyvenv.cfg").write_text("home = /usr\n", encoding="utf-8")
        (repo / "__pycache__").mkdir()
        (repo / "__pycache__" / "mod.cpython-311.pyc").write_bytes(b"\x00")
        (repo / ".DS_Store").write_bytes(b"\x00")
        (repo / "data").mkdir()
        (repo / "data" / "real.csv").write_text("a,b\n1,2\n", encoding="utf-8")

        entries = worktree_data_discovery.discover_managed_entries(repo)
        paths = {e["path"] for e in entries}

        assert ".venv" not in paths
        assert "__pycache__" not in paths
        assert ".DS_Store" not in paths
        assert "data" in paths

    def test_denylisted_root_with_annotation_is_symlink_only(self, tmp_path):
        repo = tmp_path / "repo"
        self._init_repo(repo)

        (repo / "README.md").write_text("# Test\n", encoding="utf-8")
        (repo / ".gitignore").write_text(
            ".cache/\n.cache/  # data-sync:symlink\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "README.md", ".gitignore"], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True)

        (repo / ".cache").mkdir()
        (repo / ".cache" / "big.bin").write_bytes(b"\x00" * 8)

        entries = worktree_data_discovery.discover_managed_entries(repo)
        by_path = {e["path"]: e for e in entries}

        assert ".cache" in by_path
        assert by_path[".cache"]["symlink_only"] is True

    def test_tracked_internal_symlink_excluded_external_symlink_kept(self, tmp_path):
        repo = tmp_path / "repo"
        self._init_repo(repo)

        (repo / "CLAUDE.md").write_text("# Guidelines\n", encoding="utf-8")
        (repo / "AGENTS.md").symlink_to("CLAUDE.md")

        external = tmp_path / "external-notes"
        external.mkdir()
        (external / "note.txt").write_text("note\n", encoding="utf-8")
        (repo / "notes").symlink_to(external)

        subprocess.run(["git", "add", "CLAUDE.md", "AGENTS.md"], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True)

        entries = worktree_data_discovery.discover_managed_entries(repo)
        paths = {e["path"] for e in entries}

        assert "AGENTS.md" not in paths
        assert "notes" in paths


class TestSafeJoinUnder:
    """Tests for _safe_join_under path validation."""

    def test_symlinked_directory_component(self, tmp_path):
        """_safe_join_under should succeed when a directory component is a symlink pointing outside base."""
        base = tmp_path / "worktree"
        base.mkdir()
        external = tmp_path / "external_data"
        external.mkdir()
        (external / "file.csv").write_text("data", encoding="utf-8")

        # Create symlink: worktree/Data -> ../external_data
        (base / "Data").symlink_to(external)

        # Should succeed — logical path stays within base
        result = sync_worktree_data._safe_join_under(base, Path("Data/file.csv"))
        assert result == Path(base / "Data" / "file.csv").absolute()

    def test_dotdot_traversal_rejected(self, tmp_path):
        """_safe_join_under should reject .. traversal that escapes base."""
        base = tmp_path / "worktree"
        base.mkdir()

        with pytest.raises(ValueError, match="escapes base root"):
            sync_worktree_data._safe_join_under(base, Path("../etc/passwd"))

    def test_normal_relative_path(self, tmp_path):
        """_safe_join_under should accept a normal relative path."""
        base = tmp_path / "worktree"
        base.mkdir()

        result = sync_worktree_data._safe_join_under(base, Path("src/main.py"))
        assert result == Path(base / "src" / "main.py").absolute()


class TestNestedWorktreeSelfReference:
    """Guard against self-referential links when --to is nested under a
    gitignored folder of --from (e.g., /repo/nested-worktrees/foo seeded from /repo).

    Uses a non-denylisted directory name so this exercises the self-reference
    guard specifically, independent of TestDiscoveryPrecision's denylist coverage
    of the conventional ".worktrees" name.
    """

    @pytest.fixture
    def repo_with_nested_worktree(self, tmp_path):
        repo = tmp_path / "repo"
        repo.mkdir()
        subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True, capture_output=True)

        (repo / "README.md").write_text("# Test\n", encoding="utf-8")
        (repo / ".gitignore").write_text("nested-worktrees/\noutput/\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True)

        (repo / "output").mkdir()
        (repo / "output" / "result.csv").write_text("a,b\n", encoding="utf-8")

        (repo / "nested-worktrees").mkdir()
        child = repo / "nested-worktrees" / "foo"
        subprocess.run(
            ["git", "worktree", "add", str(child), "-b", "foo"],
            cwd=repo, check=True, capture_output=True,
        )

        return {"main": repo, "child": child}

    def test_nested_worktree_excluded_from_managed_entries(self, repo_with_nested_worktree):
        main = repo_with_nested_worktree["main"]
        child = repo_with_nested_worktree["child"]

        entries = worktree_data_discovery.discover_managed_entries(main, dest_worktree=child)
        paths = {e["path"] for e in entries}

        assert "nested-worktrees" not in paths
        assert "output" in paths

    def test_nested_worktree_seed_does_not_self_reference(self, repo_with_nested_worktree):
        main = repo_with_nested_worktree["main"]
        child = repo_with_nested_worktree["child"]

        entries = worktree_data_discovery.discover_managed_entries(main, dest_worktree=child)
        sync_worktree_data.run_seed(entries, child, verbose=False)

        assert not (child / "nested-worktrees").exists()
        assert (child / "output" / "result.csv").exists()

    def test_no_dest_preserves_legacy_behavior(self, repo_with_nested_worktree):
        main = repo_with_nested_worktree["main"]

        entries = worktree_data_discovery.discover_managed_entries(main)
        paths = {e["path"] for e in entries}

        assert "nested-worktrees" in paths
