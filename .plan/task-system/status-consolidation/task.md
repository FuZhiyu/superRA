---
title: "Consolidate status and review_status into a single status field"
status: not-started
review_status: ~
integration_status: ~
depends_on:
  - agent-interface
tags: [status, simplification]
script: ""
input: []
output: []
created: 2026-05-26
updated: 2026-05-26
---

## Objective

Merge `review_status` into `status` to eliminate redundancy between the two fields. Today, implementers set both `status: implemented` and `review_status: implemented` on commit — two writes for one event. The frontier computation and rollup logic only consume `status`, so `review_status` is tracked but never auto-consumed by the system. This makes auto-computation fragile and the protocol confusing.

**Target state:** A single `status` field with a clear state machine:

```
not-started → in-progress → implemented → revise → approved
```

- **Implementer** owns transitions up to `implemented` (and `revise → implemented` on fix rounds).
- **Reviewer** owns `implemented → revise` and `implemented → approved`.
- Frontier computation, rollup, and dashboard rendering all use `status` directly.

`integration_status` stays as a separate field — it covers a genuinely distinct lifecycle (post-sync codebase-fit review).

**Scope:** task-system data layer, CLI scripts, SKILL.md, agent specs (implementer.md, reviewer.md), workflow skills (implementation-workflow, integration-workflow, agent-orchestration), dashboard rendering, migration of existing `.plan/` trees, and tests.

## Results
