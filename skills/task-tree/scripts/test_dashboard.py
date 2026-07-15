#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pytest", "httpx", "pyyaml", "fastapi", "jinja2"]
# ///
"""Tests for the live dashboard server, comments system, SSE, and templates.

Also contains the canonical tests for plan_dashboard static export, server
lifecycle, and the master-detail partials (moved from test_task_tree.py).
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

import _task_io
import dashboard_artifact_workflow
import plan_dashboard
import cli
from _comments import (
    add_comment,
    delete_comment,
    load_comments,
    resolve_anchors,
    resolve_comment,
    save_comments,
    split_into_blocks,
)

# Shared helpers — canonical definitions live in conftest.py.
from conftest import _write_task_md, _write_tiny_png, _serve_plan


def _workflow_lines(content: str) -> list[str]:
    return [line.rstrip() for line in content.splitlines()]


def _line_index(lines: list[str], text: str) -> int:
    return lines.index(text)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def plan_root(tmp_path):
    """Create a minimal plan tree for dashboard testing."""
    root = tmp_path / "superRA"
    root.mkdir()

    _write_task_md(root / "task.md", "Test Project", "not-started",
                   objective="A test plan.")

    d1 = root / "01-first"
    d1.mkdir()
    _write_task_md(d1 / "task.md", "First Task", "approved",
                   objective="Complete step 1.",
                   results="### Key Findings\n- Found 100 rows")

    d2 = root / "02-second"
    d2.mkdir()
    _write_task_md(d2 / "task.md", "Second Task", "not-started",
                   depends_on=["01-first"],
                   objective="Complete step 2.")

    d3 = root / "03-third"
    d3.mkdir()
    _write_task_md(d3 / "task.md", "Third Task", "not-started",
                   depends_on=["02-second"],
                   objective="Complete step 3.")

    return root


@pytest.fixture
def postponed_plan_root(tmp_path):
    """Plan tree exercising postponed rendering: a postponed leaf, a sibling
    blocked by a postponed dependency, an approved leaf, and a branch whose
    children are all postponed (rolls up to postponed)."""
    root = tmp_path / "superRA"
    root.mkdir()
    _write_task_md(root / "task.md", "Postponed Fixture Root", "in-progress",
                   objective="Fixture tree for postponed rendering.")

    leaf = root / "01-postponed-leaf"
    leaf.mkdir()
    _write_task_md(leaf / "task.md", "A postponed leaf", "postponed",
                   objective="Parked leaf.")

    blocked = root / "02-blocked-by-postponed"
    blocked.mkdir()
    _write_task_md(blocked / "task.md", "Blocked by postponed dep", "not-started",
                   depends_on=["01-postponed-leaf"],
                   objective="Depends on the postponed leaf.")

    approved = root / "03-approved-leaf"
    approved.mkdir()
    _write_task_md(approved / "task.md", "An approved leaf", "approved",
                   objective="Done work.")

    branch = root / "04-postponed-branch"
    branch.mkdir()
    _write_task_md(branch / "task.md", "A postponed branch", "in-progress",
                   objective="Branch with all children postponed.")
    for child in ("a", "b"):
        cd = branch / child
        cd.mkdir()
        _write_task_md(cd / "task.md", f"branch child {child}", "postponed",
                       objective="Postponed child.")

    return root


@pytest.fixture
def client(plan_root):
    """Create a TestClient with the dashboard server pointed at plan_root."""
    from starlette.testclient import TestClient

    # Reset module-level state
    plan_dashboard.PLAN_ROOT = plan_root
    plan_dashboard._project_root = str(plan_root.resolve().parent)
    plan_dashboard._jinja_env = None
    plan_dashboard.rebuild_tree()

    # Use the app without the lifespan (no watcher needed in tests)
    with TestClient(plan_dashboard.app, raise_server_exceptions=True) as c:
        yield c


@pytest.fixture
def flow_plan_root(tmp_path):
    """A plan tree with one parent whose direct children form a branching
    dependency chain (a -> b, a -> c, b -> d) and a second parent whose
    children have no inter-child dependency.  Exercises the GET /dag?root=
    data contract that base.html's children panel parses into cards.

    Statuses are deliberately varied so per-child fill colors are testable.
    """
    root = tmp_path / "superRA"
    root.mkdir()
    _write_task_md(root / "task.md", "Test Project", "not-started",
                   objective="A test plan.")

    # Parent with a branching dependency chain among its direct children.
    flow = root / "00-flow"
    flow.mkdir()
    _write_task_md(flow / "task.md", "Flow Parent", "in-progress",
                   objective="Branching children.")
    children = {
        "a": ("Child A", "approved", []),
        "b": ("Child B", "in-progress", ["a"]),
        "c": ("Child C", "not-started", ["a"]),
        "d": ("Child D", "not-started", ["b"]),
    }
    for slug, (title, status, deps) in children.items():
        d = flow / slug
        d.mkdir()
        _write_task_md(d / "task.md", title, status,
                       depends_on=deps, objective=f"Task {slug}.")

    # Parent whose children have no inter-child dependency.
    flat = root / "01-flat"
    flat.mkdir()
    _write_task_md(flat / "task.md", "Flat Parent", "not-started",
                   objective="Independent children.")
    for slug in ("x", "y"):
        d = flat / slug
        d.mkdir()
        _write_task_md(d / "task.md", f"Child {slug.upper()}", "not-started",
                       objective=f"Task {slug}.")

    return root


@pytest.fixture
def flow_client(flow_plan_root):
    """TestClient pointed at the branching-dependency plan tree."""
    from starlette.testclient import TestClient

    plan_dashboard.PLAN_ROOT = flow_plan_root
    plan_dashboard._project_root = str(flow_plan_root.resolve().parent)
    plan_dashboard._jinja_env = None
    plan_dashboard.rebuild_tree()
    with TestClient(plan_dashboard.app, raise_server_exceptions=True) as c:
        yield c


# ---------------------------------------------------------------------------
# TestServerRoutes
# ---------------------------------------------------------------------------


class TestServerRoutes:
    def test_index_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "Test Project" in resp.text

    def test_healthz_reports_dashboard_identity(self, client, monkeypatch):
        """The launcher's reuse probe relies on this identity payload."""
        monkeypatch.setattr(plan_dashboard, "DOC_MODE", False)
        monkeypatch.setattr(plan_dashboard, "REPO_ID", "abc123repoid")
        resp = client.get("/healthz")
        assert resp.status_code == 200
        body = resp.json()
        assert body["service"] == "superra-dashboard"
        assert body["pid"] == os.getpid()
        assert body["doc_mode"] is False
        assert body["repo_id"] == "abc123repoid"

    def test_healthz_reflects_doc_mode(self, client, monkeypatch):
        monkeypatch.setattr(plan_dashboard, "DOC_MODE", True)
        assert client.get("/healthz").json()["doc_mode"] is True

    def test_index_contains_workspace_shell(self, client):
        # The master-detail workspace renders an empty shell server-side; the
        # nav-tree and active-node regions are filled client-side from
        # /nav and /node, so the index no longer embeds the task-node tree.
        resp = client.get("/")
        text = resp.text
        assert 'id="nav-tree"' in text
        assert 'id="crumbs"' in text
        assert 'id="active-node"' in text
        assert 'id="children-dag"' in text
        # Workspace/Kanban toggle; the standalone DAG button is removed.
        assert 'id="btn-workspace"' in text
        assert 'id="btn-kanban"' in text
        assert 'id="btn-dag"' not in text

    def test_get_task_returns_children_fragment(self, client, plan_root):
        # Add children to 01-first so the fragment has content
        child = plan_root / "01-first" / "sub"
        child.mkdir()
        _write_task_md(child / "task.md", "Sub Task", "not-started",
                       objective="A child.")
        plan_dashboard.rebuild_tree()
        resp = client.get("/task/01-first")
        assert resp.status_code == 200

    def test_get_task_valid_path(self, client):
        resp = client.get("/task/01-first")
        assert resp.status_code == 200

    def test_get_task_nonexistent_returns_404(self, client):
        resp = client.get("/task/nonexistent")
        assert resp.status_code == 404

    def test_dag_returns_mermaid(self, client):
        resp = client.get("/dag")
        assert resp.status_code == 200
        assert "mermaid" in resp.text
        assert "graph LR" in resp.text

    def test_kanban_returns_7_columns(self, client):
        resp = client.get("/kanban")
        assert resp.status_code == 200
        # Each column has a kanban-col-header; count those for the 7 statuses
        assert resp.text.count("kanban-col-header") == 7

    def test_export_returns_attachment(self, client):
        """The Share route returns standalone HTML as a file download."""
        resp = client.get("/export")
        assert resp.status_code == 200
        cd = resp.headers.get("content-disposition", "")
        assert "attachment" in cd
        assert ".html" in cd
        assert "window.STANDALONE = true" in resp.text

    def test_export_subtree_scopes_and_names_file(self, flow_client):
        """A root= export scopes the embedded data to that subtree and names the
        download after the subtree slug."""
        resp = flow_client.get("/export", params={"root": "00-flow"})
        assert resp.status_code == 200
        assert 'filename="00-flow-dashboard.html"' in resp.headers.get(
            "content-disposition", ""
        )
        html = resp.text
        # Re-based subtree children present; out-of-subtree sibling absent.
        assert 'set["a"] = true' in html
        assert 'set["01-flat"] = true' not in html

    def test_export_unknown_root_returns_404(self, client):
        resp = client.get("/export", params={"root": "no/such"})
        assert resp.status_code == 404

    def test_export_filename_is_sanitized(self, client):
        """The download filename is interpolated into a quoted Content-Disposition
        value, so the slug must be restricted to filename-safe chars — a stray `"`
        (or path/control char) cannot break out of the header. The route's slug
        comes from a task slug, but defense-in-depth keeps the header safe even if
        an unusual slug ever reaches it (mirrors the route's sanitize regex)."""
        import re as _re

        # The header for a normal export carries only the safe charset between the
        # wrapping quotes (no raw quote injection possible).
        cd = client.get("/export").headers.get("content-disposition", "")
        m = _re.search(r'filename="([^"]*)"', cd)
        assert m, f"no quoted filename in: {cd!r}"
        name = m.group(1)
        assert _re.fullmatch(r"[A-Za-z0-9._-]+", name), f"unsafe filename: {name!r}"
        assert name.endswith("-dashboard.html")
        # The sanitizing transform the route applies neutralizes a hostile slug.
        sanitize = lambda s: _re.sub(r"[^A-Za-z0-9._-]", "-", s or "").strip("-") or "plan"
        assert sanitize('evil"drop') == "evil-drop"  # the `"` cannot escape the header
        assert sanitize("a/b") == "a-b"  # path separators neutralized
        assert sanitize("") == "plan"
        # Whatever the slug, the result is always header-safe (the property that
        # matters), even if dots survive (they are filename-safe).
        for hostile in ('x"y', "../../etc/passwd", "a;b\nc", "  "):
            assert _re.fullmatch(r"[A-Za-z0-9._-]+", sanitize(hostile))

    def test_export_does_not_disturb_live_state(self, client):
        """Rendering an export must restore the live server's module state so
        subsequent live routes are unaffected."""
        before = client.get("/node/01-first").text
        client.get("/export", params={"root": "01-first"})
        after = client.get("/node/01-first").text
        assert before == after
        # And the live index still serves (state intact).
        assert client.get("/").status_code == 200

    def test_index_wires_share_button(self, client):
        """The live page carries the Share affordance: the per-node Share button
        is emitted in the active-node card and backed by shareSubtree()."""
        html = client.get("/").text
        assert "function shareSubtree" in html
        # The button is gated to server mode in the card header builder.
        assert "shareSubtree(" in html
        assert "window.STANDALONE ? '' :" in html

    def test_served_page_keeps_cdn_render_tags(self, client):
        """Server mode is unchanged by the standalone embedding: the live page
        still loads markdown-it/KaTeX/texmath from the CDN and does NOT inline the
        vendored libraries or font woff2 data URIs."""
        html = client.get("/").text
        assert "cdn.jsdelivr.net/npm/markdown-it@14" in html
        assert "cdn.jsdelivr.net/npm/katex@0.16/dist/katex.min.css" in html
        assert "cdn.jsdelivr.net/npm/katex@0.16/dist/katex.min.js" in html
        assert "cdn.jsdelivr.net/npm/markdown-it-texmath@1" in html
        # No standalone-only inlining leaks into the served page.
        assert "data:font/woff2;base64," not in html
        assert "var STANDALONE_IMAGES =" not in html
        assert "window.STANDALONE = false" in html

    def test_files_serves_existing_file(self, client, plan_root):
        # Create a test file in the project root
        project_root = plan_root.parent
        test_file = project_root / "test_image.txt"
        test_file.write_text("file content here")
        resp = client.get("/files/test_image.txt")
        assert resp.status_code == 200

    def test_files_rejects_path_traversal(self, client):
        resp = client.get("/files/../../../etc/passwd")
        assert resp.status_code in (403, 404)

    def test_files_returns_404_for_missing(self, client):
        resp = client.get("/files/no_such_file.txt")
        assert resp.status_code == 404

    def test_events_sse_generator_yields_heartbeat(self, client):
        """The SSE event_generator yields a heartbeat as its first message.

        We drive the generator directly rather than through the HTTP layer to
        avoid blocking on the long-lived stream.  ``/events`` now resolves the
        worktree from the request and registers/unregisters the client's queue
        per worktree, so we pass a real Request and check it cleaned up.  The
        ``client`` fixture seeds the launch worktree state the resolver needs.
        """
        from starlette.requests import Request

        loop = asyncio.new_event_loop()

        def _req() -> Request:
            return Request({
                "type": "http", "method": "GET", "path": "/events",
                "query_string": b"", "headers": [],
            })

        async def _test():
            wt = plan_dashboard._launch_wt_id
            gen = plan_dashboard.sse_events(_req())
            resp = await gen
            body_iter = resp.body_iterator
            first = await body_iter.__anext__()
            assert "heartbeat" in first
            assert resp.media_type == "text/event-stream"
            # The client registered itself and started the launch watcher.
            assert wt in plan_dashboard._worktree_clients
            assert wt in plan_dashboard._worktree_watchers
            # Closing the stream removes the queue and stops the watcher.
            await body_iter.aclose()
            assert wt not in plan_dashboard._worktree_clients
            assert wt not in plan_dashboard._worktree_watchers

        try:
            loop.run_until_complete(_test())
        finally:
            plan_dashboard._worktree_clients.clear()
            plan_dashboard._worktree_watchers.clear()
            loop.close()

    def test_comment_api_crud(self, client, plan_root):
        """Test the full comment lifecycle: create -> list -> resolve -> delete."""
        # POST create
        resp = client.post(
            "/api/task/01-first/comment",
            json={
                "section": "Objective",
                "block_index": 0,
                "text_preview": "Complete step 1.",
                "body": "This looks good.",
                "author": "tester",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "created"
        comment_id = data["id"]

        # GET list
        resp = client.get("/api/task/01-first/comments")
        assert resp.status_code == 200
        comments = resp.json()
        assert len(comments) >= 1
        assert any(c["id"] == comment_id for c in comments)

        # PATCH resolve (toggle)
        resp = client.patch(f"/api/task/01-first/comment/{comment_id}")
        assert resp.status_code == 200
        assert resp.json()["resolved"] is True

        # DELETE
        resp = client.delete(f"/api/task/01-first/comment/{comment_id}")
        assert resp.status_code == 200
        assert resp.json()["status"] == "deleted"

        # Verify it's gone
        resp = client.get("/api/task/01-first/comments")
        assert all(c["id"] != comment_id for c in resp.json())

    def test_comments_summary_empty(self, client):
        """GET /api/comments/summary returns {} when no comments exist."""
        resp = client.get("/api/comments/summary")
        assert resp.status_code == 200
        assert resp.json() == {}

    def test_comments_summary_counts_unresolved(self, client, plan_root):
        """GET /api/comments/summary returns counts of unresolved comments per task."""
        # Add comments to different tasks
        add_comment(plan_root / "01-first", "Objective", 0, "p1", "body1", author="u")
        add_comment(plan_root / "01-first", "Results", 0, "p2", "body2", author="u")
        add_comment(plan_root / "02-second", "Objective", 0, "p3", "body3", author="u")

        resp = client.get("/api/comments/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["01-first"] == 2
        assert data["02-second"] == 1
        assert "03-third" not in data  # no comments

    def test_comments_summary_excludes_resolved(self, client, plan_root):
        """Resolved comments are not counted in the summary."""
        c = add_comment(plan_root / "01-first", "Objective", 0, "p", "body", author="u")
        resolve_comment(plan_root / "01-first", c.id)

        resp = client.get("/api/comments/summary")
        assert resp.status_code == 200
        data = resp.json()
        # c is resolved, so 01-first should not appear (count == 0)
        assert "01-first" not in data

    def test_comments_summary_nested_tasks(self, client, plan_root):
        """Summary includes comments on nested child tasks."""
        child = plan_root / "01-first" / "sub"
        child.mkdir()
        _write_task_md(child / "task.md", "Sub Task", "not-started",
                       objective="A child.")
        plan_dashboard.rebuild_tree()

        add_comment(child, "Objective", 0, "preview", "nested comment", author="u")

        resp = client.get("/api/comments/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["01-first/sub"] == 1

    def test_comment_api_404_on_bad_task(self, client):
        resp = client.post(
            "/api/task/nonexistent/comment",
            json={"body": "test"},
        )
        assert resp.status_code == 404

    def test_comment_resolve_404_on_bad_id(self, client):
        resp = client.patch("/api/task/01-first/comment/9999")
        assert resp.status_code == 404

    def test_comment_delete_404_on_bad_id(self, client):
        resp = client.delete("/api/task/01-first/comment/9999")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Per-worktree state + request resolution
#
# The dashboard serves any discovered worktree on demand, resolved per request
# from the ``?wt=<name>`` query param (worktree id = canonical selector token).  A
# request with no ``?wt=`` resolves to the launch worktree; an unknown ``?wt=``
# is a 404.  These tests build two distinct trees, seed both into the worktree
# cache, and assert each request renders from the matching tree's state.
# ---------------------------------------------------------------------------


@pytest.fixture
def two_worktree_client(tmp_path):
    """A TestClient with two worktree trees ('wt-a', 'wt-b') seeded in the
    worktree cache, the first as the launch (default) worktree.

    Each worktree's plan root lives at ``tmp_path/<wt-id>/superRA`` so the
    directory basename (the worktree id) is distinct and stable.  Yields
    ``(client, wt_a_id, wt_b_id)``.
    """
    from starlette.testclient import TestClient

    def _make_tree(wt_id: str, title_suffix: str):
        wt_dir = tmp_path / wt_id
        wt_dir.mkdir()
        root = wt_dir / "superRA"
        root.mkdir()
        _write_task_md(root / "task.md", f"Project {title_suffix}", "not-started",
                       objective=f"Plan {title_suffix}.")
        d1 = root / "01-first"
        d1.mkdir()
        _write_task_md(d1 / "task.md", f"First {title_suffix}", "approved",
                       objective=f"Step one in {title_suffix}.")
        return root

    root_a = _make_tree("wt-a", "A")
    root_b = _make_tree("wt-b", "B")

    plan_dashboard._jinja_env = None
    plan_dashboard._worktree_cache.clear()

    # Launch worktree = wt-a (the default when no ?wt= is given).
    plan_dashboard.PLAN_ROOT = root_a
    plan_dashboard.rebuild_tree()
    wt_a_id = plan_dashboard._launch_wt_id

    # Seed wt-b into the cache directly (a second discovered worktree).
    wt_b_id = plan_dashboard._worktree_id_for_plan_root(root_b)
    plan_dashboard._worktree_cache[wt_b_id] = plan_dashboard._build_worktree_state(
        wt_b_id, root_b
    )

    # Run without the lifespan watcher (no need; cache is seeded manually).
    c = TestClient(plan_dashboard.app, raise_server_exceptions=True)
    try:
        yield c, wt_a_id, wt_b_id
    finally:
        plan_dashboard._worktree_cache.clear()


class TestPerWorktreeResolution:
    def test_node_resolves_by_wt_param(self, two_worktree_client):
        client, wt_a, wt_b = two_worktree_client
        a = client.get(f"/node/01-first?wt={wt_a}")
        b = client.get(f"/node/01-first?wt={wt_b}")
        assert a.status_code == 200 and b.status_code == 200
        assert "Step one in A." in a.text
        assert "Step one in B." in b.text
        assert "Step one in B." not in a.text

    def test_nav_resolves_by_wt_param(self, two_worktree_client):
        client, wt_a, wt_b = two_worktree_client
        a = client.get(f"/nav?wt={wt_a}").text
        b = client.get(f"/nav?wt={wt_b}").text
        # Both trees have a single '01-first' child; titles differ per tree.
        assert "First A" in a
        assert "First B" in b
        assert "First B" not in a

    def test_index_resolves_by_wt_param(self, two_worktree_client):
        client, wt_a, wt_b = two_worktree_client
        assert "Project A" in client.get(f"/?wt={wt_a}").text
        assert "Project B" in client.get(f"/?wt={wt_b}").text

    def test_no_wt_param_returns_launch_worktree(self, two_worktree_client):
        client, wt_a, wt_b = two_worktree_client
        # Launch worktree is wt-a; a request with no ?wt= must render it.
        assert "Step one in A." in client.get("/node/01-first").text
        assert "Project A" in client.get("/").text

    def test_comments_summary_resolves_by_wt_param(self, two_worktree_client):
        client, wt_a, wt_b = two_worktree_client
        a_state = plan_dashboard._worktree_cache[wt_a]
        b_state = plan_dashboard._worktree_cache[wt_b]
        add_comment(a_state.plan_root / "01-first", "Objective", 0, "p", "ba", author="u")
        add_comment(b_state.plan_root / "01-first", "Objective", 0, "p", "bb", author="u")
        add_comment(b_state.plan_root / "01-first", "Objective", 1, "p2", "bb2", author="u")
        assert client.get(f"/api/comments/summary?wt={wt_a}").json() == {"01-first": 1}
        assert client.get(f"/api/comments/summary?wt={wt_b}").json() == {"01-first": 2}

    def test_unknown_wt_returns_404(self, two_worktree_client):
        client, wt_a, wt_b = two_worktree_client
        # A ?wt= that is neither the launch worktree nor a discovered one. The
        # tmp trees are not git worktrees, so discovery yields no match -> 404.
        assert client.get("/node/01-first?wt=no-such-worktree").status_code == 404
        assert client.get("/nav?wt=no-such-worktree").status_code == 404

    def test_state_cached_and_rebuilt_on_invalidation(self, two_worktree_client):
        client, wt_a, wt_b = two_worktree_client
        # Cache hit: resolving the launch worktree twice returns the same object.
        from starlette.requests import Request

        def _req(qs: str) -> Request:
            scope = {
                "type": "http", "method": "GET", "path": "/",
                "query_string": qs.encode(), "headers": [],
            }
            return Request(scope)

        first = plan_dashboard.resolve_worktree(_req(f"wt={wt_a}"))
        second = plan_dashboard.resolve_worktree(_req(f"wt={wt_a}"))
        assert first is second  # cache hit, not rebuilt

        # Edit the launch worktree's task on disk, then invalidate via the hook.
        task_md = first.plan_root / "01-first" / "task.md"
        task_md.write_text(task_md.read_text().replace("First A", "Edited A"))
        # Pre-invalidation: cached state still shows the old title.
        assert first.task_index["01-first"].title == "First A"
        rebuilt = plan_dashboard.rebuild_worktree_state(wt_a)
        assert rebuilt is first  # same object, refreshed in place
        assert first.task_index["01-first"].title == "Edited A"


# ---------------------------------------------------------------------------
# TestDataLayer
# ---------------------------------------------------------------------------


class TestDataLayer:
    def test_rebuild_tree_populates_index(self, plan_root):
        plan_dashboard.PLAN_ROOT = plan_root
        plan_dashboard.rebuild_tree()
        assert "" in plan_dashboard._task_index  # root
        assert "01-first" in plan_dashboard._task_index
        assert "02-second" in plan_dashboard._task_index
        assert "03-third" in plan_dashboard._task_index

    def test_rebuild_task_updates_single(self, plan_root):
        plan_dashboard.PLAN_ROOT = plan_root
        plan_dashboard.rebuild_tree()

        # Modify the task on disk
        task_md = plan_root / "01-first" / "task.md"
        content = task_md.read_text()
        content = content.replace("First Task", "Updated First Task")
        task_md.write_text(content)

        updated, children_changed = plan_dashboard.rebuild_task("01-first")
        assert updated is not None
        assert updated.title == "Updated First Task"
        assert plan_dashboard._task_index["01-first"].title == "Updated First Task"
        assert children_changed is False

    def test_rebuild_task_discovers_existing_children(self, plan_root):
        # Add a child to 01-first
        child = plan_root / "01-first" / "sub"
        child.mkdir()
        _write_task_md(child / "task.md", "Sub Task", "not-started")
        plan_dashboard.PLAN_ROOT = plan_root
        plan_dashboard.rebuild_tree()

        original = plan_dashboard._task_index["01-first"]
        assert len(original.children) == 1

        # rebuild_task should re-discover existing children
        updated, children_changed = plan_dashboard.rebuild_task("01-first")
        assert updated is not None
        assert len(updated.children) == 1
        assert updated.children[0].title == "Sub Task"
        assert children_changed is False

    def test_rebuild_task_discovers_new_children(self, plan_root):
        """A new child created after the initial tree build is discovered."""
        plan_dashboard.PLAN_ROOT = plan_root
        plan_dashboard.rebuild_tree()

        original = plan_dashboard._task_index["01-first"]
        assert len(original.children) == 0

        # Create a new child directory after the tree was built
        child = plan_root / "01-first" / "sub"
        child.mkdir()
        _write_task_md(child / "task.md", "New Child", "not-started")

        updated, children_changed = plan_dashboard.rebuild_task("01-first")
        assert updated is not None
        assert children_changed is True
        assert len(updated.children) == 1
        assert updated.children[0].title == "New Child"
        # New child should be in the flat index
        assert "01-first/sub" in plan_dashboard._task_index

    def test_rebuild_task_removes_deleted_children(self, plan_root):
        """A child removed from disk is dropped from the tree and index."""
        child = plan_root / "01-first" / "sub"
        child.mkdir()
        _write_task_md(child / "task.md", "Doomed Child", "not-started")
        plan_dashboard.PLAN_ROOT = plan_root
        plan_dashboard.rebuild_tree()

        assert "01-first/sub" in plan_dashboard._task_index
        assert len(plan_dashboard._task_index["01-first"].children) == 1

        # Remove the child's task.md (simulating directory deletion)
        (child / "task.md").unlink()
        child.rmdir()

        updated, children_changed = plan_dashboard.rebuild_task("01-first")
        assert updated is not None
        assert children_changed is True
        assert len(updated.children) == 0
        assert "01-first/sub" not in plan_dashboard._task_index

    def test_rebuild_task_returns_none_for_deleted(self, plan_root):
        plan_dashboard.PLAN_ROOT = plan_root
        plan_dashboard.rebuild_tree()
        # Remove the task.md
        (plan_root / "01-first" / "task.md").unlink()
        result, children_changed = plan_dashboard.rebuild_task("01-first")
        assert result is None
        assert "01-first" not in plan_dashboard._task_index

    def test_build_index_creates_flat_dict(self, plan_root):
        plan_dashboard.PLAN_ROOT = plan_root
        plan_dashboard.rebuild_tree()
        root = plan_dashboard._root_task
        idx: dict[str, _task_io.Task] = {}
        plan_dashboard._build_index(root, idx)
        assert "" in idx
        assert "01-first" in idx
        assert "02-second" in idx
        assert "03-third" in idx
        assert len(idx) == 4  # root + 3 children


# ---------------------------------------------------------------------------
# TestComments
# ---------------------------------------------------------------------------


class TestComments:
    def test_load_comments_empty_for_missing(self, tmp_path):
        assert load_comments(tmp_path) == []

    def test_add_comment_auto_increment(self, tmp_path):
        c1 = add_comment(tmp_path, "Objective", 0, "preview1", "body1", author="user")
        c2 = add_comment(tmp_path, "Objective", 1, "preview2", "body2", author="user")
        assert c1.id == 1
        assert c2.id == 2

    def test_add_comment_gap_handling(self, tmp_path):
        """After deleting a comment, next ID should still be max+1."""
        c1 = add_comment(tmp_path, "Objective", 0, "p1", "b1", author="u")
        c2 = add_comment(tmp_path, "Objective", 1, "p2", "b2", author="u")
        delete_comment(tmp_path, c1.id)
        c3 = add_comment(tmp_path, "Objective", 2, "p3", "b3", author="u")
        assert c3.id == 3  # max was 2, so next is 3

    def test_resolve_comment_toggles(self, tmp_path):
        c = add_comment(tmp_path, "Objective", 0, "preview", "body", author="u")
        assert c.resolved is False
        resolved = resolve_comment(tmp_path, c.id)
        assert resolved is not None
        assert resolved.resolved is True
        # Toggle back
        unresolved = resolve_comment(tmp_path, c.id)
        assert unresolved is not None
        assert unresolved.resolved is False

    def test_resolve_nonexistent_returns_none(self, tmp_path):
        assert resolve_comment(tmp_path, 999) is None

    def test_delete_comment_returns_bool(self, tmp_path):
        c = add_comment(tmp_path, "S", 0, "p", "b", author="u")
        assert delete_comment(tmp_path, c.id) is True
        assert delete_comment(tmp_path, c.id) is False  # already deleted

    def test_split_into_blocks_paragraphs(self):
        text = "First paragraph.\n\nSecond paragraph.\n\nThird."
        blocks = split_into_blocks(text)
        assert len(blocks) == 3
        assert blocks[0] == "First paragraph."
        assert blocks[1] == "Second paragraph."
        assert blocks[2] == "Third."

    def test_split_into_blocks_fenced_code(self):
        text = "Before.\n\n```python\nx = 1\ny = 2\n```\n\nAfter."
        blocks = split_into_blocks(text)
        assert len(blocks) == 3
        assert "```python" in blocks[1]
        assert "x = 1" in blocks[1]

    def test_split_into_blocks_lists(self):
        text = "Intro.\n\n- item 1\n- item 2\n- item 3\n\nEnd."
        blocks = split_into_blocks(text)
        assert len(blocks) == 3
        # The list items should be grouped into one block
        assert "item 1" in blocks[1]
        assert "item 2" in blocks[1]
        assert "item 3" in blocks[1]

    def test_resolve_anchors_exact_match(self):
        body = "## Objective\n\nFirst block.\n\nSecond block.\n"
        from _comments import Comment, CommentAnchor
        anchor = CommentAnchor(section="Objective", block_index=0, text_preview="First block.")
        comment = Comment(id=1, author="u", timestamp="2026-01-01", resolved=False,
                          anchor=anchor, body="test")
        result = resolve_anchors([comment], body)
        assert result[0].orphaned is False
        assert result[0].anchor.block_index == 0

    def test_resolve_anchors_shifted_block(self):
        """When a block has moved to a different index, resolve_anchors should update."""
        body = "## Objective\n\nNew first block.\n\nOriginal block.\n"
        from _comments import Comment, CommentAnchor
        anchor = CommentAnchor(section="Objective", block_index=0, text_preview="Original block.")
        comment = Comment(id=1, author="u", timestamp="2026-01-01", resolved=False,
                          anchor=anchor, body="test")
        result = resolve_anchors([comment], body)
        assert result[0].orphaned is False
        assert result[0].anchor.block_index == 1  # shifted to index 1

    def test_resolve_anchors_orphan_detection(self):
        body = "## Objective\n\nCompletely different content.\n"
        from _comments import Comment, CommentAnchor
        anchor = CommentAnchor(section="Objective", block_index=0, text_preview="Gone text.")
        comment = Comment(id=1, author="u", timestamp="2026-01-01", resolved=False,
                          anchor=anchor, body="test")
        result = resolve_anchors([comment], body)
        assert result[0].orphaned is True

    def test_resolve_anchors_missing_section(self):
        body = "## Results\n\nSome results.\n"
        from _comments import Comment, CommentAnchor
        anchor = CommentAnchor(section="Objective", block_index=0, text_preview="text")
        comment = Comment(id=1, author="u", timestamp="2026-01-01", resolved=False,
                          anchor=anchor, body="test")
        result = resolve_anchors([comment], body)
        assert result[0].orphaned is True

    def test_yaml_roundtrip(self, tmp_path):
        c = add_comment(tmp_path, "Objective", 0, "preview", "body text", author="user1")
        loaded = load_comments(tmp_path)
        assert len(loaded) == 1
        assert loaded[0].id == c.id
        assert loaded[0].author == "user1"
        assert loaded[0].body == "body text"
        assert loaded[0].anchor.section == "Objective"
        assert loaded[0].anchor.block_index == 0
        assert loaded[0].anchor.text_preview == "preview"
        assert loaded[0].resolved is False


# ---------------------------------------------------------------------------
# TestSSEBroadcast
# ---------------------------------------------------------------------------


class TestSSEBroadcast:
    """Broadcast framing, scoped to a worktree's client set (task 02)."""

    @staticmethod
    def _register(wt: str, queue: asyncio.Queue) -> None:
        plan_dashboard._worktree_clients.setdefault(wt, set()).add(queue)

    @staticmethod
    def _cleanup(wt: str) -> None:
        plan_dashboard._worktree_clients.pop(wt, None)

    def test_broadcast_single_line(self):
        """Single-line data gets proper SSE framing."""
        loop = asyncio.new_event_loop()
        queue: asyncio.Queue[str] = asyncio.Queue()
        self._register("wt-a", queue)
        try:
            loop.run_until_complete(plan_dashboard._broadcast("test-event", "hello", "wt-a"))
            msg = loop.run_until_complete(asyncio.wait_for(queue.get(), timeout=1))
            assert msg.startswith("event: test-event\n")
            assert "data: hello\n" in msg
        finally:
            self._cleanup("wt-a")
            loop.close()

    def test_broadcast_multiline(self):
        """Multi-line data gets per-line data: prefix per SSE spec."""
        loop = asyncio.new_event_loop()
        queue: asyncio.Queue[str] = asyncio.Queue()
        self._register("wt-a", queue)
        try:
            loop.run_until_complete(
                plan_dashboard._broadcast("task:foo", "line1\nline2\nline3", "wt-a")
            )
            msg = loop.run_until_complete(asyncio.wait_for(queue.get(), timeout=1))
            assert "event: task:foo\n" in msg
            assert "data: line1\n" in msg
            assert "data: line2\n" in msg
            assert "data: line3\n" in msg
        finally:
            self._cleanup("wt-a")
            loop.close()

    def test_event_naming_task_path(self):
        """Per-task events use event: task:{path} naming."""
        loop = asyncio.new_event_loop()
        queue: asyncio.Queue[str] = asyncio.Queue()
        self._register("wt-a", queue)
        try:
            loop.run_until_complete(
                plan_dashboard._broadcast("task:my/nested/path", "<div>html</div>", "wt-a")
            )
            msg = loop.run_until_complete(asyncio.wait_for(queue.get(), timeout=1))
            assert msg.startswith("event: task:my/nested/path\n")
        finally:
            self._cleanup("wt-a")
            loop.close()

    def test_broadcast_drops_full_queue(self):
        """When a client queue is full, the client is removed."""
        loop = asyncio.new_event_loop()
        queue: asyncio.Queue[str] = asyncio.Queue(maxsize=1)
        # Fill the queue
        queue.put_nowait("filler")
        self._register("wt-a", queue)
        try:
            # This should not raise; the full queue gets dropped
            loop.run_until_complete(plan_dashboard._broadcast("e", "data", "wt-a"))
            assert queue not in plan_dashboard._worktree_clients.get("wt-a", set())
        finally:
            self._cleanup("wt-a")
            loop.close()

    def test_broadcast_scoped_to_worktree(self):
        """A broadcast to worktree A reaches only A's queues, never B's."""
        loop = asyncio.new_event_loop()
        qa: asyncio.Queue[str] = asyncio.Queue()
        qb: asyncio.Queue[str] = asyncio.Queue()
        self._register("wt-a", qa)
        self._register("wt-b", qb)
        try:
            loop.run_until_complete(
                plan_dashboard._broadcast("task:01-first", "<div>a</div>", "wt-a")
            )
            msg = loop.run_until_complete(asyncio.wait_for(qa.get(), timeout=1))
            assert "task:01-first" in msg
            # B's queue saw nothing.
            assert qb.empty()
        finally:
            self._cleanup("wt-a")
            self._cleanup("wt-b")
            loop.close()

    def test_broadcast_to_empty_worktree_is_noop(self):
        """A broadcast after the last client left does not raise."""
        loop = asyncio.new_event_loop()
        try:
            # No clients registered for this worktree at all.
            loop.run_until_complete(
                plan_dashboard._broadcast("full-reload", "{}", "gone")
            )
        finally:
            loop.close()


# ---------------------------------------------------------------------------
# TestWatcherLifecycle
# ---------------------------------------------------------------------------


class TestWatcherLifecycle:
    """Per-worktree watcher spawn/teardown (task 02).

    These exercise ``_ensure_watcher`` / ``_stop_watcher`` and the ``/events``
    register-then-ensure ordering directly, since TestClient disables lifespan
    and a live HTTP stream would block.  Each test runs on a fresh event loop and
    seeds a real on-disk plan root so ``watchfiles.awatch`` has a valid dir to
    watch; the watcher is cancelled before it ever needs a real fs event.
    """

    def _seed(self, tmp_path, wt_id: str):
        """Create a minimal plan tree and cache a WorktreeState for *wt_id*."""
        root = tmp_path / wt_id / "superRA"
        root.mkdir(parents=True)
        _write_task_md(root / "task.md", f"Root {wt_id}", "not-started",
                       objective="seed")
        plan_dashboard._worktree_cache[wt_id] = plan_dashboard._build_worktree_state(
            wt_id, root
        )

    def _reset(self):
        plan_dashboard._worktree_cache.clear()
        plan_dashboard._worktree_clients.clear()
        plan_dashboard._worktree_watchers.clear()
        plan_dashboard._worktree_locks.clear()

    def test_first_client_starts_exactly_one_watcher(self, tmp_path):
        loop = asyncio.new_event_loop()
        self._reset()
        self._seed(tmp_path, "wt-a")

        async def _test():
            await plan_dashboard._ensure_watcher("wt-a")
            task = plan_dashboard._worktree_watchers.get("wt-a")
            assert task is not None and not task.done()
            # A second ensure for the same worktree does not start a second.
            await plan_dashboard._ensure_watcher("wt-a")
            assert plan_dashboard._worktree_watchers["wt-a"] is task
            await plan_dashboard._stop_watcher("wt-a")

        try:
            loop.run_until_complete(_test())
        finally:
            self._reset()
            loop.close()

    def test_last_disconnect_stops_watcher(self, tmp_path):
        loop = asyncio.new_event_loop()
        self._reset()
        self._seed(tmp_path, "wt-a")

        async def _test():
            await plan_dashboard._ensure_watcher("wt-a")
            assert "wt-a" in plan_dashboard._worktree_watchers
            await plan_dashboard._stop_watcher("wt-a")
            # Popped, not left as a zombie entry.
            assert "wt-a" not in plan_dashboard._worktree_watchers

        try:
            loop.run_until_complete(_test())
        finally:
            self._reset()
            loop.close()

    def test_stop_is_bounded_under_repeated_cancellation(self, monkeypatch):
        """A non-finishing watcher is force-cancelled after a cooperative bound."""
        loop = asyncio.new_event_loop()
        self._reset()
        monkeypatch.setattr(
            plan_dashboard, "WATCHER_STOP_TIMEOUT", 0.03, raising=False
        )
        monkeypatch.setattr(
            plan_dashboard, "WATCHER_CANCEL_TIMEOUT", 0.03, raising=False
        )
        forced_exit_delays = []
        monkeypatch.setattr(
            plan_dashboard,
            "_schedule_forced_process_exit",
            forced_exit_delays.append,
            raising=False,
        )

        async def _test():
            stop_event = asyncio.Event()
            teardown_started = asyncio.Event()
            never_finishes_cooperatively = asyncio.Event()
            hard_cancelled = False

            async def _watcher():
                nonlocal hard_cancelled
                await stop_event.wait()
                teardown_started.set()
                try:
                    await never_finishes_cooperatively.wait()
                except asyncio.CancelledError:
                    hard_cancelled = True
                    # Model a faulty replacement/native boundary that suppresses
                    # hard cancellation too. _stop_watcher must still return.
                    await never_finishes_cooperatively.wait()

            watcher = asyncio.create_task(_watcher())
            plan_dashboard._worktree_watchers["wt-a"] = watcher
            plan_dashboard._worktree_stop_events["wt-a"] = stop_event

            stopper = asyncio.create_task(plan_dashboard._stop_watcher("wt-a"))
            await teardown_started.wait()
            for _ in range(3):
                stopper.cancel()
                await asyncio.sleep(0)
            await asyncio.sleep(0.08)
            completed_within_bound = stopper.done()

            # Let the reviewed, unbounded implementation unwind so a failing
            # assertion cannot strand this test's event loop.
            if not completed_within_bound:
                never_finishes_cooperatively.set()
            with pytest.raises(asyncio.CancelledError):
                await stopper

            assert completed_within_bound, "watcher teardown exceeded its bound"
            assert hard_cancelled, "non-finishing watcher was not force-cancelled"
            assert forced_exit_delays == [plan_dashboard.WATCHER_PROCESS_EXIT_TIMEOUT]
            assert not watcher.done(), "cancellation-suppressing watcher unexpectedly ended"
            never_finishes_cooperatively.set()
            await watcher
            assert watcher.done() and not watcher.cancelled()

        try:
            loop.run_until_complete(_test())
        finally:
            self._reset()
            loop.close()

    def test_late_watcher_completion_disarms_process_exit(self, monkeypatch):
        """A watcher finishing after both bounds cancels its armed watchdog."""
        loop = asyncio.new_event_loop()
        self._reset()
        monkeypatch.setattr(plan_dashboard, "WATCHER_STOP_TIMEOUT", 0.01)
        monkeypatch.setattr(plan_dashboard, "WATCHER_CANCEL_TIMEOUT", 0.01)
        forced_exits = []
        monkeypatch.setattr(plan_dashboard.os, "_exit", forced_exits.append)
        monkeypatch.setattr(plan_dashboard, "_standalone_process_owner", True)

        class FakeTimer:
            instances = []

            def __init__(self, delay, function, args=()):
                self.delay = delay
                self.function = function
                self.args = args
                self.daemon = False
                self.started = False
                self.cancelled = False
                self.instances.append(self)

            def start(self):
                self.started = True

            def cancel(self):
                self.cancelled = True

            def fire(self):
                if not self.cancelled:
                    self.function(*self.args)

        monkeypatch.setattr(plan_dashboard.threading, "Timer", FakeTimer)

        async def _test():
            stop_event = asyncio.Event()
            release = asyncio.Event()

            async def _watcher():
                await stop_event.wait()
                try:
                    await release.wait()
                except asyncio.CancelledError:
                    await release.wait()

            watcher = asyncio.create_task(_watcher())
            plan_dashboard._worktree_watchers["wt-a"] = watcher
            plan_dashboard._worktree_stop_events["wt-a"] = stop_event

            await plan_dashboard._stop_watcher("wt-a")
            assert len(FakeTimer.instances) == 1
            watchdog = FakeTimer.instances[0]
            assert watchdog.started and not watchdog.cancelled

            release.set()
            await watcher
            await asyncio.sleep(0)
            assert watchdog.cancelled
            watchdog.fire()
            assert forced_exits == []

        try:
            loop.run_until_complete(_test())
        finally:
            self._reset()
            loop.close()

    def test_embedded_server_thread_cannot_arm_process_exit(self, monkeypatch):
        """An in-process server thread never owns or terminates its host process."""
        import threading

        created = []
        monkeypatch.setattr(plan_dashboard, "_standalone_process_owner", True)
        monkeypatch.setattr(
            plan_dashboard.threading,
            "Timer",
            lambda *args, **kwargs: created.append((args, kwargs)),
        )
        results = []
        thread = threading.Thread(
            target=lambda: results.append(
                plan_dashboard._schedule_forced_process_exit(0.01)
            )
        )
        thread.start()
        thread.join(timeout=2.0)
        assert not thread.is_alive()
        assert results == [None]
        assert created == []

    def test_embedded_main_thread_cannot_arm_process_exit(self, monkeypatch):
        """A stale server handle cannot grant main-thread process ownership."""
        created = []
        monkeypatch.setattr(plan_dashboard, "_server", object())
        monkeypatch.setattr(
            plan_dashboard.threading,
            "Timer",
            lambda *args, **kwargs: created.append((args, kwargs)),
        )

        monkeypatch.setattr(plan_dashboard, "_standalone_process_owner", False)
        assert plan_dashboard._schedule_forced_process_exit(0.01) is None
        assert created == []

    def test_crashed_watcher_is_respawned(self, tmp_path):
        loop = asyncio.new_event_loop()
        self._reset()
        self._seed(tmp_path, "wt-a")

        async def _test():
            # A present-but-done() task stands in for a crashed/finished watcher.
            async def _noop():
                return None
            dead = asyncio.create_task(_noop())
            await dead
            assert dead.done()
            plan_dashboard._worktree_watchers["wt-a"] = dead
            # ensure_watcher must treat the done task as absent and respawn.
            await plan_dashboard._ensure_watcher("wt-a")
            fresh = plan_dashboard._worktree_watchers["wt-a"]
            assert fresh is not dead
            assert not fresh.done()
            await plan_dashboard._stop_watcher("wt-a")

        try:
            loop.run_until_complete(_test())
        finally:
            self._reset()
            loop.close()

    def test_content_edit_under_a_is_scoped_to_a(self, tmp_path):
        """A content edit under worktree A broadcasts a task:<path> event to A's
        clients and nothing to B's."""
        import watchfiles

        loop = asyncio.new_event_loop()
        self._reset()
        # Two worktrees, each with a child task to edit.
        for wt in ("wt-a", "wt-b"):
            root = tmp_path / wt / "superRA"
            root.mkdir(parents=True)
            _write_task_md(root / "task.md", f"Root {wt}", "not-started",
                           objective="seed")
            child = root / "01-first"
            child.mkdir()
            _write_task_md(child / "task.md", f"First {wt}", "approved",
                           objective="step")
            plan_dashboard._worktree_cache[wt] = (
                plan_dashboard._build_worktree_state(wt, root)
            )
        plan_dashboard._jinja_env = None

        qa: asyncio.Queue[str] = asyncio.Queue(maxsize=256)
        qb: asyncio.Queue[str] = asyncio.Queue(maxsize=256)
        plan_dashboard._worktree_clients["wt-a"] = {qa}
        plan_dashboard._worktree_clients["wt-b"] = {qb}

        async def _test():
            state_a = plan_dashboard._worktree_cache["wt-a"]
            edited = state_a.plan_root / "01-first" / "task.md"
            # A pure content edit (no child-set change) -> task:<path> fragment.
            changes = {(watchfiles.Change.modified, str(edited))}
            await plan_dashboard._rebuild_and_broadcast(state_a, changes)
            # A saw a task-scoped event; B's queue stayed empty.
            assert not qa.empty()
            msg = qa.get_nowait()
            assert "event: task:01-first" in msg
            assert qb.empty()

        try:
            loop.run_until_complete(_test())
        finally:
            self._reset()
            plan_dashboard._jinja_env = None
            loop.close()

    def test_events_registers_queue_before_ensuring_watcher(self, tmp_path):
        """No event-loss on the init race: the client's queue is in the
        worktree's client set before its watcher can emit.

        We patch ``_ensure_watcher`` to capture whether the queue is already
        registered at the moment the watcher would be ensured.
        """
        from starlette.requests import Request

        loop = asyncio.new_event_loop()
        self._reset()
        self._seed(tmp_path, "wt-a")
        plan_dashboard._launch_wt_id = "wt-a"

        seen = {}

        async def _spy(wt):
            seen["clients_at_ensure"] = len(plan_dashboard._worktree_clients.get(wt, set()))

        def _req() -> Request:
            return Request({
                "type": "http", "method": "GET", "path": "/events",
                "query_string": b"wt=wt-a", "headers": [],
            })

        async def _test():
            with patch.object(plan_dashboard, "_ensure_watcher", _spy):
                gen = plan_dashboard.sse_events(_req())
                resp = await gen
                body_iter = resp.body_iterator
                first = await body_iter.__anext__()
                assert "heartbeat" in first
                # The watcher (spy) ran only after the queue was registered.
                assert seen["clients_at_ensure"] == 1
                await body_iter.aclose()

        try:
            loop.run_until_complete(_test())
        finally:
            self._reset()
            loop.close()


# ---------------------------------------------------------------------------
# TestTemplateRendering
# ---------------------------------------------------------------------------


class TestTemplateRendering:
    def setup_method(self):
        """Reset the Jinja env so each test gets a clean state."""
        plan_dashboard._jinja_env = None

    def test_render_task_node_has_sse_swap(self, plan_root):
        plan_dashboard.PLAN_ROOT = plan_root
        plan_dashboard._project_root = str(plan_root.parent)
        plan_dashboard.rebuild_tree()
        task = plan_dashboard._task_index["01-first"]
        html = plan_dashboard._render_task_node(task)
        assert 'sse-swap="task:01-first"' in html
        assert 'hx-swap="outerHTML"' in html

    def test_render_task_node_has_badge(self, plan_root):
        plan_dashboard.PLAN_ROOT = plan_root
        plan_dashboard._project_root = str(plan_root.parent)
        plan_dashboard.rebuild_tree()
        task = plan_dashboard._task_index["01-first"]
        html = plan_dashboard._render_task_node(task)
        assert "badge-approved" in html
        assert "01-first" in html  # slug

    def test_render_summary_has_counts(self, plan_root):
        plan_dashboard.PLAN_ROOT = plan_root
        plan_dashboard._project_root = str(plan_root.parent)
        plan_dashboard.rebuild_tree()
        html = plan_dashboard._render_summary()
        assert "stat-tasks" in html
        assert "stat-approved" in html
        # 3 leaf tasks, 1 approved
        assert "1/3" in html

    def test_postponed_excluded_from_summary_denominator(self, postponed_plan_root):
        """Postponed leaves drop out of the active denominator, like archived,
        and surface as a visible count pill."""
        plan_dashboard.PLAN_ROOT = postponed_plan_root
        plan_dashboard._project_root = str(postponed_plan_root.parent)
        plan_dashboard.rebuild_tree()
        html = plan_dashboard._render_summary()
        # Leaves: 01 postponed, 02 not-started, 03 approved, branch a/b postponed.
        # active = 5 - 3 postponed = 2; approved = 1 -> 1/2.
        assert "1/2" in html
        assert "<strong>3</strong> postponed" in html

    def test_postponed_kanban_column_holds_postponed_leaves(self, postponed_plan_root):
        plan_dashboard.PLAN_ROOT = postponed_plan_root
        plan_dashboard._project_root = str(postponed_plan_root.parent)
        plan_dashboard.rebuild_tree()
        env = plan_dashboard._get_jinja_env()
        template = env.get_template("kanban.html")
        all_tasks = _task_io.collect_all_tasks(plan_dashboard._root_task)
        html = template.render(all_tasks=all_tasks)
        # The Postponed column exists and carries the postponed leaf + branch children.
        post_col = html.split('<div class="kanban-col">')
        post_col = next(p for p in post_col if p.lstrip().startswith("<div class=\"kanban-col-header\">\n      Postponed"))
        assert "01-postponed-leaf" in post_col
        assert "04-postponed-branch/a" in post_col
        assert "04-postponed-branch/b" in post_col

    def test_postponed_renders_badge_and_status(self, postponed_plan_root):
        plan_dashboard.PLAN_ROOT = postponed_plan_root
        plan_dashboard._project_root = str(postponed_plan_root.parent)
        plan_dashboard.rebuild_tree()
        task = plan_dashboard._task_index["01-postponed-leaf"]
        html = plan_dashboard._render_task_node(task)
        assert "badge-postponed" in html
        assert 'data-status="postponed"' in html

    def test_vscode_link_filter(self, plan_root):
        plan_dashboard.PLAN_ROOT = plan_root
        plan_dashboard._project_root = str(plan_root.parent)
        env = plan_dashboard._get_jinja_env()
        result = env.filters["vscode_link"]("src/main.py", "/project")
        assert result == "vscode://file//project/src/main.py"

    def test_file_url_filter(self, plan_root):
        plan_dashboard.PLAN_ROOT = plan_root
        plan_dashboard._project_root = str(plan_root.parent)
        env = plan_dashboard._get_jinja_env()
        result = env.filters["file_url"]("images/fig1.png")
        assert result == "/files/images/fig1.png"

    def test_script_payload_escapes_closing_script_tag(self, plan_root):
        """</script> in markdown content must be escaped so it cannot break out
        of the <script type="text/x-markdown"> payload container.

        (The payload used to live in a <template> element — hence the old test
        name — but was moved to a <script type="text/x-markdown"> tag, whose
        only breakout sequence is </script>.)
        """
        plan_dashboard.PLAN_ROOT = plan_root
        plan_dashboard._project_root = str(plan_root.parent)

        # Write a task whose body contains a literal </script>
        task_md = plan_root / "01-first" / "task.md"
        content = task_md.read_text()
        content = content.replace("Complete step 1.", "Use </script> tag in code.")
        task_md.write_text(content)
        plan_dashboard.rebuild_tree()

        task = plan_dashboard._task_index["01-first"]
        html = plan_dashboard._render_task_node(task)
        # The content's </script> is backslash-escaped to <\/script> so it does
        # not prematurely close the payload container.
        assert "<\\/script>" in html

    def test_kanban_has_7_status_columns(self, plan_root):
        plan_dashboard.PLAN_ROOT = plan_root
        plan_dashboard._project_root = str(plan_root.parent)
        plan_dashboard.rebuild_tree()
        env = plan_dashboard._get_jinja_env()
        template = env.get_template("kanban.html")
        all_tasks = _task_io.collect_all_tasks(plan_dashboard._root_task)
        html = template.render(all_tasks=all_tasks)
        assert html.count("kanban-col-header") == 7

    def test_dag_has_dependency_arrows(self, plan_root):
        plan_dashboard.PLAN_ROOT = plan_root
        plan_dashboard._project_root = str(plan_root.parent)
        plan_dashboard.rebuild_tree()
        env = plan_dashboard._get_jinja_env()
        template = env.get_template("dag.html")
        all_tasks = _task_io.collect_all_tasks(plan_dashboard._root_task)
        html = template.render(
            root_task=plan_dashboard._root_task, all_tasks=all_tasks
        )
        assert "graph LR" in html
        # 02-second depends on 01-first
        assert "-->" in html


# ---------------------------------------------------------------------------
# TestCLI
# ---------------------------------------------------------------------------


class TestCLI:
    def test_list_subcommand_output(self, plan_root):
        """CLI list shows comments for a task."""
        import task_comment

        # Add a comment first
        task_dir = plan_root / "01-first"
        add_comment(task_dir, "Objective", 0, "Complete step 1.", "A comment.", author="tester")

        captured = StringIO()
        with patch("sys.stdout", captured):
            task_comment.main([
                "--plan-root", str(plan_root),
                "list", "01-first",
            ])
        output = captured.getvalue()
        assert "#1" in output
        assert "A comment." in output

    def test_list_no_comments(self, plan_root):
        """CLI list prints 'No comments.' when there are none."""
        import task_comment

        captured = StringIO()
        with patch("sys.stdout", captured):
            task_comment.main([
                "--plan-root", str(plan_root),
                "list", "02-second",
            ])
        assert "No comments." in captured.getvalue()

    def test_resolve_subcommand(self, plan_root):
        """CLI resolve toggles and prints confirmation."""
        import task_comment

        task_dir = plan_root / "01-first"
        c = add_comment(task_dir, "Objective", 0, "p", "body", author="u")

        captured = StringIO()
        with patch("sys.stdout", captured):
            task_comment.main([
                "--plan-root", str(plan_root),
                "resolve", "01-first", str(c.id),
            ])
        assert "Resolved" in captured.getvalue()

    def test_list_tree_subcommand(self, plan_root):
        """CLI list-tree shows unresolved comment counts."""
        import task_comment

        task_dir = plan_root / "01-first"
        add_comment(task_dir, "Objective", 0, "p", "body", author="u")

        captured = StringIO()
        with patch("sys.stdout", captured):
            task_comment.main([
                "--plan-root", str(plan_root),
                "list-tree",
            ])
        output = captured.getvalue()
        assert "01-first" in output
        assert "1 unresolved" in output

    def test_list_tree_empty(self, plan_root):
        """CLI list-tree prints message when no unresolved comments."""
        import task_comment

        captured = StringIO()
        with patch("sys.stdout", captured):
            task_comment.main([
                "--plan-root", str(plan_root),
                "list-tree",
            ])
        assert "No unresolved comments" in captured.getvalue()


# ---------------------------------------------------------------------------
# Children-panel data contract (GET /dag?root=<path>)
#
# base.html's children panel parses the GET /dag?root=<path> fragment client
# side: the direct-child set from `.dag-controls[data-node-paths]`, each child's
# status from `style <id> fill:#<color>` lines, and the inter-child dependency
# edges from `<dep_id> --> <child_id>` lines (prerequisite --> dependent).  These
# tests pin the server-side half of that contract so the cards keep parsing.
# ---------------------------------------------------------------------------

BASE_HTML = (SCRIPTS_DIR / "templates" / "base.html").read_text(encoding="utf-8")

# node_id -> status fill color, mirrored from base.html's DAG_FILL_STATUS map.
_FILL_STATUS = {
    "#e0e0e0": "not-started", "#bbdefb": "in-progress", "#fff9c4": "implemented",
    "#ffcdd2": "revise", "#c8e6c9": "approved", "#f5f5f5": "archived",
}


def _parse_dag_fragment(html):
    """Parse a /dag?root= fragment the way base.html's parseChildrenDag does:
    return (node_paths, status_by_path, edges) where edges is the set of
    (dep_path, child_path) pairs in prerequisite -> dependent direction."""
    m = re.search(r"data-node-paths='(\{.*?\})'", html)
    node_paths = json.loads(m.group(1)) if m else {}
    fills = dict(re.findall(r"style\s+(\S+)\s+fill:(#[0-9a-fA-F]{3,6})", html))
    status_by_path = {
        node_paths[nid]: _FILL_STATUS.get(color.lower(), "")
        for nid, color in fills.items() if nid in node_paths
    }
    edges = set()
    for dep_id, child_id in re.findall(r"^\s*(\S+)\s*-->\s*(\S+)\s*$", html, re.M):
        if dep_id in node_paths and child_id in node_paths:
            edges.add((node_paths[dep_id], node_paths[child_id]))
    return node_paths, status_by_path, edges


class TestChildrenDagContract:
    def test_branching_parent_node_paths_are_direct_children_only(self, flow_client):
        resp = flow_client.get("/dag?root=00-flow")
        assert resp.status_code == 200
        node_paths, _, _ = _parse_dag_fragment(resp.text)
        assert set(node_paths.values()) == {
            "00-flow/a", "00-flow/b", "00-flow/c", "00-flow/d",
        }

    def test_branching_parent_per_child_status_fills(self, flow_client):
        resp = flow_client.get("/dag?root=00-flow")
        _, status_by_path, _ = _parse_dag_fragment(resp.text)
        assert status_by_path == {
            "00-flow/a": "approved",
            "00-flow/b": "in-progress",
            "00-flow/c": "not-started",
            "00-flow/d": "not-started",
        }

    def test_branching_parent_edges_direction(self, flow_client):
        """Edges run prerequisite -> dependent: a->b, a->c, b->d."""
        resp = flow_client.get("/dag?root=00-flow")
        _, _, edges = _parse_dag_fragment(resp.text)
        assert edges == {
            ("00-flow/a", "00-flow/b"),
            ("00-flow/a", "00-flow/c"),
            ("00-flow/b", "00-flow/d"),
        }

    def test_no_dependency_parent_has_no_edges(self, flow_client):
        resp = flow_client.get("/dag?root=01-flat")
        node_paths, _, edges = _parse_dag_fragment(resp.text)
        assert set(node_paths.values()) == {"01-flat/x", "01-flat/y"}
        assert edges == set()
        assert "-->" not in resp.text

    def test_leaf_parent_has_empty_child_set(self, flow_client):
        """A leaf (no children) yields an empty node-path map and no edges."""
        resp = flow_client.get("/dag?root=00-flow/a")
        node_paths, _, edges = _parse_dag_fragment(resp.text)
        assert node_paths == {}
        assert edges == set()


# ---------------------------------------------------------------------------
# Mermaid-removal regression
#
# The children panel was reworked from a clickable mermaid DAG to flat/layered
# `.child-card`s; mermaid and its click-wiring were removed.  One descriptive
# `mermaid` token survives in a comment and the `.mermaid` div is the line-based
# parser source, so we assert the *live* references are gone, not the bare word.
# ---------------------------------------------------------------------------


class TestMermaidRemoval:
    def test_no_mermaid_cdn_script(self):
        assert not re.search(r"<script[^>]+src=[^>]*mermaid", BASE_HTML, re.I)

    def test_no_mermaid_runtime_calls(self):
        assert "mermaid.initialize" not in BASE_HTML
        assert "mermaid.run" not in BASE_HTML

    def test_no_wire_dag_node_clicks(self):
        assert "wireDagNodeClicks" not in BASE_HTML

    def test_served_page_has_no_mermaid_runtime(self, client):
        text = client.get("/").text
        assert not re.search(r"<script[^>]+src=[^>]*mermaid", text, re.I)
        assert "mermaid.initialize" not in text
        assert "mermaid.run" not in text
        assert "wireDagNodeClicks" not in text


# ---------------------------------------------------------------------------
# Touch-aware sidebar + iPad breakpoints (cheap template-level regression)
#
# The behavioral gate is the Playwright touch drive (see the task file); these
# assert the rendered template still carries the touch primitives so a future
# edit that drops one fails here cheaply, without a browser.
# ---------------------------------------------------------------------------


class TestTouchSidebar:
    def test_viewport_fit_cover(self):
        """viewport-fit=cover is required for env(safe-area-inset-*) to resolve
        to non-zero values inside the notch/home-indicator region on iOS."""
        m = re.search(r'<meta name="viewport" content="([^"]*)"', BASE_HTML)
        assert m and "viewport-fit=cover" in m.group(1)

    def test_capability_detection_media_queries(self):
        """Mode is chosen by input capability, not raw width: the coarse-pointer
        / no-hover query and the portrait query must both be present."""
        assert "(hover: none), (pointer: coarse)" in BASE_HTML
        assert "(orientation: portrait)" in BASE_HTML
        assert "function sbIsTouch" in BASE_HTML
        assert "function sbIsPortrait" in BASE_HTML

    def test_touch_never_enters_hover_reveal(self):
        """On touch the unpinned hover-reveal state is unreachable by tap, so
        applySidebarMode must hard-set unpinned=false on the touch path."""
        assert "unpinned = false;" in BASE_HTML

    def test_mouse_only_chrome_disabled_on_touch(self):
        """The hover-rail and the drag-resizer are fine-pointer affordances;
        both are hidden under the .sb-touch guard."""
        assert ".sb-touch .sidebar-rail { display: none; }" in BASE_HTML
        assert ".sb-touch .sidebar-resizer { display: none; }" in BASE_HTML

    def test_hamburger_shown_in_drawer_mode_above_breakpoint(self):
        """A touch landscape iPad collapsed to the drawer sits above the 860px
        width media query, so the hamburger is driven by the body drawer-mode
        class (the hamburger is outside the workspace, so a descendant selector
        on .sb-drawer cannot reach it)."""
        assert "body.sb-drawer-mode .nav-hamburger { display: inline-flex; }" in BASE_HTML
        assert "sb-drawer-mode" in BASE_HTML

    def test_safe_area_insets_present(self):
        """The fixed header and the off-canvas drawer pad past the notch / home
        indicator with env(safe-area-inset-*)."""
        assert "env(safe-area-inset-top)" in BASE_HTML
        assert "env(safe-area-inset-left)" in BASE_HTML
        assert "env(safe-area-inset-right)" in BASE_HTML
        assert "env(safe-area-inset-bottom)" in BASE_HTML

    def test_served_page_carries_touch_primitives(self, client):
        """The same primitives survive the live render (server path), not just
        the raw template."""
        text = client.get("/").text
        assert "viewport-fit=cover" in text
        assert "(hover: none), (pointer: coarse)" in text
        assert "env(safe-area-inset-top)" in text
        assert "body.sb-drawer-mode .nav-hamburger" in text


class TestTouchPolish:
    """Cheap template-level regression assertions for the 02-touch-polish layer
    (tap targets, phone search sheet, content safe-areas, scroll ergonomics).
    The behavioral gate is the Playwright drive; these guard against accidental
    deletion of the load-bearing primitives."""

    def test_tap_targets_gated_behind_coarse_pointer(self):
        """Tap-target enlargement must be gated behind (pointer: coarse) so the
        desktop mouse density is untouched."""
        assert "@media (pointer: coarse)" in BASE_HTML
        # The enlargement floor (>=44px) lives inside the coarse-pointer block.
        coarse = BASE_HTML.split("@media (pointer: coarse)", 1)[1]
        assert "min-height: 44px" in coarse
        assert "width: 44px; height: 44px;" in coarse  # pin-toggle ::before slop

    def test_caret_coarse_rule_outweighs_base_rule(self):
        """The coarse `.task-toggle` hit-area override must out-specify the later
        unconditional `.task-toggle { width:16px; height:16px }` base rule, or
        source order shadows it and the caret stays 16x16 on touch.  The fix uses
        the child selector `.task-row > .task-toggle` (specificity 0,0,2,0) which
        wins regardless of source order.  (The behavioral gate is the rendered
        assertion in TestTouchPolishRendered; this cheap check catches a
        regression even where a browser is unavailable.)"""
        coarse = BASE_HTML.split("@media (pointer: coarse)", 1)[1].split("}\n}", 1)[0]
        # The coarse caret override must use the higher-specificity child selector,
        # not a bare `.task-toggle` (which would tie the base rule and lose).
        assert ".task-row > .task-toggle {" in coarse
        # And it must set the square 44x44 box (rotation-safe: an expanded caret
        # rotates the whole hit box, so a 28x44 box would become 44x28 = 28px tall).
        m = re.search(r"\.task-row > \.task-toggle \{[^}]*?"
                      r"width:\s*44px;\s*height:\s*44px;", coarse, re.S)
        assert m, "coarse `.task-row > .task-toggle` must set width:44px; height:44px"

    def test_search_trigger_not_forced_visible_on_all_coarse(self):
        """The phone-only search trigger must NOT be forced `display:inline-flex`
        for all coarse-pointer devices (that leaks the redundant icon onto iPad
        next to the still-inline search box).  Its display stays owned by the
        (max-width: 620px) phone block; its coarse hit-slop sizing is scoped to
        phone width AND coarse pointer."""
        # The icon-slop group that forces display must not include the trigger.
        m = re.search(r"\.nav-hamburger,\s*\.theme-toggle\s*\{[^}]*display:\s*inline-flex",
                      BASE_HTML, re.S)
        assert m, "hamburger/theme display group should exist without the trigger"
        assert ".nav-hamburger, .theme-toggle, .hc-search-trigger {" not in BASE_HTML
        # The trigger's coarse sizing is gated on phone width too.
        assert "@media (max-width: 620px) and (pointer: coarse)" in BASE_HTML

    def test_tap_highlight_suppressed_with_active_feedback(self):
        """The default gray tap flash is suppressed and replaced by a real
        :active affordance (so taps still give feedback)."""
        assert "-webkit-tap-highlight-color: transparent;" in BASE_HTML
        assert ".task-row:active" in BASE_HTML

    def test_phone_search_sheet_present(self):
        """The phone search/filter sheet, its trigger, and the JS that adopts the
        existing #search-box / #filter-status into it are all present."""
        assert 'id="search-sheet"' in BASE_HTML
        assert 'id="search-trigger"' in BASE_HTML
        assert 'id="search-sheet-backdrop"' in BASE_HTML
        assert "function toggleSearchSheet" in BASE_HTML
        assert "function openSearchSheet" in BASE_HTML
        assert "function closeSearchSheet" in BASE_HTML
        # The sheet adopts the live elements rather than duplicating inputs.
        assert 'id="search-host"' in BASE_HTML
        assert "body.appendChild(host)" in BASE_HTML

    def test_search_sheet_closed_by_navigation(self):
        """A navigation selection closes the sheet alongside the drawer."""
        assert "closeSearchSheet();" in BASE_HTML

    def test_content_safe_area_insets(self):
        """The detail panel and the bottom sheet pad past the home indicator /
        notch with env(safe-area-inset-*) (complements 01's chrome insets)."""
        assert "env(safe-area-inset-bottom)" in BASE_HTML
        assert "env(safe-area-inset-right)" in BASE_HTML

    def test_scroll_ergonomics(self):
        """overscroll containment on the scroll regions, plus a horizontal-scroll
        affordance (mask edge-fade + kanban scroll-snap) under coarse pointer."""
        assert "overscroll-behavior: contain;" in BASE_HTML
        assert "overscroll-behavior-x: contain;" in BASE_HTML
        coarse = BASE_HTML.split("@media (pointer: coarse)", 1)[1]
        assert "mask-image: linear-gradient(to right" in coarse
        assert "scroll-snap-type: x proximity;" in coarse

    def test_served_page_carries_polish_primitives(self, client):
        """The polish primitives survive the live render (server path)."""
        text = client.get("/").text
        assert "@media (pointer: coarse)" in text
        assert 'id="search-sheet"' in text
        assert "function toggleSearchSheet" in text
        assert "-webkit-tap-highlight-color: transparent;" in text


def _have_chromium() -> bool:
    """True only if Playwright AND a launchable Chromium are both available, so
    the rendered touch tests are skipped (not errored) on a bare CI box."""
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        return False
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            b.close()
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _have_chromium(), reason="playwright+chromium unavailable")
class TestTouchPolishRendered:
    """Rendered-behavior regressions for the two control surfaces the
    string-level tests can't fully pin: the coarse-pointer caret hit box must
    actually measure >=44px tall (not be shadowed by the later base rule), and
    the phone-only search trigger must not render on iPad alongside the inline
    search.  Drives the real server in a thread with Playwright touch contexts;
    skipped where a browser is unavailable."""

    def _serve(self, plan_root):
        import threading
        plan_dashboard.PLAN_ROOT = plan_root
        plan_dashboard._project_root = str(plan_root.resolve().parent)
        plan_dashboard._jinja_env = None
        plan_dashboard.rebuild_tree()
        # Pick a free port the same way the lifespan tests do.
        import socket
        s = socket.socket()
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
        s.close()
        t = threading.Thread(target=plan_dashboard.serve, args=(port,), daemon=True)
        t.start()
        assert plan_dashboard._wait_for_bind(port, timeout=5.0), "server did not bind"
        return port, t

    def _stop(self, t):
        if plan_dashboard._server is not None:
            plan_dashboard._server.should_exit = True
        t.join(timeout=5.0)

    def test_caret_hit_box_is_44_tall_on_touch(self, plan_root):
        """On a coarse/touch render the non-leaf `.task-toggle` caret must measure
        >=44px tall — the regression that caught the shadowed coarse rule (the
        caret was stuck at 16x16 because the later base rule won on source
        order)."""
        from playwright.sync_api import sync_playwright
        port, t = self._serve(plan_root)
        try:
            with sync_playwright() as p:
                b = p.chromium.launch()
                # iPad landscape: coarse pointer, pinned sidebar, tree visible.
                ctx = b.new_context(viewport={"width": 1024, "height": 768},
                                    device_scale_factor=2, is_mobile=True, has_touch=True)
                pg = ctx.new_page()
                pg.goto(f"http://127.0.0.1:{port}/", wait_until="domcontentloaded")
                pg.wait_for_selector(".task-row > .task-toggle:not(.leaf)", timeout=5000)
                box = pg.evaluate(
                    """() => {
                        const el = document.querySelector('.task-row > .task-toggle:not(.leaf)');
                        if (!el) return null;
                        const r = el.getBoundingClientRect();
                        return {w: r.width, h: r.height};
                    }""")
                b.close()
            assert box is not None, "no non-leaf caret found in the rendered tree"
            assert box["h"] >= 44 - 0.5, f"caret height {box['h']:.1f}px < 44 (rule shadowed)"
            assert box["w"] >= 28 - 0.5, f"caret width {box['w']:.1f}px < 28"
        finally:
            self._stop(t)

    def test_only_one_search_affordance_on_ipad(self, plan_root):
        """On every iPad size exactly ONE search affordance is visible: the
        inline search box, NOT the phone-only trigger.  iPhone is the inverse
        (trigger only).  Catches the trigger leaking onto coarse iPad."""
        from playwright.sync_api import sync_playwright
        port, t = self._serve(plan_root)
        try:
            with sync_playwright() as p:
                b = p.chromium.launch()
                # iPad sizes — inline search shown, trigger hidden.
                for w, h in [(768, 1024), (1024, 768), (1366, 1024)]:
                    ctx = b.new_context(viewport={"width": w, "height": h},
                                        device_scale_factor=2, is_mobile=True, has_touch=True)
                    pg = ctx.new_page()
                    pg.goto(f"http://127.0.0.1:{port}/", wait_until="domcontentloaded")
                    pg.wait_for_timeout(300)
                    trig = pg.locator("#search-trigger").is_visible()
                    inline = pg.locator("#search-box").is_visible()
                    ctx.close()
                    assert not trig, f"trigger visible on iPad {w}x{h} (should be inline only)"
                    assert inline, f"inline search hidden on iPad {w}x{h}"
                # iPhone — trigger shown, inline search hidden.
                ctx = b.new_context(viewport={"width": 390, "height": 844},
                                    device_scale_factor=3, is_mobile=True, has_touch=True)
                pg = ctx.new_page()
                pg.goto(f"http://127.0.0.1:{port}/", wait_until="domcontentloaded")
                pg.wait_for_timeout(300)
                trig = pg.locator("#search-trigger").is_visible()
                inline = pg.locator("#search-box").is_visible()
                ctx.close()
                b.close()
            assert trig, "trigger hidden on iPhone (should be shown)"
            assert not inline, "inline search visible on iPhone (should be in sheet/hidden)"
        finally:
            self._stop(t)


# ---------------------------------------------------------------------------
# Children-panel client logic (node-backed)
#
# The flat-grid-vs-layered-flow decision and the topological tiering live only
# in base.html's JS.  These tests extract the pure builder functions and run
# them under node so the genuinely new client logic is exercised, not just the
# server contract above.  Skipped when node is unavailable.
# ---------------------------------------------------------------------------

_NODE = shutil.which("node")


def _extract_js_defs(names):
    """Slice the named top-level `function NAME`/`var NAME` definitions out of
    base.html's inline script.  Every top-level construct (function/var/comment/
    event-listener) starts at column 0, so each def spans from its own header
    line up to the next top-level construct — this captures balanced braces and
    multi-line `var` continuations without a JS parser."""
    # Column-0 boundaries that open a new top-level construct.
    boundaries = list(re.finditer(
        r"^(?:async function|function|var|window\.|/\*|//)", BASE_HTML, re.M,
    ))
    offsets = [b.start() for b in boundaries] + [len(BASE_HTML)]
    wanted = {}
    order = []
    for i, b in enumerate(boundaries):
        m = re.match(r"(?:async function|function|var)\s+([A-Za-z_$][\w$]*)",
                     BASE_HTML[b.start():])
        if not m:
            continue
        name = m.group(1)
        if name in names:
            wanted[name] = BASE_HTML[b.start():offsets[i + 1]].rstrip()
            order.append(name)
    missing = set(names) - set(wanted)
    assert not missing, f"definitions not found in base.html: {missing}"
    # Preserve source order so functions referencing earlier ones resolve.
    return "\n".join(wanted[n] for n in order)


def _run_node(harness_body):
    """Run extracted client builders + a harness body under node; the body
    prints a JSON line we parse back.  Returns the decoded object."""
    defs = _extract_js_defs([
        "DAG_FILL_STATUS", "childrenSig", "childCardHTML", "SUBTASK_HEADER",
        "buildChildGrid", "buildChildFlow", "escapeHtml", "escapeAttr",
    ])
    script = defs + "\n" + harness_body
    proc = subprocess.run(
        [_NODE, "-e", script],
        capture_output=True, text=True, timeout=20,
    )
    assert proc.returncode == 0, f"node failed:\n{proc.stderr}"
    return json.loads(proc.stdout.strip().splitlines()[-1])


@pytest.mark.skipif(_NODE is None, reason="node not available")
class TestChildFlowClientLogic:
    def test_extracted_builders_run_under_node(self):
        """Smoke test: the extracted functions evaluate and a flat grid builds."""
        out = _run_node(
            "var kids=[{path:'p/a',slug:'a',title:'A',status:'approved'}];"
            "var html=buildChildGrid(kids);"
            "console.log(JSON.stringify({"
            "  hasCard: html.indexOf('child-card')>=0,"
            "  hasGrid: html.indexOf('child-grid')>=0,"
            "  hasFlow: html.indexOf('child-flow')>=0}));"
        )
        assert out["hasCard"] and out["hasGrid"] and not out["hasFlow"]

    def test_topological_tier_order(self):
        """buildChildFlow groups children into execution tiers: a (tier 0),
        then b & c (depend on a), then d (depends on b)."""
        out = _run_node(
            "var kids=["
            "  {path:'a',slug:'a',title:'A',status:'approved'},"
            "  {path:'b',slug:'b',title:'B',status:'in-progress'},"
            "  {path:'c',slug:'c',title:'C',status:'not-started'},"
            "  {path:'d',slug:'d',title:'D',status:'not-started'}];"
            "var edges={b:['a'],c:['a'],d:['b']};"
            "var html=buildChildFlow(kids, edges);"
            "var tiers=html.split('flow-tier').slice(1).map(function(seg){"
            "  var m=seg.match(/data-path=\"([a-d])\"/g)||[];"
            "  return m.map(function(s){return s.match(/\"([a-d])\"/)[1];});});"
            "console.log(JSON.stringify({tiers: tiers}));"
        )
        assert out["tiers"] == [["a"], ["b", "c"], ["d"]]

    def test_cycle_is_safe_and_terminates(self):
        """A cyclic edge set must still terminate and place every child; the
        unresolvable nodes are flushed into the final tier."""
        out = _run_node(
            "var kids=["
            "  {path:'a',slug:'a',title:'A',status:'not-started'},"
            "  {path:'b',slug:'b',title:'B',status:'not-started'},"
            "  {path:'c',slug:'c',title:'C',status:'not-started'}];"
            "var edges={a:['b'],b:['a'],c:[]};"  # a<->b cycle, c independent
            "var html=buildChildFlow(kids, edges);"
            "var tiers=html.split('flow-tier').slice(1).map(function(seg){"
            "  var m=seg.match(/data-path=\"([a-c])\"/g)||[];"
            "  return m.map(function(s){return s.match(/\"([a-c])\"/)[1];});});"
            "var all=[].concat.apply([],tiers).sort().join('');"
            "console.log(JSON.stringify({all: all, lastTier: tiers[tiers.length-1].sort()}));"
        )
        # Every child placed exactly once; the cyclic pair lands in the last tier.
        assert out["all"] == "abc"
        assert set(out["lastTier"]) == {"a", "b"}

    def test_after_footer_names_direct_deps_only(self):
        """A dependent card's `after:` footer lists only its direct sibling
        deps (d depends on b, not transitively on a)."""
        out = _run_node(
            "var kids=["
            "  {path:'a',slug:'a',title:'A',status:'approved'},"
            "  {path:'b',slug:'b',title:'B',status:'approved'},"
            "  {path:'d',slug:'d',title:'D',status:'not-started'}];"
            "var edges={b:['a'],d:['b']};"
            "var html=buildChildFlow(kids, edges);"
            # Isolate d's card markup, then read its dep-slug footer entries.
            "var dCard=html.split('data-path=\"d\"')[1].split('</button>')[0];"
            "var deps=(dCard.match(/dep-slug\">([a-d])</g)||[])"
            "  .map(function(s){return s.match(/>([a-d])</)[1];});"
            "console.log(JSON.stringify({deps: deps}));"
        )
        assert out["deps"] == ["b"]

    def test_children_sig_busts_on_status_change(self):
        out = _run_node(
            "var k1=[{path:'a',status:'not-started'},{path:'b',status:'approved'}];"
            "var k2=[{path:'a',status:'in-progress'},{path:'b',status:'approved'}];"
            "var e={};"
            "console.log(JSON.stringify({"
            "  same: childrenSig(k1,e)===childrenSig(k1,e),"
            "  busted: childrenSig(k1,e)!==childrenSig(k2,e)}));"
        )
        assert out["same"] and out["busted"]

    def test_children_sig_busts_on_dependency_change(self):
        out = _run_node(
            "var kids=[{path:'a',status:'approved'},{path:'b',status:'not-started'}];"
            "var e1={b:['a']};"
            "var e2={};"
            "console.log(JSON.stringify({"
            "  busted: childrenSig(kids,e1)!==childrenSig(kids,e2)}));"
        )
        assert out["busted"]


# ---------------------------------------------------------------------------
# renderMarkdown image-rewrite (node-backed, behavioral)
#
# The server-mode `<img src>` rewrite is a code path inside renderMarkdown that
# string-presence assertions cannot exercise — an undefined identifier there
# (the deleted `pathPrefix`) sails through a green string suite but throws a
# ReferenceError at runtime, aborting the expand handler.  This harness extracts
# the real renderMarkdown source out of base.html and runs it under node against
# a minimal DOM/markdown shim, so the image branch actually executes and its
# rewritten `src` is asserted.  Passing sectionName=null skips the block-wrap
# loop (and its richer DOM needs); a body with only a relative image exercises
# the `/files/` branch and nothing else.  Skipped when node is unavailable.
# ---------------------------------------------------------------------------

_RENDER_MD_SHIM = r"""
// Minimal markdown-it stub: emit the one relative-image we feed in as HTML.
var md = { render: function (text) {
  var m = text.match(/!\[[^\]]*\]\(([^)]+)\)/);
  return m ? '<img src="' + m[1] + '">' : '<p>' + text + '</p>';
} };
// Minimal DOM: a div whose innerHTML setter parses <img src> / <a href> into
// element stubs, and whose querySelectorAll returns them for the rewrite loop.
function makeEl(tag) {
  return {
    tagName: tag.toUpperCase(), _attrs: {}, _imgs: [], _as: [],
    set innerHTML(html) {
      var self = this; this._imgs = []; this._as = [];
      var im; var ire = /<img[^>]*\bsrc="([^"]*)"[^>]*>/g;
      while ((im = ire.exec(html))) {
        (function (val) {
          self._imgs.push({
            _src: val,
            getAttribute: function (n) { return n === 'src' ? this._src : null; },
            setAttribute: function (n, v) { if (n === 'src') this._src = v; },
          });
        })(im[1]);
      }
      this._html = html;
    },
    get innerHTML() {
      var out = '';
      for (var i = 0; i < this._imgs.length; i++) {
        out += '<img src="' + this._imgs[i]._src + '">';
      }
      return out;
    },
    querySelectorAll: function (sel) {
      if (sel === 'img[src]') return this._imgs;
      if (sel === 'a[href]') return this._as;
      return [];
    },
  };
}
var document = { createElement: function (t) { return makeEl(t); } };
var window = { STANDALONE: false };
function resolveInternalTaskPath() { return null; }
function repoFileHref(p) { return p; }
// renderMarkdown sanitizes md.render output through DOMPurify before DOM
// insertion. These link/image-rewrite tests run before sanitization matters,
// so a pass-through stub keeps the rewrite branch exercising real logic. The
// hostile-input behavior of the real DOMPurify is proven in the browser drive
// recorded in the task Results.
var DOMPurify = { sanitize: function (html) { return html; } };
"""


@pytest.mark.skipif(_NODE is None, reason="node not available")
class TestRenderMarkdownImageRewrite:
    def _run(self, root_prefix, task_path, src, repo_file_base=""):
        defs = _extract_js_defs(["renderMarkdown"])
        harness = (
            _RENDER_MD_SHIM
            + "var RESOLVED_ROOT = '/abs/root';\n"
            + "var ROOT_PREFIX = " + json.dumps(root_prefix) + ";\n"
            + "var REPO_ROOT_PREFIX = ROOT_PREFIX;\n"
            + "var REPO_FILE_BASE = " + json.dumps(repo_file_base) + ";\n"
            + "var DOC_LOCAL_LINKS = [];\n"
            + defs + "\n"
            + "var body = '![fig](" + src + ")';\n"
            + "var html = renderMarkdown(body, null, " + json.dumps(task_path) + ");\n"
            + "var m = html.match(/<img src=\"([^\"]*)\">/);\n"
            + "console.log(JSON.stringify({src: m ? m[1] : null}));\n"
        )
        proc = subprocess.run(
            [_NODE, "-e", harness], capture_output=True, text=True, timeout=20
        )
        # A ReferenceError (the shipped `pathPrefix` bug) surfaces here as a
        # nonzero exit with the error on stderr — exactly the failure mode a
        # string-presence test cannot see.
        assert proc.returncode == 0, f"node failed (ReferenceError?):\n{proc.stderr}"
        return json.loads(proc.stdout.strip().splitlines()[-1])

    def test_server_image_src_uses_root_prefix_and_task_path(self):
        """Server mode rewrites a relative image to
        /files/<ROOT_PREFIX>/<taskPath>/<src> — the resolved-root basis, so the
        /files/ route (which resolves under project_root = resolved-root parent)
        finds the file."""
        out = self._run("superRA", "01-alpha/01-model", "attachments/fig.png")
        assert out["src"] == "/files/superRA/01-alpha/01-model/attachments/fig.png"

    def test_server_image_src_for_nondefault_root(self):
        """A non-`superRA` resolved root carries its own basename into the
        /files/ path — no hardcoded `superRA/` segment."""
        out = self._run("tasks", "01-alpha", "fig.png")
        assert out["src"] == "/files/tasks/01-alpha/fig.png"

    def test_server_image_src_for_root_body(self):
        """The root body (empty taskPath) drops the task-dir segment but keeps the
        root prefix: /files/<ROOT_PREFIX>/<src>."""
        out = self._run("superRA", "", "fig.png")
        assert out["src"] == "/files/superRA/fig.png"


# ---------------------------------------------------------------------------
# Sidebar state preservation: the active page stays expanded to its children,
# and manually-opened branches survive a structural full-reload instead of
# folding back to the root. Wiring-level regression checks (the functions are
# DOM-bound, so we assert their presence + the call sites that drive them, in
# the style of TestTouchSidebar above).
# ---------------------------------------------------------------------------
class TestSidebarStatePreservation:
    def test_capture_restore_helpers_present(self):
        """The snapshot/restore pair the full-reload path relies on must exist."""
        assert "function getExpandedNavPaths()" in BASE_HTML
        assert "async function restoreExpandedNavPaths(paths)" in BASE_HTML

    def test_restore_is_shallow_to_deep(self):
        """Restoring must expand parents before descendants so each lazy branch
        is in the DOM by the time its children are re-opened — i.e. sort by
        path depth before walking."""
        m = re.search(
            r"async function restoreExpandedNavPaths\(paths\)\s*\{.*?\n\}",
            BASE_HTML, re.S,
        )
        assert m, "restoreExpandedNavPaths not found"
        body = m.group(0)
        assert ".sort(" in body and "split('/').length" in body

    def test_full_reload_captures_before_rebuild_and_restores_after(self):
        """onFullReload must snapshot the open branches before loadNavTree wipes
        them, then restore them — otherwise the tree folds to the root."""
        m = re.search(r"async function onFullReload\(\)\s*\{.*?\n\}", BASE_HTML, re.S)
        assert m, "onFullReload not found"
        body = m.group(0)
        cap = body.index("getExpandedNavPaths()")
        reload_ = body.index("await loadNavTree()")
        restore = body.index("restoreExpandedNavPaths(expanded)")
        assert cap < reload_ < restore

    def test_active_page_expands_to_its_children(self):
        """updateSidebar must open the current page's own caret (expandNavNode on
        the target), not just its ancestor chain."""
        m = re.search(r"async function updateSidebar\(path\)\s*\{.*?\n\}", BASE_HTML, re.S)
        assert m, "updateSidebar not found"
        body = m.group(0)
        assert "await expandNavNode(target)" in body

    def test_expands_root_container_before_segment_walk(self):
        """On a fresh deep-link load the root/umbrella container (path "") holds
        every top-level task but is named by no path segment, so the segment walk
        skips it and a top-level or deep target stays hidden in a collapsed root.
        updateSidebar must expand navNodeId('') BEFORE the ancestor segment loop."""
        m = re.search(r"async function updateSidebar\(path\)\s*\{.*?\n\}", BASE_HTML, re.S)
        assert m, "updateSidebar not found"
        body = m.group(0)
        assert "document.getElementById(navNodeId(''))" in body
        root_expand = body.index("expandNavNode(rootNode)")
        seg_loop = body.index("for (var i = 0; i < segs.length - 1; i++)")
        assert root_expand < seg_loop, "root must be expanded before the segment walk"


class TestWorktreeSelectorLiveRefresh:
    def test_refresh_on_open_wiring_present(self):
        """Opening the dropdown re-fetches the worktree list so a worktree added
        since page load appears without a manual page refresh."""
        assert "function initWorktreeSelectorRefresh()" in BASE_HTML
        assert "initWorktreeSelectorRefresh();" in BASE_HTML
        m = re.search(
            r"function initWorktreeSelectorRefresh\(\)\s*\{.*?\n\}", BASE_HTML, re.S
        )
        assert m
        body = m.group(0)
        assert "'mousedown'" in body and "'focus'" in body
        assert "fetchWorktrees()" in body

    def test_signature_guard_prevents_popup_flicker(self):
        """populateWorktreeSelector must short-circuit when the option set is
        unchanged, so a refresh-on-open does not rewrite options under the open
        native picker."""
        assert "_wtSignature" in BASE_HTML
        m = re.search(
            r"function populateWorktreeSelector\(data\)\s*\{.*?\n\}", BASE_HTML, re.S
        )
        assert m
        body = m.group(0)
        assert "signature === _wtSignature" in body


# ---------------------------------------------------------------------------
# TestFileLinkConsistency — every task-path -> file href derives from the
# resolved root's absolute path (not a hardcoded `superRA/` under PROJECT_ROOT),
# so links are correct for a non-default --root, a rootless forest, and a
# subtree export, while the conventional superRA/ layout stays unchanged.
# ---------------------------------------------------------------------------


def _injected_root_vars(html: str) -> dict[str, str]:
    """Pull the resolved-root JS vars the page bakes in for the file-link builders."""
    out = {}
    for name in ("RESOLVED_ROOT", "ROOT_PREFIX", "PROJECT_ROOT"):
        m = re.search(rf"var {name} = (.*?);", html)
        assert m, f"{name} not injected"
        out[name] = json.loads(m.group(1))
    return out


@pytest.fixture
def nondefault_root(tmp_path):
    """A task root NOT named `superRA`, nested one level under a project dir, with
    an umbrella task.md and a deep child.  Exercises the non-default --root case."""
    proj = tmp_path / "myproject"
    root = proj / "tasks"
    root.mkdir(parents=True)
    _write_task_md(root / "task.md", "Umbrella", "in-progress",
                   objective="See [code/main.py:5](code/main.py#L5).")
    deep = root / "01-alpha" / "01-model"
    deep.mkdir(parents=True)
    _write_task_md(deep / "task.md", "Deep", "not-started",
                   objective="Body link to [run.py:1](run.py#L1).")
    return root


@pytest.fixture
def forest_root(tmp_path):
    """A rootless forest: superRA/ with NO umbrella task.md, two top-level trees,
    one with a deep descendant.  Exercises the synthetic-container (path == "")
    render/route plus deep file-link resolution."""
    root = tmp_path / "superRA"
    (root / "01-alpha" / "01-model").mkdir(parents=True)
    _write_task_md(root / "01-alpha" / "task.md", "Alpha", "in-progress",
                   objective="Alpha root.")
    _write_task_md(root / "01-alpha" / "01-model" / "task.md", "Alpha Model",
                   "not-started", objective="See [x.py:1](x.py#L1).")
    (root / "02-beta").mkdir(parents=True)
    _write_task_md(root / "02-beta" / "task.md", "Beta", "not-started",
                   objective="Beta root.")
    assert not (root / "task.md").exists()  # truly rootless
    return root


def _client_for(plan_root):
    """Build a TestClient pointed at *plan_root* (any basename), launch worktree."""
    from starlette.testclient import TestClient

    plan_dashboard.PLAN_ROOT = plan_root
    plan_dashboard._project_root = str(plan_root.resolve().parent)
    plan_dashboard._jinja_env = None
    plan_dashboard._worktree_cache.clear()
    plan_dashboard.rebuild_tree()
    return TestClient(plan_dashboard.app, raise_server_exceptions=True)


class TestFileLinkConsistency:
    # --- Injected resolved-root template vars -----------------------------

    def test_index_injects_resolved_root_for_nondefault_root(self, nondefault_root):
        """The page bakes in the resolved root's absolute path and basename — the
        single base every file-link builder prepends instead of a literal
        `superRA/` under PROJECT_ROOT."""
        with _client_for(nondefault_root) as c:
            v = _injected_root_vars(c.get("/").text)
        assert v["RESOLVED_ROOT"] == str(nondefault_root.resolve())
        assert v["ROOT_PREFIX"] == "tasks"  # basename, NOT "superRA"
        # PROJECT_ROOT is the parent, so the OLD `PROJECT_ROOT + '/superRA/'`
        # reconstruction would have pointed at a nonexistent superRA/ dir.
        assert v["PROJECT_ROOT"] == str(nondefault_root.resolve().parent)
        assert not (Path(v["PROJECT_ROOT"]) / "superRA").exists()

    def test_nondefault_root_task_link_resolves_on_disk(self, nondefault_root):
        """taskFileVscodeHref(path) == RESOLVED_ROOT + '/' + path + '/task.md'
        must name a real file for a non-default root (the deep task.md)."""
        with _client_for(nondefault_root) as c:
            v = _injected_root_vars(c.get("/").text)
        built = Path(v["RESOLVED_ROOT"]) / "01-alpha/01-model" / "task.md"
        assert built.resolve() == (nondefault_root / "01-alpha/01-model/task.md").resolve()
        assert built.is_file()
        # In-body relative-link base: RESOLVED_ROOT + '/' + taskPath + '/' + href.
        body_target = Path(v["RESOLVED_ROOT"]) / "01-alpha/01-model" / "run.py"
        assert body_target.parent.is_dir()  # the dir the relative link resolves into

    def test_builders_use_resolved_root_not_hardcoded_superra(self):
        """The link builders prepend RESOLVED_ROOT/ROOT_PREFIX, not a literal
        `superRA/` under PROJECT_ROOT — guards the delink against regression."""
        # taskFileVscodeHref: local link off RESOLVED_ROOT, GitHub off ROOT_PREFIX.
        m = re.search(r"function taskFileVscodeHref\(path\)\s*\{.*?\n\}", BASE_HTML, re.S)
        assert m
        fn = m.group(0)
        # The `vscode://file/` scheme is composed once in vscodeFileUri; the local
        # branch prepends RESOLVED_ROOT via that shared helper.
        assert "vscodeFileUri(RESOLVED_ROOT + '/' + rel)" in fn
        assert "function vscodeFileUri(absPath)" in BASE_HTML
        assert "return 'vscode://file/' + absPath;" in BASE_HTML
        # GitHub branch uses the repo-root-relative prefix (so a nested tree keeps
        # its `docs/...` lead), not the bare basename or a hardcoded segment.
        assert "REPO_ROOT_PREFIX ? REPO_ROOT_PREFIX + '/' : ''" in fn
        assert "/superRA/" not in fn  # no hardcoded path segment
        # renderMarkdown in-body base also derives from RESOLVED_ROOT/ROOT_PREFIX.
        assert "vscode://file/' + RESOLVED_ROOT + '/' + filePath" in BASE_HTML
        assert "var repoPathPrefix = rootRel + taskDirRel;" in BASE_HTML
        # The old hardcoded prefixes are gone from the builders.
        assert "'superRA/' + path + '/task.md'" not in BASE_HTML
        assert "pathPrefix = taskPath ? 'superRA/'" not in BASE_HTML
        # Forward guard: the surviving server-mode image rewrite must use the
        # resolved-root basis (repoPathPrefix), not the deleted `pathPrefix`.
        # Without this, the def-deletion check above guards the regression
        # backwards and a dangling `pathPrefix` reference ships green
        # (TestRenderMarkdownImageRewrite executes it; this pins the source).
        assert "'/files/' + repoPathPrefix + src" in BASE_HTML
        assert "'/files/' + pathPrefix + src" not in BASE_HTML

    # --- Forest render / route / link -------------------------------------

    def test_forest_index_and_nav_render(self, forest_root):
        """A rootless forest renders (synthetic container, path == "") and the nav
        lists every independent top-level tree."""
        with _client_for(forest_root) as c:
            assert c.get("/").status_code == 200
            nav = c.get("/nav")
            assert nav.status_code == 200
            assert "01-alpha" in nav.text and "02-beta" in nav.text

    def test_forest_deep_node_routes_and_links_resolve(self, forest_root):
        """A deep forest task routes by its resolved-root-relative path and its
        task-file link resolves to a real on-disk file (the descended-path bug
        would have dropped the `01-alpha` segment)."""
        with _client_for(forest_root) as c:
            assert c.get("/node/01-alpha/01-model").status_code == 200
            v = _injected_root_vars(c.get("/").text)
        built = Path(v["RESOLVED_ROOT"]) / "01-alpha/01-model" / "task.md"
        assert built.resolve() == (forest_root / "01-alpha/01-model/task.md").resolve()
        assert built.is_file()

    def test_forest_synthetic_root_renders_and_routes(self, forest_root):
        """The synthetic container root (no umbrella task.md, path == "") renders
        as the empty-path root node and is reachable via /node/ so deep-linking /
        setActive('') back to the container works."""
        with _client_for(forest_root) as c:
            html = c.get("/").text
            # The empty-path root node is embedded (id falls back to `task-root`).
            assert 'id="task-root"' in html
            # The container's own /node/ (empty path) route resolves.
            assert c.get("/node/").status_code == 200
        # The breadcrumb builds a clickable root crumb that ascends via
        # setActive('') — the entry point that returns to the container. The
        # label is 'root' in tracker mode and the site title in doc-mode, so the
        # assertion pins the empty-path ascent, not the literal label.
        assert "addCrumb(rootLabel, '', segs.length === 0)" in BASE_HTML

    # --- Subtree export resolved-root basis -------------------------------

    def test_subtree_export_resolved_root_is_subtree_dir(self, plan_root):
        """A --root subtree export re-bases paths to the subtree, so RESOLVED_ROOT
        must be the subtree dir (not the full plan root) — else re-based links
        drop the subtree segment and point at missing files."""
        plan_dashboard._jinja_env = None
        # Give the subtree a child so a re-based deep path exists.
        sub = plan_root / "01-first" / "01-leaf"
        sub.mkdir()
        _write_task_md(sub / "task.md", "Leaf", "not-started", objective="x.")
        html = plan_dashboard.render_standalone_html(plan_root, root="01-first")
        v = _injected_root_vars(html)
        assert v["RESOLVED_ROOT"] == str((plan_root / "01-first").resolve())
        # Re-based "01-leaf/task.md" resolves under the subtree dir, on disk.
        built = Path(v["RESOLVED_ROOT"]) / "01-leaf" / "task.md"
        assert built.resolve() == (sub / "task.md").resolve()
        assert built.is_file()

    # --- Conventional layout unchanged ------------------------------------

    def test_conventional_superra_layout_unchanged(self, plan_root):
        """With an umbrella superRA/task.md, RESOLVED_ROOT is the superRA dir and
        ROOT_PREFIX is `superRA` — the conventional links keep resolving exactly
        as before the delink."""
        with _client_for(plan_root) as c:
            v = _injected_root_vars(c.get("/").text)
        assert v["RESOLVED_ROOT"] == str(plan_root.resolve())
        assert v["ROOT_PREFIX"] == "superRA"
        built = Path(v["RESOLVED_ROOT"]) / "01-first" / "task.md"
        assert built.is_file()

    # --- Server vscode_link filter ----------------------------------------

    def test_vscode_link_filter_joins_resolved_root(self, plan_root):
        """The server vscode_link filter joins whatever base it is handed with the
        path (no hardcoded `superRA/`): handed the resolved root, it yields a real
        file URI; the conventional and non-default roots behave identically."""
        plan_dashboard.PLAN_ROOT = plan_root
        plan_dashboard._jinja_env = None
        env = plan_dashboard._get_jinja_env()
        vscode_link = env.filters["vscode_link"]
        resolved = str(plan_root.resolve())
        result = vscode_link("01-first/task.md", resolved)
        assert result == f"vscode://file/{resolved}/01-first/task.md"
        # Non-default root: same join, no `superRA/` assumption baked into the filter.
        other = "/tmp/myproject/tasks"
        assert vscode_link("01-alpha/task.md", other) == (
            "vscode://file//tmp/myproject/tasks/01-alpha/task.md"
        )


# ---------------------------------------------------------------------------
# TestWorktreeRootFollowing — RESOLVED_ROOT / ROOT_PREFIX follow the active
# worktree (each worktree's root may sit at a different path / basename), like
# PROJECT_ROOT, so file links stay correct after a ?wt= switch.
# ---------------------------------------------------------------------------


class TestWorktreeRootFollowing:
    def test_worktrees_endpoint_exposes_plan_root(self, two_worktree_client):
        """/api/worktrees carries each plan-bearing worktree's absolute plan_root
        so the client can re-point RESOLVED_ROOT per ?wt= (file links follow the
        active tab).  The endpoint enumerates the real git worktrees; the contract
        under test is the per-entry plan_root field, not the seeded fixture ids."""
        client, _wt_a, _wt_b = two_worktree_client
        data = client.get("/api/worktrees").json()
        with_plan = [e for e in data["worktrees"] if e.get("has_plan")]
        assert with_plan, "expected at least one plan-bearing worktree"
        for e in with_plan:
            assert "plan_root" in e, "each plan-bearing entry carries plan_root"
            assert Path(e["plan_root"]).is_absolute()
            # plan_root is the resolved task root, distinct from the worktree path.
            assert e["plan_root"] != e["path"]

    def test_fetch_worktrees_repoints_resolved_root(self):
        """fetchWorktrees indexes plan_root per wt_id and re-points RESOLVED_ROOT /
        ROOT_PREFIX to the active worktree, guarded for standalone (empty list)."""
        m = re.search(r"function fetchWorktrees\(\)\s*\{.*?\n\}", BASE_HTML, re.S)
        assert m
        fn = m.group(0)
        assert "_wtResolvedRoots[wt.wt_id || ''] = wt.plan_root || '';" in fn
        assert "RESOLVED_ROOT = resolved;" in fn
        # ROOT_PREFIX is recomputed from the active worktree's resolved root.
        assert "ROOT_PREFIX = resolved.split('/')" in fn
        # Non-empty guard preserves the baked-in roots in standalone mode.
        assert "if (resolved) {" in fn


# ---------------------------------------------------------------------------
# TestWorktreeOpenButton — the header "open worktree in VS Code" deep-link
# button: opens the active worktree's checkout root (PROJECT_ROOT) as a folder
# via the shared vscode://file mechanism, shown for a single worktree too.
# ---------------------------------------------------------------------------


class TestWorktreeOpenButton:
    def test_button_rendered_in_live_page(self, plan_root):
        """A server-backed page renders the button (id + shared .vscode-btn class)
        as a sibling of the worktree selector, hidden until JS reveals it."""
        with _client_for(plan_root) as c:
            html = c.get("/").text
        m = re.search(r'<a class="vscode-btn" id="worktree-open-btn"[^>]*>', html)
        assert m, "worktree-open button not rendered"
        tag = m.group(0)
        assert 'target="_blank"' in tag
        assert "display:none" in tag  # hidden until updateWorktreeOpenHref runs

    def test_button_not_inside_selector_div(self):
        """The button lives OUTSIDE #worktree-selector so populateWorktreeSelector's
        `≤1 worktree → hide` never touches it: opening the worktree is useful with
        a single worktree too."""
        m = re.search(
            r'<div class="worktree-selector" id="worktree-selector">.*?</div>',
            BASE_HTML, re.S,
        )
        assert m
        assert "worktree-open-btn" not in m.group(0)
        # populateWorktreeSelector toggles only #worktree-selector, never the button.
        fn = re.search(r"function populateWorktreeSelector\(data\)\s*\{.*?\n\}",
                       BASE_HTML, re.S)
        assert fn and "worktree-open-btn" not in fn.group(0)

    def test_href_uses_project_root_via_shared_uri_builder(self):
        """updateWorktreeOpenHref points the button at PROJECT_ROOT (the whole
        worktree, not the superRA/ subdir) through the shared vscodeFileUri."""
        fn = re.search(r"function updateWorktreeOpenHref\(\)\s*\{.*?\n\}",
                       BASE_HTML, re.S)
        assert fn
        body = fn.group(0)
        assert "vscodeFileUri(PROJECT_ROOT)" in body
        assert "RESOLVED_ROOT" not in body  # the folder link uses PROJECT_ROOT
        # GitHub-file mode has no local folder to open → hide the button.
        assert "if (REPO_FILE_BASE) { btn.style.display = 'none'; return; }" in body

    def test_href_refreshed_on_worktree_change(self):
        """The href re-points on the same paths that re-point PROJECT_ROOT: inside
        fetchWorktrees (initial load + ?wt= switch via applyWorktree) and once at
        module init off the baked-in PROJECT_ROOT before the fetch resolves."""
        fw = re.search(r"function fetchWorktrees\(\)\s*\{.*?\n\}", BASE_HTML, re.S)
        assert fw and "updateWorktreeOpenHref();" in fw.group(0)
        # Init call sits alongside the module-eval fetchWorktrees() bootstrap.
        assert re.search(
            r"updateWorktreeOpenHref\(\);.*?\nfetchWorktrees\(\);", BASE_HTML, re.S
        )

    def test_doc_mode_hides_via_shared_rule(self):
        """Doc-mode hides the button through the existing shared .vscode-btn rule
        (the button carries that class), so no bespoke doc-mode CSS is needed."""
        assert "html[data-doc-mode] .vscode-btn," in BASE_HTML

    def test_standalone_omits_button(self, plan_root):
        """Standalone export omits the button (no local worktree to open from a
        file:// export) — it sits in the same not-standalone template block as the
        selector."""
        html = plan_dashboard.generate_dashboard(plan_root).read_text("utf-8")
        assert 'id="worktree-open-btn"' not in html


# ---------------------------------------------------------------------------
# Dashboard export, standalone, and artifact-workflow tests
# (moved from test_task_tree.py)
# ---------------------------------------------------------------------------

# --- Dashboard tests ---


class TestDashboard:
    """The static `generate` path renders base.html in standalone mode — one
    template, server-less, with all fragments embedded inline."""

    def test_generate_dashboard(self, plan_root):
        output = plan_root / "dashboard.html"
        ret = plan_dashboard.generate_dashboard(plan_root, output)
        assert ret == output
        assert output.exists()
        html = output.read_text(encoding="utf-8")
        # Rendered from base.html: real titles, not the old fallback string.
        assert "Test Project" in html
        assert "First Task" in html
        # base.html's full feature set (absent from the deleted DASHBOARD_HTML).
        assert "function renderMarkdown" in html
        assert "katex" in html

    def test_generate_defaults_output_into_plan_root(self, plan_root):
        ret = plan_dashboard.generate_dashboard(plan_root)
        assert ret == plan_root / "dashboard.html"
        assert ret.exists()

    def test_generate_is_standalone(self, plan_root):
        html = plan_dashboard.generate_dashboard(plan_root).read_text("utf-8")
        assert "window.STANDALONE = true" in html
        assert "STANDALONE_FRAGMENTS =" in html

    def test_generate_has_no_live_server_calls(self, plan_root):
        """The export must make zero network/SSE calls for task data."""
        html = plan_dashboard.generate_dashboard(plan_root).read_text("utf-8")
        assert "sse-connect=" not in html
        assert 'hx-ext="sse"' not in html
        assert "EventSource(" not in html
        assert "new WebSocket" not in html
        # No live server-only affordances rendered.
        assert 'id="worktree-selector"' not in html
        assert 'id="sse-full-reload"' not in html

    def test_generate_embeds_fragments_inline(self, plan_root):
        """Every fragment the standalone client fetches is pre-rendered inline."""
        second = plan_root / "02-second" / "task.md"
        second.write_text(
            second.read_text(encoding="utf-8")
            + "\n## Planner Guidance\n\nTry the existing second-stage helper.\n",
            encoding="utf-8",
        )
        html = plan_dashboard.generate_dashboard(plan_root).read_text("utf-8")
        # Nav tree, per-node bodies, per-node child DAGs, and the kanban board.
        assert "/nav" in html
        assert "/node/01-first" in html
        assert "/dag?root=02-second" in html
        assert "/kanban" in html
        # The embedded data carries the section markdown payloads.
        assert "Found 100 rows" in html
        assert "Planner Guidance" in html
        assert "Try the existing second-stage helper." in html

    def test_generate_embeds_internal_task_link_resolver(self, plan_root):
        """In-tree task citations route to internal hash navigation: the resolver
        and its task-path membership set must survive into the embedded output so
        a future refactor can't silently drop the feature from the static export."""
        html = plan_dashboard.generate_dashboard(plan_root).read_text("utf-8")
        assert "resolveInternalTaskPath" in html
        assert "TASK_PATHS" in html

    def test_generate_accepts_repo_file_base_for_static_links(self, plan_root):
        """GitHub artifact exports carry a repository blob base so standalone
        file links and the task-file button open GitHub instead of local editor
        links."""
        out = plan_root / "dashboard.html"
        plan_dashboard.generate_dashboard(
            plan_root,
            out,
            repo_file_base="https://github.com/owner/repo/blob/abc123/",
        )
        html = out.read_text("utf-8")
        assert 'var REPO_FILE_BASE = "https://github.com/owner/repo/blob/abc123";' in html
        assert "function repoFileHref(path)" in html
        assert "Open task.md on GitHub" in html

    def test_cli_dashboard_export_forwards_repo_file_base(self, plan_root, monkeypatch):
        calls = []

        def fake_module_main(module_name, argv=None, *, pass_argv=True):
            calls.append((module_name, argv, pass_argv))

        monkeypatch.setattr(cli, "_module_main", fake_module_main)
        cli.main([
            "dashboard",
            "export",
            "--root",
            str(plan_root),
            "--repo-file-base",
            "https://github.com/owner/repo/blob/abc123",
        ])

        assert calls == [(
            "plan_dashboard",
            [
                "generate",
                "--plan-root",
                str(plan_root),
                "--repo-file-base",
                "https://github.com/owner/repo/blob/abc123",
            ],
            True,
        )]

    def test_generate_repo_file_prefix_for_nested_root(self, plan_root):
        """--repo-file-prefix sets the repo-root-relative prefix for repo links,
        so a tree below the repo root keeps its leading path instead of the bare
        basename; default keeps the basename (REPO_ROOT_PREFIX falls back)."""
        out = plan_root / "dashboard.html"
        plan_dashboard.generate_dashboard(
            plan_root, out,
            repo_file_base="https://github.com/owner/repo/blob/abc123",
            repo_root_prefix="docs/showcase-demo",
        )
        html = out.read_text("utf-8")
        assert 'var REPO_ROOT_PREFIX = "docs/showcase-demo" || ROOT_PREFIX;' in html

    def test_generate_repo_file_prefix_default_falls_back(self, plan_root):
        """No --repo-file-prefix -> empty literal, so REPO_ROOT_PREFIX || ROOT_PREFIX
        resolves to the basename (a tree at the repo root is unaffected)."""
        out = plan_root / "dashboard.html"
        plan_dashboard.generate_dashboard(plan_root, out)
        assert 'var REPO_ROOT_PREFIX = "" || ROOT_PREFIX;' in out.read_text("utf-8")

    def test_cli_dashboard_export_forwards_repo_file_prefix(self, plan_root, monkeypatch):
        calls = []
        monkeypatch.setattr(
            cli, "_module_main",
            lambda mod, argv, **kw: calls.append(argv),
        )
        cli.main([
            "dashboard", "export", "--root", str(plan_root),
            "--repo-file-base", "https://github.com/owner/repo/blob/abc123",
            "--repo-file-prefix", "docs/showcase-demo",
        ])
        argv = calls[0]
        assert "--repo-file-prefix" in argv
        assert argv[argv.index("--repo-file-prefix") + 1] == "docs/showcase-demo"

    def test_dashboard_html_constant_removed(self):
        """The duplicate hand-maintained template is gone — one source remains."""
        src = (SCRIPTS_DIR / "plan_dashboard.py").read_text("utf-8")
        assert "DASHBOARD_HTML" not in src

    def test_vscode_file_links_translate_line_anchors(self):
        """File links keep their GitHub-style line anchor as VS Code's :line form
        so clicking jumps to the cited line (vscode://file ignores a #L fragment).
        Guards the renderMarkdown anchor-translation logic against removal."""
        src = (SCRIPTS_DIR / "templates" / "base.html").read_text("utf-8")
        assert "match(/#L" in src
        assert "repoFileHref(repoLinkPrefix + href)" in src

    def test_build_standalone_fragments_match_server_routes(self, plan_root):
        """Pre-rendered fragments are byte-identical to the live route output."""
        pytest.importorskip("httpx")
        from fastapi.testclient import TestClient

        plan_dashboard.PLAN_ROOT = plan_root
        # Generate to set module state, then build the fragment map.
        plan_dashboard.generate_dashboard(plan_root)
        fragments = plan_dashboard._build_standalone_fragments()

        with TestClient(plan_dashboard.app) as c:
            assert fragments["/nav"] == c.get("/nav").text
            assert fragments["/node/01-first"] == c.get("/node/01-first").text
            assert fragments["/kanban"] == c.get("/kanban").text
            assert (
                fragments["/dag?root=02-second"]
                == c.get("/dag", params={"root": "02-second"}).text
            )

    def test_standalone_dag_resolves_for_nested_path(self, plan_with_branches):
        """The /dag fragment for a multi-segment (nested) task must be reachable
        under the exact URL the standalone client builds.

        The client fetches '/dag?root=' + encodeURIComponent(path); for a nested
        path encodeURIComponent escapes '/' to %2F, so the request URL differs
        from the bare map key. The fetch shim decodes before the map lookup —
        this test locks that decode-then-lookup against the byte-identical
        server route, reproducing the %2F mismatch a single-segment path hides.
        """
        pytest.importorskip("httpx")
        from urllib.parse import quote

        from fastapi.testclient import TestClient

        plan_dashboard.PLAN_ROOT = plan_with_branches
        plan_dashboard.generate_dashboard(plan_with_branches)
        fragments = plan_dashboard._build_standalone_fragments()

        nested = "01-data-prep/02-merge"
        # The exact URL string the standalone client builds (JS encodeURIComponent
        # escapes '/' to %2F; quote(safe='') matches it for slug characters).
        client_url = "/dag?root=" + quote(nested, safe="")
        assert "%2F" in client_url  # guard: the nested path really is encoded.
        assert client_url not in fragments  # the map is keyed by the bare path.

        # The shim decodes the client URL before the lookup; that must hit.
        decoded_url = "/dag?root=" + nested
        assert decoded_url in fragments

        with TestClient(plan_dashboard.app) as c:
            assert (
                fragments[decoded_url]
                == c.get("/dag", params={"root": nested}).text
            )

    def test_standalone_embeds_root_node_body(self, plan_with_branches):
        """The root's OWN /node/ body must be embedded, not just descendants'.

        collect_all_tasks excludes the root, so without including it the root
        card fetches a missing /node/ fragment and renders "Could not load this
        task" — and a leaf-only subtree export (a re-based root with no children)
        embeds no node body at all.
        """
        plan_dashboard.PLAN_ROOT = plan_with_branches

        # Whole tree: the root's /node/ (empty path) fragment is embedded.
        whole = plan_dashboard.render_standalone_html(plan_with_branches, root=None)
        assert '"/node/"' in whole

        # Leaf subtree: the re-based root has the empty path; its body must be
        # present and reachable (the exact case that rendered "Could not load").
        leaf = plan_dashboard.render_standalone_html(
            plan_with_branches, root="01-data-prep/02-merge"
        )
        assert '"/node/"' in leaf
        assert "Merge Data" in leaf

    def test_subtree_export_scopes_paths_to_subtree(self, plan_with_branches):
        """A --root export re-bases every embedded task path so the subtree node
        is the root: paths are relative to it and out-of-subtree siblings are
        absent."""
        out = plan_with_branches / "sub.html"
        plan_dashboard.generate_dashboard(
            plan_with_branches, out, root="01-data-prep"
        )
        html = out.read_text("utf-8")
        # Re-based: the subtree's children appear under their relative paths.
        assert 'set["01-load"] = true' in html
        assert 'set["02-merge"] = true' in html
        # The full tree path of the subtree root is gone (re-based to "").
        assert 'set["01-data-prep' not in html
        # The out-of-subtree sibling never enters the embedded path set.
        assert 'set["02-estimation"] = true' not in html

    def test_subtree_export_fragments_cover_only_subtree(self, plan_with_branches):
        """The pre-rendered fragment map covers exactly the subtree, keyed by
        re-based paths, with no whole-tree-only fragments leaking in."""
        out = plan_with_branches / "sub.html"
        plan_dashboard.generate_dashboard(
            plan_with_branches, out, root="01-data-prep"
        )
        html = out.read_text("utf-8")
        assert '"/node/01-load"' in html
        assert '"/node/02-merge"' in html
        # Out-of-subtree node fragment must not be embedded.
        assert '"/node/02-estimation"' not in html
        # No un-rebased full-path fragment keys survive.
        assert '/node/01-data-prep/' not in html

    def test_subtree_export_is_offline_clean(self, plan_with_branches):
        """The subtree export inherits the standalone offline-clean property:
        embedded data, no SSE/worktree controls."""
        out = plan_with_branches / "sub.html"
        plan_dashboard.generate_dashboard(
            plan_with_branches, out, root="01-data-prep"
        )
        html = out.read_text("utf-8")
        assert "window.STANDALONE = true" in html
        assert "STANDALONE_FRAGMENTS =" in html
        assert "sse-connect=" not in html
        assert 'hx-ext="sse"' not in html
        assert "EventSource(" not in html
        assert 'id="worktree-selector"' not in html
        assert 'id="sse-full-reload"' not in html

    def test_subtree_export_unknown_root_raises(self, plan_with_branches):
        with pytest.raises(KeyError):
            plan_dashboard.generate_dashboard(
                plan_with_branches, plan_with_branches / "x.html", root="no/such"
            )

    def test_whole_tree_export_unchanged_by_root_param(self, plan_root):
        """generate_dashboard(root=None) is byte-identical to the bare call —
        adding the subtree-scoping branch did not perturb the whole-tree path."""
        a = plan_dashboard.generate_dashboard(plan_root, plan_root / "a.html")
        b = plan_dashboard.generate_dashboard(
            plan_root, plan_root / "b.html", root=None
        )
        assert a.read_text("utf-8") == b.read_text("utf-8")


class TestDashboardArtifactWorkflow:
    def test_sanitize_artifact_slug_matches_workflow_contract(self):
        assert dashboard_artifact_workflow.sanitize_artifact_slug("Feature/Foo Bar") == "feature-foo-bar"
        assert dashboard_artifact_workflow.sanitize_artifact_slug("analysis/task_tree.v2") == "analysis-task_tree.v2"
        assert dashboard_artifact_workflow.sanitize_artifact_slug("!!!") == "ref"

    def test_artifact_name_for_ref_uses_branch_stable_prefix(self):
        assert (
            dashboard_artifact_workflow.artifact_name_for_ref("Plan/GitHub Dashboard")
            == "superra-dashboard-plan-github-dashboard-e5f9ea141877"
        )

    def test_artifact_name_resists_slug_collisions(self):
        slash = dashboard_artifact_workflow.artifact_name_for_ref("feature/foo")
        hyphen = dashboard_artifact_workflow.artifact_name_for_ref("feature-foo")
        assert slash.startswith("superra-dashboard-feature-foo-")
        assert hyphen.startswith("superra-dashboard-feature-foo-")
        assert slash != hyphen

    def test_render_workflow_has_cleanup_upload_and_export_contract(self):
        workflow = dashboard_artifact_workflow.render_workflow()
        assert dashboard_artifact_workflow.MANAGED_MARKER in workflow
        assert "permissions:\n  contents: read\n  actions: write" in workflow
        assert "concurrency:" in workflow
        assert "superra-dashboard-artifact-${{ github.ref }}" in workflow
        assert "shasum -a 256" in workflow
        assert 'artifact_name=__ARTIFACT_PREFIX__-$slug-$ref_hash' not in workflow
        assert "uv run --script skills/task-tree/scripts/plan_dashboard.py dashboard export --root \"superRA\"" in workflow
        assert '--repo-file-base "https://github.com/${{ github.repository }}/blob/${{ github.sha }}"' in workflow
        assert "github.rest.actions.listArtifactsForRepo" in workflow
        assert "github.rest.actions.deleteArtifact" in workflow
        assert "actions/upload-artifact@v4" in workflow
        assert "name: ${{ steps.artifact.outputs.artifact_name }}" in workflow
        assert "retention-days: 14" in workflow
        assert "upload-artifact" not in workflow.split("Delete previous artifact for this branch", 1)[0]

    def test_render_workflow_applies_configurable_paths_and_retention(self):
        config = dashboard_artifact_workflow.WorkflowConfig(
            task_root="customRA",
            output_path="build/custom-dashboard.html",
            artifact_prefix="custom-dashboard",
            retention_days=3,
            fail_on_missing_task_root=False,
            branch_patterns=("main", "analysis/**"),
        )
        workflow = dashboard_artifact_workflow.render_workflow(config)
        assert 'uv run --script skills/task-tree/scripts/plan_dashboard.py dashboard export --root "customRA"' in workflow
        assert '--output "build/custom-dashboard.html"' in workflow
        assert "custom-dashboard-$slug-$ref_hash" in workflow
        assert "retention-days: 3" in workflow
        assert "skipping dashboard artifact" in workflow
        assert '      - "main"' in workflow
        assert '      - "analysis/**"' in workflow

    def test_install_workflow_creates_default_managed_file(self, tmp_path):
        result = dashboard_artifact_workflow.install_workflow(
            tmp_path,
            preview_ref="feature/foo",
        )
        assert result.created is True
        assert result.path == tmp_path / ".github/workflows/superra-dashboard-artifact.yml"
        content = result.path.read_text(encoding="utf-8")
        assert dashboard_artifact_workflow.MANAGED_MARKER in content
        assert result.artifact_name_preview.startswith("superra-dashboard-feature-foo-")

    def test_install_workflow_is_idempotent_for_managed_file(self, tmp_path):
        first = dashboard_artifact_workflow.install_workflow(tmp_path)
        second = dashboard_artifact_workflow.install_workflow(tmp_path)
        assert first.created is True
        assert second.created is False
        assert first.path.read_text(encoding="utf-8") == second.path.read_text(encoding="utf-8")

    def test_install_workflow_refuses_unmanaged_overwrite(self, tmp_path):
        target = tmp_path / ".github/workflows/superra-dashboard-artifact.yml"
        target.parent.mkdir(parents=True)
        target.write_text("name: existing\n", encoding="utf-8")
        with pytest.raises(FileExistsError):
            dashboard_artifact_workflow.install_workflow(tmp_path)

    def test_install_workflow_force_overwrites_unmanaged_file(self, tmp_path):
        target = tmp_path / ".github/workflows/custom.yml"
        target.parent.mkdir(parents=True)
        target.write_text("name: existing\n", encoding="utf-8")
        result = dashboard_artifact_workflow.install_workflow(
            tmp_path,
            workflow_path=".github/workflows/custom.yml",
            force=True,
        )
        assert result.created is False
        assert dashboard_artifact_workflow.MANAGED_MARKER in target.read_text(encoding="utf-8")

    def test_cli_dashboard_artifact_setup_writes_configured_workflow(self, tmp_path, capsys):
        cli.main([
            "dashboard",
            "artifact",
            "setup",
            "--repo-root",
            str(tmp_path),
            "--workflow-path",
            ".github/workflows/custom.yml",
            "--task-root",
            "customRA",
            "--output",
            "build/dashboard.html",
            "--artifact-prefix",
            "custom-dashboard",
            "--retention-days",
            "5",
            "--branch",
            "main",
            "--branch",
            "analysis/**",
            "--skip-missing-task-root",
            "--preview-ref",
            "Feature/Foo",
        ])
        target = tmp_path / ".github/workflows/custom.yml"
        content = target.read_text(encoding="utf-8")
        assert '--root "customRA"' in content
        assert '--output "build/dashboard.html"' in content
        assert "custom-dashboard-$slug-$ref_hash" in content
        assert "retention-days: 5" in content
        assert '      - "main"' in content
        assert '      - "analysis/**"' in content
        assert "skipping dashboard artifact" in content
        out = capsys.readouterr().out
        assert "Created" in out
        assert "custom-dashboard-feature-foo-" in out

    def test_cli_dashboard_artifact_setup_reports_guard_errors(self, tmp_path, capsys):
        with pytest.raises(SystemExit) as excinfo:
            cli.main([
                "dashboard",
                "artifact",
                "setup",
                "--repo-root",
                str(tmp_path),
                "--workflow-path",
                "../escape.yml",
            ])
        assert excinfo.value.code == 1
        assert "Error: Workflow path escapes repository root" in capsys.readouterr().err

    def test_generated_workflow_static_contract(self, tmp_path):
        result = dashboard_artifact_workflow.install_workflow(
            tmp_path,
            config=dashboard_artifact_workflow.WorkflowConfig(branch_patterns=("main", "feature/**")),
        )
        content = result.path.read_text(encoding="utf-8")
        lines = _workflow_lines(content)
        on_idx = _line_index(lines, "on:")
        push_idx = _line_index(lines, "  push:")
        branches_idx = _line_index(lines, "    branches:")
        workflow_dispatch_idx = _line_index(lines, "  workflow_dispatch:")
        permissions_idx = _line_index(lines, "permissions:")
        assert on_idx < push_idx < branches_idx < workflow_dispatch_idx < permissions_idx
        assert "permissions:" in lines
        assert "  contents: read" in lines
        assert "  actions: write" in lines
        assert branches_idx < _line_index(lines, '      - "main"') < workflow_dispatch_idx
        assert branches_idx < _line_index(lines, '      - "feature/**"') < workflow_dispatch_idx
        assert "concurrency:" in lines
        assert "      - name: Delete previous artifact for this branch" in lines
        assert "      - name: Upload branch dashboard artifact" in lines
        assert content.index("Delete previous artifact for this branch") < content.index("Upload branch dashboard artifact")

    def test_dashboard_export_payload_path_from_minimal_tree(self, tmp_path):
        repo = tmp_path / "repo"
        task_root = repo / "superRA"
        task_root.mkdir(parents=True)
        _write_task_md(task_root / "task.md", "Artifact Smoke", "not-started", objective="Smoke tree.")
        output = repo / ".superra-dashboard" / "dashboard.html"
        output.parent.mkdir(parents=True)
        cli.main([
            "dashboard",
            "export",
            "--root",
            str(task_root),
            "--output",
            str(output),
        ])
        html = output.read_text(encoding="utf-8")
        assert "Artifact Smoke" in html
        assert "window.STANDALONE = true" in html


class TestStandaloneSelfContained:
    """The standalone export embeds figures (base64 data URIs) and inlines the
    vendored render libraries (markdown-it/texmath/KaTeX + woff2 fonts) so a
    moved/offline single file renders figures and math with no CDN fetch.

    These committed assertions are SOURCE-PRESENCE checks (the data URIs, inline
    script/style bodies, and CDN-tag absence are in the output string). The
    behavioral proof — that a browser actually decodes the figure and renders the
    KaTeX DOM from a file:// open with the network blocked — is a separate
    headless-Chromium check, recorded in the task's Results (not committed here,
    since there is no browser harness in this suite).
    """

    @pytest.fixture
    def fig_math_plan(self, tmp_path):
        """A two-task plan: a root and one child whose body has a relative figure
        and a `$...$` math expression — the minimum to exercise both embeddings."""
        root = tmp_path / "superRA"
        root.mkdir()
        _write_task_md(root / "task.md", "Embed Project", "not-started",
                       objective="Root overview.")
        child = root / "01-figmath"
        child.mkdir()
        _write_tiny_png(child / "attachments" / "demo.png")
        _write_task_md(
            child / "task.md", "Figure and Math", "not-started",
            objective="Math $e^{i\\pi}+1=0$ and a figure.\n\n"
                      "![red square](attachments/demo.png)",
        )
        return root

    def test_figure_embedded_as_data_uri(self, fig_math_plan):
        """A relative figure in a task body is base64-embedded under the exact
        client key, and its data URI carries the correct PNG MIME."""
        out = fig_math_plan / "export.html"
        plan_dashboard.generate_dashboard(
            fig_math_plan, out, root="01-figmath"
        )
        html = out.read_text("utf-8")
        # The map var is present and contains a PNG data URI for the figure.
        assert "var STANDALONE_IMAGES =" in html
        assert "data:image/png;base64," in html
        # Re-based root key: the child becomes the root (path ""), so the figure
        # key is the bare src, not a task-path-prefixed one.
        assert "attachments/demo.png" in html

    def test_image_map_keys_and_mime(self, fig_math_plan):
        """_build_standalone_images keys by the client-computed string and picks
        MIME by extension; the bytes round-trip through the data URI."""
        import base64

        full = plan_dashboard.walk_plan(fig_math_plan)
        # Whole-tree (un-rebased) tree: the child keeps its real path "01-figmath",
        # so the key is "01-figmath/attachments/demo.png".
        images = plan_dashboard._build_standalone_images(full)
        key = "01-figmath/attachments/demo.png"
        assert key in images
        assert images[key].startswith("data:image/png;base64,")
        # Decoding the data URI yields a valid PNG (magic bytes).
        b64 = images[key].split(",", 1)[1]
        assert base64.b64decode(b64).startswith(b"\x89PNG\r\n\x1a\n")

    def test_image_map_skips_remote_and_absolute(self, tmp_path):
        """http(s)/absolute/data srcs are never embedded; only resolvable
        relative figures are."""
        root = tmp_path / "superRA"
        root.mkdir()
        _write_task_md(root / "task.md", "Root", "not-started")
        child = root / "01-mixed"
        child.mkdir()
        _write_tiny_png(child / "local.png")
        _write_task_md(
            child / "task.md", "Mixed", "not-started",
            objective="![a](local.png) ![b](https://x/y.png) "
                      "![c](/abs.png) ![d](data:image/png;base64,AAAA)",
        )
        images = plan_dashboard._build_standalone_images(
            plan_dashboard.walk_plan(root)
        )
        assert "01-mixed/local.png" in images
        assert not any("https://x/y.png" in k for k in images)
        assert not any(k.endswith("/abs.png") for k in images)
        assert "01-mixed/data:image/png;base64,AAAA" not in images

    def test_image_map_handles_html_img_tag(self, tmp_path):
        """`<img src=...>` references are embedded the same as `![alt](src)`."""
        root = tmp_path / "superRA"
        root.mkdir()
        _write_task_md(root / "task.md", "Root", "not-started")
        child = root / "01-html"
        child.mkdir()
        _write_tiny_png(child / "pic.png")
        _write_task_md(
            child / "task.md", "Html", "not-started",
            objective='An image: <img src="pic.png" alt="p">',
        )
        images = plan_dashboard._build_standalone_images(
            plan_dashboard.walk_plan(root)
        )
        assert "01-html/pic.png" in images

    def test_standalone_inlines_render_libraries(self, fig_math_plan):
        """Standalone output inlines the vendored markdown-it/texmath/KaTeX JS and
        the font-inlined KaTeX CSS — and drops the CDN tags for those three."""
        out = fig_math_plan / "export.html"
        plan_dashboard.generate_dashboard(fig_math_plan, out, root="01-figmath")
        html = out.read_text("utf-8")
        # Inline library bodies present (version banner / global from each lib).
        assert "markdown-it 14.2.0" in html
        assert "katex" in html.lower()
        # KaTeX @font-face rewritten to a base64 woff2 data URI (inlined fonts).
        assert "data:font/woff2;base64," in html
        # The required CDN tags for these three are GONE in standalone.
        assert "cdn.jsdelivr.net/npm/markdown-it@" not in html
        assert "cdn.jsdelivr.net/npm/katex@" not in html
        assert "cdn.jsdelivr.net/npm/markdown-it-texmath@" not in html
        # Google Fonts + htmx/sse CDN tags may remain (allowed by scope).
        assert "fonts.googleapis.com" in html
        assert "htmx.org@2" in html

    def test_img_loop_consults_standalone_images_first(self):
        """The client img[src] loop looks up STANDALONE_IMAGES before its
        relative-path fallback (guards the lookup against removal)."""
        src = (SCRIPTS_DIR / "templates" / "base.html").read_text("utf-8")
        assert "STANDALONE_IMAGES.hasOwnProperty(key)" in src

    def test_inline_katex_css_uses_woff2_only(self):
        """The CSS font-inlining rewrites every @font-face to one base64 woff2
        data URI and emits no remaining url(fonts/...woff2) reference."""
        assets = plan_dashboard._build_standalone_assets()
        css = assets["katex_css"]
        assert "data:font/woff2;base64," in css
        # Every original url(fonts/KaTeX_*.woff2) is replaced by a data URI.
        assert "url(fonts/KaTeX_" not in css
        # All 20 KaTeX font faces are inlined.
        assert css.count("data:font/woff2;base64,") == 20

    def test_vendor_files_present(self):
        """The vendored render libraries and the full woff2 font set exist so the
        export build is hermetic (no fetch-at-build)."""
        vendor = SCRIPTS_DIR / "vendor"
        for name in ("markdown-it.min.js", "katex.min.js",
                     "katex.min.css", "texmath.min.js", "README.md"):
            assert (vendor / name).exists(), f"missing vendored {name}"
        woff2 = list((vendor / "fonts").glob("KaTeX_*.woff2"))
        assert len(woff2) == 20, f"expected 20 woff2 fonts, found {len(woff2)}"


# ---------------------------------------------------------------------------
# Dual-use dashboard features: doc-mode, code highlighting, client search
# ---------------------------------------------------------------------------


def _docs_plan(tmp_path):
    """A two-node plan: a root landing page and one child doc page, each with a
    fenced code block — the minimum to exercise doc-mode, highlighting, and
    search over titles + body text."""
    root = tmp_path / "superRA"
    root.mkdir()
    _write_task_md(
        root / "task.md", "Quickstart Home", "not-started",
        objective="Welcome to the docs about panel regressions.",
    )
    child = root / "01-merge-guide"
    child.mkdir()
    _write_task_md(
        child / "task.md", "Merging Datasets", "approved",
        objective="How to merge CRSP and Compustat with a left join.\n\n"
                  "```python\ndf.merge(other, how='left')\n```\n\n"
                  "```julia\nf(x) = x^2\n```",
    )
    return root


def _docs_client(plan_root):
    """A TestClient serving *plan_root* — mirrors the `client` fixture setup so
    doc-mode/highlight/search tests can serve the docs plan directly."""
    from starlette.testclient import TestClient

    plan_dashboard.PLAN_ROOT = plan_root
    plan_dashboard._project_root = str(plan_root.resolve().parent)
    plan_dashboard._jinja_env = None
    plan_dashboard.rebuild_tree()
    return TestClient(plan_dashboard.app, raise_server_exceptions=True)


class TestDocMode:
    """Opt-in doc-mode renders the tree as documentation: task-workflow chrome is
    suppressed, while a default (no-flag) export stays unchanged."""

    def test_doc_mode_sets_attribute_and_flag(self, tmp_path):
        """--doc-mode marks <html data-doc-mode> and sets window.DOC_MODE true."""
        plan = _docs_plan(tmp_path)
        out = plan / "doc.html"
        plan_dashboard.generate_dashboard(plan, out, doc_mode=True)
        html = out.read_text("utf-8")
        assert 'data-doc-mode="true"' in html
        assert "window.DOC_MODE = true" in html

    def test_default_export_is_not_doc_mode(self, tmp_path):
        """Without the flag the export carries no doc-mode attribute and the flag
        is false — the default dashboard is unchanged."""
        plan = _docs_plan(tmp_path)
        out = plan / "default.html"
        plan_dashboard.generate_dashboard(plan, out)
        html = out.read_text("utf-8")
        assert 'data-doc-mode="true"' not in html
        assert "window.DOC_MODE = false" in html

    def test_doc_mode_suppresses_chrome_via_css(self, tmp_path):
        """Doc-mode output carries the chrome-suppression rules keyed off
        html[data-doc-mode] (badges, progress, summary bar, kanban toggle, DAG)."""
        plan = _docs_plan(tmp_path)
        out = plan / "doc.html"
        plan_dashboard.generate_dashboard(plan, out, doc_mode=True)
        html = out.read_text("utf-8")
        for selector in (
            "html[data-doc-mode] .badge",
            "html[data-doc-mode] #summary-bar",
            "html[data-doc-mode] #btn-kanban",
            "html[data-doc-mode] .children-dag",
        ):
            assert selector in html, f"missing doc-mode rule: {selector}"

    def test_active_node_badge_gated_on_doc_mode(self):
        """The one JS-built status badge (active-node head) is gated on
        !window.DOC_MODE so it never renders in doc-mode."""
        src = (SCRIPTS_DIR / "templates" / "base.html").read_text("utf-8")
        assert "(status && !window.DOC_MODE)" in src

    def test_doc_mode_default_off_in_render(self, tmp_path):
        """generate_dashboard defaults doc_mode off (explicit-opt-in invariant)."""
        plan = _docs_plan(tmp_path)
        out = plan / "default.html"
        plan_dashboard.generate_dashboard(plan, out)
        assert 'data-doc-mode' not in out.read_text("utf-8").split("\n")[1]

    def test_serve_index_carries_doc_mode_flag(self, tmp_path, monkeypatch):
        """The live index route honors the module DOC_MODE flag set by
        `serve --doc-mode`."""
        plan = _docs_plan(tmp_path)
        monkeypatch.setattr(plan_dashboard, "DOC_MODE", True)
        with _docs_client(plan) as client:
            html = client.get("/").text
        assert 'data-doc-mode="true"' in html
        assert "window.DOC_MODE = true" in html

    def test_serve_index_default_not_doc_mode(self, tmp_path, monkeypatch):
        """With DOC_MODE off (default) the served page carries no doc-mode."""
        plan = _docs_plan(tmp_path)
        monkeypatch.setattr(plan_dashboard, "DOC_MODE", False)
        with _docs_client(plan) as client:
            html = client.get("/").text
        assert 'data-doc-mode="true"' not in html
        assert "window.DOC_MODE = false" in html

    def test_cli_generate_doc_mode_flag(self, tmp_path):
        """`generate --doc-mode` reaches generate_dashboard."""
        plan = _docs_plan(tmp_path)
        out = plan / "cli-doc.html"
        plan_dashboard.main(
            ["generate", "--plan-root", str(plan), "--output", str(out), "--doc-mode"]
        )
        assert 'data-doc-mode="true"' in out.read_text("utf-8")

    def test_cli_dashboard_export_doc_mode_forwards(self, tmp_path, monkeypatch):
        """`cli dashboard export --doc-mode` forwards --doc-mode to generate."""
        plan = _docs_plan(tmp_path)
        out = plan / "cli-exp.html"
        captured = {}

        def fake_main(argv):
            captured["argv"] = argv

        monkeypatch.setattr(cli, "_module_main", lambda mod, argv: fake_main(argv))
        cli.main([
            "dashboard", "--root", str(plan), "export",
            "--output", str(out), "--doc-mode",
        ])
        assert "--doc-mode" in captured["argv"]

    def test_cli_dashboard_export_doc_mode_before_subcommand(self, tmp_path, monkeypatch):
        """--doc-mode also works placed before the `export` subcommand."""
        plan = _docs_plan(tmp_path)
        captured = {}
        monkeypatch.setattr(cli, "_module_main",
                            lambda mod, argv: captured.__setitem__("argv", argv))
        cli.main(["dashboard", "--root", str(plan), "--doc-mode", "export"])
        assert "--doc-mode" in captured["argv"]

    def test_doc_local_links_embedded(self, tmp_path):
        """--doc-local-link basenames land in the embedded DOC_LOCAL_LINKS so the
        client leaves those sibling-artifact links relative; default is empty."""
        plan = _docs_plan(tmp_path)
        out = plan / "doc.html"
        plan_dashboard.generate_dashboard(
            plan, out, doc_mode=True,
            doc_local_links=["demo-tree.html", "superra-dev-tree.html"],
        )
        html = out.read_text("utf-8")
        assert ('var DOC_LOCAL_LINKS = ["demo-tree.html", "superra-dev-tree.html"];'
                in html)

    def test_doc_local_links_default_empty(self, tmp_path):
        """Without --doc-local-link the embedded list is empty (no regression)."""
        plan = _docs_plan(tmp_path)
        out = plan / "doc.html"
        plan_dashboard.generate_dashboard(plan, out, doc_mode=True)
        assert "var DOC_LOCAL_LINKS = [];" in out.read_text("utf-8")

    def test_cli_generate_doc_local_link_repeatable(self, tmp_path):
        """`generate --doc-local-link` is repeatable and reaches the export."""
        plan = _docs_plan(tmp_path)
        out = plan / "cli-doc.html"
        plan_dashboard.main([
            "generate", "--plan-root", str(plan), "--output", str(out),
            "--doc-mode",
            "--doc-local-link", "demo-tree.html",
            "--doc-local-link", "superra-dev-tree.html",
        ])
        assert ('var DOC_LOCAL_LINKS = ["demo-tree.html", "superra-dev-tree.html"];'
                in out.read_text("utf-8"))

    def test_cli_dashboard_export_doc_local_link_forwards(self, tmp_path, monkeypatch):
        """`cli dashboard export --doc-local-link` forwards each to generate."""
        plan = _docs_plan(tmp_path)
        captured = {}
        monkeypatch.setattr(cli, "_module_main",
                            lambda mod, argv: captured.__setitem__("argv", argv))
        cli.main([
            "dashboard", "--root", str(plan), "export", "--doc-mode",
            "--doc-local-link", "demo-tree.html",
            "--doc-local-link", "superra-dev-tree.html",
        ])
        argv = captured["argv"]
        assert argv.count("--doc-local-link") == 2
        assert "demo-tree.html" in argv and "superra-dev-tree.html" in argv

    @pytest.mark.skipif(_NODE is None, reason="node not available")
    def test_doc_mode_link_rewrite_behavioral(self):
        """Run renderMarkdown under node and assert the doc-mode link branch:
        a repo-relative authority link resolves repo-root-relative against the
        blob base (not against the doc node dir), a sibling-export link stays a
        plain relative href, and with doc-mode off the link is task-relative."""
        defs = _extract_js_defs(["encodeRepoPath", "repoFileHref",
                                 "resolveInternalTaskPath", "renderMarkdown"])
        shim = r"""
var md = { render: function (text) {
  var out = text;
  out = out.replace(/\[([^\]]*)\]\(([^)]+)\)/g,
    function (_, t, h) { return '<a href="' + h + '">' + t + '</a>'; });
  return out;
} };
function makeEl(tag) {
  return {
    tagName: tag.toUpperCase(), _as: [],
    set innerHTML(html) {
      var self = this; this._as = [];
      var am; var are = /<a[^>]*\bhref="([^"]*)"[^>]*>/g;
      while ((am = are.exec(html))) {
        (function (val) {
          var attrs = { href: val };
          self._as.push({
            _attrs: attrs,
            getAttribute: function (n) { return attrs[n] != null ? attrs[n] : null; },
            setAttribute: function (n, v) { attrs[n] = v; },
            removeAttribute: function (n) { delete attrs[n]; },
            classList: { add: function () {} },
          });
        })(am[1]);
      }
    },
    get innerHTML() {
      var out = '';
      for (var i = 0; i < this._as.length; i++) {
        out += '<a href="' + (this._as[i]._attrs.href || '') + '"></a>';
      }
      return out;
    },
    querySelectorAll: function (sel) {
      if (sel === 'a[href]') return this._as;
      return [];
    },
  };
}
var document = { createElement: function (t) { return makeEl(t); } };
// Pass-through DOMPurify: renderMarkdown sanitizes before DOM insertion, but
// this link-rewrite branch runs after sanitization, so the stub keeps the
// rewrite logic real (see _RENDER_MD_SHIM for the same rationale).
var DOMPurify = { sanitize: function (html) { return html; } };
"""

        def run(body, task_path, doc_mode, local_links):
            harness = (
                shim
                + "var window = { STANDALONE: false, DOC_MODE: "
                + ("true" if doc_mode else "false") + " };\n"
                + "var RESOLVED_ROOT = '/abs/docs/site';\n"
                + "var ROOT_PREFIX = 'site';\n"
                + "var REPO_ROOT_PREFIX = 'site';\n"
                + "var REPO_FILE_BASE = 'https://gh/owner/repo/blob/sha';\n"
                + "var DOC_LOCAL_LINKS = " + json.dumps(local_links) + ";\n"
                + "var TASK_PATHS = {};\n"
                + defs + "\n"
                + "var out = renderMarkdown(" + json.dumps(body) + ", null, "
                + json.dumps(task_path) + ");\n"
                + "var m = out.match(/href=\"([^\"]*)\"/);\n"
                + "console.log(JSON.stringify({href: m ? m[1] : null}));\n"
            )
            proc = subprocess.run(
                [_NODE, "-e", harness], capture_output=True, text=True, timeout=20
            )
            assert proc.returncode == 0, proc.stderr
            return json.loads(proc.stdout.strip().splitlines()[-1])["href"]

        # Authority link on a deep doc page -> repo-root-relative blob URL.
        href = run("[superplan](skills/superplan/SKILL.md)",
                   "03-concepts/01-the-workflow", True,
                   ["demo-tree.html"])
        assert href == "https://gh/owner/repo/blob/sha/skills/superplan/SKILL.md"

        # Sibling-export link stays a plain relative href (build artifact).
        href = run("[demo](demo-tree.html)", "06-showcase", True,
                   ["demo-tree.html", "superra-dev-tree.html"])
        assert href == "demo-tree.html"

        # Doc-mode off: the same href is task-relative (no rebasing change).
        href = run("[fig](skills/superplan/SKILL.md)",
                   "03-concepts/01-the-workflow", False, [])
        assert href == (
            "https://gh/owner/repo/blob/sha/"
            "site/03-concepts/01-the-workflow/skills/superplan/SKILL.md"
        )


class TestCodeHighlighting:
    """Fenced code blocks render with highlight.js, wired into the markdown-it
    path and inlined in the standalone export with theme-aware token colors."""

    def test_markdown_it_wired_with_highlight(self):
        """markdown-it is constructed with the highlightFence highlighter."""
        src = (SCRIPTS_DIR / "templates" / "base.html").read_text("utf-8")
        assert "highlight: highlightFence" in src
        assert "function highlightFence" in src

    def test_unknown_language_falls_through(self):
        """highlightFence returns '' for an unknown/absent language so markdown-it
        keeps its default (plain) rendering — no regression for untagged code."""
        src = (SCRIPTS_DIR / "templates" / "base.html").read_text("utf-8")
        # Guard the gate that only highlights a registered language.
        assert "hljs.getLanguage(lang)" in src

    def test_standalone_inlines_highlight_js(self, tmp_path):
        """The standalone export inlines the highlight.js bundle + the julia
        language module and drops the highlight.js CDN tags."""
        plan = _docs_plan(tmp_path)
        out = plan / "doc.html"
        plan_dashboard.generate_dashboard(plan, out)
        html = out.read_text("utf-8")
        assert "hljs" in html  # bundle global present inline
        assert "cdn.jsdelivr.net/npm/@highlightjs" not in html

    def test_highlight_assets_built(self):
        """_build_standalone_assets reads the vendored highlight bundle + julia."""
        assets = plan_dashboard._build_standalone_assets()
        assert assets["hljs_js"]
        assert assets["hljs_julia_js"]

    def test_theme_aware_highlight_tokens(self):
        """Highlight token colors are theme tokens (--hl-*) defined in both the
        light root and the dark theme block, so code is readable in both."""
        src = (SCRIPTS_DIR / "templates" / "base.html").read_text("utf-8")
        # Defined once in :root (light) and once in [data-theme="dark"].
        assert src.count("--hl-keyword:") == 2
        assert ".rendered-md .hljs-keyword" in src

    def test_vendor_highlight_files_present(self):
        """The highlight.js bundle and the julia language module are vendored."""
        vendor = SCRIPTS_DIR / "vendor"
        assert (vendor / "highlight.min.js").exists()
        assert (vendor / "languages" / "julia.min.js").exists()

    def test_served_page_keeps_highlight_cdn(self, tmp_path):
        """Server mode loads highlight.js from the CDN tags (mirrors the existing
        markdown-it/katex CDN tags)."""
        plan = _docs_plan(tmp_path)
        with _docs_client(plan) as client:
            html = client.get("/").text
        assert "cdn.jsdelivr.net/npm/@highlightjs" in html


class TestRawHtmlSanitization:
    """Agent-authored raw HTML in task markdown renders via markdown-it (html:true)
    and is sanitized through DOMPurify before DOM insertion.

    Like the figure/highlight standalone tests, these committed checks are
    SOURCE-PRESENCE assertions over base.html / the export / the vendored asset.
    The behavioral proof — that a browser passes a styled <div> through with its
    style attribute, neutralizes a hostile <script>/onerror=/javascript: fixture,
    and leaves plain-markdown escaping unchanged — is a headless-Chromium drive
    recorded in the task's Results, since this suite has no browser/JS harness.
    """

    def test_markdownit_html_enabled(self):
        """markdown-it is constructed with html:true so agent-authored HTML in a
        task body is emitted as live HTML rather than escaped text."""
        src = (SCRIPTS_DIR / "templates" / "base.html").read_text("utf-8")
        assert "window.markdownit({ html: true," in src
        # The old escape-everything config must be gone (would re-break raw HTML).
        assert "html: false" not in src

    def test_render_result_is_sanitized(self):
        """Every md.render(...) result flows through DOMPurify.sanitize before it
        reaches the DOM, with style/class kept for authored inline styling. The
        single renderMarkdown helper is the only md.render call site, so covering
        it covers task sections, doc pages, and section previews."""
        src = (SCRIPTS_DIR / "templates" / "base.html").read_text("utf-8")
        assert (
            "DOMPurify.sanitize(md.render(text), { ADD_ATTR: ['style', 'class'] })"
            in src
        )
        # No raw md.render(...) reaches innerHTML unsanitized: the only call site
        # is the one wrapped above.
        assert src.count("md.render(") == 1

    def test_vendor_purify_present(self):
        """DOMPurify is vendored for the standalone (offline/published) export."""
        assert (SCRIPTS_DIR / "vendor" / "purify.min.js").exists()

    def test_purify_asset_built(self):
        """_build_standalone_assets reads the vendored DOMPurify body."""
        assets = plan_dashboard._build_standalone_assets()
        assert assets["purify_js"]
        assert "DOMPurify" in assets["purify_js"]

    def test_standalone_inlines_purify(self, tmp_path):
        """The standalone export inlines DOMPurify and drops its CDN tag, so a
        published/offline single file sanitizes with no network call."""
        plan = _docs_plan(tmp_path)
        out = plan / "doc.html"
        plan_dashboard.generate_dashboard(plan, out)
        html = out.read_text("utf-8")
        assert "DOMPurify" in html  # inline body present
        assert "cdn.jsdelivr.net/npm/dompurify@" not in html

    def test_served_page_keeps_purify_cdn(self, tmp_path):
        """Server mode loads DOMPurify from the CDN tag (mirrors the existing
        markdown-it/katex/highlight CDN tags)."""
        plan = _docs_plan(tmp_path)
        with _docs_client(plan) as client:
            html = client.get("/").text
        assert "cdn.jsdelivr.net/npm/dompurify@3" in html


class TestClientSearch:
    """Full-text search over node titles + body text, navigating to results in
    both the live server and the standalone export."""

    def test_search_index_records_titles_and_body(self, tmp_path):
        """The index has one record per node (root included) carrying path, slug,
        title, and flattened body text."""
        plan = _docs_plan(tmp_path)
        full = plan_dashboard.walk_plan(plan)
        index = plan_dashboard._build_search_index(
            full, plan_dashboard.collect_all_tasks(full)
        )
        by_path = {r["path"]: r for r in index}
        assert "" in by_path and "01-merge-guide" in by_path
        # Title is indexed.
        assert by_path["01-merge-guide"]["title"] == "Merging Datasets"
        # Body prose is indexed (a phrase that is NOT in the title).
        assert "left join" in by_path["01-merge-guide"]["text"].lower()
        # Root body prose is indexed too.
        assert "panel regressions" in by_path[""]["text"].lower()

    def test_search_text_strips_code_and_markdown(self):
        """_search_text drops fenced/inline code and markdown punctuation."""
        text = plan_dashboard._search_text(
            "## Heading\n\nSome **prose** with `inline` code.\n\n"
            "```python\nsecret_token = 1\n```\n"
        )
        assert "prose" in text
        assert "Heading" in text
        # Code content and markdown punctuation are gone.
        assert "secret_token" not in text
        assert "#" not in text and "`" not in text

    def test_search_index_embedded_in_export(self, tmp_path):
        """The standalone export embeds SEARCH_INDEX so search runs offline."""
        plan = _docs_plan(tmp_path)
        out = plan / "doc.html"
        plan_dashboard.generate_dashboard(plan, out)
        html = out.read_text("utf-8")
        assert "var SEARCH_INDEX =" in html
        m = re.search(r"var SEARCH_INDEX = (\[.*?\]);", html, re.DOTALL)
        assert m is not None
        index = json.loads(m.group(1))
        assert any("left join" in r["text"].lower() for r in index)

    def test_search_palette_ui_and_navigation(self):
        """The palette UI, the title+body scorer, and navigation-via-setActive
        are wired (selecting a result routes exactly as a sidebar click)."""
        src = (SCRIPTS_DIR / "templates" / "base.html").read_text("utf-8")
        assert 'id="search-palette"' in src
        assert "function runSearch" in src
        assert "function scoreSearchRecord" in src
        # chooseSearchResult navigates through the same setActive router.
        assert "setActive(rec.path" in src

    def test_search_keyboard_affordances(self):
        """Keyboard: focus shortcut ('/' or Ctrl/Cmd-K), arrow navigation, Enter
        to open, Escape to dismiss."""
        src = (SCRIPTS_DIR / "templates" / "base.html").read_text("utf-8")
        assert "openSearchPalette()" in src
        assert "ArrowDown" in src and "ArrowUp" in src
        assert "event.key === 'Enter'" in src
        assert "event.key === 'Escape'" in src

    def test_search_index_endpoint_returns_index(self, tmp_path):
        """The live /api/search-index endpoint returns the same index shape so
        search reflects current tree state after a full-reload."""
        plan = _docs_plan(tmp_path)
        with _docs_client(plan) as client:
            data = client.get("/api/search-index").json()
        by_path = {r["path"]: r for r in data}
        assert "01-merge-guide" in by_path
        assert "left join" in by_path["01-merge-guide"]["text"].lower()

    def test_search_index_refreshed_on_reload(self):
        """The client re-fetches /api/search-index on a structural full-reload and
        on a worktree switch so live search stays current."""
        src = (SCRIPTS_DIR / "templates" / "base.html").read_text("utf-8")
        assert "function refreshSearchIndex" in src
        assert "refreshSearchIndex()" in src


# ---------------------------------------------------------------------------
# Master-detail server partials and lifecycle tests
# (moved from test_task_tree.py)
# ---------------------------------------------------------------------------

# --- Master-detail server partials (/nav, /nav/{path}, /node/{path}) -------


class TestMasterDetailPartials:
    """Shape checks for the additive master-detail server endpoints."""

    def _deep_plan(self, tmp_path):
        """A plan tree deep enough (>=4 levels) to exercise lazy nav loading."""
        root = tmp_path / "superRA"
        root.mkdir()
        _write_task_md(root / "task.md", "Root", "not-started",
                       objective="Root objective.")
        a = root / "01-a"
        a.mkdir()
        _write_task_md(a / "task.md", "A", "approved",
                       objective="A obj.", results="Found 100 rows")
        b = root / "02-b"
        b.mkdir()
        _write_task_md(b / "task.md", "B", "not-started",
                       depends_on=["01-a"],
                       objective="B obj.")
        x = b / "01-x"
        x.mkdir()
        _write_task_md(x / "task.md", "X", "approved", objective="X obj.")
        y = b / "02-y"
        y.mkdir()
        _write_task_md(y / "task.md", "Y", "not-started",
                       depends_on=["01-x"], objective="Y obj.")
        deep = y / "01-deep"
        deep.mkdir()
        _write_task_md(deep / "task.md", "Deep", "not-started",
                       objective="deep obj.")
        deeper = deep / "01-deeper"
        deeper.mkdir()
        _write_task_md(deeper / "task.md", "Deeper", "not-started",
                       objective="deeper obj.")
        return root

    def _client(self, plan_root):
        pytest.importorskip("httpx")
        from fastapi.testclient import TestClient
        plan_dashboard.PLAN_ROOT = plan_root
        return TestClient(plan_dashboard.app)

    def test_nav_is_body_free(self, tmp_path):
        with self._client(self._deep_plan(tmp_path)) as c:
            r = c.get("/nav")
            assert r.status_code == 200
            # Rows for the whole tree, but no body / section markup.
            assert 'class="task-body"' not in r.text
            assert 'class="section-content"' not in r.text
            assert "data-section=" not in r.text
            # Per-node attributes the rest of the system keys off are intact.
            assert 'id="task-01-a"' in r.text
            assert 'data-path="01-a"' in r.text
            assert 'sse-swap="task:01-a"' in r.text
            assert "badge-approved" in r.text

    def test_nav_lazy_loads_deep_children(self, tmp_path):
        with self._client(self._deep_plan(tmp_path)) as c:
            r = c.get("/nav")
            # Depth >=3 children are not inlined: the depth-3 boundary node
            # renders an EMPTY .task-children container (its child node is
            # absent), which the sidebar's markLazyNodes() flags client-side
            # for lazy load. No server-emitted needsLoad flag is shipped.
            assert "needsLoad" not in r.text
            assert 'id="02-b-02-y-01-deep-children"' in r.text
            assert 'id="task-02-b-02-y-01-deep-01-deeper"' not in r.text

    def test_nav_path_returns_deep_children_body_free(self, tmp_path):
        with self._client(self._deep_plan(tmp_path)) as c:
            r = c.get("/nav/02-b/02-y/01-deep")
            assert r.status_code == 200
            assert 'id="task-02-b-02-y-01-deep-01-deeper"' in r.text
            assert 'class="task-body"' not in r.text

    def test_nav_path_missing_404(self, tmp_path):
        with self._client(self._deep_plan(tmp_path)) as c:
            assert c.get("/nav/does-not-exist").status_code == 404

    def test_node_is_body_only(self, tmp_path):
        with self._client(self._deep_plan(tmp_path)) as c:
            r = c.get("/node/01-a")
            assert r.status_code == 200
            assert 'data-section="Objective"' in r.text
            assert 'data-section="Results"' in r.text
            assert '<script type="text/x-markdown">' in r.text
            # No row, no children container.
            assert 'class="task-row"' not in r.text
            assert 'class="task-children"' not in r.text

    def test_node_meta_pills(self, tmp_path):
        with self._client(self._deep_plan(tmp_path)) as c:
            r = c.get("/node/02-b")
            assert 'class="task-meta"' in r.text
            assert "<strong>depends:</strong> 01-a" in r.text

    def test_node_sections_match_full_node(self, tmp_path):
        """The body-only partial emits the same section markup as the full node."""
        import re
        with self._client(self._deep_plan(tmp_path)) as c:
            node = c.get("/node/01-a").text
            full = c.get("/task/").text  # children of root incl. the full 01-a node

            def norm(s):
                return [ln.strip() for ln in s.splitlines() if ln.strip()]

            for sec in ("Objective", "Results"):
                node_block = re.search(
                    rf'<div data-section="{sec}">.*?</script>', node, re.S)
                full_block = re.search(
                    rf'<div data-section="{sec}">.*?</script>', full, re.S)
                assert node_block is not None
                assert full_block is not None
                assert norm(node_block.group(0)) == norm(full_block.group(0))

    def test_node_missing_404(self, tmp_path):
        with self._client(self._deep_plan(tmp_path)) as c:
            assert c.get("/node/does-not-exist").status_code == 404

    def test_existing_routes_unaffected(self, tmp_path):
        with self._client(self._deep_plan(tmp_path)) as c:
            for route in ("/", "/tree", "/dag", "/kanban"):
                assert c.get(route).status_code == 200


class TestIdleShutdown:
    """Unit tests for the idle-shutdown mechanism (task 01).

    Tests drive the pure decision function and the monitor coroutine with
    sub-second timeouts so no test sleeps for real wall-clock seconds.
    """

    # ------------------------------------------------------------------
    # _should_idle_exit — pure function, no side effects
    # ------------------------------------------------------------------

    def test_should_not_exit_when_connections_present(self):
        assert plan_dashboard._should_idle_exit(3, 999.0, 5.0) is False

    def test_should_not_exit_before_timeout(self):
        assert plan_dashboard._should_idle_exit(0, 4.9, 5.0) is False

    def test_should_exit_exactly_at_timeout(self):
        assert plan_dashboard._should_idle_exit(0, 5.0, 5.0) is True

    def test_should_exit_after_timeout(self):
        assert plan_dashboard._should_idle_exit(0, 10.0, 5.0) is True

    # ------------------------------------------------------------------
    # _open_connection_count — reads _worktree_clients
    # ------------------------------------------------------------------

    def test_connection_count_empty(self):
        saved = plan_dashboard._worktree_clients.copy()
        plan_dashboard._worktree_clients.clear()
        try:
            assert plan_dashboard._open_connection_count() == 0
        finally:
            plan_dashboard._worktree_clients.clear()
            plan_dashboard._worktree_clients.update(saved)

    def test_connection_count_with_clients(self):
        import asyncio

        saved = plan_dashboard._worktree_clients.copy()
        plan_dashboard._worktree_clients.clear()
        try:
            q1: asyncio.Queue[str] = asyncio.Queue()
            q2: asyncio.Queue[str] = asyncio.Queue()
            q3: asyncio.Queue[str] = asyncio.Queue()
            plan_dashboard._worktree_clients["wt-a"] = {q1, q2}
            plan_dashboard._worktree_clients["wt-b"] = {q3}
            assert plan_dashboard._open_connection_count() == 3
        finally:
            plan_dashboard._worktree_clients.clear()
            plan_dashboard._worktree_clients.update(saved)

    # ------------------------------------------------------------------
    # _idle_monitor coroutine — driven with sub-second timeout
    # ------------------------------------------------------------------

    def test_monitor_exits_when_no_clients(self):
        """Monitor sets should_exit after idle timeout with zero connections."""
        import asyncio

        class FakeServer:
            should_exit = False

        saved_clients = plan_dashboard._worktree_clients.copy()
        saved_server = plan_dashboard._server
        plan_dashboard._worktree_clients.clear()

        fake = FakeServer()
        plan_dashboard._server = fake  # type: ignore[assignment]
        try:
            asyncio.run(plan_dashboard._idle_monitor(timeout=0.05, poll=0.01))
        finally:
            plan_dashboard._server = saved_server
            plan_dashboard._worktree_clients.clear()
            plan_dashboard._worktree_clients.update(saved_clients)

        assert fake.should_exit is True

    def test_monitor_does_not_exit_while_clients_present(self):
        """Monitor resets its timer while connections are open and does not fire."""
        import asyncio

        class FakeServer:
            should_exit = False

        saved_clients = plan_dashboard._worktree_clients.copy()
        saved_server = plan_dashboard._server

        q: asyncio.Queue[str] = asyncio.Queue()
        plan_dashboard._worktree_clients.clear()
        plan_dashboard._worktree_clients["wt-a"] = {q}

        fake = FakeServer()
        plan_dashboard._server = fake  # type: ignore[assignment]

        async def _run():
            task = asyncio.create_task(
                plan_dashboard._idle_monitor(timeout=0.05, poll=0.01)
            )
            # Let several poll cycles pass with a client present.
            await asyncio.sleep(0.12)
            assert not fake.should_exit, "should not have exited with a client"
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        try:
            asyncio.run(_run())
        finally:
            plan_dashboard._server = saved_server
            plan_dashboard._worktree_clients.clear()
            plan_dashboard._worktree_clients.update(saved_clients)

    def test_monitor_exits_after_last_client_leaves(self):
        """Timer starts (or restarts) once the last client disconnects."""
        import asyncio

        class FakeServer:
            should_exit = False

        saved_clients = plan_dashboard._worktree_clients.copy()
        saved_server = plan_dashboard._server

        q: asyncio.Queue[str] = asyncio.Queue()
        plan_dashboard._worktree_clients.clear()
        plan_dashboard._worktree_clients["wt-a"] = {q}

        fake = FakeServer()
        plan_dashboard._server = fake  # type: ignore[assignment]

        async def _run():
            task = asyncio.create_task(
                plan_dashboard._idle_monitor(timeout=0.05, poll=0.01)
            )
            # Remove the client mid-run; monitor should now count down.
            await asyncio.sleep(0.02)
            plan_dashboard._worktree_clients.clear()
            # Wait for idle window to complete.
            await asyncio.sleep(0.12)
            await task  # monitor coroutine should have returned normally

        try:
            asyncio.run(_run())
        finally:
            plan_dashboard._server = saved_server
            plan_dashboard._worktree_clients.clear()
            plan_dashboard._worktree_clients.update(saved_clients)

        assert fake.should_exit is True


class TestIdleShutdownLifespan:
    """Drive the real serve()/lifespan/SSE path with a sub-second idle timeout.

    These lock in the linchpin behavior the task-01 unit tests verify in
    isolation: the actual ``uvicorn.Server`` self-exits while idle, stays up
    while a client is connected, and the periodic heartbeat prunes a dead SSE
    connection from the open-connection count.
    """

    def _free_port(self):
        import socket as _socket

        s = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
        s.bind(("localhost", 0))
        port = s.getsockname()[1]
        s.close()
        return port

    def test_server_self_exits_when_idle(self, tmp_path):
        """A real serve() with a sub-second IDLE_TIMEOUT and no clients exits."""
        pytest.importorskip("uvicorn")
        import threading

        plan_root = _serve_plan(tmp_path)
        plan_dashboard.PLAN_ROOT = plan_root
        port = self._free_port()

        saved_timeout = plan_dashboard.IDLE_TIMEOUT
        saved_hb = plan_dashboard.HEARTBEAT_INTERVAL
        plan_dashboard.IDLE_TIMEOUT = 0.3
        plan_dashboard.HEARTBEAT_INTERVAL = 0.1
        t = threading.Thread(target=plan_dashboard.serve, args=(port,), daemon=True)
        try:
            t.start()
            # Server must come up, then self-exit within the idle window.
            assert plan_dashboard._wait_for_bind(port, timeout=5.0)
            t.join(timeout=5.0)
            assert not t.is_alive(), "server did not self-exit while idle"
            assert not plan_dashboard._port_serving(port)
        finally:
            plan_dashboard.IDLE_TIMEOUT = saved_timeout
            plan_dashboard.HEARTBEAT_INTERVAL = saved_hb
            if plan_dashboard._server is not None:
                plan_dashboard._server.should_exit = True
            t.join(timeout=5.0)

    def test_server_stays_up_while_client_connected(self, tmp_path):
        """An open /events client holds the server past several idle windows."""
        pytest.importorskip("uvicorn")
        pytest.importorskip("httpx")
        import threading

        import httpx

        plan_root = _serve_plan(tmp_path)
        plan_dashboard.PLAN_ROOT = plan_root
        port = self._free_port()
        url = f"http://localhost:{port}"

        saved_timeout = plan_dashboard.IDLE_TIMEOUT
        saved_hb = plan_dashboard.HEARTBEAT_INTERVAL
        plan_dashboard.IDLE_TIMEOUT = 0.3
        plan_dashboard.HEARTBEAT_INTERVAL = 0.1
        t = threading.Thread(target=plan_dashboard.serve, args=(port,), daemon=True)
        try:
            t.start()
            assert plan_dashboard._wait_for_bind(port, timeout=5.0)

            # Hold an SSE connection open across multiple idle windows.
            with httpx.Client(timeout=5.0) as client:
                with client.stream("GET", f"{url}/events") as resp:
                    assert resp.status_code == 200
                    it = resp.iter_lines()
                    next(it)  # initial heartbeat — connection established
                    time.sleep(1.0)  # >3 idle windows
                    assert t.is_alive(), "server exited while a client was connected"
                    assert plan_dashboard._port_serving(port)

            # Client gone — server now self-exits within an idle window.
            t.join(timeout=5.0)
            assert not t.is_alive(), "server did not exit after client left"
        finally:
            plan_dashboard.IDLE_TIMEOUT = saved_timeout
            plan_dashboard.HEARTBEAT_INTERVAL = saved_hb
            if plan_dashboard._server is not None:
                plan_dashboard._server.should_exit = True
            t.join(timeout=5.0)

    def test_heartbeat_prunes_dead_connection(self, tmp_path):
        """A dropped SSE connection is removed from the count after a heartbeat.

        Opens a streaming /events request, abandons it, and asserts the periodic
        heartbeat write fails and the generator's finally drops the queue so the
        open-connection count returns to zero.
        """
        pytest.importorskip("uvicorn")
        pytest.importorskip("httpx")
        import threading

        import httpx

        plan_root = _serve_plan(tmp_path)
        plan_dashboard.PLAN_ROOT = plan_root
        port = self._free_port()
        url = f"http://localhost:{port}"

        saved_timeout = plan_dashboard.IDLE_TIMEOUT
        saved_hb = plan_dashboard.HEARTBEAT_INTERVAL
        # Keep the server alive long enough to observe the prune, but use a tiny
        # heartbeat so the dead-connection write happens quickly.
        plan_dashboard.IDLE_TIMEOUT = 5.0
        plan_dashboard.HEARTBEAT_INTERVAL = 0.1
        t = threading.Thread(target=plan_dashboard.serve, args=(port,), daemon=True)
        try:
            t.start()
            assert plan_dashboard._wait_for_bind(port, timeout=5.0)

            client = httpx.Client(timeout=5.0)
            stream_cm = client.stream("GET", f"{url}/events")
            resp = stream_cm.__enter__()
            assert resp.status_code == 200
            next(resp.iter_lines())  # establish, registering the queue

            # The connection is registered server-side.
            deadline = time.monotonic() + 3.0
            while plan_dashboard._open_connection_count() == 0 and time.monotonic() < deadline:
                time.sleep(0.05)
            assert plan_dashboard._open_connection_count() >= 1

            # Abandon the connection hard, then wait for a heartbeat to prune it.
            try:
                resp.close()
            except Exception:
                pass
            try:
                stream_cm.__exit__(None, None, None)
            except Exception:
                pass
            client.close()

            deadline = time.monotonic() + 3.0
            while plan_dashboard._open_connection_count() > 0 and time.monotonic() < deadline:
                time.sleep(0.05)
            assert plan_dashboard._open_connection_count() == 0, (
                "dead connection was not pruned from the count"
            )
        finally:
            plan_dashboard.IDLE_TIMEOUT = saved_timeout
            plan_dashboard.HEARTBEAT_INTERVAL = saved_hb
            if plan_dashboard._server is not None:
                plan_dashboard._server.should_exit = True
            t.join(timeout=5.0)

    def test_detached_repeated_abrupt_disconnects_exit_cleanly(self, tmp_path):
        """Detached servers exit after concurrent RSTs and native watcher close.

        The child wraps the real watchfiles watcher with a post-cleanup stall.
        This deterministically reaches Uvicorn's graceful-shutdown race: the
        native watcher has closed, but the watcher task does not finish unless
        the bounded fallback cancels it.  The reviewed unbounded implementation
        leaves the detached child alive and its port open.
        """
        pytest.importorskip("uvicorn")
        pytest.importorskip("watchfiles")
        import struct
        import threading

        plan_root = _serve_plan(tmp_path)
        runner = tmp_path / "detached_dashboard_runner.py"
        runner.write_text(
            "\n".join(
                [
                    "import sys",
                    "from pathlib import Path",
                    f"sys.path.insert(0, {str(SCRIPTS_DIR)!r})",
                    "plan_root, port, marker_path = sys.argv[1:4]",
                    f"source_path = Path({str(SCRIPTS_DIR / 'plan_dashboard.py')!r})",
                    "source = source_path.read_text(encoding='utf-8')",
                    "injection = '''",
                    "original_watch = _watch_worktree",
                    "marker = Path(_test_marker_path)",
                    "async def delayed_finish(wt, stop_event):",
                    "    await original_watch(wt, stop_event)",
                    "    marker.write_text('native watcher closed', encoding='utf-8')",
                    "    while True:",
                    "        try:",
                    "            await asyncio.Event().wait()",
                    "        except asyncio.CancelledError:",
                    (
                        "            marker.write_text('native watcher closed\\\\n"
                        "hard cancel suppressed', encoding='utf-8')"
                    ),
                    "_watch_worktree = delayed_finish",
                    "IDLE_TIMEOUT = 0.3",
                    "HEARTBEAT_INTERVAL = 0.05",
                    "WATCHER_STOP_TIMEOUT = 0.1",
                    "WATCHER_CANCEL_TIMEOUT = 0.1",
                    "WATCHER_PROCESS_EXIT_TIMEOUT = 0.1",
                    "'''",
                    "entry = '\\nif __name__ == \"__main__\":\\n'",
                    "source = source.replace(entry, '\\n' + injection + entry, 1)",
                    (
                        "sys.argv = [str(source_path), 'serve', '--foreground', "
                        "'--root', plan_root, '--port', port, '--no-open']"
                    ),
                    (
                        "scope = {'__name__': '__main__', '__file__': "
                        "str(source_path), '__package__': None, "
                        "'_test_marker_path': marker_path}"
                    ),
                    "exec(compile(source, str(source_path), 'exec'), scope)",
                ]
            ),
            encoding="utf-8",
        )

        def _connect(port):
            client = socket.create_connection(("127.0.0.1", port), timeout=5.0)
            client.sendall(
                b"GET /events HTTP/1.1\r\n"
                + f"Host: 127.0.0.1:{port}\r\n".encode()
                + b"Accept: text/event-stream\r\nConnection: keep-alive\r\n\r\n"
            )
            received = b""
            while b": heartbeat\n\n" not in received:
                received += client.recv(4096)
            return client

        for cycle in range(2):
            port = self._free_port()
            marker = tmp_path / f"native-closed-{cycle}"
            log_path = tmp_path / f"detached-{cycle}.log"
            with log_path.open("wb") as log:
                process = subprocess.Popen(
                    [
                        sys.executable,
                        str(runner),
                        str(plan_root),
                        str(port),
                        str(marker),
                    ],
                    stdin=subprocess.DEVNULL,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
            try:
                assert os.getsid(process.pid) == process.pid
                assert plan_dashboard._wait_for_bind(port, timeout=5.0)

                clients = [_connect(port) for _ in range(8)]
                barrier = threading.Barrier(len(clients))

                def _reset(client):
                    barrier.wait()
                    client.setsockopt(
                        socket.SOL_SOCKET,
                        socket.SO_LINGER,
                        struct.pack("ii", 1, 0),
                    )
                    client.close()

                closers = [
                    threading.Thread(target=_reset, args=(client,))
                    for client in clients
                ]
                for closer in closers:
                    closer.start()
                for closer in closers:
                    closer.join(timeout=2.0)

                deadline = time.monotonic() + 5.0
                while process.poll() is None and time.monotonic() < deadline:
                    time.sleep(0.05)
                assert process.poll() == 0, (
                    f"cycle {cycle}: detached server did not exit; "
                    f"log={log_path.read_text(encoding='utf-8', errors='replace')}"
                )
                assert marker.read_text(encoding="utf-8") == (
                    "native watcher closed\nhard cancel suppressed"
                )
                assert not plan_dashboard._port_serving(port)
                assert not plan_dashboard._pid_alive(process.pid)
            finally:
                if process.poll() is None:
                    process.kill()
                process.wait(timeout=5.0)


class TestRuntimeFileKeying:
    """PID/log files are keyed to the same repo identity as the port."""

    def test_runtime_dir_uses_git_common_dir(self, tmp_path):
        common = tmp_path / "common.git"
        common.mkdir()
        plan_root = tmp_path / "wt" / "superRA"
        plan_root.mkdir(parents=True)
        assert plan_dashboard._runtime_dir(plan_root, str(common)) == common
        assert plan_dashboard._pid_file(plan_root, str(common)) == (
            common / "superra-dashboard.pid"
        )
        assert plan_dashboard._log_file(plan_root, str(common)) == (
            common / "superra-dashboard.log"
        )

    def test_runtime_dir_falls_back_to_plan_root(self, tmp_path):
        plan_root = tmp_path / "superRA"
        plan_root.mkdir()
        assert plan_dashboard._runtime_dir(plan_root, None) == plan_root.resolve()
        assert plan_dashboard._pid_file(plan_root, None) == (
            plan_root.resolve() / "superra-dashboard.pid"
        )

    def test_shared_across_worktrees_of_one_repo(self, tmp_path):
        """Two worktrees of the same repo resolve to one PID file."""
        common = tmp_path / "common.git"
        common.mkdir()
        wt_a = tmp_path / "a" / "superRA"
        wt_b = tmp_path / "b" / "superRA"
        wt_a.mkdir(parents=True)
        wt_b.mkdir(parents=True)
        assert plan_dashboard._pid_file(wt_a, str(common)) == plan_dashboard._pid_file(
            wt_b, str(common)
        )

    def test_default_port_is_deterministic_even_when_busy(self, tmp_path):
        """The port must not walk off a busy port to the next free one.

        A busy deterministic port means a server may already be there to reuse;
        walking to the next free port is what planted a second server per repo.
        The derivation must be a pure function of the repo identity.
        """
        common = tmp_path / "common.git"
        common.mkdir()
        plan_root = tmp_path / "wt" / "superRA"
        plan_root.mkdir(parents=True)
        port = plan_dashboard._default_port(plan_root, str(common))
        assert 8100 <= port <= 8999
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(("127.0.0.1", port))
        listener.listen(1)
        try:
            assert plan_dashboard._default_port(plan_root, str(common)) == port, (
                "a busy port must still be returned, not incremented"
            )
        finally:
            listener.close()


class TestPidHelpers:
    """PID-file read/health helpers used by idempotent launch and stop."""

    def test_read_pid_missing_file(self, tmp_path):
        assert plan_dashboard._read_pid(tmp_path / "nope.pid") is None

    def test_read_pid_garbage(self, tmp_path):
        p = tmp_path / "x.pid"
        p.write_text("not-a-number", encoding="utf-8")
        assert plan_dashboard._read_pid(p) is None

    def test_read_pid_valid(self, tmp_path):
        p = tmp_path / "x.pid"
        p.write_text("12345\n", encoding="utf-8")
        assert plan_dashboard._read_pid(p) == 12345

    def test_read_pid_port_roundtrip(self, tmp_path):
        p = tmp_path / "x.pid"
        plan_dashboard._write_pid_port(p, 12345, 8123)
        assert plan_dashboard._read_pid_port(p) == (12345, 8123)
        assert plan_dashboard._read_pid(p) == 12345

    def test_read_pid_port_legacy_pid_only(self, tmp_path):
        """A legacy pid-only file parses as (pid, None)."""
        p = tmp_path / "x.pid"
        p.write_text("12345\n", encoding="utf-8")
        assert plan_dashboard._read_pid_port(p) == (12345, None)

    def test_pid_alive_self(self):
        assert plan_dashboard._pid_alive(os.getpid()) is True

    def test_pid_alive_dead(self):
        # A very high PID is almost certainly not in use.
        assert plan_dashboard._pid_alive(2_000_000_000) is False

    def test_running_pid_stale_file_cleaned(self, tmp_path):
        """A PID file naming a dead process is removed and None returned."""
        p = tmp_path / "x.pid"
        p.write_text("2000000000", encoding="utf-8")
        port = TestIdleShutdownLifespan()._free_port()  # nothing serving here
        assert plan_dashboard._running_pid(p, port) is None
        assert not p.exists(), "stale PID file should be cleaned up"

    def test_running_pid_alive_but_port_dead(self, tmp_path):
        """A live PID whose port is not serving is treated as stale."""
        p = tmp_path / "x.pid"
        p.write_text(str(os.getpid()), encoding="utf-8")
        port = TestIdleShutdownLifespan()._free_port()
        assert plan_dashboard._running_pid(p, port) is None
        assert not p.exists()

    def test_running_pid_probes_recorded_port(self, tmp_path):
        """Reuse probes the PID file's recorded port, not the passed-in port.

        Mirrors the real case where a server bound a different port than a fresh
        derivation would pick (the deterministic port was occupied at launch).
        """
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.bind(("localhost", 0))
        listener.listen(1)
        recorded_port = listener.getsockname()[1]
        try:
            p = tmp_path / "x.pid"
            plan_dashboard._write_pid_port(p, os.getpid(), recorded_port)
            other_port = TestIdleShutdownLifespan()._free_port()  # nothing serving
            result = plan_dashboard._running_pid(p, other_port)
            assert result == (os.getpid(), recorded_port)
        finally:
            listener.close()


class TestBackgroundLaunch:
    """End-to-end process-management tests for serve_background / stop_background.

    Each test launches a real detached server with a sub-second idle timeout
    (passed to the child via its ``--idle-timeout`` arg) so the test is
    self-cleaning even if an assertion bails early.  Kept few and deterministic
    per planner guidance.
    """

    def test_background_launch_returns_and_writes_pid(self, tmp_path, capsys):
        pytest.importorskip("uvicorn")
        plan_root = _serve_plan(tmp_path)
        common = tmp_path / "common.git"
        common.mkdir()
        port = TestIdleShutdownLifespan()._free_port()
        pid_path = plan_dashboard._pid_file(plan_root, str(common))
        try:
            rc = plan_dashboard.serve_background(
                plan_root, port, str(common), open_browser=False
            )
            assert rc == 0
            assert pid_path.exists(), "PID file should be written"
            pid = plan_dashboard._read_pid(pid_path)
            assert pid is not None and plan_dashboard._pid_alive(pid)
            assert plan_dashboard._port_serving(port)
            assert (
                f"Dashboard running at {plan_dashboard._dashboard_url(port, plan_root)}"
                in capsys.readouterr().out
            )
        finally:
            plan_dashboard.stop_background(plan_root, str(common))

    def test_idempotent_second_launch_reuses_server(self, tmp_path):
        pytest.importorskip("uvicorn")
        plan_root = _serve_plan(tmp_path)
        common = tmp_path / "common.git"
        common.mkdir()
        port = TestIdleShutdownLifespan()._free_port()
        pid_path = plan_dashboard._pid_file(plan_root, str(common))
        try:
            assert plan_dashboard.serve_background(
                plan_root, port, str(common), open_browser=False
            ) == 0
            pid1 = plan_dashboard._read_pid(pid_path)
            # Second launch must reuse, not spawn a duplicate.
            assert plan_dashboard.serve_background(
                plan_root, port, str(common), open_browser=False
            ) == 0
            pid2 = plan_dashboard._read_pid(pid_path)
            assert pid1 == pid2, "second launch spawned a different process"
            assert plan_dashboard._pid_alive(pid1)
        finally:
            plan_dashboard.stop_background(plan_root, str(common))

    def test_background_launch_opens_browser_before_return(self, tmp_path, monkeypatch):
        pytest.importorskip("uvicorn")
        plan_root = _serve_plan(tmp_path)
        common = tmp_path / "common.git"
        common.mkdir()
        port = TestIdleShutdownLifespan()._free_port()
        opened: list[str] = []
        monkeypatch.setattr(plan_dashboard.webbrowser, "open", lambda url: opened.append(url))
        try:
            assert plan_dashboard.serve_background(
                plan_root, port, str(common), open_browser=True
            ) == 0
            assert opened == [plan_dashboard._dashboard_url(port, plan_root)]
        finally:
            plan_dashboard.stop_background(plan_root, str(common))

    def test_idempotent_second_launch_opens_existing_server(self, tmp_path, monkeypatch):
        pytest.importorskip("uvicorn")
        plan_root = _serve_plan(tmp_path)
        common = tmp_path / "common.git"
        common.mkdir()
        port = TestIdleShutdownLifespan()._free_port()
        opened: list[str] = []
        monkeypatch.setattr(plan_dashboard.webbrowser, "open", lambda url: opened.append(url))
        try:
            assert plan_dashboard.serve_background(
                plan_root, port, str(common), open_browser=False
            ) == 0
            assert plan_dashboard.serve_background(
                plan_root, port, str(common), open_browser=True
            ) == 0
            assert opened == [plan_dashboard._dashboard_url(port, plan_root)]
        finally:
            plan_dashboard.stop_background(plan_root, str(common))

    def test_repo_reuse_opens_invoking_worktree(self, tmp_path, monkeypatch, capsys):
        """A repo-shared server launched from A must reopen scoped to B."""
        pytest.importorskip("uvicorn")
        (tmp_path / "worktree-a").mkdir()
        (tmp_path / "worktree-b").mkdir()
        plan_a = _serve_plan(tmp_path / "worktree-a")
        plan_b = _serve_plan(tmp_path / "worktree-b")
        common = tmp_path / "common.git"
        common.mkdir()
        port = TestIdleShutdownLifespan()._free_port()
        opened: list[str] = []
        monkeypatch.setattr(plan_dashboard.webbrowser, "open", lambda url: opened.append(url))
        try:
            assert plan_dashboard.serve_background(
                plan_a, port, str(common), open_browser=False
            ) == 0
            capsys.readouterr()
            assert plan_dashboard.serve_background(
                plan_b, port, str(common), open_browser=True
            ) == 0
            expected = plan_dashboard._dashboard_url(port, plan_b)
            assert opened == [expected]
            assert f"Dashboard already running at {expected}" in capsys.readouterr().out
        finally:
            plan_dashboard.stop_background(plan_a, str(common))

    def test_scoped_url_encodes_collision_safe_selector(self, tmp_path, monkeypatch):
        plan_root = tmp_path / "shared name" / "superRA"
        plan_root.mkdir(parents=True)
        monkeypatch.setattr(
            plan_dashboard,
            "_discovered_worktree_map",
            lambda: {"parent one/shared name": plan_root},
        )
        assert plan_dashboard._dashboard_url(8123, plan_root) == (
            "http://localhost:8123/?wt=parent%20one%2Fshared%20name"
        )

    def test_stop_terminates_and_removes_pid(self, tmp_path):
        pytest.importorskip("uvicorn")
        plan_root = _serve_plan(tmp_path)
        common = tmp_path / "common.git"
        common.mkdir()
        port = TestIdleShutdownLifespan()._free_port()
        pid_path = plan_dashboard._pid_file(plan_root, str(common))
        assert plan_dashboard.serve_background(
            plan_root, port, str(common), open_browser=False
        ) == 0
        pid = plan_dashboard._read_pid(pid_path)
        rc = plan_dashboard.stop_background(plan_root, str(common))
        assert rc == 0
        assert not pid_path.exists(), "PID file should be removed on stop"
        # Process should be gone.
        deadline = time.monotonic() + 5.0
        while plan_dashboard._pid_alive(pid) and time.monotonic() < deadline:
            time.sleep(0.05)
        assert not plan_dashboard._pid_alive(pid)
        assert not plan_dashboard._port_serving(port)

    def test_stop_noop_when_nothing_running(self, tmp_path):
        plan_root = _serve_plan(tmp_path)
        common = tmp_path / "common.git"
        common.mkdir()
        # No server, no PID file — clean no-op.
        assert plan_dashboard.stop_background(plan_root, str(common)) == 0

    def test_stale_pid_file_does_not_block_launch(self, tmp_path):
        pytest.importorskip("uvicorn")
        plan_root = _serve_plan(tmp_path)
        common = tmp_path / "common.git"
        common.mkdir()
        port = TestIdleShutdownLifespan()._free_port()
        pid_path = plan_dashboard._pid_file(plan_root, str(common))
        # Plant a stale PID file (dead process).
        pid_path.write_text("2000000000", encoding="utf-8")
        try:
            rc = plan_dashboard.serve_background(
                plan_root, port, str(common), open_browser=False
            )
            assert rc == 0, "stale PID file should not block a fresh launch"
            pid = plan_dashboard._read_pid(pid_path)
            assert pid is not None and pid != 2000000000
            assert plan_dashboard._pid_alive(pid)
        finally:
            plan_dashboard.stop_background(plan_root, str(common))

    def test_bind_failure_surfaces_nonzero(self, tmp_path):
        """A child that cannot bind its port → non-zero exit, no PID file.

        Occupies a port with a bound-but-not-listening socket: uvicorn cannot
        bind it (address in use) and the child exits, while TCP connects are
        refused so the supervisor's bind poll never sees a false "serving".  The
        supervisor must time out, surface the error, and return non-zero rather
        than leaving a dead background process.
        """
        pytest.importorskip("uvicorn")
        plan_root = _serve_plan(tmp_path)
        common = tmp_path / "common.git"
        common.mkdir()
        # Bind but do not listen → port is occupied, connects are refused.
        # Bind loopback to match the child's default --host 127.0.0.1 bind, so
        # the child genuinely collides (a 0.0.0.0 blocker would not block a later
        # 127.0.0.1 bind on macOS, letting the child bind loopback and "succeed").
        blocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        blocker.bind(("127.0.0.1", 0))
        port = blocker.getsockname()[1]
        assert not plan_dashboard._port_serving(port), "blocker should refuse connects"
        try:
            rc = plan_dashboard.serve_background(
                plan_root, port, str(common), open_browser=False, bind_timeout=3.0
            )
            assert rc != 0, "bind failure should produce a non-zero exit code"
            # No PID file left naming a dead background process.
            assert not plan_dashboard._pid_file(plan_root, str(common)).exists()
        finally:
            blocker.close()
            plan_dashboard.stop_background(plan_root, str(common))

    def test_background_server_self_exits_when_idle(self, tmp_path):
        """A backgrounded server with no clients self-exits within the idle window.

        Launches a real detached child with a short ``idle_timeout`` so the
        self-exit happens in a couple of seconds, then asserts the process and
        port are gone without an explicit stop.  This proves background-default
        is safe to leak: the detached server self-cleans like any other.
        """
        pytest.importorskip("uvicorn")
        plan_root = _serve_plan(tmp_path)
        common = tmp_path / "common.git"
        common.mkdir()
        port = TestIdleShutdownLifespan()._free_port()
        pid_path = plan_dashboard._pid_file(plan_root, str(common))
        try:
            assert plan_dashboard.serve_background(
                plan_root, port, str(common), open_browser=False, idle_timeout=0.5
            ) == 0
            pid = plan_dashboard._read_pid(pid_path)
            assert pid is not None
            # Genuinely detached and reachable from the parent process.
            assert plan_dashboard._port_serving(port)
            # No client opened — it self-exits within the (shrunk) idle window.
            deadline = time.monotonic() + 10.0
            while plan_dashboard._pid_alive(pid) and time.monotonic() < deadline:
                time.sleep(0.1)
            assert not plan_dashboard._pid_alive(pid), "background server did not self-exit"
            assert not plan_dashboard._port_serving(port)
        finally:
            plan_dashboard.stop_background(plan_root, str(common))

    def test_probe_reuse_when_pid_file_missing(self, tmp_path):
        """A live server with no PID file is reused via /healthz, not duplicated.

        Reproduces the core duplicate-spawn: a server is genuinely serving the
        repo port but this launch sees no valid PID file (a foreground launch
        writes none; a background file can be lost or removed while the process
        lives).  The relaunch must recover the running server via its /healthz
        identity, repair the PID file, and spawn no second process.
        """
        pytest.importorskip("uvicorn")
        plan_root = _serve_plan(tmp_path)
        common = tmp_path / "common.git"
        common.mkdir()
        port = TestIdleShutdownLifespan()._free_port()
        pid_path = plan_dashboard._pid_file(plan_root, str(common))
        try:
            assert plan_dashboard.serve_background(
                plan_root, port, str(common), open_browser=False
            ) == 0
            pid1 = plan_dashboard._read_pid(pid_path)
            assert pid1 is not None and plan_dashboard._pid_alive(pid1)
            # Simulate the missing/stale PID file while the server stays alive.
            pid_path.unlink()
            rc = plan_dashboard.serve_background(
                plan_root, port, str(common), open_browser=False
            )
            assert rc == 0, "probe reuse should succeed without spawning"
            assert pid_path.exists(), "probe reuse must repair the PID file"
            pid2 = plan_dashboard._read_pid(pid_path)
            assert pid2 == pid1, "reuse must recover the running PID, not spawn a duplicate"
            assert plan_dashboard._pid_alive(pid1)
        finally:
            plan_dashboard.stop_background(plan_root, str(common))

    def test_lost_race_terminates_child_and_reuses_winner(self, tmp_path, monkeypatch):
        """A launch that loses the concurrent bind race reuses the winner and
        leaves no lingering child.

        Both reuse layers miss (no server found pre-spawn), the child is spawned,
        but by the time the port serves a dashboard a *different* PID answers
        /healthz — a concurrent launch won.  The redundant child must be
        terminated (not left alive-but-not-listening) and the winner reused.
        """
        plan_root = _serve_plan(tmp_path)
        common = tmp_path / "common.git"
        common.mkdir()
        port = 34567
        pid_path = plan_dashboard._pid_file(plan_root, str(common))

        class _FakeProc:
            pid = 55555

            def poll(self):
                return None  # our child is alive (a lingering loser)

        winner_repo = plan_dashboard._repo_id(str(common), plan_root)
        monkeypatch.setattr(plan_dashboard, "_discovered_worktree_map", lambda: {})
        monkeypatch.setattr(plan_dashboard.subprocess, "Popen", lambda cmd, **kw: _FakeProc())
        monkeypatch.setattr(plan_dashboard, "_running_pid", lambda *a, **k: None)
        monkeypatch.setattr(plan_dashboard, "_probe_dashboard", lambda *a, **k: None)
        # The winner is our own repo (same repo id) — a same-repo race, so we
        # reuse it rather than spawn a second server.
        monkeypatch.setattr(
            plan_dashboard, "_wait_for_dashboard", lambda *a, **k: (77777, False, winner_repo)
        )
        terminated: list[int] = []
        monkeypatch.setattr(
            plan_dashboard, "_terminate", lambda pid, **k: (terminated.append(pid), True)[1]
        )

        rc = plan_dashboard.serve_background(
            plan_root, port, str(common), open_browser=False
        )
        assert rc == 0, "the race loser should reuse the winner and succeed"
        assert 55555 in terminated, "the redundant losing child must be terminated"
        assert plan_dashboard._read_pid(pid_path) == 77777, "PID file should name the winner"

    def test_failed_child_does_not_linger(self, tmp_path, monkeypatch):
        """When no dashboard comes up, a still-alive child is terminated, not left."""
        plan_root = _serve_plan(tmp_path)
        common = tmp_path / "common.git"
        common.mkdir()

        class _FakeProc:
            pid = 55555

            def poll(self):
                return None  # child alive but never brought the dashboard up

        monkeypatch.setattr(plan_dashboard, "_discovered_worktree_map", lambda: {})
        monkeypatch.setattr(plan_dashboard.subprocess, "Popen", lambda cmd, **kw: _FakeProc())
        monkeypatch.setattr(plan_dashboard, "_running_pid", lambda *a, **k: None)
        monkeypatch.setattr(plan_dashboard, "_probe_dashboard", lambda *a, **k: None)
        monkeypatch.setattr(plan_dashboard, "_wait_for_dashboard", lambda *a, **k: None)
        terminated: list[int] = []
        monkeypatch.setattr(
            plan_dashboard, "_terminate", lambda pid, **k: (terminated.append(pid), True)[1]
        )

        rc = plan_dashboard.serve_background(
            plan_root, 34568, str(common), open_browser=False
        )
        assert rc == 1
        assert 55555 in terminated, "a child that never serves must not be left lingering"

    def test_task_mode_launch_does_not_reuse_doc_mode_server(self, tmp_path, monkeypatch):
        """A task-mode launch must never adopt a same-repo --doc-mode server.

        The PID file is per-repo, not per-mode, so a second server can't coexist:
        the repo-aware walk detects our repo already serving the port in the
        other mode and reports a conflict without spawning or reusing.
        """
        plan_root = _serve_plan(tmp_path)
        common = tmp_path / "common.git"
        common.mkdir()
        port = 34569
        repo = plan_dashboard._repo_id(str(common), plan_root)
        # Our repo's doc-mode dashboard is present per both reuse layers.
        monkeypatch.setattr(plan_dashboard, "_running_pid", lambda *a, **k: (12321, port))
        monkeypatch.setattr(
            plan_dashboard, "_probe_dashboard", lambda *a, **k: (12321, True, repo)
        )
        spawned: list[list[str]] = []

        def _fake_popen(cmd, **kw):
            spawned.append(cmd)
            raise AssertionError("must not spawn a conflicting cross-mode server")

        monkeypatch.setattr(plan_dashboard.subprocess, "Popen", _fake_popen)

        rc = plan_dashboard.serve_background(
            plan_root, port, str(common), doc_mode=False, open_browser=False
        )
        assert not spawned, "task-mode launch must not spawn atop a doc-mode server"
        assert rc == 1, "a same-repo cross-mode conflict should be reported"

    def test_different_repo_on_port_advances_to_next_free_port(self, tmp_path, monkeypatch):
        """A *different* repo colliding on our start port must not be reused or
        killed: probe reuse requires a repo-id match, so our launch advances to
        the next free port and spawns its own server there.
        """
        plan_root = _serve_plan(tmp_path)
        common = tmp_path / "common.git"
        common.mkdir()
        base = 34600
        our_repo = plan_dashboard._repo_id(str(common), plan_root)

        # A different repo's dashboard holds the start port; the next port is free.
        def _fake_probe(p, *a, **k):
            if p == base:
                return (99999, False, "a-different-repo-id")
            return None

        monkeypatch.setattr(plan_dashboard, "_probe_dashboard", _fake_probe)
        monkeypatch.setattr(plan_dashboard, "_running_pid", lambda *a, **k: None)
        # The start port is occupied (by the other repo); adjacent ports are free.
        monkeypatch.setattr(plan_dashboard, "_port_serving", lambda p: p == base)

        spawned: list[list[str]] = []

        class _FakeProc:
            pid = 55555

            def poll(self):
                return None

        def _fake_popen(cmd, **kw):
            spawned.append(cmd)
            return _FakeProc()

        monkeypatch.setattr(plan_dashboard, "_discovered_worktree_map", lambda: {})
        monkeypatch.setattr(plan_dashboard.subprocess, "Popen", _fake_popen)
        monkeypatch.setattr(
            plan_dashboard, "_wait_for_dashboard", lambda *a, **k: (55555, False, our_repo)
        )
        terminated: list[int] = []
        monkeypatch.setattr(
            plan_dashboard, "_terminate", lambda pid, **k: (terminated.append(pid), True)[1]
        )

        pid_path = plan_dashboard._pid_file(plan_root, str(common))
        rc = plan_dashboard.serve_background(
            plan_root, base, str(common), open_browser=False
        )
        assert rc == 0
        assert spawned, "our launch must spawn its own server"
        cmd = spawned[0]
        assert cmd[cmd.index("--port") + 1] == str(base + 1), (
            "must take the next free port, not the colliding repo's start port"
        )
        assert 99999 not in terminated, "the other repo's server must not be killed"
        assert plan_dashboard._read_pid(pid_path) == 55555

    def test_colliding_repos_each_get_own_server(self, tmp_path):
        """End-to-end: two different repos sharing a start port each run their
        own server; the second does not adopt (or later kill) the first's.
        """
        pytest.importorskip("uvicorn")
        (tmp_path / "a").mkdir()
        (tmp_path / "b").mkdir()
        plan_a = _serve_plan(tmp_path / "a")
        plan_b = _serve_plan(tmp_path / "b")
        common_a = tmp_path / "a.git"
        common_a.mkdir()
        common_b = tmp_path / "b.git"
        common_b.mkdir()
        port = TestIdleShutdownLifespan()._free_port()
        pid_a = plan_dashboard._pid_file(plan_a, str(common_a))
        pid_b = plan_dashboard._pid_file(plan_b, str(common_b))
        try:
            # Repo A takes the shared start port.
            assert plan_dashboard.serve_background(
                plan_a, port, str(common_a), open_browser=False
            ) == 0
            a_pid = plan_dashboard._read_pid(pid_a)
            assert a_pid is not None and plan_dashboard._pid_alive(a_pid)
            a_probe = plan_dashboard._probe_dashboard(port)
            assert a_probe is not None
            a_repo = a_probe[2]

            # Repo B collides on the same start port. It must not reuse A; it
            # walks to an adjacent free port and spawns its own server.
            assert plan_dashboard.serve_background(
                plan_b, port, str(common_b), open_browser=False
            ) == 0
            b_pid, b_port = plan_dashboard._read_pid_port(pid_b)
            assert b_pid is not None and b_pid != a_pid, "B must not adopt A's server"
            assert b_port != port, "B must bind an adjacent port, not A's"
            assert plan_dashboard._pid_alive(a_pid), "A must be untouched by B's launch"
            # A still serves its own identity on the shared port.
            a_probe2 = plan_dashboard._probe_dashboard(port)
            assert a_probe2 is not None and a_probe2[0] == a_pid and a_probe2[2] == a_repo
            # B serves its own, distinct identity on its own port.
            b_probe = plan_dashboard._probe_dashboard(b_port)
            assert b_probe is not None and b_probe[0] == b_pid and b_probe[2] != a_repo
        finally:
            plan_dashboard.stop_background(plan_a, str(common_a))
            plan_dashboard.stop_background(plan_b, str(common_b))


# ---------------------------------------------------------------------------
# Canonical path basis: paths are relative to the resolved root, with forest
# support (regression for the descend bug that dropped a leading segment when
# <root>/task.md was absent).
# ---------------------------------------------------------------------------


@pytest.fixture
def forest_root(tmp_path):
    """A rootless forest: a superRA/ dir with no umbrella task.md, holding two
    independent top-level trees, each with descendants."""
    root = tmp_path / "superRA"
    root.mkdir()

    # Tree A: 01-alpha with a child and grandchild.
    a = root / "01-alpha"
    a.mkdir()
    _write_task_md(a / "task.md", "Alpha", "in-progress", objective="Alpha root.")
    a1 = a / "01-model"
    a1.mkdir()
    _write_task_md(a1 / "task.md", "Alpha Model", "not-started", objective="Model.")
    a1a = a1 / "01-derive"
    a1a.mkdir()
    _write_task_md(a1a / "task.md", "Derive", "not-started", objective="Derive it.")

    # Tree B: 02-beta with a child.
    b = root / "02-beta"
    b.mkdir()
    _write_task_md(b / "task.md", "Beta", "not-started", objective="Beta root.")
    b1 = b / "01-data"
    b1.mkdir()
    _write_task_md(b1 / "task.md", "Beta Data", "not-started", objective="Data.")

    return root


class TestServeBindHost:
    """The unauthenticated server must bind loopback by default and only open up
    on an explicit ``--host`` opt-in.  Background-by-default makes an all-
    interfaces bind a long-lived ambient exposure (file reads via /files, the
    full task tree via /export, disk writes via the comment routes), so the
    default must be 127.0.0.1.  These pin the bound host without standing up a
    real socket by capturing the ``uvicorn.Config`` that ``serve()`` builds."""

    def _capture_config(self, monkeypatch, **serve_kwargs):
        pytest.importorskip("uvicorn")
        import uvicorn

        captured = {}

        class _FakeServer:
            def __init__(self, config):
                captured["host"] = config.host

            def run(self):
                pass  # do not actually bind

        monkeypatch.setattr(uvicorn, "Server", _FakeServer)
        plan_dashboard.serve(12345, **serve_kwargs)
        return captured["host"]

    def test_serve_defaults_to_loopback(self, monkeypatch):
        assert self._capture_config(monkeypatch) == "127.0.0.1"

    def test_serve_honors_explicit_host(self, monkeypatch):
        assert self._capture_config(monkeypatch, host="0.0.0.0") == "0.0.0.0"

    def test_background_spawn_forwards_host(self, tmp_path, monkeypatch):
        """serve_background must pass its --host through to the detached child so
        the background path's bind matches the foreground path's."""
        pytest.importorskip("uvicorn")
        plan_root = _serve_plan(tmp_path)
        common = tmp_path / "common.git"
        common.mkdir()
        captured = {}

        class _FakeProc:
            pid = 999999

            def poll(self):
                return None

        def _fake_popen(cmd, **kw):
            captured["cmd"] = cmd
            return _FakeProc()

        monkeypatch.setattr(plan_dashboard, "_discovered_worktree_map", lambda: {})
        monkeypatch.setattr(plan_dashboard.subprocess, "Popen", _fake_popen)
        # No pre-existing server (layer 1/2 reuse skipped), and the post-spawn
        # /healthz wait reports our fake child as the winner so no real poll runs.
        monkeypatch.setattr(plan_dashboard, "_running_pid", lambda *a, **k: None)
        monkeypatch.setattr(plan_dashboard, "_probe_dashboard", lambda *a, **k: None)
        monkeypatch.setattr(
            plan_dashboard, "_wait_for_dashboard", lambda *a, **k: (999999, False, None)
        )
        plan_dashboard.serve_background(
            plan_root, 23456, str(common), host="0.0.0.0", open_browser=False
        )
        cmd = captured["cmd"]
        assert "--host" in cmd and cmd[cmd.index("--host") + 1] == "0.0.0.0"

    def test_serve_cli_default_host_is_loopback(self):
        """The CLI surface defaults --host to loopback (string assertion on the
        argparse default, mirroring the help text)."""
        ns = plan_dashboard.parse_args(["serve"])
        assert ns.host == "127.0.0.1"

    def test_foreground_emits_and_opens_scoped_url(self, tmp_path, monkeypatch, capsys):
        plan_root = _serve_plan(tmp_path)
        port = 23457
        opened: list[str] = []
        monkeypatch.setattr(plan_dashboard, "PLAN_ROOT", plan_dashboard.PLAN_ROOT)
        monkeypatch.setattr(plan_dashboard, "DOC_MODE", plan_dashboard.DOC_MODE)
        monkeypatch.setattr(plan_dashboard, "REPO_ID", plan_dashboard.REPO_ID)
        monkeypatch.setattr(plan_dashboard, "get_git_common_dir", lambda: None)
        monkeypatch.setattr(plan_dashboard, "serve", lambda *args, **kwargs: None)
        monkeypatch.setattr(plan_dashboard, "_open_browser_async", opened.append)

        plan_dashboard.main([
            "serve", "--foreground", "--root", str(plan_root), "--port", str(port),
        ])

        expected = plan_dashboard._dashboard_url(port, plan_root)
        assert opened == [expected]
        assert f"Starting dashboard at {expected}" in capsys.readouterr().out
