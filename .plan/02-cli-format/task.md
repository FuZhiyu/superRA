---
title: "CLI Format Changes"
status: approved
review_status: approved
integration_status: ~
depends_on:
  - 01-data-model
tags: []
script: skills/task-system/scripts/task_create.py
created: 2026-05-23
updated: 2026-05-24
---

## Objective

Update `TASK_TEMPLATE` to emit `## Objective` / `## Results` instead of `# {title}` / `{description}`. Rename `--description` CLI arg to `--objective`. Update `tree_to_json()` to include parsed body sections (`objective`, `results`, `decisions`, `review_notes`) in JSON output.

## Results

### Key Findings
- Template now produces clean frontmatter + `## Objective` + `## Results` skeleton (no `# Title` heading)
- `--objective` rename complete across all 4 touchpoints: parse_args, create_task signature, main, template format key
- `tree_to_json()` calls `parse_body_sections()` and includes 4 structured section fields
- Reviewer noted redundant double-parsing (once in `parse_task()`, once in `tree_to_json()`) — accepted as consistent with plan, not a correctness issue
