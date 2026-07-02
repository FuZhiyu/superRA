---
title: "Skill Definition + Inventory"
status: approved
depends_on:
  - core-data-layer
  - cli-scripts
  - dashboard
---

## Objective

Write the task-tree `SKILL.md` with core concepts (everything is a task, `## Objective` planner-owned, `## Results` implementer-owned and recursive, filesystem hierarchy, sibling-only deps, status rollup), directory structure, the command surface with examples, the task-file template, and migration docs. Update `CATEGORIES.md` and `README.md` skill inventory.

## Results

`skills/task-tree/SKILL.md` is a compact routing layer over three references (`commands.md`, `task-file-contract.md`, `internals.md`), with migration documented via a pointer to `internals.md §Migration`.

### Key Findings
- Added the `superra task check` routing row and a `§Diagnostics` section to `skills/task-tree/references/commands.md`.
- `CATEGORIES.md` and `README.md` skill entries were trimmed to discovery-level descriptions and updated to the live SSE server wording.
