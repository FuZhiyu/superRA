---
name: agent-orchestration
description: Use when orchestrating multi-agent work — provides decision framework for parallel dispatch (independent tasks) vs Agent Teams (iterative workflows), team recipes, and session handoff protocol
---

# Agent Orchestration

## Overview

You delegate tasks to specialized agents with isolated context. This skill covers two orchestration patterns and helps you choose between them.

**Core principle:** Use teams when agents need to iterate with each other. Use parallel subagents when you just need results back.

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

**Rule of thumb:** If two agents will exchange feedback more than once, use a team (or orchestrator relay). If each agent does its work and returns a result, use parallel dispatch.

---

## Parallel Dispatch

For 2+ independent tasks that can be worked on without shared state or sequential dependencies.

### When to Use

- 3+ test files failing with different root causes
- Multiple subsystems broken independently
- Each problem can be understood without context from others
- No shared state between investigations

### When NOT to Use

- Failures are related (fixing one might fix others)
- Need to understand full system state
- Agents would interfere with each other (editing same files)

### The Pattern

#### 1. Identify Independent Domains

Group failures by what's broken:
- File A tests: Tool approval flow
- File B tests: Batch completion behavior
- File C tests: Abort functionality

Each domain is independent — fixing tool approval doesn't affect abort tests.

#### 2. Create Focused Agent Tasks

Each agent gets:
- **Specific scope:** One test file or subsystem
- **Clear goal:** Make these tests pass
- **Constraints:** Don't change other code
- **Expected output:** Summary of what you found and fixed

#### 3. Dispatch in Parallel

```typescript
// All three run concurrently
Task("Fix agent-tool-abort.test.ts failures")
Task("Fix batch-completion-behavior.test.ts failures")
Task("Fix tool-approval-race-conditions.test.ts failures")
```

#### 4. Review and Integrate

When agents return:
- Read each summary
- Verify fixes don't conflict
- Run full test suite
- Integrate all changes

### Agent Prompt Structure

Good agent prompts are:
1. **Focused** — One clear problem domain
2. **Self-contained** — All context needed to understand the problem
3. **Specific about output** — What should the agent return?

```markdown
Fix the 3 failing tests in src/agents/agent-tool-abort.test.ts:

1. "should abort tool with partial output capture" - expects 'interrupted at' in message
2. "should handle mixed completed and aborted tools" - fast tool aborted instead of completed
3. "should properly track pendingToolCount" - expects 3 results but gets 0

These are timing/race condition issues. Your task:

1. Read the test file and understand what each test verifies
2. Identify root cause - timing issues or actual bugs?
3. Fix by:
   - Replacing arbitrary timeouts with event-based waiting
   - Fixing bugs in abort implementation if found
   - Adjusting test expectations if testing changed behavior

Do NOT just increase timeouts - find the real issue.

Return: Summary of what you found and what you fixed.
```

### Common Mistakes

**Too broad:** "Fix all the tests" — agent gets lost
**No context:** "Fix the race condition" — agent doesn't know where
**No constraints:** Agent might refactor everything
**Vague output:** "Fix it" — you don't know what changed

### Verification

After agents return:
1. **Review each summary** — Understand what changed
2. **Check for conflicts** — Did agents edit same code?
3. **Run full suite** — Verify all fixes work together
4. **Spot check** — Agents can make systematic errors

---

## Agent Teams

Agent Teams let multiple Claude Code sessions work together with direct peer-to-peer communication and a shared task list. When available, prefer teams over orchestrator relay for workflows with iteration loops.

### Availability Check

Agent Teams require the experimental feature flag:
- Environment: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- Or settings.json: `{"env": {"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"}}`

If the session-start context includes "Agent Teams: available", use teams for appropriate workflows. Otherwise, fall back to subagent patterns (orchestrator relay).

### When to Use Teams vs Subagents

| Pattern | Use Teams | Use Subagents |
|---------|-----------|---------------|
| Creator ↔ reviewer iteration | Yes — direct feedback | No — orchestrator relays |
| Implementer ↔ reviewer iteration | Yes — direct feedback | No — orchestrator relays |
| Independent parallel tasks | No — overhead | Yes — Task tool |
| Single focused task | No — overhead | Yes — lighter weight |
| Sequential pipeline (no iteration) | No — no benefit | Yes — simpler |

### Critical Constraint: One Team Per Session

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

### Team Recipes

#### Analysis Task Team

**When:** `superRA:executing-analysis` in subagent mode with multiple tasks

**Teammates (3):**
- `implementer` — Executes analysis tasks (data-first discipline)
- `data-reviewer` — Reviews data integrity (must complete before implementation review)
- `implementation-reviewer` — Reviews implementation correctness

**Spawn:**
```
Create an agent team for analysis execution:
- implementer: [use `implementer` agent type; load superRA:econ-data-analysis; provide project context]
- data-reviewer: [use `reviewer` agent type; load superRA:econ-data-analysis; handoff: PLAN.md data integrity status]
- implementation-reviewer: [use `reviewer` agent type; load superRA:econ-data-analysis; handoff: PLAN.md APPROVED status]
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
- Provide each teammate with their agent type, skill to load, and project context
- Verify that teammates commit their own PLAN.md and RESULTS_UPDATE.md updates atomically with their work (per executing-analysis responsibility matrix)
- Monitor for BLOCKED or data quality escalations (teammates message lead)
- Handle sensitivity analysis assessment
- Note team phase in PLAN.md (e.g., "Analysis Team active, tasks 1-3 of 5 complete")
- Clean up team before proceeding to finishing-analysis

#### Pre-Merge Gate Team

**When:** `superRA:pre-merge-gate` is invoked (from finishing-analysis, Options 1 or 2)

**Teammates (4):**
- `test-creator` — Creates drift tests for key results
- `test-reviewer` — Reviews tests for coverage, tolerances, independence
- `refactorer` — Refactors code for codebase integration
- `integration-reviewer` — Reviews integration quality

**Spawn:**
```
Create an agent team for pre-merge quality gate:
- test-creator: [use `implementer` agent type; load superRA:econ-data-analysis; domain ref: pre-merge-gate/references/drift-test-quality.md]
- test-reviewer: [use `reviewer` agent type; load superRA:econ-data-analysis; domain ref: pre-merge-gate/references/drift-test-quality.md]
- refactorer: [use `implementer` agent type; load superRA:econ-data-analysis; domain ref: pre-merge-gate/references/codebase-integration.md]
- integration-reviewer: [use `reviewer` agent type; load superRA:econ-data-analysis; domain ref: pre-merge-gate/references/codebase-integration.md]

