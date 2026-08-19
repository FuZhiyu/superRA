# Standalone Semantic-Merge Mode

Standalone mode uses `semantic-merge/SKILL.md` §Shared Steps and §Semantic Coherence Checklist. This reference carries the standalone boundary, inputs, and report fields.

## Boundary

Standalone semantic-merge carries the merge through to **semantic coherence** using the Shared Steps, landing the merge commit plus any propagation commits needed, and captures the approved resolution in the commit body — the durable record by design, the same "git for change" principle that drops the in-tree sync record in workflow mode. The stopping rule and per-commit protection-pass come from `SKILL.md §Semantic Coherence Checklist §Scope boundary`, with existing tests and drift tests as the protection here. **Codebase coherence**, when wanted, is the caller's job via `refactor-and-integrate` after this skill returns.

## Inputs

Caller supplies (or the agent infers from the session):

- requested operation: `merge | rebase | cherry-pick`
- incoming ref (branch, tag, or commit range)
- current branch
- governing baseline (merge base, or caller-declared baseline)
- direction — ask when direction is ambiguous and affects results, scope, or architecture

Intent sources are per `SKILL.md §Shared Steps` step 2.

## Mode-Specific Process

1. Run the requested merge / rebase / cherry-pick after intent investigation.
2. **Land the merge commit plus any propagation commits needed to reach semantic coherence** per `SKILL.md §Shared Steps` step 5, recording the resolution in the commit body of the merge commit (and any propagation commit). The commit body captures the resolution thesis (what the merge kept, dropped, or synthesized), file/script-level impact and codebase context useful for later `refactor-and-integrate` review, any user decisions logged during escalation, and the checks run. It explains the approved post-merge diff; it is not a backlog of unresolved semantic work.

## Report

Report:

- operation, incoming ref, governing baseline, and direction
- current-branch intent and incoming intent
- merge commit SHA and any propagation-commit SHAs
- user decisions asked and logged
- stash status (if any)
- checks run (existing tests, drift tests) and codebase context recorded for the caller / `refactor-and-integrate`
