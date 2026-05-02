# `writing` Domain Skill — Results

> Mirrors PLAN.md structure. Updated after each task with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-05-02 (main re-synced under minimum-net-diff)
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

- **`style-checklist.md`:** 9 sentence-level rules (actions-in-verbs / nominalization, old→new info flow, single-hedge-per-claim, active voice, parallel structure, noun-cluster avoidance, sentence length, dangling modifiers, ambiguous pronouns) + 4 paragraph-level rules (topic sentence first, one idea per paragraph, transitions at start, first-sentence link test). Each rule has: ≤10-word name, 1–2 sentence principle, detection trick, before/after example, explicit "Do NOT apply when" exception note (honors Iron Law — rules are heuristics not mandates). §Gated Checklist: `[ADVISORY]` rule-application items + handoff items; **SKILL.md's scope/voice BLOCKING quartet removed per shared-gating DRY** (walked via SKILL.md §Three Concurrent Disciplines).
- **`structure-checklist.md`:** Pyramid Principle (governing idea, MECE, horizontal/vertical logic), SCQ framing, RAP (Chaubey), two-part introduction (Chaubey p. 108 — LRS 5–6 co-cite removed since source PDFs were empty placeholders), title-states-finding rule, section-level anatomy (intro/methods/results/conclusion/abstract), no-mystery-novel front-loading, reader-facing headings (Chaubey p. 71), Miller 7±2 chunking. §Gated Checklist: ~20 `[ADVISORY]` structural items + 1 `[BLOCKING]` handoff item; **§Scope and authorization BLOCKING items removed per shared-gating DRY** (walked via SKILL.md §Preserve + §Implementation standards).
- **Source coverage:** LRS 1-1a (nominalization — read in full, 32 pages including "some nominalizations are useful" caveats which we preserved), LRS 3-4 (info flow — read in full, first 10 pages covering old→new principle). Chaubey cited by page number for every rule it contributed. Minto / Pyramid Principle webs cited qualitatively. **Sources lines corrected:** `style-checklist.md` no longer cites LRS 1-1b / LRS 2 (no rule draws from them); `structure-checklist.md` now reads "LRS plan summaries (LRS 5, 6, Arg 1–3 — pending source verification)" rather than claiming direct LRS attribution.
- **Source-material surprise:** 12 of 14 LRS PDFs at `/Users/zhiyufu/Dropbox/PhD/writing_resources/LittleRedHouse/` are **empty files (0 bytes, Dropbox sync placeholders)** — only LRS 1-1a and LRS 3-4 have content. LRS 5, 6, Arg 1–3, DS 1–2, triage, character (1-1b), cohesion (2) are all inaccessible. The content attributed to them in `style-checklist.md` and `structure-checklist.md` is drawn from Chaubey + plan file summaries. **Flagged for researcher** in final report — should be resolved before Task 8 dogfood.
- **SKILL.md §Pitfalls pointers resolve:** `style-checklist.md` and `structure-checklist.md` both exist at the paths referenced.
- **Re-reviewed 2026-04-19:** addressed MAJOR 1 (shared-gating de-duplication), MAJOR 3 (LRS source re-attribution), MINOR 7 ("Do NOT apply when" exception notes added to 7 style rules). See commit `224c8cb`.

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

**Status:** IMPLEMENTED

**Key findings:**

