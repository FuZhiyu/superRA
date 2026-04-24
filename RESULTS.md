# Worktree Branch Naming Fix - Results

> Mirrors PLAN.md structure. Updated after each step with key findings.

**Last updated:** 2026-04-24 (Task 1 approved)
**Status:** Completed

**PR:** https://github.com/FuZhiyu/superRA/pull/23

---

## Task 1: Fix parallel worktree branch namespace

**Status:** Completed (Task 1 approved 2026-04-24)

### Key Findings
- The old `${current_branch}/parallel/<slug>` protocol fails when `${current_branch}` already exists as a branch ref because Git cannot create `refs/heads/<branch>/...` under an existing `refs/heads/<branch>` leaf.
- The new `${current_branch}-agent/parallel/<slug>` protocol preserves the `/parallel/` infix used by `merge-guard` while avoiding that ref namespace collision.
- Active runtime surfaces now point to `<current-branch>-agent/parallel/<slug>`; historical `docs/plans/` records were left unchanged as historical records.

### Verification
- `python3 scripts/sync_codex_agents.py --scope project --check`
- `bash hooks/merge-guard` regression inputs for `foo-agent/parallel/a`, `feat-agent/parallel/b`, `main`, and `--abort`
- Active-surface grep for old branch-name patterns under `skills`, `agents`, `hooks`, `tests`, `.codex`, `README.md`, and `AGENTS.md`
- Throwaway Git repo ref test: `feature/parallel/a` failed under existing `feature`; `feature-agent/parallel/a` succeeded
