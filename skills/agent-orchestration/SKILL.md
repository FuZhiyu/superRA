---
name: agent-orchestration
description: Requires `superRA:using-superra` loaded first. Use when dispatching agents in the superRA workflow. Triggers include "dispatch N agents", "run these in parallel", "who should do the review", a multi-step workflow that needs coordination across roles, or a session handoff where workflow state must survive. Usable in any phase of the superRA workflow (PLAN / IMPLEMENT / INTEGRATE).
---

# Agent Orchestration

## Overview

You delegate tasks to specialized agents with isolated context. This skill carries the **high-level orchestrator guidance** — when to dispatch, what dispatch shape to use, how to read the resulting state from `PLAN.md`, and how to adjudicate reviewer feedback.

Parallel-dispatch independent tasks/reviews; serialize iterative loops; do trivial work inline.

## Workload Balancing

Every dispatch has spawn cost — skill-load, context hydration, per-turn
overhead. Treating every sub-task as dispatch-worthy wastes tokens and
serializes work that could run inline; treating every bundle as "split
it up" over-spawns. Pick the tier that matches the work:

### Tier 1 — Trivial: do it inline

The orchestrator executes the task itself, no subagent. Use when the
task fits in a single edit, reads no unfamiliar files, and needs no
domain skill beyond what the orchestrator already has loaded.

- Typo or comment fix in one file.
- A 2-line constant change the orchestrator has already read.
- Removing a known-dead import.

Dispatch cost > work content. Just do it.

### Tier 2 — Slightly involved: bundle and delegate

Group multiple small-to-medium tasks that share context (same file, same
skill load, same domain references) into one dispatch. One agent does the
whole bundle in a single turn.

- Three edits in the same skill file.
- A reviewer sweep over two sibling agent files.
- Updating a template plus its one consumer.

The agent pays the spawn cost once and amortizes it across the bundle.

### Tier 3 — Complicated: one dedicated agent per task

One agent owns one task. Use when the task needs deep context (cross-file
grep, multi-step refactor, full skill-load chain), or its deliverable
will be reviewed in isolation.

- A refactor that touches >5 files across skills + agents + tests.
- A new feature that requires full domain-skill engagement.
- Any task where bundle-context would exceed ~150k tokens.

### Model Tier Selection

Harnesses expose multiple tiers of model capacity (Sonnet vs. Opus in Claude Code; configurable thinking depth in Codex).

**Default to medium tier (Sonnet in Claude Code, medium thinking in Codex).** Step up to higher tier (Opus / deep thinking) when *any* of these apply:

- **Spec emerges mid-task.** The right approach only becomes clear after investigation, or the task requires re-scoping from what `PLAN.md` says.
- **Silent-error risk is high.** Results-bearing code (data transforms, methodology, drift tests) where a wrong output ships without obvious failure.
- **Adversarial first-pass review.** The failure mode is *not noticing* — capacity buys thoroughness, and lower-tier agents tend to over-comply, which breaks adversarial review. Narrow re-review of a cited fix stays on Sonnet.
- **Heavy context synthesis.** Many files/skills must be reconciled in one head; Sonnet degrades faster under context pressure.

These are defaults, not rules. Use your discretion and honor any explicit user preference.

### Rules of thumb

**≤150k tokens per agent.** When estimating: manifest skill loads (~5–15k
each), `PLAN.md` + `RESULTS.md` (5–50k depending on stage), plus per-task
file reads. If an agent's projected context exceeds ~150k, split the work
across two agents even when the individual items are small — context
thrash degrades output quality more than the cost of a second spawn.


---

## Parallelization and Worktree Isolation

Parallel dispatch is worthwhile for independent tasks or reviewers covering disjoint work. Tasks with all `Depends on:` lines satisfied and no shared mutable state are natural candidates. **Prefer background dispatch.**

Parallel agents **must** run in separate worktrees. Create each with raw git before dispatch. 

CLaude Code Agents: branching off the current branch, **not** via the `Agent` tool's `isolation: "worktree"` parameter — that branches off main's HEAD and the subagent cannot see in-flight state:

```bash
git worktree add -b "$(git branch --show-current)/parallel/<slug>" <worktree-path> HEAD
```

The `/parallel/` infix matters: the `merge-guard` hook exempts `*/parallel/*` source refs on merge-back. Pass the absolute `<worktree-path>` via the dispatch `Worktree:` field. The subagent enters via `EnterWorktree(path=...)` (or `cd` as fallback), works on whatever branch the worktree is on, and **never creates its own worktree or touches the branch name**. The `Worktree:` field in the dispatch **requires** this steering in `Additionally:`:

