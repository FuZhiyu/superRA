---
title: "Per-Stage Skill-Load Fixture Task"
status: not-started
depends_on: []
tags: [fixture]
output:
  - stage-loads-evidence.json
created: 2026-06-19
---

## Objective

Read this task with `./superRA/superra task read stage-loads-task`. You are an
implementer (or reviewer); load the skill or reference your role spec and the
Skill-Load Manifest tell you to load for the `Stage:` your dispatch named, before
acting. Do not edit source code, install anything, run a test suite, or explore
the codebase.

Do exactly this:

1. Load the manifest skill or reference for your dispatch's `Stage:`.
2. Write `stage-loads-evidence.json` at the workspace root with exactly:

```json
{
  "schema_version": 1,
  "stage": "<your dispatch Stage: value>"
}
```
