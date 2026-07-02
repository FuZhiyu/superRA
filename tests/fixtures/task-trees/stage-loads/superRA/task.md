---
title: "Per-Stage Skill-Load Fixture Root"
status: not-started
depends_on: []
tags:
  - fixture
  - stage-loads
created: 2026-06-19
---

## Objective

Disposable task tree for the per-stage skill-load live coverage (task 11). A single
shared leaf task below carries no stage of its own; the live dispatch supplies the
`Stage:` line, and the dispatched implementer/reviewer loads the manifest skill or
reference that stage maps to before acting. One body is reused across every stage —
only the dispatch `Stage:` line differs — so adding a future stage is a one-row
change in the harness table, not a new fixture.
