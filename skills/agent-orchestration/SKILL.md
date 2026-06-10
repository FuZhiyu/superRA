---
name: agent-orchestration
description: Requires `superRA:using-superra` loaded first. Use when dispatching agents in the superRA workflow. Triggers include "dispatch N agents", "run these in parallel", "who should do the review", a multi-step workflow that needs coordination across roles, or a session handoff where workflow state must survive. Usable in any phase of the superRA workflow (PLAN / IMPLEMENT / INTEGRATE).
---

# Agent Orchestration

## Overview

You delegate tasks to specialized agents with isolated context. Parallel-dispatch independent tasks/reviews; serialize iterative loops; do trivial work inline.

## Workload Balancing

Every dispatch has spawn cost — skill-load, context hydration, per-turn overhead. Pick the tier that matches the work:

### Tier 1 — Trivial: do it inline

The orchestrator executes the task itself, no subagent. Use when the task fits in a single edit, reads no unfamiliar files, and needs no domain skill beyond what the orchestrator already has loaded.

- Typo or comment fix in one file.
- A 2-line constant change the orchestrator has already read.
- Removing a known-dead import.

Dispatch cost > work content. Just do it.

### Tier 2 — Slightly involved: bundle and delegate

Group multiple small-to-medium tasks that share context (same stage, same domain, same parent, shared files or references) into one dispatch. One agent does the whole bundle in a single turn.

- Three edits in the same skill file.
- A reviewer sweep over two sibling agent files.
- Updating a template plus its one consumer.

The agent pays the spawn cost once and amortizes it across the bundle. In a `superRA/` task tree, bundling is spawn-cost amortization only: each bundled task remains its own contract, status, results section, and review verdict.

### Tier 3 — Complicated: one dedicated agent per task

One agent owns one task. Use when the task needs deep context (cross-file grep, multi-step refactor, full skill-load chain), or its deliverable will be reviewed in isolation.

- A refactor that touches >5 files across skills + agents + tests.
- A new feature that requires full domain-skill engagement.
- Any task where bundle-context would exceed ~150k tokens.

### Model Tier Selection

Harnesses expose multiple tiers of model capacity (Sonnet vs. Opus in Claude Code; configurable thinking depth in Codex).

**Default to medium tier (Sonnet in Claude Code, medium thinking in Codex).** Step up to higher tier (Opus / deep thinking) when *any* of these apply:

- **Spec emerges mid-task.** The right approach only becomes clear after investigation, or the task requires re-scoping from what the objective says.
- **Silent-error risk is high.** Results-bearing code (data transforms, methodology, drift tests) where a wrong output ships without obvious failure.
- **Adversarial first-pass review.** The failure mode is *not noticing* — capacity buys thoroughness, and lower-tier agents tend to over-comply, which breaks adversarial review. Narrow re-review of a cited fix stays on Sonnet.
- **Heavy context synthesis.** Many files/skills must be reconciled in one head; Sonnet degrades faster under context pressure.

For Claude agents, Fable is reserved for the most challenging, expensive tasks; use it only when the task has substantial unknowns or very high complexity.

These are defaults, not rules. Use your discretion and honor any explicit user preference.

### Rules of thumb

**≤150k tokens per agent.** When estimating: manifest skill loads (~5–15k each), task tree context (ancestor chain + sibling deps, 2–20k depending on depth), plus per-task file reads. If an agent's projected context exceeds ~150k, split the work across two agents even when the individual items are small — context thrash degrades output quality more than the cost of a second spawn.

---

## Parallelization and Worktree Isolation

Parallel dispatch is worthwhile for independent tasks or reviewers covering disjoint work. Tasks with all `Depends on:` lines satisfied and no shared mutable state are natural candidates. **Prefer background dispatch.**

Parallel agents **must** run in separate worktrees, one per agent, created before dispatch. The branch name carries a `/parallel/` infix (`<current-branch>-agent/parallel/<slug>`) so the `merge-guard` hook exempts the source ref on merge-back. Create, place, and remove worktrees per `references/worktree-harness-fallback.md`. In Claude Code, do **not** use the `Agent` tool's `isolation: "worktree"` parameter — it branches off main's HEAD, so the subagent cannot see in-flight state; branch off the current branch instead.

Pass the absolute worktree path via the dispatch `Worktree:` field, plus this `Additionally:` steering:

> *Work inside the worktree at `<path>`. Enter via `EnterWorktree` if available, otherwise `cd <path>`. Do not edit files outside. Do not merge or push — the orchestrator owns merge-back.*

**Seeding data in.** Use `worktree-data-sync` in `--mode seed`. **Always pass `--from "$(pwd)"` (or an explicit path)** — `sync_worktree_data.py`'s `--from` default points at the main worktree, not the orchestrator's analysis worktree.

**Harvest-out and conflicts.** `git merge --no-ff <current-branch>-agent/parallel/<slug>`. Task boundaries are set ex-ante, so parallel branches are mechanically disjoint and typically merge cleanly. Resolve trivial adjacent conflicts inline; escalate material ones to the researcher.

