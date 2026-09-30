---
title: "Reproduce in an Isolated Worktree and Merge Back"
status: revise
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

## Review Notes

Tier: quick. Focuses: the CLAUDE.md §Teach the Protocol instruction gate on added skill lines, cross-reference consistency with the owners, correctness of the verdict protocol.

1. **[BLOCKING] The comparison can approve an output the build never rewrote.** Seeding copies every gitignored root into the worktree ([worktree-data-sync SKILL.md](../../../skills/worktree-data-sync/SKILL.md), §Managed Path Discovery), and stage 4's `.gitignore` puts generated outputs there, so the worktree starts holding the originals. `repro build` does not check that a step rewrote its outs ([repro_run.py:196-227](../../../skills/task-tree/scripts/repro_run.py#L196-L227)). A script that writes through a hard-coded absolute path — a case [adoption.md:10](../../../skills/reproducibility/references/adoption.md#L10) expects stage 3 to note — writes into the original project folder, breaking isolation, and leaves the seeded copy in the worktree, where [isolated-run.md:19-21](../../../skills/onboarding/references/isolated-run.md#L19-L21)'s `cmp` finds identical bytes and marks the task `approved`. A misdeclared out has the same effect. Fix: before building a slice, resolve the hard-coded paths noted in `## Details`, and either remove the slice's seeded outs in the worktree or require each compared out to be newer than the build start; an out not rewritten is a divergence.
2. **[BLOCKING] Description of the owner's behavior (gate test 1, DRY).** [isolated-run.md:13](../../../skills/onboarding/references/isolated-run.md#L13) ", which clones by copy-on-write when the worktree is on the same disk as the project" narrates what `worktree-data-sync --mode seed` does, which its SKILL.md §`--mode seed` states. The step itself also repeats [worktree-harness-fallback.md:21](../../../skills/agent-orchestration/references/worktree-harness-fallback.md#L21) ("Then seed non-git data via … `--mode seed`"). Fix: cut the clause; keep the step only if the step list needs it for ordering.
3. **[ADVISORY] Reconcile step does not scope the apply.** [isolated-run.md:31](../../../skills/onboarding/references/isolated-run.md#L31) runs `--mode apply --action overwrite` over the whole diff, which also carries the worktree's gitignored `.superra-repro/` (cache, logs, run records) and any other managed scratch into the project. Name the paths: the declared outs that differ, plus the check stamps under `.superra-repro/stamps/` if check steps should read fresh.
4. **[ADVISORY] Default placement is a temp directory.** The fallback's default, `${TMPDIR:-/tmp}/superRA-worktrees/...`, is written "for ephemeral parallel worktrees" ([worktree-harness-fallback.md:47](../../../skills/agent-orchestration/references/worktree-harness-fallback.md#L47)); a multi-day reproduction run with cloned data there can be swept by OS temp cleanup. Consider naming a durable location outside the synced folder.
