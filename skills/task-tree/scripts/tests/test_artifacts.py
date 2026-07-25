#!/usr/bin/env python3
"""Companion-file discovery, security, API, watcher, and export regressions."""

from __future__ import annotations

import asyncio
import base64
import json
import re
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

SCRIPTS_DIR = Path(__file__).parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))

import _artifacts
import _task_io
import _task_validate
import plan_dashboard
import plan_migrate
import task_create
import task_hook
import task_link
import task_read
import task_rename
import task_update
from _task_io import walk_plan
from conftest import _write_task_md, _write_tiny_png


def _tree(tmp_path: Path, root_name: str = "superRA") -> Path:
    root = tmp_path / root_name
    root.mkdir(parents=True)
    _write_task_md(root / "task.md", "Root", "in-progress", objective="Root task.")
    child = root / "child"
    child.mkdir()
    _write_task_md(child / "task.md", "Child", "not-started", objective="Child task.")
    return root


def _task(root: Path, path: str = ""):
    tree = walk_plan(root)
    if not path:
        return tree
    return next(task for task in tree.children if task.path == path)


def _client_for(root: Path):
    from starlette.testclient import TestClient

    plan_dashboard.PLAN_ROOT = root
    plan_dashboard._worktree_cache.clear()
    plan_dashboard._jinja_env = None
    plan_dashboard.rebuild_tree()
    return TestClient(plan_dashboard.app, raise_server_exceptions=True)


def _standalone_payload(html: str) -> dict:
    match = re.search(r"var STANDALONE_ARTIFACTS = (.*?);\n", html)
    assert match is not None
    return json.loads(match.group(1))


class TestArtifactDiscovery:
    def test_direct_attachment_and_legacy_classification_preserves_task_ownership(
        self, tmp_path
    ):
        root = _tree(tmp_path)
        (root / "note.md").write_text("# note", encoding="utf-8")
        (root / "model.py").write_text("print('ok')\n", encoding="utf-8")
        (root / "analysis.R").write_text("summary(x)\n", encoding="utf-8")
        (root / "legacy.bin").write_bytes(b"\x00\x01")
        (root / "comments.yaml").write_text("comments: []\n", encoding="utf-8")
        (root / ".hidden.md").write_text("hidden", encoding="utf-8")
        (root / "child" / "child-note.md").write_text("child", encoding="utf-8")

        deep = root / "attachments" / "bundle"
        for level in range(12):
            deep /= f"level-{level:02d}"
        deep.mkdir(parents=True)
        (root / "attachments" / "task.md").write_text("opaque asset", encoding="utf-8")
        (deep / "result.csv").write_text("x\n1\n", encoding="utf-8")
        (root / "attachments" / ".ipynb_checkpoints").mkdir()
        (root / "attachments" / ".ipynb_checkpoints" / "x.ipynb").write_text("{}")

        tree = walk_plan(root)
        assert [child.path for child in tree.children] == ["child"]
        manifest = _artifacts.build_manifest(root, tree)
        by_path = {entry["path"]: entry for entry in manifest["files"]}

        assert by_path["note.md"]["placement"] == "direct"
        assert by_path["model.py"]["kind"] == "python"
        assert by_path["analysis.R"]["kind"] == "r"
        assert by_path["legacy.bin"]["placement"] == "legacy"
        assert by_path["attachments/task.md"]["placement"] == "attachment"
        assert any(path.endswith("/result.csv") for path in by_path)
        assert "comments.yaml" not in by_path
        assert ".hidden.md" not in by_path
        assert "child/child-note.md" not in by_path
        assert not any(".ipynb_checkpoints" in path for path in by_path)

        child_manifest = _artifacts.build_manifest(root, _task(root, "child"))
        assert [entry["path"] for entry in child_manifest["files"]] == ["child-note.md"]

    def test_symlinks_and_ancillary_directories_are_ignored(self, tmp_path):
        root = _tree(tmp_path)
        outside = tmp_path / "outside.txt"
        outside.write_text("secret", encoding="utf-8")
        try:
            (root / "linked.txt").symlink_to(outside)
            (root / "attachments").mkdir()
            (root / "attachments" / "linked.txt").symlink_to(outside)
            (root / "attachments" / "linked-dir").symlink_to(tmp_path, target_is_directory=True)
        except OSError:
            pytest.skip("symlinks unavailable")
        scratch = root / "scratch"
        scratch.mkdir()
        (scratch / "ignored.md").write_text("scratch", encoding="utf-8")

        paths = {
            entry["path"]
            for entry in _artifacts.build_manifest(root, _task(root))["files"]
        }
        assert paths == set()

    def test_file_count_and_manifest_byte_budgets_truncate_deterministically(self, tmp_path):
        root = _tree(tmp_path)
        for name in ("a.md", "b.py", "c.jl"):
            (root / name).write_text(name, encoding="utf-8")
        task = _task(root)

        count_limited = _artifacts.build_manifest(
            root,
            task,
            limits=_artifacts.ArtifactLimits(max_files=2),
        )
        assert [entry["path"] for entry in count_limited["files"]] == ["a.md", "b.py"]
        assert count_limited["truncated"] is True
        assert count_limited["truncation_reason"] == "file-count-limit"

        byte_limited = _artifacts.build_manifest(
            root,
            task,
            limits=_artifacts.ArtifactLimits(
                max_manifest_bytes=260,
                manifest_entry_overhead=256,
            ),
        )
        assert len(byte_limited["files"]) == 1
        assert byte_limited["truncation_reason"] == "manifest-byte-limit"

    def test_traversal_budget_bounds_wide_entries_and_empty_directory_work(self, tmp_path):
        root = _tree(tmp_path)
        for index in range(24):
            (root / f"legacy-{index:02d}.bin").write_bytes(b"x")
        direct = _artifacts.build_manifest(
            root,
            _task(root),
            limits=_artifacts.ArtifactLimits(max_traversal_entries=8),
        )
        assert direct["traversal_entries"] == 8
        assert direct["truncated"] is True
        assert direct["truncation_reason"] == "traversal-entry-limit"

        empty_root = _tree(tmp_path / "empty")
        attachments = empty_root / "attachments"
        attachments.mkdir()
        for index in range(24):
            (attachments / f"empty-{index:02d}").mkdir()
        empty = _artifacts.build_manifest(
            empty_root,
            _task(empty_root),
            limits=_artifacts.ArtifactLimits(max_traversal_entries=8),
        )
        assert empty["files"] == []
        assert empty["traversal_entries"] == 8
        assert empty["truncation_reason"] == "traversal-entry-limit"


