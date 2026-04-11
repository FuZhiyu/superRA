---
name: implementer-protocol
description: >
  Use when the main agent is implementing analysis work in-session without
  dispatching a subagent — e.g., a single-file task, no subagent
  infrastructure available, the user has asked you to implement directly,
  or a full dispatch would be overkill; when resuming implementation
  mid-session after a subagent returned BLOCKED; when a trivial change
  does not warrant the dispatch overhead. Triggers include "just
  implement this directly", "do this yourself", "no need to dispatch",
  "run task N in this session", or a small task the orchestrator wants
  to handle inline. Canonical direct-mode counterpart to the `implementer`
  agent type — loads the same execution discipline the dispatched agent
  uses. Do not use for subagent dispatch; use the `implementer` agent
  type instead.
---

# Implementer Protocol (Direct Mode)

`Read` the file `agents/implementer.md` at the plugin base directory that was announced when this skill loaded, and follow the protocol within. That file is the canonical source for the implementer's execution discipline — the before-you-start load order, the data-first execution protocol, the self-review gate, the unified stage handoff, the pre-commit self-check, the report format, and the escalation rules. Do not duplicate or paraphrase it.

After reading, continue with your task using the skill and domain reference appropriate to your current stage.
