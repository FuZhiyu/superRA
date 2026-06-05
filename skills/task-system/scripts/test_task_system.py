#!/usr/bin/env python3
"""Tests for the task-system skill scripts."""

from __future__ import annotations

import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

import _task_io
import dashboard_artifact_workflow
from _task_io import parse_body_sections
import plan_dashboard
import plan_migrate
import task_add_result
import task_check
import task_create
import task_hook
import task_link
import task_query
import task_read
import task_rename
import task_update


# --- Helpers ---


def _write_task_md(path: Path, title: str, status: str, **kwargs):
    """Write a task.md file (unified status format).

    kwargs: depends_on, tags, objective, results, created.
    For legacy test scenarios, review_status and integration_status can be
    passed to produce old-format files.
    """
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

    # Build frontmatter — include legacy fields only if explicitly passed
    fm_lines = [f'title: "{title}"', f"status: {status}"]
    if "review_status" in kwargs:
        fm_lines.append(f"review_status: {kwargs['review_status']}")
    if "integration_status" in kwargs:
        fm_lines.append(f"integration_status: {kwargs['integration_status']}")
    fm_lines.extend([
        f"depends_on:{deps_yaml}",
        f"tags: {tags_yaml}",
        f"created: {created}",
    ])

    content = "---\n" + "\n".join(fm_lines) + "\n---\n\n" + body
    path.write_text(content, encoding="utf-8")


def _write_tiny_png(path: Path) -> bytes:
    """Write a minimal valid 2x2 PNG (no PIL dependency) and return its bytes."""
    import struct
    import zlib

    def _chunk(typ: bytes, data: bytes) -> bytes:
        body = typ + data
        return (
            struct.pack(">I", len(data))
            + body
            + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", 2, 2, 8, 2, 0, 0, 0)
    raw = (b"\x00" + b"\xff\x00\x00" * 2) * 2
    png = (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(raw))
        + _chunk(b"IEND", b"")
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)
    return png


# --- Fixtures ---


@pytest.fixture
def plan_root(tmp_path):
    """Create a minimal plan tree for testing."""
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
                   objective="Complete step 1 and step 2.")

    d3 = root / "03-third"
    d3.mkdir()
    _write_task_md(d3 / "task.md", "Third Task", "not-started",
                   depends_on=["02-second"],
                   objective="Complete step 1.")

    return root


@pytest.fixture
def plan_with_branches(tmp_path):
    """Create a plan tree with branch tasks (non-leaf) and leaf tasks."""
    root = tmp_path / "superRA"
    root.mkdir()

    _write_task_md(root / "task.md", "Branch Project", "not-started",
                   objective="Branch project overview.")

    parent = root / "01-data-prep"
    parent.mkdir()
    _write_task_md(parent / "task.md", "Data Preparation", "not-started",
                   objective="Prepare all datasets.")

    child1 = parent / "01-load"
    child1.mkdir()
    _write_task_md(child1 / "task.md", "Load Data", "approved",
                   objective="Read parquet files.")

    child2 = parent / "02-merge"
    child2.mkdir()
    _write_task_md(child2 / "task.md", "Merge Data", "not-started",
                   depends_on=["01-load"],
                   objective="Left join datasets.")

    est = root / "02-estimation"
    est.mkdir()
    _write_task_md(est / "task.md", "Estimation", "not-started",
                   depends_on=["01-data-prep"],
                   objective="Run model.")

    return root


# --- _task_io tests ---


class TestParseTask:
    def test_parse_leaf_task(self, plan_root):
        task = _task_io.parse_task(plan_root / "01-first" / "task.md")
        assert task.title == "First Task"
        assert task.status == "approved"
        assert task.depends_on == []
        assert task.tags == ["data"]
        assert task.path == "01-first"
        assert task.is_leaf  # no children loaded yet

    def test_parse_task_with_deps(self, plan_root):
        task = _task_io.parse_task(plan_root / "02-second" / "task.md")
        assert task.depends_on == ["01-first"]
        assert task.tags == ["analysis"]

    def test_parse_root(self, plan_root):
        task = _task_io.parse_task(plan_root / "task.md")
        assert task.title == "Test Project"
        assert task.is_root

    def test_unknown_status_warns_and_preserves(self, tmp_path):
        # An unknown status must NOT crash the reader; parse_task warns and keeps
        # the raw value so the dashboard/query/read tree walk survives one bad
        # file. task_check remains the strict validator.
        task_md = tmp_path / "task.md"
        task_md.write_text(
            "---\ntitle: T\nstatus: done\n---\n## Objective\n\nx\n",
            encoding="utf-8",
        )
        with pytest.warns(UserWarning, match="Invalid status 'done'"):
            task = _task_io.parse_task(task_md)
        assert task.status == "done"  # raw value preserved, not coerced


class TestWalkPlan:
    def test_walk_flat(self, plan_root):
        root = _task_io.walk_plan(plan_root)
        assert root.title == "Test Project"
        assert len(root.children) == 3
        assert root.children[0].slug == "01-first"
        assert root.children[1].slug == "02-second"
        assert root.children[2].slug == "03-third"

    def test_walk_nested(self, plan_with_branches):
        root = _task_io.walk_plan(plan_with_branches)
        assert len(root.children) == 2

        data_prep = root.children[0]
        assert data_prep.slug == "01-data-prep"
        assert len(data_prep.children) == 2
        assert not data_prep.is_leaf

        load = data_prep.children[0]
        assert load.slug == "01-load"
        assert load.is_leaf


class TestComputeStatus:
    def test_leaf_status(self, plan_root):
        root = _task_io.walk_plan(plan_root)
        assert root.children[0].effective_status() == "approved"
        assert root.children[1].effective_status() == "not-started"

    def test_branch_rollup_partial(self, plan_with_branches):
        root = _task_io.walk_plan(plan_with_branches)
        data_prep = root.children[0]
        assert data_prep.effective_status() == "in-progress"

    def test_branch_rollup_all_approved(self, plan_with_branches):
        root = _task_io.walk_plan(plan_with_branches)
        data_prep = root.children[0]
        data_prep.children[1].status = "approved"
        assert data_prep.effective_status() == "approved"


class TestComputeFrontier:
    def test_linear_chain(self, plan_root):
        root = _task_io.walk_plan(plan_root)
        frontier = _task_io.compute_frontier(root)
        paths = [t.path for t in frontier]
        assert "02-second" in paths
        assert "01-first" not in paths  # already approved
        assert "03-third" not in paths  # blocked by 02-second

    def test_nested_frontier(self, plan_with_branches):
        root = _task_io.walk_plan(plan_with_branches)
        frontier = _task_io.compute_frontier(root)
        paths = [t.path for t in frontier]
        assert "01-data-prep/02-merge" in paths
        assert "02-estimation" not in paths  # blocked by 01-data-prep not approved

    def test_all_approved(self, plan_root):
        root = _task_io.walk_plan(plan_root)
        for child in root.children:
            child.status = "approved"
        frontier = _task_io.compute_frontier(root)
        assert len(frontier) == 0

    def test_no_deps_all_frontier(self, tmp_path):
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Test", "not-started")
        for name in ["01-a", "02-b", "03-c"]:
            d = root_dir / name
            d.mkdir()
            _write_task_md(d / "task.md", name, "not-started",
                           objective="Do it.")
        root = _task_io.walk_plan(root_dir)
        frontier = _task_io.compute_frontier(root)
        assert len(frontier) == 3

    def test_revise_status_excluded_from_frontier(self, plan_root):
        """A task with status 'revise' should NOT appear on the frontier.

        The frontier only includes 'not-started' and 'in-progress' tasks.
        'revise' means the task needs rework after review, but the current
        implementation treats it as non-dispatchable until explicitly
        moved back to 'in-progress'.
        """
        root = _task_io.walk_plan(plan_root)
        # 02-second depends on 01-first (approved), so deps are met.
        # Set it to 'revise' — it should NOT appear on the frontier.
        root.children[1].status = "revise"
        frontier = _task_io.compute_frontier(root)
        paths = [t.path for t in frontier]
        assert "02-second" not in paths, (
            "'revise' tasks should not be on the frontier; "
            "only 'not-started' and 'in-progress' are dispatchable"
        )
        # 03-third depends on 02-second which is 'revise' (not approved),
        # so 03-third should also be blocked.
        assert "03-third" not in paths

    def test_diamond_dependency(self, tmp_path):
        """Diamond DAG: D(approved) -> B, D -> C, B -> A, C -> A.

        Frontier should be [B, C] — D is done, A is blocked by both B and C.
        """
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Diamond", "not-started")
        for name, status, deps in [
            ("01-D", "approved", []),
            ("02-B", "not-started", ["01-D"]),
            ("03-C", "not-started", ["01-D"]),
            ("04-A", "not-started", ["02-B", "03-C"]),
        ]:
            d = root_dir / name
            d.mkdir()
            _write_task_md(d / "task.md", name, status,
                           depends_on=deps, objective="Do it.")
        root = _task_io.walk_plan(root_dir)
        frontier = _task_io.compute_frontier(root)
        paths = [t.path for t in frontier]
        assert "02-B" in paths
        assert "03-C" in paths
        assert "04-A" not in paths, "A is blocked by unapproved B and C"
        assert "01-D" not in paths, "D is already approved"

    def test_three_level_nesting(self, tmp_path):
        """3-level deep tree: root -> L1 -> L2 -> leaf tasks.

        Verify frontier propagates ancestors_ready=False through
        intermediate levels correctly.
        """
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        # Level 1: two branch tasks, L1-b depends on L1-a
        l1a = root_dir / "01-L1a"
        l1a.mkdir()
        _write_task_md(l1a / "task.md", "L1-a", "not-started")
        l1b = root_dir / "02-L1b"
        l1b.mkdir()
        _write_task_md(l1b / "task.md", "L1-b", "not-started",
                       depends_on=["01-L1a"])
        # Level 2 under L1-a: one sub-branch
        l2 = l1a / "01-L2"
        l2.mkdir()
        _write_task_md(l2 / "task.md", "L2", "not-started")
        # Level 3 (leaf) under L2
        leaf = l2 / "01-leaf"
        leaf.mkdir()
        _write_task_md(leaf / "task.md", "Deep Leaf", "not-started",
                       objective="Do it.")
        # Level 2 under L1-b: a leaf that should be blocked
        l1b_leaf = l1b / "01-blocked-leaf"
        l1b_leaf.mkdir()
        _write_task_md(l1b_leaf / "task.md", "Blocked Leaf", "not-started",
                       objective="Do it.")

        root = _task_io.walk_plan(root_dir)
        frontier = _task_io.compute_frontier(root)
        paths = [t.path for t in frontier]
        # Deep leaf under L1-a is reachable (no blocking deps at any level)
        assert "01-L1a/01-L2/01-leaf" in paths
        # Blocked leaf under L1-b is NOT reachable because L1-b depends on
        # L1-a which is not yet approved
        assert "02-L1b/01-blocked-leaf" not in paths, (
            "ancestors_ready=False should propagate: L1-b is blocked by L1-a"
        )

    def test_empty_plan_tree(self, tmp_path):
        """A plan with only root task.md and no children.

        When the root has no children, it is treated as a leaf by
        _collect_frontier. Since its status is 'not-started' and
        ancestors_ready=True, the root itself appears on the frontier.
        This is correct: a childless root IS the work to be done.

        render_dag should return the fallback 'no children' output.
        """
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Empty", "not-started")
        root = _task_io.walk_plan(root_dir)
        frontier = _task_io.compute_frontier(root)
        # Root with no children is itself a leaf and is on the frontier
        assert len(frontier) == 1
        assert frontier[0].is_root
        dag = task_query.render_dag(root)
        assert "no children" in dag


class TestWriteTask:
    def test_roundtrip(self, plan_root):
        task = _task_io.parse_task(plan_root / "01-first" / "task.md")
        original_body = task.body
        _task_io.write_task(task)
        task2 = _task_io.parse_task(plan_root / "01-first" / "task.md")
        assert task2.title == task.title
        assert task2.status == task.status
        assert task2.tags == task.tags
        assert task2.body == original_body


class TestFrontmatterParsing:
    def test_inline_list(self):
        text = '---\ntitle: "Test"\ntags: [a, b, c]\n---\nBody\n'
        fm, body = _task_io.parse_frontmatter(text)
        assert fm["tags"] == ["a", "b", "c"]

    def test_multiline_list(self):
        text = '---\ntitle: "Test"\ndepends_on:\n  - 01-first\n  - 02-second\n---\nBody\n'
        fm, body = _task_io.parse_frontmatter(text)
        assert fm["depends_on"] == ["01-first", "02-second"]

    def test_empty_list(self):
        text = '---\ntitle: "Test"\ndepends_on: []\n---\nBody\n'
        fm, body = _task_io.parse_frontmatter(text)
        assert fm["depends_on"] == []

    def test_tilde_value(self):
        text = '---\nreview_status: ~\n---\nBody\n'
        fm, body = _task_io.parse_frontmatter(text)
        assert fm["review_status"] == "~"

    def test_no_frontmatter(self):
        """Text with no frontmatter at all returns empty dict and full text."""
        text = "Just a body with no frontmatter.\n"
        fm, body = _task_io.parse_frontmatter(text)
        assert fm == {}
        assert body == text

    def test_only_opening_delimiter(self):
        """Text with only '---' opening but no closing should return empty dict."""
        text = "---\ntitle: Test\nNo closing delimiter.\n"
        fm, body = _task_io.parse_frontmatter(text)
        assert fm == {}
        assert body == text

    def test_value_containing_colon(self):
        """Values with colons (e.g., 'Part 1: Introduction') should parse correctly."""
        text = '---\ntitle: "Part 1: Introduction"\nstatus: not-started\n---\nBody\n'
        fm, body = _task_io.parse_frontmatter(text)
        assert fm["title"] == "Part 1: Introduction"
        assert fm["status"] == "not-started"


