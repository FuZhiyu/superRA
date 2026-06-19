---
title: "Agent Loading Tests"
status: revise
depends_on: []
tags: []
created: 2026-06-19
---

## Objective

Design and implement a small, durable test suite for superRA agent instruction-following, file-loading, and workflow-orchestrator behavior across Claude and Codex. The suite should answer: when a dispatch, role spec, stage, domain, task tree, or workflow trigger asks an agent to load a file, run `superra task read`, or dispatch a subagent by default, does the harness expose enough structural evidence that the agent did it before acting?

The scope is the agent-interface contract, not prose quality. The tests must avoid asserting generated prose. Prefer structural evidence: manifest and role-surface text, generated-agent drift checks, hook outputs, transcript tool events, `superra task read` output, sentinel files, and output artifacts whose values can only be produced after reading the required file.

Bundle related checks so one dispatch can test multiple behaviors. The live Claude and Codex smokes should run a compact multi-requirement scenario before adding one-off probes: one agent turn should need task-read context, dependency visibility, comment surfacing, external marker-file reads, and at least one manifest or role-surface load expectation whose evidence can be checked structurally. Keep the assigned task itself superficial and very quick: it should only require reading the fixture context and writing a tiny evidence JSON artifact, not solving a real coding or research problem.

### Required Behavior To Cover

- Baseline role requirements from `agents/implementer.md` and `agents/reviewer.md`: load skills per the `superRA:using-superra` Skill-Load Manifest and read each assigned task with `superra task read <path>` before code/file work.
- Stage loads from `skills/using-superra/SKILL.md`: `planning-review` loads `skills/superplan/references/planning-review.md`; `protection` loads `result-protection`; `sync` loads `semantic-merge`; `integration` loads `refactor-and-integrate`; `implementation` and `documentation` have no extra stage skill.
- Domain loads from the Skill-Load Manifest: `econ-data-analysis`, `theory-modeling`, `writing`, and `slide-design`, including any stage-scoped references owned by those domain skills.
- Direct-mode and harness-specific surfaces: main-agent direct mode uses `skills/using-superra/references/direct-mode-implementer.md` or `direct-mode-reviewer.md`; Codex additionally uses `skills/using-superra/references/codex-instructions.md`; generated `.codex/agents/*.toml` must stay aligned with canonical role specs.
- Task-read context behavior: `superra task read` exposes ancestor `## Objective` context, target body, unresolved comments, and sibling dependency status while not inheriting dependency `## Results`.
- Workflow-orchestrator behavior: when the user invokes `superimplement`, the main agent loads `superimplement`, follows its default subagent mode, loads `agent-orchestration` before dispatch, and dispatches implementer/reviewer subagents unless the harness lacks subagents, the user asks for direct mode, or the task is trivial enough for documented direct mode. Codex-specific evidence should use `skills/using-superra/references/codex-instructions.md` as the adapter authority.

### Constraints

- Live model calls are manual-only. Do not add Claude or Codex live tests to default CI.
- Use the dumbest/cheapest available harness settings: Claude defaults to `CLAUDE_MODEL=haiku`; Codex uses a configurable `CODEX_MODEL` and documents that this repo does not currently prescribe a cheapest Codex model.
- The live bundled task should complete in one short agent turn under normal conditions. Avoid prompts that invite broad codebase exploration, real implementation, package installs, long test suites, or domain reasoning.
- Keep reusable transcript parsing in Python under `tests/harness-instruction-following/`, not embedded shell heredocs.
- Keep deterministic hook-only and fixture tests CI-safe.
- Treat ambiguous terminology drift, such as `Stage: protection` versus older `drift-test` wording, as a static lint or follow-up finding rather than a live-agent behavior assertion.

## Planner Guidance

Recommended target layout:

- `tests/harness-instruction-following/parse_harness_jsonl.py`
- `tests/harness-instruction-following/assertions.py`
- `tests/harness-instruction-following/test_contract.py`
- `tests/harness-instruction-following/run-claude.sh`
- `tests/harness-instruction-following/run-codex.sh`
- `tests/harness-instruction-following/run-orchestrator.sh` or an equivalent `--scenario orchestrator-superimplement` mode in the live scripts
- `tests/fixtures/task-trees/bundle-two-tasks/`
- `tests/fixtures/task-trees/minimal-superra/`
- `tests/fixtures/task-trees/review-round/`

Use existing scripts as style references: `tests/hooks/test-e2e-cli.sh` for Claude stream JSON and `tests/hooks/test-codex-e2e-cli.sh` for Codex JSONL. The implementation may revise locations if an adjacent existing test directory is a better fit, but it must preserve the CI/manual boundary. Build `bundle-two-tasks` as the primary live fixture and keep smaller fixtures for parser/unit isolation. The fixture task should look realistic in shape, with ordinary `task.md` files, dependency metadata, comments, marker files, and role/stage dispatch text, but the required work should be no more than copying sentinel values into an evidence JSON file. For orchestrator behavior, use a separate mock frontier whose implementation is intentionally trivial; the test target is whether the orchestrator chooses the documented dispatch path for `superimplement`, not whether the subagent performs meaningful work.

## Results
