---
title: "Claude Agent-SDK Skill-Load Harness"
status: not-started
depends_on:
  - 02-fixtures-and-parser
tags: []
created: 2026-06-19
---

## Objective

Build the Claude skill-load verification harness used by the stage, domain, and always-loaded live smokes (10–12). It drives the Python `claude-agent-sdk` with **in-process hooks** so skill loading is observable by name, reliably in headless mode — filesystem `PreToolUse` hooks do not fire under `claude -p` (see [load-testing-research.md](../../../../../tests/harness-instruction-following/references/load-testing-research.md)).

Deliverables:

- A Python runner that starts a `claude-agent-sdk` session **configured with the superRA plugin/skills directory** so `Skill(...)` resolves, registers in-process hooks — `PreToolUse(matcher="Skill")` recording each loaded skill name and its event index, and `InstructionsLoaded` recording CLAUDE.md/rules loads with `load_reason` — runs a supplied mock task, and returns structured evidence: skills loaded (name + order), instructions loaded, and the index of the first edit/write.
- A reusable assertion helper: assert a required set of skills loaded, and loaded **before** the first edit/write; produce a clear failure naming the missing or late skill.
- Opt-in gating identical to the existing smokes (`RUN_LIVE_HARNESS=1`), cheapest model default (`CLAUDE_MODEL=haiku`) with override, manual-only. The `claude-agent-sdk` dependency must be reachable only on the live path (supplied via `uv run --with`), never imported on any default-CI path.
- A CI-safe unit test for the evidence/assertion layer driven by synthetic hook records (no live call): green case plus red cases (required skill missing; skill loaded only after the first edit).
- Audit the existing `claude-live-smoke.sh` / `orchestrator-live-smoke.sh` use of `--include-hook-events` (undocumented/unconfirmed per the research): confirm whether it changes output and either drop it or document what it does.

Success criteria: a live run on the bundled `bundle-two-tasks` fixture records the skills the agent loaded by name (at minimum `using-superra`); the assertion library passes the green case and fails both red cases; the default `pytest` path neither imports `claude-agent-sdk` nor makes a model call.

### Constraints

- Manual-only; never added to default CI. The CI-safe unit test must run without `claude-agent-sdk` installed (mock/synthesize the hook records).
- Keep SDK session configuration (plugin dir, `setting_sources`, model) isolated in the harness; downstream smokes (10–12) consume the harness, not raw SDK calls.

## Planner Guidance

Reuse the bundled fixture and expected artifact from [02-fixtures-and-parser](../02-fixtures-and-parser/task.md); do not re-derive the mock scenario. Skill-load evidence comes from the hook callbacks, not transcript parsing — keep the existing `transcript_assertions.py` for ordering/task-read proxies and add the SDK-hook evidence as a separate module. Note the auto-loaded-vs-Skill-tool distinction: always-loaded skills may surface via `InstructionsLoaded` or a canary rather than a `Skill` tool_use (10 handles that case). Reference the SDK hooks docs and the reliability rationale in the research doc.
