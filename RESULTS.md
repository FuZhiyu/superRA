# `writing` Skill — Redesign Results

> Mirrors PLAN.md task structure. Updated after each task with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-05-02 (redesign plan committed; tasks not yet started)
**Status:** In Progress

The 2026-04-19 → 2026-05-02 build of `skills/writing/` (Iron Law, Three Concurrent Disciplines, four-mode workflow, eleven references) is the *input* to this redesign. That work's findings are recorded in commits `7a4cf1a` and earlier; per the inline-edit rule (`superRA:handoff-doc`), this RESULTS.md describes only the redesign work.

---

## Task 1: Rewrite `SKILL.md` + author three mode files

**Status:** IMPLEMENTED

**Files written:**
- `skills/writing/SKILL.md` — full rewrite (54 lines, was 171). Body sections in PLAN order: frontmatter (mode-organized triggers); §What this skill does (one paragraph); §Preserve substance, polish prose (preserve-list / polish-list / no-restructure-without-load); §Before you start (3 numbered items: classify mode, inspect git, inline-directive convention); §Mode routing table (4 rows: Review / Polish-sentence / Polish-structural / Draft); §Knowledge files table (style.md, structure.md, consistency/*.md, refactor-and-compile.md, integration.md); §Coupling to superRA workflows (one paragraph); §Sources.
- `skills/writing/references/review.md` — new (25 lines). Workflow steps (scope confirm → load dimension files → end-to-end read → classify findings into style/structure/consistency/argument → report); multi-dimensional parallel-reviewer pattern; review-as-planning; "no edits in this mode" invariant.
- `skills/writing/references/polish.md` — new (40 lines). §Input shapes A/B/C (unstaged edits / named target / review-findings list); §Edit-vs-propose-vs-ask matrix (relocated from collaboration.md); §Minimal-edit discipline + post-edit build. The §Sentence-vs-structural-scope and §Inline-directive-convention subsections, plus the §Input-shape-A item 4 commit-handoff line, were cut on REVISE round 1 — all three failed the necessity gate as restatements of `SKILL.md` content or workflow-skill territory.
- `skills/writing/references/draft.md` — new (19 lines). 5-step workflow (gather inputs → outline → draft → self-check → build); §Workflow coupling (whole-section drafts route through planning-workflow); §Author intent and tone.

**Content relocations from old files:**
- Iron Law / Three Concurrent Disciplines / Common Rationalizations from old `SKILL.md` → dropped wholesale per the 2026-05-02 redesign decision; the single principle "Preserve substance, polish prose" replaces them.
- Voice quartet from old `SKILL.md §Preserve` → softened: structure / argument / claims / intent / tone are sovereign, but the strict "co-author would recognize the diff" line is gone.
- "Two hard rules" from old `workflow.md` → reviewer-dispatch invariant moved out of the writing skill (now owned by workflow skills); parallel-dispatch survives in `review.md` as a behavior the review-mode agent applies when scope is multi-dimensional.
- Four usage modes from old `workflow.md` → replaced by three working modes; mode (a)/(b)/(c)/(d) taxonomy retired.
- "Edit vs propose vs ask" matrix from old `collaboration.md` → relocated into `polish.md`.
- "Detect in-progress work" from old `collaboration.md` → absorbed into `SKILL.md §Before you start` (item 2: git-status/diff inspection) and `polish.md §Input shapes A` (unstaged-edit handling).
- Inline-directive convention — inverted from old `collaboration.md` (TODOs were sacred) to the redesign default (TODOs are tasks for the agent; explicit `DO NOT EDIT` is the hands-off marker).
- Review-as-planning pattern from old `planning.md` → relocated into `review.md`.

**Necessity-gate audit (CLAUDE.md §Teach the Protocol):**
- Removed: planned `§Before you start` item 4 (intent comments) — Task 4 owns adding this; including it pre-emptively in Task 1 would conflict with Task 4's authoring.
- Removed: redundant "polish requests with structural edits route to Polish (structural scope)" tail clause in `SKILL.md §Before you start` item 1 — the Mode routing table below already states this; restating it is wrapper text.
- Cut on REVISE r1: `polish.md §Sentence vs structural scope` — the rule lives in `SKILL.md §Mode routing` and is operationalized again in the §Edit-vs-propose-vs-ask matrix; the subsection added no behavior.
- Cut on REVISE r1: `polish.md §Inline-directive convention` — bare pointer + paraphrase of `SKILL.md §Before you start`; the operational rule is already stated in §Input shape A items 2–3.
- Cut on REVISE r1: `polish.md §Input shape A` item 4 (commit-handoff line) — workflow-skill territory; "commit only when requested" is default agent behavior.
- Tightened: `review.md` multi-dimensional reviews paragraph — removed orchestrator-specific dispatch mechanics (those live in the workflow skills) and the consolidate-relay procedural detail; kept the load-bearing rule (one reviewer per dimension in parallel) and its rationale.
- Tightened: `draft.md §Coupling to the full superRA workflow` — replaced narrative paragraph with two-line directive.

**Knowledge files NOT touched in this task:** `style-checklist.md`, `structure-checklist.md`, `refactor-and-compile.md`, all 8 `consistency/*.md`, `integration.md`. Task 2 owns those header rewrites + severity-tag drops + integration trim.

**Cross-references that will become stale after this task lands but before Task 3:** the new `SKILL.md` does not reference `workflow.md`, `planning.md`, or `collaboration.md` — those forward-pointers are gone. The old knowledge files (`style-checklist.md` etc.) still carry references to `§Three Concurrent Disciplines` and the old `workflow.md` — Task 2 cleans those up. No grep-target stale references introduced by Task 1.

## Task 2: Lighten knowledge files and trim `integration.md`

**Status:** IMPLEMENTED

**Files renamed (`git mv`):**
- `style-checklist.md` → `style.md` (was 166 lines, now 156). Severity tags `[ADVISORY]` dropped on every heuristic in the Gated Checklist (sentence-level + paragraph-level). The single `[BLOCKING]` survivor is the handoff "every applied rule traceable to a real problem" item — that one shapes behavior. Header rewritten to point at modes ("Load when Polish or Draft mode applies sentence-level rules"); `IMPLEMENT phase` framing dropped; "Walked in addition to SKILL.md §Three Concurrent Disciplines" cross-reference dropped; `## Reviewer verdict protocol` block dropped. Iron Law mention in the §How-To preamble rewritten to point at `SKILL.md §Preserve substance, polish prose`.
- `structure-checklist.md` → `structure.md` (was 143 lines, now 133). Same treatment: severity tags dropped on heuristic items; the `[BLOCKING]` handoff item ("structural change documented") survives; header rewritten ("Load when Draft mode runs, or when Polish mode is authorized to restructure — loading this file is the authority grant"); cross-reference and verdict-protocol blocks dropped; Iron Law mention rewritten.

**Files header-rewritten (substance unchanged):**
- `refactor-and-compile.md` (158 lines, was 166). Header rewritten to point at modes; `Three Concurrent Disciplines §Verify` cross-references replaced (one with the cross-references consistency file; the trailing "Walked in addition to ..." block deleted with one line folded back into the Compile checklist as the build-runs-clean BLOCKING item). Verdict-protocol block dropped. The §Refactor Iron-Law mention rewritten to `SKILL.md §Preserve substance, polish prose`. Severity tags on operationally meaningful items (preview matches, word-boundary, build-after) preserved per the plan ("substance unchanged").
- All 8 × `consistency/*.md`. Headers rewritten from "Load when a task involves..." to "Load when Review or Polish mode targets..." with the severity-marker note reframed as "shape reviewer output" instead of "fix to earn APPROVE" (the verdict ritual is workflow-owned). Severity-grading content from the dropped verdict-protocol blocks (math: "issues are almost always MAJOR/CRITICAL"; argument-logic: "main causal claims are CRITICAL/MAJOR"; code-paper: "main-spec mismatches are CRITICAL") folded into the headers — that content is behavior-shaping. The `## Reviewer verdict protocol` H2 dropped from all 8; the `## Output format` H2 preserved (load-bearing for reviewer output). `terminology.md` lost its stale `workflow.md §Mode (b)` cross-reference.
- `argument-logic.md` line 80 had a stale path `style-checklist.md` from the rename — updated in place to `style.md`. Iron-Law body mentions in `argument-logic.md`, `citations.md`, `math.md`, `terminology.md` (§Scope and Gated-Checklist prose) left untouched — the plan scopes consistency-file content as unchanged. **They now point at a section that no longer exists in `SKILL.md`; flagged below for Task 3 stale-reference sweep.**

**File trimmed:**
- `integration.md` (was 119 lines, now 42). Dropped: redundant Gates 3 (cross-reference integrity — restated of `consistency/cross-references.md`) and Gate 4 (per-dimension consistency reviewers — restated of `review.md` parallel-dispatch pattern); the data-analysis-touching section's prose detail (replaced with one-line pointer); the verdict-protocol block; the stale `workflow.md §Mode (b)` and `collaboration.md §What "voice preservation" means in practice` cross-references. Kept: build-on-merged-state (Gate 1), outline stability (Gate 2 here), voice-preserved three-hunk sample (Gate 3 here, was Gate 5), scope-respected hunk-trace (Gate 4 here, was Gate 6), data-analysis-touching pointer.

**Necessity-gate audit:**
- The reframed severity-marker headers (`Severity markers shape reviewer output: ...`) are behavior-shaping (tells the reviewer which markers go in the Output-format block); kept.
- The plan's "Walked in addition to" boilerplate was wrapper text pointing at SKILL.md content the reviewer no longer walks; deletion was unambiguous.
- The "walk top to bottom, never halt" verdict ritual is workflow-owned; deletion was unambiguous.

**Stale-reference flags for Task 3 / orchestrator:**
- `consistency/argument-logic.md:11`, `consistency/argument-logic.md:96`, `consistency/citations.md:78`, `consistency/math.md:11`, `consistency/math.md:83`, `consistency/terminology.md:32`, `consistency/terminology.md:67` — body prose mentions "Iron Law (main SKILL.md)" or "Iron Law §Scope". The new SKILL.md does not carry an Iron Law section (replaced by §Preserve substance, polish prose). The plan scopes consistency-file content as unchanged, so these were not rewritten in this task. They are stale-but-substantively-fine — the principle they invoke still holds, just under a different name. Recommend Task 3 sweep them as part of the broader stale-reference sweep, or leave for the orchestrator to adjudicate.

**Knowledge files NOT touched in this task:** None — all in-scope files are now lightened. Task 3 owns the deletion of `workflow.md`, `planning.md`, `collaboration.md` and the routing-row updates.

**REVISE round 1 fix (rename-residue):** `docs/writing-references/README.md` lines 9, 10, 11, 36, 37 carried stale `style-checklist.md` / `structure-checklist.md` paths — direct fallout from the Step 1 `git mv` that the Step 5 self-review's grep set did not target. Updated in place to `style.md` / `structure.md`; post-edit `grep` for the old names in the file returns empty.

## Task 3: Retire deprecated references and update routing

**Status:** IMPLEMENTED

**Deleted (`git rm`):**
- `skills/writing/references/workflow.md` (160 lines)
- `skills/writing/references/planning.md` (122 lines)
- `skills/writing/references/collaboration.md` (161 lines)

Content from these files was already absorbed in Task 1 (collaboration's "edit vs propose vs ask" matrix and `DO NOT EDIT` convention live in `polish.md`; workflow.md's mode descriptions are subsumed by the new mode files; planning.md's task-shape decision matrix is replaced by mode classification in `SKILL.md §Mode routing`).

**Doctrinal residue swept (in-place edits, substance unchanged — only the principle name changes):**
- `consistency/math.md:11`, `:83` — `Iron Law (main SKILL.md)` → `SKILL.md §Preserve substance, polish prose`.
- `consistency/citations.md:78` — `Iron Law` → `SKILL.md §Preserve substance, polish prose`.
- `consistency/terminology.md:32`, `:67` — `Iron Law` / `Iron Law §Scope` → `SKILL.md §Preserve substance, polish prose`.
- `consistency/argument-logic.md:11`, `:96` — `Iron Law (main SKILL.md)` → `SKILL.md §Preserve substance, polish prose`.

**Cross-skill stale-reference fix:**
- `skills/integration-workflow/SKILL.md:358` — the "Writing-vertical tasks" lighten-when bullet pointed at the now-deleted `writing/references/workflow.md` and used the four-standalone-modes framing. Rewritten to point at `skills/writing/SKILL.md` and the new Review / Polish / Draft taxonomy. Substance preserved (most writing work doesn't enter Integrate; only large work does, and the integration reviewer walks `writing/references/integration.md`).

**Routing rows refreshed:**
- `skills/using-superRA/SKILL.md:56` — Skill Inventory writing row reflects the new mode taxonomy and the preserve-substance-polish-prose principle.
- `skills/CATEGORIES.md:25` — writing row description updated; the pre-rename `style-checklist.md` / `structure-checklist.md` paths flagged by Task 2's last reviewer (and by this task's `Additionally:` line) were corrected to `style.md` / `structure.md`, and the file list now lists the three new mode references (`review.md`, `polish.md`, `draft.md`) ahead of the knowledge files. The Skill-Load Manifest add-on table (line 101) already routes `superRA:writing` correctly — no change there.
- `README.md:67` — Domain-skills writing-row description updated to the three-mode framing; preserved the per-dimension parallel-consistency-reviewer note (still in force after the redesign per the 2026-04-19 user decision).

**Verification (Step 4 grep checks):**
- `grep -rn 'references/workflow\.md\|references/planning\.md\|references/collaboration\.md' skills/writing/` — empty.
- `grep -rn 'writing/references/\(workflow\|planning\|collaboration\)' . --include='*.md'` — empty after excluding PLAN.md self-references (the file describes this task's work).
- `grep -rn 'Iron Law\|Three Concurrent Disciplines\|Preserve.Improve.Verify' skills/writing/` — empty. Surviving `§Preserve` hits all match the new `§Preserve substance, polish prose` principle name.
- `grep -n 'style-checklist\|structure-checklist' skills/CATEGORIES.md` — empty.

## Task 4: Add intent-comment discipline to `polish.md` / `draft.md` / `SKILL.md`

**Status:** IMPLEMENTED

**Files edited:**
- `skills/writing/references/polish.md` — added §Intent comments (26 lines) between §Edit-vs-propose-vs-ask and §Minimal-edit discipline. Covers: format per extension (`.tex` / `.md` / `.qmd`); pre-existing comments are the preservation target and outrank current wording on conflict; "may add inferred, must hedge" rule with the `(inferred)` qualifier; explicit persistence rule — `(inferred)` survives until the author ratifies (deletes the qualifier or rewrites the line) and the agent must not drop it itself, on a later polish pass, or because the prose now matches the inference; one LaTeX example.
- `skills/writing/references/draft.md` — added §Intent comments (15 lines) between §Workflow and §Workflow coupling. Covers: format per extension; intent written first as the drafting brief, prose fulfills it; comment ships with the prose; clarification that draft-authored intent does not carry `(inferred)` (later polish passes treat it as the preservation target); one LaTeX example.
- `skills/writing/SKILL.md` — added §Before you start item 4 (3 sentences, 1 line) summarizing the convention and pointing at the `polish.md` / `draft.md` sections.

**Convention consistency:** Format spec (`% intent: …` for `.tex`, `<!-- intent: … -->` for `.md` / `.qmd`) is identical across the three files. Position spec ("line immediately above the paragraph" / "line above") is consistent.

**`(inferred)` persistence (per `Additionally:` directive):** `polish.md` is explicit on three failure modes: agent does not drop the qualifier itself, does not drop it on a later polish pass, and does not drop it because the prose has been edited to match the inference. Ratification is defined as an author action (deleting `(inferred)` or rewriting the line).

**Necessity-gate audit (CLAUDE.md §Teach the Protocol):**
- Every line in the new §Intent comments sections names a non-default behavior or a failure mode the agent would otherwise produce. The convention itself is non-default; the preservation-target rule resolves conflict direction (prose vs intent) which an agent would otherwise have to guess; the hedge persistence rule blocks three plausible "agent rationalizes dropping the hedge" failure modes that would otherwise occur on subsequent polish passes.
- `SKILL.md` item 4 is a one-line summary + pointer (acceptable per CLAUDE.md "one-line echoes are tolerable when the alternative is forcing a redundant file load"); the operational details live only in the references.

## Task 5: Dogfood — three-mode verification

**Status:** Not started
