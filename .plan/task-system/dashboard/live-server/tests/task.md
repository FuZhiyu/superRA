---
title: "Test suite for live dashboard"
status: in-progress
depends_on:
  - ../server
  - ../templates
  - ../live-reload
  - ../cli-entry
  - ../comments
tags: []
created: 2026-05-25
updated: 2026-05-26
---

## Objective

Add tests for the live dashboard server, templates, comments system, and CLI. Tests should cover the core functionality verified during review: route responses, SSE event format, template rendering, comment CRUD, anchor resolution, and CLI output.

Test file: `skills/task-system/scripts/test_dashboard.py` — extends the existing `test_task_system.py` pattern.
