---
name: agent-orchestration
description: Use when about to dispatch multiple agents and unsure whether to use parallel subagents or an Agent Team; when tasks are independent vs iterative and the right dispatch pattern is not obvious; when picking teammate composition for an analysis / integration / merge / semantic-merge job; when a previous session ended mid-workflow and team context needs to be rehydrated; when choosing lead + implementer + reviewer roles for a multi-step workflow. Triggers include "dispatch N agents", "run these in parallel", "use an Agent Team for this", "who should do the review", "spawn a team for the merge", a multi-step workflow that needs coordination across roles, or a session handoff where team state must survive. Usable in any phase of the superRA workflow (PLAN / IMPLEMENT / VALIDATE / INTEGRATE).
---

# Agent Orchestration

## Overview

You delegate tasks to specialized agents with isolated context. This skill carries the **high-level orchestrator guidance** — when to dispatch, what dispatch shape to use, how to read the resulting state from `PLAN.md`, and how to adjudicate reviewer feedback. **Technical team + parallel-dispatch mechanics** (TeamCreate usage, task-graph construction, parallel-dispatch how-to, known limitations) live in `references/agent-teams.md`; load that reference when you are about to spawn or clean up a team, or fan out parallel subagents.

**Core principle:** use teams when agents need to iterate with each other; use parallel subagents when you just need results back; use a single subagent for a single focused task.

Team composition at each workflow stage is derived from the manifest — the lead spawns one teammate per stage the workflow runs, using `subagent_type: superRA:implementer` for implementer-role stages and `superRA:reviewer` for reviewer-role stages; the teammate loads what `superRA:using-superRA` §Skill-Load Manifest lists for its Stage. No per-workflow recipe is needed.

## Decision Framework

```dot
digraph decision {
    "Multiple tasks?" [shape=diamond];
    "Need iteration between agents?" [shape=diamond];
    "Agent Teams available?" [shape=diamond];
    "Parallel dispatch (Task tool)" [shape=box style=filled fillcolor=lightgreen];
    "Agent Teams (persistent sessions)" [shape=box style=filled fillcolor=lightblue];
    "Subagents with orchestrator relay" [shape=box style=filled fillcolor=lightyellow];
    "Single subagent" [shape=box];

    "Multiple tasks?" -> "Need iteration between agents?" [label="yes"];
    "Multiple tasks?" -> "Single subagent" [label="no"];
    "Need iteration between agents?" -> "Agent Teams available?" [label="yes"];
    "Need iteration between agents?" -> "Parallel dispatch (Task tool)" [label="no"];
    "Agent Teams available?" -> "Agent Teams (persistent sessions)" [label="yes"];
    "Agent Teams available?" -> "Subagents with orchestrator relay" [label="no"];
}
```

| Pattern | Use when | Mechanism |
|---------|----------|-----------|
| **Parallel dispatch** | Independent tasks, no shared state | Task tool, one-shot |
| **Agent Teams** | Creator↔reviewer iteration, feedback loops | Persistent sessions, peer messaging |
| **Orchestrator relay** | Need iteration but Teams unavailable | Subagents + orchestrator relays feedback |

**Rule of thumb:** if two agents will exchange feedback more than once, use a team (or orchestrator relay). If each agent does its work and returns a result, use parallel dispatch. For the technical mechanics of either pattern — TeamCreate usage, task-graph construction, parallel-dispatch infrastructure (worktrees, data sync), known limitations — see `references/agent-teams.md`.

## Dispatch Templates

Every workflow skill that dispatches an `implementer` or `reviewer` subagent uses the canonical template shape defined here. Stage-specific bodies (what goes into `Task:`, `Git range:`, and `Additionally:` for a given stage) live inside each workflow skill — those skills point here for the shape rules.

Every template opens with the canonical prefix **"Follow the standard stage-relevant workflow and load relevant skills and documents to proceed. Additionally, …"**. The prefix tells the agent that its standard Before-You-Start is in effect and it loads what `superRA:using-superRA` §Skill-Load Manifest specifies for its Stage; whatever follows `Additionally,` is task-specific steering on top — focus areas, prior-round adjudication notes, warnings, or additional non-default skill/reference. The dispatch prompt does not repeat the standard protocol, never paraphrases `PLAN.md` content, and never restates checklist items the agent already reads.

