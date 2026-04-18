# Plan Stage Marker + Iterative Re-entry Mechanism

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all PLAN.md / RESULTS.md editing. Use `superRA:execution-workflow` to execute this plan. Skill changes — also load `superRA:writing-skills` per `CLAUDE.md` §Skill Changes. Steps use checkbox (`- [ ]`) syntax for tracking and cross-session handoff.

**Objective:** Give the superRA skills a unified iterative re-entry mechanism so a fresh agent picking up an in-flight project (a) can tell which workflow stage is active from `## Workflow Status` + per-task fields, (b) can re-enter execution/integration for small-scope additions without spinning up a new PLAN.md, and (c) main agents always have handoff-doc discipline loaded at session start.

**Methodology:** This is a **skill-editing task**, not a data-analysis task. No domain vertical (per `planning-workflow` Phase 1 routing table) covers it; the gap is flagged. The work follows the principles in `CLAUDE.md` (lean agents / rich references, DRY one-source-of-truth, do not weaken any of the four workflow principles).

Four coordinated changes, scoped to existing skills + one new reference file:

1. **`## Scope Changes and Re-entry`** (renamed + extended from `## Mid-Session Scope Changes`) in `handoff-doc/SKILL.md` — single protocol covering both in-execution researcher pings and post-integration scope additions; includes DAG cascade rule and full-drift-suite-always invariant.
2. **`**Integration status:**` task-block field** added in `plan-anatomy.md` alongside `**Review status:**`. Project-level `## Workflow Status` boxes become a rollup over per-task states; orchestrator unchecks at re-entry.
3. **Workflow-skill updates.** `integration-workflow` spells out full-drift-suite-always + scoped refactor + doc-writer-full-reviewer-diff; `execution-workflow` Step 1 reads Integration status and proposes DAG transitive-downstream invalidation on re-entry; all four workflow skills rename the renamed section pointer.
4. **Main-agent reference consolidation.** Merge `session-bootstrap.md` + `main-agent-autonomy.md` → single `main-agent.md`; add `superRA:handoff-doc` to the main-agent default session-start load.

**Vertical-coverage gap:** `planning-workflow` Phase 1 has no entry for "skill editing" or "plugin development". Per the workflow rule, this is documented as a flag, not a blocker. We proceed without a domain skill — the discipline rules in `CLAUDE.md`'s Design Principles section take the role that the domain skill normally plays for data analysis.

**Affected files (file inventory, updated for this re-entry):**

| File | Change shape (this iteration) |
|---|---|
| `skills/handoff-doc/SKILL.md` | Rename `## Mid-Session Scope Changes` → `## Scope Changes and Re-entry`; extend to cover post-integration re-entry + add DAG cascade paragraph + full-drift-suite banned-shortcut bullet |
| `skills/handoff-doc/references/plan-anatomy.md` | Add `**Integration status:**` to task-block template + Field-by-Field; expand `## Workflow Status` description for re-entry semantics; rename the SKILL.md section pointer |
| `skills/planning-workflow/SKILL.md` | Pointer rename only |
| `skills/execution-workflow/SKILL.md` | Step 1: read `**Integration status:**` + DAG cascade detection on re-entry; Stop-Points class (b) pointer rename |
| `skills/integration-workflow/SKILL.md` | Stage 1: always-full-drift-suite rule; Stage 2: scoped refactor reviewer; Step 3: doc-writer full + doc-reviewer diff; box-flip language keys on per-task Integration-status rollup |
| `skills/merge-workflow/SKILL.md` | Pointer rename only |
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

**Expected results:** A fresh agent running `cat PLAN.md` on any project using this updated skill set will see (a) the `## Workflow Status` rollup to know which stage is active and which boxes were unchecked at re-entry, (b) per-task `**Review status:**` + `**Integration status:**` fields to know which tasks remain APPROVED (no re-work needed) vs which were cleared under the DAG cascade, and (c) the `§Scope Changes and Re-entry` section covering both researcher pings during execution and scope additions that arrive after integration or merge. Main agents have `superRA:handoff-doc` loaded at session start so the editing discipline is available without a separate invocation.

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

