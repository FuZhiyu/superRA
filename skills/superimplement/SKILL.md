---
name: superimplement
description: "Implement a superRA task tree. Requires superRA:using-superra. Use to dispatch implementer/reviewer pairs, resume mixed task statuses, handle revise states, or verify code-complete work."
---

# superimplement — the IMPLEMENT phase

Owns per-task dispatch, the implementer-reviewer loop with orchestrator-discipline filtering, end-to-end reproducibility verification, and the 4-option completion menu.

**Announce at start:** "I'm using the superimplement skill to implement the task tree."

## Execution Modes

Default to subagent-driven execution on a built tree; interactive on explicit researcher request, including mid-flight. Definitions: `using-superra/references/main-agent.md §Execution Modes`.

## The Process

**Load `superRA:agent-orchestration` before selecting seats or writing any dispatch prompt.**

1. Complete Steps 0–1.
2. Execute frontier tasks through Step 2 until none require implementation or review.
3. Verify pipeline and reproducibility through Step 3.
4. Present the Step 4 completion menu.

### Step 0: Branch Check

Before any task-tree check, dispatch, or commit:

```bash
git branch --show-current
```

On `main` or `master`:
```
You're on main. I recommend creating a branch for this work:
  git checkout -b <topic>
Want me to create one?
```

User declines: proceed — that is explicit consent to work on the default branch.

### Step 0b: Task Tree Existence Check

Confirm `superRA/` exists with at least one task, is tracked, and has no uncommitted modifications:

```bash
[ -d superRA ] \
  && [ -n "$(find superRA -maxdepth 2 -name task.md -print -quit)" ] \
  && git ls-files --error-unmatch -- superRA >/dev/null 2>&1 \
  && git diff --quiet -- superRA/ \
  && git diff --quiet --cached -- superRA/
```

All conjuncts must succeed — the first two confirm a valid tree (an umbrella `task.md`, top-level task dirs, or both), the rest tracking and a clean worktree.

**Check fails: the tree is outside this workflow's valid entry conditions. Invoke `superRA:superplan` to bootstrap or repair**, proceeding through its full phases, which end by resuming on the affected frontier.

Step 0b runs after Step 0 so bootstrap commits cannot silently land on `main` / `master`.

### Step 1: Load

1. Run `superra task tree` for the full tree with statuses.
2. **Confirm there is implementation work.** Continue here when the frontier has tasks to implement, review, or fix, or reproducibility or the Step 4 disposition is pending. All tasks already `approved`: skip dispatch, start at Step 3.
3. **Load the active domain skill(s) following the manifest**, plus any task-specific helper skills named in the active task or its ancestor chain.
4. **Repair missing context:** a frontier task lacking the inherited convention context an agent needs — distill it into the objective of the lowest governing task (`superplan/references/task-tree-design.md` §Context Distillation) and commit before dispatching.

### Step 2: Execute Tasks

**Compute the frontier with `superra task frontier`.** Execute frontier tasks singly or as same-parent bundles; use a parallel Agent-tool batch when multiple selected seats are dispatched and independent (subject to `agent-orchestration` §Workload Balancing). Serialize only when no parallel batch is available. Re-compute the frontier after each completed task or bundle.

#### Task Execution Steps

1. Select the per-task seat structure through `superRA:agent-orchestration`.
2. Execute the implementer seat. `Task:` carries one task path (e.g. `Task: data-preparation/merge`); `Tasks:` lists a bundle.
3. **NEEDS_CONTEXT or BLOCKED:** provide context and rerun the implementer seat (`agent-orchestration` §Orchestrator Duties).
4. **DONE or DONE_WITH_CONCERNS:** execute the reviewer seat per assigned task, naming the tier and focuses the work warrants. On REVISE, adjudicate and schedule fixes per §Handling Reviewer Feedback — fix now and iterate to APPROVE, or defer and advance.
5. **APPROVE:** in a bundle, verify every assigned task has its own `status: approved` — an aggregate approval is invalid. A child major result worth surfacing: one-line entry in the immediate parent's `## Results` linking to the child, not restating its numbers. Findings that change upcoming tasks: update those objectives and commit. Re-compute the frontier.

#### Seat execution

| Filler | Execute |
|---|---|
| `main` | `role-skill` |
| `subagent` | `dispatch` |

`role-skill` means load the selected seat's role skill and run it in this session; `dispatch` uses the template — both defined by `agent-orchestration` §Seat Assignment.

