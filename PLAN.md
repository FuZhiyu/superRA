# Plan Stage Marker + Mid-Session Scope-Change Protocol

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all PLAN.md / RESULTS.md editing. Use `superRA:execution-workflow` to execute this plan. Skill changes — also load `superRA:writing-skills` per `CLAUDE.md` §Skill Changes. Steps use checkbox (`- [ ]`) syntax for tracking and cross-session handoff.

**Objective:** Add three coordinated mechanisms to the superRA skills so a fresh agent picking up an in-flight project can tell exactly which workflow stage it is at, and so researcher-initiated scope changes mid-session land in `PLAN.md` instead of chat or TodoWrite.

**Methodology:** This is a **skill-editing task**, not a data-analysis task. No domain vertical (per `planning-workflow` Phase 1 routing table) covers it; the gap is flagged. The work follows the principles in `CLAUDE.md` (lean agents / rich references, DRY one-source-of-truth, do not weaken any of the four workflow principles). Three coordinated additions, scoped to existing skills — no new skill files.

1. **`## PLAN.md Is the Task Tracker`** — a new top-level section in `handoff-doc/SKILL.md` establishing PLAN.md as the source of truth for analysis tasks, with TodoWrite as a transient view. Cross-referenced from `execution-workflow` Step 1.
2. **`## Mid-Session Scope Changes`** — a new top-level section in `handoff-doc/SKILL.md` defining a 6-step protocol for researcher-initiated scope changes (confirm → log → inline edit → roll back checkboxes → atomic commit → resume). Cross-referenced from `execution-workflow` stop-points class (b) and `planning-workflow` Living Plan section.
3. **`## Workflow Status` checklist** — a new section in `handoff-doc/references/plan-anatomy.md` carrying six irreversible-milestone checkboxes (`Plan approved`, `Execution complete`, `Drift tests created`, `Refactored`, `Docs finalized`, `Merged`). Each box is flipped by the workflow skill that owns the corresponding completion gate; subagents may not flip boxes (header is orchestrator-owned).

**Vertical-coverage gap:** `planning-workflow` Phase 1 has no entry for "skill editing" or "plugin development". Per the workflow rule, this is documented as a flag, not a blocker. We proceed without a domain skill — the discipline rules in `CLAUDE.md`'s Design Principles section take the role that the domain skill normally plays for data analysis.

**Affected files (file inventory):**

| File | Current size | Change shape |
|---|---|---|
| `skills/handoff-doc/SKILL.md` | 119 lines | +2 new top-level sections (~75 lines added) |
| `skills/handoff-doc/references/plan-anatomy.md` | 117 lines | Insert `## Workflow Status` block in template + extend Header-ownership note + add Field-by-Field bullet |
| `skills/execution-workflow/SKILL.md` | 333 lines | Reframe Step 1 (TodoWrite as derived view + read Workflow Status); add Step 3 box-flip; rewrite stop-points class (b) phrasing |
| `skills/integration-workflow/SKILL.md` | 495 lines | Three box-flip lines (end of Stage 1 / Stage 2 / after doc-reviewer APPROVE) |
| `skills/merge-workflow/SKILL.md` | 237 lines | Step 3 entry: uncheck Refactored on post-merge re-entry; Step 4 before-action: check Merged |
| `skills/planning-workflow/SKILL.md` | 142 lines | Living Plan section: pointer to Mid-Session Scope Changes; Execution Handoff: Plan approved box-flip |
| `agents/implementer.md` | ~190 lines | One bullet in "may NOT edit" list (Workflow Status + Decisions are orchestrator-owned) |
| `agents/reviewer.md` | ~170 lines | One bullet in "may NOT edit" list (same) |

**Quality notes:**

- A **stash exists** (`stash@{0}` in the main repo) carrying an earlier version of these edits made against a much older base SHA. The intent is preserved; the patch itself does not apply (every target file has changed). Use the stash patch at `/tmp/stash.patch` as a content-spec reference, not a mechanical apply target.
- The `handoff-doc` "Six Principles" became "Four Principles" in the recent refactor — references must use "four principles" (not "six").
- Step 0b in `execution-workflow` now requires `PLAN.md` and `RESULTS.md` to exist, be tracked, and be clean before any task dispatch. This worktree starts with both committed, satisfying that gate.

**Output:** Edits to the 8 files listed above. No new files. README/RELEASE-NOTES/CATEGORIES updates not needed (no skill added or renamed; only sections inside existing skills).

**Expected results:** A fresh agent running `cat PLAN.md` on any project using this updated skill set will see the `## Workflow Status` checklist and immediately know which stage the project is at, without needing to grep commits or read every task block. The `Mid-Session Scope Changes` protocol gives the agent a deterministic flow when the researcher requests a new task mid-execution. The `PLAN.md Is the Task Tracker` rule prevents drift between TodoWrite and the persistent doc.

**Pipeline:** None — skill changes are static text edits. Verification is behavior-based per `CLAUDE.md` §Skill Changes ("Run the skill through a realistic session to confirm it triggers when it should").

---

## Decisions

