# Isolated Reproduction Run and Merge Back

Stages 5 and 6: rerun the project in a separate worktree, compare each rebuilt output with its original, and merge back.

## Explain the worktree

A worktree is a second folder holding the same git project on its own branch. The rerun happens there, so the project folder — and the original outputs the rerun is checked against — stays untouched until the researcher chooses to merge. In a shared Dropbox folder, coauthors also never see half-built results.

## Set up

1. **Uncommitted changes:** the worktree holds only committed files. Ask the researcher to commit them or leave them out.
2. **Create the worktree** per `agent-orchestration/references/worktree-harness-fallback.md`, on a new branch such as `onboarding/reproduction`.
3. **Seed the data** with `superRA:worktree-data-sync` `--mode seed`, which clones by copy-on-write when the worktree is on the same disk as the project.

## Run

- **Build by slice** per `reproducibility/references/adoption.md` §The first build, from inside the worktree.
- **Edit code only to make it run:** a hard-coded path, a missing package, a moved input. Commit each fix in the worktree with its reason and task. A fix that would change what a script computes: stop and ask.
- **Compare each rebuilt output with its original** in the project folder: identical bytes first (`cmp`), then values within a tolerance you state for tables and data, and figures through their plotted data.
- **Record the verdict per task:**
  - **Match** — `approved`; `## Results` adds which build reproduced it and whether bytes or values matched.
  - **Failure or divergence** — `revise`; `## Review Notes` states what failed or differed, by how much, and the fixes tried.
  - Either way, `## Results` keeps presenting the current results.
- **Commit** the task files and `repro-lock.json` in the worktree.

## Merge back

1. **Explain the merge:** the branch carries `superRA/`, `repro-lock.json`, and the code fixes. Show `git diff --stat` against the base and each fix.
2. **Merge after the researcher agrees,** with `git merge` from the project folder. A branch grown beyond minimal fixes: `superRA:superintegrate` instead.
3. **Reconcile the outputs.** `repro-lock.json` records the rebuilt outputs, so each original that differs from its rebuild reads stale in the project folder. Offer either:
   - copy the rebuilds over the originals with `superRA:worktree-data-sync` (`--from <worktree> --to <project>`, `--mode diff`, then `--mode apply --action overwrite`) — overwrites originals, so only with consent;
   - `superra repro build` in the project folder.
4. **Remove the worktree** per `worktree-harness-fallback.md` §Remove.
