---
title: "Main-Agent Trimming: Status+Git Resume Model, Less Prescription"
status: approved
depends_on: []
tags: []
created: 2026-06-21
---

## Objective

`skills/using-superra/references/main-agent.md` had drifted from how the workflow actually operates and over-prescribed. Two problems:

1. **The "Workflow Frontier Resolver" framing assumed a workflow-stage that does not exist.** The only durable state is per-task `status` frontmatter plus the git log — the frontmatter field set is closed, and INTEGRATE deliberately keeps no stage marker, so "stages" (implemented-or-not, integrated-or-not) are reconstructed from git. The resolver's "compute which phase to enter" procedure was ceremony over a status-driven loop, and its safety-invariant list restated gates the workflows already own locally.
2. **The pause/proceed guidance enumerated scenarios instead of teaching the idea** — "Banned Phrasings", scenario-by-scenario lists, and long pause-class enumerations, against the CLAUDE.md "Teach the Protocol, Don't Prescribe Each Action" gate.

**Goal:** make `main-agent.md` reflect the status+git architecture (a "Resuming Work" model, not phase resolution) and state pause/proceed as principles.

## Results

Both outcomes shipped and are verified in the branch diff:

1. **Frontier broadened to all actionable leaf statuses.** `compute_frontier` ([_task_io.py](../../skills/task-tree/scripts/_task_io.py)) now includes `implemented` (ready to review) and `revise` (ready to fix) alongside `not-started`/`in-progress` via a named `_ACTIONABLE_STATUSES`, so `superra task frontier` is the complete "what needs doing now" surface and the caller reads the next action from each task's `status`. Dependency-satisfaction is **unchanged** (approved-only), so dependents of unreviewed work stay blocked. Its single consumer is the `task frontier` CLI; the dashboard does not call it. Covered by `test_revise_and_implemented_on_frontier`; full suite 698 passed, 2 skipped. Decision rationale (option (a) over keeping the frontier as "ready for implementation") is captured at the `compute_frontier` docstring.
2. **main-agent.md rewritten to the status+git resume model.** The "Workflow Frontier Resolver" phase-resolution procedure (~100 lines) is replaced by `## Resuming Work`: no durable workflow-stage exists; status + git are the state; status-driven resume routes the not-all-approved tree to the implement loop via `task frontier`, with the all-approved → integrate path deferred to `superimplement`. Pause/proceed is distilled to two principle-based classes (a researcher-only decision that materially changes a task objective; a pre-set workflow gate). All eight inbound `§Workflow Frontier Resolver` pointers were dropped — each owning workflow now states its own next move — keeping one survivor (the `using-superra` master map → `§Resuming Work`).
