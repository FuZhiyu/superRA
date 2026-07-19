#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pytest", "httpx", "pyyaml", "fastapi", "jinja2"]
# ///
"""Tests for state-preservation server-side behavior.

Covers:
- rebuild_task() children_changed detection
- _render_nav_node() depth parameter behavior
- Watcher decision logic (broadcast event classification)
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import plan_dashboard


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_task_md(path: Path, title: str, status: str, **kwargs):
    """Write a v2-format task.md file."""
    review_status = kwargs.get("review_status", "~")
    integration_status = kwargs.get("integration_status", "~")
    depends_on = kwargs.get("depends_on", [])
    objective = kwargs.get("objective", "")
    results = kwargs.get("results", "")
    body_text = kwargs.get("body_text", "")

    if depends_on:
        deps_yaml = "\n" + "".join(f"  - {d}\n" for d in depends_on)
    else:
        deps_yaml = " []"

    body = ""
    if body_text:
        body = body_text
    else:
        body = f"## Objective\n\n{objective}\n"
        if results:
            body += f"\n## Results\n\n{results}\n"

    content = (
        f'---\ntitle: "{title}"\nstatus: {status}\nreview_status: {review_status}\n'
        f"integration_status: {integration_status}\ndepends_on:{deps_yaml}\n---\n\n{body}"
    )
    path.write_text(content, encoding="utf-8")


def _init_dashboard(plan_root: Path):
    """Point the dashboard module at a plan root and build the tree."""
    plan_dashboard.PLAN_ROOT = plan_root
    plan_dashboard._project_root = str(plan_root.resolve().parent)
    plan_dashboard._jinja_env = None
    plan_dashboard.rebuild_tree()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def plan_root(tmp_path):
    """Create a minimal plan tree: root + 3 leaf tasks."""
    root = tmp_path / "superRA"
    root.mkdir()

    _write_task_md(root / "task.md", "Test Project", "not-started",
                   objective="A test plan.")

    d1 = root / "01-first"
    d1.mkdir()
    _write_task_md(d1 / "task.md", "First Task", "approved",
                   review_status="approved", tags=["data"],
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
def dashboard(plan_root):
    """Initialize dashboard state for plan_root. Yields plan_root for convenience."""
    _init_dashboard(plan_root)
    return plan_root


# ---------------------------------------------------------------------------
# TestRebuildTaskChildrenChanged
# ---------------------------------------------------------------------------


class TestRebuildTaskChildrenChanged:
    """Test rebuild_task() return values for children_changed flag."""

    def test_content_only_change_returns_false(self, dashboard):
        """Editing task.md text without adding/removing children: children_changed=False."""
        task_md = dashboard / "01-first" / "task.md"
        content = task_md.read_text()
        task_md.write_text(content.replace("First Task", "Edited First Task"))

        updated, children_changed = plan_dashboard.rebuild_task("01-first")
        assert updated is not None
        assert updated.title == "Edited First Task"
        assert children_changed is False

    def test_new_child_added_returns_true(self, dashboard):
        """Adding a new child directory: children_changed=True."""
        child = dashboard / "01-first" / "sub-a"
        child.mkdir()
        _write_task_md(child / "task.md", "New Sub", "not-started")

        updated, children_changed = plan_dashboard.rebuild_task("01-first")
        assert updated is not None
        assert children_changed is True
        assert any(c.path == "01-first/sub-a" for c in updated.children)

    def test_child_removed_returns_true(self, dashboard):
        """Removing a child directory: children_changed=True."""
        # First add a child
        child = dashboard / "01-first" / "sub-a"
        child.mkdir()
        _write_task_md(child / "task.md", "Doomed Sub", "not-started")
        plan_dashboard.rebuild_tree()  # re-initialize to know about the child

        # Remove it
        (child / "task.md").unlink()
        child.rmdir()

        updated, children_changed = plan_dashboard.rebuild_task("01-first")
        assert updated is not None
        assert children_changed is True
        assert len(updated.children) == 0

    def test_child_removed_cleans_index(self, dashboard):
        """Removing a child also removes it from the flat index."""
        child = dashboard / "02-second" / "nested"
        child.mkdir()
        _write_task_md(child / "task.md", "Nested", "not-started")
        plan_dashboard.rebuild_tree()
        assert "02-second/nested" in plan_dashboard._task_index

        (child / "task.md").unlink()
        child.rmdir()
        plan_dashboard.rebuild_task("02-second")
        assert "02-second/nested" not in plan_dashboard._task_index

    def test_deleted_task_returns_none(self, dashboard):
        """When task.md itself is deleted, rebuild_task returns (None, False)."""
        (dashboard / "01-first" / "task.md").unlink()
        result, children_changed = plan_dashboard.rebuild_task("01-first")
        assert result is None
        assert children_changed is False
        assert "01-first" not in plan_dashboard._task_index

    def test_same_children_returns_false(self, dashboard):
        """rebuild_task with unchanged children: children_changed=False."""
        child = dashboard / "03-third" / "sub"
        child.mkdir()
        _write_task_md(child / "task.md", "Stable Sub", "not-started")
        plan_dashboard.rebuild_tree()

        # Rebuild without changing structure
        updated, children_changed = plan_dashboard.rebuild_task("03-third")
        assert updated is not None
        assert children_changed is False

    def test_new_child_added_to_flat_index(self, dashboard):
        """A newly discovered child appears in the flat index."""
        child = dashboard / "02-second" / "new-child"
        child.mkdir()
        _write_task_md(child / "task.md", "Fresh Child", "not-started")

        plan_dashboard.rebuild_task("02-second")
        assert "02-second/new-child" in plan_dashboard._task_index
        assert plan_dashboard._task_index["02-second/new-child"].title == "Fresh Child"


# ---------------------------------------------------------------------------
# TestRenderNavNodeDepth
# ---------------------------------------------------------------------------


class TestRenderNavNodeDepth:
    """Test _render_nav_node() depth parameter and depth inference."""

    def test_render_with_explicit_depth(self, dashboard):
        """Passing an explicit depth renders correctly."""
        task = plan_dashboard._task_index["01-first"]
        html_depth0 = plan_dashboard._render_nav_node(task, depth=0)
        html_depth5 = plan_dashboard._render_nav_node(task, depth=5)
        # Both should render the task node with data-path
        assert 'data-path="01-first"' in html_depth0
        assert 'data-path="01-first"' in html_depth5

    def test_render_with_default_depth(self, dashboard):
        """Default depth (None) infers from the task's path."""
        task = plan_dashboard._task_index["01-first"]
        html = plan_dashboard._render_nav_node(task)
        assert 'data-path="01-first"' in html
        assert "task-node" in html

    def test_children_inline_at_low_depth(self, dashboard):
        """At depth < 3, children are rendered inline in the HTML."""
        child_dir = dashboard / "01-first" / "sub"
        child_dir.mkdir()
        _write_task_md(child_dir / "task.md", "Sub Task", "not-started",
                       objective="Child objective.")
        plan_dashboard.rebuild_tree()

        parent = plan_dashboard._task_index["01-first"]
        html = plan_dashboard._render_nav_node(parent, depth=0)
        # At depth 0, children rendered at depth 1 (< 3) should be inline
        assert 'data-path="01-first/sub"' in html

    def test_children_lazy_at_high_depth(self, dashboard):
        """At depth >= 3, children are lazy-loaded (not rendered inline)."""
        # Build a 4-level deep structure
        current = dashboard / "01-first"
        for level_name in ["level2", "level3", "level4"]:
            current = current / level_name
            current.mkdir()
            _write_task_md(current / "task.md", f"Task {level_name}", "not-started")
        plan_dashboard.rebuild_tree()

        # Render from depth 3 — the task at level 3 has a child at level 4
        task_l3 = plan_dashboard._task_index["01-first/level2/level3"]
        html = plan_dashboard._render_nav_node(task_l3, depth=3)
        # At depth 3, children should NOT be rendered inline (the
        # container is present but empty; markLazyNodes() flags it
        # client-side rather than a server-emitted needsLoad marker)
        assert 'data-path="01-first/level2/level3/level4"' not in html