> **User decision (2026-04-17, post-rebase):** Merge `origin/main` into this branch via `superRA:semantic-merge` (Tier 3) to reconcile the design-coherence-refactor divergence. For the four conflicted files (`RELEASE-NOTES.md`, `skills/execution-workflow/SKILL.md`, `skills/planning-workflow/SKILL.md`, `tests/structural-invariants.sh`) take main's version in the mechanical commit; re-apply the branch's unique wire-ups (Workflow Status reads + box-flips + scope-change pointers) against main's new structure in the integration commit. Chose Option A (merge path, preserves history via merge commit) over Option B (hard rebase, discards 14 branch commits). Main's rewritten `tests/structural-invariants.sh` supersedes the branch's four-principles awk scoping fix — no re-application needed. Line-number citations in Task 1–4 sub-steps are stale against main's restructured handoff-doc / workflow skills; the implementations were committed at the old base SHA and remain valid in content, only the line numbers drifted.
> **Question asked:** Rebase this branch on main; keep unique and essential parts only. Merge vs hard rebase?

---

## Workflow Status

- [ ] **Plan approved** — unchecked at re-entry (2026-04-17): plan rewritten to adopt per-task `**Integration status:**` + iterative re-entry mechanism; Tasks 1/2/3 rescoped, Task 5 added
- [ ] **Execution complete** — unchecked at re-entry: Tasks 1/2/3/5 need re-implementation against the new design; Task 4 remains APPROVED (header-ownership language unaffected by the redesign)
- [ ] **Drift tests created** — unchecked at re-entry: no new invariants to author this iteration, but full-suite `bash tests/structural-invariants.sh` must re-run green before recheck
- [ ] **Refactored** — unchecked at re-entry: Tasks 1/2/3/5 code changes require integration-reviewer pass
- [ ] **Docs finalized** — unchecked at re-entry: RELEASE-NOTES needs a new entry describing the unified re-entry mechanism + main-agent handoff-doc default; doc-reviewer runs on the diff
- [ ] **Merged** — unchecked at re-entry: PR #2 update path to be decided at merge-workflow Step 4 (update in place vs stacked PR)

---

### Task 1: Reframe `## Mid-Session Scope Changes` → `## Scope Changes and Re-entry` in `handoff-doc/SKILL.md`
**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:**

**Script:** `skills/handoff-doc/SKILL.md` (edit)
**Input:** Current `handoff-doc/SKILL.md` carrying `## Mid-Session Scope Changes` (lines 48–82) + `## PLAN.md Is the Task Tracker` (lines 27–42, landed in a prior pass, keep as-is).
**Output:** Same file with the §Mid-Session section renamed and extended to cover both in-execution drift and post-integration re-entry, including the DAG cascade rule.

- [x] **Step 1: Rename section heading** from `## Mid-Session Scope Changes` to `## Scope Changes and Re-entry` and rewrite the one-paragraph preamble so it frames the protocol as covering (a) researcher pings during execution and (b) scope additions that arrive after integration or merge (PR-review additions, reviewer-requested adjacent features, follow-on ideas). Keep the "there is one PLAN.md per analysis" rule.

- [x] **Step 2: Extend the Material / Not-material bullets** so "Material (require this protocol)" names post-integration additions explicitly as one of the covered cases. "Not material" bullets are unchanged.

- [x] **Step 3: Rewrite the 6-step Protocol** to keep the existing skeleton (confirm intent → log decision → edit PLAN inline → update Workflow Status → commit atomically → resume) but:
  - Step 3 "Update PLAN.md inline" gets a new first bullet: "Prefer modifying existing task blocks over appending. Append only when the change cannot be expressed as an edit to an existing task's scope."
  - Step 4 "Update `## Workflow Status`" gets explicit language that the orchestrator unchecks project-level boxes by judgment and declares in the §Decisions entry *which* boxes and *why*. Add sub-bullet: per-task fields (`**Review status:**` / `**Integration status:**`) on tasks fully re-implemented are cleared; untouched tasks retain APPROVED; minor-edited tasks clear `**Integration status:**` while keeping `**Review status:** APPROVED` if code is unchanged.
  - Step 6 "Resume" gets the full-drift-suite rule: `integration-workflow` runs the full drift-test suite on every re-entry regardless of closure; only *authoring* new drift tests is scoped. Doc-writer always re-runs whole doc; doc-reviewer on diff.

