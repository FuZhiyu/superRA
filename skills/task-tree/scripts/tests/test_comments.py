#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pytest", "pyyaml"]
# ///
"""Tests for comment surfacing on the agent read path.

Covers the comment-surfacing subtree:
- `_comments.anchored_block` — in-block, moved-then-reanchored, orphaned.
- `task_read` surfacing — human `=== Open Comments ===` section, orphaned
  degradation, no-section-when-none, resolved excluded, `--json` parity.
- Reliability — the read path surfaces JSON sidecars and degrades legacy
  block-YAML sidecars *without* `pyyaml`, proven by making `import yaml` fail
  inside the test.
- Enriched `task_comment list` — full block in human + `--json` output.

Run with an interpreter that has pyyaml (e.g. `~/.venv/bin/python`); the
no-pyyaml path is exercised by monkeypatching the import machinery, not by the
ambient environment.
"""

from __future__ import annotations

import importlib
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import _comments
import task_comment
import task_read
from _comments import (
    Comment,
    CommentAnchor,
    add_comment,
    anchored_block,
    save_comments,
)


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def _write_task_md(task_dir: Path, title: str, status: str = "not-started",
                   *, objective: str = "", results: str = "") -> None:
    """Write a minimal task.md with the given body sections."""
    body = f"## Objective\n\n{objective}\n"
    if results:
        body += f"\n## Results\n\n{results}\n"
    content = (
        f'---\ntitle: "{title}"\nstatus: {status}\n'
        f"depends_on: []\ntags: []\ncreated: 2026-01-01\n---\n\n{body}"
    )
    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / "task.md").write_text(content, encoding="utf-8")


@pytest.fixture
def plan_root(tmp_path):
    """A minimal plan tree: root + one leaf task with a multi-block Objective."""
    root = tmp_path / "superRA"
    _write_task_md(root, "Test Project", "in-progress",
                   objective="A test plan.")

    objective = (
        "First paragraph anchor target.\n"
        "\n"
        "Second paragraph that we will pin a comment to with full detail.\n"
        "\n"
        "Third paragraph, the orphan-bait block.\n"
    )
    _write_task_md(root / "01-task", "First Task", "not-started",
                   objective=objective,
                   results="A result paragraph.")
    return root


def _task_body(task_dir: Path) -> str:
    """Return the body (post-frontmatter) of a task.md, as the readers see it."""
    from _task_io import parse_frontmatter
    text = (task_dir / "task.md").read_text(encoding="utf-8")
    _, body = parse_frontmatter(text)
    return body


def _mk_comment(section: str, block_index: int, preview: str,
                body: str = "please fix", resolved: bool = False) -> Comment:
    return Comment(
        id=1,
        author="reviewer",
        timestamp="2026-06-01T00:00:00",
        resolved=resolved,
        anchor=CommentAnchor(section=section, block_index=block_index,
                             text_preview=preview),
        body=body,
    )


# ---------------------------------------------------------------------------
# Block accessor (task 01) — anchored_block
# ---------------------------------------------------------------------------

class TestAnchoredBlock:
    def test_in_block_returns_full_block(self, plan_root):
        body = _task_body(plan_root / "01-task")
        # Pin to block 1 (the second paragraph), preview is a substring.
        c = _mk_comment("Objective", 1, "Second paragraph")
        block = anchored_block(c, body)
        assert block == (
            "Second paragraph that we will pin a comment to with full detail."
        )

    def test_block_moved_then_reanchored(self, plan_root):
        body = _task_body(plan_root / "01-task")
        # Comment was anchored at index 0, but its preview matches block 2.
        # anchored_block must scan and re-anchor to the moved block, returning
        # the *full* text of the block the preview now lives in.
        c = _mk_comment("Objective", 0, "Third paragraph")
        block = anchored_block(c, body)
        assert block == "Third paragraph, the orphan-bait block."
        # Re-anchoring updates the stored index in place.
        assert c.anchor.block_index == 2
        assert c.orphaned is False

    def test_orphaned_section_removed_returns_none(self, plan_root):
        body = _task_body(plan_root / "01-task")
        c = _mk_comment("Nonexistent Section", 0, "Second paragraph")
        assert anchored_block(c, body) is None
        assert c.orphaned is True

    def test_orphaned_preview_no_match_returns_none(self, plan_root):
        body = _task_body(plan_root / "01-task")
        c = _mk_comment("Objective", 0, "text that appears nowhere at all")
        assert anchored_block(c, body) is None
        assert c.orphaned is True


# ---------------------------------------------------------------------------
# task_read surfacing (task 02)
# ---------------------------------------------------------------------------

def _read_human(plan_root: Path, path: str) -> str:
    buf = io.StringIO()
    with redirect_stdout(buf):
        task_read.main(["--plan-root", str(plan_root), "--path", path])
    return buf.getvalue()


