# Plan Stage Marker + Iterative Re-entry Mechanism

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all PLAN.md / RESULTS.md editing. Use `superRA:execution-workflow` to execute this plan. Skill changes — also load `superRA:writing-skills` per `CLAUDE.md` §Skill Changes. Steps use checkbox (`- [ ]`) syntax for tracking and cross-session handoff.

**Objective:** Give the superRA skills a unified iterative re-entry mechanism so a fresh agent picking up an in-flight project (a) can tell which workflow stage is active from `## Workflow Status` + per-task fields, (b) can re-enter execution/integration for small-scope additions without spinning up a new PLAN.md, and (c) main agents always have handoff-doc discipline loaded at session start.

**Methodology:** This is a **skill-editing task**, not a data-analysis task. No domain vertical (per `planning-workflow` Phase 1 routing table) covers it; the gap is flagged. The work follows the principles in `CLAUDE.md` (lean agents / rich references, DRY one-source-of-truth, do not weaken any of the four workflow principles).

Four coordinated changes, scoped to existing skills + one new reference file:

1. **`## Changing Plans` in `planning-workflow/SKILL.md`** — single protocol covering both in-session scope changes and cross-session re-entry; includes DAG cascade rule and full-drift-suite-always invariant. `handoff-doc/SKILL.md` keeps a one-line pointer only (doc structure stays in handoff-doc; plan-update choreography belongs in planning-workflow per DRY).
2. **`**Integration status:**` task-block field** added in `plan-anatomy.md` alongside `**Review status:**`. Project-level `## Workflow Status` boxes become a rollup over per-task states; orchestrator unchecks at re-entry.
3. **Workflow-skill updates.** `integration-workflow` spells out full-drift-suite-always + scoped refactor + doc-writer-full-reviewer-diff; `execution-workflow` Step 1 reads Integration status and proposes DAG transitive-downstream invalidation on re-entry; all four workflow skills rename the renamed section pointer.
4. **Main-agent reference consolidation.** Merge `session-bootstrap.md` + `main-agent-autonomy.md` → single `main-agent.md`; add `superRA:handoff-doc` to the main-agent default session-start load.

**Vertical-coverage gap:** `planning-workflow` Phase 1 has no entry for "skill editing" or "plugin development". Per the workflow rule, this is documented as a flag, not a blocker. We proceed without a domain skill — the discipline rules in `CLAUDE.md`'s Design Principles section take the role that the domain skill normally plays for data analysis.

**Affected files (file inventory, updated for this re-entry):**

| File | Change shape (this iteration) |
|---|---|
| `skills/handoff-doc/SKILL.md` | Remove `§Scope Changes and Re-entry` body; append one-line pointer under `§PLAN.md Is the Task Tracker` directing to `planning-workflow §Changing Plans` |
| `skills/handoff-doc/references/plan-anatomy.md` | Add `**Integration status:**` to task-block template + Field-by-Field; expand `## Workflow Status` description for re-entry semantics; retarget SKILL.md section pointer to `planning-workflow §Changing Plans` |
| `skills/planning-workflow/SKILL.md` | Author new `## Changing Plans` section (6-step protocol + DAG cascade + banned shortcuts, moved from handoff-doc) |
| `skills/execution-workflow/SKILL.md` | Step 1 sub-step 2a rewritten as ≤3 clean sentences covering both triggers; all pointers retarget to `planning-workflow §Changing Plans` |
| `skills/integration-workflow/SKILL.md` | Stage 1 always-full-drift-suite rule; Stage 2 scoped refactor; Step 3 doc-writer full + doc-reviewer diff (content landed in prior iteration); pointers retargeted to `planning-workflow §Changing Plans` |
| `skills/merge-workflow/SKILL.md` | No changes (no pointers to retarget) |
| `skills/using-superRA/SKILL.md` | Rewrite main-agent-load reference to new `main-agent.md`; add note that `handoff-doc` is a main-agent default load (subagent rows unaffected) |
| `skills/using-superRA/references/main-agent.md` (NEW) | Consolidated session-bootstrap + main-agent-autonomy + new handoff-doc-default directive |
| `skills/using-superRA/references/session-bootstrap.md` | DELETE |
| `skills/using-superRA/references/main-agent-autonomy.md` | DELETE |
| `RELEASE-NOTES.md` | New Unreleased entry describing iterative re-entry mechanism + main-agent handoff-doc default |
| `agents/implementer.md` / `agents/reviewer.md` | No change this iteration (Task 4 stays APPROVED) |