- [x] **Step 4: Add a new paragraph under the Protocol on DAG cascade.** When re-entering, the orchestrator walks the transitive downstream closure of each task whose code or outputs will change (from `**Depends on:**` fields). Default: every task in the closure has `**Review status:**` and `**Integration status:**` cleared. Exemption: the orchestrator may leave a task APPROVED by documenting *why* the change does not affect its inputs — one blockquote per exempted task in §Decisions. The drift-test suite runs in full regardless of the closure; closure scopes re-review and integration-review dispatch only.

- [x] **Step 5: Extend "Banned shortcuts"** with one bullet: "Running a subset of the drift-test suite on re-entry because 'only these tasks changed' — authoring is scoped, running is not. Always run the full suite."

- [x] **Step 6: Validate** — `grep -n "Mid-Session Scope Changes" skills/` returns zero hits across the repo (pointers in other skills are updated in Task 3). The §Scope Changes and Re-entry section cross-references §User Decisions Log, §PLAN.md Is the Task Tracker, and `plan-anatomy.md` §Field-by-Field. Voice matches the existing four-principles-era sections.

---

### Task 2: Add `**Integration status:**` field + re-entry semantics to `plan-anatomy.md`
**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:**

**Script:** `skills/handoff-doc/references/plan-anatomy.md` (edit)
**Input:** Current `plan-anatomy.md` carrying the header template with `## Workflow Status` (lines 47–60, landed in a prior pass), task-block anatomy (lines 122+), and Field-by-Field notes.
**Output:** Same file carrying (a) `**Integration status:**` in the task-block template, (b) expanded `## Workflow Status` description noting derived-from-task-status + re-entry unchecks, (c) new Field-by-Field bullets, (d) updated pointer from §Mid-Session Scope Changes → §Scope Changes and Re-entry.

- [x] **Step 1: Add `**Integration status:**` line to the task-block template** (currently line 127) immediately below `**Review status:**`. Render as: `**Integration status:** *(set during integration — not filled at planning time)*`. Values: unset / IMPLEMENTED / REVISE / APPROVED.

- [x] **Step 2: Expand the `## Workflow Status` paragraph** in the header template (currently line 49) so it explains: project-level boxes are a rollup over per-task `**Review status:**` / `**Integration status:**`; the orchestrator unchecks them at re-entry when a scope change invalidates the milestone; the full drift-test suite must re-run green before rechecking `Drift tests created`. Point at `SKILL.md §Scope Changes and Re-entry` (renamed in Task 1).

- [x] **Step 3: Update the Field-by-Field section.** Edit the existing `**Review status:**` bullet to note that downstream tasks in the DAG closure of a modified task have their status cleared by default (orchestrator-documented exemptions in §Decisions). Add a new bullet for `**Integration status:**` with the same values vocabulary, set by the integration reviewer considering drift / refactor / doc coverage for that task's contribution, same cascade rule as `**Review status:**`. Update the existing `## Workflow Status checkboxes` bullet: change the pointer `SKILL.md §Mid-Session Scope Changes` → `SKILL.md §Scope Changes and Re-entry`.

- [x] **Step 4: Validate** — Fenced block count stays even (template not broken). Template line count changes by +1 (Integration status line). Pointer renames complete: `grep -n "Mid-Session Scope Changes" skills/handoff-doc/references/plan-anatomy.md` returns zero. Field-by-Field now has explicit cascade semantics for both Review and Integration status.

---

