---
name: implementation-workflow
description: Requires `superRA:using-superra` loaded first. Use when you have a PLAN.md in the superRA task-block format and are ready to implement its tasks; when a plan has been approved and you need per-task implementation with an implementer-reviewer pair; when resuming work on a plan where some tasks are `IMPLEMENTED`, some `REVISE`, and some not started; when an analysis is code-complete and you want to verify reproducibility and present completion options (merge / PR / keep / discard). Triggers include "execute the plan", "run task N", "implement this PLAN.md", "finish this analysis", a branch with an APPROVED plan but no code yet, or a REVISE state that needs orchestrator adjudication before re-dispatch.
---

# Implementation Workflow

**First, load `superRA:using-superra` if not already loaded.** It carries the Skill-Load Manifest, handoff-doc pointer, code-change defaults, and commit hygiene this workflow assumes.

Workflow skill for the **IMPLEMENT** and **VALIDATE** phases of the superRA workflow. Owns per-task dispatch, the implementer-reviewer loop with orchestrator-discipline filtering, end-to-end reproducibility verification, and the 4-option completion menu. 

Default mode dispatches a fresh subagent per task. Each task gets one comprehensive review pass whose verdict is APPROVE / REVISE; the reviewer walks the active domain skill's gated checklist top to bottom, plus any operation-conditional sections matching operations performed in this task. Falls back to direct execution when the user requests it or tasks are trivial.

**Announce at start:** "I'm using the implementation-workflow skill to implement this plan."

## Execution Modes

1. Load plan from `PLAN.md` (run `superRA:planning-workflow` first if no plan exists).
2. Use **subagent mode** (default): dispatch implementer subagent per task; fresh context per task; orchestrator preserves context for coordination.
3. Fall back to **direct mode** when the harness lacks subagent capability, the user explicitly requests it, or tasks are trivial. Direct mode: main agent implements; reviewer subagents still dispatched after each task (review is never skipped).

## The Process

**Load `superRA:agent-orchestration` before writing any dispatch prompt** — the canonical template shape, `Additionally:` anchor rules, and banned fields live there. Dispatching without it produces malformed prompts.

1. Read plan, extract all tasks;
2. **Go through tasks:**
   a. Dispatch implementer subagent. Answer context questions, re-dispatch if needed.
   b. Dispatch reviewer subagent (one comprehensive pass).
   c. **APPROVE** → update plan file + commit, next task. **REVISE** → fix `[BLOCKING]` findings → narrow re-review (cited fixes + dependent findings). Loop until APPROVE, then update plan file + commit.
3. When no tasks remain → verify pipeline + reproducibility (Step 3).
4. Present Step 4 completion menu; dispatch `integration-workflow` on merge/PR.

### Step 0: Branch Check

Before any handoff-doc check, dispatch, or commit, check if on a default branch:

```bash
git branch --show-current
```

If on `main` or `master`:
```
You're on main. I recommend creating a feature branch for this work:
  git checkout -b analysis/<topic>
Want me to create one?
```

If the user declines, proceed — they've given explicit consent to work on the default branch.

### Step 0b: Handoff-Doc Existence Check

After the branch check, confirm `PLAN.md` and `RESULTS.md` exist, are tracked, **and** have no uncommitted modifications (neither unstaged nor staged):

```bash
[ -f PLAN.md ] && [ -f RESULTS.md ] \
  && git ls-files --error-unmatch PLAN.md RESULTS.md >/dev/null 2>&1 \
  && git diff --quiet -- PLAN.md RESULTS.md \
  && git diff --quiet --cached -- PLAN.md RESULTS.md
```

All four conjuncts must succeed. The first two confirm existence and tracking; the last two confirm the worktree copy matches the committed copy (neither a dirty edit nor a staged-but-uncommitted change).

**If the check fails, halt and invoke `superRA:planning-workflow` to bootstrap the docs.** Do not inline planning-workflow content here — proceed through its full Phase 1 / Phase 2 / Self-Review; resume implementation-workflow at Step 1 after planning-workflow completes.

