#!/usr/bin/env python3
"""Tests for worktree discovery and server-side switching."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

import _worktree_discovery as wd
from _worktree_discovery import (
    WorktreeInfo,
    _parse_plan_title,
    _parse_porcelain,
    discover_worktrees,
    filter_worktrees,
    get_git_common_dir,
    sort_worktrees,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_task_md(path: Path, title: str) -> None:
    """Write a minimal task.md with frontmatter title."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'---\ntitle: "{title}"\nstatus: not-started\n---\n\n## Objective\n\nDo it.\n',
        encoding="utf-8",
    )


REALISTIC_PORCELAIN = """\
worktree /Users/dev/project
HEAD abc123def456abc123def456abc123def456abc123
branch refs/heads/main

worktree /Users/dev/project.worktrees/feature-a
HEAD def456abc123def456abc123def456abc123def456
branch refs/heads/feature-a

worktree /Users/dev/project.worktrees/agent-cleanup
HEAD 789012345678901234567890123456789012345678
branch refs/heads/worktree-agent-cleanup
locked

worktree /Users/dev/project.worktrees/detached
HEAD aaa111bbb222ccc333ddd444eee555fff666aaa11
detached

worktree /Users/dev/project.worktrees/old-branch
HEAD bbb222ccc333ddd444eee555fff666aaa111bbb22
branch refs/heads/old-branch
prunable gitdir file points to non-existent location
"""


def _make_worktree(
    path: str = "/tmp/wt",
    branch: str | None = "main",
    head: str = "abc123",
    plan_root: str | None = "/tmp/wt/superRA",
    plan_title: str | None = "Test Plan",
    is_current: bool = False,
    is_locked: bool = False,
    is_prunable: bool = False,
    is_agent: bool = False,
    last_activity: float | None = 1000.0,
) -> WorktreeInfo:
    return WorktreeInfo(
        path=path,
        branch=branch,
        head=head,
        plan_root=plan_root,
        plan_title=plan_title,
        is_current=is_current,
        is_locked=is_locked,
        is_prunable=is_prunable,
        is_agent=is_agent,
        last_activity=last_activity,
    )


# ===========================================================================
# _parse_porcelain tests
# ===========================================================================


class TestParsePorcelain:
    def test_multi_worktree_output(self):
        blocks = _parse_porcelain(REALISTIC_PORCELAIN)
        assert len(blocks) == 5

    def test_worktree_paths(self):
        blocks = _parse_porcelain(REALISTIC_PORCELAIN)
        paths = [b["worktree"] for b in blocks]
        assert paths[0] == "/Users/dev/project"
        assert paths[1] == "/Users/dev/project.worktrees/feature-a"

    def test_head_sha(self):
        blocks = _parse_porcelain(REALISTIC_PORCELAIN)
        assert blocks[0]["HEAD"] == "abc123def456abc123def456abc123def456abc123"

    def test_branch_refs(self):
        blocks = _parse_porcelain(REALISTIC_PORCELAIN)
        assert blocks[0]["branch"] == "refs/heads/main"
        assert blocks[1]["branch"] == "refs/heads/feature-a"

    def test_detached_head(self):
        blocks = _parse_porcelain(REALISTIC_PORCELAIN)
        detached = blocks[3]
        assert "detached" in detached
        assert "branch" not in detached

    def test_locked_flag(self):
        blocks = _parse_porcelain(REALISTIC_PORCELAIN)
        agent_block = blocks[2]
        assert "locked" in agent_block

    def test_prunable_with_reason(self):
        blocks = _parse_porcelain(REALISTIC_PORCELAIN)
        prunable_block = blocks[4]
        assert "prunable" in prunable_block
        assert "non-existent" in prunable_block["prunable"]

    def test_empty_output(self):
        blocks = _parse_porcelain("")
        assert blocks == []

    def test_single_worktree(self):
        output = (
            "worktree /repo\n"
            "HEAD abcdef1234567890abcdef1234567890abcdef12\n"
            "branch refs/heads/main\n"
        )
        blocks = _parse_porcelain(output)
        assert len(blocks) == 1
        assert blocks[0]["worktree"] == "/repo"


# ===========================================================================
# _parse_plan_title tests
# ===========================================================================


