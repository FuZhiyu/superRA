# Agent Load-Testing: Mechanism Research and Design Decisions

Design input for the agent-loading-tests expansion (live verification that dispatched agents load every skill the Skill-Load Manifest claims, at every stage). Captures how the Claude Code and Codex harnesses expose — or fail to expose — skill/context loading, the cross-harness verification techniques the agent-eval literature converges on, and the resulting mechanism decision for this suite.

## The core problem

No harness emits a reliable "this instruction/skill was *followed*" event. Loading a skill body or a CLAUDE.md/AGENTS.md file into context is silent context assembly. So "did the agent load skill X" must be established either by a real load event the harness *does* expose, or — failing that — by an observable side effect only that skill produces.

The convergent recommendation across promptfoo, LangSmith/agentevals, OpenAI Evals, DeepEval, Inspect (UK AISI), and Anthropic's own "Demystifying evals for AI agents" is a **layered observable-proxy stack, graded deterministically**:

- **Canary token** — a high-entropy marker the skill body tells the agent to emit under a trigger; exact-match scan proves the skill body was *present* in context.
- **Context-only fact** — a value derivable only from the skill/file; proves it was *read*.
- **Structural rule** — output obeys a format/decision only that skill defines; proves it was *applied* (the thing we actually care about).
- **LLM-judge** — reserved for the irreducibly fuzzy residue, calibrated against human labels (watch verbosity/self-preference bias — a verbose answer that merely *looks* informed can fool a judge into "yes it loaded the skill").

Stage protocols become **verifiable predicates** (IFEval / SOPBench style): ordering = index check on the trace; gate-before-mutation = sequence check. Verify load-bearing invariants, not full prescribed paths (Anthropic explicitly warns that asserting exact tool-call sequences is too brittle).

CI tiering: deterministic static/fixture tests gate every commit; live runs stay gated behind an env flag, use the cheapest model for plumbing (not for reasoning assertions), bound cost/turns, and use repeated trials (pass@k for capability, pass^k for consistency) rather than a single binary assertion. Determinism comes from cassettes/mocks, not temperature 0.

## Claude Code

- **Stage and domain skills load *explicitly* via the `Skill` tool** (the manifest tells agents to load them), so they appear as `tool_use` blocks with `name: "Skill"` in `claude -p --output-format=stream-json` — directly assertable by name.
- **Always-loaded skills (`using-superra`, `report-in-markdown`) and CLAUDE.md auto-inject** — no `Skill` tool_use, so the stream alone does not prove them. The `InstructionsLoaded` hook event (fields `file_path`, `memory_type`, `load_reason`) is the CLAUDE.md/rules signal; always-loaded *skills* still need a canary or an in-process hook.
- **Subagent dispatch is observable** as a `Task`/`Agent` tool_use block (the tool was renamed across versions — match both) with `subagent_type`; nested activity links via `parent_tool_use_id`. Full child trajectory needs reading the child JSONL (`~/.claude/projects/<cwd>/<session>.jsonl`, subagents in separate files keyed by `agentId`/`agentType`) or promptfoo's `forward_subagent_text`.
- **Filesystem hooks are unreliable in headless `claude -p`**: `PreToolUse` hooks do not fire (#40506) and do not block before execution (#36071); `allowedTools:["*"]` skips the hook pipeline. **In-process Agent SDK hooks run reliably** — this is why the suite drives Claude through the SDK, not bare `claude -p`, for skill-load assertions.
- **`--include-hook-events` is a real, documented flag** — audited against CLI 2.1.183, where `claude -p --help` lists it as "Include all hook lifecycle events in the output stream (only works with --output-format=stream-json)". It is not a no-op: it surfaces hook lifecycle events (e.g. the `UserPromptSubmit` autoloads) into the stream. It does **not** make filesystem `PreToolUse` hooks fire under `claude -p` (#40506), so it gives no skill-load-by-name evidence — that is exactly why this suite drives the in-process Agent SDK for skill-load assertions. The existing `claude-*-smoke.sh` scripts keep the flag for debugging visibility; the smokes do not assert on the extra events.
- No event proves a *specific instruction was followed* — infer from side effects.

Sources: Claude Code headless & CLI reference (code.claude.com/docs/en/headless, /cli-reference); Agent SDK streaming-output, subagents, hooks (code.claude.com/docs/en/agent-sdk/*); hooks reference (code.claude.com/docs/en/hooks); Agent Skills best practices (platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices); Anthropic "Demystifying evals for AI agents"; issues anthropics/claude-code #40506, #36071, #35319, #33292, #24596; promptfoo claude-agent-sdk provider (`skill-used`/`not-skill-used`).

## Codex (`codex exec --json`)

- **JSONL event shape** (from the SDK source `sdk/typescript/src/events.ts`, `items.ts`): discriminator `type`; items `command_execution` (`command`, `aggregated_output`, `exit_code`), `file_change` (`changes[].path`/`kind`/`diff`), `agent_message` (`text`), `mcp_tool_call`, `web_search`. The published docs shipped stale field names (`item_type`/`assistant_message`) — actual is `type`/`agent_message` (#4776); no published JSON schema (#1673); `--json` is still experimental — pin to the codex version (we run 0.140.0).
- **Skill / AGENTS.md loading is NOT observable** — no `skill_loaded` event; injection is silent. File *reads* are observable only when done through a visible `command_execution` (e.g. `cat`/`sed`); internal context injection emits nothing.
- **Subagent dispatch is NOT observable in the JSONL** — no `spawn_agent` item type. The **`SubagentStart` hook (matcher = agent type)** is the deterministic out-of-band signal; have it write a sentinel.
- **Hooks are the best deterministic channel**: events incl. `SessionStart`, `PreToolUse`/`PostToolUse`, `SubagentStart`/`SubagentStop`, `Stop`; payload on stdin carries `hook_event_name`, `transcript_path`, `model`. A hook is your own executable, so it can append a log / touch a sentinel for a model-independent assertion. `--model` is the only reliable record of which model ran (usage omits it, #14736). `--output-schema` + `--output-last-message` force checkable output.

Sources: developers.openai.com/codex (noninteractive, cli/reference, skills, agents-md, hooks, subagents, app-server); openai/codex repo (events.ts, items.ts, issues #4776, #1673, #14736); OpenAI Codex cookbook "building consistent workflows".

## Mechanism decision for this suite

Chosen: **Claude via the Python `claude-agent-sdk` with in-process hooks; Codex via canary side-effects + a `SubagentStart` hook.**

- **Claude side** — drive the SDK with a `PreToolUse(matcher="Skill")` hook that records every skill loaded by name (and its order relative to edits) and an `InstructionsLoaded` hook for CLAUDE.md/rules. This yields real skill-load-by-name assertions across stages and domains, reliably in headless mode (unlike filesystem hooks under `claude -p`). The SDK session must be configured with the superRA plugin/skills dir so `Skill(...)` resolves.
- **Codex side** — skill-load and subagent-dispatch are unobservable in JSONL, so use the canary/side-effect proxy: the fixture's task instructs the agent to perform a skill-unique observable action (a prescribed command, a sentinel in the artifact) that is only producible if the skill body was loaded; and a `SubagentStart` hook writes agent-type sentinels for orchestrator dispatch.
- **Cross-harness backbone** — canary + structural-rule proxies work identically on both and are the fallback wherever a direct load event is unavailable.
- **A failing load assertion is a real finding, not a test bug.** If `report-in-markdown` (or any claimed always-loaded skill) never loads, that is a gap in the loading contract to escalate, not something to weaken the test around.