**Canonical shape — required fields first, `Additionally:` anchor last:**

**Implementer:**
```
Agent(subagent_type: "superRA:implementer"):
  Stage: <stage-name>
  Task: <task pointer — e.g., "Task N in PLAN.md">

  Follow the standard stage-relevant workflow and load
    relevant skills and documents to proceed. Additionally,
    <optional one-or-two-sentence steering — focus area, prior-round
    adjudication, warning, anything non-default>.
```

**Reviewer:**
```
Agent(subagent_type: "superRA:reviewer"):
  Stage: <stage-name>
  Task: <task pointer>
  Git range: <BASE_SHA>..<HEAD_SHA>

  Follow the standard stage-relevant workflow and load
    relevant skills and documents to proceed. Additionally,
    <optional steering>.
```

The agent reads `PLAN.md`, Data Inventory, Conventions, and prior results from `RESULTS.md` directly — the dispatch does not re-state them. If a non-default skill load, an extra domain reference, or an override of the standard handoff is required for this particular call, add `Skills:` and `References:` lines between the required fields and the prefix line. In Agent Teams mode, teammate pairing is set at team-spawn time (see `references/agent-teams.md`) — not inside the per-task dispatch template.

**Banned in dispatch prompts:**

- `Work from:` — the worker's cwd is the default; stating it is noise.
- `Counterpart:` — teammate pairing belongs in team-spawn config, not in the per-task dispatch.
- Free-form `Note:` fields — fold task-specific notes into the `Additionally:` tail so all task-specific steering flows through one channel.
- Re-statement of `PLAN.md` content, standard protocol, or the manifest's skill/reference loads — the agent reads those itself.

## Dispatch-Return Deltas

Dispatch prompts and status returns both carry a one-line what-changed delta so the receiving side doesn't have to diff the doc to know what moved.

**Orchestrator → worker (in the dispatch prompt):** one line describing what changed in the task since the last touch. Example: "Task 3 updated — revised Step 2; adjudication note on review item 3 accepted."

**Worker → orchestrator (in the status return):** a `**Doc edits:**` line describing what the worker changed in `PLAN.md` / `RESULTS.md` this round. The status return is a navigation aid, not a content dump — it summarizes and points at the doc for detail. Full format discipline lives in `agents/implementer.md` §Report Format and `agents/reviewer.md` §Report Format; this section is the cross-stage orchestration convention that keeps the two sides in sync.

## Handling Reviewer Feedback (Orchestrator Discipline)

The reviewer is adversarial by design — it flags aggressively, and some findings will be false positives. This is the intended dynamic. **You — the orchestrator — are the arbitrator.** You made the plan, you talk to the researcher, and you have big-picture context the reviewer lacks. Your job between a REVISE / CONDITIONAL APPROVE verdict and re-dispatch is to independently evaluate each issue against that context, not to forward findings mechanically or defer to the reviewer's judgment.

When a reviewer returns REVISE or CONDITIONAL APPROVE:

1. **Read the actual code at the cited file:line.** Do not trust the reviewer's summary. The reviewer is also a subagent and can be wrong.

2. **For each issue, classify it:**
   - **Real bug** (the code is incorrect or missing required discipline) → forward to implementer
   - **Pedantic but valid** (the issue is real but tiny — missing markdown cell on a trivial step, etc.) → decide whether the fix is worth the cycle. For minors, often yes; for cosmetic minors on a fast-iteration draft, often no
   - **Wrong** (the reviewer misread the code, missed context, or is suggesting a change that conflicts with the methodology you established with the human partner) → push back on the reviewer, do not forward to the implementer

