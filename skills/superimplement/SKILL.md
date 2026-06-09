---
name: superimplement
description: Requires `superRA:using-superra` loaded first. Use when you have a `superRA/` task tree and are ready to implement its tasks; when a plan has been approved and you need per-task implementation with an implementer-reviewer pair; when resuming work on a plan where some tasks are `implemented`, some `revise`, and some not started; when an analysis is code-complete and you want to verify reproducibility and present completion options (merge / PR / keep / discard). Triggers include "execute the plan", "run task N", "implement this plan", "finish this analysis", a branch with an approved plan but no code yet, or a `revise` state that needs orchestrator adjudication before re-dispatch.
---

# superimplement — the IMPLEMENT phase

Workflow skill for the **IMPLEMENT** and **VALIDATE** phases. Owns per-task dispatch, the implementer-reviewer loop with orchestrator-discipline filtering, end-to-end reproducibility verification, and the 4-option completion menu.

**Announce at start:** "I'm using the superimplement skill to implement this plan."

## Execution Modes

Default is **subagent mode**: one implementer subagent per task, fresh context per task. Fall back to **direct mode** when the harness lacks subagents, the user requests it, or tasks are trivial. Direct mode still dispatches reviewer subagents after each task — review is never skipped.

## The Process

**Load `superRA:agent-orchestration` before writing any dispatch prompt.**

1. Read the task tree, compute the frontier;
2. **Go through tasks:**
   a. Dispatch implementer subagent. Answer context questions, re-dispatch if needed.
   b. Dispatch reviewer subagent (one comprehensive pass).
   c. **APPROVE** → next task. **REVISE** → fix reviewer-found blocking findings → narrow re-review (cited fixes + dependent findings). Loop until APPROVE.
3. When no selected task still requires implementation or review, verify pipeline + reproducibility (Step 3).
4. Present Step 4 completion menu; dispatch `superintegrate` on merge/PR.

### Step 0: Branch Check

Before any task-tree check, dispatch, or commit, check if on a default branch:

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

### Step 0b: Task Tree Existence Check

After the branch check, confirm the `superRA/` directory exists with a root `task.md`, is tracked, and has no uncommitted modifications:

```bash
[ -f superRA/task.md ] \
  && git ls-files --error-unmatch superRA/task.md >/dev/null 2>&1 \
  && git diff --quiet -- superRA/ \
  && git diff --quiet --cached -- superRA/
```

All conjuncts must succeed. The first confirms the root task exists; the rest confirm tracking and a clean worktree.

**If the check fails, the task tree is outside this workflow's valid entry conditions. Invoke `superRA:superplan` to bootstrap or repair**, proceeding through its full phases. After the repair commit, run `using-superRA/references/main-agent.md` §Workflow Frontier Resolver to choose the next entry point.

Step 0b runs after Step 0 so bootstrap commits cannot silently land on `main` / `master`.

### Step 1: Load and Review Plan

1. Read the root `superRA/task.md` and run `superra task tree` to see the full task tree with statuses.
2. **Resolve entry** via `using-superRA/references/main-agent.md` §Workflow Frontier Resolver if not already done; continue here only when it selects implementation, review, reproducibility verification, or the Step 4 disposition. If all tasks are already `approved`, skip dispatch and start at Step 3 so approved work is verified and disposition-logged before integration.
3. **Load the active domain skill(s) following the manifest.** Also load any task-specific helper skills named in the active task or its ancestor chain.
4. **Read the scoped `### Conventions` / `### Context` / `### Constraints` context in the active task's objective and its ancestor chain** (anatomy: `task-system/references/task-file-contract.md` §Context Inheritance). When a task the frontier will touch lacks the inherited convention context an agent needs, walk the relevant docs and distill it into the objective of the lowest governing task now (`superplan/references/task-tree-design.md` §Context Distillation) — commit before dispatching subagents.
5. Review the task tree critically — identify any questions or concerns:
   - Are data sources / inputs available and accessible?
   - Are the dependencies in the right order?
   - Is the pipeline file included (for multi-script analyses)?
   - Does any task conflict with a project convention you found in step 4?
