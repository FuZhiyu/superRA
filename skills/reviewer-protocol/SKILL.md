---
name: reviewer-protocol
description: >
  Use when the main agent is reviewing analysis work in-session without
  dispatching a reviewer subagent — e.g., ad-hoc code review mid-session,
  no reviewer subagent available, user asked you to review directly,
  a single-commit sanity check, or a quick second opinion on a change
  you want to audit before moving on. Triggers include "review this
  yourself", "what do you think of this commit", "sanity-check this
  change", "look at what the implementer did", or an ad-hoc diff review
  outside the formal two-stage execution-workflow loop. Canonical
  direct-mode counterpart to the `reviewer` agent type — loads the
  same severity definitions and verdict protocol the dispatched agent
  uses. Do not use for subagent dispatch; use the `reviewer` agent type
  instead.
---

# Reviewer Protocol (Direct Mode)

`Read` the file `agents/reviewer.md` at the plugin base directory that was announced when this skill loaded, and follow the protocol within. That file is the canonical source for the reviewer's discipline — the before-you-start load order, the read-code-first rule, the CRITICAL/MAJOR/MINOR severity definitions, the APPROVE/REVISE verdict protocol, the unified stage handoff with first-review and re-review sub-protocols, the pre-commit self-check, and the report format. Do not duplicate or paraphrase it.

After reading, continue with your domain-specific review using the skill and domain reference appropriate to your current stage.