> *Work inside the worktree at `<path>`. Enter via `EnterWorktree` if available, otherwise `cd <path>`. Do not edit files outside. Do not merge or push — the orchestrator owns merge-back.*

**Seeding data in.** Use `worktree-data-sync` in `--mode seed`. **Always pass `--from "$(pwd)"` (or an explicit path)** — never rely on `sync_worktree_data.py`'s `--from` default, which points at the main worktree, not the orchestrator's analysis worktree.

**Harvest-out and conflicts.** `git merge --no-ff <branch>/parallel/<slug>`. Task boundaries are set ex-ante in `PLAN.md`, so parallel branches are mechanically disjoint and typically merge cleanly. If a conflict surfaces, resolve trivial adjacent edits inline; escalate material ones to the researcher. Cleanup: `git worktree remove` + `git branch -D`.

Transient state (branch names, HEAD SHAs, worktree paths) is not persisted in `PLAN.md` — git (`git worktree list`, `git branch`) is the source of truth.

---

## Dispatch Templates

Every workflow skill that dispatches an `implementer` or `reviewer` subagent uses the canonical template shape defined here. Stage-specific bodies (what goes into `Task:`, `Git range:`, and `Additionally:` for a given stage) live inside each workflow skill — those skills point here for the shape rules.

Every template opens with the canonical prefix **"Follow the standard stage-relevant workflow and load relevant skills and documents to proceed. Additionally, …"**. The prefix tells the agent that its standard Before-You-Start is in effect and it loads what `superRA:using-superra` §Skill-Load Manifest specifies for its Stage; whatever follows `Additionally,` is task-specific steering on top — focus areas, prior-round adjudication notes, warnings, or additional non-default skill/reference. The dispatch prompt does not repeat the standard protocol, never paraphrases `PLAN.md` content, and never restates checklist items the agent already reads.

**Canonical shape — required fields first, `Additionally:` anchor last:**

**Implementer:**
```
Agent(subagent_type: "superRA:implementer"):
  Stage: <stage-name>
  Task: <task pointer — e.g., "Task N in PLAN.md">
  Worktree: <absolute path>   # optional — parallel-dispatch only

  Follow the standard stage-relevant workflow and load
    relevant skills and documents to proceed. Additionally,
    <optional steering — focus area, prior-round adjudication notes, or
    warnings. Must add information on top of the default; never restate
    what the default protocol, skill-load manifest, or PLAN.md already
    says.>
```

**Reviewer:**
```
Agent(subagent_type: "superRA:reviewer"):
  Stage: <stage-name>
  Task: <task pointer>
  Git range: <BASE_SHA>..<HEAD_SHA>
  Worktree: <absolute path>   # optional — parallel-reviewer pattern only

  Follow the standard stage-relevant workflow and load
    relevant skills and documents to proceed. Additionally,
    <optional steering — focus area, prior-round adjudication notes, or
    warnings. Must add information on top of the default; never restate
    what the default protocol, skill-load manifest, or PLAN.md already
    says.>
```

**Optional steering is strictly additive.** If your `Additionally:` line only paraphrases the default protocol, the skill-load manifest, or `PLAN.md` content, delete it — the agent reads those itself. Never include `Work from:` (cwd is implicit) or restate `PLAN.md` content / manifest loads.

If a non-default skill load, an extra domain reference, or an override is required, add `Skills:` and `References:` lines between the required fields and the prefix line.

## Orchestrator Duties

These are the things the orchestrator does that no subagent does. Applies at every workflow stage.

- **Task sequencing and dispatch.** Read `PLAN.md`, decide what to dispatch next, apply §Workload Balancing to size and bundle.
- **Adjudicate reviewer feedback in place.** See §Handling Reviewer Feedback below for the full protocol.
- **Handle implementer status returns.** See §Handling Implementer Status below.
- **Edit future tasks inline** when findings from a completed task change the upcoming plan — rewrite stale text in place, do not annotate. Commit atomically with the commit that completes the triggering task.
- **Escalate to the researcher via `AskUserQuestion`** (plain text if unavailable) when stuck — hard blocker, methodology decision beyond RA authority, CRITICAL override, repeated reviewer disagreement. Log per `handoff-doc` §User Decisions Log **before** acting.

## Handling Reviewer Feedback (Orchestrator Discipline)