- **`refactor-and-compile.md`:** Two sections. §Refactor covers the Four Always (preview, word-boundary, case/plural variants, quotations sacred), worked false-positive table (now includes a genuine `Table` / `Tablespoon` / `TableView` / `turntable` row plus an illustrative `est` row — the earlier misleading `Table 1` / `acceptable` entry was replaced per MINOR 10), math-mode refactor approach, terminology refactor rules. §Compile covers build commands for LaTeX (latexmk), Quarto, Pandoc; 11-row warning triage table; error-escalation rules; handoff format. §Refactor Gated Checklist: 6 BLOCKING + 1 ADVISORY. **§Compile Gated Checklist slimmed per shared-gating DRY** — SKILL.md §Verify owns "document builds / no new unresolved cross-references / no new undefined citations"; this file keeps only operation-specific items (build-command-stated, File-not-found, warning-triage).
- **`collaboration.md`:** Detection patterns (git-level: `git status`/`git diff`/`git log`; in-file: TODO, `\todo{}`, `[fill in]`, `??`, commented-out text, unfinished paragraphs; file-level: `*-draft`, `.gitignore`, read-only). Edit-vs-propose-vs-ask decision matrix (7 rows). Four escalation templates ("I noticed...", "should I include...", "conflict with in-progress work", "structural proposal"). Voice-preservation operational definition (diction + register + sentence-shape; 6 concrete signals). §Gated Checklist slimmed per shared-gating DRY — **SKILL.md's Preserve quartet (no-edits-outside-scope, voice preservation, in-progress-work respected, meaning preservation) removed** from this file; collaboration-specific items retained (git-status check, hot-line handling, escalation-template-used, user-decisions-logged).
- **Re-reviewed 2026-04-19:** addressed MAJOR 1 (shared-gating de-duplication in both files) + MINOR 10 (Table 1 false-positive row). See commit `224c8cb`.
- **One-source-of-truth discipline:** Style rules are NOT re-explained in refactor-and-compile.md (cross-refs to `style-checklist.md`). Cross-reference check in §Refactor points at `consistency/cross-references.md` rather than re-stating the rules. Collaboration.md points at `consistency/terminology.md` for terminology legitimacy rather than duplicating.
- **Iron-Law alignment:** collaboration.md explicitly operationalizes the Preserve side of the Iron Law (detection patterns for in-progress work, escalation templates for structural changes, voice-preservation checks). refactor-and-compile.md §Refactor gates on "direct quotations and block quotes not touched (quotes are sacred)" — the Iron Law meaning-preservation clause operationalized.
- **Handoff-doc discipline:** collaboration.md references `handoff-doc` §User Decisions Log for logging escalation outcomes, and `AskUserQuestion` for the escalation tool.

**Files:** `skills/writing/references/refactor-and-compile.md` (154 lines), `skills/writing/references/collaboration.md` (158 lines).

## Task 5: `planning.md` + `workflow.md` — mode-heavy orchestration guidance

**Status:** IMPLEMENTED

**Key findings:**

