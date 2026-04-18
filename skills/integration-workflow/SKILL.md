---
name: integration-workflow
description: Use when an analysis is code-complete and reproducibility-verified and the user has chosen to merge back or open a PR; when you need drift tests to guard key results before they touch main; when analysis code needs a refactor pass to fit existing codebase conventions before integration (including a project-level CLAUDE.md / AGENTS.md / README.md audit for the diff); when the Stage 1 dev-log RESULTS.md still needs to be matured into its permanent, fact-checked, co-located form (Stage 2); when PLAN.md needs final disposition before merge. Triggers include "prepare this for merge", "write drift tests for the key results", "refactor this to match the codebase style", "consolidate RESULTS.md", "mature the results document", "update project docs for this analysis", "get this ready to PR", or the transition from `execution-workflow`'s completion menu (options 1 or 2). Sits at the INTEGRATE phase, step 1 of 2; hands off to `merge-workflow` for the main update and actual merge/PR.
---

# Integration Workflow

Workflow skill for the **INTEGRATE** phase of the superRA workflow. Owns the three steps that prepare an analysis branch for merging into main: protect results with drift tests (Stage 1), refactor code for codebase integration and audit project-level docs reachable from the diff (Stage 2), and finalize RESULTS.md into its Stage 2 permanent form plus dispose of PLAN.md (Step 3). Hands off the actual merge/PR mechanics to `superRA:merge-workflow`.

Assumes execution-workflow has already verified reproducibility and the user has chosen Option 1 (merge locally) or Option 2 (push + PR). If you find yourself running reproducibility checks or presenting the 4-option menu, something is wrong: that work belongs in execution-workflow.

**Core principle:** Tests guard results. Integration review identifies what needs changing in both the code and the project-level docs that describe it. Refactoring addresses specific issues. Before merge, RESULTS.md matures from dev log into a permanent co-located record through a dedicated doc-writer + doc-reviewer pair, and PLAN.md is disposed of. Nothing hands off to merge-workflow without integration reviewer approval on the refactored code + project-doc audit (Stage 2) AND doc-reviewer approval on the matured RESULTS.md (Step 3).

**Announce at start:** "I'm using the integration-workflow skill to prepare this work for integration."

**Autonomy:** this workflow has exactly four legitimate stop points — drift-test candidate confirmation (Stage 1 Step 2), meaningful drift escalation after refactoring (Stage 2 / "Handling Drift Test Failures"), Stage 2 RESULTS.md relocation target if project guidance does not specify one (Step 3 sub-part A), and PLAN.md disposition (Step 3 sub-part C). Between those, run on your own power: do not check in after each stage, do not ask "ready to move to the next step?", do not re-confirm a reviewer's APPROVE. See `superRA:using-superRA` §Universal Principles (principle #4) + `references/main-agent.md` for the full autonomy rule, and `superRA:handoff-doc` §User Decisions Log for how the answer at each stop point must be recorded in PLAN.md before the workflow acts on it.

## The Process

**Stage 1 — Drift Test Creation:**

1. Extract key results from `RESULTS.md`.
2. Present candidates to the user (legitimate stop point).
3. Dispatch test-creator → dispatch test-reviewer. Iterate REVISE → fix → re-review until APPROVE.
4. Run tests to establish a green baseline.
5. Commit test files.

**Stage 2 — Integration Review → Refactor Loop:**

1. Identify codebase conventions.
2. Dispatch integration-reviewer.
3. On APPROVE → final commit, proceed to Step 3.
4. On REVISE → dispatch refactor subagent with specific feedback → run drift tests.
   - **Drift tests pass** → commit refactored code → re-dispatch integration-reviewer.
   - **Drift tests fail** → assess economic significance.
     - **Minor variation** → update test expectations, document the reason, commit, re-dispatch reviewer.
     - **Meaningful** → STOP, ask the user with before/after numbers (legitimate stop point).

**Step 3 — Documentation Finalization:**

1. Resolve `RESULTS_DIR` (stop if project guidance is missing — legitimate stop point).
2. Dispatch doc-writer → mature `RESULTS.md` in place, then `git mv` to its destination.
3. Dispatch doc-reviewer. Iterate REVISE → fix → re-review until APPROVE.
4. Ask `PLAN.md` disposition (legitimate stop point).
5. Execute disposition → hand off to `merge-workflow`.

## Dispatch Convention

