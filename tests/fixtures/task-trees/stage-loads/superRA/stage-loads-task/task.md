---
title: "Per-Stage Skill-Load Behavior Task"
status: not-started
depends_on: []
tags: [fixture, harness]
output:
  - stage-loads-evidence.json
created: 2026-06-19
---

## Objective

Read this task with `./superRA/superra task read stage-loads-task`. You are an
implementer (or reviewer); load the skill or reference your role spec and the
Skill-Load Manifest tell you to load for the `Stage:` your dispatch named, before
acting. This task proves that stage skill/reference reached your context by asking
for the structured load identity. Do not edit source code, install anything, run a
test suite, or explore the codebase.

Do exactly this:

1. Load the manifest skill or reference for your dispatch's `Stage:`.
2. Write `stage-loads-evidence.json` at the workspace root with exactly:

```json
{
  "schema": "superra.stage-load-evidence/v1",
  "stage": "<your dispatch Stage: value>",
  "loads": ["<structured load identities described below>"]
}
```

Encode each required load as its stable identity:

- Skill: `{"kind": "skill", "id": "<manifest skill ID>"}`
- Reference: `{"kind": "reference", "path": "<manifest reference path>"}`

For `maturation`, load the skills the manifest maps that stage to (`task-tree`,
`superplan`; `writing` only for prose-heavy maturation). For `implementation`,
write an empty `loads` list.
