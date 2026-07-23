---
title: "Econ-data-analysis: reviewer read-first default and prefer-visualization"
status: not-started
depends_on: []
---

## Objective

Fold two efficiency refinements into `skills/econ-data-analysis/SKILL.md`, as domain discipline (the generic role specs stay adversarial and unchanged):

1. **Reviewer read-first / targeted-effort default.** In data work, verification assesses the committed diagnostics, row-count logs, and output files first; re-execution is targeted to a *suspected discrepancy* (implausible magnitude, missing count, number disagreeing with `## Results`), not routine. When iterating or fixing, re-run only the changed step and its downstream dependents — unaffected upstream outputs stand as committed.
2. **Prefer visualization in results.** Present headline findings visually by default (distribution, relationship, or time path); reserve number-only / table-only reporting for findings a figure would not clarify.

Success: both behaviors are stated in the domain skill, positively framed, DRY against the existing generic reviewer rule (`agents/reviewer.md:30`) and the upstream-validated-data line (`SKILL.md:58`) — stated as a domain instantiation, not a paraphrase — and with no cross-skill citations.

## Planner Guidance

These are the two edits drafted and reverted during planning; wording exists in that session and is a starting point, not a spec. Fix #1 is a domain instantiation of the generic "no full re-runs, targeted verification" rule — instantiate with concrete triggers, don't restate the generic line. Fix #2: the researcher's intent is "always prefer visualization," so encode it as `[BLOCKING]` with a built-in judgment escape ("unless a figure would not clarify the finding") rather than a mechanical requirement on every single result. Independent of the interactive-mode workstream — a separate concern (data-domain discipline), placed as its own top-level task per concern-first placement.
