---
title: "Verify claimed results and simplify reproduction adoption"
status: implemented
depends_on: []
---

## Objective

Make reproduction verification cover the claimed result and its selected checks, with task-scoped execution by default, explicit upstream reconstruction, task-based completion targets, and a small adoption path.

- **Task-based completion and lifecycle:** implement [task targets and step lifecycle](task-targets-and-lifecycle/task.md), replacing tiers with final deliverable/check targets and defining registration, rehoming, and retirement.
- **Scoped execution and evidence:** implement the [task-scoped build contract](task-scoped-builds/task.md). Build and status use the same task/step selection and saved-input boundary; upstream expansion is explicit. A claim names the verified steps and boundary. An empty selection cannot certify a result; scoped freshness, numerical validity, and end-to-end reproduction remain distinct claims.
- **Forced reruns:** scope and force are independent under that contract. Forcing never silently expands execution. Preview the effective scope without executing or changing evidence.
- **Protection coverage:** include selected protection checks in named completion targets, including check-only tasks; producer ancestry alone does not select downstream checks.
- **Authoring:** keep stable repo-relative paths and run selection in the task, shared roots and execution settings in config. Require declared paths to agree with runtime reads/writes. Use the existing path/config schema and cheap discovery.
- **Environment changes:** omit environment files from graph dependencies by default. Agents use Git diffs to judge reruns and investigate reproduction failures. Add no environment flag, assessment record, or runner-specific configuration; preserve existing explicitly configured `env_deps` as an opt-in.
- **Adoption and diagnosis:** provide a bounded one-producer/one-check pilot and a reusable acceptance recipe, used for adoption or mechanism changes. Diagnose changed outputs from evidence; preserve intentional saved-input boundaries and content-equivalent relocation semantics.
- **Validation:** an unbuilt target fails scoped status; unrelated stale work does not block it; selected protection checks block completion on failure. Exercise task-based CLI/dashboard selection, migration from tiers, the step lifecycle, and pilot cases for unchanged inputs, timestamps, helpers, missing/identical/corrupt/restored outputs. Undeclared environment changes skip all steps; explicit `env_deps` retain invalidation.
- **Force validation:** test fresh targets, stale upstream inputs, task/step unions and explicit producer expansion, complete reruns, and dry-run scope/evidence preservation against the task-scoped build contract.

## Revision Notes

The researcher selected tier removal and asked for an explicit step lifecycle; [task targets and lifecycle](task-targets-and-lifecycle/task.md) implements both.

## Details

The audience is researchers choosing what to rebuild and contributors implementing that contract. The accepted design keeps the existing content-based runner and task-local declarations.

