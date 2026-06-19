---
title: "Agent Loading Bundle"
status: in-progress
depends_on: []
tags: [fixture, harness-loading]
created: 2026-06-19
---

## Objective

Parent task for a bundled agent-loading smoke scenario.

PARENT_CONTEXT_SENTINEL_RIVER

### Constraints

The only write expected from this fixture is `loading-evidence.json` at the
fixture root. The artifact should match
`expected/loading-evidence.expected.json` after replacing nothing; all values are
literal sentinel strings gathered from task-read output or marker files.
