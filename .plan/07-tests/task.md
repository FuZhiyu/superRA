---
title: "Test Suite Updates"
status: approved
review_status: approved
integration_status: ~
depends_on:
  - 01-data-model
  - 02-cli-format
  - 03-auto-rebuild
  - 05-v2-migration
tags: []
script: skills/task-system/scripts/test_task_system.py
created: 2026-05-23
updated: 2026-05-24
---

## Objective

Update all fixtures to v2 format (`## Objective` not `## Steps`). Add `TestParseBodySections` (4 tests), `TestAutoRebuild` (2 tests), `TestMigrateV2` (2 tests). Verify `tree_to_json` includes structured section fields. 53 total tests.

## Results

### Key Findings
- All fixture task.md content converted from v1 to v2 format via `_write_task_md()` helper
- `TestParseBodySections`: all sections, objective only, empty body, unknown sections preserved
- `TestAutoRebuild`: verifies dashboard content changes (not just file existence) after create and update
- `TestMigrateV2`: v1→v2 upgrade converts Steps to Objective + strips checkboxes; idempotent on v2 files
- `test_tree_to_json` verifies `objective`, `results`, `decisions`, `review_notes` keys in JSON output
- 53/53 tests passing in 0.14s

### Notes
- `TestAutoRebuild` covers 2 of 5 mutation scripts (create, update) — remaining 3 have identical hook pattern
