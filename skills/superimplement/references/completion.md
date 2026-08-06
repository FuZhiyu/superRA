# Closing IMPLEMENT

The phase-exit gate, run once the frontier is empty — in either execution mode. Read this file directly; closing the phase is not a reason to load `superRA:superimplement`.

## Verify Pipeline and Reproducibility

After every task is `approved`, walk all three checks against actual command output, not recollection. Any failure blocks the completion menu.

1. **All code committed?**
   ```bash
   git status
   ```
   Uncommitted changes: investigate (probably a missed inline edit), commit, or ask the user.

2. **Results recorded?** Read the completed task files. Fails in either direction against `communicate`: missing, thin, or status-report-only results for substantive work; results that restate an artifact, diff, commit body, or child task instead of pointing at it.

3. **Reproducibility verification.**
   - Multi-script pipeline runs end-to-end if the tree declares one.
   - Outputs exist and came from committed code, not ad-hoc REPL state.
   - Retained task companions are committed and pass `../../using-superra/references/task-companion-files.md`.

Fix any failure before proceeding. Never present completion options for unreproducible work.

## Present Completion Options

**Domain pre-step (theory-modeling only): notation/assumption promotion.** Scan each task's `## Results` Notation & Assumptions Ledger for entries whose symbol or assumption is not yet in the canonical Notation Conventions table. Surface any candidates via `AskUserQuestion` with a per-candidate Promote / Keep-in-ledger / Remove choice. Apply the answers: promotions are inline-edited into the canonical table and committed; keep-in-ledger candidates stay; remove deletes both the ledger entry and any in-text use (re-dispatch the implementer for code changes). Skip when the domain is not theory-modeling or every ledger says "None." Necessity gate, ledger schema, and canonical-vs-ledger split: `theory-modeling/SKILL.md` §Documentation and handoff.

**Present the 4 completion options via `AskUserQuestion`.**

```
Work complete and verified. <one line naming what the tree delivered>
Results: <dashboard URL for the affected task>
What would you like to do?

1. Proceed with integration
2. Change the task tree
3. Keep the branch as-is (I'll handle it later)
4. Discard this work
```

The folded-in answer (per the autonomy contract) goes in the first commit of whatever workflow the option dispatches to.

**Execute the user's choice:**

- **Option 1 (Proceed with integration):** invoke `superRA:superintegrate`.
- **Option 2 (Change the task tree):** re-enter `superRA:superplan §User Feedback and Changing the Task Tree` with the researcher's scope change as the trigger; it ends by resuming on the affected frontier.
- **Option 3 (Keep as-is):** report the branch name and worktree path, then stop. No cleanup.
- **Option 4 (Discard):** confirm by typed input — the user types `discard` exactly. Resolve the base branch with `git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null` (ask via `AskUserQuestion` if ambiguous), then tear down: `git checkout <base-branch>`, `git branch -D <work-branch>`, remove the worktree if the work was in one. Report what was deleted and stop.