class TestAttachmentOpacity:
    def test_task_scanners_mutators_hooks_and_migrations_share_opaque_rule(
        self, tmp_path
    ):
        root = _tree(tmp_path)
        attachments = root / "attachments"
        attachments.mkdir()
        asset_md = attachments / "task.md"
        original = """---
title: "Opaque asset"
status: not-started
depends_on:
  - missing
review_status: revise
---

## Steps

- [ ] This is asset content.

## Workflow Status

Do not rewrite.
"""
        asset_md.write_text(original, encoding="utf-8")

        assert [path.parent for path in _task_io.iter_task_markdown_files(root)] == [
            root,
            root / "child",
        ]
        assert _task_validate.validate_plan(root) == []
        with pytest.raises(ValueError, match="reserved attachments"):
            _task_io.parse_task(asset_md, root)
        assert "attachments" not in task_read._sibling_map(root, _task(root, "child"))
        assert task_hook._task_path_from_file_path(asset_md) is None
        moved_asset = attachments / "renamed-bundle"
        moved_asset.mkdir()
        (moved_asset / "task.md").write_text("asset", encoding="utf-8")
        assert task_hook._detect_same_parent_rename(
            f"mv {attachments / 'bundle'} {moved_asset}",
            tmp_path,
            _task_io,
        ) is None
        assert plan_dashboard.rebuild_state_task(
            plan_dashboard._build_worktree_state("wt", root),
            "attachments",
        ) == (None, False)

        with pytest.raises(SystemExit):
            task_update.update_task(root, "attachments", status="approved")
        with pytest.raises(SystemExit):
            task_rename.rename_task(root, "attachments", "renamed-assets")
        with pytest.raises(SystemExit):
            task_create.create_task(root, "attachments/new-task", "Not a task")
        with pytest.raises(SystemExit):
            task_create.create_task(
                root,
                "new-task",
                "New task",
                depends_on=["attachments"],
            )
        with pytest.raises(SystemExit):
            task_link.link_task(root, "child", "attachments")

        assert plan_migrate.upgrade_v1_to_v2(root) == []
        assert plan_migrate.upgrade_status(root) == []
        assert asset_md.read_text(encoding="utf-8") == original