# ---------------------------------------------------------------------------
# TestWatcherDecisionLogic
# ---------------------------------------------------------------------------


class TestWatcherDecisionLogic:
    """Test the watcher's broadcast event classification.

    The watcher (_watch_worktree) is async and uses watchfiles.awatch(),
    which is impractical to unit test directly. Instead, we test the decision
    logic by simulating the change classification and broadcast calls that
    the watcher makes.
    """

    def _run_watcher_logic(self, plan_root, changes, *, skip_init: bool = False):
        """Simulate the watcher's classification and broadcast logic.

        Takes a list of (change_type, file_path_str) tuples and returns
        a list of (event_name, data_snippet) broadcast calls.

        This mirrors the logic in _rebuild_and_broadcast() without depending on
        watchfiles.awatch().

        When *skip_init* is True, the caller is responsible for having called
        ``_init_dashboard(plan_root)`` beforehand.  This allows tests to
        set up dashboard state at a known point in time (e.g. before creating
        a child directory on disk) so that ``rebuild_task()`` can detect the
        structural change (``children_changed=True``).
        """
        import enum

        class Change(enum.Enum):
            added = 1
            modified = 2
            deleted = 3

        if not skip_init:
            _init_dashboard(plan_root)

        # Classify changes (mirrors watcher logic lines 196-224)
        structural_parent_paths: set[str] = set()
        changed_paths: set[str] = set()

        for change_type_str, file_path_str in changes:
            fp = Path(file_path_str)
            name = fp.name

            if name not in ("task.md", "comments.yaml"):
                continue

            task_dir = fp.parent
            try:
                rel = task_dir.relative_to(plan_root)
                task_path = str(rel) if str(rel) != "." else ""
            except ValueError:
                continue

            change_type = Change[change_type_str]

            if change_type == Change.added:
                if name == "task.md":
                    parent_path = str(Path(task_path).parent) if task_path else ""
                    if parent_path == ".":
                        parent_path = ""
                    structural_parent_paths.add(parent_path)
            elif change_type == Change.deleted:
                if name == "task.md":
                    parent_path = str(Path(task_path).parent) if task_path else ""
                    if parent_path == ".":
                        parent_path = ""
                    structural_parent_paths.add(parent_path)
            else:
                changed_paths.add(task_path)

        # Simulate the broadcast decisions — matches production logic in
        # _rebuild_and_broadcast() (plan_dashboard.py).
        broadcasts: list[tuple[str, str]] = []

        if structural_parent_paths:
            plan_dashboard.rebuild_tree()
            root_task = plan_dashboard._root_task
            if root_task is not None:
                for parent_path in structural_parent_paths:
                    if parent_path == "" and not (root_task.body and root_task.body.strip()):
                        broadcasts.append(("full-reload", "{}"))
                        break
                    parent_task = plan_dashboard._task_index.get(parent_path)
                    if parent_task is not None:
                        fragment = plan_dashboard._render_nav_node(parent_task)
                        broadcasts.append((f"task:{parent_path}", fragment))
                    else:
                        broadcasts.append(("full-reload", "{}"))
                        break

                summary_html = plan_dashboard._render_summary()
                broadcasts.append(("summary-updated", summary_html))

        # Process content-only changes — collect children_changed paths
        # first, do one rebuild_tree(), then re-render (mirrors production).
        content_paths = changed_paths - structural_parent_paths
        if content_paths:
            children_changed_paths: set[str] = set()

            for task_path in content_paths:
                updated, children_changed = plan_dashboard.rebuild_task(task_path)
                if children_changed:
                    children_changed_paths.add(task_path)
                elif updated is not None and plan_dashboard._root_task is not None:
                    fragment = plan_dashboard._render_nav_node(updated)
                    broadcasts.append((f"task:{task_path}", fragment))

            if children_changed_paths:
                plan_dashboard.rebuild_tree()
                if plan_dashboard._root_task is not None:
                    for task_path in children_changed_paths:
                        task = plan_dashboard._task_index.get(task_path)
                        if task is not None:
                            fragment = plan_dashboard._render_nav_node(task)
                            broadcasts.append((f"task:{task_path}", fragment))
                        else:
                            broadcasts.append(("full-reload", "{}"))
                            break

            if content_paths and plan_dashboard._root_task is not None:
                summary_html = plan_dashboard._render_summary()
                broadcasts.append(("summary-updated", summary_html))

        return broadcasts

    def test_content_change_broadcasts_task_event(self, plan_root):
        """Modifying a task.md broadcasts task:{path}, not full-reload."""
        # Modify the file on disk first
        task_md = plan_root / "01-first" / "task.md"
        content = task_md.read_text()
        task_md.write_text(content.replace("First Task", "Edited First"))

        broadcasts = self._run_watcher_logic(plan_root, [
            ("modified", str(task_md)),
        ])

        event_names = [e for e, _ in broadcasts]
        assert "task:01-first" in event_names
        assert "full-reload" not in event_names

    def test_structural_add_broadcasts_parent_event(self, plan_root):
        """Adding a new task.md broadcasts task:{parent_path}."""
        new_dir = plan_root / "01-first" / "sub-new"
        new_dir.mkdir()
        _write_task_md(new_dir / "task.md", "Brand New", "not-started")

        broadcasts = self._run_watcher_logic(plan_root, [
            ("added", str(new_dir / "task.md")),
        ])

        event_names = [e for e, _ in broadcasts]
        assert "task:01-first" in event_names
        assert "full-reload" not in event_names

    def test_structural_delete_broadcasts_parent_event(self, plan_root):
        """Deleting a task.md broadcasts task:{parent_path}."""
        # Create a child first, then initialize with it, then simulate deletion
        child = plan_root / "02-second" / "doomed"
        child.mkdir()
        _write_task_md(child / "task.md", "Doomed", "not-started")

        # Now remove it from disk
        (child / "task.md").unlink()
        child.rmdir()

        # Simulate watcher seeing the deletion
        broadcasts = self._run_watcher_logic(plan_root, [
            ("deleted", str(child / "task.md")),
        ])

        event_names = [e for e, _ in broadcasts]
        assert "task:02-second" in event_names
        assert "full-reload" not in event_names

    def test_root_structural_change_with_no_body_falls_back(self, tmp_path):
        """Root-level structural change when root has no body -> full-reload."""
        root = tmp_path / "superRA"
        root.mkdir()
        # Root with truly empty body — no ## sections at all
        bare_content = (
            '---\ntitle: "Empty Root"\nstatus: not-started\nreview_status: ~\n'
            'integration_status: ~\ndepends_on: []\ntags: []\n'
            'created: 2026-01-01\n---\n'
        )
        (root / "task.md").write_text(bare_content, encoding="utf-8")

        d1 = root / "task-a"
        d1.mkdir()
        _write_task_md(d1 / "task.md", "Task A", "not-started")

        # Simulate adding a new top-level task
        new_dir = root / "task-b"
        new_dir.mkdir()
        _write_task_md(new_dir / "task.md", "Task B", "not-started")

        broadcasts = self._run_watcher_logic(root, [
            ("added", str(new_dir / "task.md")),
        ])

        event_names = [e for e, _ in broadcasts]
        assert "full-reload" in event_names

    def test_root_structural_change_with_body_broadcasts_task(self, plan_root):
        """Root-level structural change when root has body -> task: event."""
        # plan_root has a root with body ("## Objective\n\nA test plan.\n")
        new_dir = plan_root / "04-brand-new"
        new_dir.mkdir()
        _write_task_md(new_dir / "task.md", "Brand New Top", "not-started")

        broadcasts = self._run_watcher_logic(plan_root, [
            ("added", str(new_dir / "task.md")),
        ])

        event_names = [e for e, _ in broadcasts]
        # Root has body, so parent ("") gets a task: event, not full-reload
        assert "task:" in event_names
        assert "full-reload" not in event_names

    def test_children_changed_broadcasts_task_event(self, plan_root):
        """When rebuild_task detects children_changed, broadcasts task:{path}.

        The dashboard state is initialized BEFORE creating the child directory
        on disk, so rebuild_task() sees the new child as a structural change
        (children_changed=True).  skip_init=True prevents _run_watcher_logic
        from re-initializing and masking the change.
        """
        # Initialize dashboard while 03-third has NO children
        _init_dashboard(plan_root)
        assert plan_dashboard._task_index["03-third"].children == []

        # Now create a child directory on disk that the dashboard doesn't know about
        child = plan_root / "03-third" / "sub-dynamic"
        child.mkdir()
        _write_task_md(child / "task.md", "Dynamic Sub", "not-started")

        # Simulate a content-only change (modified) to 03-third's task.md.
        # The watcher classifies this as a content change, but rebuild_task()
        # will detect the new child directory -> children_changed=True.
        task_md = plan_root / "03-third" / "task.md"
        content = task_md.read_text()
        task_md.write_text(content.replace("Third Task", "Third Updated"))

        broadcasts = self._run_watcher_logic(plan_root, [
            ("modified", str(task_md)),
        ], skip_init=True)

        event_names = [e for e, _ in broadcasts]
        assert "task:03-third" in event_names
        assert "full-reload" not in event_names

        # Verify rebuild_tree() was triggered (the child should now be indexed)
        assert "03-third/sub-dynamic" in plan_dashboard._task_index

    def test_non_task_file_changes_ignored(self, plan_root):
        """Changes to non-task.md files (e.g. .py, .txt) produce no broadcasts."""
        random_file = plan_root / "01-first" / "notes.txt"
        random_file.write_text("some notes")

        broadcasts = self._run_watcher_logic(plan_root, [
            ("modified", str(random_file)),
        ])

        assert len(broadcasts) == 0

    def test_multiple_content_changes_broadcast_each(self, plan_root):
        """Multiple content changes in one batch produce per-task events."""
        # Modify two tasks
        t1 = plan_root / "01-first" / "task.md"
        content1 = t1.read_text()
        t1.write_text(content1.replace("First Task", "First Edited"))

        t2 = plan_root / "02-second" / "task.md"
        content2 = t2.read_text()
        t2.write_text(content2.replace("Second Task", "Second Edited"))

        broadcasts = self._run_watcher_logic(plan_root, [
            ("modified", str(t1)),
            ("modified", str(t2)),
        ])

        event_names = [e for e, _ in broadcasts]
        assert "task:01-first" in event_names
        assert "task:02-second" in event_names
        assert "full-reload" not in event_names

    def test_summary_updated_after_content_change(self, plan_root):
        """Content changes emit summary-updated after task events."""
        task_md = plan_root / "01-first" / "task.md"
        content = task_md.read_text()
        task_md.write_text(content.replace("First Task", "First Edited"))

        broadcasts = self._run_watcher_logic(plan_root, [
            ("modified", str(task_md)),
        ])

        event_names = [e for e, _ in broadcasts]
        assert "summary-updated" in event_names
        # summary-updated should come after the task event
        task_idx = event_names.index("task:01-first")
        summary_idx = event_names.index("summary-updated")
        assert summary_idx > task_idx

    def test_summary_updated_after_structural_change(self, plan_root):
        """Structural changes emit summary-updated after parent events."""
        new_dir = plan_root / "01-first" / "sub-new"
        new_dir.mkdir()
        _write_task_md(new_dir / "task.md", "Brand New", "not-started")

        broadcasts = self._run_watcher_logic(plan_root, [
            ("added", str(new_dir / "task.md")),
        ])

        event_names = [e for e, _ in broadcasts]
        assert "summary-updated" in event_names
        assert "task:01-first" in event_names


