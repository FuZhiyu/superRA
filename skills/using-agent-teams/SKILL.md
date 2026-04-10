---
name: using-agent-teams
description: Use when orchestrating multi-agent workflows — provides Agent Teams decision framework, team recipes, and session handoff protocol
---

# Using Agent Teams

## Overview

Agent Teams let multiple Claude Code sessions work together with direct peer-to-peer communication and a shared task list. When available, prefer teams over regular subagents for workflows with iteration loops between agents.

**Core principle:** Use teams when agents need to iterate with each other. Use subagents when you just need a result back.

**Announce at start:** "I'm using the using-agent-teams skill to set up team orchestration."

## Availability Check

Agent Teams require the experimental feature flag:
- Environment: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- Or settings.json: `{"env": {"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"}}`

If the session-start context includes "Agent Teams: available", use teams for appropriate workflows. Otherwise, fall back to subagent patterns described in each skill's standard process.

## When to Use Teams vs Subagents

| Pattern | Use Teams | Use Subagents |
|---------|-----------|---------------|
| Creator ↔ reviewer iteration | Yes — direct feedback | No — orchestrator relays |
| Implementer ↔ reviewer iteration | Yes — direct feedback | No — orchestrator relays |
| Independent parallel tasks | No — overhead | Yes — Task tool |
| Single focused task | No — overhead | Yes — lighter weight |
| Sequential pipeline (no iteration) | No — no benefit | Yes — simpler |

**Rule of thumb:** If two agents will exchange feedback more than once, use a team. If an agent does its work and returns a result, use a subagent.

## Critical Constraint: One Team Per Session

Only one team can exist per session. You must clean up the current team before starting a new one.

The full superRA workflow spans two team-worthy phases:

```
executing-analysis (Analysis Team)
  → cleanup
    → finishing-analysis
      → pre-merge-gate (Pre-Merge Team)
        → cleanup
```

**Sequential teams with cleanup.** The lead cleans up the Analysis Team before spawning the Pre-Merge Team:

1. All analysis tasks complete → shut down all teammates → clean up team
2. Lead proceeds to finishing-analysis (no team needed)
3. If user chooses merge/PR → spawn Pre-Merge Team → run 3 stages → clean up team

## Team Recipes

### Analysis Task Team

**When:** `superRA:executing-analysis` in subagent mode with multiple tasks

**Teammates (3):**
- `implementer` — Executes analysis tasks (data-first discipline)
- `data-reviewer` — Reviews data integrity (must complete before implementation review)
- `implementation-reviewer` — Reviews implementation correctness

**Spawn:**
```
Create an agent team for analysis execution:
- implementer: [paste implementer-prompt.md with project context filled in]
- data-reviewer: [paste data-reviewer-prompt.md with project context filled in]
- implementation-reviewer: [paste implementation-reviewer-prompt.md filled in]
```

**Task graph (per analysis task N):**
1. `implement-task-N` → assigned: implementer
2. `data-review-task-N` → depends: implement-task-N, assigned: data-reviewer
3. `impl-review-task-N` → depends: data-review-task-N, assigned: implementation-reviewer

**Cross-task dependency:** `implement-task-N+1` depends on `impl-review-task-N`. This prevents the implementer from starting the next task before the current one is fully approved.

Create all tasks upfront from PLAN.md so teammates can see the full scope.

**Iteration:** When data-reviewer finds issues, they message implementer directly with specific feedback. Implementer fixes the code, then messages data-reviewer to re-review. Same pattern for implementation-reviewer ↔ implementer.

**Lead responsibilities:**
- Read PLAN.md, create full task graph with all dependencies
- Provide each teammate with their prompt template and project context
- Update PLAN.md and RESULTS_UPDATE.md after each task completes (teammates commit code; lead updates plan documents)
- Monitor for BLOCKED or data quality escalations (teammates message lead)
- Handle sensitivity analysis assessment
- Note team phase in PLAN.md (e.g., "Analysis Team active, tasks 1-3 of 5 complete")
- Clean up team before proceeding to finishing-analysis

### Pre-Merge Gate Team

**When:** `superRA:pre-merge-gate` is invoked (from finishing-analysis, Options 1 or 2)

**Teammates (4):**
- `test-creator` — Creates drift tests for key results
- `test-reviewer` — Reviews tests for coverage, tolerances, independence
- `refactorer` — Refactors code for codebase integration
- `integration-reviewer` — Reviews integration quality

**Spawn:**
```
Create an agent team for pre-merge quality gate:
- test-creator: [paste test-creator-prompt.md with filled placeholders]
- test-reviewer: [paste test-reviewer-prompt.md with filled placeholders]
- refactorer: [paste refactor-prompt.md with filled placeholders]
- integration-reviewer: [paste integration-reviewer-prompt.md with filled placeholders]

Require plan approval before they make changes.
```

**Task graph:**
1. `create-drift-tests` → assigned: test-creator
2. `review-drift-tests` → depends: 1, assigned: test-reviewer
3. `establish-green-baseline` → depends: 2, assigned: test-creator (run tests)
4. `refactor-code` → depends: 3, assigned: refactorer
5. `run-drift-tests-post-refactor` → depends: 4, assigned: refactorer
6. `review-integration` → depends: 5, assigned: integration-reviewer