The reviewer is adversarial by design — it flags aggressively, and some findings will be false positives. This is the intended dynamic. **You — the orchestrator — are the arbitrator.** You made the plan, you talk to the researcher, and you have big-picture context the reviewer lacks. Your job between a REVISE verdict and re-dispatch is to independently evaluate each issue against that context, not to forward findings mechanically or defer to the reviewer's judgment.

When a reviewer returns REVISE:

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

   **Do not clear the blockquote.** For items you accept, rewrite the task steps in place; the blockquote itself stays intact. The implementer appends `→ implemented: ...` annotations on their fix pass; the reviewer deletes confirmed-fixed items on re-review. For the full annotation mechanics see `agents/implementer.md §"How You Fix Review Items on a REVISE Round"` and `agents/reviewer.md §"How You Write a Review"`. Commit the annotated `PLAN.md` atomically with the adjudication.

   This protects you in three ways: (a) the human partner can audit the override, (b) future sessions see why the reviewer's note was ignored, (c) it forces you to articulate the reasoning rather than wave it away.

4. **If you push back on the reviewer (rather than override them), re-dispatch the same reviewer with counter-evidence.** Cite the file:line that proves the reviewer wrong, the methodology section that overrides their suggestion, or the human partner conversation that established the convention. The reviewer should then either retract or escalate.

5. **If you genuinely cannot tell whether the reviewer is right, escalate via `AskUserQuestion`** (plain text if unavailable). Do not flip a coin and hope. Log per `handoff-doc` §User Decisions Log (inside the relevant task's review-notes area); commit the doc edit in the same commit as the re-dispatched implementer's fix (or as the commit that records the override).

**The orchestrator's authority:** You can override any reviewer issue with documented reasoning. You cannot silently ignore one. If you find yourself dismissing reviewer feedback without writing down why, stop — that's the slip that turns a critical filter into an excuse to skip reviews.

**The orchestrator's limits:**
- You cannot override CRITICAL severity without escalating via `AskUserQuestion` first (plain text if unavailable) and logging the researcher's decision per `handoff-doc` §User Decisions Log. CRITICAL means "will produce wrong results"; if the reviewer is wrong about that, it warrants a real discussion, not a unilateral override.
- You cannot override the same reviewer issue twice across re-dispatches. If the reviewer keeps raising the same point and you keep rejecting it, the disagreement is real — escalate via `AskUserQuestion` and let the researcher settle it, then log the answer per `handoff-doc` §User Decisions Log.

This discipline applies equally to all stages of the using superRA workflow. The orchestrator owns the final call in every loop.

## Review Status Reference

Implementer and reviewer agents own their commits and document updates — see `agents/implementer.md` and `agents/reviewer.md` for the full discipline (scope rule, inline-edit rule, stage-specific handoff). The orchestrator only needs to know how to **read** the resulting state from `PLAN.md`:

| Status line | Meaning | Orchestrator action |
|---|---|---|
| *(no line)* | Not started | Dispatch implementer |
| `IMPLEMENTED` | Code committed, awaiting review | Dispatch reviewer |
| `REVISE` | Reviewer found `[BLOCKING]` issue(s) | Adjudicate (see Handling Reviewer Feedback), re-dispatch implementer, then re-dispatch reviewer for a narrow re-review (cited fixes + dependent findings) |
| `APPROVED` | Review passed | Proceed to next task |

**A task is complete only when its status is `APPROVED`.** Do not proceed to the next task while any review has open issues that you have not adjudicated.

For direct mode (orchestrator executes the step itself), see `superRA:using-superra` §Execution Modes.

## Handling Implementer Status

Implementers return one of four statuses in their dispatch response. Applies at every Stage (implementation, drift-test, integration, documentation).

- **DONE:** Proceed to review.
- **DONE_WITH_CONCERNS:** Read the concerns. If about input quality or unexpected findings, investigate before review. If about methodology choices, note and proceed to review.
- **NEEDS_CONTEXT:** Provide missing upstream inputs, documentation, or methodology details and re-dispatch.
- **BLOCKED:** Assess the blocker:
  1. Required input not available → help locate or download.
  2. Input quality too poor → escalate via `AskUserQuestion`, log answer in `PLAN.md` before proceeding.
  3. Task requires methodology decisions → escalate via `AskUserQuestion`, log answer in `PLAN.md` before proceeding.
  4. Task too complex → break into smaller pieces or use a more capable model.

