---
title: "Claude Agent-SDK Skill-Load Harness"
status: revise
depends_on:
  - 02-fixtures-and-parser
tags: []
created: 2026-06-19
---

## Objective

Build the Claude skill-load verification harness used by the stage, domain, and always-loaded live smokes (10–12). It drives the Python `claude-agent-sdk` with **in-process hooks** so skill loading is observable by name, reliably in headless mode — filesystem `PreToolUse` hooks do not fire under `claude -p` (see [load-testing-research.md](../../../../../tests/harness-instruction-following/references/load-testing-research.md)).

Deliverables:

- A Python runner that starts a `claude-agent-sdk` session **configured with the superRA plugin/skills directory** so `Skill(...)` resolves and **dispatches the real plugin agent** (`superRA:implementer` / `superRA:reviewer`, available in the SDK init `agents` list) rather than a bare `query()` — only a real role dispatch reproduces the manifest-driven loads. Register the in-process `PreToolUse(matcher="Skill")` hook (records each on-demand loaded skill name + event index, including loads inside the dispatched subagent) and `PreToolUse(matcher="Edit|Write")` (first edit index). Return structured evidence: on-demand skills loaded (name + order) and the first-edit index. **Do not register an `InstructionsLoaded` hook — it is not a real `claude-agent-sdk` hook event (see Revision Notes); registering it is a silent no-op.**
- **Always-loaded skill coverage is a separate mechanism.** `using-superra` and `report-in-markdown` are preloaded via agent frontmatter `skills: [...]`, not loaded through the `Skill` tool, so the `Skill` hook cannot see them. Provide (a) a CI-safe **static frontmatter contract** check asserting both `agents/implementer.md` and `agents/reviewer.md` declare both skills in `skills:`, and (b) a hook/helper that task 10 uses for a live **behavioral canary** (proof a preloaded skill shaped output). Leave the live canary fixtures to task 10; task 08 owns the reusable checker.
- A reusable assertion helper: assert a required set of skills loaded, and loaded **before** the first edit/write; produce a clear failure naming the missing or late skill.
- Opt-in gating identical to the existing smokes (`RUN_LIVE_HARNESS=1`), cheapest model default (`CLAUDE_MODEL=haiku`) with override, manual-only. The `claude-agent-sdk` dependency must be reachable only on the live path (supplied via `uv run --with`), never imported on any default-CI path.
- A CI-safe unit test for the evidence/assertion layer driven by synthetic hook records (no live call): green case plus red cases (required skill missing; skill loaded only after the first edit).
- Audit the existing `claude-live-smoke.sh` / `orchestrator-live-smoke.sh` use of `--include-hook-events` (undocumented/unconfirmed per the research): confirm whether it changes output and either drop it or document what it does.