Step 0 (branch check) must have already run — Step 0b comes after Step 0 so bootstrap commits cannot silently land on `main` / `master`.

If the docs exist, are tracked, and the worktree is clean, proceed to Step 1.

### Step 1: Load and Review Plan

1. Read `PLAN.md` and `RESULTS.md`. `PLAN.md` is the task tracker (`superRA:planning-workflow §PLAN.md Is the Task Tracker`); `TodoWrite` mirrors it as a transient session view, not a substitute.
2. **Read `## Workflow Status`** at the top of `PLAN.md`. The checklist names which milestones are complete (`Plan approved`, `Execution complete`, `Drift tests created`, `Integrated`, `Docs finalized`, `Finished`) and tells a resuming agent exactly which phase this branch is at without grepping commits. If `Execution complete` is already checked, skip to Step 3 (verification); if earlier milestones are unchecked unexpectedly, raise it with the user before dispatching tasks.
   - **Also read per-task `**Review status:**` and `**Integration status:**` fields alongside `## Workflow Status`.** If any project-level box is unchecked while some tasks remain APPROVED, a prior `planning-workflow §User Feedback and Changing Plans` invocation unchecked those boxes (Step 4) and paused — resume that protocol at Step 6 before dispatching any implementer. Enter `§User Feedback and Changing Plans` at Step 1 if the researcher instead pings mid-execution with a scope change.
3. **Load the active domain skill(s) following the manifest** Any task-specific helper skills named in PLAN.md's header — load those too. Subagents load these same skills per `superRA:using-superra` §Skill-Load Manifest at dispatch time; the orchestrator loads them in-session because orchestrator judgment happens outside any subagent.
4. **Read PLAN.md's `## Project Conventions` section** (anatomy: `handoff-doc/references/plan-anatomy.md` §Project Conventions). If the section is missing, empty, or stale, walk and populate it now — commit before dispatching subagents.
5. Review PLAN.md critically — identify any questions or concerns:
   - Are data sources / inputs available and accessible?
   - Are the steps in the right order?
   - Is the pipeline file included (for multi-script analyses)?
   - Does any step conflict with a project convention you found in step 4?
6. Review RESULTS.md for context on any completed steps (if resuming).
7. If concerns: raise them with your human partner before starting.
8. If no concerns: proceed.

### Step 2: Execute Tasks

**Before dispatching, read each pending task's `Depends on:` field.**
Tasks whose dependencies are all `APPROVED` may be dispatched as a
single parallel Agent-tool batch (subject to `agent-orchestration`
§Workload Balancing). Serialize only when no parallel batch is
available.

#### Task Execution Steps

1. **Dispatch implementer.** Subagent mode: dispatch agents following `superRA:agent-orchestration`. 
2. **If NEEDS_CONTEXT or BLOCKED:** provide context and re-dispatch (see Handling Implementer Status below).
3. **Once DONE or DONE_WITH_CONCERNS:** the implementer has already committed code + PLAN.md (`IMPLEMENTED`) + RESULTS.md. **Dispatch the reviewer (one comprehensive pass).** The reviewer walks the active domain skill's gated checklist top to bottom, plus any operation-conditional sections matching operations performed in this task, and returns one of two verdicts:
   - **APPROVE** — no `[BLOCKING]` findings. Proceed to the next task.
   - **REVISE** — at least one `[BLOCKING]` finding. Adjudicate feedback in place inside the PLAN.md review-notes blockquote — append `→ orchestrator: rejected <reason>` or `→ orchestrator: <second opinion requested> <reason>` annotations to items you are rejecting or flagging, rewrite task steps in place for items you are accepting, commit, then re-dispatch the implementer. Leave the blockquote itself intact — the implementer will annotate items with `→ implemented: ...` markers on their pass, and the reviewer will delete confirmed-fixed items on re-review. The reviewer's re-review is **narrow by default**: verify the cited fixes + any finding annotated as depending on an upstream fix; everything else is accepted from the first pass. See the "Handling Reviewer Feedback" section below and `agents/implementer.md` / `agents/reviewer.md` for the full annotation mechanics. Iterate until APPROVE.