6. Review completed tasks' `## Results` sections for context (if resuming).
7. If concerns: raise them with your human partner before starting.
8. If no concerns: proceed.

### Step 2: Execute Tasks

**Compute the frontier with `superra task frontier`.** This returns leaf tasks whose dependencies are all `approved`. Tasks on the frontier may be dispatched as a single parallel Agent-tool batch (subject to `agent-orchestration` §Workload Balancing). Serialize only when no parallel batch is available. Re-compute the frontier after each task completes.

#### Task Execution Steps

1. **Dispatch implementer** per `superRA:agent-orchestration`. The `Task:` field uses the task path (e.g., `Task: data-preparation/merge`).
2. **If NEEDS_CONTEXT or BLOCKED:** provide context and re-dispatch (see Handling Implementer Status below).
3. **Once DONE or DONE_WITH_CONCERNS:** dispatch the reviewer for one comprehensive task-local pass. On REVISE, adjudicate per §Handling Reviewer Feedback below and iterate until APPROVE.
4. **Once APPROVE:** a generic APPROVE with no file/line citations is a red flag — re-dispatch the reviewer to cite the code paths it examined. If the child produced a major result worth surfacing, roll it up selectively into the immediate parent's `## Results` with a link to the child. If findings change upcoming tasks, update those task objectives and commit. Proceed to next task.

When a downstream task would inherit a structurally messy or notation-incoherent derivation from a just-APPROVED task, dispatch `Stage: integration` against that single task before advancing.

**In direct mode:** the main agent does Steps 1–2 directly; Steps 3–4 still dispatch reviewer subagents unless the user overrides.


#### Handling Reviewer Feedback (Orchestrator Discipline)

See `superRA:agent-orchestration` §Handling Reviewer Feedback (Orchestrator Discipline).

### Step 3: Verify Pipeline and Reproducibility

After every task is `approved`, verify the work end-to-end before presenting completion options. Walk all five checks against actual command output, not recollection; do not proceed if any fails.

1. **All code committed?**
   ```bash
   git status
   ```
   If uncommitted changes exist: investigate (probably an agent missed an inline-edit), commit, or ask the user.

2. **Task tree up to date?** Run `superra task tree` and confirm all tasks show `approved`. No tasks stuck in `implemented` or `revise`. Major outcomes are captured in task `## Results` sections, with parent rollups where a higher-level monitoring view needs them.

3. **Results recorded?** Read the completed task files. Treat missing, thin, or status-report-only major results as a failed gate: every completed task with substantive work needs findings, key numbers, caveats, and verification evidence in `## Results`. Parent `## Results` sections should summarize direct children selectively, not recursively copy every finding. Figure attachments in each task's `attachments/` directory are committed.

4. **Reproducibility verification.**
   - Multi-script pipeline runs end-to-end if the plan declares one.
   - Outputs exist and were generated from committed code, not ad-hoc REPL state.

5. **Deferred MINORs resolved?** Check task `## Review Notes` sections for any remaining MINOR items. If a MINOR was deferred across tasks and never addressed, resolve it now (dead code removal, missing documentation, format compliance) or document it as an accepted limitation in the relevant task's `## Results`.

If any check fails: fix it before proceeding. Do not present completion options for unreproducible work.

**Once all five checks pass:** proceed to the Step 4 completion menu.

### Step 4: Present Completion Options

