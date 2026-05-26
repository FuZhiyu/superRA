---
title: "Comment system and CLI tests"
status: implemented
depends_on: []
tags: []
created: 2026-05-25
updated: 2026-05-25
---

## Objective

Test the comment sidecar data layer and agent CLI.

**Tests:**
- `load_comments()` returns empty list for missing file
- `add_comment()` auto-increments ID, handles gaps from deletions
- `resolve_comment()` toggles resolved status
- `delete_comment()` removes comment and returns True, False for missing
- `split_into_blocks()` handles paragraphs, fenced code, list groups
- `resolve_anchors()` re-resolves shifted blocks via fuzzy matching
- `resolve_anchors()` marks orphaned comments when section/text gone
- CLI `list` shows unresolved by default, `--all` includes resolved
- CLI `resolve` toggles and prints confirmation
- CLI `list-tree` aggregates counts across plan tree
- YAML round-trip: save then load preserves all fields

## Results

Implemented in [`test_dashboard.py`](skills/task-system/scripts/test_dashboard.py).

**TestComments** (13 tests): load_comments empty, add_comment auto-increment + gap handling, resolve_comment toggle + nonexistent, delete_comment bool, split_into_blocks (paragraphs, fenced code, lists), resolve_anchors (exact match, shifted block, orphan detection, missing section), YAML round-trip.

**TestCLI** (5 tests): list subcommand output, list no comments, resolve subcommand, list-tree with comments, list-tree empty.