4. **Once APPROVE:** the reviewer has committed `APPROVED` to PLAN.md. Check whether the review report cites specific files and lines — a substantive APPROVE describes what was verified. A generic APPROVE with no file citations is a red flag: re-dispatch the reviewer with an instruction to cite the key code paths it examined. If findings change upcoming tasks, update future task descriptions in PLAN.md and commit. Proceed to next task.

**In direct mode:** Steps 1–2 are done by the main agent directly (follow `superRA:using-superra` §Execution Modes). Steps 3–4 are unchanged — still dispatch reviewer subagents unless overridden by the user.


#### Handling Reviewer Feedback (Orchestrator Discipline)

See `superRA:agent-orchestration` §Handling Reviewer Feedback (Orchestrator Discipline).

### Step 3: Verify Pipeline and Reproducibility

After every task is APPROVED, verify the work end-to-end before presenting completion options. Walk all five checks; do not proceed if any fails.

**Run every check. Don't trust "looks committed" — execute `git status` and read the output. The five checks below are the orchestrator's verification gate: evidence before claims, no shortcuts.**

1. **All code committed?**
   ```bash
   git status
   ```
   If uncommitted changes exist: investigate (probably an agent missed an inline-edit), commit, or ask the user.

2. **PLAN.md up to date?** All tasks have `**Review status:** APPROVED`. All steps marked `- [x]` with result notes. No tasks stuck in `IMPLEMENTED` or `REVISE`. Discovery notes captured. Upcoming-task descriptions reflect current understanding.

3. **RESULTS.md up to date?** Has findings for all completed tasks. Figure attachments in `results_attachments/` committed.

4. **Reproducibility verification.**
   - Multi-script pipeline runs end-to-end if the plan declares one.
   - Outputs exist and were generated from committed code, not ad-hoc REPL state.

5. **Deferred MINORs resolved?** Check PLAN.md review-notes blockquotes for any remaining MINOR items. If a MINOR was deferred across tasks and never addressed, resolve it now (dead code removal, missing documentation, format compliance) or document it as an accepted limitation in RESULTS.md.

If any check fails: fix it before proceeding. Do not present completion options for unreproducible work.

**Once all five checks pass:** check the `Execution complete` box in `PLAN.md` §Workflow Status (see `superRA:handoff-doc` references/plan-anatomy.md) and commit the box-flip before presenting the Step 4 completion menu. The flip records that the branch has reached the IMPLEMENT/VALIDATE terminus and is ready for the researcher's disposition choice.

### Step 4: Present Completion Options

**Present the 4 completion options via `AskUserQuestion` when the tool is available.** This is a legitimate user-defined milestone — the agent has driven the work to an `APPROVED` + reproducible state on its own power, and the next step is the researcher's call. Frame the question as "Work complete and verified. What would you like to do with this branch?" with the four options below; each option also gets a short description so the researcher does not have to re-derive what each one means. When `AskUserQuestion` is unavailable, fall back to the plain-text form.

```
Work complete and verified. Here are the results summary:
<summarize the results>
What would you like to do?

1. Proceed with integration
2. Change the plan
3. Keep the branch as-is (I'll handle it later)
4. Discard this work
```

Log the researcher's answer per `handoff-doc` §User Decisions Log — top-level `## Decisions` section, before executing the choice, included in the first commit of whatever workflow the option dispatches to.

**Execute the user's choice:**

- **Option 1 (Proceed with integration):** Invoke `superRA:integration-workflow`. It runs Protect, Sync, Integrate, Document, and Finish.
- **Option 2 (Change the plan):** Re-enter `superRA:planning-workflow §User Feedback and Changing Plans` — treat the researcher's scope change as the trigger; resume implementation-workflow from Step 1 after the plan is re-approved.
- **Option 3 (Keep as-is):** Report the branch name and worktree path back to the user, then stop. Do not clean up.
- **Option 4 (Discard):** Confirm with the user by typed input — they must type the word `discard` exactly. Resolve the base branch with `git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null` (ask via `AskUserQuestion` if ambiguous), then perform the teardown: `git checkout <base-branch>`, `git branch -D <analysis-branch>`, and — if the analysis was in a worktree, remove the worktree. Stop after the branch and worktree are removed. Report what was deleted.

