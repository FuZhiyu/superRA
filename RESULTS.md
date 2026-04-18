# Plan Stage Marker + Iterative Re-entry Mechanism — Results

> Mirrors PLAN.md structure. Updated after each task with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-17 (Bundle B IMPLEMENTED)
**Status:** Bundle A (Tasks 1+2) APPROVED; Bundle B (Tasks 3+5) implemented; awaiting reviewer.

---

## Task 1: Reframe `## Mid-Session Scope Changes` → `## Scope Changes and Re-entry` in `handoff-doc/SKILL.md`

**Status:** IMPLEMENTED (Bundle A, awaiting reviewer)

### Key Findings
- `## Mid-Session Scope Changes` renamed to `## Scope Changes and Re-entry` in `skills/handoff-doc/SKILL.md`.
- Preamble rewritten to frame the protocol as covering both (a) mid-execution researcher pings and (b) post-integration / post-merge scope additions (PR-review requests, adjacent features, follow-on ideas).
- "Material" bullets extended with explicit post-integration case.
- Protocol Step 3 gains "prefer modifying existing tasks over appending" bullet.
- Protocol Step 4 gains orchestrator-judgment language: orchestrator declares which boxes and why; per-task status clearing rules for fully-re-implemented / untouched / minor-edited tasks.
- Protocol Step 6 gains full-drift-suite-always rule and doc-writer/doc-reviewer scope rule.
- New DAG cascade paragraph added after protocol: transitive closure clearing, exemption mechanism via §Decisions blockquote, cross-reference to `plan-anatomy.md §Field-by-Field`.
- Banned shortcuts extended: one new bullet forbidding subset drift-test runs on re-entry.
- Validation: `grep "Mid-Session Scope Changes" skills/handoff-doc/` → zero hits; all cross-references (§User Decisions Log, §PLAN.md Is the Task Tracker, `plan-anatomy.md`) resolve; four-principles framing preserved.

---

## Task 2: Add `**Integration status:**` field + re-entry semantics to `plan-anatomy.md`

**Status:** IMPLEMENTED (Bundle A, awaiting reviewer)

### Key Findings
- `**Integration status:** *(set during integration — not filled at planning time)*` added to task-block template immediately below `**Review status:**`.
- `## Workflow Status` description in header template expanded: boxes are now described as a rollup over per-task `**Review status:**` / `**Integration status:**`; re-entry unchecks by orchestrator judgment; full drift-test suite required before rechecking `Drift tests created`; pointer updated to `SKILL.md §Scope Changes and Re-entry`.
- Field-by-Field updated: `**Review status:**` bullet gains DAG cascade language (downstream closure cleared by default, orchestrator exemptions in §Decisions). New `**Integration status:**` bullet with same values vocabulary and same cascade rule. `## Workflow Status checkboxes` bullet pointer renamed from `§Mid-Session Scope Changes` → `§Scope Changes and Re-entry`; rollup logic described.
- Validation: fenced block count still 12 (even, template balanced); `grep "Mid-Session Scope Changes" skills/handoff-doc/references/plan-anatomy.md` → zero hits.

---

## Task 3: Update the four workflow skills for iterative re-entry + full drift-suite always + renamed section pointer

**Status:** IMPLEMENTED (Bundle B)

### Key Findings
- `planning-workflow/SKILL.md`: Living Plan section pointer renamed `§Mid-Session Scope Changes` → `§Scope Changes and Re-entry`.
- `execution-workflow/SKILL.md`: Three edits — (1) Stop-Points class (b) pointer renamed; (2) New sub-step 2a after "Read Workflow Status" adds per-task `**Review status:**` + `**Integration status:**` read and DAG cascade detection on re-entry, cross-referencing `handoff-doc §Scope Changes and Re-entry` for exemption protocol; (3) Autonomy section reference updated from `main-agent-autonomy.md` to `main-agent.md`.
- `integration-workflow/SKILL.md`: Always-full-drift-suite rule added before Stage 1 test-creator dispatch; `Drift tests created` box-flip updated to key on all tasks `**Integration status:** APPROVED`; Stage 2 refactorer scope clause added; `Refactored` box-flip updated to rollup; doc-writer always-full-doc rule and doc-reviewer diff-focus rule added to Step 3; `Docs finalized` box-flip updated to rollup. Autonomy reference updated.
- `merge-workflow/SKILL.md`: No `§Mid-Session Scope Changes` pointers existed in file; no changes needed.
- Also updated stale pointer in `agent-orchestration/references/agent-teams.md` and `skills/CATEGORIES.md` (found during Task 5 validation; Task 3's scope).

### Validation
- `grep -rn "Mid-Session Scope Changes" skills/` → zero hits. Integration-workflow always-full-drift-suite rule present. Execution-workflow step 2a references `**Integration status:**` and DAG cascade cross-ref. No Principle 3 violations.

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

**Status:** IMPLEMENTED (Bundle B)

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
- Bundle B (Tasks 3+5): IMPLEMENTED, awaiting reviewer.
- Task 4: APPROVED (unaffected by re-entry).
- No deferred MINOR items in any blockquote.
- All `§<heading>` cross-references introduced by Bundles A and B resolve to real headings.
- `## Workflow Status` checklist in this PLAN.md is the first end-to-end usage of the new mechanism — a meta-test that the design is self-applicable.
