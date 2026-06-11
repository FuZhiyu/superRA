---
title: "Syntax Highlighting for Fenced Code Blocks"
status: not-started
depends_on: []
tags: []
created: 2026-06-10
---

## Objective

Render fenced code blocks with syntax highlighting in both the live server and the standalone export.

- Vendor a highlighting library (highlight.js or equivalent) under `skills/task-tree/scripts/vendor/` per its README conventions, with a language set covering the doc and task content actually present (at minimum: bash/shell, python, julia, yaml, markdown, json).
- Wire it into the existing markdown-it rendering path so highlighting applies wherever markdown bodies render today.
- Highlight colors respect the existing light/dark theme tokens in `base.html` — readable in both themes.
- Standalone export inlines the new assets like the existing vendored libraries; no network fetch at runtime.

Success criteria: a fenced block with a language tag renders highlighted in a live session and in an exported file, in both themes, verified in the rendered DOM; unknown/absent language tags degrade to today's plain rendering; vendored assets documented in `vendor/README.md`.
