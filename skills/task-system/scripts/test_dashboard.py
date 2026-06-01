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
    root = tmp_path / ".plan"
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
    root = tmp_path / ".plan"
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

    def test_kanban_returns_6_columns(self, client):
        resp = client.get("/kanban")
        assert resp.status_code == 200
        # Each column has a kanban-col-header; count those for the 6 statuses
        assert resp.text.count("kanban-col-header") == 6

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

    def test_events_sse_generator_yields_heartbeat(self):
        """The SSE event_generator yields a heartbeat as its first message.

        We test the generator directly rather than through the HTTP layer
        to avoid blocking on the long-lived stream.
        """
        loop = asyncio.new_event_loop()
        queue: asyncio.Queue[str] = asyncio.Queue(maxsize=256)

        async def _test():
            # Simulate what the /events endpoint does
            plan_dashboard._sse_clients.add(queue)
            try:
                # The generator yields heartbeat first, then blocks on queue
                gen = plan_dashboard.sse_events()
                resp = await gen
                # resp is a StreamingResponse; get the body iterator
                body_iter = resp.body_iterator
                first = await body_iter.__anext__()
                assert "heartbeat" in first
                # Verify content type
                assert resp.media_type == "text/event-stream"
            finally:
                plan_dashboard._sse_clients.discard(queue)

        try:
            loop.run_until_complete(_test())
        finally:
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
    def test_broadcast_single_line(self):
        """Single-line data gets proper SSE framing."""
        loop = asyncio.new_event_loop()
        queue: asyncio.Queue[str] = asyncio.Queue()
        plan_dashboard._sse_clients.add(queue)
        try:
            loop.run_until_complete(plan_dashboard._broadcast("test-event", "hello"))
            msg = loop.run_until_complete(asyncio.wait_for(queue.get(), timeout=1))
            assert msg.startswith("event: test-event\n")
            assert "data: hello\n" in msg
        finally:
            plan_dashboard._sse_clients.discard(queue)
            loop.close()

    def test_broadcast_multiline(self):
        """Multi-line data gets per-line data: prefix per SSE spec."""
        loop = asyncio.new_event_loop()
        queue: asyncio.Queue[str] = asyncio.Queue()
        plan_dashboard._sse_clients.add(queue)
        try:
            loop.run_until_complete(
                plan_dashboard._broadcast("task:foo", "line1\nline2\nline3")
            )
            msg = loop.run_until_complete(asyncio.wait_for(queue.get(), timeout=1))
            assert "event: task:foo\n" in msg
            assert "data: line1\n" in msg
            assert "data: line2\n" in msg
            assert "data: line3\n" in msg
        finally:
            plan_dashboard._sse_clients.discard(queue)
            loop.close()

    def test_event_naming_task_path(self):
        """Per-task events use event: task:{path} naming."""
        loop = asyncio.new_event_loop()
        queue: asyncio.Queue[str] = asyncio.Queue()
        plan_dashboard._sse_clients.add(queue)
        try:
            loop.run_until_complete(
                plan_dashboard._broadcast("task:my/nested/path", "<div>html</div>")
            )
            msg = loop.run_until_complete(asyncio.wait_for(queue.get(), timeout=1))
            assert msg.startswith("event: task:my/nested/path\n")
        finally:
            plan_dashboard._sse_clients.discard(queue)
            loop.close()

    def test_broadcast_drops_full_queue(self):
        """When a client queue is full, the client is removed."""
        loop = asyncio.new_event_loop()
        queue: asyncio.Queue[str] = asyncio.Queue(maxsize=1)
        # Fill the queue
        queue.put_nowait("filler")
        plan_dashboard._sse_clients.add(queue)
        try:
            # This should not raise; the full queue gets dropped
            loop.run_until_complete(plan_dashboard._broadcast("e", "data"))
            assert queue not in plan_dashboard._sse_clients
        finally:
            plan_dashboard._sse_clients.discard(queue)
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

    def test_kanban_has_6_status_columns(self, plan_root):
        plan_dashboard.PLAN_ROOT = plan_root
        plan_dashboard._project_root = str(plan_root.parent)
        plan_dashboard.rebuild_tree()
        env = plan_dashboard._get_jinja_env()
        template = env.get_template("kanban.html")
        all_tasks = _task_io.collect_all_tasks(plan_dashboard._root_task)
        html = template.render(all_tasks=all_tasks)
        assert html.count("kanban-col-header") == 6

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
