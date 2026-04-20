# `writing` Domain Skill — Results

> Mirrors PLAN.md structure. Updated after each task with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-19 (bootstrap)
**Status:** In Progress

---

## Task 1: Scaffold `skills/writing/SKILL.md` — Iron Law + §Three Concurrent Disciplines

**Status:** IMPLEMENTED

**Key findings:**

- **Iron Law final text:** `RESPECT THE AUTHOR'S INTENT` — three clauses (meaning-preserving, scope-bounded, in-progress work respected) + explicit non-goal ("does NOT require preserving word choices, typos, passive-voice awkwardness"). Matches the locked wording from the plan file.
- **§Common Rationalizations table:** 8 rows covering all three Iron Law clauses (rewrite, guessed meaning, structural reorder, voice/diction confusion, TODO handling, warnings, author-mind-reading, post-hoc reversion).
- **§Three Concurrent Disciplines (Preserve / Improve / Verify):** 18 severity-marked items total — Preserve 4, Improve 5, Verify 4, Implementation standards 3, Documentation/handoff 2. Counts: 14 `[BLOCKING]`, 4 `[ADVISORY]`. Reviewer verdict protocol (APPROVE / REVISE) mirrors `econ-data-analysis` exactly.
- **§Pitfalls pointer list:** 7 operation-conditional pointers (sentence edits, structural drafting, multi-dim consistency sweep, single-dim consistency, terminology/notation refactor, build fix, user-work detected). All eight consistency dimensions addressed generically via `consistency/*.md`.
- **§Mode selection** and **§Key References** present and pointing forward at references that will land in subsequent tasks.
- **Architectural parity with `econ-data-analysis/SKILL.md`:** frontmatter shape, Stage-Scoped References table, Iron Law + Common Rationalizations + §Three Concurrent Disciplines + §Pitfalls + §Key References — same anatomy, adapted for writing vertical.

**File:** `skills/writing/SKILL.md` (296 lines).

## Task 2: `style-checklist.md` + `structure-checklist.md`

**Status:** IMPLEMENTED

**Key findings:**

- **`style-checklist.md`:** 9 sentence-level rules (actions-in-verbs / nominalization, old→new info flow, single-hedge-per-claim, active voice, parallel structure, noun-cluster avoidance, sentence length, dangling modifiers, ambiguous pronouns) + 4 paragraph-level rules (topic sentence first, one idea per paragraph, transitions at start, first-sentence link test). Each rule has: ≤10-word name, 1–2 sentence principle, detection trick, before/after example, explicit "do NOT apply when" exceptions (honors Iron Law — rules are heuristics not mandates). §Gated Checklist: 4 `[BLOCKING]` scope/voice items + 13 `[ADVISORY]` rule-application items + 2 handoff items.
- **`structure-checklist.md`:** Pyramid Principle (governing idea, MECE, horizontal/vertical logic), SCQ framing, RAP (Chaubey), two-part introduction (Chaubey p. 108), title-states-finding rule, section-level anatomy (intro/methods/results/conclusion/abstract), no-mystery-novel front-loading, reader-facing headings (Chaubey p. 71), Miller 7±2 chunking. §Gated Checklist: 3 `[BLOCKING]` scope/authorization items + ~20 `[ADVISORY]` structural items + 1 `[BLOCKING]` handoff item.
- **Source coverage:** LRS 1-1a (nominalization — read in full, 32 pages including "some nominalizations are useful" caveats which we preserved), LRS 3-4 (info flow — read in full, first 10 pages covering old→new principle). Chaubey cited by page number for every rule it contributed. Minto / Pyramid Principle webs cited qualitatively.
- **Source-material surprise:** 12 of 14 LRS PDFs at `/Users/zhiyufu/Dropbox/PhD/writing_resources/LittleRedHouse/` are **empty files (0 bytes, Dropbox sync placeholders)** — only LRS 1-1a and LRS 3-4 have content. LRS 5, 6, Arg 1–3, DS 1–2, triage, character (1-1b), cohesion (2) are all inaccessible. The content attributed to them in `style-checklist.md` and `structure-checklist.md` is drawn from Chaubey + plan file summaries. **Flagged for researcher** in final report — should be resolved before Task 8 dogfood.
- **SKILL.md §Pitfalls pointers resolve:** `style-checklist.md` and `structure-checklist.md` both exist at the paths referenced.

