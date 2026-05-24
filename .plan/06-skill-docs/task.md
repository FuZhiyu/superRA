---
title: "SKILL.md + Inventory Updates"
status: approved
review_status: approved
integration_status: ~
depends_on:
  - 01-data-model
  - 02-cli-format
tags: []
created: 2026-05-23
updated: 2026-05-24
---

## Objective

Rewrite SKILL.md core concepts: remove task/step distinction, document `## Objective` (planner-owned) and `## Results` (implementer-owned, recursive). Update task file format example. Document auto-rebuild and `--upgrade` flag.

## Results

### Key Findings
- Core concepts rewritten: 7 bullet points replacing the old task/step decomposition rule
- Directory structure comments updated (removed "has steps" / "no steps" annotations)
- `task_create` example shows `--objective` flag
- Format example shows populated `## Objective` and `## Results` (not empty checkboxes)
- Auto-rebuild documented under dashboard command
- `--upgrade` command surface added
