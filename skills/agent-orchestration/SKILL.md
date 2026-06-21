---
name: agent-orchestration
description: Coordinate superRA agents and handoffs. Requires superRA:using-superra. Use to dispatch roles, run parallel agents, choose reviewers, or preserve workflow state.
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
- **Heavy context synthesis.** Many files/skills must be reconciled in one head.

For Claude agents, Fable is reserved for the most challenging, expensive tasks; use it only when the task has substantial unknowns or very high complexity.

These are defaults, not rules. Use your discretion and honor any explicit user preference.

---

## Parallelization and Worktree Isolation

Parallel dispatch is worthwhile for independent tasks or reviewers covering disjoint work. Tasks with all `Depends on:` lines satisfied and no shared mutable state are natural candidates. **Prefer background dispatch.**

Claude Code: dispatch role agents fire-and-return — never assign a `name:` to a `superRA:implementer` / `superRA:reviewer`. A named `Agent` call silently drops the `subagent_type` role spec, so the agent comes up generic.

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

At the dispatch boundary, parent objectives are inherited shared context. Dependency status does not inject sibling results; when a downstream task needs an upstream finding, output, sample, variable, or decision, dispatch steering or the downstream objective names the approved dependency `## Results` to read.

**Implementer:**
```
Agent(subagent_type: "superRA:implementer"):
  Stage: <stage-name>
  Task(s): <task path — e.g., "data-preparation/merge">
  Worktree: <absolute path>   # optional — parallel-dispatch only

  Additionally: <optional steering — focus area, prior-round adjudication notes, warnings>
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


## Orchestrator Duties

Done by the orchestrator alone, at every workflow stage:

- **Task sequencing and dispatch inside the selected frontier.** The main agent's Workflow Frontier Resolver chooses the workflow/frontier; this skill sizes, bundles, and dispatches the work inside that frontier.
- **Adjudicate reviewer feedback in place.** See §Handling Reviewer Feedback below for the full protocol.
- **Handle implementer status returns.** Re-dispatch when context is missing; escalate researcher-owned blockers through the active workflow's pause rules.
- **Escalate to the researcher via `AskUserQuestion`** (plain text if unavailable) when stuck — hard blocker, research-related decision, CRITICAL override. Fold the decision into the task objective (rewrite it fully); add a `## Revision Notes` entry if the change is non-obvious.

## Handling Reviewer Feedback

Adjudicate REVISE findings before forwarding them. Read cited code or task context only when needed to decide whether to accept, reject, escalate, or inline-verify a minor fix.

For each finding:

- **Accept** real issues. 
- **Reject** false positives by remove it from the `Review Notes`.
- **Escalate** issues that will materially change the direction of the task

If there are active `Review Notes`, redispatch implementers and reviewers for another round. When the harness keeps agents warm and the fix/re-review is small, steer the same implementer or reviewer instead of spawning a fresh agent for token efficiency. 

For a tiny fix you can verify directly, set `status: approved` inline instead.