- [Small-pilot feedback](../08-pilot-treasurygiv/attachments/2026-09-06-small-pilot-design-feedback.md) records slow discovery and the bounded-adoption proposal. [Earlier pilot](../08-pilot-treasurygiv/task.md#what-the-pilot-taught-the-model) records omitted protection checks.
- [Graph parser](../../../skills/task-tree/scripts/_repro.py), [selection/status](../../../skills/task-tree/scripts/_repro_state.py), and [runner entry](../../../skills/task-tree/scripts/repro_run.py) own tier normalization and target scope. Tier is absent from the step spec hash, allowing a rename without rebuilding.

- [Task query](../../../skills/task-tree/scripts/task_query.py), [dashboard server](../../../skills/task-tree/scripts/plan_dashboard.py), and [dashboard client](../../../skills/task-tree/scripts/templates/dashboard.js) expose tier values. Update their live contracts and current documentation together.
- [Reproducibility skill](../../../skills/reproducibility/SKILL.md) owns the verification and adoption rules; [task contract](../../../skills/task-tree/references/task-file-contract.md#reproduction-section) owns schema and command semantics. Follow the existing ownership split for workflow call sites.
- A same-byte output-root relocation currently stays fresh when it does not change the resolved command. Correct the explanatory promise rather than adding path-based invalidation. A corrupted output may be repaired by its producer before a downstream check runs; test rejection by the numerical check separately from successful repair.
- One temporary update task covers the shared parser/runner/skill edit surface. The existing skill-authoring task does not own CLI changes, and workflow-integration does not own runner semantics. Fold the validated outcome into the owning tasks during integration.

## Results

[Task-scoped builds](task-scoped-builds/task.md) implements the current selection, saved-input evidence, and concurrent-edit contract. Its results supersede the earlier upstream/force behavior below. [Task targets and lifecycle](task-targets-and-lifecycle/task.md) then removed tiers: every tier name, flag, and default below is historical.

### Earlier implementation evidence

The runner verifies explicit task/step targets, and the skill requires evidence for the claimed result and selected checks. `required` / `on-demand` are the displayed tier names; legacy inputs remain supported without rewriting declarations or invalidating existing locks.

- [Runner regression tests](../../../skills/task-tree/scripts/test_repro_runner.py) cover alias equivalence, lock preservation, missing on-demand targets, unrelated stale work, cross-tier ancestors, unknown targets, and a selected check-only task blocking required completion. The complete task-tree suite passed **1,047 tests** with pytask and the web dependencies installed. [Harness packaging check](../../../tests/check-harness-compatibility.sh), task-tree validation, skill validation, and Markdown checks also passed.
- A disposable two-step shell pilot passed first build, unchanged build, timestamp-only change, producer/helper edits, explicitly configured environment-dependency changes, missing output, identical-output suppression, direct corruption rejection, and restoration. Producer/helper edits made both steps report stale, but only the producer executed after identical regeneration. The saved input retained its original bytes and both steps finished fresh.
- In that tiny fixture, median unchanged CLI status/build times over three warm invocations were **0.054 s / 0.338 s**. Graph construction took **0.0012 s** and warm state computation **0.00085 s**; there were no shell resolvers. These observations validate the simple fixture, not a TreasuryGIV speedup. TreasuryGIV's dynamic branch/sandbox routing and revised resolver latency remain unmeasured in this change.
- [Pilot acceptance](../../../skills/reproducibility/references/pilot-acceptance.md) owns the reusable adoption matrix. The authoring instructions keep stable paths in the task, resolve shared dynamic roots cheaply, and bind declarations to runtime routing.
- [Environment changes](../../../skills/reproducibility/SKILL.md#environment-changes) use Git-based agent judgment; the default config example omits environment dependencies. A script-level fixture verified that editing each of `Project.toml`, `Manifest.toml`, `pyproject.toml`, and `uv.lock` left all steps fresh and executed none when undeclared. Explicitly configuring `Manifest.toml` as `env_deps` still invalidated every step after an edit. Environment handling added no runner logic or assessment machinery.

- Forced reruns now distinguish direct targets (`--force`) from the full producer closure (`--force-all`); `--tier all --force-all` executes every registered step. Transient per-step invalidation preserves successful locks and works with parallel execution. A failed forced run is retained in the existing run record and retried by ordinary builds even when declared inputs are unchanged.
- The force change passed **208 reproduction/core/CLI tests**, including 70 runner tests. Shell fixtures verify exact executed steps for target/task/tier scopes, stale ancestors with identical regeneration, full-graph reruns, parallel execution, dry-run evidence preservation, and retry after a failed forced check. Skill, Markdown, and task-tree validation passed.

- Review fixes passed **923 reproduction, CLI, task-tree, and dashboard tests**, including 77 runner tests. Six new alias/scope cases failed before the fixes and passed afterward; an additional fixture verifies that old alias locks rebuild only their affected consumer. Producer identity and sidecar state are shared across equivalent paths, and scoped status hashes only selected steps and ancestors. Clarity fixes remove duplicated rules and stale guidance, and permit existing numerical artifacts for figure checks. Skill, Markdown, and task validation passed.

Both independent Astra/high reviewers approved their fixes on narrow re-review: design/correctness verified alias identity, scoped hashing, and diagnosis with nine targeted tests; instruction clarity/CLAUDE.md compliance confirmed relocation guidance, deduplication, and figure-artifact flexibility. All six findings are resolved.
