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
- Remove `review_status` and `integration_status` rows from the frontmatter field table
- Update ownership note — `status` is co-owned by implementer and reviewer
- Update the task file format example — remove both fields
- Update the `task_update.py` example to not pass `--review-status` or `--integration-status`

**`skills/task-system/references/planning.md`:**
- Remove both fields from field anatomy, defaults, and ownership sections
- Update the "who sets what" ownership rules to reflect single `status` field with reviewer as co-owner
- Remove `## Workflow Status` documentation — phase is inferred, not stored

**`skills/task-system/references/internals.md`:**
- Remove both fields from dataclass field documentation
- Remove `VALID_REVIEW_STATUSES` and `VALID_INTEGRATION_STATUSES` from constants documentation
- Update migration normalization docs to reflect unified status path

## Results
