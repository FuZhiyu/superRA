---
name: agent-orchestration
description: Coordinate superRA agents and handoffs. Requires superRA:using-superra. Use to dispatch roles, run parallel agents, choose reviewers, or preserve workflow state.
---

# Agent Orchestration

## Overview

You delegate tasks to specialized agents with isolated context. Parallel-dispatch independent tasks/reviews; serialize iterative loops.

## Workload Balancing

Every dispatch has spawn cost — skill-load, context hydration, per-turn overhead. Pick the tier that matches the work:

### Tier 1 — Small: main implementer seat

Use the small-task structure in §Seat Assignment.

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

Default to the medium tier (Sonnet in Claude Code, medium thinking in Codex). Step up (Opus / deep thinking) when any of these apply: the spec emerges mid-task rather than from the objective; silent-error risk is high (results-bearing code where a wrong output ships without obvious failure); the dispatch is a thorough-tier first-pass review (lower-tier agents over-comply; a narrow re-review of a cited fix stays medium); or heavy context synthesis reconciles many files/skills in one head. Fable is reserved for the most challenging, expensive tasks. These are defaults, not rules — honor any explicit user preference.

---

## Parallelization and Worktree Isolation

Before dispatching agents in parallel or isolating an agent in its own worktree, load `references/parallel-dispatch.md` — parallel agents require per-agent worktrees, and the seeding and harvest rules live there.

---

## Dispatch Templates

Every workflow skill that dispatches a task-scoped implementer or reviewer uses the shape below; the stage-specific body lives in that workflow skill. The load line is the whole role contract — the role skill pulls the always-loaded pair and the manifest's stage and domain skills. `Stage: sync` is the exception: it names `semantic-merge` mode references instead of a role skill.

**Implementer:**
```
Agent:
  Load `superRA:implement-task` skill.

  Stage: <stage-name>
  Task(s): <task path — e.g., "data-preparation/merge">
  Worktree: <absolute path>   # optional — parallel-dispatch only

  Additionally: <optional steering — focus area, prior-round adjudication notes, warnings>
```

**Reviewer:**
```
Agent:
  Load `superRA:review-task` skill.

  Stage: <stage-name>
  Task: <task path — e.g., "data-preparation/merge">
  Git range: <BASE_SHA>..<HEAD_SHA>
  Tier: quick | thorough      # optional — defaults to quick
  Focus: <dimensions>         # optional — defaults to correctness
  Worktree: <absolute path>   # optional — parallel-reviewer pattern only

  Additionally: <optional steering — focus area, prior-round adjudication notes, warnings>
```

`Additionally:` is steering only. Omit it when there is none, and never use it to restate role protocol, manifest loads, or task content. Never add `Work from:` — cwd is implicit.

Bundle only same-stage, same-domain, same-parent frontier leaves that share context and are simple enough for one agent; keep dependent siblings out unless the upstream task is already `approved` or deferred (§Handling Reviewer Feedback).

Parent objectives are inherited shared context at the dispatch boundary; sibling results are not. When a downstream task consumes an upstream result, the steering or the downstream objective names the approved dependency `## Results` to read.


## Seat Assignment

Each task has an implementer seat and a reviewer seat; each is independently filled by the main agent or a dispatched subagent. These are the seat structures of **subagent** mode (`using-superra/references/main-agent.md §Execution Modes`):

| Implementer | Reviewer | Choose when |
|---|---|---|
| subagent | subagent | Default for large or routine work. |
| subagent | main | Small or high-stakes work where the main context should carry the review. |
| main | subagent | Small or context-heavy implementation that still needs independent review. |

When the main agent fills a seat, load that seat's role skill — `superRA:implement-task` or `superRA:review-task` — plus its stage and domain loads, and execute it directly. A main reviewer receives the same `Git range:` a dispatched reviewer would; a main implementer hands its commits to the dispatched reviewer.

## Orchestrator Duties

Done by the orchestrator alone, at every workflow stage:

- **Task sequencing and dispatch inside the selected frontier.** The main agent selects which frontier to work; this skill sizes, bundles, and dispatches the work inside it.
- **Adjudicate reviewer feedback in place.** See §Handling Reviewer Feedback below for the full protocol.
- **Handle implementer status returns.** Re-dispatch when context is missing; escalate researcher-owned blockers through the active workflow's pause rules.
- **Escalate to the researcher via `AskUserQuestion`** (plain text if unavailable) when stuck — hard blocker, research-related decision, override of a blocking finding. Fold the decision into the task objective (rewrite it fully); add a `## Revision Notes` entry if the change is non-obvious.

## Handling Reviewer Feedback

Adjudicate REVISE findings before forwarding them. Read cited code or task context only when needed to decide whether to accept, reject, escalate, or inline-verify a minor fix.

For each finding:

- **Accept** real issues.
- **Reject** false positives, removing them from `## Review Notes`.
- **Escalate** findings that would materially change the direction of the task.

**Schedule accepted fixes against the whole workflow.** The reviewer graded severity by effect on the task's result; you hold the workflow context, so you decide when each fix lands:

- **Fix now** when the issue significantly affects downstream tasks. Redispatch implementer and reviewer for another round and iterate to APPROVE before advancing the frontier. For a tiny fix you can verify directly, apply or verify it and set `status: approved` inline. When the harness keeps agents warm and the fix/re-review is small, steer the same implementer or reviewer instead of spawning a fresh agent (in Claude Code, `SendMessage` to the agent's id/name; a new `Agent` call always starts cold).
- **Defer** when the main result stands and the open items do not affect downstream work: leave the findings in `## Review Notes`, leave `status: revise`, and proceed to the dependent tasks — a task may stay in revision while downstream work advances. `superra task frontier` lists only dependents of `approved` tasks, so dispatch the dependents of a deferred task yourself. Track deferred items as you go; when the active frontier's implementations are done, clear them all in one bundled fix pass (§Workload Balancing Tier 2) and re-review to `approved`.
