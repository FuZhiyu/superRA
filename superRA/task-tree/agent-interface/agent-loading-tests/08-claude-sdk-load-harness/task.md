---
title: "Claude Agent-SDK Skill-Load Harness"
status: implemented
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

The Claude skill-load harness is a CI-safe evidence/assertion layer plus a manual-only live runner, split so `claude-agent-sdk` is reachable only on the live path. This revision incorporated the orchestrator's live-run findings (see `## Revision Notes`): the `InstructionsLoaded` hook and its derived skill-name channel are removed (it is not a registrable SDK `HookEvent`), the live runner now **dispatches the real plugin role agent** so manifest loads fire, and always-loaded skills are covered by a static frontmatter contract plus a reusable behavioral canary rather than the `Skill` hook.

**Two separate channels (kept distinct, not unioned):**

- **On-demand skills** (stage/domain manifest loads) load through the `Skill` tool → recorded by the `PreToolUse(matcher="Skill")` hook by name.
- **Always-loaded skills** (`superRA:using-superra`, `superRA:report-in-markdown`) preload via agent frontmatter `skills: [...]`, emit no `Skill` tool_use, and are not in the SDK init's per-agent list → covered by the static frontmatter contract + the live behavioral canary.

**Modules (all under `tests/harness-instruction-following/`):**

- [sdk_load_evidence.py](../../../../../tests/harness-instruction-following/sdk_load_evidence.py) — CI-safe evidence model + assertions + contract + canary; **never imports `claude-agent-sdk`**.
  - `SkillLoadEvidence` carries on-demand `Skill`-tool loads (name + event index + source) and the first edit/write index. `check_skills_loaded_before_first_edit` ([sdk_load_evidence.py:116](../../../../../tests/harness-instruction-following/sdk_load_evidence.py#L116)) requires each named skill to have loaded and loaded before the first edit, collecting all failures and naming the missing-or-late skill. `evidence_from_hook_records` is the shared builder for the live runner and the unit test. The `InstructionsLoaded` record type and the two-channel union are gone.
  - `check_always_loaded_frontmatter` ([sdk_load_evidence.py:234](../../../../../tests/harness-instruction-following/sdk_load_evidence.py#L234)) is the **static CI-safe contract**: `parse_frontmatter_skills` (stdlib-only, no PyYAML; handles inline and block list forms) parses each role spec's frontmatter and the checker asserts both `agents/implementer.md` and `agents/reviewer.md` declare both `ALWAYS_LOADED_SKILLS`. A missing declaration is a regressed preloaded contract to escalate.
  - `BehavioralCanarySpec` + `check_behavioral_canary` ([sdk_load_evidence.py:298](../../../../../tests/harness-instruction-following/sdk_load_evidence.py#L298)) is the **reusable live checker task 10 consumes**: it proves a preloaded skill's structural rule shaped the output (output matches a regex only that skill's body defines). Task 08 owns the checker; task 10 owns the `BehavioralCanarySpec` rows and the prompts that trigger them.
- [sdk_load_harness.py](../../../../../tests/harness-instruction-following/sdk_load_harness.py) — the live runner. `run_skill_load_session` ([sdk_load_harness.py:208](../../../../../tests/harness-instruction-following/sdk_load_harness.py#L208)) configures `ClaudeAgentOptions` with `plugins=[{"type": "local", "path": ...}]` + `setting_sources=["project"]` so `Skill(...)` resolves and the role agents are dispatchable, registers `PreToolUse(matcher="Skill")` and `PreToolUse(matcher="Edit|Write")` only (no `InstructionsLoaded`), and **dispatches the real `superRA:implementer` agent** (`agent_type` param, default `DEFAULT_AGENT_TYPE`) via the Task/Agent tool rather than running the prompt at the top level. The `Skill` hook tags each load's `source` as `subagent_skill_tool` vs `skill_tool` via a best-effort subagent-context probe ([sdk_load_harness.py:118](../../../../../tests/harness-instruction-following/sdk_load_harness.py#L118)) so the orchestrator can confirm, on the live path, that loads inside the dispatched subagent are captured — the linchpin for 11/12. The `claude_agent_sdk` import is **deferred into the session function** ([sdk_load_harness.py:151](../../../../../tests/harness-instruction-following/sdk_load_harness.py#L151)). Gated on `RUN_LIVE_HARNESS=1` (raises if unset; bare run is a documented SKIP no-op), default `CLAUDE_MODEL=haiku`, plugin dir defaults to repo root (`CLAUDE_PLUGIN_DIR` override). Downstream smokes (10–12) consume `run_skill_load_session`, not raw SDK calls.
- [test_sdk_load_evidence.py](../../../../../tests/harness-instruction-following/test_sdk_load_evidence.py) — CI-safe unit test (no live call): on-demand ordering green + the two red cases (required skill never loaded; skill loaded only after the first edit) + no-edit + all-failures-collected; frontmatter parser (inline/block/none); **frontmatter contract green against the real role specs** + red (missing skill, missing file); **behavioral canary green + red**.

**`--include-hook-events` audit (carried over, unchanged).** Real, documented flag (CLI 2.1.183: "Include all hook lifecycle events in the output stream (only works with --output-format=stream-json)"). Not a no-op — surfaces hook lifecycle events — but does NOT make filesystem `PreToolUse` hooks fire under `claude -p` (#40506), so no skill-load-by-name evidence (why the SDK harness exists). **Kept** in both `claude-live-smoke.sh` and `orchestrator-live-smoke.sh` for debugging visibility, documented in both scripts, the research doc, and the README; the smokes do not assert on the extra events.

**Verification (CI-safe, run this session):**

- CI-safe suite: `uv run --with pytest --with pyyaml python -m pytest tests/harness-instruction-following` → **60 passed**.
- SDK isolation, verified with `claude-agent-sdk` NOT installed: `importlib.util.find_spec("claude_agent_sdk") is None`; importing `sdk_load_harness` leaves `claude_agent_sdk` out of `sys.modules` (deferred import); `run_skill_load_session` raises `RuntimeError` naming `RUN_LIVE_HARNESS` when the gate is unset; bare `python sdk_load_harness.py` prints SKIP and exits 0. The default `pytest` path neither imports `claude-agent-sdk` nor makes a model call.
- Static frontmatter contract passes against the real `agents/implementer.md` and `agents/reviewer.md` (both declare both always-loaded skills) — the green test is wired to the live files, not a fixture.

**NOT live-verified (hand back to the orchestrator — no network/subscription in this sandbox):** the live SDK path was not run. Run on a credentialed machine:

```bash
RUN_LIVE_HARNESS=1 uv run --with claude-agent-sdk \
  python tests/harness-instruction-following/sdk_load_harness.py
```

Expected: it dispatches `superRA:implementer`, prints the per-load source list, and records at least one on-demand skill the agent loaded via the `Skill` tool. **Two things to confirm on that run, both linchpins for 11/12:** (1) at least one load is tagged `subagent_skill_tool` — i.e. the `Skill` hook fires for tool use *inside* the dispatched subagent (the standalone smoke prints a `WARN` if none is, so escalate rather than build 11/12 on an unconfirmed seam); (2) the subagent-context probe in `_is_subagent_context` ([sdk_load_harness.py:118](../../../../../tests/harness-instruction-following/sdk_load_harness.py#L118)) reads the actual hook-context shape — its key names (`parent_tool_use_id` / `agent_type` / …) are best-effort and should be pinned against the installed SDK on the first live run; the `Skill` tool_input key for the skill name (`_skill_name_from_tool_input`) should likewise be confirmed (it degrades to `<unknown>` rather than crashing).

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
