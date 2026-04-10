---
name: implementer-protocol
description: >
  Load the implementer behavioral protocol for direct-mode execution. Use when
  the main agent implements work itself instead of dispatching an implementer
  subagent. Provides the same execution discipline, self-review, escalation
  protocol, and report format that the `implementer` agent uses.
---

# Implementer Protocol (Direct Mode)

Find and read the `implementer` agent definition file (`agents/implementer.md` in the plugin directory — use Glob `**/agents/implementer.md` if needed) and follow the protocol within. This is the same protocol the `implementer` agent type uses when dispatched as a subagent.

After loading, continue with your task using the skill and domain reference appropriate to your current stage.