# --- CLI script tests ---


class TestTaskCreate:
    def test_create_basic(self, plan_root):
        task_create.create_task(
            plan_root=plan_root,
            task_path="04-new-task",
            title="New Task",
            objective="A new objective.",
        )
        task_md = plan_root / "04-new-task" / "task.md"
        assert task_md.exists()
        content = task_md.read_text(encoding="utf-8")
        assert "## Objective" in content
        assert "## Steps" not in content
        assert "# New Task\n" not in content  # no title heading in v2
        assert "A new objective." in content
        task = _task_io.parse_task(task_md)
        assert task.title == "New Task"
        assert task.status == "not-started"
        assert task.depends_on == []

    def test_create_with_planner_guidance(self, plan_root):
        task_create.create_task(
            plan_root=plan_root,
            task_path="04-new-task",
            title="New Task",
            objective="A binding objective.",
            guidance="Consider starting from Code/example.py.",
        )
        content = (plan_root / "04-new-task" / "task.md").read_text(
            encoding="utf-8"
        )
        assert "## Objective\n\nA binding objective." in content
        assert "## Planner Guidance\n\nConsider starting from Code/example.py." in content
        assert content.index("## Objective") < content.index("## Planner Guidance")
        assert content.index("## Planner Guidance") < content.index("## Results")

    def test_create_without_guidance_omits_empty_section(self, plan_root):
        task_create.create_task(
            plan_root=plan_root,
            task_path="04-new-task",
            title="New Task",
            objective="A binding objective.",
        )
        content = (plan_root / "04-new-task" / "task.md").read_text(
            encoding="utf-8"
        )
        assert "## Planner Guidance" not in content

    def test_create_with_deps(self, plan_root):
        task_create.create_task(
            plan_root=plan_root,
            task_path="04-new-task",
            title="New Task",
            depends_on=["01-first"],
        )
        task = _task_io.parse_task(plan_root / "04-new-task" / "task.md")
        assert task.depends_on == ["01-first"]

    def test_create_duplicate_fails(self, plan_root):
        with pytest.raises(SystemExit) as exc_info:
            task_create.create_task(
                plan_root=plan_root,
                task_path="01-first",
                title="Duplicate",
            )
        assert exc_info.value.code == 1

    def test_create_bad_dep_fails(self, plan_root):
        with pytest.raises(SystemExit) as exc_info:
            task_create.create_task(
                plan_root=plan_root,
                task_path="04-new",
                title="New",
                depends_on=["99-nonexistent"],
            )
        assert exc_info.value.code == 1

    def test_create_root_task_does_not_generate_serve_script(self, plan_root):
        task_create.create_task(
            plan_root=plan_root,
            task_path="04-new-task",
            title="New Task",
        )
        serve = plan_root / "serve"
        assert not serve.exists()

    def test_create_root_task_does_not_overwrite_serve(self, plan_root):
        serve = plan_root / "serve"
        serve.write_text("existing content", encoding="utf-8")
        task_create.create_task(
            plan_root=plan_root,
            task_path="04-new-task",
            title="New Task",
        )
        assert serve.read_text(encoding="utf-8") == "existing content"

    def test_create_nested_task_does_not_generate_serve(self, plan_root):
        # Create a parent for nesting
        parent = plan_root / "04-parent"
        parent.mkdir()
        _write_task_md(parent / "task.md", "Parent", "not-started")
        task_create.create_task(
            plan_root=plan_root,
            task_path="04-parent/01-child",
            title="Child Task",
        )
        serve = plan_root / "serve"
        assert not serve.exists()

    def test_traversal_rejected(self, plan_root, tmp_path):
        """Path traversal via .. is rejected before any filesystem mutation."""
        with pytest.raises(SystemExit) as exc_info:
            task_create.create_task(
                plan_root=plan_root,
                task_path="../escaped",
                title="Escaped",
            )
        assert exc_info.value.code == 1
        assert not (tmp_path / "escaped").exists()

    def test_absolute_path_outside_root_rejected(self, plan_root, tmp_path):
        """An absolute path outside the task root is rejected."""
        outside = str(tmp_path / "outside")
        with pytest.raises(SystemExit) as exc_info:
            task_create.create_task(
                plan_root=plan_root,
                task_path=outside,
                title="Outside",
            )
        assert exc_info.value.code == 1
        assert not Path(outside).exists()

    def test_valid_nested_create_succeeds(self, plan_root):
        """A valid nested path (existing parent) is created without error."""
        parent = plan_root / "04-parent"
        parent.mkdir()
        _write_task_md(parent / "task.md", "Parent", "not-started")
        task_create.create_task(
            plan_root=plan_root,
            task_path="04-parent/01-child",
            title="Child Task",
            objective="A nested task.",
        )
        task_md = plan_root / "04-parent" / "01-child" / "task.md"
        assert task_md.exists()
        task = _task_io.parse_task(task_md)
        assert task.title == "Child Task"

    def test_create_child_under_approved_parent_rolls_up(self, plan_root):
        """Creating a not-started child under an approved parent must demote the parent.

        Regression test for the missing propagate_parent_status call in create_task.
        """
        parent = plan_root / "04-parent"
        parent.mkdir()
        _write_task_md(parent / "task.md", "Parent", "approved")

        # Verify precondition: parent starts approved
        before = _task_io.parse_task(parent / "task.md")
        assert before.status == "approved"

        task_create.create_task(
            plan_root=plan_root,
            task_path="04-parent/01-child",
            title="Child Task",
        )

        # After creating the child, parent must no longer be approved
        after = _task_io.parse_task(parent / "task.md")
        assert after.status != "approved", (
            f"parent still has status={after.status!r} after adding a not-started child; "
            "propagate_parent_status was not called"
        )


class TestTaskUpdate:
    def test_update_status(self, plan_root):
        task_update.update_task(
            plan_root=plan_root,
            task_path="02-second",
            status="in-progress",
        )
        task = _task_io.parse_task(plan_root / "02-second" / "task.md")
        assert task.status == "in-progress"

    def test_update_tags(self, plan_root):
        task_update.update_task(
            plan_root=plan_root,
            task_path="02-second",
            add_tags=["new-tag"],
        )
        task = _task_io.parse_task(plan_root / "02-second" / "task.md")
        assert "new-tag" in task.tags
        assert "analysis" in task.tags

    def test_remove_tag(self, plan_root):
        task_update.update_task(
            plan_root=plan_root,
            task_path="02-second",
            remove_tags=["analysis"],
        )
        task = _task_io.parse_task(plan_root / "02-second" / "task.md")
        assert "analysis" not in task.tags


class TestTaskLink:
    def test_add_dependency(self, plan_root):
        task_link.link_task(
            plan_root=plan_root,
            task_path="03-third",
            depends_on="01-first",
        )
        task = _task_io.parse_task(plan_root / "03-third" / "task.md")
        assert "01-first" in task.depends_on
        assert "02-second" in task.depends_on

    def test_remove_dependency(self, plan_root):
        task_link.link_task(
            plan_root=plan_root,
            task_path="02-second",
            depends_on="01-first",
            remove=True,
        )
        task = _task_io.parse_task(plan_root / "02-second" / "task.md")
        assert "01-first" not in task.depends_on


class TestTaskRename:
    def test_rename_cascades(self, plan_root):
        task_rename.rename_task(plan_root, "01-first", "01-first-renamed")
        assert not (plan_root / "01-first").exists()
        assert (plan_root / "01-first-renamed" / "task.md").exists()

        task2 = _task_io.parse_task(plan_root / "02-second" / "task.md")
        assert "01-first-renamed" in task2.depends_on
        assert "01-first" not in task2.depends_on


class TestTaskAddResult:
    def test_add_finding(self, plan_root):
        task_add_result.add_result(
            plan_root=plan_root,
            task_path="02-second",
            finding="Found 42 interesting rows",
        )
        task = _task_io.parse_task(plan_root / "02-second" / "task.md")
        assert "Found 42 interesting rows" in task.body

    def test_add_finding_with_preexisting_results(self, plan_root):
        """Adding a finding to a task that already has ## Results and ### Key Findings.

        The existing content (01-first has 'Found 100 rows') should be
        preserved, and the new finding should be appended.
        """
        task_add_result.add_result(
            plan_root=plan_root,
            task_path="01-first",
            finding="Found 200 more rows",
        )
        task = _task_io.parse_task(plan_root / "01-first" / "task.md")
        assert "Found 100 rows" in task.body, "Pre-existing finding should be preserved"
        assert "Found 200 more rows" in task.body, "New finding should be appended"
        # Verify structural integrity: exactly one ## Results and one ### Key Findings
        assert task.body.count("## Results") == 1
        assert task.body.count("### Key Findings") == 1


class TestReviewedCliTaskRootDefaults:
    def test_reviewed_clis_autodetect_superra_from_repo_dir(self, plan_root, monkeypatch):
        """Reviewed CLIs run from a repo dir without an explicit --plan-root."""
        monkeypatch.chdir(plan_root.parent)

        task_update.main(["--propagate-all"])
        task_update.main(["--path", "02-second", "--status", "in-progress"])
        task_add_result.main([
            "--path", "02-second",
            "--finding", "CLI autodetected the task root",
        ])
        task_link.main([
            "--path", "03-third",
            "--depends-on", "01-first",
        ])
        task_rename.main([
            "--from", "01-first",
            "--to", "01-first-renamed",
        ])

        with pytest.raises(SystemExit) as excinfo:
            task_check.main([])
        assert excinfo.value.code == 0

        second = _task_io.parse_task(plan_root / "02-second" / "task.md")
        third = _task_io.parse_task(plan_root / "03-third" / "task.md")
        assert second.status == "in-progress"
        assert "CLI autodetected the task root" in second.body
        assert "01-first-renamed" in second.depends_on
        assert "01-first-renamed" in third.depends_on

    def test_explicit_plan_root_override_is_preserved(self, tmp_path, monkeypatch):
        """An explicit legacy path overrides a visible superRA/ task root."""
        superra_root = tmp_path / "superRA"
        superra_root.mkdir()
        _write_task_md(superra_root / "task.md", "SuperRA", "not-started")
        superra_task = superra_root / "01-target"
        superra_task.mkdir()
        _write_task_md(superra_task / "task.md", "SuperRA Target", "not-started")

        legacy_root = tmp_path / ".plan"
        legacy_root.mkdir()
        _write_task_md(legacy_root / "task.md", "Legacy", "not-started")
        legacy_task = legacy_root / "01-target"
        legacy_task.mkdir()
        _write_task_md(legacy_task / "task.md", "Legacy Target", "not-started")

        monkeypatch.chdir(tmp_path)
        task_add_result.main([
            "--plan-root", str(legacy_root),
            "--path", "01-target",
            "--finding", "explicit legacy override",
        ])

        legacy = _task_io.parse_task(legacy_task / "task.md")
        current = _task_io.parse_task(superra_task / "task.md")
        assert "explicit legacy override" in legacy.body
        assert "explicit legacy override" not in current.body

    def test_task_check_autodetects_legacy_plan_root(self, tmp_path, monkeypatch):
        """Legacy .plan/ remains readable when superRA/ is absent."""
        legacy_root = tmp_path / ".plan"
        legacy_root.mkdir()
        _write_task_md(legacy_root / "task.md", "Legacy", "not-started")
        child = legacy_root / "01-child"
        child.mkdir()
        _write_task_md(child / "task.md", "Child", "not-started")

        monkeypatch.chdir(tmp_path)
        with pytest.raises(SystemExit) as excinfo:
            task_check.main([])
        assert excinfo.value.code == 0

    def test_reviewed_cli_help_describes_autodetect_task_root(self, capsys):
        """The reviewed CLIs document optional task-root auto-detection."""
        parsers = [
            task_update.parse_args,
            task_add_result.parse_args,
            task_link.parse_args,
            task_rename.parse_args,
            task_check.parse_args,
        ]

        for parse in parsers:
            with pytest.raises(SystemExit) as excinfo:
                parse(["--help"])
            assert excinfo.value.code == 0
            out = capsys.readouterr().out
            assert "--plan-root" in out
            assert "task root directory" in out
            assert "auto-detect" in out
            assert "superRA" in out


class TestCollectAllTasks:
    def test_depth_first_excluding_root(self, plan_root):
        """collect_all_tasks returns depth-first ordered list excluding root."""
        root = _task_io.walk_plan(plan_root)
        all_tasks = _task_io.collect_all_tasks(root)
        paths = [t.path for t in all_tasks]
        assert "" not in paths, "Root should be excluded"
        assert paths == ["01-first", "02-second", "03-third"]

    def test_nested_depth_first(self, plan_with_branches):
        """Nested plan returns children in depth-first order."""
        root = _task_io.walk_plan(plan_with_branches)
        all_tasks = _task_io.collect_all_tasks(root)
        paths = [t.path for t in all_tasks]
        assert "" not in paths
        assert paths == [
            "01-data-prep",
            "01-data-prep/01-load",
            "01-data-prep/02-merge",
            "02-estimation",
        ]


