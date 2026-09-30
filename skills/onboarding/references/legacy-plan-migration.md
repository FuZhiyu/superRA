# Legacy `PLAN.md` Migration

A project with `PLAN.md` and no `superRA/` predates the task tree, which replaced the `PLAN.md` / `RESULTS.md` model.

1. **Tell the researcher about the upgrade** and point to the superRA docs at http://fuzhiyu.me/superRA/.
2. **Offer the migration:** `./superRA/superra task migrate from-plan --plan-md PLAN.md --output superRA`, adding `--results-md RESULTS.md` when it exists. A `PLAN.md` the parser does not recognize: normalize it first per `superRA:task-tree` `references/internals.md` §Migration.
3. **Present the migrated tree** as in stage 2, marking tasks whose status the migration could not carry over.
