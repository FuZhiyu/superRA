---
title: "Replace Dashboard and Comment Prose Oracles"
status: implemented
depends_on:  []
---

## Objective

Replace dashboard and comment tests that assert human labels, logged text, rendered diagnostics, or templates with DOM attributes/classes, JSON fields, parsed workflow structure, URLs, numeric/PID/server state, and user-content round trips. Success: presentation copy may change without breaking tests while UI/workflow behavior remains covered.

## Planner Guidance

Own test_dashboard.py, tests/test_comments.py, dashboard/comment renderers, and workflow generator only. Preserve intentional user-authored content round-trip assertions.

## Results

Dashboard and comment regression coverage now observes stable behavior instead
of presentation wording:

- Comment read/list coverage uses JSON fields and preserves user-authored
  authors, bodies, anchors, previews, and full anchored blocks. Legacy
  block-YAML degradation now exposes the stable
  `legacy-comment-format` code while retaining the prior human explanation for
  compatibility ([comment read contract](../../../../skills/task-tree/scripts/task_read.py#L108),
  [comment tests](../../../../skills/task-tree/scripts/tests/test_comments.py#L158)).
- Dashboard summary and kanban renderers expose numeric and status state through
  `data-*` attributes; tests parse DOM attributes/classes instead of rendered
  labels or count prose ([summary renderer](../../../../skills/task-tree/scripts/templates/summary_bar.html#L13),
  [kanban renderer](../../../../skills/task-tree/scripts/templates/kanban.html#L26),
  [DOM assertions](../../../../skills/task-tree/scripts/test_dashboard.py#L1692)).
- Comment CLI, parse-error, launch/reuse, and foreground coverage now asserts
  JSON, persisted state, exit codes, URLs, browser calls, PID/port state, and
  server arguments rather than confirmation text, diagnostics, or logged paths
  ([comment CLI tests](../../../../skills/task-tree/scripts/test_dashboard.py#L1833),
  [background state tests](../../../../skills/task-tree/scripts/test_dashboard.py#L5429),
  [foreground state test](../../../../skills/task-tree/scripts/test_dashboard.py#L6004)).
- Workflow tests parse YAML and verify permissions, branch configuration,
  `uses` identities, `run` payloads, and cleanup-before-upload ordering. The
  first parsed-YAML run failed four tests because multiline guard substitution
  produced invalid indentation; indentation-aware token replacement fixed the
  generator ([generator fix](../../../../skills/task-tree/scripts/dashboard_artifact_workflow.py#L86),
  [workflow contracts](../../../../skills/task-tree/scripts/test_dashboard.py#L3634)).

Verification:

- Red: the new parsed-workflow checks failed 4 tests with
  `yaml.scanner.ScannerError` before the generator fix.
- Green: targeted replacement set — 66 passed.
- Green: full dashboard/comment files — 321 passed, 2 dependency deprecation
  warnings.
- Green: full `skills/task-tree/scripts` suite — 723 passed, 4 expected warnings.
