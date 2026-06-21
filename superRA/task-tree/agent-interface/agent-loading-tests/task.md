---
title: "Agent Loading Tests"
status: approved
depends_on: []
tags: []
created: 2026-06-19
---

## Objective

Design and implement a small, durable test suite for superRA agent instruction-following, file-loading, and workflow-orchestrator behavior across Claude and Codex. The suite answers one question: when a dispatch, role spec, stage, domain, task tree, or workflow trigger asks an agent to load a file, run `superra task read`, or dispatch a subagent by default, does the harness expose enough structural evidence that the agent did it before acting?

The scope is the agent-interface contract, not prose quality. The tests avoid asserting generated prose. They prefer structural evidence: manifest and role-surface text, generated-agent drift checks, hook outputs, transcript tool events, `superra task read` output, sentinel files, and output artifacts whose values can only be produced after reading the required file.

### Required Behavior To Cover

- Baseline role requirements from `agents/implementer.md` and `agents/reviewer.md`: load skills per the `superRA:using-superra` Skill-Load Manifest and read each assigned task with `superra task read <path>` before code/file work.
- Stage loads from `skills/using-superra/SKILL.md`: `planning-review` loads `skills/superplan/references/planning-review.md`; `protection` loads `result-protection`; `sync` loads `semantic-merge`; `integration` loads `refactor-and-integrate`; `maturation` loads `task-tree` + `superplan` (always) plus `writing` (conditional for prose-heavy maturation); `implementation` and `documentation` have no extra stage skill.
- Domain loads from the Skill-Load Manifest: `econ-data-analysis`, `theory-modeling`, `writing`, and `slide-design`, including any stage-scoped references owned by those domain skills.
- Direct-mode and harness-specific surfaces: main-agent direct mode uses `skills/using-superra/references/direct-mode-implementer.md` or `direct-mode-reviewer.md`; Codex additionally uses `skills/using-superra/references/codex-instructions.md`; generated `.codex/agents/*.toml` must stay aligned with canonical role specs.
- Task-read context behavior: `superra task read` exposes ancestor `## Objective` context, target body, unresolved comments, and sibling dependency status while not inheriting dependency `## Results`.
- Workflow-orchestrator behavior: when the user invokes `superimplement`, the main agent loads `superimplement`, follows its default subagent mode, loads `agent-orchestration` before dispatch, and dispatches implementer/reviewer subagents unless the harness lacks subagents, the user asks for direct mode, or the task is trivial enough for documented direct mode. Codex-specific evidence uses `skills/using-superra/references/codex-instructions.md` as the adapter authority.

### Constraints

- Live model calls are manual-only. Do not add Claude or Codex live tests to default CI.
- Use the dumbest/cheapest available harness settings: Claude defaults to `CLAUDE_MODEL=haiku` (the always-loaded/stage/domain SDK canaries default to `sonnet` for reliable dispatch); Codex uses a configurable `CODEX_MODEL` and documents that this repo does not currently prescribe a cheapest Codex model.
- The live bundled task should complete in one short agent turn under normal conditions. Avoid prompts that invite broad codebase exploration, real implementation, package installs, long test suites, or domain reasoning.
- Keep reusable transcript parsing in Python under `tests/harness-instruction-following/`, not embedded shell heredocs.
- Keep deterministic hook-only and fixture tests CI-safe.
- Treat ambiguous terminology drift, such as `Stage: protection` versus older `drift-test` wording, as a static lint or follow-up finding rather than a live-agent behavior assertion.

## Results

The suite lives under [tests/harness-instruction-following/](../../../../../tests/harness-instruction-following/); its [README.md](../../../../../tests/harness-instruction-following/README.md) is the canonical reference — the LC001–LC023 coverage matrix (each row mapped to its covering test and layer), the four-layer structure, the CI/manual boundary, and the honest coverage caveats. [load_contract.json](../../../../../tests/harness-instruction-following/load_contract.json) is the machine-readable source of truth behind the matrix; `test_contract.py::test_every_load_contract_entry_carries_covered_by` keeps the two from drifting.

**Coverage across four layers.** Every load-contract entry LC001–LC023 carries at least static or fixture coverage; live rows extend the strongest ones:

- **Static CI** parses committed source/JSON and asserts the contract is present — the Skill-Load Manifest rows, the role/generated surfaces that must name the manifest and `superra task read`, the hook registries, and the workflow-orchestration surfaces. The generated-agent drift check runs `sync_codex_agents.py --check`, so a hand-edited `.codex/agents/*.toml` that diverges from its role spec fails CI.
- **Fixture / parser unit tests** drive the real `task_read.py` against the committed `bundle-two-tasks` fixture (confirming ancestor `## Objective` context, unresolved comments, and sibling dependency status surface while a dependency's `## Results` never leaks) and the transcript parser against committed sample transcripts (ordering, dispatch, fallback, artifact-diff, with red cases).
- **Live-claude** (opt-in, gated on `RUN_LIVE_HARNESS=1`) drives a real Claude agent through the Python `claude-agent-sdk` — `claude -p` filesystem hooks do not fire (issue #40506), so on-demand skill loads are recorded by an in-process `PreToolUse(matcher="Skill")` hook (plus an opt-in `Read` hook for reference loads). The always-loaded skills preload via agent frontmatter `skills: [...]`, so they are evidenced by a static frontmatter contract plus a live behavioral introspection canary (zero `Skill`-tool loads is the expected signal).
- **Live-codex** (opt-in) uses per-skill canary/side-effect proxies whose skill-unique tokens are only producible if the skill body loaded, plus a `SubagentStart` hook for dispatch — codex JSONL exposes neither skill loads nor subagent spawns.

**Coverage reach.** Live-claude rows are verified for the always-loaded skills (LC001), all four non-empty stages (LC002, LC007–LC010), and all four domains plus the multi-domain every-match rule (LC003, LC011–LC014). The Codex side is built and CI-tested on synthetic inputs but live-pending (no credentials). LC023 (`maturation` → `task-tree` + `superplan`, `writing` conditional) is fixture-covered, live-pending both harnesses. The orchestrator-dispatch smoke (LC020–LC022) is built; its live run is pending. Per the README caveats: loading ≠ full rule-compliance, sub-reference routing within a loaded skill is static-only, and the Codex always-loaded canary is a weak standalone proxy backstopped by the Claude hook and SubagentStart hook.

**Deferred-import CI boundary.** [test_deferred_import_isolation.py](../../../../../tests/harness-instruction-following/test_deferred_import_isolation.py) locks in that importing any live-harness module pulls neither `claude_agent_sdk` nor a codex-cli client into `sys.modules` and makes no model call — the SDK import stays deferred inside the live entry point, so the default CI path never touches it.

**Verification:** CI-safe suite green — `uv run --with pytest --with pyyaml python -m pytest tests/harness-instruction-following` → 140 passed. Generated-agent drift check clean (`sync_codex_agents.py --scope project --check`).

## Review Notes