**Quality notes:**

- A **stash exists** (`stash@{0}` in the main repo) carrying an earlier version of these edits made against a much older base SHA. The intent is preserved; the patch itself does not apply (every target file has changed). Use the stash patch at `/tmp/stash.patch` as a content-spec reference, not a mechanical apply target.
- The `handoff-doc` "Six Principles" became "Four Principles" in the recent refactor — references must use "four principles" (not "six").
- Step 0b in `execution-workflow` now requires `PLAN.md` and `RESULTS.md` to exist, be tracked, and be clean before any task dispatch. This worktree starts with both committed, satisfying that gate.

**Output:** Edits to the files listed above; one new reference file (`main-agent.md`); two reference files deleted; new RELEASE-NOTES entry. README / CATEGORIES updates not needed (no skill added or renamed).

**Expected results:** A fresh agent running `cat PLAN.md` on any project using this updated skill set will see (a) the `## Workflow Status` rollup to know which stage is active and which boxes were unchecked at re-entry, (b) per-task `**Review status:**` + `**Integration status:**` fields to know which tasks remain APPROVED (no re-work needed) vs which were cleared under the DAG cascade, and (c) the `planning-workflow §Changing Plans` section covering both in-session scope changes and cross-session re-entry under a single 6-step protocol. Main agents have `superRA:handoff-doc` loaded at session start so the editing discipline is available without a separate invocation.

**Pipeline:** None — skill changes are static text edits. Verification is behavior-based per `CLAUDE.md` §Skill Changes ("Run the skill through a realistic session to confirm it triggers when it should").

---

## Decisions

> **User decision (2026-04-17):** Adopt per-task `**Integration status:**` field + iterative re-entry mechanism. Project-level `## Workflow Status` boxes become a rollup over per-task states; orchestrator unchecks them at re-entry and declares which tasks need re-work. Full drift-test suite always runs on every integration pass; only *authoring* new drift tests is scoped. Doc-writer always re-runs the whole doc; doc-reviewer reviews the diff. Orchestrator has authority over which tasks are "related" and which project-level boxes to uncheck — not the new task's implementer. Rename `handoff-doc §Mid-Session Scope Changes` → `§Scope Changes and Re-entry` so the single protocol subsumes both in-execution drift and post-integration additions. Favor updating existing task blocks over appending new ones.
> **Question asked:** How should small-scope additions after integration/merge (common in research, e.g., PR review surfacing an adjacent request) be recorded without fragmenting PLAN.md into a new plan per addition?
> **Rationale:** "Such situations happen in research very often. It's not worth a whole restart, but it's a new task." User explicitly rejected decision-tree taxonomies and chose orchestrator judgment + `AskUserQuestion` pause. The iterative model subsumes mid-session scope changes; one mechanism replaces two.

> **User decision (2026-04-17):** On re-entry for this PR: Tasks 1/2/3 have their `**Review status:**` cleared and their scope rewritten against the new design; Task 4 stays APPROVED (header-ownership bullet unaffected). Task 5 added for main-agent reference consolidation + `handoff-doc` default load. Project-level boxes `Plan approved` / `Execution complete` / `Refactored` / `Docs finalized` / `Merged` unchecked; `Drift tests created` unchecked pending full-suite re-run (no new invariants authored this iteration). PR #2 disposition (update in place vs stacked follow-up PR) deferred to merge-workflow Step 4. DAG cascade: no downstream-closure invalidations triggered this re-entry — Tasks 1, 2, 3 are independent edits to disjoint skill files; Task 5 targets files not referenced by Tasks 1–4; Task 4 did not depend on Tasks 1–3.
> **Question asked:** Which tasks carry APPROVED status forward, which get cleared, and which project-level boxes flip back on this re-entry?

