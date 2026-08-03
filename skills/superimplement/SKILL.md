---
name: superimplement
description: "Run a superRA task tree autonomously through dispatched implementer and reviewer seats. Requires superRA:using-superra. Use when the researcher asks for autonomous execution or accepts a recommendation for it, and to resume mixed task statuses or verify code-complete work."
---

# superimplement — autonomous IMPLEMENT execution

Owns per-task dispatch, the implementer-reviewer loop with orchestrator-discipline filtering, and the phase-exit gate in `references/completion.md`.

**Announce at start:** "I'm using the superimplement skill to run the task tree autonomously."

## Execution Modes

Entering this skill *is* subagent mode. Interactive main-agent execution is the default on a built tree — you are here because the researcher asked for autonomous execution or accepted your recommendation of it (`using-superra/references/main-agent.md` §Execution Modes). Researcher asks to steer closely mid-flight: hand the frontier back to `using-superra/references/interactive-mode.md`.

## The Process

**Load `superRA:agent-orchestration` before selecting seats or writing any dispatch prompt.**

1. Complete Steps 0–1.
2. Execute frontier tasks through Step 2 until none require implementation, review, or fixes.
3. Close the phase through `references/completion.md`.

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
2. **Confirm there is implementation work.** Continue here when the frontier has tasks to implement, review, or fix, or reproducibility or the completion disposition is pending. All tasks already `approved`: skip dispatch, go to `references/completion.md`.
3. **Load the active domain skill(s) following the manifest**, plus any task-specific helper skills named in the active task or its ancestor chain.
4. **Repair missing context:** a frontier task lacking the inherited convention context an agent needs — distill it into the objective of the lowest governing task (`superplan/references/task-tree-design.md` §Context Distillation) and commit before dispatching.

### Step 2: Execute Tasks

**Compute the frontier with `superra task frontier`.** Execute frontier tasks singly or as same-parent bundles; use a parallel Agent-tool batch when multiple selected seats are dispatched and independent (subject to `agent-orchestration` §Workload Balancing). Serialize only when no parallel batch is available. Re-compute the frontier after each completed task or bundle.

#### Task Execution Steps

1. Select the per-task seat structure through `superRA:agent-orchestration`.
2. Execute the implementer seat. `Task:` carries one task path (e.g. `Task: data-preparation/merge`); `Tasks:` lists a bundle.
3. **NEEDS_CONTEXT or BLOCKED:** provide context and rerun the implementer seat (`agent-orchestration` §Orchestrator Duties).
4. **DONE or DONE_WITH_CONCERNS:** decide per assigned task whether an independent pass runs, per `using-superra/references/main-agent.md` §Deciding on Review. Review runs: execute the reviewer seat, naming the tier and focuses; on REVISE, adjudicate and schedule fixes per §Handling Reviewer Feedback — fix now and iterate to APPROVE, or defer and advance. No review: verify the work against the objective yourself and set `status: approved`.
5. **Approved:** in a bundle, verify every assigned task has its own `status: approved` — an aggregate approval is invalid. A child major result worth surfacing: one-line entry in the immediate parent's `## Results` linking to the child, not restating its numbers. Findings that change upcoming tasks: update those objectives and commit. Re-compute the frontier.

#### Seat execution

| Filler | Execute |
|---|---|
| `main` | `role-skill` |
| `subagent` | `dispatch` |

`role-skill` means load the selected seat's role skill and run it in this session; `dispatch` uses the template — both defined by `agent-orchestration` §Seat Assignment.

A downstream task about to inherit a structurally messy or notation-incoherent derivation from a just-approved task: dispatch `Stage: integration` against that single task before advancing.

#### Handling Reviewer Feedback (Orchestrator Discipline)

See `superRA:agent-orchestration` §Handling Reviewer Feedback (Orchestrator Discipline).

### Step 3: Close the Phase

Follow `references/completion.md` — reproducibility verification, then the 4-option completion menu.

## Orchestrator Discipline

Cross-stage orchestrator behavior: `superRA:agent-orchestration`.

**Review scope at interim checkpoints:** task-local correctness under `superRA:review-task` §Review Protocol. Codebase integration review defers to `superintegrate`.

## Autonomy and Stop Points

The autonomy contract is in `superRA:using-superra/references/main-agent.md` (main-agent only). The superimplement-specific stop points that plug into its pause classes:

- **The completion menu** (`references/completion.md`). Pre-set workflow gate — pause class 2.
- **Hard blockers from domain signals** — pause class 1. Unexpected input-quality issues during initial description, scope changes from a merge (row count shifts), validation failure against domain expectation, task tree with critical gaps, pipeline file missing for a multi-script analysis, required input unavailable.
- **Methodology / authority boundary decisions** — pause class 1. Methodology disagreement with a reviewer, a blocking finding the orchestrator wants to override, repeated reviewer disagreement across re-dispatches on the same point, validation failure of unclear domain significance, scope or definition call with no obvious right answer. A **researcher-initiated scope change** mid-execution — new task, removed task, methodology pivot, sample redefinition — routes through `superplan §User Feedback and Changing the Task Tree`.

Blocking reviewer findings are not a stop point — adjudicate and fix through the REVISE loop without asking the user.

## Agent Loads

Both roles run the `implementation` Stage (`superRA:using-superra` §Skill-Load Manifest).
