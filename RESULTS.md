# Fix-Tier Vocabulary — Results

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-05-08 (Tasks 1 + 2 landed; Task 3 vocabulary re-cut planned)
**Status:** Tasks 1 + 2 APPROVED; Task 3 not started (re-cut to mechanical / conventional / authorial + sequence/set/force test)

---

## Task 1: Replace `Auto-fixable` flag with `Fix:` tier across review-mode output (Commit A)

**Status:** APPROVED. Commit A landed.

Final state across the touched files:
- `skills/writing/references/review.md` — defines `## Fix tiers` (the single source of truth for the vocabulary). Three concrete consistency-dimension examples per tier; producer-side rule names the reviewer as the tier-picker.
- `skills/writing/references/polish.md §Input shape C` — apply behavior follows the `Fix:` tier on accepted findings.
- 8× `skills/writing/references/consistency/*.md` — output blocks carry `Fix: mechanical | judgment | decision   # see review.md §Fix tiers`.
- `skills/writing/references/long-form-review.md` — REVIEW.md per-aspect-blocks pointer + final-summary tables use the tier vocabulary.
- `skills/writing/CLAUDE.md §Multi-agent review pattern` — fifth bullet records the rationale and the binary's rejected failure mode.

Verification:
- `grep -rn "Auto-fixable\|auto-fixable" skills/writing/` returns 2 hits, both intentional history mentions naming the prior flag (`CLAUDE.md:51`, `review.md:21`).
- `grep -rn "§Fix tiers\|## Fix tiers" skills/writing/` returns the expected 12 hits: 1 definition site (`review.md:13`), 1 polish.md shape C, 1 long-form-review.md, 8 consistency files, 1 CLAUDE.md bullet.

---

## Task 2: Wire fix-tier vocabulary into polish-mode internal triage (Commit B)

**Status:** APPROVED. Commit B landed.

Final state across the touched files:
- `skills/writing/references/review.md §Fix tiers` — first paragraph names two call sites (review output + polish-mode internal triage).
- `skills/writing/references/polish.md` — new `§Triage` section (between §Intent comments and §Minimal-edit discipline) names the apply-vs-surface split for shapes A/B; §Minimal-edit discipline replaced with balanced two-failure-mode framing (the minimal-edit rule constrains size of each fix, not count of fixes).
- `skills/writing/CLAUDE.md` — augmented §Multi-agent review pattern fix-tier bullet with second-call-site pointer; added new §Polish-mode triage section recording the shared-vocabulary rationale and the under-editing failure mode + framing-suppression cause.
- `skills/writing/feedback_polish_under_editing.md` — deleted (recoverable via `git log --diff-filter=D -- skills/writing/feedback_polish_under_editing.md`).

Design-principle filter results (recorded so future contributors can audit which feedback suggestions were absorbed and why):

| Feedback suggestion | Verdict | Reason |
|---|---|---|
| Symmetric over/under-editing warning | Keep | `polish.md §Minimal-edit discipline` actively suppressed baseline diagnostic competence; removing the suppression is one line, behavior-shaping. |
| "Diagnose first" procedural block | Drop | Re-narrates baseline (read before editing). Wrapper around what the agent already does. |
| Reframe `style.md` gated-checklist intro | Drop | Not the failure cause; agent didn't fail to use the checklist because of its framing. |
| Cross-paragraph audit subsection | Drop | Contingency tree — anti-pattern per repo `CLAUDE.md`. General principle is captured by removing framing suppression. |
| End-of-polish self-check | Drop | Baseline competence; additive-rules framing already names it. |
| Mode-specific tier examples (first-pass plan) | Drop | Tier classification is situational, not type-bound; abstract definitions in `review.md` work for both call sites. |

Verification:
- `grep -rn "Auto-fixable\|auto-fixable" skills/writing/` returns 2 hits, both intentional history mentions (`CLAUDE.md:51`, `review.md:21`).
- `grep -rn "§Fix tiers\|## Fix tiers\|§Triage\|## Triage" skills/writing/` returns 14 hits: 1 definition site (`review.md`), 1 polish.md shape C, 1 polish.md §Triage, 1 long-form-review.md, 8 consistency files, 2 CLAUDE.md mentions.
- Manual end-to-end read of `polish.md` confirms balanced framing and named surface path for shapes A/B.

---

## Task 3: Re-cut tier vocabulary to `mechanical` / `conventional` / `authorial` and add the sequence/set/force test (Commit C)

**Status:** *(not started)*

*To be filled in by the implementer after Commit C lands.*
