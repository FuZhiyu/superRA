---
title: Wire and Verify Claude Code Enforcement
status: not-started
depends_on:
  - 02-enforcement-hook
---

## Objective

Enable the shared model-selection gate on Claude Code's `PreToolUse(Agent)` path and verify that it blocks an inherited generic model before any subagent starts while allowing an explicit concrete selection.

- Register the shared hook under an `Agent` matcher in the Claude hook manifest without changing unrelated lifecycle hooks.
- Extend Claude-only manifest and hook tests to protect the matcher, command, and Claude-specific contract.
- Run a realistic Claude CLI or Agent SDK session that captures the pre-dispatch payload and proves a missing or `inherit` model is denied and retried, while a concrete model reaches `SubagentStart`.
- Record any documented headless-CLI limitation precisely; synthetic tests may supplement but not replace one realistic harness verification of the changed path.
- Update only Claude-specific hook documentation where the supported behavior or troubleshooting surface changes. Leave shared cross-harness contract tests and documentation to `05-cross-harness-convergence`.

## Planner Guidance

Claude's documented `SubagentStart` payload omits the original Agent arguments and cannot block creation. The existing live harness notes warn that filesystem `PreToolUse` behavior differs under some `claude -p` paths; prefer the Agent SDK surface when necessary and state what the live run actually proves.

## Results

(empty)
