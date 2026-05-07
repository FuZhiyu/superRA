# Fix-Tier Vocabulary — Results

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-05-06 (planning — Task 2 added, Task 1 partial)
**Status:** In Progress

---

## Task 1: Replace `Auto-fixable` flag with `Fix:` tier across review-mode output (Commit A)

**Status:** In progress — Steps 1–3 done in working tree (uncommitted); Steps 4–6 pending.

Working-tree state (verified by `git diff --stat`):
- `skills/writing/references/review.md` — adds §Output contract: Fix tiers (renamed to §Fix tiers in Task 2 Step 1).
- `skills/writing/references/polish.md` — adds tier-based apply policy in §Input shape C.
- 8× `skills/writing/references/consistency/*.md` — `Auto-fixable: Yes / No` line replaced with `Fix: mechanical | judgment | decision   # see review.md §Output contract: Fix tiers` (pointer text updated to `§Fix tiers` in Task 2 Step 1).

Verification commands and results to be filled in after Commit A lands.

---

## Task 2: Wire fix-tier vocabulary into polish-mode internal triage (Commit B)

**Status:** Not started.

Design-principle filter results (recorded so future contributors can audit which feedback suggestions were absorbed and why):

| Feedback suggestion | Verdict | Reason |
|---|---|---|
| Symmetric over/under-editing warning | Keep | `polish.md §Minimal-edit discipline` actively suppresses baseline diagnostic competence; removing the suppression is one line, behavior-shaping. |
| "Diagnose first" procedural block | Drop | Re-narrates baseline (read before editing). Wrapper around what the agent already does. |
| Reframe `style.md` gated-checklist intro | Drop | Not the failure cause; agent didn't fail to use the checklist because of its framing. |
| Cross-paragraph audit subsection | Drop | Contingency tree — anti-pattern per repo `CLAUDE.md`. General principle is captured by removing framing suppression. |
| End-of-polish self-check | Drop | Baseline competence; additive-rules framing already names it. |
| Mode-specific tier examples (first-pass plan) | Drop | Tier classification is situational, not type-bound; abstract definitions in `review.md` work for both call sites. |

Verification commands and results to be filled in after Commit B lands.