def _read_json(plan_root: Path, path: str) -> dict:
    import json
    buf = io.StringIO()
    with redirect_stdout(buf):
        task_read.main(["--plan-root", str(plan_root), "--path", path,
                        "--json"])
    return json.loads(buf.getvalue())


class TestTaskReadSurfacing:
    def test_human_shows_open_comments_with_full_block(self, plan_root):
        add_comment(plan_root / "01-task", "Objective", 1,
                    "Second paragraph", "Tighten this sentence.",
                    author="reviewer")
        out = _read_human(plan_root, "01-task")
        assert "=== Open Comments ===" in out
        assert "[reviewer] on ## Objective" in out
        # Full block text surfaced (not just the ≤60-char preview).
        assert ("Second paragraph that we will pin a comment to with full "
                "detail.") in out
        assert "Tighten this sentence." in out

    def test_human_orphaned_shows_preview_and_note(self, plan_root):
        add_comment(plan_root / "01-task", "Objective", 0,
                    "preview-that-matches-nothing", "stale comment",
                    author="reviewer")
        out = _read_human(plan_root, "01-task")
        assert "=== Open Comments ===" in out
        assert 'block: "preview-that-matches-nothing"' in out
        assert "[ORPHANED — block moved/edited away]" in out

    def test_human_no_section_when_no_unresolved(self, plan_root):
        # No comments at all -> no Open Comments section.
        out = _read_human(plan_root, "01-task")
        assert "=== Open Comments ===" not in out

    def test_human_resolved_excluded(self, plan_root):
        c = add_comment(plan_root / "01-task", "Objective", 1,
                        "Second paragraph", "already handled",
                        author="reviewer")
        # Mark resolved by rewriting the sidecar.
        c.resolved = True
        save_comments(plan_root / "01-task", [c])
        out = _read_human(plan_root, "01-task")
        assert "=== Open Comments ===" not in out
        assert "already handled" not in out

    def test_json_carries_full_block(self, plan_root):
        add_comment(plan_root / "01-task", "Objective", 1,
                    "Second paragraph", "Tighten this sentence.",
                    author="reviewer")
        data = _read_json(plan_root, "01-task")
        assert "open_comments" in data
        assert len(data["open_comments"]) == 1
        entry = data["open_comments"][0]
        assert entry["section"] == "Objective"
        assert entry["block"] == (
            "Second paragraph that we will pin a comment to with full detail."
        )
        assert entry["orphaned"] is False
        assert entry["degraded"] is None

    def test_json_orphaned_shape_block_null(self, plan_root):
        add_comment(plan_root / "01-task", "Objective", 0,
                    "preview-that-matches-nothing", "stale",
                    author="reviewer")
        data = _read_json(plan_root, "01-task")
        entry = data["open_comments"][0]
        assert entry["block"] is None
        assert entry["orphaned"] is True
        assert entry["preview"] == "preview-that-matches-nothing"

    def test_json_empty_when_no_unresolved(self, plan_root):
        data = _read_json(plan_root, "01-task")
        assert data["open_comments"] == []


# ---------------------------------------------------------------------------
# Reliability — surfacing must work without pyyaml (the load-bearing test)
# ---------------------------------------------------------------------------

class _NoYamlFinder:
    """A meta-path finder that makes ``import yaml`` raise ModuleNotFoundError."""

    def find_spec(self, name, path, target=None):
        if name == "yaml" or name.startswith("yaml."):
            raise ModuleNotFoundError("No module named 'yaml' (test-disabled)")
        return None


def _reload_comment_modules_without_yaml(monkeypatch):
    """Make pyyaml unavailable and reload the comment modules under that view.

    Returns freshly-imported ``(_comments, task_read)`` modules whose
    ``load_comments`` cannot import yaml. Asserts the import genuinely fails so
    the test cannot silently pass with pyyaml present.
    """
    # Drop any cached yaml so the import machinery re-resolves it.
    for mod in list(sys.modules):
        if mod == "yaml" or mod.startswith("yaml."):
            monkeypatch.delitem(sys.modules, mod, raising=False)
    finder = _NoYamlFinder()
    monkeypatch.setattr(sys, "meta_path", [finder, *sys.meta_path])

    # Prove the no-yaml condition actually holds in this test.
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("yaml")

    # Reload the modules under test so their `import yaml` (inside
    # load_comments) resolves through the disabled finder.
    fresh_comments = importlib.reload(_comments)
    monkeypatch.setitem(sys.modules, "_comments", fresh_comments)
    fresh_read = importlib.reload(task_read)
    return fresh_comments, fresh_read


@pytest.fixture(autouse=False)
def restore_modules():
    """Restore the canonical (yaml-enabled) modules after a no-yaml test."""
    yield
    importlib.reload(_comments)
    importlib.reload(task_read)
    importlib.reload(task_comment)


