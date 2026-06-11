---
title: "Test Coverage for Comment Surfacing"
status: approved
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
- New tests added under `skills/task-tree/scripts/tests/` (new `test_comments.py` or extend `test_dashboard.py`), all passing: `~/.venv/bin/python -m pytest skills/task-tree/scripts/tests/ skills/task-tree/scripts/test_dashboard.py -q`.
- The full existing suite still passes (no regressions).
- The no-pyyaml reliability assertion is present and meaningful.

**Output:** `skills/task-tree/scripts/tests/` (and/or `test_dashboard.py`).

## Results

Added [`skills/task-tree/scripts/tests/test_comments.py`](../../../../../skills/task-tree/scripts/tests/test_comments.py) — 17 tests covering all four areas of the comment-surfacing subtree. Placed alongside the existing suite (`tests/` package) as a new file rather than extending `test_dashboard.py`, since the behavior under test (read-path + CLI surfacing) is distinct from the dashboard's HTTP-API comment CRUD.

**Coverage by area:**

- **Block accessor (`anchored_block`), 4 tests** — in-block comment returns the full block text; comment whose stored index is stale but whose preview matches a moved block re-anchors and returns the moved block's full text (asserts `block_index` updated in place, `orphaned is False`); section removed → `None` + `orphaned`; preview matching nothing → `None` + `orphaned`.
- **`task_read` surfacing, 7 tests** — human `=== Open Comments ===` shows the full block (asserts the full sentence, not the ≤60-char preview); orphaned → `block: "<preview>"` + `[ORPHANED …]` note; no-unresolved-comments task → no section; a resolved comment is excluded (no section, body absent); `--json` `open_comments` carries the full `block` text with `orphaned: false`/`degraded: null`; orphaned `--json` shape is `block: null`, `orphaned: true`, `preview` retained; empty `open_comments` when none unresolved. Driven through `task_read.main(...)` so the real CLI render path is exercised.
- **Reliability (no-`pyyaml`), 3 tests — the load-bearing requirement.** A custom `sys.meta_path` finder makes `import yaml` raise `ModuleNotFoundError`; the comment modules are reloaded under that view. The setup asserts `importlib.import_module("yaml")` actually raises inside the test, so it cannot silently pass with pyyaml present. Then: (1) a JSON-format sidecar still SURFACES its unresolved comment with full block (stdlib `json` path); (2) a legacy block-YAML sidecar DEGRADES gracefully — `task_read` emits the `[open comments unavailable: legacy sidecar format …]` note and the rest of the read still prints (frontmatter + sections), no crash; (3) a direct unit assertion that `load_comments` raises `LegacyCommentFormatError` on a block-YAML file only when yaml is unavailable. A `restore_modules` fixture reloads the canonical (yaml-enabled) modules afterward so module-state mutation does not leak into other tests.

  I verified the no-yaml tests are not false-passing: with yaml present, the same legacy block-YAML sidecar loads cleanly (no exception, no degradation), so the degrade/raise assertions succeed *only* because the test genuinely disabled yaml.

- **Enriched CLI (`task_comment list`), 3 tests** — human output emits the full block; `--json` carries the full `block` with `orphaned: false`; orphaned `--json` shape is `block: null`, `orphaned: true`. Driven through `task_comment.main(...)`.

**Validation (run with `~/.venv/bin/python`, which has pyyaml):**

- New file: `17 passed`.
- Full existing task-tree suite (`tests/`, `test_dashboard.py`, `test_task_tree.py`, `test_cli.py`, `test_multi_worktree.py`, `test_worktree_selector.py`): `534 passed, 3 warnings` — no regressions (the 3 warnings are pre-existing, from a status-validation test that intentionally writes an invalid status).