> **User decision (2026-04-17):** Execute via subagent mode but bundle tasks together — do not dispatch one subagent per task. For easy implementer dispatches use sonnet; reviewers stay on the most-capable model (opus) per `execution-workflow` §Model Selection.
> **Question asked:** How should I execute the four-task plan — subagent-per-task, inline, or pause for plan review?
> **Rationale:** Tasks 1+2 (handoff-doc additions) form a coherent content-addition unit that other tasks reference; Tasks 3+4 (wire-up across workflow skills + agent files) form a coherent wire-up unit that depends on Bundle A landing first. Bundling reduces dispatch overhead while preserving the implementer-reviewer pair at the bundle boundary. Sonnet is sufficient for prose insertion at this scope.

**Bundling plan derived from the decision:**

- **Bundle A** = Task 1 + Task 2 — single implementer dispatch (sonnet), single reviewer dispatch (opus). Lands the two new `handoff-doc/SKILL.md` sections + the `plan-anatomy.md` template + Field-by-Field updates in one atomic commit set.
- **Bundle B** = Task 3 + Task 4 — single implementer dispatch (sonnet), single reviewer dispatch (opus). Lands the workflow-skill wire-ups + the agent header-ownership bullets. Depends on Bundle A being committed first because every wire-up references content that Bundle A creates.

Per-task `**Review status:**` fields still flip individually at the implementer's commit, and the reviewer issues one `APPROVE` / `REVISE` / `CONDITIONAL APPROVE` verdict per bundle.

> **User decision (2026-04-17):** Chose Option 2 (Push and open PR against `econ-adaption`) at `execution-workflow` Step 4. Run `integration-workflow` then `merge-workflow`; the final merge action is `git push -u origin feat/plan-stage-marker` + `gh pr create --base econ-adaption`, not a local merge.
> **Question asked:** Work complete and verified — what should I do with the branch (merge / PR / keep / discard)?

> **User decision (2026-04-17):** At integration-workflow Stage 1, fix the existing `structural-invariants.sh` principle-count test ONLY. Skip the three optional new invariants (assert new sections exist; assert milestone names appear; assert each workflow skill references Workflow Status).
> **Question asked:** Which drift-test invariants should this PR add — just the required test fix, or also new protective invariants for the new sections / milestones / wire-up?

> **User decision (2026-04-17):** Skip the RELEASE-NOTES one-block-vs-two convention call. Keep the current two-block structure as-is and proceed; only apply the two trivial accuracy fixes (sub-step-number citation, contradictory "unconditionally" wording) from the doc-reviewer's REVISE.
> **Question asked:** Should this PR's RELEASE-NOTES entry be a separate ## Unreleased block (current) or folded into the existing workflow-domain-split block?
> **Rationale:** "I don't care about release note for the moment" — orchestrator interprets as: do not spend cycles on the convention call; ship the entry as-written with only the accuracy fixes.

> **User decision (2026-04-17):** Push and open the PR now; user will handle the divergence with `econ-adaption` later. Skip integration-workflow Step 3 Sub-part C (PLAN.md disposition stays in worktree) and skip merge-workflow Step 1 (semantic-merge with main). Move directly to merge-workflow Step 4 PR push.
> **Question asked:** econ-adaption diverged 10+ commits (rescue/design-coherence-refactor merged) while this PR was in flight. Pause for user review, run semantic-merge, or abandon?
> **Rationale:** "Create the PR and I'll handle the divergence later." User accepts the divergence-resolution burden as a separate, post-PR-creation task. The PR is for design discussion and historical reference; the actual merge will be reconciled by the user manually against the new econ-adaption.

