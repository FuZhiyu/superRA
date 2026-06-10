#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pytest", "httpx", "pyyaml", "fastapi", "jinja2"]
# ///
"""Tests for the live dashboard server, comments system, SSE, and templates."""

from __future__ import annotations

import asyncio
import json
import re
import shutil
import subprocess
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

import _task_io
import plan_dashboard
from _comments import (
    add_comment,
    delete_comment,
    load_comments,
    resolve_anchors,
    resolve_comment,
    save_comments,
    split_into_blocks,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_task_md(path: Path, title: str, status: str, **kwargs):
    """Write a task.md file with the unified status model."""
    depends_on = kwargs.get("depends_on", [])
    tags = kwargs.get("tags", [])
    objective = kwargs.get("objective", "")
    results = kwargs.get("results", "")
    created = kwargs.get("created", "2026-01-01")

    if depends_on:
        deps_yaml = "\n" + "".join(f"  - {d}\n" for d in depends_on)
    else:
        deps_yaml = " []"
    if tags:
        tags_yaml = "[" + ", ".join(tags) + "]"
    else:
        tags_yaml = "[]"

    body = f"## Objective\n\n{objective}\n"
    if results:
        body += f"\n## Results\n\n{results}\n"

    content = (
        f'---\ntitle: "{title}"\nstatus: {status}\n'
        f"depends_on:{deps_yaml}\n"
        f"tags: {tags_yaml}\ncreated: {created}\n---\n\n{body}"
    )
    path.write_text(content, encoding="utf-8")


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
                   tags=["data"],
                   objective="Complete step 1.",
                   results="### Key Findings\n- Found 100 rows")

    d2 = root / "02-second"
    d2.mkdir()
    _write_task_md(d2 / "task.md", "Second Task", "not-started",
                   depends_on=["01-first"], tags=["analysis"],
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
# from the ``?wt=<name>`` query param (worktree id = directory basename).  A
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
        assert "vscode://file/' + RESOLVED_ROOT + '/'" in fn
        assert "ROOT_PREFIX ? ROOT_PREFIX + '/' : ''" in fn
        assert "/superRA/" not in fn  # no hardcoded path segment
        # renderMarkdown in-body base also derives from RESOLVED_ROOT/ROOT_PREFIX.
        assert "vscode://file/' + RESOLVED_ROOT + '/' + filePath" in BASE_HTML
        assert "var repoPathPrefix = rootRel + taskDirRel;" in BASE_HTML
        # The old hardcoded prefixes are gone from the builders.
        assert "'superRA/' + path + '/task.md'" not in BASE_HTML
        assert "pathPrefix = taskPath ? 'superRA/'" not in BASE_HTML

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
        # The breadcrumb builds a clickable `root` crumb that ascends via
        # setActive('') — the entry point that returns to the container.
        assert "addCrumb('root', '', segs.length === 0)" in BASE_HTML

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
