---
title: "Agent CLI for reading and resolving comments"
status: not-started
review_status: ~
integration_status: ~
depends_on:
  - ../sidecar-format
tags: []
created: 2026-05-24
updated: 2026-05-24
---

## Objective

Provide CLI commands so agents can read, act on, and resolve comments without parsing YAML directly.

**Commands:**
- `task-comment list <task-path>` — list all unresolved comments for a task, showing anchor context and body
- `task-comment list <task-path> --all` — include resolved comments
- `task-comment resolve <task-path> <comment-id>` — mark a comment as resolved
- `task-comment list-tree [root-path]` — list all unresolved comments across the tree (summary: task path + count)

**Output format:**
- Human-readable by default (for agent consumption):
  ```
  [#2] (unresolved) Objective, block 3: "The server should work as..."
    > Do we really need configurable root? YAGNI.
  ```
- `--json` flag for structured output if needed

**Integration with agent workflow:**
- Agents check for comments before starting work on a task (`task-comment list <path>`)
- After addressing a comment, agents resolve it (`task-comment resolve <path> <id>`)
- The resolve action is picked up by the file watcher → SSE → dashboard updates live