class TestTaskQuery:
    def test_tree_to_json(self, plan_root):
        root = _task_io.walk_plan(plan_root)
        data = task_query.tree_to_json(root)
        assert data["title"] == "Test Project"
        assert len(data["children"]) == 3
        assert data["children"][0]["is_leaf"] is True
        # Verify v2 fields are present in JSON output
        for key in ("objective", "results", "decisions", "revision_notes", "review_notes"):
            assert key in data, f"Missing key {key!r} in tree_to_json output"
        first_child = data["children"][0]
        assert "Complete step 1." in first_child["objective"]
        assert "Found 100 rows" in first_child["results"]

    def test_render_dag(self, plan_root):
        root = _task_io.walk_plan(plan_root)
        mermaid = task_query.render_dag(root)
        assert "graph LR" in mermaid
        assert "01-first" in mermaid
        assert "02-second" in mermaid
        assert "01-first --> 02-second" in mermaid

    def test_render_dag_with_subtree_success(self, plan_with_branches):
        """render_dag with a valid subtree_path renders only that subtree."""
        root = _task_io.walk_plan(plan_with_branches)
        mermaid = task_query.render_dag(root, subtree_path="01-data-prep")
        assert "graph LR" in mermaid
        assert "01-load" in mermaid
        assert "02-merge" in mermaid
        # Should NOT contain the sibling estimation task
        assert "02-estimation" not in mermaid

    def test_render_dag_with_nonexistent_subtree_exits(self, plan_root):
        """render_dag with a non-existent subtree_path calls sys.exit(1)."""
        root = _task_io.walk_plan(plan_root)
        with pytest.raises(SystemExit) as exc_info:
            task_query.render_dag(root, subtree_path="99-nonexistent")
        assert exc_info.value.code == 1


# --- Migration tests ---


class TestPlanMigrate:
    def test_slugify(self):
        assert plan_migrate.slugify("Load Raw Data") == "load-raw-data"
        assert plan_migrate.slugify("Merge & Clean (v2)") == "merge-clean-v2"

    def test_migrate_basic(self, tmp_path):
        plan_md = tmp_path / "PLAN.md"
        plan_md.write_text(
            "# Test Analysis Plan\n\n**Objective:** Test\n\n---\n\n"
            "### Task 1: Load Data\n"
            "**Depends on:** *(none)*\n"
            "**Script:** `Code/01_load.py`\n"
            "**Input:** `Data/raw.csv`\n"
            "**Output:** `Data/clean.parquet`\n\n"
            "- [x] **Step 1: Read CSV**\n\n"
            "```python\ndf = pd.read_csv('Data/raw.csv')\n```\n\n"
            "- [x] **Step 2: Clean**\n\n"
            "### Task 2: Analyze\n"
            "**Depends on:** Task 1\n"
            "**Script:** `Code/02_analyze.py`\n\n"
            "- [ ] **Step 1: Compute stats**\n",
            encoding="utf-8",
        )

        results_md = tmp_path / "RESULTS.md"
        results_md.write_text(
            "# Test Analysis — Results\n\n"
            "## Task 1: Load Data\n\n"
            "**Status:** Completed\n\n"
            "### Key Findings\n- 1000 rows loaded\n- 5 columns\n\n"
            "## Task 2: Analyze\n\n"
            "**Status:** Not started\n",
            encoding="utf-8",
        )

        output = tmp_path / "superRA"
        plan_migrate.migrate(plan_md, results_md, output)

        assert (output / "task.md").exists()
        assert (output / "01-load-data" / "task.md").exists()
        assert (output / "02-analyze" / "task.md").exists()

        t1 = _task_io.parse_task(output / "01-load-data" / "task.md")
        assert t1.title == "Load Data"
        assert t1.script == "Code/01_load.py"
        assert t1.input == ["Data/raw.csv"]
        assert t1.output == ["Data/clean.parquet"]
        assert "1000 rows loaded" in t1.body
        # Migration should produce v2 format
        content = (output / "01-load-data" / "task.md").read_text(encoding="utf-8")
        assert "## Objective" in content
        assert "## Steps" not in content

        # Migrated files should not contain stale status fields
        assert "review_status" not in content
        assert "integration_status" not in content

        t2 = _task_io.parse_task(output / "02-analyze" / "task.md")
        assert "01-load-data" in t2.depends_on
        root_content = (output / "task.md").read_text(encoding="utf-8")
        assert "review_status" not in root_content
        assert "integration_status" not in root_content


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
        assert dashboard_artifact_workflow.sanitize_artifact_slug("analysis/task_system.v2") == "analysis-task_system.v2"
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
        assert "uv run --project skills/task-system superra dashboard export --root \"superRA\"" in workflow
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
        )
        workflow = dashboard_artifact_workflow.render_workflow(config)
        assert 'uv run --project skills/task-system superra dashboard export --root "customRA"' in workflow
        assert '--output "build/custom-dashboard.html"' in workflow
        assert "custom-dashboard-$slug-$ref_hash" in workflow
        assert "retention-days: 3" in workflow
        assert "skipping dashboard artifact" in workflow


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


# --- parse_body_sections tests ---


class TestParseBodySections:
    def test_all_sections(self):
        body = (
            "## Objective\n\nDo the thing.\n\n"
            "## Planner Guidance\n\nTry the obvious path.\n\n"
            "## Results\n\n### Key Findings\n- Found it\n\n"
            "## Decisions\n\n> Use method A\n\n"
            "## Revision Notes\n\nChanged scope to X.\n\n"
            "## Review Notes\n\n> [MAJOR] Fix this\n"
        )
        sections = parse_body_sections(body)
        assert "Objective" in sections
        assert "Do the thing." in sections["Objective"]
        assert "Planner Guidance" in sections
        assert "Try the obvious path." in sections["Planner Guidance"]
        assert "Results" in sections
        assert "Decisions" in sections
        assert "Revision Notes" in sections
        assert "Changed scope to X." in sections["Revision Notes"]
        assert "Review Notes" in sections

    def test_objective_only(self):
        body = "## Objective\n\nJust the objective.\n"
        sections = parse_body_sections(body)
        assert len(sections) == 1
        assert "Objective" in sections

    def test_empty_body(self):
        sections = parse_body_sections("")
        assert sections == {}

    def test_unknown_sections_preserved(self):
        body = "## Custom Section\n\nContent here.\n"
        sections = parse_body_sections(body)
        assert "Custom Section" in sections

    def test_fenced_header_not_a_section(self):
        # A `## ` line quoted inside a code fence is body content, not a header:
        # it must neither start a phantom section nor truncate the section that
        # contains the fence.
        body = (
            "## Objective\n\n"
            "Embed a template:\n\n"
            "```\n"
            "## Results\n"
            "fake\n"
            "```\n\n"
            "Real objective tail.\n\n"
            "## Results\n\nActual results.\n"
        )
        sections = parse_body_sections(body)
        assert "Real objective tail." in sections["Objective"]
        assert "fake" in sections["Objective"]  # fenced content stays in Objective
        assert sections["Results"].strip() == "Actual results."


# --- Auto-rebuild tests ---


class TestAutoRebuild:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.plan_root = Path(self.tmpdir) / "superRA"
        self.plan_root.mkdir()
        # Create root task.md
        _write_task_md(self.plan_root / "task.md", "Root", "not-started")
        # Create initial dashboard
        plan_dashboard.generate_dashboard(self.plan_root)
        self.dashboard = self.plan_root / "dashboard.html"
        assert self.dashboard.exists()
        self.initial_content = self.dashboard.read_text()

    def teardown_method(self):
        shutil.rmtree(self.tmpdir)

    def test_create_triggers_rebuild(self):
        task_create.create_task(self.plan_root, "01-first", "First Task")
        new_content = self.dashboard.read_text()
        assert "First Task" in new_content
        assert new_content != self.initial_content

    def test_update_triggers_rebuild(self):
        task_create.create_task(self.plan_root, "01-first", "First Task")
        content_after_create = self.dashboard.read_text()
        task_update.update_task(self.plan_root, "01-first", status="in-progress")
        content_after_update = self.dashboard.read_text()
        assert content_after_update != content_after_create


# --- v1-to-v2 upgrade tests ---


class TestMigrateV2:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.plan_root = Path(self.tmpdir) / "superRA"
        self.plan_root.mkdir()

    def teardown_method(self):
        shutil.rmtree(self.tmpdir)

    def test_upgrade_steps_to_objective(self):
        # Write a v1-format task.md with ## Steps and checkboxes
        task_dir = self.plan_root / "01-task"
        task_dir.mkdir()
        v1_content = (
            '---\ntitle: "Test Task"\nstatus: not-started\nreview_status: ~\n'
            "integration_status: ~\ndepends_on: []\ntags: []\n"
            "created: 2026-01-01\n---\n\n"
            "# Test Task\n\n## Steps\n\n"
            "- [ ] Step 1: Do first thing\n"
            "- [x] Step 2: Do second thing\n\n"
            "## Results\n\n### Key Findings\n- Found something\n"
        )
        (task_dir / "task.md").write_text(v1_content)
        # Also write root task.md
        _write_task_md(self.plan_root / "task.md", "Root", "not-started")

        modified = plan_migrate.upgrade_v1_to_v2(self.plan_root)

        assert len(modified) == 1  # only the v1 file, not root
        content = (task_dir / "task.md").read_text()
        assert "## Objective" in content
        assert "## Steps" not in content
        assert "# Test Task" not in content  # title heading removed
        assert "- [ ]" not in content  # checkboxes stripped
        assert "- [x]" not in content
        assert "Step 1: Do first thing" in content  # text preserved
        assert "## Results" in content  # results preserved

    def test_idempotent(self):
        task_dir = self.plan_root / "01-task"
        task_dir.mkdir()
        v2_content = (
            '---\ntitle: "Test Task"\nstatus: not-started\nreview_status: ~\n'
            "integration_status: ~\ndepends_on: []\ntags: []\n"
            "created: 2026-01-01\n---\n\n"
            "## Objective\n\nAlready in v2 format.\n\n"
            "## Results\n\n"
        )
        (task_dir / "task.md").write_text(v2_content)
        _write_task_md(self.plan_root / "task.md", "Root", "not-started")

        modified = plan_migrate.upgrade_v1_to_v2(self.plan_root)
        assert len(modified) == 0  # nothing changed


# --- Status consolidation upgrade tests ---


class TestUpgradeStatus:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.plan_root = Path(self.tmpdir) / "superRA"
        self.plan_root.mkdir()
        _write_task_md(self.plan_root / "task.md", "Root", "not-started")

    def teardown_method(self):
        shutil.rmtree(self.tmpdir)

    def test_strips_review_and_integration_status(self):
        """Removes review_status and integration_status from frontmatter."""
        task_dir = self.plan_root / "01-task"
        task_dir.mkdir()
        _write_task_md(task_dir / "task.md", "Task A", "implemented",
                       review_status="approved", integration_status="~")

        modified = plan_migrate.upgrade_status(self.plan_root)
        assert len(modified) >= 1
        content = (task_dir / "task.md").read_text(encoding="utf-8")
        assert "review_status" not in content
        assert "integration_status" not in content

    def test_review_status_takes_precedence_over_status(self):
        """review_status overrides status when integration_status is ~."""
        task_dir = self.plan_root / "01-task"
        task_dir.mkdir()
        _write_task_md(task_dir / "task.md", "Task A", "implemented",
                       review_status="approved", integration_status="~")

        plan_migrate.upgrade_status(self.plan_root)
        fm, _ = _task_io.parse_frontmatter(
            (task_dir / "task.md").read_text(encoding="utf-8")
        )
        assert fm["status"] == "approved"

    def test_integration_status_takes_precedence_over_review(self):
        """integration_status overrides both review_status and status."""
        task_dir = self.plan_root / "01-task"
        task_dir.mkdir()
        _write_task_md(task_dir / "task.md", "Task A", "implemented",
                       review_status="approved", integration_status="revise")

        plan_migrate.upgrade_status(self.plan_root)
        fm, _ = _task_io.parse_frontmatter(
            (task_dir / "task.md").read_text(encoding="utf-8")
        )
        assert fm["status"] == "revise"

    def test_status_preserved_when_no_overrides(self):
        """When review/integration are both ~, status is kept as-is."""
        task_dir = self.plan_root / "01-task"
        task_dir.mkdir()
        _write_task_md(task_dir / "task.md", "Task A", "in-progress",
                       review_status="~", integration_status="~")

        plan_migrate.upgrade_status(self.plan_root)
        fm, _ = _task_io.parse_frontmatter(
            (task_dir / "task.md").read_text(encoding="utf-8")
        )
        assert fm["status"] == "in-progress"

    def test_removes_workflow_status_section(self):
        """Strips ## Workflow Status sections from the task body."""
        task_dir = self.plan_root / "01-task"
        task_dir.mkdir()
        content = (
            '---\ntitle: "Task A"\nstatus: approved\nreview_status: approved\n'
            "integration_status: ~\ndepends_on: []\ntags: []\n"
            "created: 2026-01-01\n---\n\n"
            "## Objective\n\nDo the thing.\n\n"
            "## Workflow Status\n\nPhase: implementation\n\n"
            "## Results\n\nDone.\n"
        )
        (task_dir / "task.md").write_text(content, encoding="utf-8")

        plan_migrate.upgrade_status(self.plan_root)
        new_content = (task_dir / "task.md").read_text(encoding="utf-8")
        assert "## Workflow Status" not in new_content
        assert "Phase: implementation" not in new_content
        assert "## Objective" in new_content
        assert "## Results" in new_content

    def test_dry_run_does_not_write(self):
        """--dry-run reports changes without modifying files."""
        task_dir = self.plan_root / "01-task"
        task_dir.mkdir()
        _write_task_md(task_dir / "task.md", "Task A", "implemented",
                       review_status="approved", integration_status="~")
        original = (task_dir / "task.md").read_text(encoding="utf-8")

        modified = plan_migrate.upgrade_status(self.plan_root, dry_run=True)
        assert len(modified) >= 1
        # File should be unchanged
        assert (task_dir / "task.md").read_text(encoding="utf-8") == original

    def test_idempotent_on_already_clean_files(self):
        """Files without review_status/integration_status are not touched."""
        task_dir = self.plan_root / "01-task"
        task_dir.mkdir()
        _write_task_md(task_dir / "task.md", "Task A", "approved")

        modified = plan_migrate.upgrade_status(self.plan_root)
        assert len(modified) == 0

    def test_multiple_files_upgraded(self):
        """All task.md files in the tree are processed."""
        for i in range(1, 4):
            d = self.plan_root / f"{i:02d}-task"
            d.mkdir()
            _write_task_md(d / "task.md", f"Task {i}", "implemented",
                           review_status="approved", integration_status="~")

        modified = plan_migrate.upgrade_status(self.plan_root)
        # Root + 3 tasks, but root has no stale fields so only 3 modified
        assert len(modified) == 3


