---
title: "Update task-system skill docs"
status: not-started
review_status: ~
integration_status: ~
depends_on:
  - 01-design
tags: [docs]
script: ""
input: []
output: []
created: 2026-05-26
updated: 2026-05-26
---

## Objective

Update the task-system skill's own documentation to reflect the unified status model.

**`skills/task-system/SKILL.md`:**
- Remove `review_status` row from the frontmatter field table (line 77)
- Update ownership note (line 100) — remove mention of `review_status` frontmatter
- Update the task file format example (line 112) — remove `review_status: ~` line
- Update the `task_update.py` example to not pass `--review-status`

**`skills/task-system/references/planning.md`:**
- Remove `review_status` from field anatomy, defaults, and ownership sections
- Update the "who sets what" ownership rules to reflect single `status` field with reviewer as co-owner

**`skills/task-system/references/internals.md`:**
- Remove `review_status` from dataclass field documentation
- Remove `VALID_REVIEW_STATUSES` from constants documentation
- Update migration normalization docs to reflect unified status path

## Results