Require plan approval before they make changes.
```

**Task graph:**
1. `create-drift-tests` → assigned: test-creator
2. `review-drift-tests` → depends: 1, assigned: test-reviewer
3. `establish-green-baseline` → depends: 2, assigned: test-creator (run tests)
4. `review-integration` → depends: 3, assigned: integration-reviewer
5. `refactor-code` → depends: 4 (only if REVISE), assigned: refactorer
6. `run-drift-tests-post-refactor` → depends: 5, assigned: refactorer
7. `re-review-integration` → depends: 6, assigned: integration-reviewer

**Flow:** Integration reviewer runs first (task 4). If APPROVE, no refactoring needed — skip tasks 5-7. If REVISE, refactorer addresses specific feedback (task 5), drift tests verify (task 6), integration reviewer re-reviews (task 7). Loop until APPROVE.

**Iteration:** When test-reviewer sends REVISE, they message test-creator directly with specific feedback. Test-creator fixes and marks task updated. Test-reviewer re-reviews. For the integration loop: integration-reviewer messages refactorer with specific issues, refactorer fixes and runs drift tests, then messages integration-reviewer to re-review.

**Lead responsibilities:**
- Present drift test candidates to user BEFORE creating team (Stage 1 user confirmation)
- Create team and task graph with dependencies
- Monitor for meaningful drift escalations from refactorer
- Handle user communication for all escalation decisions
- Commit at stage boundaries
- Clean up team after final integration reviewer APPROVE

#### Semantic Merge Team

**When:** `superRA:semantic-merge` at Tier 2 or Tier 3

**Teammates (2):**
- `merge-proposer` — Analyzes incoming intent, proposes integration, executes two-commit merge
- `merge-reviewer` — Reviews integration for intent preservation, research integrity, data discipline

**Spawn:**
```
Create an agent team for semantic merge integration:
- merge-proposer: [use `implementer` agent type; load superRA:econ-data-analysis; domain ref: semantic-merge/references/merge-quality.md]
- merge-reviewer: [use `reviewer` agent type; load superRA:econ-data-analysis; domain ref: semantic-merge/references/merge-quality.md]
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

### Team Lifecycle & Session Handoff

#### Cleanup Protocol

When a team's work is complete:

1. Shut down each teammate: "Ask [teammate-name] to shut down"
2. Wait for all teammates to confirm shutdown
3. Clean up team resources: "Clean up the team"
4. Verify cleanup: team config and task list removed

**Always use the lead to clean up.** Teammates should not run cleanup.

#### Session Interruption

If context runs out or the session ends mid-team:
- **Teammates are lost.** `/resume` and `/rewind` do not restore teammates.
- **Completed work is safe.** All completed tasks are committed to git and recorded in PLAN.md/RESULTS_UPDATE.md.
- **New session detects in-progress work.** SuperRA's cross-session detection (in `using-superRA`) checks for incomplete PLAN.md.
- **Resume with new team.** New session reads PLAN.md to find last completed task, spawns a fresh team for remaining work.

#### Checkpointing for Team Safety

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

### Constraints

**File conflicts:** Never assign two teammates to edit the same file simultaneously. Task dependencies prevent this for sequential work. For parallel tasks, ensure each teammate owns different files.

**Ordering guarantees:** Data integrity review MUST complete before implementation review. Enforce via task dependencies, never via convention.

**Escalation to user:** Teammates must message the lead (not the user directly) for escalation decisions. The lead handles all user communication.

**Team size:** Keep teams small (3-5 teammates). Larger teams increase coordination overhead and token cost without proportional benefit.

**Cleanup:** Lead must shut down all teammates and clean up team resources when done. Never leave zombie teammates running.

### Known Limitations

- **No session resumption** — `/resume` and `/rewind` do not restore teammates
- **Task status can lag** — teammates sometimes fail to mark tasks as completed; check if work is actually done
- **One team per session** — must clean up before starting a new team
- **No nested teams** — teammates cannot spawn their own teams (they can use subagents via Task tool)
- **Skills/mcpServers frontmatter** — not applied to team teammates; they load from project and user settings like regular sessions
- **Shutdown can be slow** — teammates finish current request/tool call before shutting down

---

## Integration

**Skills that use Agent Teams mode:**
- **superRA:pre-merge-gate** — 4-teammate pre-merge team
- **superRA:executing-analysis** — 3-teammate analysis team
- **superRA:semantic-merge** — 2-teammate merge team

**Skills that always use parallel dispatch:**
- **superRA:requesting-analysis-review** — one-shot review, no iteration

**When Agent Teams are unavailable:** All skills fall back to standard subagent patterns (Task tool dispatch with orchestrator-as-hub). No functionality is lost — teams are an enhancement, not a requirement.