See `superRA:agent-orchestration` §Dispatch Templates for the canonical dispatch shape and §Handling Reviewer Feedback (Orchestrator Discipline) for the REVISE adjudication protocol. The same discipline applies at every stage of this workflow — you are the senior researcher; the reviewer is an advisor.

## Stage 1: Drift Test Creation

Drift tests guard key results from unintended changes during refactoring or future modifications. They are the safety net that makes refactoring safe.

### Steps

1. **Extract key results from RESULTS.md.** Read the results document and use economic reasoning to identify KEY results -- main findings that define the analysis conclusions, not every intermediate number.

2. **Present candidates to user via `AskUserQuestion`** (plain text if unavailable). This is a legitimate stop point — drift-test coverage is a researcher-owned decision because it encodes what counts as a "key result" worth protecting. Show the candidates with their values and let the researcher confirm, add, or remove:
   ```
   These results seem like the key findings to protect with drift tests:
   - [result 1: description and value]
   - [result 2: description and value]
   - ...

   Which of these should be protected? Any to add or remove?
   ```
   Log per `handoff-doc` §User Decisions Log; commit the PLAN.md edit **before** dispatching the test-creator.

**Always run the full drift-test suite on every integration pass, regardless of re-entry scope.** Author new drift tests only for tasks with `**Integration status:**` ≠ APPROVED plus any orchestrator-declared related tasks per `handoff-doc §Scope Changes and Re-entry`. Running a subset of the suite because "only these tasks changed" is a banned shortcut — authoring is scoped, running is not.

3. **Dispatch test-creator:**
   ```
   Agent(subagent_type: "superRA:implementer"):
     Stage: drift-test
     Task: Task N in PLAN.md — create drift tests for the user-confirmed key results

     Follow the standard stage-relevant workflow and load
       relevant skills and documents to proceed. Additionally,
       <optional steering — e.g., tolerance conventions specific to this
       analysis, prior-round adjudication if this is a re-dispatch>.
   ```

4. **Dispatch test-reviewer:**
   ```
   Agent(subagent_type: "superRA:reviewer"):
     Stage: drift-test
     Task: Task N in PLAN.md — drift tests under review
     Git range: <BASE_SHA>..<HEAD_SHA>

     Follow the standard stage-relevant workflow and load
       relevant skills and documents to proceed. Additionally,
       <optional steering>.
   ```

5. **If REVISE:** adjudicate the reviewer's issues per the orchestrator discipline above. For accepted issues, re-dispatch the test-creator with the specific feedback. Re-dispatch the test-reviewer. Iterate until APPROVE.

6. **Run tests to establish green baseline.** All drift tests must pass on the current code before proceeding. If tests fail on the existing code, the tests are wrong -- fix them.

7. **Commit test files.**
   ```bash
   git add tests/
   git commit -m "add drift tests for key analysis results"
   ```

8. **Flip the milestone.** Check the `Drift tests created` box in `PLAN.md` §Workflow Status (see `superRA:handoff-doc` references/plan-anatomy.md) only once all tasks have `**Integration status:** APPROVED` (drift-test coverage is one of the three integration gates) and commit the doc edit before moving to Stage 2.

## Stage 2: Integration Review → Refactor Loop

The integration reviewer is the gatekeeper. Review first to identify what needs changing, then refactor to address specific issues. Nothing moves forward without integration reviewer approval.

### Steps

1. **Identify existing codebase conventions.** Read:
   - CLAUDE.md, AGENTS.md, or project configuration for coding standards
   - Existing code in the repository for naming patterns, file organization, utility functions
   - Available utility functions that the new code should adopt

2. **Dispatch integration-reviewer:**
   ```
   Agent(subagent_type: "superRA:reviewer"):
     Stage: integration
     Task: Task N in PLAN.md — integration review of the refactored analysis code
     Git range: <BASE_SHA>..<HEAD_SHA>

     Follow the standard stage-relevant workflow and load
       relevant skills and documents to proceed. Additionally,
       this stage also covers the project doc audit per
       `codebase-integration.md` §Project Doc Audit (walk-up
       CLAUDE.md / AGENTS.md / README.md reachable from the diff).
       <optional steering>.
   ```

3. **If APPROVE:** No refactoring needed. Proceed to final commit.

