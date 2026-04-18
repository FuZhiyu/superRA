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
    def test_defaults_from_to_main_when_omitted(self, repo_with_worktrees):
        source, destination = worktree_data_discovery.resolve_endpoints(
            repo_with_worktrees["a"],
            to_path=str(repo_with_worktrees["b"]),
            from_path=None,
        )

        assert source == repo_with_worktrees["main"].resolve()
        assert destination == repo_with_worktrees["b"].resolve()

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
    gitignored folder of --from (e.g., /repo/.worktrees/foo seeded from /repo)."""

    @pytest.fixture
    def repo_with_nested_worktree(self, tmp_path):
        repo = tmp_path / "repo"
        repo.mkdir()
        subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True, capture_output=True)

        (repo / "README.md").write_text("# Test\n", encoding="utf-8")
        (repo / ".gitignore").write_text(".worktrees/\noutput/\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True)

        (repo / "output").mkdir()
        (repo / "output" / "result.csv").write_text("a,b\n", encoding="utf-8")

        (repo / ".worktrees").mkdir()
        child = repo / ".worktrees" / "foo"
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

        assert ".worktrees" not in paths
        assert "output" in paths

    def test_nested_worktree_seed_does_not_self_reference(self, repo_with_nested_worktree):
        main = repo_with_nested_worktree["main"]
        child = repo_with_nested_worktree["child"]

        entries = worktree_data_discovery.discover_managed_entries(main, dest_worktree=child)
        sync_worktree_data.run_seed(entries, child, verbose=False)

        assert not (child / ".worktrees").exists()
        assert (child / "output" / "result.csv").exists()

    def test_no_dest_preserves_legacy_behavior(self, repo_with_nested_worktree):
        main = repo_with_nested_worktree["main"]

        entries = worktree_data_discovery.discover_managed_entries(main)
        paths = {e["path"] for e in entries}

        assert ".worktrees" in paths
