# Agent Teams — Technical Mechanics

> **ARCHIVED (2026-04-17).** Agent Teams mode proved unreliable in practice
> and is no longer used by any superRA workflow. This file is retained as
> a historical reference only — **do not load it, do not cite it from any
> active skill**. If you are reading this because an agent pointed you
> here, the pointer is stale; please flag it.

This reference carries the technical how-to for Agent Teams and parallel-dispatch: TeamCreate usage, task-graph construction, the parallel-dispatch pattern, and known limitations. Load it whenever you are about to spawn or clean up a team, or dispatch parallel subagents and want the mechanics right. High-level orchestration guidance (when to dispatch at all, how to adjudicate reviewer feedback, how to relay) lives in `SKILL.md`.

**Pointers — do not duplicate here:**

- **For skill-loads per stage, see `superRA:using-superra` §Skill-Load Manifest.** Every agent (main, subagent, team teammate) reads the manifest; this file does not repeat per-stage skill/reference lists.
- **Team composition: spawn one teammate per stage the workflow runs.** Role is encoded by `subagent_type` — `superRA:implementer` for implementer-role stages, `superRA:reviewer` for reviewer-role stages. The teammate then loads what the manifest lists for its Stage. No per-workflow team recipe is needed.

---

## Availability Check

Agent Teams require the experimental feature flag:

- Environment: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- Or settings.json: `{"env": {"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"}}`

If the session-start context includes "Agent Teams: available", use teams for appropriate workflows. Otherwise, fall back to subagent patterns (orchestrator relay).

## When to Use Teams vs Subagents

| Pattern | Use Teams | Use Subagents |
|---------|-----------|---------------|
| Creator ↔ reviewer iteration | Yes — direct feedback | No — orchestrator relays |
| Implementer ↔ reviewer iteration | Yes — direct feedback | No — orchestrator relays |
| Independent parallel tasks | No — overhead | Yes — Task tool |
| Single focused task | No — overhead | Yes — lighter weight |
| Sequential pipeline (no iteration) | No — no benefit | Yes — simpler |

## Critical Constraint: One Team Per Session

Only one team can exist per session. The lead must clean up the current team before starting a new one.

The full superRA workflow spans three team-worthy phases:

```
implementation-workflow (analysis team)
  → cleanup
    → integration-workflow (integration team, Phases A–D)
      → cleanup
```

Sequential teams with cleanup. The lead cleans up each team before spawning the next.

## Spawning a Team

Team composition is derived from the manifest — the lead spawns one teammate per stage the workflow runs, using `subagent_type: superRA:implementer` for implementer-role stages and `superRA:reviewer` for reviewer-role stages; the teammate loads what `superRA:using-superra` §Skill-Load Manifest lists for its Stage. There is no per-workflow recipe beyond this; the composition is read from the workflow skill (which stages it runs) and the manifest (what each stage loads).

**Generic spawn template:**

```
Create an agent team for <workflow-name>:
- <teammate-name>: subagent_type <superRA:implementer | superRA:reviewer>; Stage: <stage-name from manifest>
- <teammate-name>: ...
```

Each teammate loads what the manifest specifies for its Stage. Do not duplicate skill/reference lists in the spawn prompt — the teammate reads the manifest itself.

## Task-Graph Construction

Construct the full task graph from `PLAN.md` upfront so teammates see the whole scope. Each graph node is one stage of one task, assigned to the teammate whose `subagent_type` matches the stage's role.

**Dependency rules:**

- Review depends on implementation of the same task.
- Implementation of task N+1 depends on review APPROVE of task N. This prevents the implementer from starting the next task before the current one is fully approved.
- For integration / merge workflows: refactor depends on the preceding review; post-refactor drift-test runs depend on the refactor; re-review depends on the post-refactor run.

**Task creation order:** Create the team (`TeamCreate`) before creating tasks (`TaskCreate`). Tasks created before the team exist in a separate namespace and are invisible to teammates.

**Iteration pattern:** When a reviewer returns REVISE, they message the implementer/refactorer directly with specific feedback. The implementer fixes and messages the reviewer to re-review. The orchestrator lead adjudicates REVISE feedback per `SKILL.md` §Handling Reviewer Feedback (Orchestrator Discipline) — read the cited code, classify each issue, override with documented reasoning where the reviewer is wrong.

## Parallel Dispatch (Subagents, Not Teams)

For 2+ independent tasks that can be worked on without shared state or sequential dependencies, use parallel subagent dispatch via the Task tool (not an Agent Team — teams add coordination overhead that independent tasks do not need).

**When to use:**

- 3+ test files failing with different root causes
- Multiple subsystems broken independently
- Each problem can be understood without context from others
- No shared state between investigations

**When NOT to use:**

- Failures are related (fixing one might fix others)
- Need to understand full system state
- Agents would interfere with each other (editing same files)

