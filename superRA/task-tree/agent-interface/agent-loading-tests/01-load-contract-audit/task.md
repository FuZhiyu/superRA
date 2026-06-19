---
title: "Audit Agent Load Contract"
status: approved
depends_on: []
tags: []
created: 2026-06-19
---

## Objective

Create a machine-readable or tightly structured audit of the agent loading contract that future tests can target. The audit should identify each required load source, the trigger that should cause it, the expected observable evidence, and whether it belongs in CI-safe checks or manual live-harness checks.

At minimum, cover:

- `skills/using-superra/SKILL.md` always-loaded skills, stage rows, domain rows, and harness adapter references.
- `agents/implementer.md`, `agents/reviewer.md`, generated direct-mode references, and generated `.codex/agents/*.toml`.
- `skills/superplan/references/planning-review.md`, `result-protection`, `semantic-merge`, and `refactor-and-integrate` stage requirements.
- Domain skills `econ-data-analysis`, `theory-modeling`, `writing`, and `slide-design`.
- `task_read.py` / `task-file-contract.md` behavior for ancestor context, comments, dependency status, and dependency result non-inheritance.
- Hook registries in `hooks.json` and `hooks-codex.json`.
- Workflow-orchestrator behavior from `skills/superimplement/SKILL.md`, `skills/agent-orchestration/SKILL.md`, and `skills/using-superra/references/codex-instructions.md`: `superimplement` default subagent mode, required `agent-orchestration` load before dispatch, implementer/reviewer dispatch templates, and documented direct-mode/fallback exceptions.

## Planner Guidance

Prefer a compact checked-in artifact such as `tests/harness-instruction-following/load_contract.json` or `load_contract.yml` plus a short README table. Do not duplicate long instruction prose from the source files; store source paths, triggers, and expected evidence.

If the audit finds inconsistent stage terminology or an untestable requirement, record it as a static finding with a proposed owner rather than forcing it into live-agent tests.

## Results

Created [load_contract.json](../../../../../tests/harness-instruction-following/load_contract.json) as the machine-readable audit artifact and [README.md](../../../../../tests/harness-instruction-following/README.md) as a short index table for the planned harness instruction-following suite.

### Coverage

- The audit records 22 contract entries covering the Skill-Load Manifest, canonical role specs, generated direct-mode and Codex agent surfaces, stage loads, domain loads, task-read behavior, hook registries, and workflow-orchestrator behavior.
- Each entry includes source paths, trigger, expected observable evidence, and CI-safe/manual-live classification.
- Task-read entries separate deterministic fixture coverage for ancestor context, unresolved comments, sibling dependency status, and dependency-result non-inheritance.
- Workflow entries distinguish static source checks from manual live transcript evidence for `superimplement`, `agent-orchestration`, and Codex named-agent dispatch behavior.

### Static Findings

- `SF001`: the task objective uses shorthand `hooks.json` / `hooks-codex.json`, while committed hook registries live at [hooks/hooks.json](../../../../../hooks/hooks.json) and [hooks/hooks-codex.json](../../../../../hooks/hooks-codex.json).
- `SF002`: `Stage: protection` is the manifest term, but some sources still use `drift-test` terminology, including [result-protection/SKILL.md](../../../../../skills/result-protection/SKILL.md), [theory-modeling/SKILL.md](../../../../../skills/theory-modeling/SKILL.md), and [agent-orchestration/SKILL.md](../../../../../skills/agent-orchestration/SKILL.md).
- `SF003`: Codex Bash hook coverage is documented as best-effort, so future tests should avoid treating it as a complete live enforcement boundary.
- `SF004`: direct-mode fallback is observable only when a transcript records a dispatch path or explicit allowed fallback reason.

### Verification

- `python3 -m json.tool tests/harness-instruction-following/load_contract.json`
- `python3 skills/report-in-markdown/scripts/check_markdown.py tests/harness-instruction-following/README.md superRA/task-tree/agent-interface/agent-loading-tests/01-load-contract-audit/task.md`
