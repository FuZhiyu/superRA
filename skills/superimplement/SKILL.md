---
name: superimplement
description: "Implement a superRA task tree. Requires superRA:using-superra. Use to dispatch implementer/reviewer pairs, resume mixed task statuses, handle revise states, or verify code-complete work."
---

# superimplement — the IMPLEMENT phase

Workflow skill for the **IMPLEMENT** and **VALIDATE** phases. Owns per-task dispatch, the implementer-reviewer loop with orchestrator-discipline filtering, end-to-end reproducibility verification, and the 4-option completion menu.

**Announce at start:** "I'm using the superimplement skill to implement the task tree."

## Execution Modes

Default to subagent-driven execution on a built tree unless the researcher explicitly requests interactive; interactive can also be requested mid-flight. The mode definitions are in `using-superra/references/main-agent.md §Execution Modes`.

## The Process

**Load `superRA:agent-orchestration` before writing any dispatch prompt.**

1. Read the task tree, compute the frontier;
2. **Go through frontier work units:**
   a. Dispatch one task or a same-parent bundle per `agent-orchestration` §Dispatch Templates. Answer context questions, re-dispatch if needed.
   b. Dispatch reviewer subagent for the same task or bundle (one comprehensive pass per task).
   c. **APPROVE** → next frontier recompute. **REVISE** → adjudicate and fix per `agent-orchestration` §Handling Reviewer Feedback. Loop until APPROVE.
3. When no selected task still requires implementation or review, verify pipeline + reproducibility (Step 3).
4. Present Step 4 completion menu; dispatch `superintegrate` on merge/PR.

### Step 0: Branch Check

Before any task-tree check, dispatch, or commit, check if on a default branch:

```bash
git branch --show-current
```

If on `main` or `master`:
```
You're on main. I recommend creating a branch for this work:
  git checkout -b <topic>
Want me to create one?
```

If the user declines, proceed — they've given explicit consent to work on the default branch.

### Step 0b: Task Tree Existence Check

After the branch check, confirm the `superRA/` directory exists with at least one task, is tracked, and has no uncommitted modifications:

```bash
[ -d superRA ] \
  && [ -n "$(find superRA -maxdepth 2 -name task.md -print -quit)" ] \
  && git ls-files --error-unmatch -- superRA >/dev/null 2>&1 \
  && git diff --quiet -- superRA/ \
  && git diff --quiet --cached -- superRA/
```

All conjuncts must succeed. The first two confirm a valid tree exists (an umbrella `task.md`, top-level task dirs, or both); the rest confirm tracking and a clean worktree.

**If the check fails, the task tree is outside this workflow's valid entry conditions. Invoke `superRA:superplan` to bootstrap or repair**, proceeding through its full phases, which end by resuming on the affected frontier.

Step 0b runs after Step 0 so bootstrap commits cannot silently land on `main` / `master`.

### Step 1: Load

1. Run `superra task tree` to see the full task tree with statuses.
2. **Confirm there is implementation work.** Continue here when the frontier has tasks to implement, review, or fix, or when reproducibility or the Step 4 disposition is still pending. If all tasks are already `approved`, skip dispatch and start at Step 3 so approved work is verified and disposition-logged before integration.
3. **Load the active domain skill(s) following the manifest.** Also load any task-specific helper skills named in the active task or its ancestor chain.
4. **Repair missing context:** when a task the frontier will touch lacks the inherited convention context an agent needs, distill it into the objective of the lowest governing task (`superplan/references/task-tree-design.md` §Context Distillation) and commit before dispatching.

### Step 2: Execute Tasks

**Compute the frontier with `superra task frontier`.** This returns leaf tasks whose dependencies are all `approved`. Tasks on the frontier may be dispatched singly, as one or more same-parent bundles, or as a parallel Agent-tool batch (subject to `agent-orchestration` §Workload Balancing). Serialize only when no parallel batch is available. Re-compute the frontier after each completed task or bundle.

#### Task Execution Steps

1. **Dispatch implementer** per `superRA:agent-orchestration`. The `Task:` field uses one task path (e.g., `Task: data-preparation/merge`); `Tasks:` lists a bundle.
2. **If NEEDS_CONTEXT or BLOCKED:** provide context and re-dispatch (`agent-orchestration` §Orchestrator Duties).
3. **Once DONE or DONE_WITH_CONCERNS:** dispatch the reviewer for one comprehensive task-local pass per assigned task. On REVISE, adjudicate per §Handling Reviewer Feedback below and iterate until APPROVE.
4. **Once APPROVE:** a generic APPROVE with no file/line citations is a red flag — re-dispatch the reviewer to cite the code paths it examined. In a bundle, verify every assigned task has its own `status: approved`; an aggregate approval is invalid. If a child produced a major result worth surfacing, roll it up selectively into the immediate parent's `## Results` with a link to the child. If findings change upcoming tasks, update those task objectives and commit. Re-compute the frontier.

When a downstream task would inherit a structurally messy or notation-incoherent derivation from a just-APPROVED task, dispatch `Stage: integration` against that single task before advancing.

**In interactive mode:** the main agent executes the task directly and runs the canvas loop — self-review always, independent review elective — per `superplan/references/interactive-mode.md`.