> **User decision (2026-04-17, re-entry):** Consolidate the change-plan protocol under DRY. The "how to change a plan" procedure currently lives in `handoff-doc §Scope Changes and Re-entry` but belongs in `planning-workflow` — handoff-doc owns doc *structure*, planning-workflow owns how to *create and update* plans. Rename to `§Changing Plans` and move the content there. When plans change (in-session scope change OR re-entry on a branch), agents re-invoke `planning-workflow §Changing Plans` and follow its checklist. `handoff-doc` keeps a one-line pointer only. `execution-workflow` Step 1's current paragraph conflates two triggers (re-entry detection + in-session change) into one dense sentence — rewrite as a clean pointer to the single procedure. **Per the prefer-updating rule** (`planning-workflow §Changing Plans` Step 3: "Prefer modifying existing task blocks over appending"), this re-entry is expressed as inline edits to Tasks 1 and 3 — not a new Task 6. Task 1's scope shifts from "author in handoff-doc" to "author in planning-workflow + reduce handoff-doc to pointer"; Task 3 absorbs the Step 1 paragraph rewrite + pointer retargets. Downstream closure: Task 1 fully re-implemented → both statuses cleared; Task 2 minor-edited (pointer flip only, field addition stays) → Integration status cleared; Task 3 fully re-implemented → both cleared; Task 4 untouched; Task 5 minor-edited (`main-agent.md` has a stale `§Scope Changes and Re-entry` reference) → Integration status cleared. Boxes flipped: `Execution complete`, `Refactored`, `Docs finalized`. `Drift tests created` stays checked pending full-suite re-run at integration.
> **Question asked:** The `§Scope Changes and Re-entry` wording is dense and the procedure is in the wrong skill — how should we restructure?
> **Rationale:** User observed the paragraph in `execution-workflow` Step 1 packages two distinct triggers (re-entry vs in-session change) confusingly, and that "how to handle tasks" is a planning-workflow concern, not a handoff-doc concern. Naming it `§Changing Plans` captures both triggers in plain language.

> **User decision (2026-04-17, post-rebase):** Merge `origin/main` into this branch via `superRA:semantic-merge` (Tier 3) to reconcile the design-coherence-refactor divergence. For the four conflicted files (`RELEASE-NOTES.md`, `skills/execution-workflow/SKILL.md`, `skills/planning-workflow/SKILL.md`, `tests/structural-invariants.sh`) take main's version in the mechanical commit; re-apply the branch's unique wire-ups (Workflow Status reads + box-flips + scope-change pointers) against main's new structure in the integration commit. Chose Option A (merge path, preserves history via merge commit) over Option B (hard rebase, discards 14 branch commits). Main's rewritten `tests/structural-invariants.sh` supersedes the branch's four-principles awk scoping fix — no re-application needed. Line-number citations in Task 1–4 sub-steps are stale against main's restructured handoff-doc / workflow skills; the implementations were committed at the old base SHA and remain valid in content, only the line numbers drifted.
> **Question asked:** Rebase this branch on main; keep unique and essential parts only. Merge vs hard rebase?

---

## Workflow Status

- [x] **Plan approved** — re-approved at re-entry (2026-04-17): iterative re-entry mechanism plan adopted; Tasks 1/2/3 rescoped, Task 5 added
- [ ] **Execution complete** — unchecked at re-entry (2026-04-17): Tasks 1 and 3 rescoped to consolidate change-plan protocol into `planning-workflow §Changing Plans`; Task 2/5 Integration cleared for pointer retarget; Task 4 preserved APPROVED
- [x] **Drift tests created** — re-run green (2026-04-17): no new invariants authored this iteration; full suite `bash tests/structural-invariants.sh` passes (0 FAIL) against the post-re-entry tree
- [ ] **Refactored** — unchecked at re-entry (2026-04-17): pending integration pass against the consolidated section location (planning-workflow §Changing Plans)
- [ ] **Docs finalized** — unchecked at re-entry (2026-04-17): pending Task 1+3 completion — RELEASE-NOTES + RESULTS.md need the §Changing Plans rename documented
- [ ] **Merged** — unchecked at re-entry: PR #2 update path to be decided at merge-workflow Step 4 (update in place vs stacked PR)

---

### Task 1: Author `## Changing Plans` in `planning-workflow/SKILL.md`; reduce handoff-doc to a pointer
**Depends on:** *(none)*
**Review status:** IMPLEMENTED
**Integration status:** *(cleared at re-entry)*

