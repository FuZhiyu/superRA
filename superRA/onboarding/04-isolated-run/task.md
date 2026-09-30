---
title: "Reproduce in an Isolated Worktree and Merge Back"
status: not-started
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
