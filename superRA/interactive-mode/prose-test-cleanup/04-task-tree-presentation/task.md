---
title: "Replace Dashboard and Comment Prose Oracles"
status: not-started
depends_on:  []
---

## Objective

Replace dashboard and comment tests that assert human labels, logged text, rendered diagnostics, or templates with DOM attributes/classes, JSON fields, parsed workflow structure, URLs, numeric/PID/server state, and user-content round trips. Success: presentation copy may change without breaking tests while UI/workflow behavior remains covered.

## Planner Guidance

Own test_dashboard.py, tests/test_comments.py, dashboard/comment renderers, and workflow generator only. Preserve intentional user-authored content round-trip assertions.

## Results