**Script:** `skills/planning-workflow/SKILL.md` (edit — new section), `skills/handoff-doc/SKILL.md` (edit — remove body, leave pointer)
**Input:** Current `handoff-doc/SKILL.md §Scope Changes and Re-entry` carries the 6-step protocol, DAG cascade paragraph, and banned-shortcuts bullets authored in prior iterations. Procedure belongs in planning-workflow (which owns how to create/update plans); handoff-doc owns doc *structure*, not plan-update choreography.
**Output:** New `planning-workflow §Changing Plans` section owning the full procedure; `handoff-doc §Scope Changes and Re-entry` reduced to a one-line pointer (or removed with pointer placed under `§PLAN.md Is the Task Tracker`).

- [x] **Step 1: Author `## Changing Plans` in `planning-workflow/SKILL.md`.** Added as top-level section after "Living Plan and Results Docs" and before "No Placeholders". One-paragraph framing names both triggers (in-session scope change + cross-session re-entry). Body carries the 6-step protocol, DAG cascade paragraph, and banned-shortcuts bullets verbatim from handoff-doc, with internal pointers retargeted from `references/plan-anatomy.md` (inside handoff-doc) to `handoff-doc/references/plan-anatomy.md` and §User Decisions Log references to `handoff-doc` §User Decisions Log. Living Plan paragraph's cross-ref retargeted to §Changing Plans below.

- [x] **Step 2: Reduced `handoff-doc/SKILL.md §Scope Changes and Re-entry` to a pointer.** Section body deleted, the heading removed. Under `§PLAN.md Is the Task Tracker`, appended one sentence: "When the plan itself changes — in-session scope change or cross-session re-entry — re-invoke `planning-workflow §Changing Plans` and follow its protocol."

- [x] **Step 3: Validate** — `grep -rn "Scope Changes and Re-entry" skills/` returns only the pre-existing pointers in execution-workflow, integration-workflow, plan-anatomy.md, main-agent.md, and using-superRA/SKILL.md (all retargeted in Task 3). `grep -n "## Changing Plans" skills/planning-workflow/SKILL.md` returns the new section. Content parity: all 6 protocol steps + DAG cascade + banned shortcuts present verbatim in planning-workflow. Voice matches existing planning-workflow sections.

---

### Task 2: Add `**Integration status:**` field + re-entry semantics to `plan-anatomy.md`
**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:** *(cleared at re-entry 2026-04-17 — pointer from `§Scope Changes and Re-entry` → `planning-workflow §Changing Plans` to be re-flipped in Task 3; field addition unaffected)*

**Script:** `skills/handoff-doc/references/plan-anatomy.md` (edit)
**Input:** Current `plan-anatomy.md` carrying the header template with `## Workflow Status` (lines 47–60, landed in a prior pass), task-block anatomy (lines 122+), and Field-by-Field notes.
**Output:** Same file carrying (a) `**Integration status:**` in the task-block template, (b) expanded `## Workflow Status` description noting derived-from-task-status + re-entry unchecks, (c) new Field-by-Field bullets, (d) updated pointer from §Mid-Session Scope Changes → §Scope Changes and Re-entry.

- [x] **Step 1: Add `**Integration status:**` line to the task-block template** (currently line 127) immediately below `**Review status:**`. Render as: `**Integration status:** *(set during integration — not filled at planning time)*`. Values: unset / IMPLEMENTED / REVISE / APPROVED.

- [x] **Step 2: Expand the `## Workflow Status` paragraph** in the header template (currently line 49) so it explains: project-level boxes are a rollup over per-task `**Review status:**` / `**Integration status:**`; the orchestrator unchecks them at re-entry when a scope change invalidates the milestone; the full drift-test suite must re-run green before rechecking `Drift tests created`. Point at `SKILL.md §Scope Changes and Re-entry` (renamed in Task 1).

- [x] **Step 3: Update the Field-by-Field section.** Edit the existing `**Review status:**` bullet to note that downstream tasks in the DAG closure of a modified task have their status cleared by default (orchestrator-documented exemptions in §Decisions). Add a new bullet for `**Integration status:**` with the same values vocabulary, set by the integration reviewer considering drift / refactor / doc coverage for that task's contribution, same cascade rule as `**Review status:**`. Update the existing `## Workflow Status checkboxes` bullet: change the pointer `SKILL.md §Mid-Session Scope Changes` → `SKILL.md §Scope Changes and Re-entry`.

