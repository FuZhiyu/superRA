# Parallel-Implementer Worktree Isolation — Results

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-17 (Task 1)
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
