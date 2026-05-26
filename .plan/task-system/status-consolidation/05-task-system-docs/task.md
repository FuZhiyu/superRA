---
title: "Update task-system skill docs"
status: implemented
review_status: approved
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

All three task-system documentation files updated to reflect the unified status model.

**`skills/task-system/SKILL.md`** ([SKILL.md](skills/task-system/SKILL.md)):
- Removed `review_status` and `integration_status` rows from frontmatter field table; `status` now shows `archived` and owner `implementer / reviewer`
- Updated ownership note to explain co-ownership (implementer owns up to `implemented`, reviewer owns `implemented → revise/approved`)
- Removed both fields from the task file format YAML example; added `archived` to the status comment
- Removed `--review-status approved` from the `task_update.py` CLI example
- Updated migration section: `**Review status:**` and `**Integration status:**` annotated as legacy fields; status inference rewritten to describe the priority-based mapping

**`skills/task-system/references/planning.md`** ([planning.md](skills/task-system/references/planning.md)):
- Removed `review_status` and `integration_status` bullets from Field-by-Field Notes; consolidated into a single `status` entry with `archived` in the valid values and co-ownership documented
- Removed `task_create.py` defaults mentioning `review_status: ~, integration_status: ~`
- Removed `## Workflow Status Checkboxes` section entirely (phase is inferred, not stored)

**`skills/task-system/references/internals.md`** ([internals.md](skills/task-system/references/internals.md)):
- Removed `review_status` and `integration_status` fields from the Task dataclass documentation; added `archived` to the status comment
- Removed `VALID_REVIEW_STATUSES` and `VALID_INTEGRATION_STATUSES` from enum constants; added `archived` to `VALID_STATUSES`
- Updated migration status inference to describe the unified mapping: `integration_status` → `review_status` → checkbox inference priority chain