**Iteration:** When test-reviewer sends REVISE, they message test-creator directly with specific feedback. Test-creator fixes and marks task updated. Test-reviewer re-reviews. Same pattern for integration-reviewer ↔ refactorer.

**Lead responsibilities:**
- Present drift test candidates to user BEFORE creating team (Stage 1 user confirmation)
- Create team and task graph with dependencies
- Monitor for meaningful drift escalations from refactorer (Stage 2)
- Handle user communication for all escalation decisions
- Commit at stage boundaries
- Clean up team after final APPROVE

### Semantic Merge Team

**When:** `superRA:semantic-merge` at Tier 2 or Tier 3

**Teammates (2):**
- `merge-proposer` — Analyzes incoming intent, proposes integration, executes two-commit merge
- `merge-reviewer` — Reviews integration for intent preservation, research integrity, data discipline

**Spawn:**
```
Create an agent team for semantic merge integration:
- merge-proposer: [paste merge-proposer-prompt.md with merge context filled in]
- merge-reviewer: [paste merge-reviewer-prompt.md with merge context filled in]
```

**Task graph:**
1. `propose-integration` → assigned: merge-proposer
2. `review-integration` → depends: 1, assigned: merge-reviewer

**Iteration:** When merge-reviewer sends REVISE, they message merge-proposer directly with specific feedback (what conflict resolution is wrong, what reference is stale). Merge-proposer fixes and messages back. Merge-reviewer re-reviews.

**Lead responsibilities:**
- Perform tier classification before deciding whether to spawn team (Tier 1 = no team)
- For Tier 3: present integration map to user, relay user decisions to proposer
- Commit at each stage (mechanical commit, integration commit)
- Run drift tests and pipeline verification after integration
- Handle drift test failure escalation to user
- Clean up team after final APPROVE

**Team slot:** This team runs during finishing-analysis Step 4d. The pre-merge-gate team (if used) must be cleaned up before this point. The current workflow guarantees this: pre-merge gate runs in Step 4a, team cleaned up before Step 4d.

## Team Lifecycle & Session Handoff

### Cleanup Protocol

When a team's work is complete:

1. Shut down each teammate: "Ask [teammate-name] to shut down"
2. Wait for all teammates to confirm shutdown
3. Clean up team resources: "Clean up the team"
4. Verify cleanup: team config and task list removed

**Always use the lead to clean up.** Teammates should not run cleanup.

### Session Interruption

If context runs out or the session ends mid-team:
- **Teammates are lost.** `/resume` and `/rewind` do not restore teammates.
- **Completed work is safe.** All completed tasks are committed to git and recorded in PLAN.md/RESULTS_UPDATE.md.
- **New session detects in-progress work.** SuperRA's cross-session detection (in `using-superRA`) checks for incomplete PLAN.md.
- **Resume with new team.** New session reads PLAN.md to find last completed task, spawns a fresh team for remaining work.

### Checkpointing for Team Safety

Because teammates can be lost at any time, checkpointing discipline is critical:
- Commit after each completed task (already required by superRA)
- Update PLAN.md and mark tasks `- [x]` with result notes (already required)
- Update RESULTS_UPDATE.md with findings (already required)
- **Additionally:** Lead records active team phase in PLAN.md when spawning a team

Example PLAN.md team status note:
```markdown
## Team Status
Analysis Team active. Tasks 1-3 of 5 complete. Data-reviewer reviewing task 4.
```

On session resume, this tells the new lead exactly where to pick up.

## Constraints

**File conflicts:** Never assign two teammates to edit the same file simultaneously. Task dependencies prevent this for sequential work. For parallel tasks, ensure each teammate owns different files.

**Ordering guarantees:** Data integrity review MUST complete before implementation review. Enforce via task dependencies, never via convention.

**Escalation to user:** Teammates must message the lead (not the user directly) for escalation decisions. The lead handles all user communication.

**Team size:** Keep teams small (3-5 teammates). Larger teams increase coordination overhead and token cost without proportional benefit.

**Cleanup:** Lead must shut down all teammates and clean up team resources when done. Never leave zombie teammates running.

## Known Limitations

- **No session resumption** — `/resume` and `/rewind` do not restore teammates
- **Task status can lag** — teammates sometimes fail to mark tasks as completed; check if work is actually done
- **One team per session** — must clean up before starting a new team
- **No nested teams** — teammates cannot spawn their own teams (they can use subagents via Task tool)
- **Skills/mcpServers frontmatter** — not applied to team teammates; they load from project and user settings like regular sessions
- **Shutdown can be slow** — teammates finish current request/tool call before shutting down

## Integration

**Skills that support Agent Teams mode:**
- **superRA:pre-merge-gate** — 4-teammate pre-merge team
- **superRA:executing-analysis** — 3-teammate analysis team
- **superRA:semantic-merge** — 2-teammate merge team

**Skills that always use subagents:**
- **superRA:dispatching-parallel-agents** — independent tasks, no iteration needed
- **superRA:requesting-analysis-review** — one-shot review, no iteration

**When Agent Teams are unavailable:** All skills fall back to standard subagent patterns (Task tool dispatch with orchestrator-as-hub). No functionality is lost — teams are an enhancement, not a requirement.
