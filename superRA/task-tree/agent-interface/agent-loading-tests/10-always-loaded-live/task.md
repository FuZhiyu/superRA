---
title: "Always-Loaded Skills Live Coverage"
status: implemented
depends_on:
  - 08-claude-sdk-load-harness
  - 09-codex-canary-and-dispatch-hook
tags: []
created: 2026-06-19
---

## Objective

Verify live, in both harnesses, that **both** always-loaded skills are in the dispatched role's context before any task-file or code edit: `using-superra` **and** `report-in-markdown` (contract LC001 in [load_contract.json](../../../../../tests/harness-instruction-following/load_contract.json)), and regression-guard that contract.

What is already established (do not re-litigate; build the regression guard): in **Claude**, both skills are **autoloaded** via the agents' frontmatter `skills: [...]` — orchestrator-confirmed live, a dispatched `superRA:implementer` recited `report-in-markdown`'s file-citation rule with zero `Skill`-tool loads. In **Codex** there is no autoload, so the [role-spec-always-load](../../role-spec-always-load/task.md) body instruction is what loads them. This task turns those one-off confirmations into committed checks.

Deliverables:

- A fixture role dispatch (reuse `bundle-two-tasks` shape) and assertions that, for each harness, evidence both always-loaded skills:
  - **Claude** — autoloaded skills are invisible to the `Skill` hook by construction (zero `Skill`-tool loads is the expected, correct signal — not a failure). Evidence them two ways: (1) the 08 **static frontmatter contract** check (both `agents/implementer.md` and `agents/reviewer.md` declare both skills), and (2) a **live discriminating canary** via the 08 harness dispatching the real `superRA:implementer`. The canary must use a rule the base model would NOT follow unprompted — the bare file-link-with-anchor format is too close to a model default to discriminate. The orchestrator's working probe was an **introspection prompt**: ask the dispatched implementer to state its markdown file-citation rule *without loading any skill or reading any file*; a context-grounded recital of `report-in-markdown`'s rule (with zero `Skill` loads) proves autoload. Prefer that, or pick a more arbitrary skill-unique rule.
  - **Codex** via the 09 canary convention — a fixture output value producible only by following a `report-in-markdown` rule and a `using-superra` behavior; this is what exercises the role-spec body-load path that substitutes for Claude's autoload.
- The discriminating canary asserts the skill's rule reached context; the static check asserts the declared contract.

Success criteria: both always-loaded skills are evidenced loaded in both harnesses on the dispatched role turn; the red case (a required always-loaded skill not evidenced) fails.

### Constraints

- Manual-only; consume the 08/09 harnesses, do not re-implement evidence capture.
- **A failing result is a real finding, not a test bug.** If `report-in-markdown` does not load, record it in `## Results` as a loading-contract gap and escalate to the orchestrator (it likely needs a hook/manifest fix), rather than relaxing the assertion.

## Planner Guidance

Design the discriminating canary first — a rule only `report-in-markdown` defines that the base model would not produce unprompted; the introspection probe above is the proven approach. A bare presence token or a model-default format is not evidence.

The live SDK dispatch is mildly nondeterministic (it leans on the top-level model to issue the Task dispatch): use the cheapest model that dispatches reliably (sonnet did; haiku was flaky) and assert across a small retry / pass@k window, not a single shot. The deterministic backbone is the static frontmatter contract; the live canary corroborates. A genuine failure (skill's rule absent from a reliable dispatch) is a real loading-contract finding to escalate, not an assertion to relax.

## Results

Both always-loaded skills (`using-superra`, `report-in-markdown`, LC001) now have committed regression checks in both harnesses, built on the 08/09 harnesses (no evidence-capture re-implementation). All 78 CI-safe harness tests pass; both live entry points are documented no-ops without `RUN_LIVE_HARNESS=1`. I could not run the live model path (no network) — it is built CI-safe-verifiable and handed back with the exact commands below.

### Claude — autoload, evidenced two ways

Claude autoloads both skills via the agents' frontmatter `skills: [...]`, so an autoloaded skill is invisible to the `Skill` hook: zero `Skill`-tool loads is the correct signal, not a failure (per the orchestrator's live confirmation).