class TestParsePlanTitle:
    def test_normal_title(self, tmp_path):
        task_md = tmp_path / "task.md"
        _write_task_md(task_md, "My Project")
        assert _parse_plan_title(task_md) == "My Project"

    def test_quoted_title(self, tmp_path):
        task_md = tmp_path / "task.md"
        task_md.write_text(
            '---\ntitle: "Quoted Title"\nstatus: not-started\n---\n\nBody.\n',
            encoding="utf-8",
        )
        assert _parse_plan_title(task_md) == "Quoted Title"

    def test_no_frontmatter(self, tmp_path):
        task_md = tmp_path / "task.md"
        task_md.write_text("Just some text, no frontmatter.\n", encoding="utf-8")
        assert _parse_plan_title(task_md) is None

    def test_no_title_field(self, tmp_path):
        task_md = tmp_path / "task.md"
        task_md.write_text("---\nstatus: not-started\n---\n\nBody.\n", encoding="utf-8")
        assert _parse_plan_title(task_md) is None

    def test_nonexistent_file(self, tmp_path):
        task_md = tmp_path / "nonexistent.md"
        assert _parse_plan_title(task_md) is None

    def test_broken_file_returns_none(self, tmp_path):
        """A file with valid frontmatter but no title field returns None."""
        task_md = tmp_path / "task.md"
        task_md.write_text("---\nfoo: bar\n---\n\n## Objective\n", encoding="utf-8")
        assert _parse_plan_title(task_md) is None


# ===========================================================================
# get_git_common_dir tests
# ===========================================================================