class TestArtifactResolution:
    @pytest.mark.parametrize(
        "requested",
        [
            "/etc/passwd",
            "../outside.txt",
            "attachments/../../outside.txt",
            ".hidden.md",
            "attachments/.hidden/x.txt",
            "child/child-note.md",
            "task.md",
        ],
    )
    def test_rejects_absolute_traversal_hidden_cross_task_and_reserved_paths(
        self, tmp_path, requested
    ):
        root = _tree(tmp_path)
        with pytest.raises(
            (_artifacts.ArtifactPathError, _artifacts.ArtifactSecurityError)
        ):
            _artifacts.resolve_artifact(root, _task(root), requested)

    def test_rejects_symlink_escape(self, tmp_path):
        root = _tree(tmp_path)
        outside = tmp_path / "outside.txt"
        outside.write_text("secret", encoding="utf-8")
        try:
            (root / "escape.txt").symlink_to(outside)
        except OSError:
            pytest.skip("symlinks unavailable")
        with pytest.raises(_artifacts.ArtifactSecurityError):
            _artifacts.resolve_artifact(root, _task(root), "escape.txt")


class TestArtifactAPI:
    def test_manifest_content_mime_download_and_exact_bytes(self, tmp_path):
        root = _tree(tmp_path)
        (root / "note.md").write_bytes(b"# caf\xc3\xa9\n")
        (root / "analysis.R").write_text("summary(x)\n", encoding="utf-8")
        (root / "unsafe.html").write_text("<script>alert(1)</script>", encoding="utf-8")
        (root / "attachments").mkdir()
        raw = b"\x00\xff\x10binary\r\n"
        (root / "attachments" / "raw.bin").write_bytes(raw)

        with _client_for(root) as client:
            manifest = client.get("/api/artifacts", params={"task": ""})
            assert manifest.status_code == 200
            assert {item["path"] for item in manifest.json()["files"]} == {
                "note.md",
                "analysis.R",
                "attachments/raw.bin",
                "unsafe.html",
            }

            note = client.get(
                "/api/artifact", params={"task": "", "path": "note.md"}
            )
            assert note.status_code == 200
            assert note.content == b"# caf\xc3\xa9\n"
            assert note.headers["content-type"].startswith("text/markdown")
            assert note.headers["x-content-type-options"] == "nosniff"
            assert note.headers["content-disposition"].startswith("inline")

            r_source = client.get(
                "/api/artifact", params={"task": "", "path": "analysis.R"}
            )
            assert r_source.headers["content-type"].startswith("text/x-r-source")

            unsafe = client.get(
                "/api/artifact", params={"task": "", "path": "unsafe.html"}
            )
            assert unsafe.status_code == 200
            assert unsafe.headers["content-disposition"].startswith("attachment")
            assert unsafe.headers["x-content-type-options"] == "nosniff"

            downloaded = client.get(
                "/api/artifact",
                params={"task": "", "path": "attachments/raw.bin", "download": "true"},
            )
            assert downloaded.status_code == 200
            assert downloaded.content == raw
            assert downloaded.headers["content-disposition"].startswith("attachment")

    def test_api_rejects_attacks_and_reports_oversized_preview(self, tmp_path, monkeypatch):
        root = _tree(tmp_path)
        (root / "large.md").write_bytes(b"12345")
        monkeypatch.setattr(
            _artifacts,
            "DEFAULT_ARTIFACT_LIMITS",
            _artifacts.ArtifactLimits(max_preview_bytes=4),
        )
        with _client_for(root) as client:
            assert client.get(
                "/api/artifact", params={"task": "", "path": "../outside"}
            ).status_code == 400
            assert client.get(
                "/api/artifact", params={"task": "", "path": ".hidden"}
            ).status_code == 403
            too_large = client.get(
                "/api/artifact", params={"task": "", "path": "large.md"}
            )
            assert too_large.status_code == 413
            assert too_large.json()["detail"]["reason"] == "preview-byte-limit"
            assert client.get(
                "/api/artifact",
                params={"task": "", "path": "large.md", "download": "true"},
            ).content == b"12345"

    def test_worktree_isolation_and_custom_root(self, tmp_path):
        root_a = _tree(tmp_path / "a", "tasks")
        root_b = _tree(tmp_path / "b", "tasks")
        (root_a / "note.md").write_text("from-a", encoding="utf-8")
        (root_b / "note.md").write_text("from-b", encoding="utf-8")

        with _client_for(root_a) as client:
            plan_dashboard._worktree_cache["other"] = plan_dashboard._build_worktree_state(
                "other", root_b
            )
            assert client.get(
                "/api/artifact", params={"task": "", "path": "note.md"}
            ).text == "from-a"
            assert client.get(
                "/api/artifact",
                params={"task": "", "path": "note.md", "wt": "other"},
            ).text == "from-b"

    def test_rootless_forest_exposes_real_tasks_not_synthetic_container(self, tmp_path):
        root = tmp_path / "superRA"
        child = root / "alpha"
        child.mkdir(parents=True)
        _write_task_md(child / "task.md", "Alpha", "not-started", objective="A.")
        (child / "note.md").write_text("alpha", encoding="utf-8")

        with _client_for(root) as client:
            assert client.get("/api/artifacts", params={"task": ""}).status_code == 404
            manifest = client.get("/api/artifacts", params={"task": "alpha"})
            assert manifest.status_code == 200
            assert manifest.json()["files"][0]["path"] == "note.md"