class TestMigrationMapping:
    """Tests for _compute_status_from_steps migration mapping in PLAN.md migration."""

    def test_integration_status_wins(self, tmp_path):
        """When PLAN.md has integration_status, it determines the unified status."""
        plan_md = tmp_path / "PLAN.md"
        plan_md.write_text(
            "# Test Plan\n\n---\n\n"
            "### Task 1: Done Task\n"
            "**Depends on:** *(none)*\n"
            "**Review status:** approved\n"
            "**Integration status:** revise\n\n"
            "- [x] Step 1\n",
            encoding="utf-8",
        )
        output = tmp_path / "superRA"
        plan_migrate.migrate(plan_md, None, output)
        fm, _ = _task_io.parse_frontmatter(
            (output / "01-done-task" / "task.md").read_text(encoding="utf-8")
        )
        assert fm["status"] == "revise"

    def test_review_status_wins_over_checkbox(self, tmp_path):
        """When review_status is set but integration_status is not, review wins."""
        plan_md = tmp_path / "PLAN.md"
        plan_md.write_text(
            "# Test Plan\n\n---\n\n"
            "### Task 1: Reviewed Task\n"
            "**Depends on:** *(none)*\n"
            "**Review status:** approved\n\n"
            "- [x] Step 1\n",
            encoding="utf-8",
        )
        output = tmp_path / "superRA"
        plan_migrate.migrate(plan_md, None, output)
        fm, _ = _task_io.parse_frontmatter(
            (output / "01-reviewed-task" / "task.md").read_text(encoding="utf-8")
        )
        assert fm["status"] == "approved"

    def test_checkbox_fallback(self, tmp_path):
        """When no review/integration status, checkboxes determine status."""
        plan_md = tmp_path / "PLAN.md"
        plan_md.write_text(
            "# Test Plan\n\n---\n\n"
            "### Task 1: Partial Task\n"
            "**Depends on:** *(none)*\n\n"
            "- [x] Step 1\n"
            "- [ ] Step 2\n",
            encoding="utf-8",
        )
        output = tmp_path / "superRA"
        plan_migrate.migrate(plan_md, None, output)
        fm, _ = _task_io.parse_frontmatter(
            (output / "01-partial-task" / "task.md").read_text(encoding="utf-8")
        )
        assert fm["status"] == "in-progress"


# --- Validation function tests ---


class TestValidateFrontmatter:
    def test_valid_task_no_warnings(self, plan_root):
        task = _task_io.parse_task(plan_root / "01-first" / "task.md")
        warnings = _task_io.validate_frontmatter(task)
        assert warnings == []

    def test_bad_status_value(self, plan_root):
        task = _task_io.parse_task(plan_root / "02-second" / "task.md")
        task.status = "done"  # invalid enum value
        warnings = _task_io.validate_frontmatter(task)
        assert any("invalid status" in w for w in warnings)
        assert any("done" in w for w in warnings)

    def test_depends_on_not_list(self, plan_root):
        task = _task_io.parse_task(plan_root / "02-second" / "task.md")
        task.depends_on = "01-first"  # string instead of list
        warnings = _task_io.validate_frontmatter(task)
        assert any("depends_on" in w for w in warnings)

    def test_empty_title_warning(self, plan_root):
        task = _task_io.parse_task(plan_root / "01-first" / "task.md")
        task.title = ""
        warnings = _task_io.validate_frontmatter(task)
        assert any("title" in w for w in warnings)

    def test_tags_not_list(self, plan_root):
        task = _task_io.parse_task(plan_root / "01-first" / "task.md")
        task.tags = "data"  # string instead of list
        warnings = _task_io.validate_frontmatter(task)
        assert any("tags" in w for w in warnings)


class TestValidateDependencies:
    def test_valid_dep_no_warnings(self, plan_root):
        task = _task_io.parse_task(plan_root / "02-second" / "task.md")
        warnings = _task_io.validate_dependencies(task, ["01-first", "02-second", "03-third"])
        assert warnings == []

    def test_missing_sibling_ref(self, plan_root):
        task = _task_io.parse_task(plan_root / "02-second" / "task.md")
        # Pass siblings that don't include 01-first
        warnings = _task_io.validate_dependencies(task, ["02-second", "03-third"])
        assert len(warnings) == 1
        assert "01-first" in warnings[0]
        assert "does not match" in warnings[0]

    def test_nonexistent_dep(self, plan_root):
        task = _task_io.parse_task(plan_root / "02-second" / "task.md")
        task.depends_on = ["nonexistent"]
        warnings = _task_io.validate_dependencies(task, ["01-first", "02-second"])
        assert any("nonexistent" in w for w in warnings)

    def test_no_deps_no_warnings(self, plan_root):
        task = _task_io.parse_task(plan_root / "01-first" / "task.md")
        assert task.depends_on == []
        warnings = _task_io.validate_dependencies(task, ["01-first"])
        assert warnings == []


class TestDetectCycles:
    def _make_tasks(self, tmp_path, specs):
        """Create tasks from (slug, deps) specs. Returns list of Task objects."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir(exist_ok=True)
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        for slug, deps in specs:
            d = root_dir / slug
            d.mkdir(exist_ok=True)
            _write_task_md(d / "task.md", slug, "not-started", depends_on=deps)
        tasks = []
        for slug, _deps in specs:
            tasks.append(_task_io.parse_task(root_dir / slug / "task.md"))
        return tasks

    def test_no_cycle(self, tmp_path):
        tasks = self._make_tasks(tmp_path, [
            ("01-a", []),
            ("02-b", ["01-a"]),
            ("03-c", ["02-b"]),
        ])
        warnings = _task_io.detect_cycles(tasks)
        assert warnings == []

    def test_simple_cycle(self, tmp_path):
        tasks = self._make_tasks(tmp_path, [
            ("01-a", ["02-b"]),
            ("02-b", ["01-a"]),
        ])
        warnings = _task_io.detect_cycles(tasks)
        assert len(warnings) >= 1
        assert any("cycle" in w.lower() for w in warnings)

    def test_three_node_cycle(self, tmp_path):
        tasks = self._make_tasks(tmp_path, [
            ("01-a", ["03-c"]),
            ("02-b", ["01-a"]),
            ("03-c", ["02-b"]),
        ])
        warnings = _task_io.detect_cycles(tasks)
        assert any("cycle" in w.lower() for w in warnings)
        # Cycle description should mention the nodes involved
        cycle_msg = warnings[0]
        assert "->" in cycle_msg

    def test_independent_tasks_no_cycle(self, tmp_path):
        tasks = self._make_tasks(tmp_path, [
            ("01-a", []),
            ("02-b", []),
            ("03-c", []),
        ])
        warnings = _task_io.detect_cycles(tasks)
        assert warnings == []


class TestValidatePlan:
    def test_valid_plan_no_warnings(self, plan_root):
        warnings = _task_io.validate_plan(plan_root)
        assert warnings == []

    def test_missing_dep_produces_warning(self, plan_root):
        # Add a task with a depends_on pointing to a nonexistent sibling
        bad_dir = plan_root / "04-bad"
        bad_dir.mkdir()
        _write_task_md(bad_dir / "task.md", "Bad Task", "not-started",
                       depends_on=["99-nonexistent"])
        warnings = _task_io.validate_plan(plan_root)
        assert any("nonexistent" in w for w in warnings)

    def test_warnings_prefixed_with_task_path(self, plan_root):
        bad_dir = plan_root / "04-bad"
        bad_dir.mkdir()
        _write_task_md(bad_dir / "task.md", "Bad Task", "not-started",
                       depends_on=["99-nonexistent"])
        warnings = _task_io.validate_plan(plan_root)
        # Each warning should be prefixed with the task path
        assert any(w.startswith("04-bad:") for w in warnings)

    def test_cycle_produces_warning(self, tmp_path):
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        d1 = root_dir / "01-a"
        d1.mkdir()
        _write_task_md(d1 / "task.md", "A", "not-started", depends_on=["02-b"])
        d2 = root_dir / "02-b"
        d2.mkdir()
        _write_task_md(d2 / "task.md", "B", "not-started", depends_on=["01-a"])
        warnings = _task_io.validate_plan(root_dir)
        assert any("cycle" in w.lower() for w in warnings)


# --- Topological sort tests ---


class TestTopologicalSort:
    def _make_plan(self, tmp_path, specs):
        """Create plan from list of (slug, title, deps) specs."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        for slug, title, deps in specs:
            d = root_dir / slug
            d.mkdir()
            _write_task_md(d / "task.md", title, "not-started", depends_on=deps)
        return root_dir

    def test_dep_order_b_after_a(self, tmp_path):
        """If B depends on A, order must be A then B (not alphabetical B before A)."""
        root_dir = self._make_plan(tmp_path, [
            ("02-b", "B Task", ["01-a"]),
            ("01-a", "A Task", []),
        ])
        root = _task_io.walk_plan(root_dir)
        slugs = [c.slug for c in root.children]
        assert slugs.index("01-a") < slugs.index("02-b")

    def test_independent_tasks_alphabetical(self, tmp_path):
        """Independent tasks sorted alphabetically by slug (tiebreaker)."""
        root_dir = self._make_plan(tmp_path, [
            ("03-c", "C", []),
            ("01-a", "A", []),
            ("02-b", "B", []),
        ])
        root = _task_io.walk_plan(root_dir)
        slugs = [c.slug for c in root.children]
        assert slugs == ["01-a", "02-b", "03-c"]

    def test_diamond_order(self, tmp_path):
        """Diamond: A and B independent, C depends on both A and B. Order: A, B, C."""
        root_dir = self._make_plan(tmp_path, [
            ("01-a", "A", []),
            ("02-b", "B", []),
            ("03-c", "C", ["01-a", "02-b"]),
        ])
        root = _task_io.walk_plan(root_dir)
        slugs = [c.slug for c in root.children]
        assert slugs.index("01-a") < slugs.index("03-c")
        assert slugs.index("02-b") < slugs.index("03-c")
        # A and B are independent, so alphabetical tiebreaker applies
        assert slugs.index("01-a") < slugs.index("02-b")

    def test_missing_dep_falls_back_to_alphabetical(self, tmp_path):
        """Missing dep slug: warn and fall back to alphabetical for that task."""
        root_dir = self._make_plan(tmp_path, [
            ("02-b", "B", ["99-missing"]),
            ("01-a", "A", []),
        ])
        root = _task_io.walk_plan(root_dir)
        slugs = [c.slug for c in root.children]
        # Both tasks must appear; exact order may vary but no crash
        assert "01-a" in slugs
        assert "02-b" in slugs


# --- task_read tests ---


