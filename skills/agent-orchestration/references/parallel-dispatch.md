# Parallel Dispatch and Worktree Isolation

Load when dispatching agents in parallel or isolating an agent in its own worktree.

Candidates: independent tasks, or reviewers covering disjoint work — every `Depends on:` satisfied, no shared mutable state. **Prefer background dispatch.**

Parallel agents **must** run in separate worktrees, one per agent, created before dispatch, per `references/worktree-harness-fallback.md`. The branch name carries a `/parallel/` infix (`<current-branch>-agent/parallel/<slug>`) so the `merge-guard` hook exempts the source ref on merge-back. In Claude Code, do **not** use the `Agent` tool's `isolation: "worktree"` — it branches off main's HEAD, hiding in-flight state; branch off the current branch.

Pass the absolute worktree path in the dispatch `Worktree:` field, plus this `Additionally:` steering:

> *Work inside the worktree at `<path>`. Enter via `EnterWorktree` if available, otherwise `cd <path>`. Do not edit files outside. Do not merge or push — the orchestrator owns merge-back.*

**Seeding data in:** `worktree-data-sync` in `--mode seed`.

**Harvest-out:** `git merge --no-ff <current-branch>-agent/parallel/<slug>`. Ex-ante task boundaries make parallel branches mechanically disjoint, so they typically merge cleanly. Resolve trivial adjacent conflicts inline; escalate material ones to the researcher.

Transient state — branch names, HEAD SHAs, worktree paths — never enters the task tree; git (`git worktree list`, `git branch`) is the source of truth.
