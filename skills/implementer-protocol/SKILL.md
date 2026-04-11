---
name: implementer-protocol
description: >
  Utility (direct-mode alias for agents/implementer.md). Use when the main
  agent implements work in-session without dispatching a subagent. Loads
  the same stage-handoff matrix, report format, document discipline, and
  self-review checklist that the implementer agent uses — just inside the
  main session instead of a dispatched one. Do not load unless running in
  direct mode; for subagent dispatch, use the implementer agent type.
---

# Implementer Protocol (Direct Mode)

Find and read the `implementer` agent definition file (`agents/implementer.md` in the plugin directory — use Glob `**/agents/implementer.md` if needed) and follow the protocol within. This is the same protocol the `implementer` agent type uses when dispatched as a subagent.

After loading, continue with your task using the skill and domain reference appropriate to your current stage.
