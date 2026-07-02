"""Shared test helpers and fixtures for the task-tree script test suite.

All loose test_*.py files in this directory pick up module-level helpers and
fixtures defined here automatically via pytest's conftest discovery.

Convention: new tests go into a loose scripts/test_*.py file (not the
scripts/tests/ subpackage); the subpackage exists for historical reasons and
is collected too, but the canonical home for new tests is the scripts/ level.
"""

from __future__ import annotations

import struct
import sys
import zlib
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _write_task_md(path: Path, title: str, status: str, **kwargs):
    """Write a task.md file (unified status format).

    kwargs: depends_on, objective, results.
    For legacy test scenarios, review_status and integration_status can be
    passed to produce old-format files.
    """
    depends_on = kwargs.get("depends_on", [])
    objective = kwargs.get("objective", "")
    results = kwargs.get("results", "")

    if depends_on:
        deps_yaml = "\n" + "".join(f"  - {d}\n" for d in depends_on)
    else:
        deps_yaml = " []"

    body = f"## Objective\n\n{objective}\n"
    if results:
        body += f"\n## Results\n\n{results}\n"

    # Build frontmatter — include legacy fields only if explicitly passed
    fm_lines = [f'title: "{title}"', f"status: {status}"]
    if "review_status" in kwargs:
        fm_lines.append(f"review_status: {kwargs['review_status']}")
    if "integration_status" in kwargs:
        fm_lines.append(f"integration_status: {kwargs['integration_status']}")
    fm_lines.append(f"depends_on:{deps_yaml}")

    content = "---\n" + "\n".join(fm_lines) + "\n---\n\n" + body
    path.write_text(content, encoding="utf-8")


def _write_tiny_png(path: Path) -> bytes:
    """Write a minimal valid 2x2 PNG (no PIL dependency) and return its bytes."""

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


def _serve_plan(tmp_path: Path) -> Path:
    """Build a minimal task tree under tmp_path/superRA and return its plan root."""
    plan_root = tmp_path / "superRA"
    plan_root.mkdir()
    a = plan_root / "01-a"
    a.mkdir()
    _write_task_md(a / "task.md", "A", "not-started", objective="A obj.")
    return plan_root


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


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
