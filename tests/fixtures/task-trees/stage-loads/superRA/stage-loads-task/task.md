---
title: "Per-Stage Skill-Load Canary Task"
status: not-started
depends_on: []
tags: [fixture, canary]
output:
  - stage-loads-evidence.json
created: 2026-06-19
---

## Objective

Read this task with `./superRA/superra task read stage-loads-task`. You are an
implementer (or reviewer); load the skill or reference your role spec and the
Skill-Load Manifest tell you to load for the `Stage:` your dispatch named, before
acting. This task proves that stage skill/reference reached your context by asking
for one skill-unique token from it. Do not edit source code, install anything, run
a test suite, or explore the codebase.

Do exactly this:

1. Load the manifest skill or reference for your dispatch's `Stage:`.
2. Write `stage-loads-evidence.json` at the workspace root with exactly:

```json
{
  "schema_version": 1,
  "stage": "<your dispatch Stage: value>",
  "stage_canary": "<the discriminating concept named below>"
}
```

The `stage_canary` value is the discriminating concept that stage's manifest
skill/reference body prescribes — knowable only from that body:

- `protection` → `drift test`
- `sync` → `intent conflict`
- `integration` → `minimum net diff`
- `planning-review` → `handoff-readiness`

For `implementation` and `documentation` there is no extra stage skill; set
`stage_canary` to `none`.
