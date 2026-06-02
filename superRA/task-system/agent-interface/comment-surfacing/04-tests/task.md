---
title: "Test Coverage for Comment Surfacing"
status: not-started
depends_on:
  - 02-surface-in-task-read
  - 03-document-cli
tags: []
created: 2026-06-01
---

## Objective

Add test coverage for the new comment-surfacing behavior. Existing tests cover only HTTP-API comment CRUD (`test_dashboard.py:327`); nothing exercises full-block resolution, the `task_read` surfacing, or the enriched CLI. Depends on tasks 02 and 03 (the behavior under test). Run with `~/.venv/bin/python` (has `pyyaml`).

**Cover:**
- **Block accessor (task 01):** comment anchored in-block → full block text; block moved then re-anchored → correct full block; orphaned (section removed / preview matches nothing) → `None`.
- **`task_read.py` surfacing (task 02):** human output shows the `=== Open Comments ===` section with full blocks for unresolved comments; orphaned → preview + orphaned note; a task with no unresolved comments shows no section; resolved comments excluded. `--json` carries `open_comments` with full block text and the orphaned shape (`block: null`).
- **Reliability:** the `task_read` comment path works **without `pyyaml`** — simulate/assert the stdlib path so a missing-pyyaml environment still surfaces comments (this is the researcher's load-bearing reliability requirement; a test that only passes under `uv` does not prove it).
- **Enriched CLI (task 03):** `task_comment.py list` emits the full block; `--json` parity.

**Validation:**
- New tests added under `skills/task-system/scripts/tests/` (new `test_comments.py` or extend `test_dashboard.py`), all passing: `~/.venv/bin/python -m pytest skills/task-system/scripts/tests/ skills/task-system/scripts/test_dashboard.py -q`.
- The full existing suite still passes (no regressions).
- The no-pyyaml reliability assertion is present and meaningful.

**Output:** `skills/task-system/scripts/tests/` (and/or `test_dashboard.py`).

## Results
