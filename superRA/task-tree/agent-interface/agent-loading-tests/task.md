---
title: "Agent Loading Tests"
status: not-started
depends_on: []
tags: []
created: 2026-06-19
---

## Objective

Design and implement a small, durable test suite for superRA agent instruction-following and file-loading behavior across Claude and Codex. The suite should answer: when a dispatch, role spec, stage, domain, or task tree asks an agent to load a file or run `superra task read`, does the harness expose enough structural evidence that the agent did it before acting?

The scope is the agent-interface contract, not prose quality. The tests must avoid asserting generated prose. Prefer structural evidence: manifest and role-surface text, generated-agent drift checks, hook outputs, transcript tool events, `superra task read` output, sentinel files, and output artifacts whose values can only be produced after reading the required file.

### Required Behavior To Cover

- Baseline role requirements from `agents/implementer.md` and `agents/reviewer.md`: load skills per the `superRA:using-superra` Skill-Load Manifest and read each assigned task with `superra task read <path>` before code/file work.
- Stage loads from `skills/using-superra/SKILL.md`: `planning-review` loads `skills/superplan/references/planning-review.md`; `protection` loads `result-protection`; `sync` loads `semantic-merge`; `integration` loads `refactor-and-integrate`; `implementation` and `documentation` have no extra stage skill.
- Domain loads from the Skill-Load Manifest: `econ-data-analysis`, `theory-modeling`, `writing`, and `slide-design`, including any stage-scoped references owned by those domain skills.
- Direct-mode and harness-specific surfaces: main-agent direct mode uses `skills/using-superra/references/direct-mode-implementer.md` or `direct-mode-reviewer.md`; Codex additionally uses `skills/using-superra/references/codex-instructions.md`; generated `.codex/agents/*.toml` must stay aligned with canonical role specs.
- Task-read context behavior: `superra task read` exposes ancestor `## Objective` context, target body, unresolved comments, and sibling dependency status while not inheriting dependency `## Results`.

### Constraints

- Live model calls are manual-only. Do not add Claude or Codex live tests to default CI.
- Use the dumbest/cheapest available harness settings: Claude defaults to `CLAUDE_MODEL=haiku`; Codex uses a configurable `CODEX_MODEL` and documents that this repo does not currently prescribe a cheapest Codex model.
- Keep reusable transcript parsing in Python under `tests/harness-instruction-following/`, not embedded shell heredocs.
- Keep deterministic hook-only and fixture tests CI-safe.
- Treat ambiguous terminology drift, such as `Stage: protection` versus older `drift-test` wording, as a static lint or follow-up finding rather than a live-agent behavior assertion.

## Planner Guidance

Recommended target layout:

- `tests/harness-instruction-following/parse_harness_jsonl.py`
- `tests/harness-instruction-following/assertions.py`
- `tests/harness-instruction-following/run-claude.sh`
- `tests/harness-instruction-following/run-codex.sh`
- `tests/fixtures/task-trees/minimal-superra/`
- `tests/fixtures/task-trees/review-round/`
- `tests/fixtures/task-trees/bundle-two-tasks/`

Use existing scripts as style references: `tests/hooks/test-e2e-cli.sh` for Claude stream JSON and `tests/hooks/test-codex-e2e-cli.sh` for Codex JSONL. The implementation may revise locations if an adjacent existing test directory is a better fit, but it must preserve the CI/manual boundary.

## Results

## Review Notes

1. [BLOCKING] The subtree does not assign ownership for the CI-safe static/hook assertions required by the parent objective. The parent requires structural checks over manifest/role text, generated-agent drift, hook outputs, stage/domain/direct-mode surfaces, and task-read context behavior ([task.md:11-29](task.md#L11-L29)), but the children only create an audit artifact ([01-load-contract-audit/task.md:11-26](01-load-contract-audit/task.md#L11-L26)), parser/fixture infrastructure for live transcripts ([02-fixtures-and-parser/task.md:12-32](02-fixtures-and-parser/task.md#L12-L32)), manual live smokes, and documentation. The docs task even expects static CI checks and hook unit tests to exist ([05-docs-ci-boundary/task.md:13-27](05-docs-ci-boundary/task.md#L13-L27)), but no prerequisite child produces them. Fix by adding a CI-safe test child, or expanding an existing child objective, to implement deterministic assertions that check the audit/contract against `skills/using-superra/SKILL.md`, role specs, direct-mode/generated Codex surfaces, hook registries, and task-read fixtures; wire downstream dependencies so the live and documentation tasks consume those outputs.