Success criteria: a live run dispatching the real `superRA:implementer` agent on the bundled `bundle-two-tasks` fixture records, by name, at least one on-demand skill the agent loaded via the `Skill` tool (the manifest's stage/domain load for the fixture); the `Skill` PreToolUse hook is confirmed to fire for tool use inside the dispatched subagent; the static frontmatter contract check passes for both role specs; the assertion library passes the green case and fails both red cases; the default `pytest` path neither imports `claude-agent-sdk` nor makes a model call.

### Constraints

- Manual-only; never added to default CI. The CI-safe unit test must run without `claude-agent-sdk` installed (mock/synthesize the hook records).
- Keep SDK session configuration (plugin dir, `setting_sources`, model) isolated in the harness; downstream smokes (10–12) consume the harness, not raw SDK calls.

## Planner Guidance

Reuse the bundled fixture and expected artifact from [02-fixtures-and-parser](../02-fixtures-and-parser/task.md); do not re-derive the mock scenario. On-demand skill-load evidence comes from the `Skill` PreToolUse hook, not transcript parsing — keep the existing `transcript_assertions.py` for ordering/task-read proxies and keep the SDK-hook evidence as a separate module. The auto-loaded-vs-Skill-tool distinction is now load-bearing and resolved: preloaded (`skills:` frontmatter) skills are covered by the static contract check + behavioral canary, on-demand skills by the `Skill` hook — keep the two channels separate rather than unioning them.

## Results

Built the Claude skill-load harness as a CI-safe evidence/assertion layer plus a manual-only live runner, split so the `claude-agent-sdk` dependency is reachable only on the live path.

**Modules added (all under `tests/harness-instruction-following/`):**

- [sdk_load_evidence.py](../../../../../tests/harness-instruction-following/sdk_load_evidence.py) — CI-safe evidence model + assertions. `SkillLoadEvidence` carries skill loads (name + event index + source), `InstructionsLoaded` records, and the first edit/write index; `check_skills_loaded_before_first_edit` ([sdk_load_evidence.py:127](../../../../../tests/harness-instruction-following/sdk_load_evidence.py#L127)) requires each named skill to have loaded and loaded before the first edit, collecting all failures and naming the missing-or-late skill. `evidence_from_hook_records` is the shared builder used by both the live runner and the unit test. The auto-loaded-vs-Skill-tool distinction is handled by unioning both channels in `loaded_skill_names` and deriving a skill name from an `InstructionsLoaded` `skills/<name>/SKILL.md` path, so an always-loaded skill satisfies a required-skill assertion via either channel. **Never imports `claude-agent-sdk`.**
- [sdk_load_harness.py](../../../../../tests/harness-instruction-following/sdk_load_harness.py) — the live runner. `run_skill_load_session` ([sdk_load_harness.py:177](../../../../../tests/harness-instruction-following/sdk_load_harness.py#L177)) configures `ClaudeAgentOptions` with `plugins=[plugin_dir]` + `setting_sources=["project"]` so `Skill(...)` resolves, registers `PreToolUse(matcher="Skill")` (records skill name + event index), `PreToolUse(matcher="Edit|Write")` (records first edit index), and `InstructionsLoaded` (records `file_path`/`memory_type`/`load_reason` and contributes a skill load when the path names a SKILL.md), runs the supplied mock task, and returns `SkillLoadEvidence`. The `claude_agent_sdk` import is **deferred into the session function** ([sdk_load_harness.py:103](../../../../../tests/harness-instruction-following/sdk_load_harness.py#L103)), so importing the module is SDK-free. Gated on `RUN_LIVE_HARNESS=1` (raises if unset; bare run is a documented SKIP no-op), default `CLAUDE_MODEL=haiku` with override, plugin dir defaults to repo root (override via `CLAUDE_PLUGIN_DIR`). Downstream smokes (10–12) consume `run_skill_load_session`, not raw SDK calls.
- [test_sdk_load_evidence.py](../../../../../tests/harness-instruction-following/test_sdk_load_evidence.py) — CI-safe unit test on synthetic hook records (no live call): green case, always-loaded-via-`InstructionsLoaded` green case, and the two red cases — required skill never loaded ([test_sdk_load_evidence.py:88](../../../../../tests/harness-instruction-following/test_sdk_load_evidence.py#L88)) and skill loaded only after the first edit ([test_sdk_load_evidence.py:106](../../../../../tests/harness-instruction-following/test_sdk_load_evidence.py#L106)) — plus a no-edit case and an all-failures-collected case. A required skill that never loads is treated as a real loading-contract finding to escalate.

**`--include-hook-events` audit.** It is a real, documented flag — confirmed against CLI 2.1.183 where `claude -p --help` lists it as "Include all hook lifecycle events in the output stream (only works with --output-format=stream-json)". Not a no-op: it surfaces hook lifecycle events (e.g. the `UserPromptSubmit` autoloads). It does NOT make filesystem `PreToolUse` hooks fire under `claude -p` (#40506), so it gives no skill-load-by-name evidence — which is why the in-process SDK harness exists. Decision: **kept** the flag in both `claude-live-smoke.sh` and `orchestrator-live-smoke.sh` for debugging visibility, and documented what it does in both scripts, in [load-testing-research.md](../../../../../tests/harness-instruction-following/references/load-testing-research.md), and in the README. The smokes do not assert on the extra events.

**Verification (live-verified vs not):**

- CI-safe suite: `uv run --with pytest --with pyyaml python -m pytest tests/harness-instruction-following` → **34 passed** (was 27; +7 from `test_sdk_load_evidence.py`).
- SDK isolation, verified in this session with `claude-agent-sdk` NOT installed: `importlib.util.find_spec("claude_agent_sdk") is None`; importing `sdk_load_harness` leaves `claude_agent_sdk` out of `sys.modules` (deferred import); `run_skill_load_session` raises `RuntimeError` naming `RUN_LIVE_HARNESS` when the gate is unset; bare `python sdk_load_harness.py` prints SKIP and exits 0. The default `pytest` path neither imports `claude-agent-sdk` nor makes a model call.
- **NOT live-verified:** the live SDK path (`RUN_LIVE_HARNESS=1 uv run --with claude-agent-sdk python sdk_load_harness.py`) was not run — no credentials were authorized this turn. The success criterion "a live run records the skills loaded by name (at minimum `using-superra`)" remains to be confirmed on a credentialed machine. The hook callback shapes (`ClaudeAgentOptions`/`HookMatcher`/`InstructionsLoaded` payload fields) follow the mechanism recorded in the research doc; the field-access in the callbacks is defensive (`.get(...)` with fallbacks) so a minor SDK payload-shape difference degrades to `<unknown>` rather than crashing, but the exact `Skill` tool_input key and `InstructionsLoaded` payload keys should be confirmed against the installed SDK on the first live run.

## Revision Notes

The orchestrator ran the live SDK path against the user's subscription (`claude-agent-sdk` 0.x / Claude Code 2.1.183). The run invalidated two assumptions the original design and the research doc carried. Both are real findings, not test flakes.

1. **`InstructionsLoaded` is not a registrable `claude-agent-sdk` hook event.** The SDK `HookEvent` union is exactly: `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `UserPromptSubmit`, `Stop`, `SubagentStop`, `PreCompact`, `Notification`, `SubagentStart`, `PermissionRequest`. Registering an `InstructionsLoaded` hook is a silent no-op (the live run captured `instructions_loaded: 0`). Remove that hook and the `InstructionsLoaded`-derived skill-name channel.

2. **Always-loaded skills are preloaded via agent frontmatter `skills: [...]`, not loaded through the `Skill` tool.** `agents/implementer.md` and `agents/reviewer.md` both declare `skills: [superRA:using-superra, superRA:report-in-markdown]`. Preloaded skills do not emit a `Skill` tool_use, so the `Skill` PreToolUse hook cannot see them, and the init/system message lists only *available* skills, not per-agent preloaded ones. Cover them by the static frontmatter contract check + the live behavioral canary (task 10), not the hook.

What the live run confirmed works (keep):
- The `Skill` PreToolUse hook captures on-demand loads by name — proven: an explicit `Skill('superRA:using-superra')` was recorded as `('superRA:using-superra', 'skill_tool')`.
- The plugin resolves and the real `superRA:implementer` / `superRA:reviewer` agents are dispatchable (present in the SDK init `agents` list). The harness should dispatch the real agent so manifest loads actually fire.

Already fixed this turn (incorporated, do not redo): `plugins=` must be `[{"type": "local", "path": ...}]` (SdkPluginConfig), not a bare path string — the bare-string form raised `TypeError: string indices must be integers`. This fix is committed with these notes.

Re-implementation scope (preserve the CI-safe evidence model, gating, and unit-test scaffold; change only the live mechanism):
- Drop the `InstructionsLoaded` hook and its derived-name path from `sdk_load_evidence.py` / `sdk_load_harness.py`; stop unioning the two channels.
- Dispatch the real plugin agent in `run_skill_load_session` (via the Task/Agent tool or an `agents=` `AgentDefinition` carrying the role prompt + `skills:`), and **verify the `Skill` hook fires for tool use inside the dispatched subagent** — this is the linchpin for 11/12; probe it on the live path before claiming it.
- Add a CI-safe static checker that parses `agents/implementer.md` + `agents/reviewer.md` frontmatter and asserts both always-loaded skills are declared in `skills:` (green + red unit tests).
- Add the reusable behavioral-canary checker task 10 consumes (proof a preloaded skill's rule was applied); leave the fixtures to 10.
- Update [load-testing-research.md](../../../../../tests/harness-instruction-following/references/load-testing-research.md): correct the `InstructionsLoaded` claim and the always-loaded detection approach to match these findings.
