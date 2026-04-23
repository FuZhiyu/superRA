# Standalone Semantic-Merge Mode

Use when this skill is invoked directly for a merge, rebase, cherry-pick, or branch sync outside `integration-workflow`. Also load `sync-quality.md` and `sync-map-format.md`.

Standalone mode completes semantic merge work. It does not stop after identifying the map.

## Process

1. Identify the requested operation, incoming ref, current branch, governing baseline, and direction. Ask when direction is ambiguous and affects results, scope, or architecture.
2. Confirm the worktree is clean enough to operate. Preserve unrelated dirty state with a reversible named stash and report it.
3. Research current-branch intent from branch name, commits, PLAN.md / RESULTS.md if present, docs, and diffs.
4. Research incoming intent from commits, diffs, docs, and any caller-supplied context.
5. Create or update `SEMANTIC_MERGE.md` when the operation is material, lacks PLAN.md task structure, or leaves file/script-level obligations.
6. Ask the researcher before resolving research-meaningful conflicts. Record decisions in PLAN.md when present, otherwise in `SEMANTIC_MERGE.md` and the relevant commit body.
7. Run the requested merge/rebase/cherry-pick only after intent research.
8. Resolve conflicts by semantic intent, preferring synthesis when both sides are valid and compatible.
9. Land the sync commit.
10. Make follow-up semantic propagation commits when needed so non-conflicted sibling files, scripts, tests, docs, and handoff records reflect the chosen resolution.
11. Run targeted checks and existing drift tests when present. Do not silently re-expect drift tests after meaningful result changes.
12. Stop before broad codebase refactor. If broad refactor is needed, record it as a remaining obligation.

## Report

Report:

- operation, incoming ref, governing baseline, and direction
- current-branch intent and incoming intent
- sync commit and propagation commits
- merge record location or why none was needed
- user decisions asked and logged
- checks run and remaining obligations
