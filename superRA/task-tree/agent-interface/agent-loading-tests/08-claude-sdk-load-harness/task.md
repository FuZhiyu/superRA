---
title: "Claude Agent-SDK Skill-Load Harness"
status: approved
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
- [sdk_load_harness.py](../../../../../tests/harness-instruction-following/sdk_load_harness.py) — the live runner. `run_skill_load_session` ([sdk_load_harness.py:208](../../../../../tests/harness-instruction-following/sdk_load_harness.py#L208)) configures `ClaudeAgentOptions` with `plugins=[{"type": "local", "path": ...}]` + `setting_sources=["project"]` so `Skill(...)` resolves and the role agents are dispatchable, registers `PreToolUse(matcher="Skill")` and `PreToolUse(matcher="Edit|Write")` only (no `InstructionsLoaded`), and **dispatches the real `superRA:implementer` agent** (`agent_type` param, default `DEFAULT_AGENT_TYPE`) via the Task/Agent tool rather than running the prompt at the top level. The `Skill` hook tags each load's `source` as `subagent_skill_tool` vs `skill_tool` via `_is_subagent_load(input_data)` ([sdk_load_harness.py:118](../../../../../tests/harness-instruction-following/sdk_load_harness.py#L118)), which keys off the hook `input_data`'s `agent_id`/`agent_type` (the SDK `_SubagentContextMixin`) — live-confirmed to correctly tag loads inside the dispatched subagent, the linchpin for 11/12. The `claude_agent_sdk` import is **deferred into the session function** ([sdk_load_harness.py:151](../../../../../tests/harness-instruction-following/sdk_load_harness.py#L151)). Gated on `RUN_LIVE_HARNESS=1` (raises if unset; bare run is a documented SKIP no-op), default `CLAUDE_MODEL=haiku`, plugin dir defaults to repo root (`CLAUDE_PLUGIN_DIR` override). Downstream smokes (10–12) consume `run_skill_load_session`, not raw SDK calls.
- [test_sdk_load_evidence.py](../../../../../tests/harness-instruction-following/test_sdk_load_evidence.py) — CI-safe unit test (no live call): on-demand ordering green + the two red cases (required skill never loaded; skill loaded only after the first edit) + no-edit + all-failures-collected; frontmatter parser (inline/block/none); **frontmatter contract green against the real role specs** + red (missing skill, missing file); **behavioral canary green + red**.

**`--include-hook-events` audit (carried over, unchanged).** Real, documented flag (CLI 2.1.183: "Include all hook lifecycle events in the output stream (only works with --output-format=stream-json)"). Not a no-op — surfaces hook lifecycle events — but does NOT make filesystem `PreToolUse` hooks fire under `claude -p` (#40506), so no skill-load-by-name evidence (why the SDK harness exists). **Kept** in both `claude-live-smoke.sh` and `orchestrator-live-smoke.sh` for debugging visibility, documented in both scripts, the research doc, and the README; the smokes do not assert on the extra events.

**Verification (CI-safe, run this session):**

- CI-safe suite: `uv run --with pytest --with pyyaml python -m pytest tests/harness-instruction-following` → **60 passed**.
- SDK isolation, verified with `claude-agent-sdk` NOT installed: `importlib.util.find_spec("claude_agent_sdk") is None`; importing `sdk_load_harness` leaves `claude_agent_sdk` out of `sys.modules` (deferred import); `run_skill_load_session` raises `RuntimeError` naming `RUN_LIVE_HARNESS` when the gate is unset; bare `python sdk_load_harness.py` prints SKIP and exits 0. The default `pytest` path neither imports `claude-agent-sdk` nor makes a model call.
- Static frontmatter contract passes against the real `agents/implementer.md` and `agents/reviewer.md` (both declare both always-loaded skills) — the green test is wired to the live files, not a fixture.

**Live-verified (orchestrator ran the live SDK path against the subscription, haiku, `claude-agent-sdk` 0.x / Claude Code 2.1.183):**

```bash
RUN_LIVE_HARNESS=1 uv run --with claude-agent-sdk \
  python tests/harness-instruction-following/sdk_load_harness.py
```

- **Both 11/12 linchpins confirmed.** The harness dispatches the real `superRA:implementer` (full message stream showed `Agent subagent_type=superRA:implementer`), the dispatched implementer loads `superRA:using-superra` via the `Skill` tool *inside the subagent*, and the `Skill` PreToolUse hook fires for that subagent tool use and captures it by name, before the first edit. Two consecutive runs printed `superRA:using-superra [event 0, subagent_skill_tool]`, `first edit index: 1`, OK.
- **Subagent attribution is in the hook `input_data`, not the `context` arg.** The `context` arg is `{'signal': None}`; the subagent fields (`agent_id`, `agent_type='superRA:implementer'`) live on the hook `input_data` (the SDK `_SubagentContextMixin`; `agent_id` is documented as present only inside a Task-spawned subagent). The original `_is_subagent_context(context)` checked the wrong argument and mis-tagged subagent loads as top-level; the orchestrator fixed it to `_is_subagent_load(input_data)` keying off `agent_id`/`agent_type`, re-ran live, and confirmed correct `subagent_skill_tool` tagging. The `Skill` tool_input key for the name is `skill` (confirmed live).
- **Known flakiness (manual-smoke caveat, relevant to 10/11/12):** the standalone smoke leans on a weak top-level model (haiku) to both issue the Task dispatch and load a skill via the `Skill` tool. Across four live runs the captured load varied (`task-tree`; `using-superra`×3; one run captured nothing). The mechanism is sound, but the live smokes are not single-shot deterministic — 10/11/12 should assert across retries / pass@k or use strongly skill-triggering fixture wording, not a single-run equality. The always-loaded contract itself is covered deterministically by the CI-safe static frontmatter check; the live observation of `using-superra` via the hook is corroborating, not the sole evidence.
