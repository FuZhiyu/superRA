#!/usr/bin/env python3
"""Tests for the task-system skill scripts."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

import _task_io
from _task_io import parse_body_sections
import plan_dashboard
import plan_migrate
import task_add_result
import task_create
import task_hook
import task_link
import task_query
import task_read
import task_rename
import task_update


# --- Helpers ---


def _write_task_md(path: Path, title: str, status: str, **kwargs):
    """Write a v2-format task.md file.

    kwargs: review_status, integration_status, depends_on, tags,
            objective, results, created, updated.
    """
    review_status = kwargs.get("review_status", "~")
    integration_status = kwargs.get("integration_status", "~")
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
        f'---\ntitle: "{title}"\nstatus: {status}\nreview_status: {review_status}\n'
        f"integration_status: {integration_status}\ndepends_on:{deps_yaml}\n"
        f"tags: {tags_yaml}\ncreated: {created}\nupdated: {updated}\n---\n\n{body}"
    )
    path.write_text(content, encoding="utf-8")


# --- Fixtures ---


@pytest.fixture
def plan_root(tmp_path):
    """Create a minimal plan tree for testing."""
    root = tmp_path / ".plan"
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
    root = tmp_path / ".plan"
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
                   review_status="approved",
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
        root_dir = tmp_path / ".plan"
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
        root_dir = tmp_path / ".plan"
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
        root_dir = tmp_path / ".plan"
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
        # Verify v2 fields are present in JSON output
        for key in ("objective", "results", "decisions", "review_notes"):
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
        # Migration should produce v2 format
        content = (output / "01-load-data" / "task.md").read_text(encoding="utf-8")
        assert "## Objective" in content
        assert "## Steps" not in content

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


# --- parse_body_sections tests ---


class TestParseBodySections:
    def test_all_sections(self):
        body = (
            "## Objective\n\nDo the thing.\n\n"
            "## Results\n\n### Key Findings\n- Found it\n\n"
            "## Decisions\n\n> Use method A\n\n"
            "## Review Notes\n\n> [MAJOR] Fix this\n"
        )
        sections = parse_body_sections(body)
        assert "Objective" in sections
        assert "Do the thing." in sections["Objective"]
        assert "Results" in sections
        assert "Decisions" in sections
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


# --- Auto-rebuild tests ---


class TestAutoRebuild:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.plan_root = Path(self.tmpdir) / ".plan"
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
        self.plan_root = Path(self.tmpdir) / ".plan"
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
            "created: 2026-01-01\nupdated: 2026-01-01\n---\n\n"
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
            "created: 2026-01-01\nupdated: 2026-01-01\n---\n\n"
            "## Objective\n\nAlready in v2 format.\n\n"
            "## Results\n\n"
        )
        (task_dir / "task.md").write_text(v2_content)
        _write_task_md(self.plan_root / "task.md", "Root", "not-started")

        modified = plan_migrate.upgrade_v1_to_v2(self.plan_root)
        assert len(modified) == 0  # nothing changed


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

    def test_bad_review_status_value(self, plan_root):
        task = _task_io.parse_task(plan_root / "01-first" / "task.md")
        task.review_status = "complete"  # invalid
        warnings = _task_io.validate_frontmatter(task)
        assert any("invalid review_status" in w for w in warnings)

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
        root_dir = tmp_path / ".plan"
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
        root_dir = tmp_path / ".plan"
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
        root_dir = tmp_path / ".plan"
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
        assert "Ancestor Context" not in output
        assert "Second Task" in output

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


# --- task_hook tests ---


class TestTaskHook:
    def _run_hook(self, payload: dict) -> int:
        """Run task_hook.main() with the given payload via stdin, return exit code."""
        import io
        import subprocess
        hook_path = SCRIPTS_DIR / "task_hook.py"
        result = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
        )
        return result.returncode, result.stderr

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
        code, _ = self._run_hook(payload)
        assert code == 0

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

    def test_outputs_warnings_to_stderr(self, plan_root):
        """Hook emits validation warnings to stderr for the agent to see."""
        bad_dir = plan_root / "04-bad"
        bad_dir.mkdir()
        _write_task_md(bad_dir / "task.md", "Bad Task", "not-started",
                       depends_on=["99-nonexistent"])
        payload = {
            "tool_name": "Edit",
            "tool_input": {"file_path": str(bad_dir / "task.md")},
        }
        code, stderr = self._run_hook(payload)
        assert code == 0
        assert "WARNING" in stderr or "warning" in stderr.lower()

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
        """Hook exits 0 for task.md files not inside a .plan/ directory."""
        # Create a task.md somewhere outside of .plan/
        other_task = tmp_path / "task.md"
        other_task.write_text("## Objective\n\nSome task.\n")
        payload = {
            "tool_name": "Edit",
            "tool_input": {"file_path": str(other_task)},
        }
        code, _ = self._run_hook(payload)
        assert code == 0