Transient state (branch names, HEAD SHAs, worktree paths) is not persisted in the task tree — git (`git worktree list`, `git branch`) is the source of truth.

---

## Dispatch Templates

Every workflow skill that dispatches a task-scoped `implementer` or `reviewer` subagent uses the canonical template shape defined here. Stage-specific bodies (what goes into `Task:`, `Git range:`, and `Additionally:` for a given stage) live inside each workflow skill — those skills point here for the shape rules. Branch-level `Stage: sync` dispatches generic sync author / sync reviewer agents with explicit `semantic-merge` mode references.

Templates carry required fields plus an optional `Additionally:` line for task-specific steering: focus areas, prior-round adjudication notes, warnings, or non-default skill/reference overrides. Omit `Additionally:` when there is no extra steering; never use it to restate role protocol, manifest loads, or task content. Never include `Work from:` — cwd is implicit.

Use a bundle only for same-stage, same-domain, same-parent frontier leaves that share context and are simple enough for one agent. Keep dependent siblings out of the same implementation bundle unless the upstream task is already `approved`; `depends_on` sequences tasks whose outputs or findings are prerequisites.

Bundle dispatches use `Tasks:` instead of `Task:`. The assignee runs the role protocol separately for each listed task: `superra task read` per path, task-local `## Results` or `## Review Notes`, independent status transitions, and independent commit evidence. A reviewer may review a bundle in one dispatch, but cannot approve it as an aggregate; every listed task must reach its own verdict.

At the dispatch boundary, parent objectives are inherited shared context. Dependency status does not inject sibling results; when a downstream task needs an upstream finding, output, sample, variable, or decision, dispatch steering or the downstream objective names the approved dependency `## Results` to read.

**Implementer:**
```
Agent(subagent_type: "superRA:implementer"):
  Stage: <stage-name>
  Task: <task path — e.g., "data-preparation/merge">
  Worktree: <absolute path>   # optional — parallel-dispatch only

  Additionally: <optional steering — focus area, prior-round adjudication notes, warnings>
```

**Bundled implementer:**
```
Agent(subagent_type: "superRA:implementer"):
  Stage: <stage-name>
  Tasks:
    - <task path>
    - <task path>
  Worktree: <absolute path>   # optional — parallel-dispatch only

  Additionally: <optional shared steering plus any per-task notes>
```

**Reviewer:**
```
Agent(subagent_type: "superRA:reviewer"):
  Stage: <stage-name>
  Task: <task path — e.g., "data-preparation/merge">
  Git range: <BASE_SHA>..<HEAD_SHA>
  Worktree: <absolute path>   # optional — parallel-reviewer pattern only

  Additionally: <optional steering — focus area, prior-round adjudication notes, warnings>
```

**Bundled reviewer:**
```
Agent(subagent_type: "superRA:reviewer"):
  Stage: <stage-name>
  Tasks:
    - <task path>
    - <task path>
  Git range: <BASE_SHA>..<HEAD_SHA>
  Worktree: <absolute path>   # optional — parallel-reviewer pattern only

  Additionally: <optional shared steering plus any per-task notes>
```

**Planning reviewer:**
```
Agent(subagent_type: "superRA:reviewer"):
  Stage: planning-review
  Task: <task path or root>
  Review mode: handoff-readiness | design-review
  Context: <exploration synthesis, inline or path>
  Review target: assigned task/subtree design, not implementation diff
```

When useful, run `superra task comment list <task-path>` to fold unresolved researcher comments into `Additionally:` steering.

For a non-default skill load, an extra domain reference, or an override, add `Skills:` and `References:` lines between the required fields and `Additionally:`.

## Orchestrator Duties

Done by the orchestrator alone, at every workflow stage:

- **Task sequencing and dispatch inside the selected frontier.** The main agent's Workflow Frontier Resolver chooses the workflow/frontier; this skill sizes, bundles, and dispatches the work inside that frontier.
- **Adjudicate reviewer feedback in place.** See §Handling Reviewer Feedback below for the full protocol.
- **Handle implementer status returns.** See §Handling Implementer Status below.
- **Edit future tasks inline** when findings from a completed task change the upcoming plan — rewrite stale text in the relevant task's `task.md` in place, do not annotate. Commit atomically with the commit that completes the triggering task.
- **Escalate to the researcher via `AskUserQuestion`** (plain text if unavailable) when stuck — hard blocker, methodology decision beyond RA authority, CRITICAL override, repeated reviewer disagreement. Fold the decision into the task objective (rewrite it fully); add a `## Revision Notes` entry if the change is non-obvious.

## Handling Reviewer Feedback (Orchestrator Discipline)

The reviewer is adversarial by design — it flags aggressively, and some findings will be false positives. **You — the orchestrator — are the arbitrator.** You made the plan, you talk to the researcher, and you have big-picture context the reviewer lacks. Between a REVISE verdict and re-dispatch, independently evaluate each issue against that context, rather than forwarding findings mechanically or deferring to the reviewer.