3. **If you reject reviewer feedback, document why in place on the review item.** Append an `→ orchestrator: rejected <reason>` annotation directly under the item in the review-notes blockquote:
   ```markdown
   > **Review notes:**
   > 1. [MAJOR] Use log returns, not arithmetic. (`Code/03.py:42`)
   >    → orchestrator: rejected — methodology specifies arithmetic returns per plan header Section 2. Reviewer lacked methodology context.
   ```
   For items you are flagging for a second opinion, use `→ orchestrator: <second opinion requested> <reason>` instead. The implementer will see these annotations and leave those items alone; the reviewer will see them on re-review and either accept the override (by deleting the item) or escalate.

   This protects you in three ways: (a) the human partner can audit the override, (b) future sessions see why the reviewer's note was ignored, (c) it forces you to articulate the reasoning rather than wave it away.

4. **If you push back on the reviewer (rather than override them), re-dispatch the same reviewer with counter-evidence.** Cite the file:line that proves the reviewer wrong, the methodology section that overrides their suggestion, or the human partner conversation that established the convention. The reviewer should then either retract or escalate.

5. **If you genuinely cannot tell whether the reviewer is right, escalate via `AskUserQuestion`** (plain text if unavailable). Do not flip a coin and hope. Log the researcher's answer as a user decision in the relevant task's review-notes area per `handoff-doc` §User Decisions Log, and commit the doc edit in the same commit as the re-dispatched implementer's fix (or as the commit that records the override). The `ask-user-question-logger` hook will remind you.

**The orchestrator's authority:** You can override any reviewer issue with documented reasoning. You cannot silently ignore one. If you find yourself dismissing reviewer feedback without writing down why, stop — that's the slip that turns a critical filter into an excuse to skip reviews.

**The orchestrator's limits:**
- You cannot override CRITICAL severity without escalating via `AskUserQuestion` first (plain text if unavailable) and logging the researcher's decision per `handoff-doc` §User Decisions Log. CRITICAL means "will produce wrong results"; if the reviewer is wrong about that, it warrants a real discussion, not a unilateral override.
- You cannot override the same reviewer issue twice across re-dispatches. If the reviewer keeps raising the same point and you keep rejecting it, the disagreement is real — escalate via `AskUserQuestion` and let the researcher settle it, then log the answer per `handoff-doc` §User Decisions Log.

This discipline applies equally to `execution-workflow` (implementation review), `integration-workflow` (drift test review, integration review, doc review), `merge-workflow` (merge review, post-merge integration review), and `semantic-merge` (merge review). The orchestrator owns the final call in every loop.

## Review Status Reference

Implementer and reviewer agents own their commits and document updates — see `agents/implementer.md` and `agents/reviewer.md` for the full discipline (scope rule, inline-edit rule, stage-specific handoff). The orchestrator only needs to know how to **read** the resulting state from `PLAN.md`:

| Status line | Meaning | Orchestrator action |
|---|---|---|
| *(no line)* | Not started | Dispatch implementer |
| `IMPLEMENTED` | Code committed, awaiting review | Dispatch reviewer |
| `REVISE` | Reviewer found `[STANDARD]` issues | Adjudicate (see Handling Reviewer Feedback), then re-dispatch implementer |
| `CONDITIONAL APPROVE` | Reviewer found `[GATING]` issue(s); downstream walked and looks correct contingent on the gating fix | Adjudicate the gating item(s), re-dispatch implementer, then re-dispatch reviewer for a narrow re-review |
| `APPROVED` | Review passed | Proceed to next task |

**A task is complete only when its status is `APPROVED`.** Do not proceed to the next task while any review has open issues that you have not adjudicated.

For direct mode (orchestrator executes the step itself), see `superRA:using-superRA` §Execution Modes.

## Integration

**Skills that use Agent Teams mode** (composition derived from the manifest — see `references/agent-teams.md` for spawn mechanics):

- **superRA:execution-workflow** — analysis team (implementer + reviewer).
- **superRA:integration-workflow** — integration team (one implementer + one reviewer per stage the workflow runs: drift-test, refactoring, documentation).
- **superRA:merge-workflow** — merge team (merge-stage implementer + reviewer, plus refactoring / integration-review stages as needed).
- **superRA:semantic-merge** — merge team (merge-stage implementer + reviewer).

**When Agent Teams are unavailable:** all skills fall back to standard subagent patterns (Task tool dispatch with orchestrator-as-hub). No functionality is lost — teams are an enhancement, not a requirement.
