---
title: "Codex Canary + SubagentStart Dispatch Hook"
status: implemented
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

## Results

Established the Codex evidence mechanism as a CI-safe evidence module plus a manual-only live hook, mirroring the Claude SDK harness (08) so the two sides stay consistent for the 10–12 consumers. The evidence module never imports codex-cli and makes no model call.

**Modules added (all under `tests/harness-instruction-following/`):**

- [codex_load_evidence.py](../../../../../tests/harness-instruction-following/codex_load_evidence.py) — the CI-safe evidence layer, the Codex counterpart to `sdk_load_evidence.py`. Two channels:
  - **Canary / side-effect.** `CanarySpec` ([codex_load_evidence.py:66](../../../../../tests/harness-instruction-following/codex_load_evidence.py#L66)) names a skill, a high-entropy `token`, and the source(s) that prove the skill body loaded — `in_command` (the token appears in a `command_execution` command the skill body prescribed) and/or `in_artifact_field` (a dotted JSON path in the output artifact whose value must equal the token). `evaluate_canary` ([codex_load_evidence.py:123](../../../../../tests/harness-instruction-following/codex_load_evidence.py#L123)) scans both sources; the canary fails only if none of its enabled sources carry the token, and the failure names the skill and reads as a "skill body did not load" finding to escalate. The "token in command OR token at artifact field" convention is generic — 11/12 supply per-skill `CanarySpec` rows with no bespoke parsing; `command_strings_from_events` ([codex_load_evidence.py:194](../../../../../tests/harness-instruction-following/codex_load_evidence.py#L194)) feeds it from the shared `transcript_assertions` codex parser, so it stays pinned to the codex-cli 0.140.0 `command_execution` shape via that single parser.
  - **SubagentStart dispatch log.** `handle_subagent_start_payload` ([codex_load_evidence.py:224](../../../../../tests/harness-instruction-following/codex_load_evidence.py#L224)) is the shared payload handler: it pulls the agent type from the payload (accepting `agent_type`/`subagent_type`/`name` etc. defensively) and **disambiguates by the agent-type field, not `session_id`** — a payload with only a session id yields `None` and nothing is logged. `append_subagent_start` applies it and appends the bare agent-type sentinel; `evaluate_dispatch_log` ([codex_load_evidence.py:282](../../../../../tests/harness-instruction-following/codex_load_evidence.py#L282)) requires each of `superra_implementer` / `superra_reviewer` to appear.
- [subagent_start_hook.py](../../../../../tests/harness-instruction-following/subagent_start_hook.py) — the live hook executable wired into the codex profile. Stdlib-only, reads the payload from stdin, appends the agent type to the file named by `SUPERRA_SUBAGENT_LOG` via the shared handler, and always emits `{}` + exit 0 so it never blocks or perturbs the codex run (malformed/empty payload records nothing).
- [test_codex_load_evidence.py](../../../../../tests/harness-instruction-following/test_codex_load_evidence.py) — 18 CI-safe unit tests on synthetic inputs (no codex-cli, no model call): canary green (in command, in artifact field, either-source), canary red (absent from all sources; artifact field missing), `evaluate_canaries` collecting all failures, codex `command_execution` extraction via the shared parser; payload handler (agent-type extraction, alternate key spellings, **session-id-only payload yields nothing**); dispatch-log green/red (missing reviewer; empty); and the live hook executable end-to-end on a synthetic payload (appends; survives malformed JSON).

**Wiring (orchestrator smoke codex path).** [orchestrator-live-smoke.sh](../../../../../tests/harness-instruction-following/orchestrator-live-smoke.sh) now generates two `SubagentStart` hook entries in the temporary codex profile (matcher = each agent type), each running `subagent_start_hook.py` with `SUPERRA_SUBAGENT_LOG` pointed at a per-run dispatch log, and passes `--dispatch-log` to the checker. [check_orchestrator_smoke.py](../../../../../tests/harness-instruction-following/check_orchestrator_smoke.py) routes the codex path through `_check_codex_with_dispatch_log` ([check_orchestrator_smoke.py:84](../../../../../tests/harness-instruction-following/check_orchestrator_smoke.py#L84)): the SubagentStart log is the dispatch signal (superseding JSONL detection for codex), falling back to a documented direct-mode exception named in the transcript only when the log is empty. The claude path is unchanged (still keys off `Task`/`Agent` events). Reuses the temporary-profile + `RUN_LIVE_HARNESS=1` opt-in pattern from the existing codex smoke.

**README.** [README.md](../../../../../tests/harness-instruction-following/README.md) updated: the per-harness dispatch-evidence section now documents the codex SubagentStart out-of-band mechanism, and the "specific skill loaded" non-tested-through-prose bullet documents the codex canary convention and that an absent canary is a real finding.

**Verification (live-verified vs not):**

- CI-safe suite: `uv run --with pytest --with pyyaml python -m pytest tests/harness-instruction-following` → **52 passed** (was 34; +18 from `test_codex_load_evidence.py`).
- codex-cli isolation: the default pytest path imports only `codex_load_evidence` (asserted no `codex_cli*` module enters `sys.modules`); the module and the hook executable are stdlib-only.
- Generated codex profile validated this session: the profile-generation Python produces valid TOML with two `SubagentStart` entries (matchers `superra_implementer`, `superra_reviewer`); `bash -n` on the smoke passes.
- End-to-end checker behavior validated this session on synthetic log + transcript: green (both sentinels logged) → PASS rc 0; red (missing reviewer, no fallback) → FAIL rc 1; empty log + documented direct-mode exception in transcript → PASS-with-skip rc 0.
- **NOT live-verified (handoff):** the actual live codex run (`RUN_LIVE_HARNESS=1 HARNESS=codex bash tests/harness-instruction-following/orchestrator-live-smoke.sh`, and a canary-producing codex loading run) was not executed — no codex credentials authorized this turn, matching how 08 left its live SDK step. The success criteria "a live codex run produces the canary side-effect" and "the SubagentStart log records dispatched agent types" remain to be confirmed on a credentialed machine. The codex `SubagentStart` payload key for the agent type is handled defensively (`agent_type`/`subagentType`/`name` etc.); the exact key codex-cli 0.140.0 sends should be confirmed against the installed CLI on the first live run, and the `SubagentStart` matcher = agent-type TOML form should be confirmed to fire per agent type.