**Domain pre-step (theory-modeling only): notation/assumption promotion.** Before presenting the completion menu, when the active domain is theory-modeling, scan each task's `## Results` Notation & Assumptions Ledger and collect every entry whose symbol or assumption is not yet in the root task.md's Notation Conventions table. If any candidates exist, surface them via `AskUserQuestion` with a per-candidate Promote / Keep-in-ledger / Remove choice. Apply the researcher's answers: promotions are inline-edited into the canonical table and committed; keep-in-ledger candidates stay where they are; remove decisions delete both the ledger entry and any in-text use (re-dispatch the implementer if code changes are needed). Skip this pre-step entirely when the domain is not theory-modeling or when every ledger says "None." The semantics of the necessity gate, the ledger schema, and the canonical-vs-ledger split are owned by `theory-modeling/SKILL.md` §Documentation and handoff — do not restate them here.

**Present the 4 completion options via `AskUserQuestion` when available** (plain-text fallback otherwise).

```
Work complete and verified. Here are the results summary:
<summarize the results>
What would you like to do?

1. Proceed with integration
2. Change the plan
3. Keep the branch as-is (I'll handle it later)
4. Discard this work
```

Fold the researcher's answer into the relevant task objective (rewriting it to be self-sufficient with the new context) before executing the choice, included in the first commit of whatever workflow the option dispatches to.

**Execute the user's choice:**

- **Option 1 (Proceed with integration):** Invoke `superRA:superintegrate`.
- **Option 2 (Change the plan):** Re-enter `superRA:superplan §User Feedback and Changing the Task Tree` — treat the researcher's scope change as the trigger; after the plan edit commit, run the main-agent Workflow Frontier Resolver to choose the next entry point.
- **Option 3 (Keep as-is):** Report the branch name and worktree path back to the user, then stop. Do not clean up.
- **Option 4 (Discard):** Confirm with the user by typed input — they must type the word `discard` exactly. Resolve the base branch with `git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null` (ask via `AskUserQuestion` if ambiguous), then perform the teardown: `git checkout <base-branch>`, `git branch -D <analysis-branch>`, and — if the analysis was in a worktree, remove the worktree. Stop after the branch and worktree are removed. Report what was deleted.

## Orchestrator Discipline

Cross-stage orchestrator behavior lives in `superRA:agent-orchestration`.

**Workflow-specific review scope at interim checkpoints:** Task-local correctness under `agents/reviewer.md` §Review Protocol. Codebase integration review is deferred to `superintegrate` (dispatched at Step 4 when the user chooses Option 1 — Proceed with integration).

## Autonomy and Stop Points

The autonomy contract is in `superRA:using-superra/references/main-agent.md` (main-agent only). This section lists the **superimplement-specific stop points** that plug into its pause classes.

- **Step 4 completion menu.** User-defined workflow milestone (see Step 4 above for the four options).
- **Hard blockers from domain signals.** Unexpected input-quality issues during initial description, scope changes from a merge (row count shifts), validation failure against domain expectation, plan with critical gaps, pipeline file missing for a multi-script analysis, required input unavailable. Pause class (1) in the autonomy contract.
- **Methodology / authority boundary decisions.** Methodology disagreement with a reviewer, CRITICAL severity issue the orchestrator wants to override, repeated reviewer disagreement across re-dispatches on the same point, validation failure of unclear domain significance, scope or definition call with no obvious right answer. **Researcher-initiated scope change** mid-execution — new task, removed task, methodology pivot, sample redefinition — route through `superplan §User Feedback and Changing the Task Tree`; after the plan edit commit, run the Workflow Frontier Resolver. Pause class (2) in the autonomy contract.

Every stop above: stop and `AskUserQuestion` (plain text if unavailable); fold the answer into the relevant task objective **before** acting on it.

## Agent Loads

Both roles run the `implementation` Stage (`superRA:using-superra` §Skill-Load Manifest).

## Red Flags

- Skipping review, even in direct mode.
- Advancing past a task whose review has open issues or whose status is not `approved` — a REVISE task is complete only once re-review promotes it to APPROVED.
- Accepting "looks fine" without verification, or ignoring implementer input-quality or methodology concerns.
- Asking the user whether to fix blocking findings instead of iterating REVISE → fix → re-review automatically.
