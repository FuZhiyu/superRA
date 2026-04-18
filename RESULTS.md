---
author: "Zhiyu Fu"
date: 2026-04-17
git_commit: "9a1b097d15eea25208c973dd44a0d9d786fae93e"
git_message: "plan: flip Integration status + Drift tests / Refactored boxes"
git_dirty: false
tags: ["results", "integration", "agent-orchestration", "worktree"]
project: "superRA"
permalink: "docs/plans/2026-04-17-parallel-implementer-worktree-isolation-results"
---

# Parallel-Implementer Worktree Isolation

## Problem

Parallel implementer dispatches in superRA previously had no isolation contract. Two implementers could share a worktree, race on `PLAN.md` / `RESULTS.md`, and collide on output paths. Separately, `worktree-data-sync` had grown two overlapping concerns — worktree lifecycle (create, enter, remove) and non-git data sync (seed, diff, apply) — with lifecycle prescriptions that presumed raw `git worktree` commands even when a harness exposed native worktree tools.

This branch adds an isolation contract for concurrent writers, carves worktree lifecycle out of `worktree-data-sync` into a harness-aware fallback reference, wires the new contract into the consumer workflows, and exempts parallel-branch merges from the `merge-guard` semantic-merge reminder.

## Resolution

### §Concurrent Writers Require Worktree Isolation + `Worktree:` dispatch field