# ---------------------------------------------------------------------------
# TestBroadcastIntegration (async, mocking _broadcast)
# ---------------------------------------------------------------------------


class TestBroadcastIntegration:
    """Test that _broadcast() is called with correct event names.

    Uses AsyncMock to capture actual _broadcast calls without needing
    real SSE clients.
    """

    def test_broadcast_formats_task_event_correctly(self):
        """_broadcast produces SSE frames with event: task:{path} naming."""
        loop = asyncio.new_event_loop()
        queue: asyncio.Queue[str] = asyncio.Queue()
        plan_dashboard._worktree_clients["wt"] = {queue}
        try:
            loop.run_until_complete(
                plan_dashboard._broadcast("task:01-first", "<div>fragment</div>", "wt")
            )
            msg = loop.run_until_complete(asyncio.wait_for(queue.get(), timeout=1))
            assert msg.startswith("event: task:01-first\n")
            assert "data: <div>fragment</div>\n" in msg
        finally:
            plan_dashboard._worktree_clients.pop("wt", None)
            loop.close()

    def test_broadcast_full_reload_event(self):
        """full-reload event is properly formatted."""
        loop = asyncio.new_event_loop()
        queue: asyncio.Queue[str] = asyncio.Queue()
        plan_dashboard._worktree_clients["wt"] = {queue}
        try:
            loop.run_until_complete(
                plan_dashboard._broadcast("full-reload", "{}", "wt")
            )
            msg = loop.run_until_complete(asyncio.wait_for(queue.get(), timeout=1))
            assert msg.startswith("event: full-reload\n")
            assert "data: {}\n" in msg
        finally:
            plan_dashboard._worktree_clients.pop("wt", None)
            loop.close()

    def test_summary_updated_event(self):
        """summary-updated event is properly formatted."""
        loop = asyncio.new_event_loop()
        queue: asyncio.Queue[str] = asyncio.Queue()
        plan_dashboard._worktree_clients["wt"] = {queue}
        try:
            loop.run_until_complete(
                plan_dashboard._broadcast("summary-updated", "<span>3 tasks</span>", "wt")
            )
            msg = loop.run_until_complete(asyncio.wait_for(queue.get(), timeout=1))
            assert msg.startswith("event: summary-updated\n")
        finally:
            plan_dashboard._worktree_clients.pop("wt", None)
            loop.close()


# ---------------------------------------------------------------------------
# TestTaskDepth
# ---------------------------------------------------------------------------


class TestTaskDepth:
    """Test the _task_depth() helper used by _render_nav_node()."""

    def test_root_path_is_depth_0(self):
        assert plan_dashboard._task_depth("") == 0

    def test_top_level_task_is_depth_0(self):
        assert plan_dashboard._task_depth("my-task") == 0

    def test_nested_task_depth(self):
        assert plan_dashboard._task_depth("parent/child") == 1
        assert plan_dashboard._task_depth("a/b/c") == 2
        assert plan_dashboard._task_depth("a/b/c/d") == 3

    def test_deeply_nested(self):
        assert plan_dashboard._task_depth("a/b/c/d/e/f") == 5
