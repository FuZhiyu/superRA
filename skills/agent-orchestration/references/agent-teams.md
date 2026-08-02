# Agent Teams — Technical Mechanics

> **ARCHIVED (2026-04-17).** Agent Teams mode proved unreliable in practice and is no longer used by any superRA workflow. Retained as historical reference only — **do not load it, do not cite it from any active skill**. A pointer that sent you here is stale; flag it.

Technical how-to for Agent Teams and parallel-dispatch: TeamCreate usage, task-graph construction, the parallel-dispatch pattern, known limitations. High-level orchestration guidance lives in `SKILL.md`.

**Pointers — do not duplicate here:**

- **Skill-loads per stage: `superRA:using-superra` §Skill-Load Manifest.** Every agent reads the manifest; this file does not repeat per-stage lists.
- **Team composition: one teammate per stage the workflow runs.** Role comes from the skill the teammate's prompt names — `superRA:implement-task` for implementer-role stages, `superRA:review-task` for reviewer-role stages. The teammate then loads what the manifest lists for its Stage.

## Availability Check

Agent Teams require the experimental feature flag:

- Environment: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- Or settings.json: `{"env": {"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"}}`

Session-start context includes "Agent Teams: available": use teams for appropriate workflows. Otherwise fall back to subagent patterns (orchestrator relay).

## When to Use Teams vs Subagents

| Pattern | Use Teams | Use Subagents |
|---------|-----------|---------------|
| Creator ↔ reviewer iteration | Yes — direct feedback | No — orchestrator relays |
| Implementer ↔ reviewer iteration | Yes — direct feedback | No — orchestrator relays |
| Independent parallel tasks | No — overhead | Yes — Task tool |
| Single focused task | No — overhead | Yes — lighter weight |
| Sequential pipeline (no iteration) | No — no benefit | Yes — simpler |

## Critical Constraint: One Team Per Session

Only one team exists per session; the lead cleans up the current team before starting the next.

```
superimplement (analysis team)
  → cleanup
    → superintegrate (integration team, Phases A–D)
      → cleanup
```

## Spawning a Team

Composition is derived, not recipe-driven: one teammate per stage the workflow runs, naming `superRA:implement-task` or `superRA:review-task`; the teammate loads what the manifest lists for its Stage.

**Generic spawn template:**

```
Create an agent team for <workflow-name>:
- <teammate-name>: role skill <superRA:implement-task | superRA:review-task>; Stage: <stage-name from manifest>
- <teammate-name>: ...
```

No skill/reference lists in the spawn prompt — the teammate reads the manifest itself.

## Task-Graph Construction

Construct the full task graph from the `superRA/` tree upfront so teammates see the whole scope. Each node is one stage of one task, assigned to the teammate whose `subagent_type` matches the stage's role.

**Dependency rules:**

- Review depends on implementation of the same task.
- Implementation of task N+1 depends on review APPROVE of task N — the implementer must not start the next task before the current one is approved.
- Integration / merge workflows: refactor depends on the preceding review; post-refactor drift-test runs depend on the refactor; re-review depends on the post-refactor run.

**Task creation order:** `TeamCreate` before `TaskCreate`. Tasks created before the team live in a separate namespace, invisible to teammates.

**Iteration pattern:** a reviewer returning REVISE messages the implementer/refactorer directly; the implementer fixes and messages the reviewer to re-review. The lead adjudicates per `SKILL.md` §Handling Reviewer Feedback.

## Parallel Dispatch (Subagents, Not Teams)

For 2+ independent tasks with no shared state or sequential dependencies, use parallel subagent dispatch via the Task tool — teams add coordination overhead independent tasks do not need.

**Use when:**

- 3+ test files failing with different root causes
- Multiple subsystems broken independently
- Each problem is understandable without context from the others
- No shared state between investigations

**Do not use when:**

- Failures are related (fixing one might fix others)
- Full system state must be understood
- Agents would interfere — editing the same files

### Infrastructure for Parallel Work