4. **If REVISE:** Adjudicate the reviewer's feedback per the orchestrator discipline above. For accepted issues, refactor. Refactorer scope = tasks with `**Integration status:**` ≠ APPROVED plus any orchestrator-declared related tasks per `handoff-doc §Scope Changes and Re-entry`.

   a. **Dispatch refactorer:**
      ```
      Agent(subagent_type: "superRA:implementer"):
        Stage: integration
        Task: Task N in PLAN.md — address integration reviewer's accepted findings

        Follow the standard stage-relevant workflow and load
          relevant skills and documents to proceed. Additionally,
          this stage also covers the project doc audit per
          `codebase-integration.md` §Project Doc Audit (walk-up
          CLAUDE.md / AGENTS.md / README.md reachable from the diff).
          <optional steering — e.g., prior-round adjudication, items the
          orchestrator has rejected vs. accepted>.
      ```

   b. **After refactoring: run drift tests.**
      - **Pass:** Commit and re-submit for review.
      - **Fail:** Assess economic significance of the drift.
        - **Meaningful drift** (results change substantively): STOP. Show the user before/after values and ask how to proceed. Do not silently accept changed results.
        - **Minor variation** (rounding, floating-point, inconsequential magnitude change): Update test expectations with the new values, document the reason in a comment, and proceed.

   c. **Commit refactored code.**
      ```bash
      git add -A
      git commit -m "refactor analysis code for codebase integration"
      ```

   d. **Re-dispatch integration-reviewer.** Loop back to step 2. Iterate until APPROVE.

5. **Final commit** after integration reviewer APPROVE.
   ```bash
   git add -A
   git commit -m "address integration review feedback"
   ```

6. **Flip the milestone.** Check the `Refactored` box in `PLAN.md` §Workflow Status and commit the doc edit once all tasks have `**Integration status:** APPROVED` (the box is a rollup over per-task Integration-status fields). If a later round of refactoring is triggered (post-merge integration review in `merge-workflow`, or a researcher-initiated scope change that touches refactored code), uncheck the box until the next integration-reviewer APPROVE — the box reflects current state, not historical state.

## Step 3: Documentation Finalization

After Stage 2 APPROVES the refactored code (including the project doc audit that Stage 2 now covers via `codebase-integration.md` §Project Doc Audit), `RESULTS.md` still needs to mature from dev log to permanent record, and `PLAN.md` still needs to be disposed of. This step gates the RESULTS.md maturation behind a **single implementer-reviewer pair** — a dispatched doc-writer subagent performs sub-part A, a dispatched doc-reviewer subagent gates it, and the orchestrator handles the user-facing decisions (relocation target in the preamble, PLAN.md disposition in sub-part C) on either side of the subagent cycle.

Why a doc-writer subagent and not orchestrator-performed: workflow principle P1 requires an enforced implementer-reviewer pair at every step. Having the orchestrator do the consolidation and then dispatching only a reviewer is a reviewer-only gate, not a pair. The doc-writer subagent closes that gap and keeps Step 3 consistent with the rest of the workflow.

The format discipline for sub-part A lives entirely in `superRA:report-in-markdown`. This step orchestrates and dispatches; it does not duplicate the rules.

### Orchestrator preamble: resolve RESULTS_DIR

The matured `RESULTS.md` lands in the analysis's permanent code folder, **per project guidance**. Before dispatching the doc-writer, read `CLAUDE.md`, `AGENTS.md`, or the project README for the convention. If none exists, this is a legitimate stop point — ask the researcher via `AskUserQuestion` (plain text if unavailable):

```
Stage 2 RESULTS.md needs a permanent location in this project. The matured
file will be co-located with the analysis code so it travels with it.
Where should it land?

Suggested: <best guess from the analysis code's location, e.g. analyses/<name>/>
```

Log per `handoff-doc` §User Decisions Log **before** dispatching the doc-writer. If a project convention exists in the guidance files, use it directly without asking.

Define `RESULTS_DIR` = the resolved permanent folder. Define `RESULTS_ATTACHMENTS_DIR` = `${RESULTS_DIR}/attachments` (destination for materialized figures, distinct from the worktree-root `results_attachments/` that the analysis script writes to). Pass both as dispatch parameters.

### Dispatch the doc-writer

```
Agent(subagent_type: "superRA:implementer"):
  Stage: documentation
  Task: Task N in PLAN.md — Stage 2 RESULTS.md maturation
  RESULTS_DIR: <resolved permanent folder>
  RESULTS_ATTACHMENTS_DIR: ${RESULTS_DIR}/attachments

  Follow the standard stage-relevant workflow and load
    relevant skills and documents to proceed. Additionally, this dispatch
    matures RESULTS.md per `final-form.md` §The consolidation pass —
    four ordered commits. Land each of the four commits separately (in
    order: fact-check → restructure → materialize figures → relocate)
    so a session interruption is recoverable. In your status return,
    list which of the four sub-commits landed.
    <optional additional steering — e.g., project-specific doc conventions,
    prior-round doc-reviewer feedback on a re-dispatch>.
```