[`skills/agent-orchestration/SKILL.md`](../../skills/agent-orchestration/SKILL.md#concurrent-writers-require-worktree-isolation) gains a new section between §Workload Balancing and §Dispatch Templates. Two subsections after the `78183d6` simplify pass: §Ownership split (orchestrator seeds in, subagent executes, orchestrator harvests with plain `git merge --no-ff`, orchestrator cleans up) and §Worktree lifecycle (prefer harness tools, fall back to raw git via the new reference, do not persist transient state in `PLAN.md`).

§Dispatch Templates gains an optional `Worktree:` field on the implementer template. When the field is present, the dispatch **must** carry a canned steering sentence in the `Additionally:` tail — the single documented exception to the "additive-only" `Additionally:` rule. Justification is in place: the agent's spawn cwd defaults would otherwise cause silent wrong-copy edits.

### `worktree-harness-fallback.md`

[`skills/agent-orchestration/references/worktree-harness-fallback.md`](../../skills/agent-orchestration/references/worktree-harness-fallback.md) (79 lines) covers harness-tool preference, raw-git create / enter / remove, placement priority, gotchas, and an example orchestrator invocation (`## Example Orchestrator Invocation` appended during dogfood). The reference lives under `agent-orchestration/` because worktree lifecycle is an orchestration concern, not a data-sync concern.

### Narrowed `worktree-data-sync`

[`skills/worktree-data-sync/SKILL.md`](../../skills/worktree-data-sync/SKILL.md) drops §When to Use a Worktree (~13 lines) and §Creating a Worktree (~80 lines across six subsections). The former §Cleanup is renamed §Data Teardown and restricted to the "seeded data disappears with the worktree" fact; `git worktree remove` and branch-deletion prescriptions are repointed at `agent-orchestration/references/worktree-harness-fallback.md`. A §See Also section points at the lifecycle reference and at §Concurrent Writers. Description frontmatter is narrowed to "syncing non-git-controlled data files between existing worktrees".

Post-refactor outline: frontmatter → `# Worktree Data Sync Skill` → §When to Use → §Command Surface (§Endpoints) → §Modes (§`--mode seed` / §`--mode diff` / §`--mode apply`) → §Managed Path Discovery → §Examples → §Data Teardown → §See Also.

### `hooks/merge-guard` exemption for `parallel/*`

[`hooks/merge-guard`](../../hooks/merge-guard) gains a third early-exit branch between the abort/continue/skip/quit skip and the reminder-emitting regex. The pattern `git (merge|rebase|cherry-pick)(\s+--?\S+)*\s+parallel/` matches a parallel/-prefixed positional argument while allowing intermediate flags like `--no-ff`. A header comment block documents the four synthetic regression inputs and their expected outputs.

### Implementer dedicated-worktree commit path

[`agents/implementer.md`](../../agents/implementer.md) gains:

- §Before You Start step 6 — when `Worktree:` is present, enter it (harness tool or `cd` + verify `git rev-parse --show-toplevel`), do all I/O inside, do not merge / rebase / push / clean up, report branch + HEAD SHA.
- §Handoff → Update the Docs and Commit — split into (A) shared-worktree path with the existing discipline and (B) dedicated-worktree path on `parallel/<branch>/<slug>`. Atomic-commit block stays shared across both paths.
- §Report Format — new `Worktree return (path B only)` bullet reporting branch name and HEAD SHA; path A omits the field.

### Consumer workflow pointer updates (no content duplicated)

- [`skills/planning-workflow/SKILL.md`](../../skills/planning-workflow/SKILL.md) — removed the instruction directing the planner to load `worktree-data-sync` for worktree setup (worktree setup is not a planning-time concern).
- [`skills/execution-workflow/SKILL.md`](../../skills/execution-workflow/SKILL.md) — Option 4 Discard retargeted at `agent-orchestration/references/worktree-harness-fallback.md §Remove`; the Red Flag about "dispatch multiple implementers in parallel on the same working tree" reworded to point at §Concurrent Writers; §Integration workflow-skill list deduplicated the two `worktree-data-sync` entries and added `agent-orchestration` as the owner of parallel-dispatch discipline.
- [`skills/merge-workflow/SKILL.md`](../../skills/merge-workflow/SKILL.md) — Step 5 Cleanup Worktree and §Pairs with list split: lifecycle → the fallback reference, data teardown → `worktree-data-sync §Data Teardown`.
- [`skills/semantic-merge/SKILL.md`](../../skills/semantic-merge/SKILL.md) — §When to Use gained an Exception paragraph noting that `parallel/*` branches bypass this skill.
- [`skills/using-superRA/references/codex-tools.md`](../../skills/using-superRA/references/codex-tools.md) and [`skills/agent-orchestration/references/agent-teams.md`](../../skills/agent-orchestration/references/agent-teams.md) — two additional dangling `§Creating a Worktree` references caught in cross-reference audit, rewritten to point at the fallback reference and describe the §Concurrent Writers flow.

Skill-inventory blurbs in `README.md`, `skills/CATEGORIES.md`, and `skills/using-superRA/SKILL.md` are updated to reflect the narrowed `worktree-data-sync` scope. `RELEASE-NOTES.md` carries a 2-bullet entry under 2026-04-17 covering the refactor.

## Verification

- **Structural invariants:** `bash tests/structural-invariants.sh` exits 0.
- **Data-sync CLI regression:** `~/.venv/bin/python -m pytest skills/worktree-data-sync/scripts/test_worktree_data_sync.py -x` → 30 passed in ~3.5s. No tests reference deleted SKILL.md sections; CLI logic is unchanged.
- **Merge-guard regression (synthetic inputs):**

| Input | Expected | Actual |
|---|---|---|
| `git merge parallel/foo/a` | `{}` (exempt) | `{}` |
| `git merge --no-ff parallel/feat/b` | `{}` (exempt) | `{}` |
| `git merge main` | STOP reminder | STOP reminder |
| `git merge --abort` | `{}` (already skipped) | `{}` |

- **Cross-reference audit:** `grep -rn "§Creating a Worktree\|worktree-data-sync.*§Cleanup" skills/ agents/ hooks/` returns zero hits. All `agent-orchestration/references/worktree-harness-fallback` references land at the correct path, and all `worktree-data-sync §\`--mode seed\`` anchors resolve to the actual heading.
- **Integration review:** adversarial `code-quality-reviewer` dispatched against the branch — verdict `REVISE` → fixes landed in `ca67934` (MAJOR M1 anchor corrections; MINOR m1 inventory-blurb and release-notes updates) → re-review APPROVE.

## Limitations

**Merge-guard `parallel/*` exemption not load-bearing under the Claude Code Bash tool harness.** Direct CLI tests against the exact `git merge --no-ff parallel/feedback/agent-dispatch-fixes/alpha -m "..."` command return `{}` (exempt, as intended). When the same command ran through the Claude Code Bash tool during the dogfood pass, the PreToolUse hook emitted the STOP reminder on both `parallel/` slot merges. Reminder is advisory-only so the merges proceeded, but the exemption did not fire as designed. Root cause is likely a JSON-escaping or command-string difference in how the harness serializes the `Bash` invocation to the hook's stdin. A follow-up would harden the hook's input parsing and add an integration test that invokes the hook through a Bash-tool-equivalent JSON wrapper.

**Shared-file appends at EOF still conflict under parallel dispatch.** The §Concurrent Writers boundary contract — "task blocks are line-separated so disjoint tasks produce disjoint hunks" — held for `PLAN.md` (distinct task blocks mid-file merged cleanly) but broke for `RESULTS.md` during the Task 7 / Task 8 dogfood (both agents appended new sections at EOF; overlapping line range → conflict). The conflict was resolved inline by concatenating the two sections. Follow-up `2f58b6c` pre-allocates per-task `RESULTS.md` stubs at planning time so appends land in distinct, disjoint regions.

## Reproducibility pointer

Branch `feedback/agent-dispatch-fixes` at commit [`9a1b097`](../../../../commit/9a1b097). Regression coverage: `bash tests/structural-invariants.sh && ~/.venv/bin/python -m pytest skills/worktree-data-sync/scripts/test_worktree_data_sync.py -x`.
