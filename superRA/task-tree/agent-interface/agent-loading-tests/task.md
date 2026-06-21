---
title: "Agent Loading Tests"
status: approved
depends_on: []
tags: []
created: 2026-06-19
---

## Objective

Design and implement a small, durable test suite for superRA agent instruction-following, file-loading, and workflow-orchestrator behavior across Claude and Codex. The suite should answer: when a dispatch, role spec, stage, domain, task tree, or workflow trigger asks an agent to load a file, run `superra task read`, or dispatch a subagent by default, does the harness expose enough structural evidence that the agent did it before acting?

The scope is the agent-interface contract, not prose quality. The tests must avoid asserting generated prose. Prefer structural evidence: manifest and role-surface text, generated-agent drift checks, hook outputs, transcript tool events, `superra task read` output, sentinel files, and output artifacts whose values can only be produced after reading the required file.

### Context

The first implementation pass (tasks 01–07) delivered the CI-safe static/fixture layer plus live smokes for the **implementation / task-read / dispatch** slice using observable proxies. Tasks 08–13 extend live coverage to the rest of the `manual_live_*` contracts the audit catalogued in [load_contract.json](../../../../../tests/harness-instruction-following/load_contract.json) but the smokes do not yet exercise: every always-loaded skill **by name** (`using-superra` **and** `report-in-markdown`, LC001), every non-empty **stage** load (planning-review/protection/sync/integration, LC002/LC007–LC010), and every **domain** load (econ-data-analysis/theory-modeling/writing/slide-design, LC003/LC011–LC014).

Mechanism (researcher-approved) and the harness constraints that force it are recorded in [load-testing-research.md](../../../../../tests/harness-instruction-following/references/load-testing-research.md). In short: skill/context loading is not directly observable from raw transcripts, so the suite verifies it through (a) **Claude: the Python `claude-agent-sdk` driven with in-process `PreToolUse(matcher="Skill")` + `InstructionsLoaded` hooks**, giving real skill-load-by-name evidence reliably in headless mode (filesystem hooks do not fire under `claude -p`); and (b) **Codex: canary/side-effect proxies** (a skill-unique observable action only producible if the skill body loaded) plus a **`SubagentStart` hook** for subagent dispatch, since codex JSONL exposes neither skill loads nor subagent spawns. A failing load assertion (e.g. `report-in-markdown` never loads) is a real finding in the loading contract to escalate, not a reason to weaken the test.

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

Per-subtask implementation results for the suite live in the 01–13 child tasks. This section records the integration-stage codebase-fit pass only.

**Final diff self-check:** `git diff 1739a8ff..HEAD`; surviving-change classes — (1) new instruction-following test suite under [tests/harness-instruction-following/](../../../../../tests/harness-instruction-following/) + fixtures under [tests/fixtures/task-trees/](../../../../../tests/fixtures/task-trees/) (this task's objective); (2) removal of the four prose-regression shell tests `test-{mistral,slide-design,zotero}-skill-text.sh` and `test-sync-integration-contract.sh`, plus the corresponding `Sync integration contract` / `Direct mode role references` sections in [tests/check-harness-compatibility.sh](../../../../../tests/check-harness-compatibility.sh) (objective: replace prose-regression assertions with structural-evidence tests); (3) the `role-spec-always-load` role-spec/generator/generated-artifact change (sibling task); (4) the carried-along better-handoff hook fix in `task_hook.py` + `internals.md` + `test_task_tree.py` (commit 72420b3c, in-tree convention); (5) my integration-pass doc edit to [tests/harness-instruction-following/README.md](../../../../../tests/harness-instruction-following/README.md) (Project Doc Audit, see below). Suspicious-hunk justifications: the `skills/writing/CLAUDE.md` enforcement-claim removal and the README LC-range staleness are adjudicated in `## Revision Notes`; no other suspicious hunks.

**Integration-pass edits (this turn):**
- [tests/harness-instruction-following/README.md](../../../../../tests/harness-instruction-following/README.md): added the missing **LC023** (`maturation` stage) row to the coverage matrix and corrected the matrix range claim from "LC001–LC022" to "LC001–LC023". The trunk-sync commit `0ae25595` added LC023 to [load_contract.json](../../../../../tests/harness-instruction-following/load_contract.json) and referenced it in the README body (per-stage section), but left the matrix table and its "maps every entry LC001–LC022" claim stale. No CI test cross-checks the README matrix against the contract entry set (`test_every_load_contract_entry_carries_covered_by` only verifies each contract entry has a `covered_by` block), so the drift was silent.

**Verification:** CI-safe suite green — `uv run --with pytest --with pyyaml python -m pytest tests/harness-instruction-following` → 140 passed (re-run after the README edit). Generated-agent drift check clean (`sync_codex_agents.py --scope project --check`). Task-tree hook tests green (35 passed) confirming the carried-along `task_hook.py` change is consistent. No dangling references to the four deleted shell tests in live code or docs (only dated `docs/plans/` permanent records mention them, correctly left as historical).

## Revision Notes

**Integration-pass first-round adjudication (orchestrator).** The integration self-review raised two MINOR concerns; both adjudicated, no code change required:

1. **Writing-ownership invariant now doc-only — accepted as designed.** Deleting `tests/test-sync-integration-contract.sh` removes the prose-regression assertion that the writing review-only task-tree exception must not migrate into the workflow skills, leaving that invariant enforced by docs/ownership-boundary convention rather than a test. This is the intended consequence of this task's objective (replace prose-regression assertions with structural-evidence tests), not a regression. The `skills/writing/CLAUDE.md` edit correctly dropped the now-false "contract tests enforce this" sentence.
2. **No CI guard that the README matrix matches `load_contract.json` — deferred follow-up.** The immediate drift (missing LC023 row, stale "LC001–LC022" range) was fixed this pass. A guard test asserting the README coverage matrix lists every contract entry is net-new coverage beyond this integration's scope; recorded here as a candidate follow-up (extend `test_contract.py`), not added now.

## Review Notes
