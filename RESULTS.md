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

**Status:** Not started

## Task 3: Retire deprecated references and update routing

**Status:** Not started

## Task 4: Add intent-comment discipline to `polish.md` / `draft.md` / `SKILL.md`

**Status:** Not started

## Task 5: Dogfood — three-mode verification

**Status:** Not started
