---
title: "Per-block inline comments"
status: in-progress
review_status: ~
integration_status: ~
depends_on:
  - ../server
  - ../templates
  - ../live-reload
tags: []
created: 2026-05-24
updated: 2026-05-25
---

## Objective

Add GitHub-style per-block inline commenting to the dashboard. Users comment on specific blocks (paragraphs, list items, code blocks) within a task's rendered body. Comments are stored in sidecar YAML files alongside `task.md`, readable by agents via a CLI tool.

**Design decisions:**
- Sidecar file (`comments.yaml`) per task, not embedded in `task.md` — avoids concurrent write conflicts with agents
- Anchoring: `section` (## heading) + `block_index` (0-indexed block within section) + `text_preview` (fuzzy fallback when blocks shift)
- Comments are resolve-able (like GitHub review threads)
- Dashboard renders comments as collapsible inline annotations below the anchored block
- Agents read/resolve comments via CLI tool, no need to parse YAML manually