- **`planning.md`:** Scope-inventory checklist (7 items); task-size triage table (6 shapes); PLAN.md/RESULTS.md decision matrix (6 rows, matches PLAN.md spec); optional-row rationale; "what a writing PLAN.md / RESULTS.md looks like" sections; **Hard Gate** for mode-(d) full-workflow (scope-confirmation-before-drafting — the writing-vertical analogue of econ-data-analysis's Data Inventory hard gate, lighter-weight but same principle). §Gated Checklist: 7 BLOCKING + 2 ADVISORY items.
- **`workflow.md`:** Two Hard Rules (reviewer dispatch never skipped; parallel-dispatch for multi-dim consistency) — each with explicit "why" rationale. Four usage modes fully described: (a) direct-edit, (b) pure-review (single + multi-dimensional flows), (c) review → edit → re-review loop, (d) full workflow. Mode-transition rules (a→c, b→c, c→d, d→c — normal; silent (d)-under-(a) — not normal). Dispatch quick-reference with Agent-tool envelopes for each mode. §Gated Checklist: 6 BLOCKING + 1 ADVISORY items.
- **Cross-linking verified:** `workflow.md` references each `consistency/*.md` pattern (generically — "one reviewer per `consistency/*.md` file") and the specific `style-checklist.md` / `structure-checklist.md` / `refactor-and-compile.md`. `planning.md` references `workflow.md`'s mode names consistently. Both reference `superRA:handoff-doc`, `superRA:agent-orchestration`, and `superRA:using-superRA` appropriately.
- **Reviewer-dispatch-never-skipped rule** is now stated in three places (main SKILL.md §Mode selection, `workflow.md` Rule 1, `planning.md` Gated Checklist BLOCKING item). This is intentional reinforcement of a load-bearing rule — not drift (all three point at the same rule; `workflow.md` is the source of truth).
- **Architectural parity with `econ-data-analysis/references/planning.md`:** same gate structure (Hard Gate + checklist + rationale + common-mistakes-equivalent via the decision matrix), lighter-weight content because writing scope is simpler than data inventory.
- **Re-reviewed 2026-04-19:** addressed MINOR 13 (workflow.md §Mode (c) now includes "Cap at 3 rounds" escalation guard) + MINOR 15 (dispatch envelopes for mode (a) and mode (b) now carry `subagent_type: reviewer` to make role explicit, aligning with `superRA:agent-orchestration §Dispatch Templates`).

**Files:** `skills/writing/references/planning.md` (127 lines), `skills/writing/references/workflow.md` (189 lines).

## Task 6: `integration.md` + routing updates

**Status:** IMPLEMENTED

**Key findings:**

- **`integration.md` drafted.** Writing-specific pre-merge gates organized as six numbered gates: (1) document builds clean on merged state; (2) outline stability; (3) cross-reference integrity; (4) applicable consistency dimensions pass (parallel reviewers); (5) voice preserved (three-hunk sample check); (6) scope respected (every hunk traceable). Includes a dispatch-guidance table mapping edit type → applicable consistency dimensions. Data-analysis-touching writing tasks note: when the writing task produced numbers, `econ-data-analysis/references/integration.md` applies in addition. §Gated Checklist: 7 BLOCKING + 3 ADVISORY items.
- **Routing updates applied across 5 files** (not 6 — `merge-workflow/SKILL.md` does not exist in this repo):
  - **`skills/using-superRA/SKILL.md` §Skill Inventory:** added `Domain | writing` row.
  - **`skills/using-superRA/SKILL.md` §Skill-Load Manifest:** extended the `implementation`, `integration`, `drift-test`, and `planning-review` rows with writing-specific stage-scoped references.
  - **`skills/planning-workflow/SKILL.md` Phase 1 vertical table:** added `Writing` row pointing at `superRA:writing` + `writing/references/planning.md`. Added routing explanation that most writing tasks skip `planning-workflow` entirely (modes a/b/c in `workflow.md`); only mode (d) full-workflow enters.
  - **`skills/integration-workflow/SKILL.md` Phase A:** added writing-vertical branch — drift tests replaced by build + outline-stability for writing-only tasks.
  - **`skills/integration-workflow/SKILL.md` Phase D Step 3a:** added writing-vertical post-merge verification note.
  - **`skills/CATEGORIES.md`:** added `writing` row under Domain; removed writing from the future-verticals list.
  - **`README.md`:** added `writing` row to the Domain skill table; updated section heading to "Domain — Data Analysis and Writing"; updated roadmap to say writing is implemented.
- **Manifest path verification:** all 16 `writing/references/*` files referenced in the Skill-Load Manifest and elsewhere exist on disk. Checked: `planning.md`, `workflow.md`, `style-checklist.md`, `structure-checklist.md`, `refactor-and-compile.md`, `collaboration.md`, `integration.md`, plus 8 consistency files (`terminology.md`, `notation.md`, `cross-references.md`, `citations.md`, `numerical.md`, `math.md`, `argument-logic.md`, `code-paper.md`). No broken pointers.
- **Plan deviation note (Step 3):** the PLAN.md spec named `merge-workflow/SKILL.md` as an edit target; that skill does not exist in this repo (merge choreography is Phase D of `integration-workflow`). The Phase D writing note covers the same concern. Plan step rewritten in place.
- **Re-reviewed 2026-04-19:** addressed MINOR 14 — Gate 4 text no longer requires per-dimension consistency reviewers to load `integration.md`. Per-dimension reviewers load `writing/SKILL.md` + their one `consistency/*.md`; the integration-gate reviewer (orchestrator-dispatched separately) loads this `integration.md`.
- **Rollback 2026-04-22:** reverted the attempted `main` sync (`99fb3ba`, `656e974`) after reviewing `main`'s intent. The critical mismatch was `skills/using-superRA/SKILL.md`: `main` deliberately removed `## Universal Principles` in `72c38e3` after `564021b`'s broader duplicate-protocol simplification, redistributing that content to owner files (`references/main-agent.md`, workflow structure, `handoff-doc`, reviewer/integration references). Carrying the section forward on this branch violated the minimum-net-diff rule for shared surfaces.
- **Archived-handoff rationale:** the pre-revert `main` archive at `docs/plans/2026-04-17-codex-compatibility-plan.md` explicitly says that a minimum-net-diff sync should take `main` verbatim on shared files and re-thread only branch-specific additive surfaces. The reverted sync did the opposite for `using-superRA`: it preserved an older branch-local structure on a file where `main` had already changed the source-of-truth split.
- **Current branch state after rollback:** restored to the pre-sync writing branch plus a new `PLAN.md` decision entry documenting why the sync was rejected. Any future refresh against `main` should start from `main`'s simplified shared skill surfaces and reapply only the writing-vertical deltas.
- **2026-05-02 re-sync (semantic-merge, standalone mode):** Merged `main` into `domain/writing-skills` using the take-main-verbatim rule on shared surfaces. Re-threaded writing-vertical additions into the surfaces main reshaped: writing row in `using-superRA/SKILL.md` Skill Inventory + Skill-Load Manifest add-on table; writing row in `planning-workflow/SKILL.md` Phase 1 vertical table; writing notes in `integration-workflow/SKILL.md` §Protect and §When to Lighten; writing rows in `skills/CATEGORIES.md` and `README.md` domain tables. Dropped `skills/execution-workflow/` (renamed to `implementation-workflow` on main) and the four reference files main deleted (`refactor-and-integrate/references/{codebase-integration,drift-test-quality,merge-quality}.md`, `using-superRA/references/codex-tools.md`). Refreshed stale references inside `skills/writing/` to match main's new structure (workflow-pipeline names, `§Universal Principles` rephrased generically since main moved that content into its owning files). Recorded as a `SEMANTIC_MERGE.md` entry. Note: `CLAUDE.md` did not need a writing-specific amendment because main's restructured §Adaptive, Composable Workflows already states "Domain and utility skills stand alone" — the original Task 7 amendment is now subsumed.

**Files:** `skills/writing/references/integration.md` (95 lines) + 5 routing-edit files modified (`using-superRA/SKILL.md`, `planning-workflow/SKILL.md`, `integration-workflow/SKILL.md`, `CATEGORIES.md`, `README.md`).

## Task 7: `CLAUDE.md` audit

**Status:** IMPLEMENTED

**Audit findings:**

- **(a) "Domain skills are usable standalone without the workflow scaffold": ABSENT.** Pre-amendment `CLAUDE.md` §Architectural pattern and §Domain verticals described domain skills as composing *with* the workflow scaffolding but never stated they work *without* it. Needed to be added explicitly.
- **(b) "Reviewer dispatch is never skipped, even in standalone modes": PARTIALLY STATED.** Workflow principle #1 says "Review is never skipped, regardless of perceived triviality", but the phrasing is contextualized around the workflow pipeline (drift-test review, integration review, per-task review during execution) and does not explicitly carry through to standalone / direct-mode usage. Needed the "even in standalone modes" extension.

**Amendment applied:**

Added one paragraph under §Domain verticals (between the intro sentence and "**Currently implemented:**") stating both properties:

1. Domain skills are usable standalone without the full PLAN → IMPLEMENT → VALIDATE → INTEGRATE scaffold.
2. Each domain skill owns a mode-selection reference documenting lightweight usage modes alongside the full-workflow case (writing vertical referenced as exemplar: `writing/references/workflow.md`).
3. Reviewer dispatch is never skipped even in standalone modes — explicit reinforcement of workflow principle #1 for direct-mode / standalone invocations.

The addition is concise (one paragraph), sits in the logical location (§Domain verticals — where readers learn about domain skills), and does not weaken any of the four workflow principles.

**Files:** `/CLAUDE.md` — single paragraph amendment under §Domain verticals.

**Re-reviewed 2026-04-19:** addressed MAJOR 2 — writing is no longer treated as a hypothetical future vertical.

- Added a **Writing** bullet under §Currently implemented (mirroring the Data-analysis bullet): names Iron Law (RESPECT THE AUTHOR'S INTENT), four-mode standalone usability (`workflow.md`), and the stage-scoped reference manifest.
- Reworded "Data analysis is the flagship vertical, not the whole product" to reflect that data analysis **and writing** are both implemented.
- Dropped "writing" from the §Extension path parenthetical (`theory, literature review, simulation, writing` → `theory, literature review, simulation`).
- Removed the "Writing / paper drafting" bullet from §Planned verticals.

Parallel sweep of the same stale "writing-as-future-vertical" framing across three additional files (MINORs 4, 5, 6):

- `README.md` — future-vertical sentence reframed to list writing as implemented.
- `skills/using-superRA/SKILL.md` §Composable Design — "today: `econ-data-analysis`" → include writing.
- `skills/planning-workflow/SKILL.md` — "writing" removed from future-verticals parenthetical.

See commit `bc885fe`.

## Task 8: Dogfood — three-mode verification

**Status:** Not started