class TestNoPyyamlReliability:
    def test_json_sidecar_surfaces_without_yaml(self, plan_root, monkeypatch,
                                                restore_modules):
        # Seed a JSON-format sidecar (what save_comments writes today).
        add_comment(plan_root / "01-task", "Objective", 1,
                    "Second paragraph", "fix without yaml",
                    author="reviewer")

        _, fresh_read = _reload_comment_modules_without_yaml(monkeypatch)

        buf = io.StringIO()
        with redirect_stdout(buf):
            fresh_read.main(["--plan-root", str(plan_root),
                             "--path", "01-task"])
        out = buf.getvalue()
        # The JSON sidecar is read by stdlib json — no yaml needed — so the
        # comment surfaces with its full block.
        assert "=== Open Comments ===" in out
        assert ("Second paragraph that we will pin a comment to with full "
                "detail.") in out
        assert "fix without yaml" in out

    def test_legacy_block_yaml_degrades_without_yaml(self, plan_root,
                                                     monkeypatch,
                                                     restore_modules):
        # Write a legacy PyYAML block-style sidecar (NOT valid JSON), which
        # stdlib json cannot parse and which needs pyyaml to read.
        legacy = (
            "- id: 1\n"
            "  author: reviewer\n"
            "  timestamp: '2026-06-01T00:00:00'\n"
            "  resolved: false\n"
            "  anchor:\n"
            "    section: Objective\n"
            "    block_index: 1\n"
            "    text_preview: Second paragraph\n"
            "  body: legacy comment body\n"
        )
        (plan_root / "01-task" / "comments.yaml").write_text(
            legacy, encoding="utf-8")

        _, fresh_read = _reload_comment_modules_without_yaml(monkeypatch)

        buf = io.StringIO()
        with redirect_stdout(buf):
            # Must NOT crash — degrades to a visible note, exits normally.
            fresh_read.main(["--plan-root", str(plan_root),
                             "--path", "01-task"])
        out = buf.getvalue()
        assert "open comments unavailable: legacy sidecar format" in out
        # The rest of the read still emitted (frontmatter, sections).
        assert "=== Task: First Task ===" in out
        assert "## Objective" in out

    def test_legacy_sidecar_raises_only_without_yaml(self, plan_root,
                                                     monkeypatch,
                                                     restore_modules):
        # Direct unit check: load_comments raises LegacyCommentFormatError on a
        # block-YAML file only when yaml is unavailable.
        legacy = (
            "- id: 1\n"
            "  author: reviewer\n"
            "  timestamp: '2026-06-01T00:00:00'\n"
            "  resolved: false\n"
            "  anchor:\n"
            "    section: Objective\n"
            "    block_index: 0\n"
            "    text_preview: First paragraph\n"
            "  body: legacy\n"
        )
        (plan_root / "01-task" / "comments.yaml").write_text(
            legacy, encoding="utf-8")

        fresh_comments, _ = _reload_comment_modules_without_yaml(monkeypatch)
        with pytest.raises(fresh_comments.LegacyCommentFormatError):
            fresh_comments.load_comments(plan_root / "01-task")


# ---------------------------------------------------------------------------
# Enriched CLI (task 03) — task_comment list
# ---------------------------------------------------------------------------

def _comment_cli(plan_root: Path, *args: str) -> str:
    buf = io.StringIO()
    with redirect_stdout(buf):
        task_comment.main(["--plan-root", str(plan_root), *args])
    return buf.getvalue()


class TestTaskCommentList:
    def test_human_emits_full_block(self, plan_root):
        add_comment(plan_root / "01-task", "Objective", 1,
                    "Second paragraph", "CLI fix me", author="reviewer")
        out = _comment_cli(plan_root, "list", "01-task")
        assert ("Second paragraph that we will pin a comment to with full "
                "detail.") in out
        assert "CLI fix me" in out

    def test_json_full_block_parity(self, plan_root):
        import json
        add_comment(plan_root / "01-task", "Objective", 1,
                    "Second paragraph", "CLI fix me", author="reviewer")
        out = _comment_cli(plan_root, "list", "01-task", "--json")
        data = json.loads(out)
        assert len(data) == 1
        assert data[0]["block"] == (
            "Second paragraph that we will pin a comment to with full detail."
        )
        assert data[0]["orphaned"] is False

    def test_json_orphaned_shape(self, plan_root):
        import json
        add_comment(plan_root / "01-task", "Objective", 0,
                    "preview-that-matches-nothing", "stale",
                    author="reviewer")
        out = _comment_cli(plan_root, "list", "01-task", "--json")
        data = json.loads(out)
        assert data[0]["block"] is None
        assert data[0]["orphaned"] is True