> **User decision (2026-04-17):** Execute via subagent mode but bundle tasks together — do not dispatch one subagent per task. For easy implementer dispatches use sonnet; reviewers stay on the most-capable model (opus) per `execution-workflow` §Model Selection.
> **Question asked:** How should I execute the four-task plan — subagent-per-task, inline, or pause for plan review?
> **Rationale:** Tasks 1+2 (handoff-doc additions) form a coherent content-addition unit that other tasks reference; Tasks 3+4 (wire-up across workflow skills + agent files) form a coherent wire-up unit that depends on Bundle A landing first. Bundling reduces dispatch overhead while preserving the implementer-reviewer pair at the bundle boundary. Sonnet is sufficient for prose insertion at this scope.

**Bundling plan derived from the decision:**

- **Bundle A** = Task 1 + Task 2 — single implementer dispatch (sonnet), single reviewer dispatch (opus). Lands the two new `handoff-doc/SKILL.md` sections + the `plan-anatomy.md` template + Field-by-Field updates in one atomic commit set.
- **Bundle B** = Task 3 + Task 4 — single implementer dispatch (sonnet), single reviewer dispatch (opus). Lands the workflow-skill wire-ups + the agent header-ownership bullets. Depends on Bundle A being committed first because every wire-up references content that Bundle A creates.

Per-task `**Review status:**` fields still flip individually at the implementer's commit, and the reviewer issues one `APPROVE` / `REVISE` / `CONDITIONAL APPROVE` verdict per bundle.

---

## Workflow Status

- [ ] **Plan approved** — researcher signed off on this PLAN (planning-workflow Phase 4)
- [ ] **Execution complete** — all tasks `APPROVED`, no remaining REVISE / CONDITIONAL APPROVE (execution-workflow Step 3)
- [ ] **Drift tests created** — N/A for a skill-editing task; replaced by `RELEASE-NOTES.md` entry + structural-invariants run before merge (integration-workflow Stage 1 equivalent)
- [ ] **Refactored** — integration-reviewer `APPROVED` on the final state (integration-workflow Stage 2)
- [ ] **Docs finalized** — RELEASE-NOTES.md updated, README skill summaries audited, doc-reviewer `APPROVED` (integration-workflow Step 3)
- [ ] **Merged** — branch merged to econ-adaption (or PR opened against it) (merge-workflow Step 4)

---

### Task 1: Add `## PLAN.md Is the Task Tracker` and `## Mid-Session Scope Changes` to `handoff-doc/SKILL.md`
**Review status:** APPROVED

**Script:** `skills/handoff-doc/SKILL.md` (edit)
**Input:** Current `handoff-doc/SKILL.md` (119 lines, four-principles structure)
**Output:** Same file with two new top-level sections inserted

- [x] **Step 1: Insert `## PLAN.md Is the Task Tracker` section** between `## At-a-Glance Structure` and `## Inline-Edit Rule` (now lines 65-81). Section inserted verbatim from stash patch prose. Section establishes PLAN.md as the primary task tracker, defines TodoWrite's transient role, lists banned patterns, and gives the precedence rule.

- [x] **Step 2: Insert `## Mid-Session Scope Changes` section** between `## User Decisions Log` and `## What Counts as Stale` (now lines 112-146). Section inserted verbatim from stash patch prose. Covers material vs. not-material distinction, 6-step protocol with inline-edit rules, and banned shortcuts. Cross-references `execution-workflow` Stop-Points class (b) and §User Decisions Log.

- [x] **Step 3: Validate** — Section order confirmed: At-a-Glance Structure → PLAN.md Is the Task Tracker → Inline-Edit Rule → User Decisions Log → Mid-Session Scope Changes → What Counts as Stale. `grep "six principles"` returns nothing. Cross-references to §User Decisions Log and §PLAN.md Is the Task Tracker are valid (both exist). Voice matches existing sections.

---

### Task 2: Add `## Workflow Status` template to `plan-anatomy.md` + Header-ownership and Field-by-Field updates
**Review status:** APPROVED

**Script:** `skills/handoff-doc/references/plan-anatomy.md` (edit)
**Input:** Current `plan-anatomy.md` (117 lines, header template + task block anatomy + field notes)
**Output:** Same file with `## Workflow Status` checklist inside the header template, expanded Header-ownership note, new Field-by-Field bullet on `## Workflow Status`

- [x] **Step 1: Insert `## Workflow Status` block inside the fenced header template** between `**Pipeline:**` and the closing `---` (now lines 47-57). One-paragraph description + 6-bullet checklist (Plan approved, Execution complete, Drift tests created, Refactored, Docs finalized, Merged). Outer ` ```markdown ` template block still closes cleanly — awk fence count returns 8 (even). No nested fences; checklist is plain markdown inside the outer fence.

- [x] **Step 2: Update the Header-ownership note** (now line 61) to mention `## Workflow Status` and (when present) `## Decisions` as orchestrator-owned. Added `### Decisions placement` prose below the note pointing readers at `SKILL.md §User Decisions Log` for format — no Decisions example embedded inside the outer fenced block.