- [x] **Step 4: Validate** — Fenced block count stays even (template not broken). Template line count changes by +1 (Integration status line). Pointer renames complete: `grep -n "Mid-Session Scope Changes" skills/handoff-doc/references/plan-anatomy.md` returns zero. Field-by-Field now has explicit cascade semantics for both Review and Integration status.

---

### Task 3: Retarget workflow-skill cross-references to `planning-workflow §Changing Plans` + rewrite the overloaded execution-workflow Step 1 paragraph
**Depends on:** Task 1 (new section must exist at the new location so pointers resolve), Task 2 (Integration-status field must exist in anatomy)
**Review status:** IMPLEMENTED
**Integration status:** *(cleared at re-entry)*

**Script:** `skills/execution-workflow/SKILL.md`, `skills/integration-workflow/SKILL.md`, `skills/handoff-doc/references/plan-anatomy.md`, `skills/using-superRA/references/main-agent.md`, `skills/using-superRA/SKILL.md` (edit). `skills/planning-workflow/SKILL.md` and `skills/merge-workflow/SKILL.md` carry no remaining pointers to retarget.
**Input:** Current cross-references to `handoff-doc §Scope Changes and Re-entry` across the listed files; the overloaded paragraph in `execution-workflow` Step 1 sub-step 2a that conflates re-entry detection with in-session scope change into one dense sentence; the substantive content additions to `integration-workflow` (always-full-drift-suite, refactor scope, doc-writer/reviewer scope) landed in the prior iteration and remain valid — only the pointer text changes.
**Output:** All pointers target `planning-workflow §Changing Plans`; `execution-workflow` Step 1 sub-step 2a rewritten as ≤3 short sentences that name both triggers clearly and hand off to the consolidated procedure; integration-workflow content additions preserved verbatim except for the pointer rename.

- [x] **Step 1: `execution-workflow/SKILL.md`** — two edits:
  - Rewrote Step 1 sub-step 2a to 3 sentences naming both triggers: "Also read per-task `**Review status:**` and `**Integration status:**` fields alongside `## Workflow Status`. If any project-level box is unchecked while some tasks are still APPROVED, the branch is in re-entry — invoke `planning-workflow §Changing Plans` before dispatching any implementer. The same skill covers in-session scope changes raised by the researcher mid-execution."
  - Stop-Points class (b) pointer retargeted from `handoff-doc §Scope Changes and Re-entry` → `planning-workflow §Changing Plans`.

- [x] **Step 2: `integration-workflow/SKILL.md`** — two pointer retargets, content preserved:
  - Line 70 (always-full-drift-suite rule): retargeted to `planning-workflow §Changing Plans`.
  - Line 136 (refactorer scope clause): same retarget.

- [x] **Step 3: `plan-anatomy.md`** — two retargets at lines 49 and 183 (`SKILL.md §Scope Changes and Re-entry` pointer in the Workflow Status paragraph and Field-by-Field bullet) updated to `planning-workflow §Changing Plans`.

- [x] **Step 4: `main-agent.md`** — line 52 updated so the handoff-doc default-load language names `planning-workflow §Changing Plans` as the protocol whose cross-references resolve through `handoff-doc`. Also retargeted the matching line in `using-superRA/SKILL.md` §Main-agent default load.

- [x] **Step 5: Validate** — `grep -rn "Scope Changes and Re-entry" skills/` returns zero hits. `grep -rn "Changing Plans" skills/` shows the planning-workflow section + retargeted pointers from execution-workflow (sub-step 2a + Stop-Points), integration-workflow (lines 70 + 136), plan-anatomy.md (lines 49 + 183), main-agent.md (line 52), using-superRA/SKILL.md (line 82), and handoff-doc/SKILL.md (Task 1 pointer). `execution-workflow` Step 1 sub-step 2a is 3 sentences naming both triggers. `bash tests/structural-invariants.sh` green.

---

### Task 4: Add header-ownership bullet to `agents/implementer.md` and `agents/reviewer.md`
**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:** APPROVED

