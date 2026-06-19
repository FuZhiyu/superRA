---
title: "Codex Canary + SubagentStart Dispatch Hook"
status: not-started
depends_on:
  - 02-fixtures-and-parser
  - 07-orchestrator-behavior-smoke
tags: []
created: 2026-06-19
---

## Objective

Establish the Codex evidence mechanism for skill loading and subagent dispatch, neither of which is observable in `codex exec --json` (no `skill_loaded` event, no `spawn_agent` item — see [load-testing-research.md](../../../../../tests/harness-instruction-following/references/load-testing-research.md)). This is the Codex counterpart to the Claude SDK harness (08), consumed by the stage/domain/always-loaded smokes (10–12).

Deliverables:

- A **canary / side-effect convention**: a reusable way for a fixture task to require a skill-unique observable action — a command the skill body prescribes (surfacing as a `command_execution`) or a sentinel value in the output artifact — that is only producible if the named skill body was loaded. Plus the evaluator that checks the canary from codex JSONL / the artifact.
- A **`SubagentStart` hook** (matcher = agent type) wired into the codex live profile that appends agent-type sentinels (`superra_implementer` / `superra_reviewer`) to a log file, so orchestrator dispatch is verifiable out-of-band even though JSONL hides it. Disambiguate by the hook payload, not by `session_id`.
- Opt-in gating; reuse the temporary-profile pattern from `codex-live-smoke.sh`. Pin to codex-cli 0.140.0 event shapes (`type`/`agent_message`, `command_execution`, `file_change`).
- CI-safe unit tests for the canary evaluator and the hook-payload handler on synthetic inputs: green plus red cases.

Success criteria: a live codex run produces the canary side-effect for a loaded skill and the `SubagentStart` log records dispatched agent types (or the documented direct-mode fallback); red cases (canary absent; no dispatch and no fallback) fail; the default `pytest` path runs the evaluator/hook-handler unit tests with no model call.

### Constraints

- Manual-only; never added to default CI.
- Keep the canary convention generic enough to be reused by the stage (11) and domain (12) smokes without per-skill bespoke parsing.

## Planner Guidance

Build on the existing codex smoke + orchestrator smoke ([04](../04-codex-live-smoke/task.md), [07](../07-orchestrator-behavior-smoke/task.md)) rather than starting fresh. The `SubagentStart` hook is the only reliable codex dispatch signal — it supersedes the JSONL-based detection in 07 for the codex orchestrator path; keep 07's claude path as-is. Where a skill's natural output already encodes a skill-unique value, prefer that over inventing an artificial canary command.