### Task 3: Update the four workflow skills for iterative re-entry + full drift-suite always + renamed section pointer
**Depends on:** Task 1 (section rename must land so pointers resolve), Task 2 (Integration-status field must exist in anatomy so workflow skills can reference it)
**Review status:**
**Integration status:**

**Script:** `skills/planning-workflow/SKILL.md`, `skills/execution-workflow/SKILL.md`, `skills/integration-workflow/SKILL.md`, `skills/merge-workflow/SKILL.md` (edit)
**Input:** Current state of each — they carry pointers to `§Mid-Session Scope Changes` and box-flip language landed in a prior pass. All pointer strings must be updated; `integration-workflow` needs substantive content changes for drift-suite + refactor-scope + doc-scope wording; `execution-workflow` Step 1 needs DAG-cascade detection on re-entry.
**Output:** All four skills use the new `§Scope Changes and Re-entry` name; integration-workflow spells out the always-full-drift-suite rule and the orchestrator-declared scope for refactor authoring + doc-reviewer diff; execution-workflow Step 1 reads `**Integration status:**` alongside `**Review status:**` and proposes the DAG invalidation set on re-entry; box-flip language ties to the per-task rollup.

- [ ] **Step 1: `planning-workflow/SKILL.md`** — rename the existing pointer `handoff-doc §Mid-Session Scope Changes` → `handoff-doc §Scope Changes and Re-entry` in the Living Plan section. `Plan approved` box-flip language in Execution Handoff is unchanged (still flips on planning approval).

- [ ] **Step 2: `execution-workflow/SKILL.md`** — three edits:
  - Step 1 sub-step 1 pointer rename: `handoff-doc §PLAN.md Is the Task Tracker` unchanged; the downstream reference that names `§Mid-Session Scope Changes` in the TodoWrite sub-step gets renamed to `§Scope Changes and Re-entry`.
  - Step 1 expansion: add a new sub-step after "Read `## Workflow Status`" that reads each pending task's `**Review status:**` *and* `**Integration status:**`. On detected re-entry (any project-level box unchecked but some tasks APPROVED), the orchestrator walks the DAG: any task being modified this re-entry gets its transitive downstream closure (from `**Depends on:**`) proposed for invalidation. Orchestrator adjudicates default-clear vs documented exemption per `handoff-doc §Scope Changes and Re-entry`.
  - Stop-Points class (b) pointer rename: `handoff-doc §Mid-Session Scope Changes` → `handoff-doc §Scope Changes and Re-entry`. `Execution complete` box-flip semantics unchanged (flips when every task has `**Review status:** APPROVED`).

- [ ] **Step 3: `integration-workflow/SKILL.md`** — substantive changes:
  - Stage 1 (drift tests): rewrite the authoring rule to explicitly state "Always run the full drift-test suite on every integration pass, regardless of re-entry scope. Author new drift tests only for tasks with `**Integration status:**` ≠ APPROVED plus any orchestrator-declared related tasks per §Scope Changes and Re-entry." Update `Drift tests created` box-flip to key on all tasks having `**Integration status:** APPROVED` (drift coverage is one of the three integration gates).
  - Stage 2 (refactor): refactor-reviewer scope = tasks with `**Integration status:**` ≠ APPROVED + orchestrator-declared related tasks. `Refactored` box-flip ties to the same rollup.
  - Step 3 (docs): doc-writer re-runs the whole matured doc on every integration pass; doc-reviewer reviews the diff from the last APPROVED state plus any section a newly-reworked task touches. `Docs finalized` flip language unchanged beyond the pointer rename.

- [ ] **Step 4: `merge-workflow/SKILL.md`** — Step 3 "On entry" note and Step 4 "Before executing the merge action" note both rename `§Mid-Session Scope Changes` → `§Scope Changes and Re-entry`. `Merged` flip semantics unchanged.

