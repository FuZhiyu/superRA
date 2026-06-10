---
title: "Update and extend test suite"
status: approved
depends_on:
  - 02-data-layer
  - 03-cli-scripts
  - 04-migration-tooling
  - 10-tree-diagnostics
tags:
  - code
  - tests
script: 
input: []
output: []
created: 2026-05-26
---

## Objective

Update existing tests and add new ones to cover the unified status model, `archived` status, `--cascade`, and the diagnostic tool.

**`test_task_tree.py` — field removal:**
- Remove `review_status` and `integration_status` from all test fixture helpers
- Remove assertions for both fields
- Update or remove `test_bad_review_status_value` test
- Update all frontmatter strings in test fixtures

**`test_dashboard.py` — field removal:**
- Remove both fields from test fixture helpers and fixture creation

**New tests — archived status:**
- `archived` tasks excluded from `compute_frontier()`
- `archived` tasks excluded from `compute_status()` rollup (parent with 2 approved + 1 archived = approved)
- `archived` tasks don't block dependents (sibling depends on archived task → dependency satisfied)

**New tests — cascade:**
- `--cascade approved` on branch task sets all descendant leaves to `approved`
- `--cascade not-started` resets all descendant leaves
- `--cascade archived` archives all descendant leaves
- `--cascade` with `in-progress`/`implemented`/`revise` errors
- Warning when setting status on branch task without `--cascade`

**New tests — migration:**
- Migration mapping: given various `(status, review_status, integration_status)` triples, verify the upgrade produces the correct unified `status`
- Forward-compatible reading: `_task_io.py` silently ignores `review_status`/`integration_status` in old task files
- `--upgrade-status` dry-run and actual upgrade modes
- `## Workflow Status` section removal

**New tests — diagnostics:**
- Detects: invalid status values, rollup mismatches, broken dependencies, cycles, archived dependency warnings, stale fields
- `--json` output is parseable
- Exit codes: 0 clean, 1 issues found

## Results

Audited the existing test suite (102 tests in `test_task_tree.py`, 57 in `test_dashboard.py`) against the unified status model design spec. Added 29 new tests filling gaps in four areas:

**Existing coverage confirmed clean (no changes needed):**
- Test fixture helpers in both files already use unified status format (upstream tasks 02, 03, 04, 07, 10 had already updated them)
- `test_bad_review_status_value` already removed by upstream task
- `test_dashboard.py` fixtures and kanban 6-column assertion already correct
- Existing migration tests (8 `TestUpgradeStatus` + 3 `TestMigrationMapping`) cover all migration mapping scenarios, dry-run, idempotency, and `## Workflow Status` removal

**New tests added to [`test_task_tree.py`](skills/task-tree/scripts/test_task_tree.py):**

| Class | Tests | Coverage |
|---|---|---|
| `TestArchivedInFrontier` | 2 | Archived leaf excluded from frontier; archived dependency treated as satisfied |
| `TestArchivedInRollup` | 3 | 2 approved + 1 archived = approved; all archived = archived; partial with archived = in-progress |
| `TestCascade` | 8 | Cascade approved/not-started/archived; rejected for in-progress/implemented/revise; skips archived descendants; branch warning without cascade |
| `TestForwardCompatibleReading` | 3 | Old files with stale fields parse without error; Task object has no stale attributes; write_task never emits stale fields |
| `TestTaskCheck` | 13 | Clean tree; invalid status; stale review_status/integration_status; broken dep; cycle; archived dep warning; rollup mismatch; JSON output (clean + findings); text output (clean + issues); category filter |

**Final test counts:** 131 tests in `test_task_tree.py` (was 102), 57 in `test_dashboard.py` (unchanged). All 188 tests pass.
