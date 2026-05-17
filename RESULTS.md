# REVIEW.md → PLAN.md Two-Stage Lifecycle — Results

> Mirrors PLAN.md structure. Updated after each task with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-05-16 (planning)
**Status:** In Progress

---

## Task 1: Rewrite long-form-review.md for two-stage REVIEW.md → PLAN.md flow

**Status:** IMPLEMENTED

**File edited:** `skills/writing/references/long-form-review.md` (full rewrite of `## Doc convention`, `## Dispatch convention`; new sections added)

**Key structural changes:**
- `## Doc convention` rewritten for two-stage lifecycle: Stage-1 REVIEW.md (per-aspect task blocks with global F-IDs and `**User feedback:**` field) → Stage-2 PLAN.md (via four-move orchestrator rewrite in one atomic commit). Standalone-only rename rule stated explicitly.
- `## Workflow Status` templates for both stages: slim three-box rollup in Stage 1; standard six-box PLAN.md rollup (with N/A notes for Drift tests / Integrated / Docs finalized) at Stage 2.
- Stage-2 task granularity rule: 1 authorial = 1 task; mechanical/conventional batch by issue class; Final Verify task.
- `## Implementer / reviewer interaction walk-through` section traces all roles through both stages against canonical agent specs — no adapter prose needed.
- Global F-ID rule: one rule in long-form-review.md covers all eight `consistency/<dim>.md` outputs; no per-file edits needed.
- Existing material preserved: multi-perspective deep mode, no reviewer-of-reviewer pass (optional final-summary reviewer only), parallel-dispatch from agent-orchestration, final summary block.

**DRY/Necessity check:** One wrapper sentence removed ("Each stage uses canonical agent protocols without adapter prose"). All remaining instruction lines shape behavior an agent would not produce on its own.

## Task 2: Update polish.md §C and SKILL.md lifecycle ladder sentence

**Status:** Not started

## Task 3: Update writing/CLAUDE.md contributor notes

**Status:** Not started

## Task 4: Verification sweep

**Status:** Not started