- [ ] **Step 5: Validate** — `grep -rn "Mid-Session Scope Changes" skills/` returns zero hits across the repo. The integration-workflow wording about "always-full-drift-suite" appears verbatim in Stage 1 and is cross-referenced from `handoff-doc §Scope Changes and Re-entry` Step 5 banned-shortcut bullet (set in Task 1). Execution-workflow Step 1 references `**Integration status:**` explicitly. DAG cascade language in execution-workflow Step 1 points back to handoff-doc for the exemption protocol. No Principle 3 violations — every flip keys on a rollup over per-task fields.

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
**Review status:**
**Integration status:**

**Script:** `skills/using-superRA/references/main-agent.md` (new), `skills/using-superRA/references/session-bootstrap.md` (delete), `skills/using-superRA/references/main-agent-autonomy.md` (delete), `skills/using-superRA/SKILL.md` (edit)
**Input:** Current `references/session-bootstrap.md` (55 lines: cross-session detection + mandatory start actions + "load the autonomy contract" handoff). Current `references/main-agent-autonomy.md` (52 lines: three pause classes + proceed-without-asking + banned phrasings + one-question-at-a-time + log-before-act). Current `using-superRA/SKILL.md` Skill-Load Manifest preamble at lines 65–82 (notes `handoff-doc` is loaded on `documentation` and `planning-review` rows only).
**Output:** Single `references/main-agent.md` carrying cross-session detection + autonomy contract + a new directive establishing `superRA:handoff-doc` as a main-agent default skill load. The two prior files are deleted. Skill-Load Manifest preamble gets a note describing the main-agent default that sits alongside (and does not contradict) the subagent-only rows.

- [ ] **Step 1: Create `skills/using-superRA/references/main-agent.md`** consolidating both source files. Structure: (a) MANDATORY Session Start Actions (from session-bootstrap §MANDATORY), (b) Cross-Session Detection bash block + incomplete-plan handling + worktree-no-plan handling (from session-bootstrap §Cross-Session Detection), (c) **new paragraph: "Load the handoff-doc skill"** — state that the main agent loads `superRA:handoff-doc` at session start so the editing discipline and §Scope Changes and Re-entry protocol are available before touching PLAN.md, (d) The Three Pause Classes (from main-agent-autonomy §The Three Pause Classes), (e) Proceed Without Asking (from main-agent-autonomy §Proceed Without Asking), (f) Banned Phrasings, (g) One Question at a Time, (h) Log Before You Act. Top-of-file note: "Main agent loads this at session start; subagents skip — they inherit task context from their dispatch and do not make autonomy decisions of their own."

- [ ] **Step 2: Delete `skills/using-superRA/references/session-bootstrap.md`** and **`skills/using-superRA/references/main-agent-autonomy.md`** via `git rm`. All their content lives in `main-agent.md`.

- [ ] **Step 3: Update `skills/using-superRA/SKILL.md`** — two edits:
  - The sentence at the top of the §Skill-Load Manifest that currently names `session-bootstrap.md` (currently around lines 65–69 in the preamble describing main-agent session-start loads) is rewritten to point at the new `main-agent.md`.
  - Add one sentence to the Skill-Load Manifest preamble (or a paragraph below the table at the current line 80 area): "Main agents additionally load `superRA:handoff-doc` at session start (per `references/main-agent.md`) so that editing discipline and `§Scope Changes and Re-entry` are available whenever the main agent touches PLAN.md. The subagent-side rows above are unaffected — subagents load `handoff-doc` only on `documentation` / `planning-review` stages as before." No other row in the table is changed.

- [ ] **Step 4: Validate** —
  - `ls skills/using-superRA/references/` shows `main-agent.md` but not `session-bootstrap.md` or `main-agent-autonomy.md`.
  - `grep -rn "session-bootstrap.md\|main-agent-autonomy.md" skills/` returns zero hits (no stale pointers).
  - `grep -n "handoff-doc" skills/using-superRA/SKILL.md` shows both the new main-agent-default note and the existing `documentation` / `planning-review` subagent rows.
  - Content parity: every numbered bullet / pause class / banned phrasing from the two deleted files appears in `main-agent.md`. No content dropped.
