---
name: reviewer-protocol
description: >
  Utility (direct-mode alias for agents/reviewer.md). Use when the main
  agent reviews work in-session without dispatching a subagent. Loads the
  same severity levels (CRITICAL/MAJOR/MINOR), APPROVE/REVISE verdict
  protocol, stage-specific handoff matrix, and report format that the
  reviewer agent uses — just inside the main session instead of a
  dispatched one. Do not load unless running in direct mode; for subagent
  dispatch, use the reviewer agent type.
---

# Reviewer Protocol (Direct Mode)

Find and read the `reviewer` agent definition file (`agents/reviewer.md` in the plugin directory — use Glob `**/agents/reviewer.md` if needed) and follow the protocol within. This is the same protocol the `reviewer` agent type uses when dispatched as a subagent.

After loading, continue with your domain-specific review using the skill and domain reference appropriate to your current stage.
