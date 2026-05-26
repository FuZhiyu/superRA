---
title: "Design the unified status model"
status: not-started
review_status: ~
integration_status: ~
depends_on: []
tags: [design]
script: ""
input: []
output: []
created: 2026-05-26
updated: 2026-05-26
---

## Objective

Write a design spec for the consolidated status model as a section in the parent task's body. No code changes — this task produces the authoritative reference that all downstream tasks implement against.

The spec must cover:

1. **Field definitions.** Single `status` enum replacing `status` + `review_status`. Keep `integration_status` as-is. Document the new valid values and their meanings.

2. **State machine.** Define allowed transitions and who owns each:
   - Implementer owns: `not-started → in-progress → implemented`, `revise → implemented`
   - Reviewer owns: `implemented → revise`, `implemented → approved`
   - Orchestrator owns: `approved → not-started` (scope invalidation)

3. **Migration mapping.** How to convert existing `(status, review_status)` pairs into the single `status`:
   - `review_status: approved` → `status: approved` (review outcome takes precedence)
   - `review_status: revise` → `status: revise`
   - `review_status: implemented` → `status: implemented`
   - `review_status: ~` → keep existing `status` value

4. **Rollup and frontier.** Confirm `compute_status()` and `compute_frontier()` logic is unchanged — they already operate on `status` only.

5. **Dashboard rendering.** Confirm effective_status badge logic needs no change since it reads `status`.

## Results