class TestTaskRead:
    def test_leaf_with_ancestor_context(self, plan_root):
        """read task at 02-second — output contains ancestor chain and task header."""
        ancestors = task_read._collect_ancestors(plan_root, "02-second")
        assert len(ancestors) == 1  # root only
        assert ancestors[0].is_root

    def test_root_task_no_ancestors(self, plan_root):
        """Root task has no ancestors."""
        ancestors = task_read._collect_ancestors(plan_root, "")
        assert ancestors == []

    def test_no_ancestors_flag(self, plan_root):
        """render_human with show_ancestors=False omits the ancestor section."""
        target = _task_io.parse_task(plan_root / "02-second" / "task.md")
        siblings = task_read._sibling_map(plan_root, target)
        dep_pairs = task_read._dep_tasks(target, siblings)
        output = task_read.render_human(
            ancestors=[],
            target_task=target,
            dep_pairs=dep_pairs,
            show_ancestors=False,
        )
        assert "=== Context ===" not in output
        assert "Ancestor Context" not in output
        assert "Second Task" in output

    def test_context_header_renamed(self, plan_root):
        """The Context block uses the `=== Context ===` header, not the old name."""
        target = _task_io.parse_task(plan_root / "02-second" / "task.md")
        ancestors = task_read._collect_ancestors(plan_root, target.path)
        siblings = task_read._sibling_map(plan_root, target)
        dep_pairs = task_read._dep_tasks(target, siblings)
        root = _task_io.walk_plan(plan_root)
        tree = task_query.format_focused_tree(root, target.path)
        output = task_read.render_human(
            ancestors, target, dep_pairs, show_ancestors=True, focused_tree=tree
        )
        assert "=== Context ===" in output
        assert "Ancestor Context" not in output

    def test_focused_tree_marks_current_and_shows_siblings(self, plan_root):
        """Focused tree marks the current node and lists its siblings."""
        target = _task_io.parse_task(plan_root / "02-second" / "task.md")
        root = _task_io.walk_plan(plan_root)
        tree = task_query.format_focused_tree(root, target.path)
        # Current node is marked.
        marked = [ln for ln in tree.splitlines() if "← this task" in ln]
        assert len(marked) == 1
        assert "02-second" in marked[0]
        # Siblings appear, unmarked.
        assert "01-first" in tree
        assert "03-third" in tree
        assert tree.count("← this task") == 1

    def test_focused_tree_shows_children_not_unrelated_branches(self, plan_with_branches):
        """Focused tree shows the target's direct children but not unrelated ancestor branches."""
        root = _task_io.walk_plan(plan_with_branches)
        # Target is the branch task 01-data-prep, which has children 01-load, 02-merge.
        tree = task_query.format_focused_tree(root, "01-data-prep")
        assert "← this task" in tree
        # Direct children of the target are shown.
        assert "01-load" in tree
        assert "02-merge" in tree
        # The sibling branch 02-estimation is shown (it is a sibling of the target)...
        assert "02-estimation" in tree
        # ...but its descendants are NOT expanded (unrelated branch).
        for line in tree.splitlines():
            assert "estimation" not in line or "02-estimation" in line

    def test_focused_tree_deep_leaf_no_ancestor_sibling_branches(self, plan_with_branches):
        """For a deep leaf, ancestor-sibling branches are not expanded."""
        root = _task_io.walk_plan(plan_with_branches)
        # Target 01-data-prep/02-merge: its parent's sibling (02-estimation)
        # must appear (it is an ancestor sibling) but unexpanded; the target's
        # own siblings (01-load) must appear.
        tree = task_query.format_focused_tree(root, "01-data-prep/02-merge")
        assert "← this task" in tree
        marked = [ln for ln in tree.splitlines() if "← this task" in ln]
        assert "02-merge" in marked[0]
        assert "01-load" in tree  # target sibling
        # 02-estimation is a sibling of the target's parent. It is NOT on the
        # spine and NOT a sibling of the target, so the focused form does not
        # show it at all.
        assert "02-estimation" not in tree

    def test_json_output_keys(self, plan_root):
        """render_json returns valid JSON with ancestors, task, dependencies keys."""
        target = _task_io.parse_task(plan_root / "02-second" / "task.md")
        ancestors = task_read._collect_ancestors(plan_root, target.path)
        siblings = task_read._sibling_map(plan_root, target)
        dep_pairs = task_read._dep_tasks(target, siblings)
        json_str = task_read.render_json(ancestors, target, dep_pairs)
        data = json.loads(json_str)
        assert "ancestors" in data
        assert "task" in data
        assert "dependencies" in data

    def test_planner_guidance_rendered_in_human_output(self, plan_root):
        task_md = plan_root / "02-second" / "task.md"
        task_md.write_text(
            task_md.read_text(encoding="utf-8")
            + "\n## Planner Guidance\n\nUse the current helper if it fits.\n",
            encoding="utf-8",
        )
        target = _task_io.parse_task(task_md)
        output = task_read.render_human([], target, [], show_ancestors=False)
        assert "## Planner Guidance" in output
        assert "Use the current helper if it fits." in output

    def test_planner_guidance_rendered_in_json_sections(self, plan_root):
        task_md = plan_root / "02-second" / "task.md"
        task_md.write_text(
            task_md.read_text(encoding="utf-8")
            + "\n## Planner Guidance\n\nUse the current helper if it fits.\n",
            encoding="utf-8",
        )
        target = _task_io.parse_task(task_md)
        data = json.loads(task_read.render_json([], target, [], show_ancestors=False))
        assert data["task"]["sections"]["Planner Guidance"] == (
            "Use the current helper if it fits."
        )

    def test_json_ancestors_list(self, plan_root):
        """ancestors in JSON output is a list of dicts with path/title fields."""
        target = _task_io.parse_task(plan_root / "02-second" / "task.md")
        ancestors = task_read._collect_ancestors(plan_root, target.path)
        siblings = task_read._sibling_map(plan_root, target)
        dep_pairs = task_read._dep_tasks(target, siblings)
        data = json.loads(task_read.render_json(ancestors, target, dep_pairs))
        assert isinstance(data["ancestors"], list)
        assert all("path" in a and "title" in a for a in data["ancestors"])

    def test_sibling_dep_status_shown(self, plan_root):
        """Sibling dependency status + title appear in human output."""
        target = _task_io.parse_task(plan_root / "02-second" / "task.md")
        siblings = task_read._sibling_map(plan_root, target)
        dep_pairs = task_read._dep_tasks(target, siblings)
        output = task_read.render_human([], target, dep_pairs, show_ancestors=False)
        # 01-first is approved; its status and title should appear
        assert "01-first" in output
        assert "approved" in output

    def test_autodetect_plan_root(self, plan_root):
        """Auto-detect plan root from a subdirectory inside the plan."""
        detected = task_read._autodetect_plan_root(plan_root / "01-first")
        assert detected == plan_root

    def test_autodetect_plan_root_from_repo_subdirectory(self, plan_root):
        """Auto-detect sibling task root while walking up from normal repo dirs."""
        repo_dir = plan_root.parent
        nested = repo_dir / "skills" / "task-system"
        nested.mkdir(parents=True)
        detected = task_read._autodetect_plan_root(nested)
        assert detected == plan_root

    def test_autodetect_returns_none_outside_plan(self, tmp_path):
        """Returns None when called from a directory with no task.md ancestry."""
        detected = task_read._autodetect_plan_root(tmp_path)
        assert detected is None

    def test_no_ancestors_in_json(self, plan_root):
        """--no-ancestors: JSON ancestors list is empty."""
        target = _task_io.parse_task(plan_root / "02-second" / "task.md")
        siblings = task_read._sibling_map(plan_root, target)
        dep_pairs = task_read._dep_tasks(target, siblings)
        data = json.loads(
            task_read.render_json([], target, dep_pairs, show_ancestors=False)
        )
        assert data["ancestors"] == []

    def test_nested_ancestor_chain(self, plan_with_branches):
        """Two-level deep task has both root and immediate parent as ancestors."""
        ancestors = task_read._collect_ancestors(
            plan_with_branches, "01-data-prep/02-merge"
        )
        paths = [a.path for a in ancestors]
        # root (path="") and 01-data-prep should be in ancestors
        assert "" in paths
        assert "01-data-prep" in paths

    def test_ancestor_objective_full_not_truncated(self, plan_root):
        """Human output shows the full ancestor ## Objective, beyond 10 lines and
        including nested ### subsections."""
        long_objective = (
            "\n".join(f"Objective line {i}." for i in range(1, 16))
            + "\n\n### Conventions\n\nUse left joins throughout the subtree."
        )
        root_md = plan_root / "task.md"
        _write_task_md(root_md, "Test Project", "not-started",
                       objective=long_objective)
        ancestors = task_read._collect_ancestors(plan_root, "02-second")
        target = _task_io.parse_task(plan_root / "02-second" / "task.md")
        siblings = task_read._sibling_map(plan_root, target)
        dep_pairs = task_read._dep_tasks(target, siblings)
        output = task_read.render_human(ancestors, target, dep_pairs)
        assert "Objective line 15." in output  # past old 10-line cap
        assert "..." not in output.split("=== Task:")[0]  # no truncation marker
        assert "### Conventions" in output
        assert "Use left joins throughout the subtree." in output

    def test_ancestor_objective_field_in_json_preserves_keys(self, plan_root):
        """JSON ancestors carry an explicit full `objective` field while keeping
        the existing keys (first_section, sections, path, title, status)."""
        long_objective = (
            "\n".join(f"Objective line {i}." for i in range(1, 16))
            + "\n\n### Constraints\n\nNever drop rows during the merge."
        )
        root_md = plan_root / "task.md"
        _write_task_md(root_md, "Test Project", "not-started",
                       objective=long_objective)
        ancestors = task_read._collect_ancestors(plan_root, "02-second")
        target = _task_io.parse_task(plan_root / "02-second" / "task.md")
        siblings = task_read._sibling_map(plan_root, target)
        dep_pairs = task_read._dep_tasks(target, siblings)
        data = json.loads(task_read.render_json(ancestors, target, dep_pairs))
        root_anc = next(a for a in data["ancestors"] if a["path"] == "")
        # New explicit field carries the full objective including ### subsection.
        assert "objective" in root_anc
        assert "Objective line 15." in root_anc["objective"]
        assert "### Constraints" in root_anc["objective"]
        # Existing keys preserved.
        for key in ("path", "title", "status", "effective_status",
                    "first_section", "sections"):
            assert key in root_anc


# --- task_hook tests ---


