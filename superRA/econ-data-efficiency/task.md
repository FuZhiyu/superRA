---
title: "Econ-data-analysis: reviewer read-first default and prefer-visualization"
status: approved
depends_on: []
---

## Objective

Fold two efficiency refinements into `skills/econ-data-analysis/SKILL.md`, as domain discipline (the generic role specs stay adversarial and unchanged):

1. **Reviewer read-first / targeted-effort default.** In data work, verification assesses the committed diagnostics, row-count logs, and output files first; re-execution is targeted to a *suspected discrepancy* (implausible magnitude, missing count, number disagreeing with `## Results`), not routine. When iterating or fixing, re-run only the changed step and its downstream dependents — unaffected upstream outputs stand as committed.
2. **Prefer visualization in results.** Present headline findings visually by default (distribution, relationship, or time path); reserve number-only / table-only reporting for findings a figure would not clarify.

Success: both behaviors are stated in the domain skill, positively framed, DRY against the existing generic reviewer rule (`agents/reviewer.md:30`) and the upstream-validated-data line (`SKILL.md:58`) — stated as a domain instantiation, not a paraphrase — and with no cross-skill citations.

## Planner Guidance

These are the two edits drafted and reverted during planning; wording exists in that session and is a starting point, not a spec. Fix #1 is a domain instantiation of the generic "no full re-runs, targeted verification" rule — instantiate with concrete triggers, don't restate the generic line. Fix #2: the researcher's intent is "always prefer visualization," so encode it as `[BLOCKING]` with a built-in judgment escape ("unless a figure would not clarify the finding") rather than a mechanical requirement on every single result. Independent of the interactive-mode workstream — a separate concern (data-domain discipline), placed as its own top-level task per concern-first placement.

## Results

Both refinements folded into [skills/econ-data-analysis/SKILL.md](../../skills/econ-data-analysis/SKILL.md) as domain discipline; the generic role specs were left untouched.

**Fix #1 — targeted verification effort** ([SKILL.md](../../skills/econ-data-analysis/SKILL.md)): added a `**Targeted verification effort.**` paragraph in the shared implementer/reviewer framing of §Three Concurrent Disciplines, directly after the note that hands verdict mechanics to `agents/reviewer.md`. Placed there because the discipline is applied by both roles (reviewer verification and implementer iteration), and effort allocation is domain content the reviewer spec does not own. Instantiated with data-specific evidence (committed diagnostics, row-count logs, output files) and concrete re-execution triggers (implausible magnitude, missing row-count log, number disagreeing with `## Results`), plus the iterate-only-changed-step-plus-downstream rule. It does not restate the generic reviewer line (`agents/reviewer.md:30`, "full re-runs not required, targeted verification when something looks off") — it instantiates it in data terms. It complements rather than duplicates the upstream-validated-data line (`SKILL.md:58`, a Describe-phase rule about not re-validating upstream-clean data): the new paragraph governs verification and iteration effort across a task, a distinct moment.

**Fix #2 — prefer visualization in results** ([SKILL.md](../../skills/econ-data-analysis/SKILL.md)): added a `[BLOCKING]` **Headline findings presented visually.** item to §Documentation and handoff, before the existing figure-save/embed mechanics item. Carries the built-in judgment escape ("unless a figure would not clarify it — a lone scalar, or a small table that already reads clearly") so it is a default-with-escape, not a mechanical every-result requirement. Distinct from the Describe-phase visualization `[ADVISORY]` items (histograms/scatter/line plots of *input* variables about to be transformed): this item governs presentation of *headline findings* in `## Results`.

Both edits are positively framed and carry no cross-skill citations in the shipped prose (the `agents/reviewer.md` pointer sits in a pre-existing line, not in the new text). Verified: `grep` confirms the new phrases are present and no new backtick cross-skill path citations were introduced by the added lines.