## Orchestrator Discipline

Cross-stage orchestrator behavior — task sequencing, reviewer-feedback adjudication, implementer-status handling, and escalation — lives in `superRA:agent-orchestration` §Orchestrator Duties, §Handling Reviewer Feedback, §Review Status Reference, and §Handling Implementer Status.

**Workflow-specific review scope at interim checkpoints:** Per-task correctness only (as defined by the active domain skill's gated checklist). Codebase integration review is deferred to `integration-workflow` (dispatched at Step 4 when the user chooses Option 1 — Proceed with integration).

## Autonomy and Stop Points

The autonomy contract (proceed-without-asking patterns, stop-and-ask classes, banned phrasings) is in `superRA:using-superra/references/main-agent.md` — main-agent only. Read it at session start; it applies to every workflow phase, not just execution. This section lists only the **implementation-workflow-specific stop points** — the legitimate pauses baked into this workflow that plug into the autonomy contract's three pause classes.

- **Step 4 completion menu.** The 4-option menu (merge now / continue another task / sensitivity task / discard) is a user-defined workflow milestone.
- **Hard blockers from domain signals.** Unexpected input-quality issues during initial description, scope changes from a merge (row count shifts), validation failure against domain expectation, plan with critical gaps, pipeline file missing for a multi-script analysis, required input unavailable. Pause class (1) in the autonomy contract.
- **Methodology / authority boundary decisions.** Methodology disagreement with a reviewer, CRITICAL severity issue the orchestrator wants to override, repeated reviewer disagreement across re-dispatches on the same point, validation failure of unclear domain significance, scope or definition call with no obvious right answer. **Researcher-initiated scope change** mid-execution — new task, removed task, methodology pivot, sample redefinition — route through `planning-workflow §User Feedback and Changing Plans` (confirm → log → inline-edit PLAN.md → roll back milestone checkboxes → atomic commit → resume). Pause class (2) in the autonomy contract.

Every stop above: stop and `AskUserQuestion` (plain text if unavailable); log per `handoff-doc` §User Decisions Log **before** acting on it.

## Agent Loads

See `superRA:using-superra` §Skill-Load Manifest — it is the single source of truth for what every dispatched implementer / reviewer loads per Stage. This workflow runs the `implementation` row for both roles; `subagent_type` (`superRA:implementer` vs `superRA:reviewer`) carries the role split.

## Red Flags

**Never:**
- Start work on main/master branch without proposing a feature branch first (Step 0)
- Skip review — even in direct mode
- Proceed with unfixed `[BLOCKING]` items (a REVISE task is not complete until the re-review promotes it to APPROVED)
- Dispatch multiple implementers in parallel on the same worktree — when parallel-dispatching ≥2 implementers, each must run in its own worktree per `superRA:agent-orchestration` §Parallelization and Worktree Isolation
- Paraphrase the task prompt into the dispatch instead of pointing the subagent at `PLAN.md` (the pointer-based convention is mandatory — subagents read the file directly so the dispatch and PLAN.md cannot drift)
- Skip plan file update after task completion
- Ignore implementer input-quality or methodology concerns
- Accept "looks fine" without verification
- Move to the next task while the current task's review has open issues or status is not APPROVED

**If reviewer returns REVISE:**
- Adjudicate in the review-notes blockquote first (see Handling Reviewer Feedback)
- Re-dispatch the implementer with the adjudicated items
- Re-dispatch the reviewer after implementer fixes (narrow re-review: cited fixes + dependent findings)
- Repeat until APPROVED
- Do NOT skip the re-review
- Do NOT ask the user whether to fix — iterate automatically


---

**Before proceeding:** if you have not loaded `superRA:using-superra` (and, for main agents, `superRA:using-superra/references/main-agent.md`), load them now.
