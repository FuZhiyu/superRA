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

Default to the medium tier (Sonnet in Claude Code, medium thinking in Codex). Step up (Opus / deep thinking) when any of these apply: the spec emerges mid-task rather than from the objective; silent-error risk is high (results-bearing code where a wrong output ships without obvious failure); the dispatch is an adversarial first-pass review (lower-tier agents over-comply; narrow re-review of a cited fix stays medium); or heavy context synthesis reconciles many files/skills in one head. Fable is reserved for the most challenging, expensive tasks. These are defaults, not rules — honor any explicit user preference.

---

## Parallelization and Worktree Isolation

Before dispatching agents in parallel or isolating an agent in its own worktree, load `references/parallel-dispatch.md` — parallel agents require per-agent worktrees, and the seeding and harvest rules live there.

---

## Dispatch Templates

Every workflow skill that dispatches a task-scoped `implementer` or `reviewer` subagent uses the canonical template shape defined here. Stage-specific bodies (what goes into `Task:`, `Git range:`, and `Additionally:` for a given stage) live inside each workflow skill — those skills point here for the shape rules. Branch-level `Stage: sync` dispatches generic sync author / sync reviewer agents with explicit `semantic-merge` mode references.

Templates carry required fields plus an optional `Additionally:` line for task-specific steering: focus areas, prior-round adjudication notes, warnings, or non-default skill/reference overrides. Omit `Additionally:` when there is no extra steering; never use it to restate role protocol, manifest loads, or task content. Never include `Work from:` — cwd is implicit.

Claude Code: dispatch role agents fire-and-return — never assign a `name:` to a `superRA:implementer` / `superRA:reviewer`. A named `Agent` call silently drops the `subagent_type` role spec, so the agent comes up generic.

Use a bundle only for same-stage, same-domain, same-parent frontier leaves that share context and are simple enough for one agent. Keep dependent siblings out of the same implementation bundle unless the upstream task is already `approved`; `depends_on` sequences tasks whose outputs or findings are prerequisites.

At the dispatch boundary, parent objectives are inherited shared context; sibling results are not injected. When a downstream task consumes an upstream result, dispatch steering or the downstream objective names the approved dependency `## Results` to read.

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

- **Task sequencing and dispatch inside the selected frontier.** The main agent selects which frontier to work; this skill sizes, bundles, and dispatches the work inside it.
- **Adjudicate reviewer feedback in place.** See §Handling Reviewer Feedback below for the full protocol.
- **Handle implementer status returns.** Re-dispatch when context is missing; escalate researcher-owned blockers through the active workflow's pause rules.
- **Escalate to the researcher via `AskUserQuestion`** (plain text if unavailable) when stuck — hard blocker, research-related decision, CRITICAL override. Fold the decision into the task objective (rewrite it fully); add a `## Revision Notes` entry if the change is non-obvious.

## Handling Reviewer Feedback

Adjudicate REVISE findings before forwarding them. Read cited code or task context only when needed to decide whether to accept, reject, escalate, or inline-verify a minor fix.

For each finding:

- **Accept** real issues. 
- **Reject** false positives by remove it from the `Review Notes`.
- **Escalate** issues that will materially change the direction of the task

If there are active `Review Notes`, redispatch implementers and reviewers for another round. When the harness keeps agents warm and the fix/re-review is small, steer the same implementer or reviewer instead of spawning a fresh agent for token efficiency (in Claude Code, `SendMessage` to the agent's id/name; a new `Agent` call always starts cold).

For a tiny fix you can verify directly, set `status: approved` inline instead.