#### Handling Reviewer Feedback (Orchestrator Discipline)

See `superRA:agent-orchestration` §Handling Reviewer Feedback (Orchestrator Discipline).

### Step 3: Verify Pipeline and Reproducibility

After every task is `approved`, verify the work end-to-end before presenting completion options. Walk all four checks against actual command output, not recollection; do not proceed if any fails.

1. **All code committed?**
   ```bash
   git status
   ```
   If uncommitted changes exist: investigate (probably an agent missed an inline-edit), commit, or ask the user.

2. **Results recorded?** Read the completed task files. Treat missing, thin, or status-report-only major results as a failed gate: every completed task with substantive work needs findings, key numbers, caveats, and verification evidence in `## Results`. Parent `## Results` sections should summarize direct children selectively, not recursively copy every finding. Figure attachments in each task's `attachments/` directory are committed.

3. **Reproducibility verification.**
   - Multi-script pipeline runs end-to-end if the task tree declares one.
   - Outputs exist and were generated from committed code, not ad-hoc REPL state.

4. **Deferred MINORs resolved?** Check task `## Review Notes` sections for any remaining MINOR items. If a MINOR was deferred across tasks and never addressed, resolve it now (dead code removal, missing documentation, format compliance) or document it as an accepted limitation in the relevant task's `## Results`.

If any check fails: fix it before proceeding. Do not present completion options for unreproducible work.

**Once all four checks pass:** proceed to the Step 4 completion menu.

### Step 4: Present Completion Options

**Domain pre-step (theory-modeling only): notation/assumption promotion.** Before presenting the completion menu, when the active domain is theory-modeling, scan each task's `## Results` Notation & Assumptions Ledger and collect every entry whose symbol or assumption is not yet in the canonical Notation Conventions table. If any candidates exist, surface them via `AskUserQuestion` with a per-candidate Promote / Keep-in-ledger / Remove choice. Apply the researcher's answers: promotions are inline-edited into the canonical table and committed; keep-in-ledger candidates stay where they are; remove decisions delete both the ledger entry and any in-text use (re-dispatch the implementer if code changes are needed). Skip this pre-step entirely when the domain is not theory-modeling or when every ledger says "None." The semantics of the necessity gate, the ledger schema, and the canonical-vs-ledger split are owned by `theory-modeling/SKILL.md` §Documentation and handoff — do not restate them here.

**Present the 4 completion options via `AskUserQuestion`.**

```
Work complete and verified. Here are the results summary:
<summarize the results>
What would you like to do?

1. Proceed with integration
2. Change the task tree
3. Keep the branch as-is (I'll handle it later)
4. Discard this work
```

The folded-in answer (per the autonomy contract) is included in the first commit of whatever workflow the option dispatches to.

**Execute the user's choice:**

- **Option 1 (Proceed with integration):** Invoke `superRA:superintegrate`.
- **Option 2 (Change the task tree):** Re-enter `superRA:superplan §User Feedback and Changing the Task Tree` — treat the researcher's scope change as the trigger; it ends by resuming on the affected frontier.
- **Option 3 (Keep as-is):** Report the branch name and worktree path back to the user, then stop. Do not clean up.
- **Option 4 (Discard):** Confirm with the user by typed input — they must type the word `discard` exactly. Resolve the base branch with `git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null` (ask via `AskUserQuestion` if ambiguous), then perform the teardown: `git checkout <base-branch>`, `git branch -D <work-branch>`, and — if the work was in a worktree, remove the worktree. Stop after the branch and worktree are removed. Report what was deleted.

## Orchestrator Discipline

Cross-stage orchestrator behavior lives in `superRA:agent-orchestration`.

**Workflow-specific review scope at interim checkpoints:** Task-local correctness under `agents/reviewer.md` §Review Protocol. Codebase integration review is deferred to `superintegrate` (dispatched at Step 4 when the user chooses Option 1 — Proceed with integration).

## Autonomy and Stop Points

The autonomy contract is in `superRA:using-superra/references/main-agent.md` (main-agent only). This section lists the **superimplement-specific stop points** that plug into its pause classes.

- **Step 4 completion menu.** Pre-set workflow gate — pause class 2 (see Step 4 above for the four options).
- **Hard blockers from domain signals.** Unexpected input-quality issues during initial description, scope changes from a merge (row count shifts), validation failure against domain expectation, task tree with critical gaps, pipeline file missing for a multi-script analysis, required input unavailable. Pause class 1 in the autonomy contract.
- **Methodology / authority boundary decisions.** Methodology disagreement with a reviewer, CRITICAL severity issue the orchestrator wants to override, repeated reviewer disagreement across re-dispatches on the same point, validation failure of unclear domain significance, scope or definition call with no obvious right answer. **Researcher-initiated scope change** mid-execution — new task, removed task, methodology pivot, sample redefinition — route through `superplan §User Feedback and Changing the Task Tree`. Pause class 1 in the autonomy contract.

Blocking reviewer findings are not a stop point — adjudicate and fix through the REVISE loop without asking the user.

## Agent Loads

Both roles run the `implementation` Stage (`superRA:using-superra` §Skill-Load Manifest).
