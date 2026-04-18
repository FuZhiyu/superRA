# Plan Stage Marker + Mid-Session Scope-Change Protocol — Results

> Mirrors PLAN.md structure. Updated after each task with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-17 (Bundle B APPROVED)
**Status:** Execution complete — all 4 tasks APPROVED. Ready for integration-workflow.

---

## Task 1: Add `## PLAN.md Is the Task Tracker` and `## Mid-Session Scope Changes` to `handoff-doc/SKILL.md`

**Status:** Completed (APPROVED 2026-04-17, commit `ca27535`)

### Key Findings
- Two new top-level sections landed in `skills/handoff-doc/SKILL.md`:
  - `## PLAN.md Is the Task Tracker` (currently lines 65-81) — establishes PLAN.md as the source of truth for analysis tasks; TodoWrite as a transient view; precedence rule "if `TodoWrite` and `PLAN.md` ever disagree about the state of analysis work, `PLAN.md` is right by definition".
  - `## Mid-Session Scope Changes` (currently lines 112-146) — 6-step protocol (confirm → log → inline edit → roll back checkboxes → atomic commit → resume), distinguishes material vs not-material, names banned shortcuts.
- Both sections use the established skill voice (banned-patterns lists, "rule of thumb" callouts).
- The "Six Principles → Four Principles" terminology shift (from the recent refactor) is honored — no "six principles" wording introduced.

### Notes
- The two sections sit beside the four existing principles without duplicating them — the principles are abstract rules, the new sections are operational protocols.

---

## Task 2: Add `## Workflow Status` template to `plan-anatomy.md` + Header-ownership and Field-by-Field updates

**Status:** Completed (APPROVED 2026-04-17, commit `ca27535` after one REVISE round)

### Key Findings
- `## Workflow Status` block landed inside the header template at `skills/handoff-doc/references/plan-anatomy.md` — six checkboxes (Plan approved / Execution complete / Drift tests created / Refactored / Docs finalized / Merged), each tied to the workflow skill that owns its completion gate.
- `**Header ownership:**` was promoted to a real `### Header ownership` heading at line 61 (REVISE round 1 fix). Reason: Bundle B Task 4 cross-references `§Header ownership`, which only resolves to a real heading.
- New `### Decisions placement` prose-only section explains where the conditional `## Decisions` heading goes when the first decision arrives.
- New Field-by-Field bullet on `## Workflow Status` checkboxes specifies orchestrator-only flip authority.

### Notes
- Outer fenced ` ```markdown ` block in plan-anatomy.md remains syntactically valid (8 fences total, even count).
- The `## Decisions` example does NOT appear inside the outer template fence — it lives in prose form outside the fence to avoid the nested-fence trap that broke the prior session's first attempt.

### Reviewer Notes
- One REVISE round (Header-ownership heading promotion). Re-reviewed and APPROVED.

---

## Task 3: Wire box-flip and protocol pointers into the four workflow skills

**Status:** Completed (APPROVED 2026-04-17, commit `04cec53`)

### Key Findings
- All four workflow skills now reference `## Workflow Status` and flip the milestone they own:
  - `planning-workflow` Execution Handoff (line ~130) — flips `Plan approved` after researcher confirms.
  - `execution-workflow` Step 3 (line ~200) — flips `Execution complete` once all five reproducibility checks pass. (Was "six checks" in the stash — adapted to the current Step 3 structure.)
  - `integration-workflow` Stage 1 step 8 (new, line ~162) — flips `Drift tests created`.
  - `integration-workflow` Stage 2 step 6 (new, line ~232) — flips `Refactored`, with rollback note for post-merge re-entry.
  - `integration-workflow` Step 3 doc-reviewer (after APPROVE, line ~352) — flips `Docs finalized` before Sub-part C disposition.
  - `merge-workflow` Step 4 before-action (line ~134) — flips `Merged` on the analysis branch (conditional on PLAN.md still being present after disposition).
- `merge-workflow` Step 3 entry — unchecks `Refactored` on post-merge re-entry (conditional, same disposition guard).
- `§Mid-Session Scope Changes` pointers added to:
  - `planning-workflow` Living Plan section (distinguishes agent-discovered drift from researcher-initiated scope changes).
  - `execution-workflow` Stop-Points class (b) (rewritten "scope change" line to point at the new protocol).
- `execution-workflow` Step 1 expanded from 7 to 8 sub-steps to fold in three new concepts (PLAN.md as authoritative tracker, Read Workflow Status, TodoWrite as derived view) without undoing the recent refactor that added domain-skill loading and project-guidance walk-up.

### Notes
- All six milestone names appear in exactly one owning workflow skill — no milestone is flipped by a skill that does not own its completion criterion.
- Cross-references all resolve to real headings (verified by reviewer at the heading line numbers above).

---

## Task 4: Add header-ownership bullet to `agents/implementer.md` and `agents/reviewer.md`

**Status:** Completed (APPROVED 2026-04-17, commit `04cec53`)

### Key Findings
- `agents/implementer.md` line 99 — new bullet inside "**You may NOT edit:**" list naming the PLAN.md header (`## Workflow Status` and `## Decisions`) as orchestrator-owned. Implementer-voice: "report it in your status return; the orchestrator handles the doc edit."
- `agents/reviewer.md` line 122 — same bullet with reviewer-voice: "raise it in your status report; do not edit the header yourself."
- Both bullets cite `superRA:handoff-doc references/plan-anatomy.md §Header ownership` — the cross-reference resolves to the heading promoted in Task 2.

### Notes
- Bullets land inside the existing "may NOT edit" list (not adjacent to it). Existing items in the list are unchanged.
- Reviewer's "ad-hoc stage is report-only with no document updates" exception is preserved.

---

## Cross-Bundle Verification (post-Bundle B)

- All 4 PLAN.md tasks: APPROVED.
- Working tree: clean.
- No deferred MINOR items remain in any blockquote.
- All `§<heading>` cross-references introduced by Bundles A and B resolve to real headings.
- Six milestone-flip instructions across four workflow skills match the six checkboxes in `plan-anatomy.md` exactly.
- `## Workflow Status` checklist in this very PLAN.md is the first end-to-end usage of the new mechanism — a meta-test that the design is self-applicable.
