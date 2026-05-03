# Multi-Agent Review Protocol — Results

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-05-02 (planning)
**Status:** In Progress

---

## Task 1: Author `long-form-review.md`

**Status:** IMPLEMENTED

Authored `skills/writing/references/long-form-review.md` (33 body lines, under the ~40 target). The reference covers the four sections required by PLAN Step 1 — Trigger, Doc convention, Dispatch convention, Multi-perspective deep mode — and is pointer-only for everything that already lives in `superRA:handoff-doc references/plan-anatomy.md`, `superRA:handoff-doc` SKILL.md (inline-edit / atomic-commit), `superRA:agent-orchestration §Dispatch Templates` (canonical reviewer template, parallel + worktree-isolation steering), and the eight `consistency/<dim>.md` output formats.

**Key deltas the reference teaches** (each survived the line-by-line DRY + Necessity audit):

- Doc name `REVIEW.md` at worktree root with explicit collision rationale vs `PLAN.md`, plus a one-review lifecycle.
- Header indices (notation / terminology / figures / cross-references) live under `## Project Conventions`, with `## Document Map` as the scale-up path. Orchestrator builds once before dispatch so reviewers do not cold-read the manuscript.
- Per-aspect blocks reuse the existing task-block anatomy with `**Depends on:** *(none)*` (parallel) and findings flow into the existing review-notes blockquote in each `consistency/<dim>.md`'s output format including the new `Auto-fixable` line.
- Final summary block sits at the top: severity × auto-fixable counts, top-3 priorities, pointers, and the auto-fixable batch table consumed by polish-mode shape C.
- `## Workflow Status` is omitted standalone; the riding workflow's PLAN.md owns the rollup when present.
- `Stage: implementation` reused (no new Stage value); the manuscript is the implicit implementer output and reviewers append findings instead of returning APPROVE/REVISE on a commit range.
- No reviewer-of-reviewer pass; an optional final-summary reviewer over the assembled doc is the only permitted second pass.
- Deep mode dispatches 2–3 reviewers per dimension with stance and ordering variation, each into its own per-perspective task block; closeout dedups and weights multi-agent-confirmed findings higher.

## Task 2: Thoroughness slider + cross-pointer in `review.md`

**Status:** IMPLEMENTED

Added a §Thoroughness section (5 body lines + a closing line) after §Workflow in `skills/writing/references/review.md`, and appended a one-sentence cross-pointer to the existing §Multi-dimensional consistency reviews paragraph. `long-form-review.md` is loaded only on the Deep entry and on the N > 1 condition; Quick stays purely in `review.md`.

**Pointer-only discipline** (DRY/Necessity gate applied line-by-line):

- Deep mode says only "Loads `long-form-review.md`, which owns the multi-perspective dispatch rule" — no stance / ordering / 3-reviewer detail restated. The PLAN draft's "(3 reviewers per dim with stance + ordering variation)" qualifier was deleted.
- The N > 1 cross-pointer says only "load `long-form-review.md` for the shared review-doc protocol" — no header-indices content restated. The PLAN draft's "so each reviewer reads pre-built notation / terminology / cross-reference indices" tail was deleted.
- Standard mode references the existing same-file §Multi-dimensional consistency reviews section instead of restating the one-reviewer-per-dimension mechanism.

**Net additions:** 7 lines (5 thoroughness items + closing inference line + the trailing sentence on the multi-dim paragraph).

## Task 3: Auto-fixable flag in 8 `consistency/*.md` output formats

**Status:** Implemented.

Added `Auto-fixable: Yes / No` as the last field inside the Output format fenced block in all 8 consistency reference files (argument-logic, citations, code-paper, cross-references, math, notation, numerical, terminology). Each addition is a single line placed immediately after the existing `Recommendation:` line and before the closing code fence — no other changes.

**Net additions:** 8 lines, one per file.

## Task 4: Substance gaps — `style.md` + `consistency/terminology.md`

**Status:** Implemented.

`skills/writing/references/style.md`: added §Clarity heuristics subsection (between §Precision of reference and §Gated Checklist) with two heuristics — nested-clause run-ons (3+ embedded clauses or lost subject-verb tracking → consider splitting at the clause boundary that carries the most logical weight) and vague quantifiers (`various`, `some`, `several`, `a number of` → consider quantifying or naming the set; carve-out for deliberate vagueness). Phrased as "consider X" — additive to baseline writing competence per `SKILL.md §These rules are additive`, no Gated Checklist entry, no `[BLOCKING]` markers.

