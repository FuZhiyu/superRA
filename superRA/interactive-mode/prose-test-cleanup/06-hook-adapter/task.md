---
title: "Replace Hook-Adapter Prose Oracles"
status: implemented
depends_on:  []
---

## Objective

Replace Codex hook tests that assert exact Stop reasons, invalid-status wording, or phrase-based plan detection with adapter JSON shape, block decisions, structured proposed-plan/permission-mode signals, and structured status identities. Success: hook behavior remains covered without prose heuristics or diagnostic wording oracles.

## Planner Guidance

Own tests/hooks/test-codex-hooks.sh and codex-plan-stop adapter surfaces. Coordinate any required structured task-hook contract with 03-task-tree-core; do not duplicate core changes.

## Results

- Replaced the Codex Stop hook's Markdown-heading heuristic with the structured
  `<proposed_plan>` tag gated by `permission_mode: plan`; continuation output
  remains the adapter's `decision: block` JSON shape, while the human reason is
  presentation-only
  ([codex-plan-stop:15-54](../../../../hooks/codex-plan-stop#L15-L54)).
- Replaced Stop-reason assertions with JSON shape and block-decision checks.
  Plan fixtures now use the structured tag and permission-mode identity, and a
  plan-mode Markdown heading without the tag no longer triggers the hook
  ([test-codex-hooks.sh:139-218](../../../../tests/hooks/test-codex-hooks.sh#L139-L218),
  [test-codex-hooks.sh:309-380](../../../../tests/hooks/test-codex-hooks.sh#L309-L380)).
- Replaced the task-hook invalid-status wording assertion with the adapter's
  PostToolUse JSON shape plus the core task check's structured
  `status.invalid` finding identity: `subject=status`,
  `actual=invalid-status`, `path=01-child`, and no related nodes
  ([test-codex-hooks.sh:249-293](../../../../tests/hooks/test-codex-hooks.sh#L249-L293)).
- Red evidence: the revised focused suite passed 13 cases and failed only the
  Markdown-heading-without-tag case against the old heuristic. Green evidence:
  the focused suite passed all 14 cases. Shell syntax and the harness
  compatibility suite passed; the live Codex E2E passed both UserPromptSubmit
  hook evidence and task-hook PostToolUse mutation evidence. A scoped audit
  found no remaining Stop-reason or invalid-status wording assertion in the
  owned test.