### Infrastructure for Parallel Work

When dispatching parallel agents that need isolated workspaces, follow `SKILL.md` §Parallelization and Worktree Isolation:

- Provision one worktree per agent per `references/worktree-harness-fallback.md` (harness tools preferred; raw `git worktree` otherwise).
- Seed non-git data via `superRA:worktree-data-sync` §`--mode seed` with `--seed-sync-mode force-symlink`.
- Merge back with plain `git merge` on the `<current-branch>-agent/parallel/<slug>` branches.

Do not hand-roll worktree setup or data-copy scripts.

### The Pattern

1. **Identify independent domains.** Group failures by what's broken. Each domain is independent — fixing one doesn't affect the others.

2. **Create focused agent tasks.** Each agent gets a specific scope (one file or subsystem), a clear goal, constraints (don't change other code), and an explicit expected output.

3. **Dispatch in parallel using the canonical template.** Every dispatch follows the `Stage:` / `Task:` / `Additionally:` shape defined in `SKILL.md` §Dispatch Templates. The agent reads its standard protocol and the manifest; the `Additionally:` tail carries task-specific steering only.

   ```
   Agent(subagent_type: "superRA:implementer"):
     Stage: <stage-name>
     Task: <task pointer>

     Additionally: <focus: one independent domain>

   Agent(subagent_type: "superRA:implementer"):
     Stage: <stage-name>
     Task: <task pointer>

     Additionally: <focus: a different independent domain>
   ```

   All dispatches go out in one message so they run concurrently. No per-dispatch recitation of `PLAN.md` content or manifest loads — the agent reads those itself.

4. **Review and integrate.** When agents return, read each status report, verify fixes don't conflict, run the full test suite (or pipeline), and integrate all changes.

### Common Mistakes

- **Too broad:** "Fix all the tests" — agent gets lost.
- **No context in the `Additionally:` tail:** "Fix the race condition" — agent doesn't know where.
- **No constraints:** Agent might refactor everything.
- **Vague output:** "Fix it" — you don't know what changed; the status return is a navigation aid only if the dispatch steered it.

### Verification

After agents return:

1. Read each `**Doc edits:**` line and summary to understand what changed.
2. Check for conflicts — did agents edit the same code?
3. Run the full pipeline to verify fixes work together.
4. Spot check — agents can make systematic errors.

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
- **Completed work is safe.** All completed tasks are committed to git and recorded in `PLAN.md` / `RESULTS.md`.
- **New session detects in-progress work.** superRA's cross-session detection (in `superRA:using-superra` `references/main-agent.md`) checks for incomplete `PLAN.md`.
- **Resume with new team.** New session reads `PLAN.md` to find last completed task, spawns a fresh team for remaining work.

### Checkpointing for Team Safety

Because teammates can be lost at any time, checkpointing discipline is critical:

- Commit after each completed task (already required by superRA)
- Update `PLAN.md` and mark tasks `- [x]` with result notes (already required)
- Update `RESULTS.md` with findings (already required)
- **Additionally:** lead records active team phase in `PLAN.md` when spawning a team.

Example `PLAN.md` team status note:

```markdown
## Team Status
Analysis team active. Tasks 1-3 of 5 complete. Reviewer reviewing task 4.
```

On session resume, this tells the new lead exactly where to pick up.

## Constraints

- **Task creation order:** Create the team (`TeamCreate`) before creating tasks (`TaskCreate`). Tasks created before the team exist in a separate namespace and are invisible to teammates.
- **File conflicts:** Never assign two teammates to edit the same file simultaneously. Task dependencies prevent this for sequential work. For parallel tasks, ensure each teammate owns different files.
- **Ordering guarantees:** Review of task N must complete before implementation of task N+1 starts. Enforce via task dependencies, never via convention.
- **Escalation to user:** Teammates must message the lead (not the user directly) for escalation decisions. The lead handles all user communication.
- **Team size:** Keep teams small (2–4 teammates). Larger teams increase coordination overhead and token cost without proportional benefit.
- **Cleanup:** Lead must shut down all teammates and clean up team resources when done. Never leave zombie teammates running.

## Known Limitations

- **No session resumption** — `/resume` and `/rewind` do not restore teammates.
- **Task status can lag** — teammates sometimes fail to mark tasks as completed; check if work is actually done.
- **One team per session** — must clean up before starting a new team.
- **No nested teams** — teammates cannot spawn their own teams (they can use subagents via Task tool).
- **Skills / mcpServers frontmatter** — not applied to team teammates; they load from project and user settings like regular sessions. Teammates pick up `superRA:using-superra` the same way as any regular session — via the `Skill` tool — since there is no per-teammate frontmatter preload.
- **Shutdown can be slow** — teammates finish current request / tool call before shutting down.