**Files:** `skills/writing/references/style-checklist.md` (198 lines), `skills/writing/references/structure-checklist.md` (143 lines).

## Task 3: `consistency/*.md` — 8 dimension-scoped reference files

**Status:** IMPLEMENTED

**Key findings:**

- **Eight files authored:** `terminology.md`, `notation.md`, `cross-references.md`, `citations.md`, `numerical.md`, `math.md`, `argument-logic.md`, `code-paper.md`.
- **Rule count per file** (checklist items, `[BLOCKING]` + `[ADVISORY]`):
  - `terminology.md`: 5 BLOCKING + 3 ADVISORY = 8 items. Sources: `draft-reviewer:writing-clarity-reviewer` (terminology-index pattern), Chaubey p. 76 (consistent key words), p. 157 (don't use interchangeable terms for the same identity).
  - `notation.md`: 5 BLOCKING + 4 ADVISORY = 9 items. Sources: `draft-reviewer:mathematical-reviewer` (notation-consistency section).
  - `cross-references.md`: 4 BLOCKING + 3 ADVISORY = 7 items. Sources: `draft-reviewer:consistency-checker` (cross-reference section) + `draft-reviewer:proofreader` (LaTeX-specific).
  - `citations.md`: 6 BLOCKING + 3 ADVISORY = 9 items. Sources: `draft-reviewer:citation-checker` (completeness, orphans, format, quality).
  - `numerical.md`: 8 BLOCKING + 2 ADVISORY = 10 items. Sources: `draft-reviewer:consistency-checker` (numerical, table/figure). Folds figure/table/caption alignment per user decision.
  - `math.md`: 6 BLOCKING + 3 ADVISORY = 9 items. Sources: `draft-reviewer:mathematical-reviewer` (derivations, proofs, statistical specifications).
  - `argument-logic.md`: 7 BLOCKING + 3 ADVISORY = 10 items. Sources: `draft-reviewer:argument-logic-reviewer` (claim-evidence, causal inference, alternatives, overclaiming / underclaiming).
  - `code-paper.md`: 7 BLOCKING + 3 ADVISORY = 10 items. Sources: `draft-reviewer:code-paper-consistency` (methodology match, variables, sample, reproducibility). Scope note: loaded only when the paper wraps empirical code.
- **Total:** 48 BLOCKING + 24 ADVISORY = 72 severity-marked checklist items across 8 files.
- **Harvest-not-depend discipline preserved:** dimensions come from `draft-reviewer:*`; rule content re-derived in superRA style. No runtime dependency on the draft-reviewer plugin. Common structure across files: §Scope + How-To + §Gated Checklist + §Reviewer verdict protocol + §Output format.
- **Iron-Law respect:** every consistency file explicitly states that consistency-*check* tasks report mismatches rather than silently rewriting beyond scope (flag, don't fix).
- **SKILL.md §Pitfalls pointer `references/consistency/*.md` resolves to all eight files.**
- Each file is concise (100–150 lines) — sized for a single parallel reviewer's context per the user decision on parallel dispatch.

**Files:** 8 files under `skills/writing/references/consistency/`.

## Task 4: `refactor-and-compile.md` + `collaboration.md`

**Status:** Not started

## Task 5: `planning.md` + `workflow.md` — mode-heavy orchestration guidance

**Status:** Not started

## Task 6: `integration.md` + routing updates

**Status:** Not started

## Task 7: `CLAUDE.md` audit

**Status:** Not started

## Task 8: Dogfood — three-mode verification

**Status:** Not started