A downstream task about to inherit a structurally messy or notation-incoherent derivation from a just-APPROVED task: dispatch `Stage: integration` against that single task before advancing.

**In interactive mode:** follow `superplan/references/interactive-mode.md`.

#### Handling Reviewer Feedback (Orchestrator Discipline)

See `superRA:agent-orchestration` §Handling Reviewer Feedback (Orchestrator Discipline).

### Step 3: Verify Pipeline and Reproducibility

After every task is `approved`, walk all three checks against actual command output, not recollection. Any failure blocks Step 4.

1. **All code committed?**
   ```bash
   git status
   ```
   Uncommitted changes: investigate (probably a missed inline edit), commit, or ask the user.

2. **Results recorded?** Read the completed task files. Fails in either direction against `implement-task` §Reporting: missing, thin, or status-report-only results for substantive work; results that restate an artifact, diff, commit body, or child task instead of pointing at it.

3. **Reproducibility verification.**
   - Multi-script pipeline runs end-to-end if the tree declares one.
   - Outputs exist and came from committed code, not ad-hoc REPL state.
   - Retained task companions are committed and pass `../using-superra/references/task-companion-files.md`.

Fix any failure before proceeding. Never present completion options for unreproducible work.

### Step 4: Present Completion Options

**Domain pre-step (theory-modeling only): notation/assumption promotion.** Scan each task's `## Results` Notation & Assumptions Ledger for entries whose symbol or assumption is not yet in the canonical Notation Conventions table. Surface any candidates via `AskUserQuestion` with a per-candidate Promote / Keep-in-ledger / Remove choice. Apply the answers: promotions are inline-edited into the canonical table and committed; keep-in-ledger candidates stay; remove deletes both the ledger entry and any in-text use (re-dispatch the implementer for code changes). Skip when the domain is not theory-modeling or every ledger says "None." Necessity gate, ledger schema, and canonical-vs-ledger split: `theory-modeling/SKILL.md` §Documentation and handoff.

**Present the 4 completion options via `AskUserQuestion`.**

```
Work complete and verified. <one line naming what the tree delivered>
Results: <dashboard URL for the affected task>
What would you like to do?

1. Proceed with integration
2. Change the task tree
3. Keep the branch as-is (I'll handle it later)
4. Discard this work
```

The folded-in answer (per the autonomy contract) goes in the first commit of whatever workflow the option dispatches to.

**Execute the user's choice:**

- **Option 1 (Proceed with integration):** invoke `superRA:superintegrate`.
- **Option 2 (Change the task tree):** re-enter `superRA:superplan §User Feedback and Changing the Task Tree` with the researcher's scope change as the trigger; it ends by resuming on the affected frontier.
- **Option 3 (Keep as-is):** report the branch name and worktree path, then stop. No cleanup.
- **Option 4 (Discard):** confirm by typed input — the user types `discard` exactly. Resolve the base branch with `git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null` (ask via `AskUserQuestion` if ambiguous), then tear down: `git checkout <base-branch>`, `git branch -D <work-branch>`, remove the worktree if the work was in one. Report what was deleted and stop.

## Orchestrator Discipline

Cross-stage orchestrator behavior: `superRA:agent-orchestration`.

**Review scope at interim checkpoints:** task-local correctness under `superRA:review-task` §Review Protocol. Codebase integration review defers to `superintegrate` (Step 4, Option 1).

## Autonomy and Stop Points

The autonomy contract is in `superRA:using-superra/references/main-agent.md` (main-agent only). The superimplement-specific stop points that plug into its pause classes:

- **Step 4 completion menu.** Pre-set workflow gate — pause class 2.
- **Hard blockers from domain signals** — pause class 1. Unexpected input-quality issues during initial description, scope changes from a merge (row count shifts), validation failure against domain expectation, task tree with critical gaps, pipeline file missing for a multi-script analysis, required input unavailable.
- **Methodology / authority boundary decisions** — pause class 1. Methodology disagreement with a reviewer, a blocking finding the orchestrator wants to override, repeated reviewer disagreement across re-dispatches on the same point, validation failure of unclear domain significance, scope or definition call with no obvious right answer. A **researcher-initiated scope change** mid-execution — new task, removed task, methodology pivot, sample redefinition — routes through `superplan §User Feedback and Changing the Task Tree`.

Blocking reviewer findings are not a stop point — adjudicate and fix through the REVISE loop without asking the user.

## Agent Loads

Both roles run the `implementation` Stage (`superRA:using-superra` §Skill-Load Manifest).
