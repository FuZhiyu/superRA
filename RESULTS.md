# Fix-Tier Vocabulary — Results

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-05-08 (Tasks 1 + 2 + 3 landed)
**Status:** Tasks 1 + 2 APPROVED; Task 3 IMPLEMENTED (re-cut to mechanical / conventional / authorial + sequence/set/force test)

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

**Status:** IMPLEMENTED. Commit C staged.

Final state across the touched files:
- `skills/writing/references/review.md §Fix tiers` — three tier bullets rewritten to `mechanical` / `conventional` / `authorial`. New **Sequence/set/force test** paragraph carries the rule (sequence + set + force preserved → conventional; any one shifts → authorial) and the 6 worked examples across the boundary (sentence-break vs sentence-reorder; nominalization vs hedge strengthening; coordinate-merge vs subordination; topic-sentence move). Closing footnote names the prior `judgment` / `decision` vocabulary so commit messages before 2026-05-08 stay matchable. Framing line and `Auto-fixable` history mention preserved verbatim.
- 8× `skills/writing/references/consistency/*.md` — output blocks now read `Fix: mechanical | conventional | authorial   # see review.md §Fix tiers`.
- `skills/writing/references/polish.md` — §Input shape C bullets and accepted-deferred line use the new names; §Triage applies `mechanical` and `conventional` in place and surfaces `authorial`. Example list trimmed: redundant-quote suspicion dropped (it's conventional unless it changes the set); claim-evidence gap kept as canonical authorial example; weak topic-sentence rewrite kept and reframed as authorial because the rewrite moves sequence.
- `skills/writing/references/long-form-review.md` — final-summary per-tier batch table enumeration updated to `(mechanical / conventional / authorial)`.
- `skills/writing/CLAUDE.md` — §Multi-agent review pattern fix-tier bullet renamed throughout; load-bearing rationale (continuous supervision-cost axis vs binary; one definition site; binary's failure mode) preserved; new parenthetical history note records the 2026-05-08 re-cut and names the sequence/set/force test as the load-bearing reason against re-introducing the older names. §Polish-mode triage `decision`-tier mention renamed to `authorial`-tier; under-editing failure-mode and framing-suppression cause preserved verbatim.

Verification:
- `grep -rn "judgment\|decision" skills/writing/references/ skills/writing/CLAUDE.md` returns hits in three groups: (1) intentional history mentions of the prior tier names — `review.md:23` (closing footnote), `CLAUDE.md:51` (parenthetical history note); (2) unrelated English uses of "decision" / "judgment" outside the tier vocabulary — `integration.md` (workflow "user decision" / "task or decision"); `polish.md:54` ("agent's own judgment" priority chain); `CLAUDE.md:27` ("light vs deep polish is purely a load decision"); `CLAUDE.md:47` ("per-dimension judgment"); `CLAUDE.md:55` ("apply-vs-surface decision" — the act of deciding); `CLAUDE.md:83` ("reviewer-dispatch-leaves-this-skill decision"); `consistency/numerical.md:5` ("user decision 2026-04-19"). No tier-vocabulary uses of the old names remain.
- `grep -rn "conventional\|authorial" skills/writing/` returns 16 hits in the expected locations: `review.md §Fix tiers` (definition + worked examples + footnote — 4 lines), 8 consistency files (one line each), `polish.md` (§Input shape C bullets + accepted-deferred + §Triage — 3 lines), `long-form-review.md` (1 line), `CLAUDE.md` (§Multi-agent review pattern bullet + §Polish-mode triage — 2 lines).
- Manual end-to-end read of `review.md §Fix tiers` confirms the three tier bullets are non-overlapping, the sequence/set/force test reads cleanly, and the worked examples cover the boundary in both directions. `polish.md §Triage` tier names match the §Fix tiers definition. The eight consistency output blocks all carry the new legal-values line.
