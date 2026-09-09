---
title: "Verify claimed results and simplify reproduction adoption"
status: not-started
depends_on:  []
---

## Objective

Make reproduction verification cover the claimed result and its selected checks, with clear tier names and a small adoption path.

- **Tier compatibility:** use `required` and `on-demand` in declarations, commands, and displays; accept `canon` and `local` as input aliases. New steps default to `on-demand`; default build/status select `required`. Preserve existing declarations and lock validity without a bulk migration.
- **Scoped evidence:** build and status accept the same explicit task/step targets and include their producer ancestors across tiers. A claim names the verified steps and saved-input boundary; an empty default selection cannot certify an on-demand result. Freshness, numerical validity, and end-to-end reproduction remain distinct claims.
- **Protection coverage:** tasks owning selected protection checks are `required`, including check-only tasks. Keep task-level tiers; do not infer that every downstream consumer is a selected protection check.
- **Authoring:** keep stable repo-relative paths and run selection in the task, shared roots and execution settings in config. Require declared paths to agree with runtime reads/writes. Use the existing path/config schema and cheap discovery.
- **Adoption and diagnosis:** provide a bounded one-producer/one-check pilot and a reusable acceptance recipe, used for adoption or mechanism changes. Diagnose changed outputs from evidence; preserve intentional saved-input boundaries and content-equivalent relocation semantics.
- **Validation:** demonstrate an unbuilt on-demand target fails scoped status; an unrelated stale task does not block it; selected protection checks block required completion on failure; legacy and new tiers select equivalent work without invalidating the lock. Exercise CLI and dashboard tier surfaces and the two-step pilot's unchanged/timestamp/helper/environment/missing-output/identical-output/corruption/restoration cases, recording actual execution and unchanged-command latency.

## Details

The audience is researchers choosing what to rebuild and contributors implementing that contract. The accepted design keeps the existing content-based runner and task-local declarations.

- [Small-pilot feedback](../08-pilot-treasurygiv/attachments/2026-09-06-small-pilot-design-feedback.md) records slow discovery and the bounded-adoption proposal. [Earlier pilot](../08-pilot-treasurygiv/task.md#what-the-pilot-taught-the-model) records omitted protection checks.
- [Graph parser](../../../skills/task-tree/scripts/_repro.py), [selection/status](../../../skills/task-tree/scripts/_repro_state.py), and [runner entry](../../../skills/task-tree/scripts/repro_run.py) own tier normalization and target scope. Status currently has no positional targets; build already selects a target's ancestors. Tier is absent from the step spec hash, allowing a rename without rebuilding.
- [Task query](../../../skills/task-tree/scripts/task_query.py), [dashboard server](../../../skills/task-tree/scripts/plan_dashboard.py), and [dashboard client](../../../skills/task-tree/scripts/templates/dashboard.js) expose tier values. Update their live contracts and current documentation together.
- [Reproducibility skill](../../../skills/reproducibility/SKILL.md) owns the verification and adoption rules; [task contract](../../../skills/task-tree/references/task-file-contract.md#reproduction-section) owns schema and command semantics. Follow the existing ownership split for workflow call sites.
- A same-byte output-root relocation currently stays fresh when it does not change the resolved command. Correct the explanatory promise rather than adding path-based invalidation. A corrupted output may be repaired by its producer before a downstream check runs; test rejection by the numerical check separately from successful repair.
- One temporary update task covers the shared parser/runner/skill edit surface. The existing skill-authoring task does not own CLI changes, and workflow-integration does not own runner semantics. Fold the validated outcome into the owning tasks during integration.

## Results
