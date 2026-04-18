# Parallel-Implementer Worktree Isolation — Results

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-17 (Task 3)
**Status:** In Progress

---

## Task 1: Worktree lifecycle fallback + §Concurrent Writers subsection

**Status:** Implemented (awaiting review)

### Key changes
- **New:** `skills/agent-orchestration/references/worktree-harness-fallback.md` — ~60 lines covering harness-tool preference, raw-git create/enter/remove, placement priority, and four gotchas.
- **Updated:** `skills/agent-orchestration/SKILL.md` — added §Concurrent Writers Require Worktree Isolation (seven subsections: ownership split, branch naming, plain-merge rationale, worktree lifecycle pointer, data seeding, dispatch, no-PLAN.md-bookkeeping rule). Extended §Dispatch Templates: new optional `Worktree:` field on the implementer template + required canned steering sentence when the field is present.

### Section anchor verification
`grep -n "^## \|^### "` on `agent-orchestration/SKILL.md` confirms the new section sits between §Workload Balancing (line 16) and §Dispatch Templates (line 164). All cross-references in the new content target existing anchors (§Dispatch Templates, `handoff-doc` §Living Plan, `hooks/merge-guard`, `semantic-merge/SKILL.md`, `worktree-data-sync` §Seed).

### Notes
- The canned steering sentence for `Worktree:` is codified as **required**, not additive — the single exception to the existing "additive-only" `Additionally:` rule. Justification in-place: the agent's spawn cwd defaults would otherwise cause silent wrong-copy edits.
- `references/worktree-harness-fallback.md` lives under `agent-orchestration/`, not `worktree-data-sync/` — worktree lifecycle is an orchestration concern. Task 2 points `worktree-data-sync` at this location.

## Task 2: Refactor `worktree-data-sync` to non-git data sync only

**Status:** Implemented (awaiting review)

### Key changes
- **Description frontmatter** narrowed to "syncing non-git-controlled data files between existing worktrees (seeding, diffing, reconciling, teardown). Worktree lifecycle out of scope."
- **Deleted:** §When to Use a Worktree (decision table, ~13 lines) and §Creating a Worktree (6 subsections including Directory Selection, Safety Verification, Create, Seed Data, Verify Accessibility, Report Location — ~80 lines).
- **Renamed §Cleanup → §Data Teardown** — retained the "seeded data disappears with the worktree directory" fact; removed `git worktree remove` prescription and the Option 4 Discard block (branch deletion). Repointed lifecycle operations to `agent-orchestration/references/worktree-harness-fallback.md`.
- **New §See Also** pointing at the lifecycle reference and at `agent-orchestration` §Concurrent Writers.

### Section outline after refactor
Frontmatter → `# Worktree Data Sync Skill` → §When to Use → §Command Surface (with §Endpoints) → §Modes (§`--mode seed` / §`--mode diff` / §`--mode apply`) → §Managed Path Discovery → §Examples → §Data Teardown → §See Also.

### Test verification
`~/.venv/bin/python -m pytest skills/worktree-data-sync/scripts/test_worktree_data_sync.py -x` → **30 passed in 3.37s**. No tests touched deleted SKILL.md sections; CLI logic unchanged.

## Task 3: Implementer dedicated-worktree path

**Status:** Implemented (awaiting review)

### Key changes
- **§Before You Start** — added step 6: when `Worktree:` is present, enter it (harness tool or `cd` + verify `git rev-parse --show-toplevel`), all I/O inside, do not merge/rebase/push/cleanup, report branch + HEAD SHA.
- **§Handoff → Update the Docs and Commit** — split the single "Shared-repo commit discipline" note into (A) shared-worktree path with the existing discipline and (B) dedicated-worktree path on `parallel/<branch>/<slug>`. Atomic-commit block stays shared across both paths.
- **§Report Format** — new bullet: `Worktree return (path B only)` reports branch name and HEAD SHA. Path A omits the field.