The doc-writer is the only subagent in this step. It loads `superRA:report-in-markdown` full mode (SKILL.md + all three references) and performs sub-part A before returning control. **The doc-writer always re-runs the whole matured doc on every integration pass** — even on re-entry where only some tasks changed. The doc-reviewer reviews the diff from the last APPROVED state plus any section a newly-reworked task touches.

#### Sub-part A: Mature RESULTS.md in place — four ordered commits

Drive from `final-form.md` §The consolidation pass — four ordered commits. Each commit is independently recoverable; if the session crashes between commits, a fresh dispatch resumes from the next un-landed step (the prior commits are on the branch, the file is in a coherent in-between state).

Commit sequence (suggested messages match `final-form.md`):

1. `results: fact-check Stage 2 RESULTS.md` — walk the fact-check checklist against the Stage 1 dev log at worktree root. No structural changes yet.
2. `results: restructure Stage 2 RESULTS.md to reader-facing` — reorganize by objective/data/result, merge related findings, strip resolved caveats, add frontmatter. Task numbering disappears.
3. `results: materialize figures into ${RESULTS_DIR}/attachments` — copy `results_attachments/*` into `${RESULTS_ATTACHMENTS_DIR}` (PDF→PNG per `rich-content.md`), update embed paths in `RESULTS.md`.
4. `results: relocate RESULTS.md to ${RESULTS_DIR}` — `git mv RESULTS.md ${RESULTS_DIR}/RESULTS.md` so history follows the file. Attachments folder already lives at `${RESULTS_ATTACHMENTS_DIR}` after commit 3.

Each commit has its own validation gate — see `final-form.md` for the per-commit checklist. Do NOT bundle these into one commit.

**Recovery on re-dispatch.** If the orchestrator sees the doc-writer's status return listed commits 1 and 2 as landed but not 3 or 4 (or the doc-writer crashed without returning), the re-dispatch's `Additionally:` line names which commits still need to land. The doc-writer reads `git log --oneline` on the branch and resumes at the first un-landed step.

### Dispatch the doc-reviewer

After sub-part A commits, dispatch the reviewer:

```
Agent(subagent_type: "superRA:reviewer"):
  Stage: documentation
  Task: Task N in PLAN.md — review of matured Stage 2 RESULTS.md
  Git range: <BASE_SHA>..<HEAD_SHA>
  RESULTS_DIR: <resolved permanent folder>

  Follow the standard stage-relevant workflow and load
    relevant skills and documents to proceed. Additionally,
    <optional steering>.
```