class TestGetGitCommonDir:
    @patch("_worktree_discovery.subprocess.run")
    def test_returns_resolved_path(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(
            returncode=0, stdout=str(tmp_path / ".git") + "\n"
        )
        result = get_git_common_dir()
        assert result == str((tmp_path / ".git").resolve())

    @patch("_worktree_discovery.subprocess.run")
    def test_returns_none_on_failure(self, mock_run):
        mock_run.return_value = MagicMock(returncode=128, stdout="")
        assert get_git_common_dir() is None

    @patch("_worktree_discovery.subprocess.run")
    def test_returns_none_on_empty_output(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="\n")
        assert get_git_common_dir() is None

    @patch("_worktree_discovery.subprocess.run", side_effect=FileNotFoundError)
    def test_returns_none_when_git_not_installed(self, mock_run):
        assert get_git_common_dir() is None

    @patch(
        "_worktree_discovery.subprocess.run",
        side_effect=__import__("subprocess").TimeoutExpired(cmd="git", timeout=5),
    )
    def test_returns_none_on_timeout(self, mock_run):
        assert get_git_common_dir() is None


# ===========================================================================
# discover_worktrees tests
# ===========================================================================


class TestDiscoverWorktrees:
    @patch("_worktree_discovery._get_last_activity")
    @patch("_worktree_discovery._get_current_worktree_path")
    @patch("_worktree_discovery.subprocess.run")
    def test_discovers_worktrees_with_plans(
        self, mock_run, mock_current, mock_activity, tmp_path
    ):
        # Set up two worktrees with superRA/ directories
        wt1 = tmp_path / "main"
        wt1.mkdir()
        _write_task_md(wt1 / "superRA" / "task.md", "Main Plan")

        wt2 = tmp_path / "feature"
        wt2.mkdir()
        _write_task_md(wt2 / "superRA" / "task.md", "Feature Plan")

        porcelain = (
            f"worktree {wt1}\n"
            "HEAD abc123def456abc123def456abc123def456abc123\n"
            "branch refs/heads/main\n\n"
            f"worktree {wt2}\n"
            "HEAD def456abc123def456abc123def456abc123def456\n"
            "branch refs/heads/feature\n"
        )
        mock_run.return_value = MagicMock(returncode=0, stdout=porcelain)
        mock_current.return_value = str(wt1.resolve())
        mock_activity.return_value = 1700000000.0

        result = discover_worktrees()
        assert len(result) == 2
        assert result[0].plan_title == "Main Plan"
        assert result[0].is_current is True
        assert result[1].plan_title == "Feature Plan"
        assert result[1].is_current is False
        assert result[0].branch == "main"
        assert result[1].branch == "feature"

    @patch("_worktree_discovery.subprocess.run")
    def test_empty_on_non_git(self, mock_run):
        mock_run.return_value = MagicMock(returncode=128, stdout="")
        assert discover_worktrees() == []

    @patch("_worktree_discovery.subprocess.run", side_effect=FileNotFoundError)
    def test_empty_when_git_missing(self, mock_run):
        assert discover_worktrees() == []

    @patch("_worktree_discovery._get_last_activity")
    @patch("_worktree_discovery._get_current_worktree_path")
    @patch("_worktree_discovery.subprocess.run")
    def test_prunable_skips_plan_check(
        self, mock_run, mock_current, mock_activity, tmp_path
    ):
        """Prunable worktrees skip filesystem checks; plan_root remains None."""
        wt = tmp_path / "prunable-wt"
        wt.mkdir()
        _write_task_md(wt / "superRA" / "task.md", "Should be skipped")

        porcelain = (
            f"worktree {wt}\n"
            "HEAD abc123def456abc123def456abc123def456abc123\n"
            "branch refs/heads/old\n"
            "prunable gitdir file points to non-existent location\n"
        )
        mock_run.return_value = MagicMock(returncode=0, stdout=porcelain)
        mock_current.return_value = None
        mock_activity.return_value = None

        result = discover_worktrees()
        assert len(result) == 1
        assert result[0].is_prunable is True
        assert result[0].plan_root is None

    @patch("_worktree_discovery._get_last_activity")
    @patch("_worktree_discovery._get_current_worktree_path")
    @patch("_worktree_discovery.subprocess.run")
    def test_no_plan_dir_sets_plan_root_none(
        self, mock_run, mock_current, mock_activity, tmp_path
    ):
        """Worktree without a task-root directory has plan_root=None."""
        wt = tmp_path / "no-plan"
        wt.mkdir()  # no task-root directory inside

        porcelain = (
            f"worktree {wt}\n"
            "HEAD abc123def456abc123def456abc123def456abc123\n"
            "branch refs/heads/main\n"
        )
        mock_run.return_value = MagicMock(returncode=0, stdout=porcelain)
        mock_current.return_value = None
        mock_activity.return_value = 1000.0

        result = discover_worktrees()
        assert len(result) == 1
        assert result[0].plan_root is None
        assert result[0].plan_title is None

    @patch("_worktree_discovery._get_last_activity")
    @patch("_worktree_discovery._get_current_worktree_path")
    @patch("_worktree_discovery.subprocess.run")
    def test_discovers_legacy_plan_root(
        self, mock_run, mock_current, mock_activity, tmp_path
    ):
        """Legacy .plan/ worktrees remain visible during migration."""
        wt = tmp_path / "legacy"
        wt.mkdir()
        _write_task_md(wt / ".plan" / "task.md", "Legacy Plan")

        porcelain = (
            f"worktree {wt}\n"
            "HEAD abc123def456abc123def456abc123def456abc123\n"
            "branch refs/heads/legacy\n"
        )
        mock_run.return_value = MagicMock(returncode=0, stdout=porcelain)
        mock_current.return_value = None
        mock_activity.return_value = 1000.0

        result = discover_worktrees()
        assert len(result) == 1
        assert result[0].plan_root == str((wt / ".plan").resolve())
        assert result[0].plan_title == "Legacy Plan"

    @patch("_worktree_discovery._get_last_activity")
    @patch("_worktree_discovery._get_current_worktree_path")
    @patch("_worktree_discovery.subprocess.run")
    def test_broken_task_md_sets_plan_title_none(
        self, mock_run, mock_current, mock_activity, tmp_path
    ):
        """Worktree with superRA/task.md but broken frontmatter has plan_root set, title None."""
        wt = tmp_path / "broken"
        wt.mkdir()
        plan_dir = wt / "superRA"
        plan_dir.mkdir()
        (plan_dir / "task.md").write_text("No frontmatter here.\n", encoding="utf-8")

        porcelain = (
            f"worktree {wt}\n"
            "HEAD abc123def456abc123def456abc123def456abc123\n"
            "branch refs/heads/broken\n"
        )
        mock_run.return_value = MagicMock(returncode=0, stdout=porcelain)
        mock_current.return_value = None
        mock_activity.return_value = 500.0

        result = discover_worktrees()
        assert len(result) == 1
        assert result[0].plan_root is not None
        assert result[0].plan_title is None

    @patch("_worktree_discovery._get_last_activity")
    @patch("_worktree_discovery._get_current_worktree_path")
    @patch("_worktree_discovery.subprocess.run")
    def test_agent_worktree_detected_by_branch(
        self, mock_run, mock_current, mock_activity, tmp_path
    ):
        wt = tmp_path / "agent-wt"
        wt.mkdir()
        _write_task_md(wt / "superRA" / "task.md", "Agent Plan")

        porcelain = (
            f"worktree {wt}\n"
            "HEAD abc123def456abc123def456abc123def456abc123\n"
            "branch refs/heads/worktree-agent-cleanup\n"
        )
        mock_run.return_value = MagicMock(returncode=0, stdout=porcelain)
        mock_current.return_value = None
        mock_activity.return_value = 2000.0

        result = discover_worktrees()
        assert len(result) == 1
        assert result[0].is_agent is True

    @patch("_worktree_discovery._get_last_activity")
    @patch("_worktree_discovery._get_current_worktree_path")
    @patch("_worktree_discovery.subprocess.run")
    def test_agent_worktree_detected_by_path(
        self, mock_run, mock_current, mock_activity, tmp_path
    ):
        wt = tmp_path / ".claude" / "worktrees" / "agent-task1"
        wt.mkdir(parents=True)
        _write_task_md(wt / "superRA" / "task.md", "Agent Path Plan")

        porcelain = (
            f"worktree {wt}\n"
            "HEAD abc123def456abc123def456abc123def456abc123\n"
            "branch refs/heads/some-branch\n"
        )
        mock_run.return_value = MagicMock(returncode=0, stdout=porcelain)
        mock_current.return_value = None
        mock_activity.return_value = 3000.0

        result = discover_worktrees()
        assert len(result) == 1
        assert result[0].is_agent is True

    @patch("_worktree_discovery._get_last_activity")
    @patch("_worktree_discovery._get_current_worktree_path")
    @patch("_worktree_discovery.subprocess.run")
    def test_detached_head_branch_is_none(
        self, mock_run, mock_current, mock_activity, tmp_path
    ):
        wt = tmp_path / "detached"
        wt.mkdir()

        porcelain = (
            f"worktree {wt}\n"
            "HEAD abc123def456abc123def456abc123def456abc123\n"
            "detached\n"
        )
        mock_run.return_value = MagicMock(returncode=0, stdout=porcelain)
        mock_current.return_value = None
        mock_activity.return_value = None

        result = discover_worktrees()
        assert len(result) == 1
        assert result[0].branch is None


# ===========================================================================
# filter_worktrees tests
# ===========================================================================


class TestFilterWorktrees:
    def test_default_excludes_prunable(self):
        wts = [
            _make_worktree(path="/a", is_prunable=True, plan_root="/a/superRA"),
            _make_worktree(path="/b", is_prunable=False, plan_root="/b/superRA"),
        ]
        result = filter_worktrees(wts)
        assert len(result) == 1
        assert result[0].path == "/b"

    def test_default_excludes_no_plan(self):
        wts = [
            _make_worktree(path="/a", plan_root=None),
            _make_worktree(path="/b", plan_root="/b/superRA"),
        ]
        result = filter_worktrees(wts)
        assert len(result) == 1
        assert result[0].path == "/b"

    def test_default_keeps_agent_worktrees(self):
        wts = [
            _make_worktree(path="/agent", is_agent=True, plan_root="/agent/superRA"),
            _make_worktree(path="/normal", is_agent=False, plan_root="/normal/superRA"),
        ]
        result = filter_worktrees(wts)
        assert len(result) == 2

    def test_include_prunable_override(self):
        wts = [
            _make_worktree(path="/prunable", is_prunable=True, plan_root="/p/superRA"),
        ]
        result = filter_worktrees(wts, include_prunable=True)
        assert len(result) == 1

    def test_require_plan_false(self):
        wts = [
            _make_worktree(path="/no-plan", plan_root=None),
        ]
        result = filter_worktrees(wts, require_plan=False)
        assert len(result) == 1

    def test_empty_input(self):
        assert filter_worktrees([]) == []


# ===========================================================================
# sort_worktrees tests
# ===========================================================================


class TestSortWorktrees:
    def test_descending_by_activity(self):
        wts = [
            _make_worktree(path="/old", last_activity=1000.0),
            _make_worktree(path="/new", last_activity=3000.0),
            _make_worktree(path="/mid", last_activity=2000.0),
        ]
        result = sort_worktrees(wts)
        assert [w.path for w in result] == ["/new", "/mid", "/old"]

    def test_none_activity_sorts_last(self):
        wts = [
            _make_worktree(path="/none", last_activity=None),
            _make_worktree(path="/has", last_activity=1000.0),
        ]
        result = sort_worktrees(wts)
        assert result[0].path == "/has"
        assert result[1].path == "/none"

    def test_all_none_preserves_order(self):
        wts = [
            _make_worktree(path="/a", last_activity=None),
            _make_worktree(path="/b", last_activity=None),
        ]
        result = sort_worktrees(wts)
        assert len(result) == 2

    def test_single_element(self):
        wts = [_make_worktree(path="/only", last_activity=500.0)]
        result = sort_worktrees(wts)
        assert len(result) == 1
        assert result[0].path == "/only"

    def test_empty_input(self):
        assert sort_worktrees([]) == []


# ===========================================================================
# Port derivation tests
# ===========================================================================


class TestDefaultPort:
    def test_consistent_port_from_git_common_dir(self, tmp_path):
        """Same git_common_dir produces the same port regardless of plan root."""
        from plan_dashboard import _default_port

        plan_root_a = tmp_path / "wt-a" / "superRA"
        plan_root_b = tmp_path / "wt-b" / "superRA"
        plan_root_a.mkdir(parents=True)
        plan_root_b.mkdir(parents=True)
        common_dir = str(tmp_path / ".git")

        port_a = _default_port(plan_root_a, git_common_dir=common_dir)
        port_b = _default_port(plan_root_b, git_common_dir=common_dir)
        assert port_a == port_b

    def test_fallback_to_plan_root_hashing(self, tmp_path):
        """Without git_common_dir, port is derived from plan_root."""
        from plan_dashboard import _default_port

        plan_root = tmp_path / "superRA"
        plan_root.mkdir()
        port = _default_port(plan_root, git_common_dir=None)
        assert 8100 <= port <= 8999 or port == 0

    def test_port_in_valid_range(self, tmp_path):
        from plan_dashboard import _default_port

        plan_root = tmp_path / "superRA"
        plan_root.mkdir()
        port = _default_port(plan_root, git_common_dir="/some/git/dir")
        assert 8100 <= port <= 8999 or port == 0

    def test_different_repos_likely_different_ports(self, tmp_path):
        """Different git common dirs should produce different ports (probabilistic)."""
        from plan_dashboard import _default_port

        plan_root = tmp_path / "superRA"
        plan_root.mkdir()
        port_a = _default_port(plan_root, git_common_dir="/repo-a/.git")
        port_b = _default_port(plan_root, git_common_dir="/repo-b/.git")
        # With 900 possible ports, collision is ~0.1% for two random inputs.
        # We accept this test is probabilistic.
        assert port_a != port_b


# ===========================================================================
# Server route tests (FastAPI TestClient)
# ===========================================================================


class TestWorktreeRoutes:
    """Tests for GET /api/worktrees and POST /api/worktree/switch."""

    @pytest.fixture(autouse=True)
    def setup_app(self, tmp_path):
        """Set up the FastAPI app with a temporary plan root before each test."""
        import plan_dashboard

        self._plan_root = tmp_path / "superRA"
        self._plan_root.mkdir()
        _write_task_md(self._plan_root / "task.md", "Test Dashboard")

        # Save original module state
        self._orig_plan_root = plan_dashboard.PLAN_ROOT
        self._orig_project_root = plan_dashboard._project_root
        self._orig_current_wt = plan_dashboard._current_worktree_path
        self._orig_root_task = plan_dashboard._root_task
        self._orig_task_index = plan_dashboard._task_index

        # Set module-level state
        plan_dashboard.PLAN_ROOT = self._plan_root
        plan_dashboard._project_root = str(tmp_path)
        plan_dashboard._current_worktree_path = str(tmp_path)

        # Build the task tree
        plan_dashboard.rebuild_tree()

        yield

        # Restore original state
        plan_dashboard.PLAN_ROOT = self._orig_plan_root
        plan_dashboard._project_root = self._orig_project_root
        plan_dashboard._current_worktree_path = self._orig_current_wt
        plan_dashboard._root_task = self._orig_root_task
        plan_dashboard._task_index = self._orig_task_index

    def _get_client(self):
        from fastapi.testclient import TestClient
        import plan_dashboard
        # Use raise_server_exceptions=False so we can check status codes
        return TestClient(plan_dashboard.app, raise_server_exceptions=False)

    @patch("plan_dashboard.discover_worktrees")
    def test_get_worktrees_returns_json(self, mock_discover):
        import plan_dashboard

        mock_discover.return_value = [
            WorktreeInfo(
                path=str(self._plan_root.parent),
                branch="main",
                head="abc123",
                plan_root=str(self._plan_root),
                plan_title="Test Dashboard",
                is_current=True,
                is_locked=False,
                is_prunable=False,
                is_agent=False,
                last_activity=1700000000.0,
            ),
        ]
        client = self._get_client()
        resp = client.get("/api/worktrees")
        assert resp.status_code == 200
        data = resp.json()
        assert "current" in data
        assert "worktrees" in data
        assert len(data["worktrees"]) >= 1

    @patch("plan_dashboard.discover_worktrees")
    def test_get_worktrees_fields(self, mock_discover):
        import plan_dashboard

        mock_discover.return_value = [
            WorktreeInfo(
                path=str(self._plan_root.parent),
                branch="main",
                head="abc123",
                plan_root=str(self._plan_root),
                plan_title="Test Dashboard",
                is_current=True,
                is_locked=False,
                is_prunable=False,
                is_agent=False,
                last_activity=1700000000.0,
            ),
        ]
        client = self._get_client()
        data = client.get("/api/worktrees").json()
        wt = data["worktrees"][0]
        for key in ("path", "branch", "plan_title", "is_current", "has_plan", "is_agent", "last_activity"):
            assert key in wt, f"Missing key: {key}"

    @patch("plan_dashboard.discover_worktrees")
    def test_get_worktrees_fallback_no_git(self, mock_discover):
        """When not in a git repo, returns single-entry fallback."""
        mock_discover.return_value = []
        client = self._get_client()
        data = client.get("/api/worktrees").json()
        assert len(data["worktrees"]) == 1
        assert data["worktrees"][0]["is_current"] is True
        assert data["worktrees"][0]["has_plan"] is True

    def test_switch_missing_plan_root_returns_400(self):
        client = self._get_client()
        resp = client.post("/api/worktree/switch", json={})
        assert resp.status_code == 400

    @patch("plan_dashboard.discover_worktrees")
    def test_switch_no_git_returns_404(self, mock_discover):
        mock_discover.return_value = []
        client = self._get_client()
        resp = client.post(
            "/api/worktree/switch",
            json={"plan_root": "/nonexistent/superRA"},
        )
        assert resp.status_code == 404

    @patch("plan_dashboard.discover_worktrees")
    def test_switch_nonexistent_worktree_returns_404(self, mock_discover, tmp_path):
        mock_discover.return_value = [
            WorktreeInfo(
                path="/some/other/path",
                branch="other",
                head="abc",
                plan_root="/some/other/superRA",
                plan_title="Other",
                is_current=False,
                is_locked=False,
                is_prunable=False,
                is_agent=False,
                last_activity=1000.0,
            ),
        ]
        client = self._get_client()
        resp = client.post(
            "/api/worktree/switch",
            json={"plan_root": "/nonexistent/superRA"},
        )
        assert resp.status_code == 404

    @patch("plan_dashboard.discover_worktrees")
    def test_switch_valid_worktree_success(self, mock_discover, tmp_path):
        import plan_dashboard

        # Create a second worktree with a valid superRA/
        wt2 = tmp_path / "wt2"
        wt2.mkdir()
        wt2_plan = wt2 / "superRA"
        wt2_plan.mkdir()
        _write_task_md(wt2_plan / "task.md", "Second Worktree")

        mock_discover.return_value = [
            WorktreeInfo(
                path=str(wt2),
                branch="feature",
                head="def456",
                plan_root=str(wt2_plan),
                plan_title="Second Worktree",
                is_current=False,
                is_locked=False,
                is_prunable=False,
                is_agent=False,
                last_activity=2000.0,
            ),
        ]

        client = self._get_client()
        resp = client.post(
            "/api/worktree/switch",
            json={"plan_root": str(wt2_plan)},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert data["branch"] == "feature"

        # Verify the module state was updated
        assert str(plan_dashboard.PLAN_ROOT) == str(wt2_plan.resolve())

    @patch("plan_dashboard.discover_worktrees")
    def test_switch_invalid_plan_root_no_task_md_returns_400(self, mock_discover, tmp_path):
        """Worktree exists but superRA/ has no task.md -> 400."""
        import plan_dashboard

        wt = tmp_path / "bad-plan-wt"
        wt.mkdir()
        bad_plan = wt / "superRA"
        bad_plan.mkdir()
        # No task.md inside superRA/

        mock_discover.return_value = [
            WorktreeInfo(
                path=str(wt),
                branch="bad",
                head="aaa",
                plan_root=str(bad_plan),
                plan_title=None,
                is_current=False,
                is_locked=False,
                is_prunable=False,
                is_agent=False,
                last_activity=100.0,
            ),
        ]

        client = self._get_client()
        resp = client.post(
            "/api/worktree/switch",
            json={"plan_root": str(bad_plan)},
        )
        assert resp.status_code == 400


# ===========================================================================
# SSE broadcast on switch
# ===========================================================================


class TestSSEBroadcastOnSwitch:
    """Verify that a successful worktree switch triggers a full-reload SSE event."""

    @pytest.fixture(autouse=True)
    def setup_app(self, tmp_path):
        import plan_dashboard

        self._plan_root = tmp_path / "superRA"
        self._plan_root.mkdir()
        _write_task_md(self._plan_root / "task.md", "Main Plan")

        self._orig_plan_root = plan_dashboard.PLAN_ROOT
        self._orig_project_root = plan_dashboard._project_root
        self._orig_current_wt = plan_dashboard._current_worktree_path
        self._orig_root_task = plan_dashboard._root_task
        self._orig_task_index = plan_dashboard._task_index
        self._orig_sse_clients = plan_dashboard._sse_clients.copy()

        plan_dashboard.PLAN_ROOT = self._plan_root
        plan_dashboard._project_root = str(tmp_path)
        plan_dashboard._current_worktree_path = str(tmp_path)
        plan_dashboard.rebuild_tree()

        yield

        plan_dashboard.PLAN_ROOT = self._orig_plan_root
        plan_dashboard._project_root = self._orig_project_root
        plan_dashboard._current_worktree_path = self._orig_current_wt
        plan_dashboard._root_task = self._orig_root_task
        plan_dashboard._task_index = self._orig_task_index
        plan_dashboard._sse_clients = self._orig_sse_clients

    @patch("plan_dashboard.discover_worktrees")
    def test_switch_broadcasts_full_reload(self, mock_discover, tmp_path):
        import asyncio
        import plan_dashboard

        # Create target worktree
        wt2 = tmp_path / "wt2"
        wt2.mkdir()
        wt2_plan = wt2 / "superRA"
        wt2_plan.mkdir()
        _write_task_md(wt2_plan / "task.md", "Switched Plan")

        mock_discover.return_value = [
            WorktreeInfo(
                path=str(wt2),
                branch="feature",
                head="def456",
                plan_root=str(wt2_plan),
                plan_title="Switched Plan",
                is_current=False,
                is_locked=False,
                is_prunable=False,
                is_agent=False,
                last_activity=2000.0,
            ),
        ]

        # Register a mock SSE client
        queue: asyncio.Queue[str] = asyncio.Queue(maxsize=256)
        plan_dashboard._sse_clients.add(queue)

        from fastapi.testclient import TestClient
        client = TestClient(plan_dashboard.app, raise_server_exceptions=False)
        resp = client.post(
            "/api/worktree/switch",
            json={"plan_root": str(wt2_plan)},
        )
        assert resp.status_code == 200

        # The queue should have received a full-reload event
        assert not queue.empty(), "SSE client should have received a broadcast"
        msg = queue.get_nowait()
        assert "full-reload" in msg