- [x] **Step 3: Add a Field-by-Field bullet** for `## Workflow Status` checkboxes after the Review-notes bullet (now line 125). Bullet states orchestrator-only flip, same-commit requirement, and uncheck-on-scope-change with pointer to `SKILL.md §Mid-Session Scope Changes`.

- [x] **Step 4: Validate** — Fenced block count = 8 (even, no orphan fences). Milestone names in template (Plan approved / Execution complete / Drift tests created / Refactored / Docs finalized / Merged) match the six names described in Task 3's wire-up targets. Header-ownership note names three orchestrator-owned areas (header proper, Workflow Status, Decisions). No Decisions literal embedded inside fenced template.

---

### Task 3: Wire box-flip and protocol pointers into the four workflow skills
**Review status:** IMPLEMENTED

**Script:** `skills/planning-workflow/SKILL.md`, `skills/execution-workflow/SKILL.md`, `skills/integration-workflow/SKILL.md`, `skills/merge-workflow/SKILL.md` (edit)
**Input:** Current state of each (line counts in file inventory above)
**Output:** Each workflow skill carries: (a) a thin pointer to `handoff-doc` §Mid-Session Scope Changes where its choreography touches researcher-initiated drift; (b) a one-liner that flips the relevant `## Workflow Status` box at the corresponding completion gate.

- [x] **Step 1: `planning-workflow/SKILL.md`** — two edits completed:
  - Inserted distinguishing paragraph after "The plan is NOT a static spec." (Living Plan section, now at line 87) distinguishing agent-discovered drift from researcher-initiated scope changes, with pointer to `handoff-doc` §Mid-Session Scope Changes.
  - Rewrote "After finalizing the plan, commit it" (Execution Handoff section) to include `Plan approved` box-flip with cross-ref to `superRA:handoff-doc` references/plan-anatomy.md.

- [x] **Step 2: `execution-workflow/SKILL.md`** — three edits completed:
  - Step 1 expanded from 7 to 8 sub-steps: sub-step 1 now includes cross-ref to `handoff-doc §PLAN.md Is the Task Tracker`; new sub-step 2 added "Read `## Workflow Status`"; old sub-step 7 (TodoWrite) replaced with derived-view framing per `handoff-doc §Mid-Session Scope Changes`; old sub-steps 2-6 renumbered to 3-7 (domain-skill loading, guidance walk-up, conflict check all preserved).
  - Step 3: inserted "Once all five checks pass" paragraph with `Execution complete` box-flip after "If any check fails" line.
  - Stop-Points class (b): scope-change entry bolded and extended with pointer to `handoff-doc` §Mid-Session Scope Changes.

- [x] **Step 3: `integration-workflow/SKILL.md`** — three box-flip insertions completed:
  - Stage 1 step 8 added after "Commit test files": flip `Drift tests created` box, commit before Stage 2.
  - Stage 2 step 6 added after "Final commit": flip `Refactored` box with uncheck caveat for post-merge re-entry.
  - "On doc-reviewer APPROVE" paragraph inserted after REVISE adjudication line, before Sub-part C: flip `Docs finalized` box with explanation that flip belongs here not at disposition.

- [x] **Step 4: `merge-workflow/SKILL.md`** — two edits completed:
  - Step 3: "On entry" note inserted after "When drift tests fail..." line — unchecks `Refactored` if PLAN.md present; references integration-workflow Stage 2 step 6 for re-check.
  - Step 4: "Before executing the merge action" note inserted after "Once Step 2 returns clean" — checks `Merged` box on analysis branch if PLAN.md present; explains skip condition for Options 2/3 disposition.

- [x] **Step 5: Validate** — all six milestones verified in correct workflow skills (Plan approved → planning; Execution complete → execution; Drift tests created + Refactored + Docs finalized → integration; Merged → merge). All `§Mid-Session Scope Changes` references resolved. No Principle 3 violations (every flip at natural completion gate). Self-check commands passed (see dispatch self-check notes).

---

### Task 4: Add header-ownership bullet to `agents/implementer.md` and `agents/reviewer.md`
**Review status:** IMPLEMENTED

**Script:** `agents/implementer.md`, `agents/reviewer.md` (edit)
**Input:** Both files' "What You Own, What You Don't" sections, specifically the "**You may NOT edit:**" lists (implementer line 95-100, reviewer line 118-122)
**Output:** Each list gains one bullet establishing the PLAN.md header (including `## Workflow Status` and `## Decisions`) as orchestrator-owned.

- [x] **Step 1: implementer.md** — inserted new bullet between "Any other task's content" and "The reviewer's prose" (now at line 99). Stash prose used verbatim: header is orchestrator-owned, cross-ref to `superRA:handoff-doc` references/plan-anatomy.md §Header ownership, status-return instruction.

- [x] **Step 2: reviewer.md** — inserted new bullet between "Any other task's content" and "Rewrite the prose..." (now at line 122). Adapted for reviewer voice: same header ownership cross-ref, "raise it in your status report; do not edit the header yourself."

- [x] **Step 3: Validate** — both bullets verified: sit naturally beside existing "may NOT edit" items, §Header ownership heading confirmed present in plan-anatomy.md (line 61), reviewer's ad-hoc stage exception unaffected. Cross-reference resolves.