**Script:** `agents/implementer.md`, `agents/reviewer.md` (edit)
**Input:** Both files' "What You Own, What You Don't" sections, specifically the "**You may NOT edit:**" lists (implementer line 95-100, reviewer line 118-122)
**Output:** Each list gains one bullet establishing the PLAN.md header (including `## Workflow Status` and `## Decisions`) as orchestrator-owned.

- [x] **Step 1: implementer.md** — inserted new bullet between "Any other task's content" and "The reviewer's prose" (now at line 99). Stash prose used verbatim: header is orchestrator-owned, cross-ref to `superRA:handoff-doc` references/plan-anatomy.md §Header ownership, status-return instruction.

- [x] **Step 2: reviewer.md** — inserted new bullet between "Any other task's content" and "Rewrite the prose..." (now at line 122). Adapted for reviewer voice: same header ownership cross-ref, "raise it in your status report; do not edit the header yourself."

- [x] **Step 3: Validate** — both bullets verified: sit naturally beside existing "may NOT edit" items, §Header ownership heading confirmed present in plan-anatomy.md (line 61), reviewer's ad-hoc stage exception unaffected. Cross-reference resolves.

---

### Task 5: Consolidate main-agent references into `main-agent.md` + make `handoff-doc` a main-agent default load
**Depends on:** Task 1 (the renamed `§Scope Changes and Re-entry` section is what the main agent needs handoff-doc loaded for)
**Review status:** APPROVED
**Integration status:** *(cleared at re-entry 2026-04-17 — `main-agent.md` line 52 carries a stale `§Scope Changes and Re-entry` reference retargeted in Task 3; consolidation + default-load decision unaffected)*

**Script:** `skills/using-superRA/references/main-agent.md` (new), `skills/using-superRA/references/session-bootstrap.md` (delete), `skills/using-superRA/references/main-agent-autonomy.md` (delete), `skills/using-superRA/SKILL.md` (edit)
**Input:** Current `references/session-bootstrap.md` (55 lines: cross-session detection + mandatory start actions + "load the autonomy contract" handoff). Current `references/main-agent-autonomy.md` (52 lines: three pause classes + proceed-without-asking + banned phrasings + one-question-at-a-time + log-before-act). Current `using-superRA/SKILL.md` Skill-Load Manifest preamble at lines 65–82 (notes `handoff-doc` is loaded on `documentation` and `planning-review` rows only).
**Output:** Single `references/main-agent.md` carrying cross-session detection + autonomy contract + a new directive establishing `superRA:handoff-doc` as a main-agent default skill load. The two prior files are deleted. Skill-Load Manifest preamble gets a note describing the main-agent default that sits alongside (and does not contradict) the subagent-only rows.

- [x] **Step 1: Create `skills/using-superRA/references/main-agent.md`** — consolidated both source files. Structure: (a) MANDATORY Session Start Actions, (b) Cross-Session Detection bash block + incomplete-plan handling + worktree handling, (c) Load the Handoff-Doc Skill (new paragraph), (d) The Three Pause Classes, (e) Proceed Without Asking, (f) Banned Phrasings, (g) One Question at a Time, (h) Log Before You Act. Top-of-file note present.

- [x] **Step 2: Deleted** `session-bootstrap.md` and `main-agent-autonomy.md` via `git rm`.

- [x] **Step 3: Updated `skills/using-superRA/SKILL.md`** — frontmatter rewritten to reference `main-agent.md`; Universal Principles #4 pointer updated; Skill-Load Manifest preamble extended with "Main-agent default load" paragraph for `superRA:handoff-doc`; stale pointers in `agent-orchestration/references/agent-teams.md` and `skills/CATEGORIES.md` also updated.

- [x] **Step 4: Validate** — `ls skills/using-superRA/references/` shows `main-agent.md` only. `grep -rn "session-bootstrap.md\|main-agent-autonomy.md" skills/` returns zero hits. `grep -n "handoff-doc" skills/using-superRA/SKILL.md` shows both the new main-agent-default note and the `documentation` / `planning-review` subagent rows. Content parity confirmed: all sections from both deleted files present in `main-agent.md`.

