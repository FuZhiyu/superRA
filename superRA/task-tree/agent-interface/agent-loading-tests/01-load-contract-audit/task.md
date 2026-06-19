---
title: "Audit Agent Load Contract"
status: not-started
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

## Planner Guidance

Prefer a compact checked-in artifact such as `tests/harness-instruction-following/load_contract.json` or `load_contract.yml` plus a short README table. Do not duplicate long instruction prose from the source files; store source paths, triggers, and expected evidence.

If the audit finds inconsistent stage terminology or an untestable requirement, record it as a static finding with a proposed owner rather than forcing it into live-agent tests.

## Results