When a reviewer returns REVISE:

1. **Read the actual code at the cited file:line.** Do not trust the reviewer's summary. The reviewer is also a subagent and can be wrong.

2. **For each issue, classify it:**
   - **Real bug** (the code is incorrect or missing required discipline) → forward to implementer
   - **Pedantic but valid** (the issue is real but tiny — missing markdown cell on a trivial step, etc.) → decide whether the fix is worth the cycle. For minors, often yes; for cosmetic minors on a fast-iteration draft, often no
   - **Wrong** (the reviewer misread the code, missed context, or is suggesting a change that conflicts with the methodology you established with the human partner) → push back on the reviewer, do not forward to the implementer

3. **If you reject reviewer feedback, document why in place on the review item.** Append an `→ orchestrator: rejected <reason>` annotation directly under the item in the task's `## Review Notes`:
   ```markdown
   ## Review Notes

   > 1. [MAJOR] Use log returns, not arithmetic. ([Code/03.py:42](Code/03.py#L42))
   >    → orchestrator: rejected — methodology specifies arithmetic returns per the ancestor objective's scoped conventions. Reviewer lacked methodology context.
   ```
   For items you are flagging for a second opinion, use `→ orchestrator: <second opinion requested> <reason>` instead. The implementer will see these annotations and leave those items alone; the reviewer will see them on re-review and either accept the override (by deleting the item) or escalate.

   **Do not clear the review notes.** For items you accept, rewrite the task's approach in place; the review notes stay intact. The implementer appends `→ implemented: ...` annotations on their fix pass; the reviewer deletes confirmed-fixed items on re-review. For the full annotation mechanics see `agents/implementer.md §"How You Fix Review Items on a REVISE Round"` and `agents/reviewer.md §"How You Write a Review"`. Commit the annotated `task.md` atomically with the adjudication.

4. **If you push back on the reviewer (rather than override them), re-dispatch the same reviewer with counter-evidence.** Cite the file:line that proves the reviewer wrong, the methodology section that overrides their suggestion, or the human partner conversation that established the convention. The reviewer should then either retract or escalate.

5. **If you genuinely cannot tell whether the reviewer is right, escalate via `AskUserQuestion`.** Fold the decision into the task objective (rewrite it fully); add a `## Revision Notes` entry if the change is non-obvious. Commit the edit in the same commit as the re-dispatched implementer's fix.

**Authority:** Override any reviewer issue with documented reasoning, but never silently ignore one.

**Limits:**
- Do not override CRITICAL severity without escalating via `AskUserQuestion` first — CRITICAL means "will produce wrong results", which warrants a real discussion rather than a unilateral override. Fold the decision into the task objective; add a revision note.
- Do not override the same reviewer issue twice across re-dispatches. A repeated reject of a repeated finding is a real disagreement — escalate via `AskUserQuestion` and fold the answer into the task objective.

## Review Status Reference

Implementer and reviewer agents own their commits and document updates (see `agents/implementer.md` and `agents/reviewer.md`). The orchestrator reads the resulting state from task frontmatter:

| `status:` | Meaning | Orchestrator action |
|---|---|---|
| `not-started` | Planned, no work yet | Dispatch implementer |
| `in-progress` | Being worked on | Wait for implementer or re-dispatch |
| `implemented` | Code committed and ready for review | Dispatch reviewer |
| `revise` | Reviewer found blocking issue(s) | Adjudicate (see Handling Reviewer Feedback), re-dispatch implementer, then re-dispatch reviewer for a narrow re-review (cited fixes + dependent findings) |
| `approved` | Review passed | Proceed to next task |
| `archived` | No longer relevant; removed from scope | Not dispatchable; dependency treated as satisfied — dependents may proceed. |
| `postponed` | Deferred and parked off the frontier; not deleted | Not dispatchable; its dependents are blocked until resumed. Set back to `not-started` to resume. |

**A task is complete only when its `status` is `approved`.** Do not proceed to the next task while any review has open issues that you have not adjudicated.

For direct mode (orchestrator executes the step itself), see `superRA:using-superra` §Execution Modes.

## Handling Implementer Status

Act on the implementer's returned status, at every Stage (implementation, drift-test, integration, documentation):

- **DONE:** Proceed to review.
- **DONE_WITH_CONCERNS:** Read the concerns. If about input quality or unexpected findings, investigate before review. If about methodology choices, note and proceed to review.
- **NEEDS_CONTEXT:** Provide missing upstream inputs, documentation, or methodology details and re-dispatch.
- **BLOCKED:** Assess the blocker:
  1. Required input not available → help locate or download.
  2. Input quality too poor → escalate via `AskUserQuestion`, fold the decision into the task objective before proceeding.
  3. Task requires methodology decisions → escalate via `AskUserQuestion`, fold the decision into the task objective before proceeding.
  4. Task too complex → break into subtasks or use a more capable model.
