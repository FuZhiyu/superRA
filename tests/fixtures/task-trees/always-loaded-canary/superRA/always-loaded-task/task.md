---
title: "Always-Loaded Skill Fixture Task"
status: not-started
depends_on: []
tags: [fixture]
output:
  - always-loaded-evidence.json
created: 2026-06-19
---

## Objective

Read this task with `./superRA/superra task read always-loaded-task`. You are an
implementer; load the skills your role spec tells you to load before acting. Do
not edit source code, install anything, or run a test suite.

Do exactly this, in order:

1. Run the report-in-markdown markdown self-diagnose CLI on this task file.
2. Write `always-loaded-evidence.json` at the workspace root with exactly:

```json
{
  "schema_version": 1
}
```
