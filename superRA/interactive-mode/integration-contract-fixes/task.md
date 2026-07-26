---
title: "Close Interactive Integration Contract Gaps"
status: not-started
depends_on:  []
---

## Objective

Resolve the integration review blockers as one coherent execution-contract repair: make review now/defer/skip durable with the existing status enum and completion/resume routing; wire superimplement to per-task main/subagent seat selection; make canonical role specs resolvable for main-filled and forced-inline seats in installed cross-repo use; add a minimal domain-neutral interactive self-review; remove DRY/Necessity duplication; and correct the conservative cleanup's narrow reproducibility accounting. Success: every recorded integration finding is accepted and fixed, current docs and tests reflect the same contract, packaged/generated access works, and full integration verification passes.

## Planner Guidance

The authoritative findings are in superRA/interactive-mode/task.md and superRA/interactive-mode/prose-test-cleanup/task.md at review commit f88a42f5. Reuse the existing status enum; do not add a review-status field unless unavoidable. Keep role behavior in agents/*, harness resolution in the Codex adapter/setup owner, and changing-tree behavior in its reference. Load skill-creator before skills/* edits. Apply DRY/Necessity line by line and keep the diff bounded to these findings.

## Results
