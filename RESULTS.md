# Plan Stage Marker + Iterative Re-entry Mechanism — Results

> Mirrors PLAN.md structure. Updated after each task with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-18 (all five tasks APPROVED; integration re-review APPROVED after the iterative-framing additions)
**Status:** All five tasks `**Review status:** APPROVED` and `**Integration status:** APPROVED`. Execution complete; drift tests green (`bash tests/structural-invariants.sh` → 0 FAIL); refactored; Stage 2 `RESULTS.md` maturation in progress; merge pending.

---

## Task 1: Author `## Changing Plans` in `planning-workflow/SKILL.md`; reduce handoff-doc to a pointer

**Status:** IMPLEMENTED (2026-04-18)

### Key Findings
- New `## Changing Plans` section authored in `skills/planning-workflow/SKILL.md` between "Living Plan and Results Docs" and "No Placeholders". Content moved verbatim from handoff-doc: two-trigger framing (mid-execution ping + post-integration scope addition), material / not-material bullet lists, 6-step protocol (confirm intent → log decision → edit PLAN.md inline → update `## Workflow Status` → commit atomically → resume), DAG cascade paragraph, and four banned-shortcuts bullets.
- Step 3's "Prefer modifying existing task blocks over appending" rule preserved verbatim as the first bullet of Step 3 — the load-bearing rule called out in the dispatch.
- Cross-references retargeted: inside planning-workflow the protocol now points at `handoff-doc/references/plan-anatomy.md` (was `references/plan-anatomy.md` when inside handoff-doc) and at `handoff-doc` §User Decisions Log.
- `handoff-doc/SKILL.md §Scope Changes and Re-entry` body deleted; the heading removed. A one-sentence pointer appended under `§PLAN.md Is the Task Tracker`: "When the plan itself changes — in-session scope change or cross-session re-entry — re-invoke `planning-workflow §Changing Plans` and follow its protocol."
- Living Plan paragraph's cross-ref retargeted from `handoff-doc §Scope Changes and Re-entry` → `§Changing Plans below` (local pointer since the section now lives in planning-workflow).
- Validation: `grep -n "## Changing Plans" skills/planning-workflow/SKILL.md` returns the new section; content parity verified for all 6 protocol steps + DAG cascade + banned shortcuts. Remaining `Scope Changes and Re-entry` hits across skills/ are the pre-existing pointers in execution-workflow, integration-workflow, plan-anatomy.md, main-agent.md, and using-superRA/SKILL.md — retargeted in Task 3.

---

## Task 2: Add `**Integration status:**` field + re-entry semantics to `plan-anatomy.md`

**Status:** APPROVED (Bundle A, 2026-04-17)

### Key Findings
- `**Integration status:** *(set during integration — not filled at planning time)*` added to task-block template immediately below `**Review status:**`.
- `## Workflow Status` description in header template expanded: boxes are now described as a rollup over per-task `**Review status:**` / `**Integration status:**`; re-entry unchecks by orchestrator judgment; full drift-test suite required before rechecking `Drift tests created`; pointer updated to `SKILL.md §Scope Changes and Re-entry`.
- Field-by-Field updated: `**Review status:**` bullet gains DAG cascade language (downstream closure cleared by default, orchestrator exemptions in §Decisions). New `**Integration status:**` bullet with same values vocabulary and same cascade rule. `## Workflow Status checkboxes` bullet pointer renamed from `§Mid-Session Scope Changes` → `§Scope Changes and Re-entry`; rollup logic described.
- Validation: fenced block count still 12 (even, template balanced); `grep "Mid-Session Scope Changes" skills/handoff-doc/references/plan-anatomy.md` → zero hits.

---

## Task 3: Retarget workflow-skill cross-references to `planning-workflow §Changing Plans` + rewrite execution-workflow Step 1 sub-step 2a

**Status:** IMPLEMENTED (2026-04-18)