Parallel agents needing isolated workspaces follow `references/parallel-dispatch.md`:

- One worktree per agent per `references/worktree-harness-fallback.md` (harness tools preferred; raw `git worktree` otherwise).
- Seed non-git data via `superRA:worktree-data-sync` §`--mode seed` with `--seed-sync-mode force-symlink`.
- Merge back with plain `git merge` on the `<current-branch>-agent/parallel/<slug>` branches.

Never hand-roll worktree setup or data-copy scripts.

### The Pattern

1. **Identify independent domains.** Group failures by what is broken; fixing one must not affect the others.
2. **Create focused agent tasks.** Each agent gets a specific scope (one file or subsystem), a clear goal, constraints, and an explicit expected output.
3. **Dispatch in parallel using the canonical template** from `SKILL.md` §Dispatch Templates. The `Additionally:` tail carries task-specific steering only.

   ```
   Agent:
     Load `superRA:implement-task` skill.

     Stage: <stage-name>
     Task: <task pointer>

     Additionally: <focus: one independent domain>

   Agent:
     Load `superRA:implement-task` skill.

     Stage: <stage-name>
     Task: <task pointer>

     Additionally: <focus: a different independent domain>
   ```

   All dispatches go out in one message so they run concurrently.

4. **Review and integrate.** Read each status report, verify fixes do not conflict, run the full test suite or pipeline, integrate.

### Common Mistakes

- **Too broad:** "Fix all the tests" — the agent gets lost.
- **No context in the `Additionally:` tail:** "Fix the race condition" — the agent does not know where.
- **No constraints:** the agent refactors everything.
- **Vague output:** "Fix it" — the status return navigates only if the dispatch steered it.

### Verification

1. Read each agent's commit body.
2. Check for conflicts — did agents edit the same code?
3. Run the full pipeline to verify the fixes work together.
4. Spot check — agents make systematic errors.

## Team Lifecycle & Session Handoff

### Cleanup Protocol

1. Shut down each teammate: "Ask [teammate-name] to shut down"
2. Wait for all teammates to confirm shutdown
3. "Clean up the team"
4. Verify team config and task list are removed

**The lead cleans up.** Teammates do not.

### Session Interruption

- **Teammates are lost.** `/resume` and `/rewind` do not restore them.
- **Completed work is safe** — committed to git and recorded in `superRA/` task files.
- **A new session detects in-progress work** via the cross-session detection in `superRA:using-superra` `references/main-agent.md`.
- **Resume with a new team** from the last completed task in the tree.

### Checkpointing for Team Safety

- Commit after each completed task (already required).
- Update task files with status and result notes (already required).
- **Additionally:** the lead records the active team phase in the governing ancestor task when spawning a team.

```markdown
## Team Status
Analysis team active. 3 of 5 tasks approved. Reviewer reviewing data-prep/merge.
```

## Constraints

- **Task creation order:** `TeamCreate` before `TaskCreate`.
- **File conflicts:** never assign two teammates the same file simultaneously. Task dependencies cover sequential work; for parallel tasks, give each teammate different files.
- **Ordering guarantees:** review of task N completes before implementation of task N+1 starts. Enforce via task dependencies, never convention.
- **Escalation to user:** teammates message the lead, never the user. The lead handles all user communication.
- **Team size:** 2–4 teammates. Larger teams add coordination overhead and token cost without proportional benefit.
- **Cleanup:** the lead shuts down all teammates and cleans up team resources. No zombie teammates.

## Known Limitations

- **No session resumption** — `/resume` and `/rewind` do not restore teammates.
- **Task status can lag** — teammates sometimes fail to mark tasks completed; check whether the work is actually done.
- **One team per session** — clean up before starting a new team.
- **No nested teams** — teammates cannot spawn teams (they can use subagents via the Task tool).
- **Skills / mcpServers frontmatter** — not applied to teammates; they load from project and user settings like regular sessions, picking up `superRA:using-superra` via the `Skill` tool.
- **Shutdown can be slow** — teammates finish the current request / tool call first.