`skills/writing/references/consistency/terminology.md`: added §Definition-clarity audit subsection (after §Glossary audit, inside How-To). Audits definitions for explicit (stated, not assumed), precise (not circular), field-norm-consistent, and prose↔math aligned; closes on "flag the mismatch" — flag-only-vs-author-decision framing stays owned by `SKILL.md §Preserve substance` and the file's `[BLOCKING] No silent cross-scope rewrites` gate. No Gated Checklist entry — heuristic audit, not blocking.

**Net additions:** 2 short subsections, ~3 lines of prose each (excluding headers).

## Task 5: LaTeX-rendering coverage in `refactor-and-compile.md`

**Status:** IMPLEMENTED

Verified the six PLAN-listed LaTeX-rendering hazards against `skills/writing/references/refactor-and-compile.md` at HEAD. Three were already covered by §Compile content: broken `??` cross-references (Reading build output bullet 3 + warning table `Reference(s) undefined`), missing bibliography entries (warning table `Citation(s) undefined` + Pandoc `Could not find reference`), and overfull / underfull hbox warnings (warning table rows 1–3). Three were missing: unescaped `%`, `&`, `#`, `_` in text mode; unclosed math-mode delimiters; and equation numbering gaps.

Added §LaTeX-rendering hazards subsection (one lead line + 3 bullets) inside §Compile, between the warning triage table and §Error-escalation rules. Each bullet names a failure mechanism the warning table does not surface — silent `%` truncation by a refactor, the cascade pattern of an unclosed `$/\)/\]`, and a `\label` placed in a starred env or after `\nonumber` producing `??` at every `\ref` site — and points the agent at a fix. No restatement of the warning table, the §Refactor word-boundary discipline, or the existing `??` rule.

**Net additions:** 7 lines (subsection header, blank, lead line, blank, 3 bullets) inside §Compile.

## Task 6: Routing surfaces — `SKILL.md` knowledge-files row + `CLAUDE.md` design notes

**Status:** IMPLEMENTED

`skills/writing/SKILL.md`: added one row to §Knowledge files between `consistency/*.md` and `refactor-and-compile.md` — `references/long-form-review.md` with the load condition `Multi-dimensional review (N > 1 consistency dimensions), `deep` thoroughness, or full-paper / pre-submission scope.` Pointer-only; no protocol restatement.

`skills/writing/CLAUDE.md`: added §Multi-agent review pattern (13 lines) between §Reviewer-dispatch invariants leave this skill and §Stage-scoped references. Records four design choices as rationale, not procedure:

- (a) `long-form-review.md` is orchestration-only — per-dimension substance lives in `consistency/<dim>.md`.
- (b) Shared doc is `REVIEW.md`, not `PLAN.md`, to avoid collision with a workflow's own `PLAN.md`; lifecycles coexist (project-spanning vs single-review).
- (c) No `consistency/proofreading.md` — mechanical proofreading is baseline competence; LaTeX-rendering hazards live with the build step in `refactor-and-compile.md`.
- (d) No new `Stage:` value — review-as-data dispatch reuses `Stage: implementation` and routes via the existing `using-superRA §Skill-Load Manifest` Domain add-ons row.

**DRY + Necessity gate:** applied line-by-line to both additions. SKILL.md row mirrors `long-form-review.md §Trigger` only as far as needed to gate loading. CLAUDE.md bullets each pass the "would a future contributor re-litigate this without this entry?" test — bullet (d) is borderline DRY against the global memory rule but kept because the manifest routing path is the resolution and is not obvious from the prohibition alone.

**Net additions:** 1 table row in SKILL.md; 13 lines (one §-block) in CLAUDE.md. Consistent with §Reviewer-dispatch invariants leave this skill — that section says standalone review terminates at edit + commit and parallel multi-dim dispatch is a within-skill technique; the new subsection names `long-form-review.md` as that within-skill technique and reaffirms `Stage: implementation` reuse.

## Task 7: Real-paper validation

**Status:** Not started

## Task 8: Retire `draft-reviewer` (downstream)

**Status:** Not started