class TestArtifactWatcher:
    def _events(self, state, changes):
        broadcaster = AsyncMock()
        with patch.object(plan_dashboard, "_broadcast", broadcaster):
            asyncio.run(plan_dashboard._rebuild_and_broadcast(state, changes))
        return [(call.args[0], call.args[1], call.args[2]) for call in broadcaster.await_args_list]

    def test_add_modify_delete_emit_owner_only_without_global_reload(self, tmp_path):
        watchfiles = pytest.importorskip("watchfiles")
        root = _tree(tmp_path)
        state = plan_dashboard._build_worktree_state("chosen", root)
        note = root / "child" / "note.md"

        note.write_text("one", encoding="utf-8")
        added = self._events(state, {(watchfiles.Change.added, str(note))})
        note.write_text("two", encoding="utf-8")
        modified = self._events(state, {(watchfiles.Change.modified, str(note))})
        note.unlink()
        deleted = self._events(state, {(watchfiles.Change.deleted, str(note))})

        for events in (added, modified, deleted):
            assert [event[0] for event in events] == ["artifacts:child"]
            assert events[0][2] == "chosen"
            assert "full-reload" not in [event[0] for event in events]
        assert json.loads(added[0][1])["files"][0]["path"] == "note.md"
        assert json.loads(modified[0][1])["files"][0]["size"] == 3
        assert json.loads(deleted[0][1])["files"] == []

    def test_task_md_inside_attachments_is_artifact_not_subtask(self, tmp_path):
        watchfiles = pytest.importorskip("watchfiles")
        root = _tree(tmp_path)
        state = plan_dashboard._build_worktree_state("wt", root)
        embedded = root / "child" / "attachments" / "bundle" / "task.md"
        embedded.parent.mkdir(parents=True)
        embedded.write_text("asset", encoding="utf-8")

        events = self._events(state, {(watchfiles.Change.added, str(embedded))})
        assert [event[0] for event in events] == ["artifacts:child"]
        assert "child/attachments" not in state.task_index

    def test_deep_attachment_round_trip_manifest_content_watcher_and_export(
        self, tmp_path
    ):
        watchfiles = pytest.importorskip("watchfiles")
        root = _tree(tmp_path)
        relative = Path("attachments")
        for level in range(16):
            relative /= f"level-{level:02d}"
        relative /= "deep.csv"
        deepest = root / "child" / relative
        deepest.parent.mkdir(parents=True)
        raw = b"x,y\r\n1,2\r\n"
        deepest.write_bytes(raw)
        relative_path = relative.as_posix()

        manifest = _artifacts.build_manifest(root, _task(root, "child"))
        assert relative_path in {
            entry["path"]
            for entry in manifest["files"]
        }

        with _client_for(root) as client:
            response = client.get(
                "/api/artifact",
                params={
                    "task": "child",
                    "path": relative_path,
                    "download": "true",
                },
            )
            assert response.status_code == 200
            assert response.content == raw

        state = plan_dashboard._build_worktree_state("deep-wt", root)
        events = self._events(
            state,
            {(watchfiles.Change.modified, str(deepest))},
        )
        assert [event[0] for event in events] == ["artifacts:child"]
        assert relative_path in {
            entry["path"]
            for entry in json.loads(events[0][1])["files"]
        }

        payload = _standalone_payload(
            plan_dashboard.render_standalone_html(root, root="child")
        )
        assert relative_path in {
            entry["path"]
            for entry in payload["manifests"][""]["files"]
        }
        packed = payload["contents"][""][relative_path]
        assert base64.b64decode(packed["data"]) == raw


