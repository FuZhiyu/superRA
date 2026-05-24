---
title: "CLI Format Changes"
status: approved
review_status: approved
integration_status: ~
depends_on:
  - data-model
tags: []
script: skills/task-system/scripts/task_create.py
created: 2026-05-23
updated: 2026-05-24
---

## Objective

Update `TASK_TEMPLATE` to emit `## Objective` / `## Results` instead of `# {title}` / `{description}`. Rename `--description` CLI arg to `--objective`. Update `tree_to_json()` to include parsed body sections in JSON output.

## Results

### Key Findings
- Template produces clean frontmatter + `## Objective` + `## Results` skeleton
- `--objective` rename complete across parse_args, create_task signature, main, template format key
- `tree_to_json()` includes `objective`, `results`, `decisions`, `review_notes` from `parse_body_sections()`
