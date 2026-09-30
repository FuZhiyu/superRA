---
title: "Reproduce in an Isolated Worktree and Merge Back"
status: implemented
depends_on: []
---

## Objective

Write `skills/onboarding/references/isolated-run.md`, the protocol for stages 5 and 6.

- **Explain before acting:** what a worktree is, why the run happens there, and that the original project folder stays untouched until the merge.
- **Setup:** worktree per [worktree-harness-fallback.md](../../../skills/agent-orchestration/references/worktree-harness-fallback.md); data seeded by copy-on-write via `superRA:worktree-data-sync`.
- **Run:** upstream-first by researcher-chosen slices; code edits only to make the code run, each committed in the worktree with the reason.
- **Verdict per task:** compare rebuilt outputs with the originals in the main folder. Match → `approved`. Failure or divergence → `revise`, with the problem, the edits tried, and the diff in `## Review Notes`. `## Results` keeps the current results.
- **Merge back:** explain the branch, show the diff, merge after the researcher agrees, then remove the worktree. Work beyond minimal fixes routes to `superRA:superintegrate`.
- **Outputs after the merge:** the lock records the worktree-built outputs, so the main folder's originals read stale where bytes differ. Offer the choice: copy the rebuilt outputs back (overwrites originals, needs consent) or rebuild in place.

## Details

- A project already in git with uncommitted changes: the worktree will not contain them. Ask the researcher to commit or leave them out before creating it.
- Dropbox or iCloud projects: place the worktree outside the synced folder; the placement rule already says so. Copy-on-write needs source and destination on the same volume.

## Results

[isolated-run.md](../../../skills/onboarding/references/isolated-run.md) covers stages 5 and 6.

- **Explanation:** a worktree is a second folder of the same project on its own branch; the rerun happens there so the originals it is checked against stay untouched, and coauthors on a shared Dropbox folder never see half-built results.
- **Setup:** uncommitted changes are committed or left out first; the worktree follows `worktree-harness-fallback.md`, whose placement rule already keeps Dropbox projects' worktrees outside the synced folder; data is seeded by `worktree-data-sync --mode seed`.
- **Run:** by slice per `adoption.md` §The first build. Code edits only to make the code run, each committed with its reason; a fix that would change what a script computes stops for the researcher. Each rebuilt output is compared with its original by bytes, then by values within a stated tolerance, figures through their plotted data. Match: `approved`. Failure or divergence: `revise` with `## Review Notes`. `## Results` keeps the current results either way.
- **Merge back:** explain and show the diff, `git merge` on agreement (`superintegrate` for a larger branch), then reconcile outputs — copy rebuilds over originals with `worktree-data-sync` diff and apply, with consent, or rebuild in place — and remove the worktree.
- **Not exercised:** no worktree run was performed; the researcher's end-to-end trial covers it.