class TestStandaloneArtifacts:
    def test_scoped_export_embeds_sources_reuses_figures_and_marks_size_fallback(
        self, tmp_path, monkeypatch
    ):
        root = _tree(tmp_path)
        child = root / "child"
        (child / "note.md").write_text("# source\n", encoding="utf-8")
        (child / "model.ipynb").write_text('{"cells":[]}', encoding="utf-8")
        (child / "attachments").mkdir()
        _write_tiny_png(child / "attachments" / "figure.png")
        (child / "attachments" / "large.bin").write_bytes(b"x" * 20)
        sibling = root / "sibling"
        sibling.mkdir()
        _write_task_md(sibling / "task.md", "Sibling", "not-started", objective="S.")
        (sibling / "other.md").write_text("outside scope", encoding="utf-8")
        task_md = child / "task.md"
        task_md.write_text(
            task_md.read_text(encoding="utf-8")
            + "\n## Results\n\n![figure](attachments/figure.png)\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(
            _artifacts,
            "DEFAULT_ARTIFACT_LIMITS",
            _artifacts.ArtifactLimits(
                max_export_file_bytes=12,
                max_export_total_bytes=24,
            ),
        )

        html = plan_dashboard.render_standalone_html(
            root,
            root="child",
            repo_file_base="https://github.example/repo/blob/deadbeef",
            repo_root_prefix="superRA",
        )
        payload = _standalone_payload(html)
        assert set(payload["manifests"]) == {""}
        entries = {
            entry["path"]: entry
            for entry in payload["manifests"][""]["files"]
        }
        assert entries["attachments/figure.png"]["export"]["status"] == "figure"
        assert entries["attachments/large.bin"]["export"] == {
            "bytes": 20,
            "reason": "per-file-byte-limit",
            "status": "omitted",
        }
        assert entries["attachments/large.bin"]["repo_url"].endswith(
            "/superRA/child/attachments/large.bin"
        )
        assert "other.md" not in entries

        note = payload["contents"][""]["note.md"]
        notebook = payload["contents"][""]["model.ipynb"]
        assert base64.b64decode(note["data"]) == b"# source\n"
        assert base64.b64decode(notebook["data"]) == b'{"cells":[]}'
        figure_b64 = base64.b64encode(
            (child / "attachments" / "figure.png").read_bytes()
        ).decode("ascii")
        assert html.count(figure_b64) == 1
        assert "attachments/figure.png" not in payload["contents"].get("", {})

    def test_total_export_budget_marks_later_files_omitted(self, tmp_path, monkeypatch):
        root = _tree(tmp_path)
        (root / "a.md").write_bytes(b"aaaa")
        (root / "b.py").write_bytes(b"bbbb")
        monkeypatch.setattr(
            _artifacts,
            "DEFAULT_ARTIFACT_LIMITS",
            _artifacts.ArtifactLimits(
                max_export_file_bytes=10,
                max_export_total_bytes=4,
            ),
        )

        payload = _standalone_payload(
            plan_dashboard.render_standalone_html(root)
        )
        entries = {
            entry["path"]: entry
            for entry in payload["manifests"][""]["files"]
        }
        assert entries["a.md"]["export"]["status"] == "embedded"
        assert entries["b.py"]["export"] == {
            "bytes": 4,
            "reason": "total-byte-limit",
            "status": "omitted",
        }

    def test_figure_reuse_requires_bytes_in_actual_standalone_image_map(
        self, tmp_path, monkeypatch
    ):
        root = _tree(tmp_path)
        child = root / "child"
        unsupported = child / "unsupported.txt"
        unreadable = child / "unreadable.png"
        unsupported.write_bytes(b"not an image extension")
        unreadable.write_bytes(b"png bytes retained for download")
        task_md = child / "task.md"
        task_md.write_text(
            task_md.read_text(encoding="utf-8")
            + "\n## Results\n\n"
            + "![unsupported](unsupported.txt)\n"
            + "![temporarily unreadable](unreadable.png)\n",
            encoding="utf-8",
        )

        original_read_bytes = Path.read_bytes

        def selective_read_bytes(path: Path) -> bytes:
            if path.resolve() == unreadable.resolve():
                raise OSError("simulated image read failure")
            return original_read_bytes(path)

        monkeypatch.setattr(Path, "read_bytes", selective_read_bytes)
        payload = _standalone_payload(
            plan_dashboard.render_standalone_html(root, root="child")
        )
        entries = {
            entry["path"]: entry
            for entry in payload["manifests"][""]["files"]
        }
        assert entries["unsupported.txt"]["export"]["status"] == "embedded"
        assert entries["unreadable.png"]["export"]["status"] == "embedded"
        assert base64.b64decode(
            payload["contents"][""]["unsupported.txt"]["data"]
        ) == b"not an image extension"
        assert base64.b64decode(
            payload["contents"][""]["unreadable.png"]["data"]
        ) == b"png bytes retained for download"
