#!/usr/bin/env python3
"""Tests for the task-system skill scripts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

import _task_io
import plan_dashboard
import plan_migrate
import task_add_result
import task_create
import task_link
import task_query
import task_rename
import task_update


# --- Fixtures ---


@pytest.fixture
def plan_root(tmp_path):
    """Create a minimal plan tree for testing."""
    root = tmp_path / ".plan"
    root.mkdir()

    (root / "task.md").write_text(
        '---\ntitle: "Test Project"\nstatus: not-started\nreview_status: ~\n'
        "integration_status: ~\ndepends_on: []\ntags: []\ncreated: 2026-01-01\n"
        "updated: 2026-01-01\n---\n\n# Test Project\n\nA test plan.\n",
        encoding="utf-8",
    )

    d1 = root / "01-first"
    d1.mkdir()
    (d1 / "task.md").write_text(
        '---\ntitle: "First Task"\nstatus: approved\nreview_status: approved\n'
        "integration_status: ~\ndepends_on: []\ntags: [data]\ncreated: 2026-01-01\n"
        "updated: 2026-01-01\n---\n\n# First Task\n\n## Steps\n\n- [x] Step 1\n\n"
        "## Results\n\n### Key Findings\n- Found 100 rows\n",
        encoding="utf-8",
    )

    d2 = root / "02-second"
    d2.mkdir()
    (d2 / "task.md").write_text(
        '---\ntitle: "Second Task"\nstatus: not-started\nreview_status: ~\n'
        "integration_status: ~\ndepends_on:\n  - 01-first\ntags: [analysis]\n"
        "created: 2026-01-01\nupdated: 2026-01-01\n---\n\n# Second Task\n\n"
        "## Steps\n\n- [ ] Step 1\n- [ ] Step 2\n",
        encoding="utf-8",
    )

    d3 = root / "03-third"
    d3.mkdir()
    (d3 / "task.md").write_text(
        '---\ntitle: "Third Task"\nstatus: not-started\nreview_status: ~\n'
        "integration_status: ~\ndepends_on:\n  - 02-second\ntags: []\n"
        "created: 2026-01-01\nupdated: 2026-01-01\n---\n\n# Third Task\n\n"
        "## Steps\n\n- [ ] Step 1\n",
        encoding="utf-8",
    )

    return root


@pytest.fixture
def plan_with_branches(tmp_path):
    """Create a plan tree with branch tasks (non-leaf) and leaf tasks."""
    root = tmp_path / ".plan"
    root.mkdir()

    (root / "task.md").write_text(
        '---\ntitle: "Branch Project"\nstatus: not-started\nreview_status: ~\n'
        "integration_status: ~\ndepends_on: []\ntags: []\ncreated: 2026-01-01\n"
        "updated: 2026-01-01\n---\n\n# Branch Project\n",
        encoding="utf-8",
    )

    parent = root / "01-data-prep"
    parent.mkdir()
    (parent / "task.md").write_text(
        '---\ntitle: "Data Preparation"\nstatus: not-started\nreview_status: ~\n'
        "integration_status: ~\ndepends_on: []\ntags: []\ncreated: 2026-01-01\n"
        "updated: 2026-01-01\n---\n\n# Data Preparation\n\nPrepare all datasets.\n",
        encoding="utf-8",
    )

    child1 = parent / "01-load"
    child1.mkdir()
    (child1 / "task.md").write_text(
        '---\ntitle: "Load Data"\nstatus: approved\nreview_status: approved\n'
        "integration_status: ~\ndepends_on: []\ntags: []\ncreated: 2026-01-01\n"
        "updated: 2026-01-01\n---\n\n# Load Data\n\n## Steps\n\n- [x] Read parquet\n",
        encoding="utf-8",
    )

    child2 = parent / "02-merge"
    child2.mkdir()
    (child2 / "task.md").write_text(
        '---\ntitle: "Merge Data"\nstatus: not-started\nreview_status: ~\n'
        "integration_status: ~\ndepends_on:\n  - 01-load\ntags: []\n"
        "created: 2026-01-01\nupdated: 2026-01-01\n---\n\n# Merge Data\n\n"
        "## Steps\n\n- [ ] Left join\n",
        encoding="utf-8",
    )

    est = root / "02-estimation"
    est.mkdir()
    (est / "task.md").write_text(
        '---\ntitle: "Estimation"\nstatus: not-started\nreview_status: ~\n'
        "integration_status: ~\ndepends_on:\n  - 01-data-prep\ntags: []\n"
        "created: 2026-01-01\nupdated: 2026-01-01\n---\n\n# Estimation\n\n"
        "## Steps\n\n- [ ] Run model\n",
        encoding="utf-8",
    )

    return root


# --- _task_io tests ---


class TestParseTask:
    def test_parse_leaf_task(self, plan_root):
        task = _task_io.parse_task(plan_root / "01-first" / "task.md")
        assert task.title == "First Task"
        assert task.status == "approved"
        assert task.review_status == "approved"
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
        root_dir = tmp_path / ".plan"
        root_dir.mkdir()
        (root_dir / "task.md").write_text(
            '---\ntitle: "Test"\nstatus: not-started\nreview_status: ~\n'
            "integration_status: ~\ndepends_on: []\ntags: []\n---\n\n# Test\n",
            encoding="utf-8",
        )
        for name in ["01-a", "02-b", "03-c"]:
            d = root_dir / name
            d.mkdir()
            (d / "task.md").write_text(
                f'---\ntitle: "{name}"\nstatus: not-started\nreview_status: ~\n'
                "integration_status: ~\ndepends_on: []\ntags: []\n---\n\n"
                f"# {name}\n\n## Steps\n\n- [ ] Do it\n",
                encoding="utf-8",
            )
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
        root_dir = tmp_path / ".plan"
        root_dir.mkdir()
        (root_dir / "task.md").write_text(
            '---\ntitle: "Diamond"\nstatus: not-started\nreview_status: ~\n'
            "integration_status: ~\ndepends_on: []\ntags: []\n---\n\n# Diamond\n",
            encoding="utf-8",
        )
        for name, status, deps in [
            ("01-D", "approved", []),
            ("02-B", "not-started", ["01-D"]),
            ("03-C", "not-started", ["01-D"]),
            ("04-A", "not-started", ["02-B", "03-C"]),
        ]:
            d = root_dir / name
            d.mkdir()
            deps_yaml = (
                "depends_on: []\n" if not deps
                else "depends_on:\n" + "".join(f"  - {dep}\n" for dep in deps)
            )
            (d / "task.md").write_text(
                f'---\ntitle: "{name}"\nstatus: {status}\nreview_status: ~\n'
                f"integration_status: ~\n{deps_yaml}tags: []\n---\n\n"
                f"# {name}\n\n## Steps\n\n- [ ] Do it\n",
                encoding="utf-8",
            )
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
        root_dir = tmp_path / ".plan"
        root_dir.mkdir()
        (root_dir / "task.md").write_text(
            '---\ntitle: "Root"\nstatus: not-started\nreview_status: ~\n'
            "integration_status: ~\ndepends_on: []\ntags: []\n---\n\n# Root\n",
            encoding="utf-8",
        )
        # Level 1: two branch tasks, L1-b depends on L1-a
        l1a = root_dir / "01-L1a"
        l1a.mkdir()
        (l1a / "task.md").write_text(
            '---\ntitle: "L1-a"\nstatus: not-started\nreview_status: ~\n'
            "integration_status: ~\ndepends_on: []\ntags: []\n---\n\n# L1-a\n",
            encoding="utf-8",
        )
        l1b = root_dir / "02-L1b"
        l1b.mkdir()
        (l1b / "task.md").write_text(
            '---\ntitle: "L1-b"\nstatus: not-started\nreview_status: ~\n'
            "integration_status: ~\ndepends_on:\n  - 01-L1a\ntags: []\n---\n\n# L1-b\n",
            encoding="utf-8",
        )
        # Level 2 under L1-a: one sub-branch
        l2 = l1a / "01-L2"
        l2.mkdir()
        (l2 / "task.md").write_text(
            '---\ntitle: "L2"\nstatus: not-started\nreview_status: ~\n'
            "integration_status: ~\ndepends_on: []\ntags: []\n---\n\n# L2\n",
            encoding="utf-8",
        )
        # Level 3 (leaf) under L2
        leaf = l2 / "01-leaf"
        leaf.mkdir()
        (leaf / "task.md").write_text(
            '---\ntitle: "Deep Leaf"\nstatus: not-started\nreview_status: ~\n'
            "integration_status: ~\ndepends_on: []\ntags: []\n---\n\n"
            "# Deep Leaf\n\n## Steps\n\n- [ ] Do it\n",
            encoding="utf-8",
        )
        # Level 2 under L1-b: a leaf that should be blocked
        l1b_leaf = l1b / "01-blocked-leaf"
        l1b_leaf.mkdir()
        (l1b_leaf / "task.md").write_text(
            '---\ntitle: "Blocked Leaf"\nstatus: not-started\nreview_status: ~\n'
            "integration_status: ~\ndepends_on: []\ntags: []\n---\n\n"
            "# Blocked Leaf\n\n## Steps\n\n- [ ] Do it\n",
            encoding="utf-8",
        )

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
        root_dir = tmp_path / ".plan"
        root_dir.mkdir()
        (root_dir / "task.md").write_text(
            '---\ntitle: "Empty"\nstatus: not-started\nreview_status: ~\n'
            "integration_status: ~\ndepends_on: []\ntags: []\n---\n\n# Empty\n",
            encoding="utf-8",
        )
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
            description="A new objective.",
        )
        task_md = plan_root / "04-new-task" / "task.md"
        assert task_md.exists()
        task = _task_io.parse_task(task_md)
        assert task.title == "New Task"
        assert task.status == "not-started"
        assert task.depends_on == []

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

        output = tmp_path / ".plan"
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

        t2 = _task_io.parse_task(output / "02-analyze" / "task.md")
        assert "01-load-data" in t2.depends_on


# --- Dashboard tests ---


class TestDashboard:
    def test_generate_dashboard(self, plan_root):
        output = plan_root / "dashboard.html"
        plan_dashboard.generate_dashboard(plan_root, output)
        assert output.exists()
        html = output.read_text(encoding="utf-8")
        assert "Plan Dashboard" in html
        assert "TASK_DATA" in html
        assert "Test Project" in html
        assert "First Task" in html
        assert "mermaid" in html
