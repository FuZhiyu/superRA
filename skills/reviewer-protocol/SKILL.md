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

`Read` the file `agents/reviewer.md` at the plugin base directory that was announced when this skill loaded, and follow the protocol within. That file is the canonical source for the reviewer's discipline — the before-you-start load order, the read-code-first rule, the CRITICAL/MAJOR/MINOR severity definitions, the APPROVE/REVISE verdict protocol, the unified stage handoff with first-review and re-review sub-protocols, the pre-commit self-check, and the report format. Do not duplicate or paraphrase it.

After reading, continue with your domain-specific review using the skill and domain reference appropriate to your current stage.
