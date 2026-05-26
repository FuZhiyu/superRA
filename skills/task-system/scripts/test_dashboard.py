#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pytest", "httpx", "pyyaml", "fastapi", "jinja2"]
# ///
"""Tests for the live dashboard server, comments system, SSE, and templates."""

from __future__ import annotations

import asyncio
import json
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
    updated = kwargs.get("updated", "2026-01-01")

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
        f"tags: {tags_yaml}\ncreated: {created}\nupdated: {updated}\n---\n\n{body}"
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


# ---------------------------------------------------------------------------
# TestServerRoutes
# ---------------------------------------------------------------------------


class TestServerRoutes:
    def test_index_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "Test Project" in resp.text

    def test_index_contains_task_nodes(self, client):
        resp = client.get("/")
        assert "task-node" in resp.text
        assert "First Task" in resp.text

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

    def test_template_escapes_closing_template_tag(self, plan_root):
        """</template> in markdown content should be escaped."""
        plan_dashboard.PLAN_ROOT = plan_root
        plan_dashboard._project_root = str(plan_root.parent)

        # Write a task whose body contains </template>
        task_md = plan_root / "01-first" / "task.md"
        content = task_md.read_text()
        content = content.replace("Complete step 1.", "Use </template> tag in code.")
        task_md.write_text(content)
        plan_dashboard.rebuild_tree()

        task = plan_dashboard._task_index["01-first"]
        html = plan_dashboard._render_task_node(task)
        # The raw </template> should be escaped
        assert "&lt;/template&gt;" in html

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
