---
title: "Positive 'approved' semantics fixes across integration surfaces"
status: approved
depends_on:
  - 01-core-stage-redesign
tags: []
created: 2026-06-18
---

## Objective

Finish the "approved = review-passed / ready-for-integration (reversible)" alignment in the surfaces task 01 does not own, using positive instructions only.

From the approval audit, the canonical definitions are already correct (`task-file-contract.md:22` "validity marker"; `agent-orchestration` status table "review passed"; reviewer specs own `approved → revise`). The remaining drift is scoping framing that reads as "approved = out of bounds":

- **`refactor-and-integrate/SKILL.md:56`** — "operate only on tasks whose `status` is not `approved`…" Align positively to name the in-scope set: reopened/changed tasks plus the branch-wide surviving-diff sweep that can reopen an approved task when it surfaces an unjustified hunk (consistent with `agents/reviewer.md:111` / `direct-mode-reviewer.md:115`, which already grant that reopen).
- Sweep the remaining "approv" occurrences flagged in the audit for any other line that frames approved as final/locked/excluded; fix positively or leave correct ones alone. The `:242` and `:46` lines in `superintegrate` are owned by task 01 — do not touch them here (avoid file collision).

Hard constraint: **add no negative instructions** ("approval does not mean…"). If a line currently misleads, rewrite it to state the correct positive scope, or delete it if it only restates a default.

**Success:** `refactor-and-integrate/SKILL.md:56` reads as a positive in-scope statement aligned with the reviewer reopen carve-out; an audit grep shows no surviving line that frames `approved` as final/untouchable; no negative "approved" instruction was introduced anywhere.

## Planner Guidance

Run `grep -rn "approv" skills/ agents/ --include="*.md"` and re-walk the audit classification before editing; most occurrences are correct status mechanics and must be left alone. This task is small and mostly verification.

## Results

Rewrote the one exclusionary scoping line at [refactor-and-integrate/SKILL.md](../../../../skills/refactor-and-integrate/SKILL.md) positively (name the in-scope set, including any `approved` task the surviving-diff sweep reopens); a 99-occurrence `approv` audit confirmed no other negative framing of `approved`. Matured narrative at the [subtree root](../task.md).
