---
title: "Verify claimed results and simplify reproduction adoption"
status: in-progress
depends_on:  []
---

## Objective

Make reproduction verification cover the claimed result and its selected checks, with clear tier names and a small adoption path.

- **Tier compatibility:** use `required` and `on-demand` in declarations, commands, and displays; accept `canon` and `local` as input aliases. New steps default to `on-demand`; default build/status select `required`. Preserve existing declarations and lock validity without a bulk migration.
- **Scoped evidence:** build and status accept the same explicit task/step targets and include their producer ancestors across tiers. A claim names the verified steps and saved-input boundary; an empty default selection cannot certify an on-demand result. Freshness, numerical validity, and end-to-end reproduction remain distinct claims.
- **Protection coverage:** tasks owning selected protection checks are `required`, including check-only tasks. Keep task-level tiers; do not infer that every downstream consumer is a selected protection check.
- **Authoring:** keep stable repo-relative paths and run selection in the task, shared roots and execution settings in config. Require declared paths to agree with runtime reads/writes. Use the existing path/config schema and cheap discovery.
- **Environment changes:** omit environment files from graph dependencies by default. Agents use Git diffs to judge reruns and investigate reproduction failures. Add no environment flag, assessment record, or runner-specific configuration; preserve existing explicitly configured `env_deps` as an opt-in.
- **Adoption and diagnosis:** provide a bounded one-producer/one-check pilot and a reusable acceptance recipe, used for adoption or mechanism changes. Diagnose changed outputs from evidence; preserve intentional saved-input boundaries and content-equivalent relocation semantics.
- **Validation:** demonstrate an unbuilt on-demand target fails scoped status; an unrelated stale task does not block it; selected protection checks block required completion on failure; legacy and new tiers select equivalent work without invalidating the lock. Exercise CLI and dashboard tier surfaces and the two-step pilot's unchanged/timestamp/helper/missing-output/identical-output/corruption/restoration cases, recording actual execution and unchanged-command latency. Environment-file edits alone skip all steps when those files are undeclared; explicit `env_deps` retain their invalidation behavior.

## Details

The audience is researchers choosing what to rebuild and contributors implementing that contract. The accepted design keeps the existing content-based runner and task-local declarations.

- [Small-pilot feedback](../08-pilot-treasurygiv/attachments/2026-09-06-small-pilot-design-feedback.md) records slow discovery and the bounded-adoption proposal. [Earlier pilot](../08-pilot-treasurygiv/task.md#what-the-pilot-taught-the-model) records omitted protection checks.
- [Graph parser](../../../skills/task-tree/scripts/_repro.py), [selection/status](../../../skills/task-tree/scripts/_repro_state.py), and [runner entry](../../../skills/task-tree/scripts/repro_run.py) own tier normalization and target scope. Tier is absent from the step spec hash, allowing a rename without rebuilding.

## Revision Notes

Environment changes are agent judgment based on Git history, with no new runner machinery. Remove mandatory environment dependencies from the skill and its default example; keep explicit configurations compatible.
- [Task query](../../../skills/task-tree/scripts/task_query.py), [dashboard server](../../../skills/task-tree/scripts/plan_dashboard.py), and [dashboard client](../../../skills/task-tree/scripts/templates/dashboard.js) expose tier values. Update their live contracts and current documentation together.
- [Reproducibility skill](../../../skills/reproducibility/SKILL.md) owns the verification and adoption rules; [task contract](../../../skills/task-tree/references/task-file-contract.md#reproduction-section) owns schema and command semantics. Follow the existing ownership split for workflow call sites.
- A same-byte output-root relocation currently stays fresh when it does not change the resolved command. Correct the explanatory promise rather than adding path-based invalidation. A corrupted output may be repaired by its producer before a downstream check runs; test rejection by the numerical check separately from successful repair.
- One temporary update task covers the shared parser/runner/skill edit surface. The existing skill-authoring task does not own CLI changes, and workflow-integration does not own runner semantics. Fold the validated outcome into the owning tasks during integration.

## Results

The runner verifies explicit task/step targets, and the skill requires evidence for the claimed result and selected checks. `required` / `on-demand` are the displayed tier names; legacy inputs remain supported without rewriting declarations or invalidating existing locks.

- [Runner regression tests](../../../skills/task-tree/scripts/test_repro_runner.py) cover alias equivalence, lock preservation, missing on-demand targets, unrelated stale work, cross-tier ancestors, unknown targets, and a selected check-only task blocking required completion. The complete task-tree suite passed **1,047 tests** with pytask and the web dependencies installed. [Harness packaging check](../../../tests/check-harness-compatibility.sh), task-tree validation, skill validation, and Markdown checks also passed.
- A disposable two-step shell pilot passed first build, unchanged build, timestamp-only change, producer/helper edits, environment change, missing output, identical-output suppression, direct corruption rejection, and restoration. Producer/helper edits made both steps report stale, but only the producer executed after identical regeneration. The saved input retained its original bytes and both steps finished fresh.
- In that tiny fixture, median unchanged CLI status/build times over three warm invocations were **0.054 s / 0.338 s**. Graph construction took **0.0012 s** and warm state computation **0.00085 s**; there were no shell resolvers. These observations validate the simple fixture, not a TreasuryGIV speedup. TreasuryGIV's dynamic branch/sandbox routing and revised resolver latency remain unmeasured in this change.
- [Pilot acceptance](../../../skills/reproducibility/references/pilot-acceptance.md) owns the reusable adoption matrix. The authoring instructions keep stable paths in the task, resolve shared dynamic roots cheaply, and bind declarations to runtime routing.

Self-review completed; independent review has not run.
