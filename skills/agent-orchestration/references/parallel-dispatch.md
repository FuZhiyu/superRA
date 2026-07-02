# Parallel Dispatch and Worktree Isolation

Load when dispatching agents in parallel or isolating an agent in its own worktree.

Parallel dispatch is worthwhile for independent tasks or reviewers covering disjoint work. Tasks with all `Depends on:` lines satisfied and no shared mutable state are natural candidates. **Prefer background dispatch.**

Parallel agents **must** run in separate worktrees, one per agent, created before dispatch. The branch name carries a `/parallel/` infix (`<current-branch>-agent/parallel/<slug>`) so the `merge-guard` hook exempts the source ref on merge-back. Create, place, and remove worktrees per `references/worktree-harness-fallback.md`. In Claude Code, do **not** use the `Agent` tool's `isolation: "worktree"` parameter — it branches off main's HEAD, so the subagent cannot see in-flight state; branch off the current branch instead.

Pass the absolute worktree path via the dispatch `Worktree:` field, plus this `Additionally:` steering:

> *Work inside the worktree at `<path>`. Enter via `EnterWorktree` if available, otherwise `cd <path>`. Do not edit files outside. Do not merge or push — the orchestrator owns merge-back.*

**Seeding data in.** Use `worktree-data-sync` in `--mode seed`. **Always pass `--from "$(pwd)"` (or an explicit path)** — `sync_worktree_data.py`'s `--from` default points at the main worktree, not the orchestrator's analysis worktree.

**Harvest-out and conflicts.** `git merge --no-ff <current-branch>-agent/parallel/<slug>`. Task boundaries are set ex-ante, so parallel branches are mechanically disjoint and typically merge cleanly. Resolve trivial adjacent conflicts inline; escalate material ones to the researcher.

Transient state (branch names, HEAD SHAs, worktree paths) is not persisted in the task tree — git (`git worktree list`, `git branch`) is the source of truth.
