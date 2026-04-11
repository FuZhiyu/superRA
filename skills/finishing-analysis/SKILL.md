---
name: finishing-analysis
description: Deprecated — split into superRA:integration-workflow (drift tests, refactor-review loop, report generation, dev document handling) and superRA:merge-workflow (main update, post-merge verification + refactor-review loop, local merge or PR push, worktree cleanup). The coordinating logic now lives directly in superRA:execution-workflow Step 4. This stub will be removed once cross-references migrate.
---

# Finishing Analysis (deprecated)

The `finishing-analysis` skill has been split as part of the workflow/utility restructure. Its content now lives in three places:

- **Reproducibility verification + base branch detection + 4-option menu** → already moved to `superRA:execution-workflow` Steps 3 and 4 (Phase A4/A5).
- **Drift test creation + refactor-review loop + work-journal report + development document handling** → `superRA:integration-workflow`.
- **Main update via semantic-merge + post-merge verification (drift tests AND fresh integration review) + refactor-review loop on post-merge failure + local merge or PR push + worktree cleanup** → `superRA:merge-workflow`.

**To finish an analysis, the orchestrator (`superRA:execution-workflow` Step 4) directly dispatches integration-workflow then merge-workflow when the user chooses Option 1 (merge) or Option 2 (PR).** No coordination skill is needed in the middle.

This stub exists temporarily to redirect anything still pointing at `superRA:finishing-analysis`. It will be deleted once all cross-references have been updated.