class TestTaskHook:
    def _run_hook(self, payload: dict, cwd: Path | None = None) -> int:
        """Run task_hook.main() with the given payload via stdin, return exit code."""
        result = self._run_hook_result(payload, cwd=cwd)
        return result.returncode, result.stderr

    def _run_hook_result(self, payload: dict, cwd: Path | None = None):
        """Run task_hook.py with the given payload and return the process result."""
        import subprocess
        hook_path = SCRIPTS_DIR / "task_hook.py"
        return subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            cwd=cwd,
        )

    def test_ignores_non_task_md(self, plan_root):
        """Hook exits 0 immediately for non-task.md files."""
        payload = {
            "tool_name": "Edit",
            "tool_input": {"file_path": str(plan_root / "01-first" / "README.md")},
        }
        code, _ = self._run_hook(payload)
        assert code == 0

    def test_ignores_non_edit_write_tools(self, plan_root):
        """Hook exits 0 immediately for tools other than Edit/Write."""
        payload = {
            "tool_name": "Read",
            "tool_input": {"file_path": str(plan_root / "01-first" / "task.md")},
        }
        code, _ = self._run_hook(payload)
        assert code == 0

    def test_exits_zero_on_valid_task_md(self, plan_root):
        """Hook exits 0 when processing a valid task.md."""
        payload = {
            "tool_name": "Edit",
            "tool_input": {"file_path": str(plan_root / "01-first" / "task.md")},
        }
        result = self._run_hook_result(payload)
        assert result.returncode == 0
        assert result.stdout == ""
        assert result.stderr == ""

    def test_exits_zero_on_validation_failure(self, plan_root):
        """Hook exits 0 even when validation fails (non-blocking)."""
        # Create a task with a bad dep so validation produces warnings
        bad_dir = plan_root / "04-bad"
        bad_dir.mkdir()
        _write_task_md(bad_dir / "task.md", "Bad Task", "not-started",
                       depends_on=["99-nonexistent"])
        payload = {
            "tool_name": "Write",
            "tool_input": {"file_path": str(bad_dir / "task.md")},
        }
        code, _ = self._run_hook(payload)
        assert code == 0

    def test_claude_edit_outputs_warnings_as_context_json(self, plan_root):
        """Claude Edit payloads inject validation warnings as model-visible JSON."""
        bad_dir = plan_root / "04-bad"
        bad_dir.mkdir()
        _write_task_md(bad_dir / "task.md", "Bad Task", "not-started",
                       depends_on=["99-nonexistent"])
        payload = {
            "tool_name": "Edit",
            "tool_input": {"file_path": str(bad_dir / "task.md")},
        }
        result = self._run_hook_result(payload)
        assert result.returncode == 0
        assert result.stderr == ""
        data = json.loads(result.stdout)
        context = data["additionalContext"]
        assert data["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
        assert data["hookSpecificOutput"]["additionalContext"] == context
        assert "Validation warning" in context
        assert "99-nonexistent" in context

    def test_claude_write_invalid_status_outputs_context_json(self, plan_root):
        """Claude Write payloads surface invalid enum edits without blocking."""
        bad_md = plan_root / "01-first" / "task.md"
        bad_md.write_text(
            re.sub(
                r"^status: .+$",
                "status: banana",
                bad_md.read_text(encoding="utf-8"),
                count=1,
                flags=re.MULTILINE,
            ),
            encoding="utf-8",
        )
        payload = {
            "tool_name": "Write",
            "tool_input": {"file_path": str(bad_md)},
        }
        result = self._run_hook_result(payload)
        assert result.returncode == 0
        assert result.stderr == ""
        context = json.loads(result.stdout)["additionalContext"]
        assert "invalid status 'banana'" in context

    def test_codex_apply_patch_task_md_reconciles_plan_once(self, tmp_path):
        """Codex apply_patch payloads reconcile .plan task.md edits."""
        root = tmp_path / ".plan"
        root.mkdir()
        _write_task_md(root / "task.md", "Codex Project", "not-started",
                       objective="A Codex plan.")
        child = root / "01-child"
        child.mkdir()
        _write_task_md(child / "task.md", "Child", "approved",
                       objective="Complete child.")

        dashboard = root / "dashboard.html"
        payload = {
            "tool_name": "apply_patch",
            "tool_input": {
                "command": """*** Begin Patch
*** Update File: .plan/01-child/task.md
@@
-status: not-started
+status: approved
*** End Patch
"""
            },
        }
        result = self._run_hook_result(payload, cwd=tmp_path)
        assert result.returncode == 0
        assert result.stdout == ""
        assert result.stderr == ""
        assert dashboard.exists(), "dashboard should be regenerated after apply_patch"

        after = _task_io.parse_task(root / "task.md")
        assert after.status == "approved", (
            "apply_patch should run whole-tree status propagation for the plan root once"
        )

    def test_codex_apply_patch_invalid_status_outputs_context_json(self, tmp_path):
        """Codex apply_patch payloads inject warnings for invalid task statuses."""
        root = tmp_path / ".plan"
        root.mkdir()
        _write_task_md(root / "task.md", "Codex Project", "not-started",
                       objective="A Codex plan.")
        child = root / "01-child"
        child.mkdir()
        _write_task_md(child / "task.md", "Child", "bogus",
                       objective="Invalid child.")

        payload = {
            "tool_name": "apply_patch",
            "tool_input": {
                "command": """*** Begin Patch
*** Update File: .plan/01-child/task.md
@@
*** End Patch
"""
            },
        }
        result = self._run_hook_result(payload, cwd=tmp_path)
        assert result.returncode == 0
        assert result.stderr == ""
        data = json.loads(result.stdout)
        context = data["additionalContext"]
        assert data["hookSpecificOutput"]["additionalContext"] == context
        assert "invalid status 'bogus'" in context

    def test_codex_apply_patch_irrelevant_payload_exits_zero(self, tmp_path):
        """Codex apply_patch payloads that do not touch task.md are ignored."""
        root = tmp_path / ".plan"
        root.mkdir()
        _write_task_md(root / "task.md", "Codex Project", "not-started",
                       objective="A Codex plan.")

        payload = {
            "tool_name": "apply_patch",
            "tool_input": {
                "command": """*** Begin Patch
*** Update File: README.md
@@
-old
+new
*** End Patch
"""
            },
        }
        result = self._run_hook_result(payload, cwd=tmp_path)
        assert result.returncode == 0
        assert result.stdout == ""
        assert result.stderr == ""
        assert not (root / "dashboard.html").exists()

    def test_empty_stdin_exits_zero(self):
        """Hook exits 0 on empty or invalid stdin (resilient to harness edge cases)."""
        import subprocess
        hook_path = SCRIPTS_DIR / "task_hook.py"
        result = subprocess.run(
            [sys.executable, str(hook_path)],
            input="",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_file_not_in_plan_directory_exits_zero(self, tmp_path):
        """Hook exits 0 for task.md files not inside a superRA/ directory."""
        # Create a task.md somewhere outside of superRA/
        other_task = tmp_path / "task.md"
        other_task.write_text("## Objective\n\nSome task.\n")
        payload = {
            "tool_name": "Edit",
            "tool_input": {"file_path": str(other_task)},
        }
        code, _ = self._run_hook(payload)
        assert code == 0

    # --- Bash (manual move) branch ---

    def test_bash_mv_triggers_rebuild_and_propagation(self, plan_with_branches):
        """A Bash mv that re-parents a task rebuilds the dashboard and rolls up status.

        Moving the lone not-started child out from under 01-data-prep (leaving
        only the approved 01-load) should let the parent roll up to approved
        once the post-move reconcile runs.
        """
        root = plan_with_branches
        # Remove the stale dashboard so we can assert it gets regenerated.
        dashboard = root / "dashboard.html"
        if dashboard.exists():
            dashboard.unlink()

        src = root / "01-data-prep" / "02-merge"
        dst = root / "02-merge"
        shutil.move(str(src), str(dst))

        # Parent had a not-started child before the move; assert it has not yet
        # rolled up (sanity that the reconcile is what changes it).
        before = _task_io.parse_task(root / "01-data-prep" / "task.md")
        assert before.status == "not-started"

        payload = {
            "tool_name": "Bash",
            "tool_input": {"command": f"mv {src} {dst}"},
        }
        code, _ = self._run_hook(payload)
        assert code == 0
        assert dashboard.exists(), "dashboard should be regenerated after the move"

        after = _task_io.parse_task(root / "01-data-prep" / "task.md")
        assert after.status == "approved", (
            "parent should roll up to approved after its only remaining child is approved"
        )

    def test_bash_mv_dangling_dep_warns_and_does_not_rewrite(self, plan_with_branches):
        """A re-parent that strands a depends_on warns but never rewrites the edge."""
        root = plan_with_branches
        # 02-merge depends_on 01-load, both under 01-data-prep. Move 02-merge to
        # the top level so its sibling dependency 01-load is no longer present.
        src = root / "01-data-prep" / "02-merge"
        dst = root / "02-merge"
        shutil.move(str(src), str(dst))

        payload = {
            "tool_name": "Bash",
            "tool_input": {"command": f"mv {src} {dst}"},
        }
        result = self._run_hook_result(payload)
        assert result.returncode == 0
        assert result.stderr == ""
        context = json.loads(result.stdout)["additionalContext"]
        assert "01-load" in context and "Validation warning" in context, (
            "dangling dependency should surface as a validation warning"
        )
        # The hook must NOT rewrite the dependency — it stays as authored.
        moved = _task_io.parse_task(dst / "task.md")
        assert moved.depends_on == ["01-load"], (
            "hook must not auto-cascade depends_on for a post-hoc move"
        )

    def test_bash_readonly_plan_command_no_side_effects(self, plan_root):
        """A read-only superRA Bash command early-exits with no dashboard rebuild."""
        dashboard = plan_root / "dashboard.html"
        if dashboard.exists():
            dashboard.unlink()

        payload = {
            "tool_name": "Bash",
            "tool_input": {
                "command": f"python3 task_query.py --plan-root {plan_root} frontier"
            },
        }
        code, _ = self._run_hook(payload)
        assert code == 0
        assert not dashboard.exists(), (
            "read-only superRA command must not trigger a dashboard rebuild"
        )

    def test_bash_command_without_plan_exits_zero(self):
        """A Bash command touching no superRA tree exits 0 with no error."""
        payload = {
            "tool_name": "Bash",
            "tool_input": {"command": "mv /tmp/a.txt /tmp/b.txt"},
        }
        code, _ = self._run_hook(payload)
        assert code == 0

    def test_bash_command_with_superra_prefix_path_exits_zero(self, tmp_path):
        """A path segment like superRA.worktrees is not the superRA task root."""
        pseudo_worktree = tmp_path / "superRA.worktrees"
        pseudo_worktree.mkdir()
        payload = {
            "tool_name": "Bash",
            "tool_input": {"command": f"mv {pseudo_worktree}/a.txt {pseudo_worktree}/b.txt"},
        }
        code, stderr = self._run_hook(payload, cwd=tmp_path)
        assert code == 0
        assert stderr == ""

    def test_codex_bash_plan_mv_triggers_rebuild(self, tmp_path):
        """Codex Bash payloads structurally mutating .plan trigger reconcile."""
        root = tmp_path / ".plan"
        root.mkdir()
        _write_task_md(root / "task.md", "Codex Project", "not-started",
                       objective="A Codex plan.")
        parent = root / "01-parent"
        parent.mkdir()
        _write_task_md(parent / "task.md", "Parent", "not-started",
                       objective="Parent task.")
        remaining = parent / "00-remaining"
        remaining.mkdir()
        _write_task_md(remaining / "task.md", "Remaining", "approved",
                       objective="Remaining child.")
        child = parent / "01-child"
        child.mkdir()
        _write_task_md(child / "task.md", "Child", "approved",
                       objective="Child task.")

        dst = root / "01-child"
        shutil.move(str(child), str(dst))
        payload = {
            "tool_name": "Bash",
            "tool_input": {"command": "mv .plan/01-parent/01-child .plan/01-child"},
        }
        code, _ = self._run_hook(payload, cwd=tmp_path)
        assert code == 0
        assert (root / "dashboard.html").exists()
        assert _task_io.parse_task(parent / "task.md").status == "approved"

    def test_codex_manifest_task_hook_no_root_fails_open(self):
        """Codex PostToolUse task-hook commands emit {} when no plugin root is set."""
        import subprocess

        manifest_path = SCRIPTS_DIR.parents[2] / "hooks" / "hooks-codex.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        post_tool = manifest["hooks"]["PostToolUse"]
        commands = [
            entry["hooks"][0]["command"]
            for entry in post_tool
            if entry.get("matcher") in {"Edit|Write", "Bash"}
        ]
        assert len(commands) == 2

        payload = {"tool_name": "apply_patch", "tool_input": {"command": ""}}
        for command in commands:
            result = subprocess.run(
                ["/bin/sh", "-c", command],
                input=json.dumps(payload),
                capture_output=True,
                text=True,
                env={},
            )
            assert result.returncode == 0
            assert result.stdout == ""


# --- Revision-note stale-leak validation tests ---


def _task_md_text(title: str, status: str, *, objective: str = "Do the thing.",
                  revnote: str | None = None) -> str:
    """Build a task.md text with an optional ## Revision Notes section."""
    body = f"## Objective\n\n{objective}\n"
    if revnote is not None:
        body += f"\n## Revision Notes\n\n{revnote}\n"
    fm = (
        f'title: "{title}"\n'
        f"status: {status}\n"
        f"depends_on: []\n"
        f"tags: []\n"
        f"created: 2026-01-01\n"
    )
    return f"---\n{fm}---\n\n{body}"


class TestHasNonemptySection:
    def test_detects_real_header_with_content(self):
        body = "## Revision Notes\n\nReopen: rework X.\n"
        assert _task_io._has_nonempty_section(body, "Revision Notes")

    def test_empty_section_is_false(self):
        body = "## Revision Notes\n\n## Next\n\nstuff\n"
        assert not _task_io._has_nonempty_section(body, "Revision Notes")

    def test_missing_header_is_false(self):
        body = "## Objective\n\nDo the thing.\n"
        assert not _task_io._has_nonempty_section(body, "Revision Notes")

    def test_header_inside_fence_is_ignored(self):
        body = (
            "## Objective\n\nSee the format below:\n\n"
            "```\n## Revision Notes\n\nquoted example\n```\n"
        )
        assert not _task_io._has_nonempty_section(body, "Revision Notes")

    def test_tilde_fence_is_ignored(self):
        body = (
            "## Objective\n\n~~~\n## Revision Notes\n\nquoted\n~~~\n"
        )
        assert not _task_io._has_nonempty_section(body, "Revision Notes")

    def test_real_header_after_fenced_quote_still_detected(self):
        body = (
            "## Objective\n\n```\n## Revision Notes\n```\n\n"
            "## Revision Notes\n\nGenuine note.\n"
        )
        assert _task_io._has_nonempty_section(body, "Revision Notes")


class TestValidateRevisionNotes:
    def test_approved_with_revnote_warns(self):
        t = _task_io.Task(
            path="01-t", dir_path=Path("/tmp/01-t"), title="T", status="approved",
            body="## Objective\n\nx\n\n## Revision Notes\n\nstale note\n",
        )
        assert _task_io.validate_revision_notes(t)

    def test_approved_without_revnote_no_warn(self):
        t = _task_io.Task(
            path="01-t", dir_path=Path("/tmp/01-t"), title="T", status="approved",
            body="## Objective\n\nx\n",
        )
        assert _task_io.validate_revision_notes(t) == []

    def test_implemented_with_revnote_no_warn(self):
        t = _task_io.Task(
            path="01-t", dir_path=Path("/tmp/01-t"), title="T", status="implemented",
            body="## Objective\n\nx\n\n## Revision Notes\n\nrework\n",
        )
        assert _task_io.validate_revision_notes(t) == []

    def test_not_started_with_revnote_no_warn(self):
        t = _task_io.Task(
            path="01-t", dir_path=Path("/tmp/01-t"), title="T", status="not-started",
            body="## Objective\n\nx\n\n## Revision Notes\n\nearly\n",
        )
        assert _task_io.validate_revision_notes(t) == []

    def test_in_progress_with_revnote_no_warn(self):
        t = _task_io.Task(
            path="01-t", dir_path=Path("/tmp/01-t"), title="T", status="in-progress",
            body="## Objective\n\nx\n\n## Revision Notes\n\nwip\n",
        )
        assert _task_io.validate_revision_notes(t) == []

    def test_approved_with_fenced_header_no_warn(self):
        t = _task_io.Task(
            path="01-t", dir_path=Path("/tmp/01-t"), title="T", status="approved",
            body="## Objective\n\n```\n## Revision Notes\n\nquoted\n```\n",
        )
        assert _task_io.validate_revision_notes(t) == []

    def test_approved_with_empty_revnote_no_warn(self):
        t = _task_io.Task(
            path="01-t", dir_path=Path("/tmp/01-t"), title="T", status="approved",
            body="## Objective\n\nx\n\n## Revision Notes\n\n## Next\n\ny\n",
        )
        assert _task_io.validate_revision_notes(t) == []


class TestValidatePlanRevisionNotes:
    def _write(self, path: Path, text: str) -> None:
        path.write_text(text, encoding="utf-8")

    def test_validate_plan_warns_on_approved_revnote(self, tmp_path):
        root = tmp_path / "superRA"
        root.mkdir()
        self._write(root / "task.md", _task_md_text("Root", "not-started"))
        d = root / "01-task"
        d.mkdir()
        self._write(d / "task.md",
                    _task_md_text("Task", "approved", revnote="stale note"))
        warnings = _task_io.validate_plan(root)
        assert any("Revision Notes" in w and w.startswith("01-task:")
                   for w in warnings)

    def test_validate_plan_silent_on_implemented_revnote(self, tmp_path):
        root = tmp_path / "superRA"
        root.mkdir()
        self._write(root / "task.md", _task_md_text("Root", "not-started"))
        d = root / "01-task"
        d.mkdir()
        self._write(d / "task.md",
                    _task_md_text("Task", "implemented", revnote="rework"))
        warnings = _task_io.validate_plan(root)
        assert not any("Revision Notes" in w for w in warnings)

    def test_validate_plan_silent_on_fenced_header(self, tmp_path):
        root = tmp_path / "superRA"
        root.mkdir()
        self._write(root / "task.md", _task_md_text("Root", "not-started"))
        d = root / "01-task"
        d.mkdir()
        fenced = (
            "## Objective\n\nSee format:\n\n"
            "```\n## Revision Notes\n\nquoted\n```\n"
        )
        fm = (
            'title: "Task"\nstatus: approved\ndepends_on: []\n'
            "tags: []\ncreated: 2026-01-01\n"
        )
        self._write(d / "task.md", f"---\n{fm}---\n\n{fenced}")
        warnings = _task_io.validate_plan(root)
        assert not any("Revision Notes" in w for w in warnings)



# --- Archived status tests ---


class TestArchivedInFrontier:
    def test_archived_leaf_excluded_from_frontier(self, tmp_path):
        """A leaf task with status 'archived' never appears on the frontier."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        d1 = root_dir / "01-active"
        d1.mkdir()
        _write_task_md(d1 / "task.md", "Active", "not-started")
        d2 = root_dir / "02-archived"
        d2.mkdir()
        _write_task_md(d2 / "task.md", "Archived", "archived")
        root = _task_io.walk_plan(root_dir)
        frontier = _task_io.compute_frontier(root)
        paths = [t.path for t in frontier]
        assert "01-active" in paths
        assert "02-archived" not in paths

    def test_archived_dependency_treated_as_satisfied(self, tmp_path):
        """A task depending on an archived sibling has its dependency satisfied."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        d1 = root_dir / "01-dep"
        d1.mkdir()
        _write_task_md(d1 / "task.md", "Dep", "archived")
        d2 = root_dir / "02-downstream"
        d2.mkdir()
        _write_task_md(d2 / "task.md", "Downstream", "not-started",
                       depends_on=["01-dep"])
        root = _task_io.walk_plan(root_dir)
        frontier = _task_io.compute_frontier(root)
        paths = [t.path for t in frontier]
        assert "02-downstream" in paths, (
            "archived dependency should be treated as satisfied"
        )


class TestArchivedInRollup:
    def test_archived_excluded_from_rollup(self, tmp_path):
        """Parent with 2 approved + 1 archived children computes as approved."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        parent = root_dir / "01-parent"
        parent.mkdir()
        _write_task_md(parent / "task.md", "Parent", "not-started")
        for slug, status in [("01-a", "approved"), ("02-b", "approved"), ("03-c", "archived")]:
            d = parent / slug
            d.mkdir()
            _write_task_md(d / "task.md", slug, status)
        root = _task_io.walk_plan(root_dir)
        parent_task = root.children[0]
        assert parent_task.effective_status() == "approved"

    def test_all_archived_children_rollup_archived(self, tmp_path):
        """When all children are archived, parent computes as archived."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        parent = root_dir / "01-parent"
        parent.mkdir()
        _write_task_md(parent / "task.md", "Parent", "not-started")
        for slug in ["01-a", "02-b"]:
            d = parent / slug
            d.mkdir()
            _write_task_md(d / "task.md", slug, "archived")
        root = _task_io.walk_plan(root_dir)
        parent_task = root.children[0]
        assert parent_task.effective_status() == "archived"

    def test_archived_ignored_in_partial_rollup(self, tmp_path):
        """Parent with 1 approved + 1 not-started + 1 archived = in-progress."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        parent = root_dir / "01-parent"
        parent.mkdir()
        _write_task_md(parent / "task.md", "Parent", "not-started")
        for slug, status in [("01-a", "approved"), ("02-b", "not-started"), ("03-c", "archived")]:
            d = parent / slug
            d.mkdir()
            _write_task_md(d / "task.md", slug, status)
        root = _task_io.walk_plan(root_dir)
        parent_task = root.children[0]
        assert parent_task.effective_status() == "in-progress"


class TestPostponedSemantics:
    def test_postponed_in_valid_statuses(self):
        """'postponed' is a member of the canonical status enum."""
        assert "postponed" in _task_io.VALID_STATUSES

    def test_parse_task_accepts_postponed(self, tmp_path):
        """parse_task accepts a task.md with status 'postponed'."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Parked", "postponed")
        task = _task_io.parse_task(root_dir / "task.md")
        assert task.status == "postponed"

    def test_validate_frontmatter_accepts_postponed(self, tmp_path):
        """validate_frontmatter raises no status warning for 'postponed'."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Parked", "postponed")
        task = _task_io.parse_task(root_dir / "task.md")
        warnings_out = _task_io.validate_frontmatter(task)
        assert not any("status" in w for w in warnings_out)

    def test_postponed_leaf_excluded_from_frontier(self, tmp_path):
        """A leaf task with status 'postponed' never appears on the frontier."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        d1 = root_dir / "01-active"
        d1.mkdir()
        _write_task_md(d1 / "task.md", "Active", "not-started")
        d2 = root_dir / "02-postponed"
        d2.mkdir()
        _write_task_md(d2 / "task.md", "Postponed", "postponed")
        root = _task_io.walk_plan(root_dir)
        frontier = _task_io.compute_frontier(root)
        paths = [t.path for t in frontier]
        assert "01-active" in paths
        assert "02-postponed" not in paths

    def test_postponed_dependency_blocks_dependent(self, tmp_path):
        """A task depending on a postponed sibling is blocked from the frontier."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        d1 = root_dir / "01-dep"
        d1.mkdir()
        _write_task_md(d1 / "task.md", "Dep", "postponed")
        d2 = root_dir / "02-downstream"
        d2.mkdir()
        _write_task_md(d2 / "task.md", "Downstream", "not-started",
                       depends_on=["01-dep"])
        root = _task_io.walk_plan(root_dir)
        frontier = _task_io.compute_frontier(root)
        paths = [t.path for t in frontier]
        assert "02-downstream" not in paths, (
            "postponed dependency should block the dependent"
        )

    def test_archived_vs_postponed_dependency_differ(self, tmp_path):
        """Regression guard: an archived dependency satisfies, postponed does not.

        Same tree shape as the postponed case above, but with the dependency
        'archived' — the dependent should be on the frontier here.
        """
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        d1 = root_dir / "01-dep"
        d1.mkdir()
        _write_task_md(d1 / "task.md", "Dep", "archived")
        d2 = root_dir / "02-downstream"
        d2.mkdir()
        _write_task_md(d2 / "task.md", "Downstream", "not-started",
                       depends_on=["01-dep"])
        root = _task_io.walk_plan(root_dir)
        frontier = _task_io.compute_frontier(root)
        paths = [t.path for t in frontier]
        assert "02-downstream" in paths, (
            "archived dependency should be treated as satisfied (unlike postponed)"
        )


class TestPostponedInRollup:
    def _build_parent(self, tmp_path, child_statuses):
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        parent = root_dir / "01-parent"
        parent.mkdir()
        _write_task_md(parent / "task.md", "Parent", "not-started")
        for i, status in enumerate(child_statuses, start=1):
            d = parent / f"{i:02d}-c"
            d.mkdir()
            _write_task_md(d / "task.md", f"c{i}", status)
        root = _task_io.walk_plan(root_dir)
        return root.children[0]

    def test_approved_plus_postponed_rolls_up_approved(self, tmp_path):
        """Parent with an approved child + a postponed child computes as approved."""
        parent_task = self._build_parent(tmp_path, ["approved", "postponed"])
        assert parent_task.effective_status() == "approved"

    def test_all_postponed_rolls_up_postponed(self, tmp_path):
        """When all children are postponed, parent computes as postponed."""
        parent_task = self._build_parent(tmp_path, ["postponed", "postponed"])
        assert parent_task.effective_status() == "postponed"

    def test_archived_plus_postponed_rolls_up_postponed(self, tmp_path):
        """All-parked branch with a postponed child rolls up to postponed."""
        parent_task = self._build_parent(tmp_path, ["archived", "postponed"])
        assert parent_task.effective_status() == "postponed"

    def test_all_archived_rolls_up_archived(self, tmp_path):
        """Unchanged: an all-archived branch (no postponed) rolls up to archived."""
        parent_task = self._build_parent(tmp_path, ["archived", "archived"])
        assert parent_task.effective_status() == "archived"


# --- Cascade tests ---


class TestCascade:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.plan_root = Path(self.tmpdir) / "superRA"
        self.plan_root.mkdir()
        _write_task_md(self.plan_root / "task.md", "Root", "not-started")
        # Branch task with two leaf children
        branch = self.plan_root / "01-branch"
        branch.mkdir()
        _write_task_md(branch / "task.md", "Branch", "not-started")
        c1 = branch / "01-leaf-a"
        c1.mkdir()
        _write_task_md(c1 / "task.md", "Leaf A", "not-started")
        c2 = branch / "02-leaf-b"
        c2.mkdir()
        _write_task_md(c2 / "task.md", "Leaf B", "in-progress")

    def teardown_method(self):
        shutil.rmtree(self.tmpdir)

    def test_cascade_approved(self):
        """--cascade approved sets all descendant leaves to approved."""
        task_update.update_task(
            self.plan_root, "01-branch",
            status="approved", cascade=True,
        )
        a = _task_io.parse_task(self.plan_root / "01-branch" / "01-leaf-a" / "task.md")
        b = _task_io.parse_task(self.plan_root / "01-branch" / "02-leaf-b" / "task.md")
        assert a.status == "approved"
        assert b.status == "approved"

    def test_cascade_not_started(self):
        """--cascade not-started resets all descendant leaves."""
        task_update.update_task(
            self.plan_root, "01-branch",
            status="not-started", cascade=True,
        )
        a = _task_io.parse_task(self.plan_root / "01-branch" / "01-leaf-a" / "task.md")
        b = _task_io.parse_task(self.plan_root / "01-branch" / "02-leaf-b" / "task.md")
        assert a.status == "not-started"
        assert b.status == "not-started"

    def test_cascade_archived(self):
        """--cascade archived archives all descendant leaves."""
        task_update.update_task(
            self.plan_root, "01-branch",
            status="archived", cascade=True,
        )
        a = _task_io.parse_task(self.plan_root / "01-branch" / "01-leaf-a" / "task.md")
        b = _task_io.parse_task(self.plan_root / "01-branch" / "02-leaf-b" / "task.md")
        assert a.status == "archived"
        assert b.status == "archived"

    def test_cascade_postponed(self):
        """--cascade postponed parks all non-archived descendant leaves."""
        task_update.update_task(
            self.plan_root, "01-branch",
            status="postponed", cascade=True,
        )
        a = _task_io.parse_task(self.plan_root / "01-branch" / "01-leaf-a" / "task.md")
        b = _task_io.parse_task(self.plan_root / "01-branch" / "02-leaf-b" / "task.md")
        assert a.status == "postponed"
        assert b.status == "postponed"

    def test_cascade_postponed_leaves_archived_untouched(self):
        """--cascade postponed parks non-archived leaves but leaves archived leaves archived."""
        # Archive one leaf first
        leaf_a = _task_io.parse_task(
            self.plan_root / "01-branch" / "01-leaf-a" / "task.md"
        )
        leaf_a.status = "archived"
        _task_io.write_task(leaf_a)
        task_update.update_task(
            self.plan_root, "01-branch",
            status="postponed", cascade=True,
        )
        a = _task_io.parse_task(self.plan_root / "01-branch" / "01-leaf-a" / "task.md")
        b = _task_io.parse_task(self.plan_root / "01-branch" / "02-leaf-b" / "task.md")
        assert a.status == "archived", "archived leaf should not be parked by cascade postponed"
        assert b.status == "postponed"

    def test_cascade_not_started_resumes_postponed(self):
        """--cascade not-started resumes postponed leaves (overwrites them)."""
        # Park the subtree first
        task_update.update_task(
            self.plan_root, "01-branch",
            status="postponed", cascade=True,
        )
        # Resume
        task_update.update_task(
            self.plan_root, "01-branch",
            status="not-started", cascade=True,
        )
        a = _task_io.parse_task(self.plan_root / "01-branch" / "01-leaf-a" / "task.md")
        b = _task_io.parse_task(self.plan_root / "01-branch" / "02-leaf-b" / "task.md")
        assert a.status == "not-started"
        assert b.status == "not-started"

    def test_cascade_rejected_for_in_progress(self):
        """--cascade with in-progress errors out."""
        with pytest.raises(SystemExit) as exc_info:
            task_update.update_task(
                self.plan_root, "01-branch",
                status="in-progress", cascade=True,
            )
        assert exc_info.value.code == 1

    def test_cascade_rejected_for_implemented(self):
        """--cascade with implemented errors out."""
        with pytest.raises(SystemExit) as exc_info:
            task_update.update_task(
                self.plan_root, "01-branch",
                status="implemented", cascade=True,
            )
        assert exc_info.value.code == 1

    def test_cascade_rejected_for_revise(self):
        """--cascade with revise errors out."""
        with pytest.raises(SystemExit) as exc_info:
            task_update.update_task(
                self.plan_root, "01-branch",
                status="revise", cascade=True,
            )
        assert exc_info.value.code == 1

    def test_cascade_skips_archived_descendants(self):
        """--cascade not-started does not unarchive already-archived leaves."""
        # Archive one leaf first
        leaf_a = _task_io.parse_task(
            self.plan_root / "01-branch" / "01-leaf-a" / "task.md"
        )
        leaf_a.status = "archived"
        _task_io.write_task(leaf_a)
        # Cascade not-started — should skip the archived leaf
        task_update.update_task(
            self.plan_root, "01-branch",
            status="not-started", cascade=True,
        )
        a = _task_io.parse_task(self.plan_root / "01-branch" / "01-leaf-a" / "task.md")
        b = _task_io.parse_task(self.plan_root / "01-branch" / "02-leaf-b" / "task.md")
        assert a.status == "archived", "archived leaf should not be unarchived by cascade"
        assert b.status == "not-started"

    def test_branch_status_without_cascade_warns(self, capsys):
        """Setting status on a branch task without --cascade prints a warning."""
        task_update.update_task(
            self.plan_root, "01-branch",
            status="approved",
        )
        captured = capsys.readouterr()
        assert "children" in captured.err.lower() or "rollup" in captured.err.lower()


# --- Forward-compatible reading tests ---


class TestForwardCompatibleReading:
    def test_old_file_with_review_and_integration_status_parses(self, tmp_path):
        """_task_io.parse_task silently ignores review_status/integration_status."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        d = root_dir / "01-old"
        d.mkdir()
        # Write an old-format file with all three status fields
        _write_task_md(d / "task.md", "Old Task", "implemented",
                       review_status="approved", integration_status="~")
        # parse_task should work without error and use the status field
        task = _task_io.parse_task(d / "task.md")
        assert task.status == "implemented"
        assert task.title == "Old Task"

    def test_old_file_stale_fields_not_in_task_object(self, tmp_path):
        """Task object has no review_status/integration_status attributes from old files."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        d = root_dir / "01-old"
        d.mkdir()
        _write_task_md(d / "task.md", "Old Task", "in-progress",
                       review_status="implemented", integration_status="revise")
        task = _task_io.parse_task(d / "task.md")
        # The Task dataclass should not have these attributes
        assert not hasattr(task, "review_status")
        assert not hasattr(task, "integration_status")

    def test_write_task_does_not_emit_stale_fields(self, tmp_path):
        """write_task never writes review_status or integration_status."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        d = root_dir / "01-task"
        d.mkdir()
        _write_task_md(d / "task.md", "Task", "approved")
        task = _task_io.parse_task(d / "task.md")
        _task_io.write_task(task)
        content = (d / "task.md").read_text(encoding="utf-8")
        assert "review_status" not in content
        assert "integration_status" not in content


# --- Diagnostic tool (task_check.py) tests ---


class TestTaskCheck:
    def test_clean_tree_no_findings(self, tmp_path):
        """A valid tree produces no findings."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        d1 = root_dir / "01-a"
        d1.mkdir()
        _write_task_md(d1 / "task.md", "Task A", "not-started")
        d2 = root_dir / "02-b"
        d2.mkdir()
        _write_task_md(d2 / "task.md", "Task B", "not-started",
                       depends_on=["01-a"])
        findings = task_check.run_checks(root_dir)
        assert len(findings) == 0

    def test_detects_invalid_status(self, tmp_path):
        """Flags a task with an invalid status value."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        d = root_dir / "01-bad"
        d.mkdir()
        # Write raw file with an invalid status
        content = (
            '---\ntitle: "Bad"\nstatus: completed\n'
            "depends_on: []\ntags: []\ncreated: 2026-01-01\n"
            "---\n\n## Objective\n\nBad status.\n"
        )
        (d / "task.md").write_text(content, encoding="utf-8")
        findings = task_check.run_checks(root_dir, category="status")
        assert any(f.category == "status" and f.severity == "error" for f in findings)
        assert any("completed" in f.message for f in findings)

    def test_detects_stale_review_status(self, tmp_path):
        """Flags stale review_status field still present in frontmatter."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        d = root_dir / "01-stale"
        d.mkdir()
        _write_task_md(d / "task.md", "Stale", "approved",
                       review_status="approved")
        findings = task_check.run_checks(root_dir, category="status")
        assert any(
            "review_status" in f.message and f.category == "status"
            for f in findings
        )

    def test_detects_stale_integration_status(self, tmp_path):
        """Flags stale integration_status field still present in frontmatter."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        d = root_dir / "01-stale"
        d.mkdir()
        _write_task_md(d / "task.md", "Stale", "approved",
                       integration_status="~")
        findings = task_check.run_checks(root_dir, category="status")
        assert any(
            "integration_status" in f.message and f.category == "status"
            for f in findings
        )

    def test_detects_broken_dependency(self, tmp_path):
        """Flags depends_on referencing a non-existent sibling."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        d = root_dir / "01-bad"
        d.mkdir()
        _write_task_md(d / "task.md", "Bad", "not-started",
                       depends_on=["99-missing"])
        findings = task_check.run_checks(root_dir, category="dependency")
        assert any(
            f.category == "dependency" and f.severity == "error"
            and "99-missing" in f.message
            for f in findings
        )

    def test_detects_cycle(self, tmp_path):
        """Flags dependency cycles."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        d1 = root_dir / "01-a"
        d1.mkdir()
        _write_task_md(d1 / "task.md", "A", "not-started",
                       depends_on=["02-b"])
        d2 = root_dir / "02-b"
        d2.mkdir()
        _write_task_md(d2 / "task.md", "B", "not-started",
                       depends_on=["01-a"])
        findings = task_check.run_checks(root_dir, category="dependency")
        assert any(
            f.category == "dependency" and "cycle" in f.message.lower()
            for f in findings
        )

    def test_warns_archived_dependency(self, tmp_path):
        """Warns when a task depends on an archived sibling."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        d1 = root_dir / "01-dep"
        d1.mkdir()
        _write_task_md(d1 / "task.md", "Dep", "archived")
        d2 = root_dir / "02-consumer"
        d2.mkdir()
        _write_task_md(d2 / "task.md", "Consumer", "not-started",
                       depends_on=["01-dep"])
        findings = task_check.run_checks(root_dir, category="dependency")
        assert any(
            f.category == "dependency" and f.severity == "warning"
            and "archived" in f.message
            for f in findings
        )

    def test_warns_postponed_dependency(self, tmp_path):
        """Warns when a task depends on a postponed sibling (blocked until resumed)."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        d1 = root_dir / "01-dep"
        d1.mkdir()
        _write_task_md(d1 / "task.md", "Dep", "postponed")
        d2 = root_dir / "02-consumer"
        d2.mkdir()
        _write_task_md(d2 / "task.md", "Consumer", "not-started",
                       depends_on=["01-dep"])
        findings = task_check.run_checks(root_dir, category="dependency")
        assert any(
            f.category == "dependency" and f.severity == "warning"
            and "postponed" in f.message
            for f in findings
        )

    def test_detects_rollup_mismatch(self, tmp_path):
        """Flags when stored parent status disagrees with computed rollup."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        parent = root_dir / "01-parent"
        parent.mkdir()
        # Stored status says approved, but children are not all approved
        _write_task_md(parent / "task.md", "Parent", "approved")
        c1 = parent / "01-child"
        c1.mkdir()
        _write_task_md(c1 / "task.md", "Child A", "approved")
        c2 = parent / "02-child"
        c2.mkdir()
        _write_task_md(c2 / "task.md", "Child B", "not-started")
        findings = task_check.run_checks(root_dir, category="rollup")
        assert any(
            f.category == "rollup" and "rollup" in f.message.lower()
            for f in findings
        )

    def test_json_output_parseable(self, tmp_path):
        """--json output is valid JSON with expected keys."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        d = root_dir / "01-a"
        d.mkdir()
        _write_task_md(d / "task.md", "A", "not-started")
        findings = task_check.run_checks(root_dir)
        json_str = task_check.format_json(findings)
        data = json.loads(json_str)
        assert "ok" in data
        assert "total" in data
        assert "errors" in data
        assert "warnings" in data
        assert "findings" in data
        assert data["ok"] is True
        assert data["total"] == 0

    def test_json_output_with_findings(self, tmp_path):
        """JSON output includes finding details when issues exist."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        d = root_dir / "01-bad"
        d.mkdir()
        _write_task_md(d / "task.md", "Bad", "not-started",
                       depends_on=["99-missing"])
        findings = task_check.run_checks(root_dir)
        data = json.loads(task_check.format_json(findings))
        assert data["ok"] is False
        assert data["total"] >= 1
        assert len(data["findings"]) >= 1
        f = data["findings"][0]
        assert "task_path" in f
        assert "category" in f
        assert "severity" in f
        assert "message" in f

    def test_text_output_clean(self, tmp_path):
        """Text output says 'All checks passed' for a clean tree."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        findings = task_check.run_checks(root_dir)
        text = task_check.format_text(findings)
        assert "All checks passed" in text

    def test_text_output_with_issues(self, tmp_path):
        """Text output reports issue count for a tree with problems."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        d = root_dir / "01-bad"
        d.mkdir()
        _write_task_md(d / "task.md", "Bad", "not-started",
                       depends_on=["99-missing"])
        findings = task_check.run_checks(root_dir)
        text = task_check.format_text(findings)
        assert "issue(s)" in text

    def test_category_filter(self, tmp_path):
        """Running with category='status' only returns status findings."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        d = root_dir / "01-bad"
        d.mkdir()
        # This file has a broken dep (dependency issue) and stale field (status issue)
        _write_task_md(d / "task.md", "Bad", "not-started",
                       depends_on=["99-missing"],
                       review_status="approved")
        # Only status findings
        status_findings = task_check.run_checks(root_dir, category="status")
        assert all(f.category == "status" for f in status_findings)
        # Only dependency findings
        dep_findings = task_check.run_checks(root_dir, category="dependency")
        assert all(f.category == "dependency" for f in dep_findings)


# --- Status rollup propagation tests (from better-handoff, adapted for unified status) ---


class TestFixStatusConsistency:
    """Tests for --fix mode with unified status model."""

    def test_fix_mode_corrects_parent_status(self, tmp_path):
        """--fix should set parent status to rolled-up value from children."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")

        parent = root_dir / "parent"
        parent.mkdir()
        _write_task_md(parent / "task.md", "Parent", "not-started")

        child1 = parent / "child-a"
        child1.mkdir()
        _write_task_md(child1 / "task.md", "Child A", "approved")

        child2 = parent / "child-b"
        child2.mkdir()
        _write_task_md(child2 / "task.md", "Child B", "implemented")

        # Parent status is "not-started" but children are approved/implemented
        # Rolled-up status should be "in-progress"
        fixed = task_update.fix_status_consistency(root_dir)
        assert fixed >= 1

        # Re-read the parent task
        parent_task = _task_io.parse_task(parent / "task.md")
        assert parent_task.status == "in-progress"

    def test_fix_mode_no_change_for_leaf(self, tmp_path):
        """--fix should NOT change leaf task status (only branches)."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")

        leaf = root_dir / "leaf-task"
        leaf.mkdir()
        _write_task_md(leaf / "task.md", "Leaf", "not-started")

        fixed = task_update.fix_status_consistency(root_dir)
        assert fixed == 0

        leaf_task = _task_io.parse_task(leaf / "task.md")
        assert leaf_task.status == "not-started"

    def test_fix_mode_corrects_rolled_down_status(self, tmp_path):
        """--fix corrects parent status when children force it down."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")

        parent = root_dir / "parent"
        parent.mkdir()
        _write_task_md(parent / "task.md", "Parent", "approved")

        child1 = parent / "child-a"
        child1.mkdir()
        _write_task_md(child1 / "task.md", "Child A", "approved")

        child2 = parent / "child-b"
        child2.mkdir()
        _write_task_md(child2 / "task.md", "Child B", "not-started")

        fixed = task_update.fix_status_consistency(root_dir)
        assert fixed >= 1

        parent_task = _task_io.parse_task(parent / "task.md")
        assert parent_task.status == "in-progress"


class TestPropagateParentStatus:
    def test_propagates_status_to_parent(self, tmp_path):
        """After changing a child status, propagation updates the parent."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        parent = root_dir / "parent"
        parent.mkdir()
        _write_task_md(parent / "task.md", "Parent", "not-started")
        for name in ["child-a", "child-b"]:
            d = parent / name
            d.mkdir()
            _write_task_md(d / "task.md", name, "approved")
        # Propagate from child-a
        updated = _task_io.propagate_parent_status(root_dir, "parent/child-a")
        assert updated >= 1

        # Re-read parent — should now be approved
        parent_task = _task_io.parse_task(parent / "task.md")
        assert parent_task.status == "approved"

    def test_propagates_up_to_root(self, tmp_path):
        """Propagation walks all the way from leaf to root."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        parent = root_dir / "parent"
        parent.mkdir()
        _write_task_md(parent / "task.md", "Parent", "not-started")
        child = parent / "child"
        child.mkdir()
        _write_task_md(child / "task.md", "Child", "implemented")

        updated = _task_io.propagate_parent_status(root_dir, "parent/child")
        assert updated >= 1

        # Parent should be in-progress (child is implemented, not approved)
        parent_task = _task_io.parse_task(parent / "task.md")
        assert parent_task.status == "in-progress"

        # Root should also be in-progress
        root_task = _task_io.parse_task(root_dir / "task.md")
        assert root_task.status == "in-progress"

    def test_no_update_when_already_correct(self, tmp_path):
        """No writes happen if parent already has the correct status."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "in-progress")
        child = root_dir / "child"
        child.mkdir()
        _write_task_md(child / "task.md", "Child", "implemented")

        updated = _task_io.propagate_parent_status(root_dir, "child")
        assert updated == 0

    def test_propagate_from_root_path_is_noop(self, tmp_path):
        """Propagating from root (empty path) has no ancestors to update."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        updated = _task_io.propagate_parent_status(root_dir, "")
        assert updated == 0


class TestPropagateAll:
    def test_propagate_all_updates_all_parents(self, tmp_path):
        """--propagate-all updates all branch task statuses."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")

        # Branch with two approved children
        parent = root_dir / "parent"
        parent.mkdir()
        _write_task_md(parent / "task.md", "Parent", "not-started")
        for name in ["child-a", "child-b"]:
            d = parent / name
            d.mkdir()
            _write_task_md(d / "task.md", name, "approved")

        updated = task_update.propagate_all(root_dir)
        assert updated >= 2  # parent + root

        parent_task = _task_io.parse_task(parent / "task.md")
        assert parent_task.status == "approved"

        root_task = _task_io.parse_task(root_dir / "task.md")
        assert root_task.status == "approved"

    def test_propagate_all_cli(self, tmp_path):
        """CLI --propagate-all flag runs without error."""
        root_dir = tmp_path / "superRA"
        root_dir.mkdir()
        _write_task_md(root_dir / "task.md", "Root", "not-started")
        child = root_dir / "child"
        child.mkdir()
        _write_task_md(child / "task.md", "Child", "approved")

        # Run via main()
        task_update.main(["--plan-root", str(root_dir), "--propagate-all"])


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
                       depends_on=["01-a"], tags=["analysis"],
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
            assert "<strong>tags:</strong> analysis" in r.text

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

    def test_should_exit_when_zero_connections_and_timeout_reached(self):
        assert plan_dashboard._should_idle_exit(0, 5.0, 5.0) is True

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
