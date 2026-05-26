---
title: "Consolidate to a single status field"
status: not-started
review_status: approved
integration_status: ~
depends_on:
  - agent-interface
tags:
  - status
  - simplification
created: 2026-05-26
updated: 2026-05-26
---

## Objective

Drop `review_status` and `integration_status` from task frontmatter. Merge both into the single `status` field. Today, implementers set both `status: implemented` and `review_status: implemented` on commit — two writes for one event. Frontier computation and rollup only consume `status`, so the other fields are tracked but never auto-consumed. This makes auto-computation fragile and the protocol confusing.

**Target state:** A single `status` field with a clear state machine:

```
not-started → in-progress → implemented → revise → approved
```

- **Implementer** owns transitions up to `implemented` (and `revise → implemented` on fix rounds).
- **Reviewer** owns `implemented → revise` and `implemented → approved`.
- **Workflow phase is inferred** from the subtree's status distribution, not stored.
- Frontier computation, rollup, and dashboard rendering all use `status` directly.

No `## Workflow Status` section in task files. Phase inference is recursive — any subtree is a self-contained workflow.

**Deferred:** Rearchitecting the integration workflow to be scope-flexible (single task, subtree, or branch-wide) and to reuse `status` for its revise cycle. Tracked separately under `agent-interface`. This task focuses on removing the redundant fields from the data model and updating all consumers.

**Scope:** task-system data layer, CLI scripts, SKILL.md, agent specs, workflow skills (implementation-workflow, agent-orchestration, planning-workflow), dashboard rendering, migration of existing `.plan/` trees, and tests.


## Results