The reviewer loads `superRA:report-in-markdown` SKILL.md + `final-form.md` (and only those — per the skill's load-map for the doc-reviewer role). Scope:

1. **Matured RESULTS.md** — on a first integration pass, run the fact-check checklist line by line (`final-form.md`). On re-entry, focus the review on the diff from the last APPROVED state plus any section a newly-reworked task touches; re-verify fact-check items only where the underlying analysis changed. Every cited number must match its source. Prohibited language, unsupported claims, and disallowed sections block APPROVED.
2. **Cross-consistency** — matured `RESULTS.md` and any `README.md` / `CLAUDE.md` that mentions the analysis do not contradict each other (figures of merit, method names, sample sizes). Stale project-doc claims against the diff are Stage 2's responsibility (`codebase-integration.md` §Project Doc Audit) and should already be resolved by the time Step 3 runs.

If REVISE: adjudicate per the orchestrator discipline above. For accepted issues, re-dispatch the doc-writer with specific feedback (file:line, what to fix). Re-dispatch the doc-reviewer. Iterate until APPROVE.

**On doc-reviewer APPROVE:** check the `Docs finalized` box in `PLAN.md` §Workflow Status (the box is a rollup — it flips when all tasks have `**Integration status:** APPROVED` and the doc-reviewer has approved the whole doc) and commit the doc edit before moving to Sub-part C. The box flips here, not after disposition, because by Sub-part C `PLAN.md` may be moved or removed depending on the researcher's choice — the milestone belongs to the doc-finalization gate, not the disposition.

### Sub-part C: Dispose of PLAN.md (orchestrator, after APPROVE)

Once the doc-reviewer APPROVES sub-part A, the orchestrator handles PLAN.md disposition directly — this is a user-facing decision, not an RA-implementable task, and it must not be delegated.

By this point `RESULTS.md` has graduated to `${RESULTS_DIR}` and project docs are already in sync (audited during Stage 2 per `codebase-integration.md` §Project Doc Audit). `PLAN.md` is the only Stage 1 scaffold left at the worktree root, along with the working `results_attachments/` folder (whose content has already been materialized into `${RESULTS_ATTACHMENTS_DIR}`).

Ask via `AskUserQuestion` (plain text if unavailable) — this is a legitimate stop point. The default suggestion is Option 1 (move alongside the matured RESULTS.md):

```
PLAN.md is still at the worktree root and needs disposition. RESULTS.md
has already been matured and committed at ${RESULTS_DIR}, and project docs
are up to date. Options:

1. Move PLAN.md (and results_attachments/) alongside the matured
   RESULTS.md at ${RESULTS_DIR} — keeps the prescriptive history with
   the analysis code (recommended).
2. Consolidate any plan context into existing project documentation,
   then delete PLAN.md and results_attachments/.
3. Delete PLAN.md and results_attachments/ — git history preserves
   them on this branch.

Which option?
```

Log per `handoff-doc` §User Decisions Log **before** executing the disposition. Include the log entry in the same commit that moves or removes the files — the last state of `PLAN.md` records what was done with it.

**Option 1 (Move alongside matured RESULTS.md):**
```bash
git mv PLAN.md ${RESULTS_DIR}/
git mv results_attachments/ ${RESULTS_DIR}/source_attachments/ 2>/dev/null
git commit -m "move analysis plan to ${RESULTS_DIR}"
```
The `results_attachments/` folder is renamed `source_attachments/` at the destination so it does not collide with the matured RESULTS.md's `attachments/` folder (which holds the materialized copies). Skip the rename if there are no figures.

**Option 2 (Consolidate):**
- Identify which existing project documentation should pick up plan context (data inventory, methodology rationale).
- Merge into existing docs (the researcher guides which docs).
- Remove the originals:
```bash
git rm PLAN.md
rm -rf results_attachments/
git add -A results_attachments/ 2>/dev/null
git commit -m "consolidate analysis plan context into project docs"
```

**Option 3 (Delete):**
```bash
git rm PLAN.md
rm -rf results_attachments/
git add -A results_attachments/ 2>/dev/null
git commit -m "remove analysis plan (preserved in branch history)"
```

## Hand-Off to merge-workflow

After Steps 1–3 are complete (drift tests committed, refactoring approved, all docs finalized via the doc-writer + doc-reviewer pair, and PLAN.md disposed of), invoke `superRA:merge-workflow` to update with main, run post-merge verification (drift tests + fresh integration review), and execute the local merge or PR push. Do not attempt the merge mechanics yourself — merge-workflow owns them.

## When to Lighten

**Standalone analysis (no existing codebase to integrate with):**
- Stage 1 (drift tests): Always run. Tests protect results regardless of codebase context.
- Stage 2 (integration review → refactor): Lighter pass -- focus on code quality and clarity rather than codebase convention alignment. Integration reviewer may APPROVE with no refactoring needed.

**Small changes (single-file analysis, few results):**
- Stage 1: Still run, but fewer tests needed.
- Stage 2: Integration reviewer may APPROVE immediately if code is clean.

## Handling Drift Test Failures After Refactoring

This is the critical judgment call in the process. When drift tests fail after refactoring:

1. **Identify what changed.** Compare the before/after values.
2. **Assess economic significance.** Is this a meaningful change in results, or a trivial numerical difference?
   - Point estimates shifting by more than the tolerance you set: investigate.
   - Sign changes or significance changes: always meaningful.
   - Standard errors changing modestly: usually minor (sensitive to implementation details).
3. **If meaningful:** Do not proceed. Show the user exactly what changed — before/after values side by side — and ask via `AskUserQuestion` (plain text if unavailable) whether to (a) accept the new result and update the drift test baseline with a documented reason, (b) roll back the refactoring, or (c) investigate the discrepancy further before deciding. Log the researcher's answer per `handoff-doc` §User Decisions Log before taking any action.
4. **If minor:** Update the test expectation, add a comment explaining why (e.g., "tolerance updated: refactored merge order produces equivalent result within floating-point precision"), and proceed.

## Agent Loads

See `superRA:using-superRA` §Skill-Load Manifest — it is the single source of truth for what every dispatched implementer / reviewer loads per Stage. This workflow runs the `drift-test`, `integration`, and `documentation` rows.

Step 3 sub-part A (mature RESULTS.md) is performed by the dispatched doc-writer subagent — an implementer-reviewer pair gates the RESULTS.md maturation per workflow principle P1. Sub-part C (PLAN.md disposition) stays with the orchestrator because it is a user-facing decision, not an RA-implementable task. Project-level doc audit is covered by Stage 2 refactor + integration review per `codebase-integration.md` §Project Doc Audit — not by Step 3.

## Red Flags

**Never:**
- Skip Stage 1 (drift tests) — they are the safety net for everything that follows
- Refactor before integration reviewer has identified issues — review first, then fix
- Strip domain-discipline artifacts during refactoring — see `superRA:using-superRA` §Skill-Load Manifest for `integration` for the full reference list per domain
- Judge the researcher's methodology choice — focus on implementation correctness (see the foundational RA framing in `superRA:using-superRA` §Universal Principles)
- Refactor before drift tests are committed and green
- Hand off to merge-workflow without integration reviewer APPROVE on the refactored code + project-doc audit (Stage 2) AND doc-reviewer APPROVE on the matured RESULTS.md (Step 3)
- Skip Step 3 because "RESULTS.md is already a markdown file" — the dev-log form has not been fact-checked, restructured, or relocated, and shipping it as-is bypasses the discipline gate
- Perform the Step 3 sub-part A as the orchestrator instead of dispatching a doc-writer subagent — this bypasses the implementer-reviewer pair that workflow principle P1 requires. Only sub-part C (PLAN.md disposition) is orchestrator-performed, because it is a user-facing decision
- Inline the Step 3 fact-check checklist or frontmatter spec in this skill — it lives in `superRA:report-in-markdown`'s `final-form.md` and `baseline-io.md`, and there should be exactly one source of truth
- Delegate sub-part C (PLAN.md disposition) to the doc-writer subagent — disposition is a researcher-owned decision, not an RA task

**Always:**
- Confirm key-result coverage with the researcher (via `AskUserQuestion`, logged per `handoff-doc` §User Decisions Log) before creating tests
- Run integration review before any refactoring
- Run drift tests after every refactoring change
- Re-submit to integration reviewer after every refactoring round
- Keep and re-validate all domain-discipline artifacts through refactoring — refactoring discipline lives in `superRA:using-superRA` §Skill-Load Manifest for `integration` (for data analysis: `skills/refactor-and-integrate/references/codebase-integration.md` generic + `skills/econ-data-analysis/references/integration.md` data-specific)
- Dispatch the Step 3 doc-writer subagent with `superRA:report-in-markdown` (full mode — all three references) to perform the matured RESULTS.md consolidation; dispatch the doc-reviewer afterward and iterate to APPROVE. Project-doc audit is not part of Step 3 — it is a Stage 2 refactorer / integration-reviewer concern per `codebase-integration.md` §Project Doc Audit
- Resolve `RESULTS_DIR` before dispatching the doc-writer — either from project guidance, or via `AskUserQuestion` if guidance is missing, logged in PLAN.md `## Decisions`
- Commit at each stage boundary and after each Step 3 sub-part (A and C each land as separate commits)

**Drift-test integrity is governed by the cross-cutting rules in `refactor-and-integrate` reference `drift-test-quality.md` ("Drift Test Integrity — Cross-Cutting Red Flags") — failing tests must be adjudicated, not silently re-expected; tolerance bumps require justification; and test removal during refactoring is forbidden. Load the reference before creating, reviewing, or running drift tests.**

## Integration

**Called by:**
- **superRA:execution-workflow** Step 4 -- When the user chooses Option 1 (merge) or Option 2 (PR) after execution-workflow has verified reproducibility

**Hands off to:**
- **superRA:merge-workflow** -- For main update + post-merge verification + actual merge/PR

**Requires:**
- **RESULTS.md** (Stage 1 dev log) -- Source of key results for drift tests; matured into Stage 2 form at Step 3
- **Committed analysis code** -- Must be committed before drift tests are created
- **Reproducibility already verified** by execution-workflow Step 3

**Subagents should use:**
- The active domain skill (for data analysis: `superRA:econ-data-analysis`) — domain discipline loaded at dispatch-time per `superRA:using-superRA` §Skill-Load Manifest