1. **Deterministic backbone — static frontmatter contract.** Reuses 08's `check_always_loaded_frontmatter` via [always_loaded_live.py::check_claude_always_loaded_static](../../../../../tests/harness-instruction-following/always_loaded_live.py#L189): both `agents/implementer.md` and `agents/reviewer.md` must declare both skills. Green against the real role specs; red on a missing skill ([test_always_loaded_live.py](../../../../../tests/harness-instruction-following/test_always_loaded_live.py#L209)).
2. **Live discriminating introspection canary.** [always_loaded_live.py](../../../../../tests/harness-instruction-following/always_loaded_live.py) dispatches the real `superRA:implementer` (via 08's `run_skill_load_session`, extended to capture assistant text) with an introspection prompt asking it to state its markdown file-citation rule *without loading any skill or reading any file*. The canary passes only when both: (a) the answer recites `report-in-markdown`'s **discriminating** rule — links *with line anchors* AND an explicit "not/never backticks" contrast (the bare link format is too close to a model default, so it is rejected); and (b) the always-loaded skill recorded **zero** on-demand `Skill` loads (proving autoload, not on-demand load). Evaluator: [evaluate_introspection_canary](../../../../../tests/harness-instruction-following/always_loaded_live.py#L107).

The introspection evaluator's green/red logic is exercised in CI on synthetic answers (the green case sourced through the same tool-result capture path the live harness uses): green (rule recited, zero loads); red NO_RULE; red backtick-default; red anchor-without-contrast; red stray-negation-not-governing-backticks; red no-dispatch-no-captured-answer; red rule-recited-but-loaded-on-demand (autoload violation); red both-failures-together.

### Codex — no autoload, role-spec body-load path

Codex has no autoload, so the role-spec body instruction is what loads the always-loaded skills. Uses 09's canary convention: per-skill `CanarySpec` rows whose skill-unique tokens are only producible if the skill body loaded ([always_loaded_live.py CODEX_ALWAYS_LOADED_CANARIES](../../../../../tests/harness-instruction-following/always_loaded_live.py#L222)):

- `report-in-markdown` → runs its own `check_markdown.py` self-diagnose CLI (script named only in the skill body; confirmed present at [skills/report-in-markdown/scripts/check_markdown.py](../../../../../skills/report-in-markdown/scripts/check_markdown.py)).
- `using-superra` → the `superra task read` wrapper-read convention it prescribes.

Each is checked in a `command_execution` command or at an artifact field via 09's `evaluate_canary`. Fixture: [tests/fixtures/task-trees/always-loaded-canary](../../../../../tests/fixtures/task-trees/always-loaded-canary); live smoke [always-loaded-codex-smoke.sh](../../../../../tests/harness-instruction-following/always-loaded-codex-smoke.sh) → [check_always_loaded_smoke.py](../../../../../tests/harness-instruction-following/check_always_loaded_smoke.py). CI green/red cases plus a fixture-sanity test (the committed expected artifact satisfies both canaries) in [test_always_loaded_live.py](../../../../../tests/harness-instruction-following/test_always_loaded_live.py).

### Nondeterminism handling

The live Claude introspection canary defaults to `CLAUDE_MODEL=sonnet` (sonnet dispatched reliably; haiku was flaky) and runs a pass@k retry window (`attempts`, default 3), returning the first passing report. A reliable-dispatch failure — rule absent, or a non-zero always-loaded `Skill` load — is a real LC001 finding to escalate, not an assertion to relax.

### Live commands (handed to the orchestrator — not runnable here, no network)

```bash
# Claude introspection canary:
RUN_LIVE_HARNESS=1 uv run --with claude-agent-sdk \
  python tests/harness-instruction-following/always_loaded_live.py
# Codex body-load canary (set CODEX_MODEL or use the CLI default):
RUN_LIVE_HARNESS=1 bash tests/harness-instruction-following/always-loaded-codex-smoke.sh
```

### Verification

`uv run --with pytest --with pyyaml python -m pytest tests/harness-instruction-following -q` → 78 passed. Both gated entry points print `SKIP` and exit 0 without the gate. README markdown self-diagnose clean.

### Note on the 08 harness extension

To capture the introspection *answer* (which 08's `run_skill_load_session` previously dropped — it only recorded skill loads), I added an additive `capture_text` opt-in to 08's harness/evidence (`SkillLoadEvidence.assistant_texts`). Capture is **isolated to the dispatched subagent's answer**: it reads the content of the Agent/Task `ToolResultBlock` on the message stream — not all `AssistantMessage` text — via [sdk_load_evidence.extract_agent_answers](../../../../../tests/harness-instruction-following/sdk_load_evidence.py#L194), which tracks the tool-use ids of Agent/Task dispatch calls and returns only their tool-result text. Subagent text does not stream as parented `AssistantMessage`s by default (the orchestrator live-probed this; a `parent_tool_use_id` capture came back empty), and the top-level SDK driver is not a role agent and does not autoload `report-in-markdown`, so capturing all assistant text would let a top-level recital pass the canary. The tool-result capture isolates the implementer's answer and **fails closed** when no dispatch occurs (no Agent tool-result → empty answer → canary fails), making the canary a real regression guard on implementer autoload. This consumes the harness rather than re-implementing the `Skill`-hook evidence capture; default callers (the ordering smokes) are unaffected (`capture_text=False`). The capture helper is duck-typed and SDK-free, so the CI-safe unit tests drive it on synthetic Agent/Task tool-result blocks (green case sourced through `extract_agent_answers`; isolation + "no dispatch → no captured answer" red cases).

## Review Notes

1. **MAJOR** — [sdk_load_harness.py:203-206](../../../../../tests/harness-instruction-following/sdk_load_harness.py#L203-L206): `capture_text` accumulates **every** `AssistantMessage` text block in the session, without distinguishing the dispatched subagent's text from the **top-level orchestrator model's** text. The introspection canary's whole validity rests on the answer coming from the *dispatched `superRA:implementer`* (whose frontmatter autoloads `report-in-markdown`), but the top-level SDK driver is not a role agent and does not autoload that skill. The dispatch prompt only instructs the top-level to "Dispatch … then stop," so if the top-level model recites the file-citation rule from general knowledge (or fails to dispatch and answers the introspection question directly), that recital is captured into `assistant_texts` and `evaluate_introspection_canary` passes — even though the implementer's autoload contract was not exercised. This defeats the task's regression-guard purpose: a future break in implementer autoload could still pass the live canary on a top-level recital. The capture should isolate subagent text (e.g. filter on the SDK `AssistantMessage.parent_tool_use_id` being non-`None`, the same subagent discriminator `_is_subagent_load` already relies on for the `Skill` hook), so only the dispatched agent's answer feeds the canary. Note the SDK is not installed in this sandbox, so confirm the exact attribution field on the first live run; the code comment at line 203-206 states the intent ("check the dispatched agent's *answer*") but the implementation captures all text.

   → orchestrator: accepted — the finding is valid and blocking; capture must isolate the dispatched implementer's answer. Corrected fix mechanism (orchestrator live-probed this session against the subscription): subagent text does **not** stream as parented `AssistantMessage`s by default — a `parent_tool_use_id`-non-`None` capture came back empty. The subagent's answer arrives as the **Agent/Task `ToolResultBlock`** content (capturable via `ToolResultBlock` on the message stream). Capture that instead: it is isolated to the dispatched subagent and fails closed (no answer captured → canary fails) when dispatch never occurs. Do not rely on `parent_tool_use_id`-AssistantMessage capture.
   → implemented: capture now reads only the Agent/Task `ToolResultBlock` content via the new SDK-free [extract_agent_answers](../../../../../tests/harness-instruction-following/sdk_load_evidence.py#L194) (tracks Agent/Task tool-use ids, returns matching tool-result text); the harness loop calls it instead of accumulating all `AssistantMessage` text ([sdk_load_harness.py:199-210](../../../../../tests/harness-instruction-following/sdk_load_harness.py#L199-L210)). Fails closed on no dispatch (returns `[]` → empty answer → canary fails). CI green case is now sourced through this same path and a "no dispatch → no captured answer" red case plus an isolation test were added ([test_always_loaded_live.py](../../../../../tests/harness-instruction-following/test_always_loaded_live.py)). SDK import stays deferred/off the CI path.

2. **MINOR** — [always_loaded_live.py:100-107](../../../../../tests/harness-instruction-following/always_loaded_live.py#L100-L107): the discriminating regex's second lookahead `(?=.*\b(?:not|never|...)\b.*\bback ?ticks?\b)` matches when *any* negation word and the word "backticks" both appear, however far apart and unrelated. An answer like "Do not use full URLs; cite the file in backticks and the line" (a wrong, model-default-style answer that happens to contain a stray negation plus "backticks" plus "anchor") would falsely pass. The committed test cases are all correct and the common model-default answer (backticks, no negation) is still rejected, so this is a low-likelihood over-match, but tightening the contrast clause to require the negation to govern "backticks" (e.g. a bounded gap, or `not\s+(?:\w+\s+){0,3}back ?ticks?`) would make the discrimination robust.

   → orchestrator: accepted — tighten the negation→backticks contrast to a bounded gap, and add a unit case for the stray-negation false-positive the reviewer described.
   → implemented: tightened the contrast lookahead so the negation must govern "backticks" within a bounded gap — `(?:\s+\w+){0,3}\s+back ?ticks?` ([always_loaded_live.py:100-110](../../../../../tests/harness-instruction-following/always_loaded_live.py#L100-L110)); added a stray-negation false-positive red case ("Do not use full URLs; cite the file path in backticks and the line anchor") that now fails ([test_always_loaded_live.py](../../../../../tests/harness-instruction-following/test_always_loaded_live.py)). Verified greens (incl. "instead of backticks", "not backtick-wrapped") still pass.