### Key Findings
- `execution-workflow/SKILL.md`: Step 1 sub-step 2a rewritten to 3 short sentences that cleanly separate the two triggers — (a) re-entry detection via unchecked project-level box + lingering APPROVED task statuses, (b) in-session researcher-raised scope change — and hand off to `planning-workflow §Changing Plans` for both. Stop-Points class (b) pointer retargeted from `handoff-doc §Scope Changes and Re-entry` → `planning-workflow §Changing Plans`.
- `integration-workflow/SKILL.md`: Two pointer retargets, content otherwise preserved. Line 70 (always-full-drift-suite blockquote inside Stage 1) and line 136 (Stage 2 refactorer-scope clause) both now point at `planning-workflow §Changing Plans`.
- `handoff-doc/references/plan-anatomy.md`: Two retargets — Workflow Status paragraph (line 49) and Field-by-Field `## Workflow Status checkboxes` bullet (line 183) — both renamed from `SKILL.md §Scope Changes and Re-entry` to `planning-workflow §Changing Plans`.
- `using-superRA/references/main-agent.md`: Line 52 "Load the Handoff-Doc Skill" paragraph rewritten so the handoff-doc main-agent default load is justified by (a) editing discipline and (b) resolving the `planning-workflow §Changing Plans` protocol's cross-references into handoff-doc (User Decisions Log format, plan-anatomy templates).
- `using-superRA/SKILL.md`: Main-agent default-load paragraph (line 82) retargeted to match main-agent.md — the same justification rewrite.

### Validation
- `grep -rn "Scope Changes and Re-entry" skills/` → 0 hits.
- `grep -rn "Changing Plans" skills/` → planning-workflow §Changing Plans section + retargeted pointers from all files listed above + handoff-doc/SKILL.md Task 1 pointer.
- Execution-workflow Step 1 sub-step 2a is 3 sentences naming both triggers.
- `bash tests/structural-invariants.sh` → reported below in status return.

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

## Task 5: Consolidate main-agent references into `main-agent.md` + make `handoff-doc` a main-agent default load

**Status:** APPROVED (Bundle B, 2026-04-17)

### Key Findings
- Created `skills/using-superRA/references/main-agent.md` consolidating both `session-bootstrap.md` and `main-agent-autonomy.md`. Structure: MANDATORY Session Start Actions → Cross-Session Detection (bash block + incomplete-plan handling + worktree handling) → Load the Handoff-Doc Skill (new) → The Three Pause Classes → Proceed Without Asking → Banned Phrasings → One Question at a Time → Log Before You Act.
- New "Load the Handoff-Doc Skill" paragraph directs main agent to load `superRA:handoff-doc` at session start so editing discipline and `§Scope Changes and Re-entry` are available before touching PLAN.md.
- `session-bootstrap.md` and `main-agent-autonomy.md` deleted via `git rm`.
- `using-superRA/SKILL.md` updated: frontmatter pointer, Universal Principles #4 pointer, and Skill-Load Manifest "Main-agent default load" paragraph all reference the new `main-agent.md`. Subagent-side rows in the manifest table unchanged.
- Stale pointers in `agent-orchestration/references/agent-teams.md` and `skills/CATEGORIES.md` updated to `main-agent.md`.

### Validation
- `ls skills/using-superRA/references/` → `main-agent.md` present; old files absent.
- `grep -rn "session-bootstrap.md\|main-agent-autonomy.md" skills/` → zero hits.
- `grep -n "handoff-doc" skills/using-superRA/SKILL.md` → new main-agent-default note + `documentation` / `planning-review` subagent rows both present.
- Content parity confirmed: all sections from both source files present in `main-agent.md`, no content dropped.

---

## Cross-Bundle Verification (post-Bundle B)

- Bundle A (Tasks 1+2): APPROVED.
- Bundle B (Tasks 3+5): APPROVED (2026-04-17).
- Task 4: APPROVED (unaffected by re-entry).
- No deferred MINOR items in any blockquote.
- All `§<heading>` cross-references introduced by Bundles A and B resolve to real headings.
- `## Workflow Status` checklist in this PLAN.md is the first end-to-end usage of the new mechanism — a meta-test that the design is self-applicable.
