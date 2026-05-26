---
title: "Update CLI scripts for unified status"
status: not-started
review_status: ~
integration_status: ~
depends_on:
  - 02-data-layer
tags: [code]
script: ""
input: []
output: []
created: 2026-05-26
updated: 2026-05-26
---

## Objective

Update all task-system CLI scripts to remove `review_status` references.

**`task_update.py`:**
- Remove `--review-status` CLI argument (line 26)
- Remove `review_status` parameter from update function (line 39)
- Remove conditional update logic (lines 58-60)
- Remove passing to function (line 99)

**`task_create.py`:**
- Remove `review_status: ~` from the task template (line 18)

**`task_read.py`:**
- Remove `review_status` from frontmatter field order for readable output (line 131)
- Remove `review_status` from JSON output (line 244)

**`task_query.py`:**
- Remove `review_status` from JSON serialization (line 159)

All scripts must still pass `integration_status` through unchanged.

## Results
