---
name: refactor-and-integrate
description: Utility skill (any phase). Use when creating drift tests, refactoring analysis code for codebase integration, or writing clean merge integration commits. Carries the three domain-knowledge checklists that define what "good" looks like for each task. Standalone-invokable — can be used outside the integration phase for any refactoring task. Dispatched implementer/reviewer subagents should load this skill via the Skills line when their stage is drift test creation, drift test review, refactoring, integration review, merge proposer, or merge review.
---

# Refactor and Integrate

Utility skill carrying the domain knowledge for three closely related tasks in the integration phase of an analysis:

1. **Creating drift tests** that guard key results from unintended changes during refactoring or future modifications.
2. **Refactoring analysis code** for codebase integration — making the code fit the host project's conventions, utilities, and style without losing data discipline or results.
3. **Writing clean merge integration commits** that preserve intent and research integrity when combining branches.

This is a utility skill, not a workflow skill. The workflow skills (`superRA:integration-workflow` and `superRA:merge-workflow`) own the procedural choreography — when to dispatch agents, how to sequence stages, how to handle iteration loops. This skill owns the content: what a good drift test looks like, what "refactored for codebase fit" means, what a clean merge commit structure is.

**Used by:**
- Dispatched `superRA:implementer` agents during drift test creation, refactoring, and merge proposal stages
- Dispatched `superRA:reviewer` agents during drift test review, integration review, and merge review stages
- Anyone invoking this skill directly for an ad-hoc refactoring task outside the formal integration workflow

## When to Load This Skill

Load `superRA:refactor-and-integrate` via the Skill tool whenever you are:

- Creating a new drift test file → read `references/drift-test-quality.md`
- Reviewing a drift test someone else created → read `references/drift-test-quality.md`
- Refactoring analysis code to fit a host codebase → read `references/codebase-integration.md`
- Reviewing a refactor for codebase integration → read `references/codebase-integration.md`
- Resolving a branch merge where conflicts touch research code → read `references/merge-quality.md`
- Reviewing a proposed merge for integration quality → read `references/merge-quality.md`

The runtime will announce this skill's base directory when it loads. Read the relevant reference file from `<base_dir>/references/<basename>`.

## Dispatch Convention

Workflow skills dispatching a subagent for any of the stages above pass `Skills: superRA:refactor-and-integrate` along with the domain reference basename:

```
Agent(subagent_type: "superRA:implementer"):
  Stage: drift test creation
  Skills: superRA:refactor-and-integrate
  Domain reference: drift-test-quality.md
  [task-specific pointers]
```

```
Agent(subagent_type: "superRA:reviewer"):
  Stage: integration
  Skills: superRA:refactor-and-integrate
  Domain reference: codebase-integration.md
  [task-specific pointers]
```

The agent loads this skill via the Skill tool, receives the base directory, and reads the named reference file. It then uses the reference as its checklist alongside the data-discipline principles from `superRA:econ-data-analysis` (which analysis-touching agents auto-load per the agent definition).

## What Each Reference Covers

### `references/drift-test-quality.md`

Standards for drift test creation and review:

- **Coverage:** every user-confirmed key result has at least one test; main findings, sample statistics, and directional signs all covered
- **Tolerance calibration:** how to set tolerances based on economic reasoning (point estimates, standard errors, counts, signs, significance) — neither too tight (false positives) nor too loose (misses real drift)
- **Independence:** tests run without re-executing the full pipeline; load from saved outputs
- **Clarity and robustness:** test names describe what they protect; no breakage from irrelevant changes
- **Test format:** project conventions (pytest for Python, Test module for Julia)

### `references/codebase-integration.md`

Standards for refactoring analysis code to fit a host codebase:

- **Code integration:** naming consistency, utility function reuse, no debug artifacts, minimal changes to existing files, PR-friendly diffs
- **Economic integration:** specification consistency, transformation consistency, justified inconsistencies documented
- **Data discipline preservation:** CRITICAL — never remove description steps, row count logging, validation checks, or notebook documentation cells during refactoring. You may reorganize; you may not delete.
- **Handling inconsistencies:** when to follow the convention, when to use judgment, when to flag for the user
- **PR quality:** focused diff, clean commits, self-contained, drift tests pass, appropriate tolerances

### `references/merge-quality.md`

Standards for merge proposals and merge review:

- **Intent preservation:** read commits and diffs to understand WHY, not just WHAT; no silent losses
- **Research integrity:** no silent result changes, variable definitions consistent, sample construction preserved, user decisions on research-meaningful conflicts implemented correctly
- **Two-commit structure:** mechanical commit (lowest-assumption reconciliation) + integration commit (adapt code, docs, tests to incorporate incoming intent)
- **Research-meaningful escalation (Tier 3):** when to flag for the user — variable definitions, sample construction, econometric specifications, data processing, results
- **Integration map format:** how to document conflict decisions with classification and rationale
- **Verification and data discipline:** drift tests pass, no stale references, pipeline runs, data discipline artifacts preserved through the merge

## Using Multiple References in One Task

Some tasks touch more than one domain. A refactor that happens during a merge uses both `codebase-integration.md` and `merge-quality.md`. A drift test review that flags a sign-flip caused by a refactor uses both `drift-test-quality.md` and `codebase-integration.md`.

When your dispatch prompt names multiple domain references, load them all before starting work. The checklists are designed to compose — they cover different facets of the same underlying goal (integrate analysis into the codebase without silently changing results).

## Integration

**Used by workflow skills:**
- **`superRA:integration-workflow`** — Dispatches drift test creation (loads `drift-test-quality.md`), drift test review (`drift-test-quality.md`), refactoring (`codebase-integration.md`), and integration review (`codebase-integration.md`)
- **`superRA:merge-workflow`** — Dispatches post-merge refactoring (`codebase-integration.md`) and post-merge integration review (`codebase-integration.md`) during the refactor-review loop triggered by drift test failure or reviewer REVISE
- **`superRA:semantic-merge`** — Dispatches merge proposer (`merge-quality.md`) and merge reviewer (`merge-quality.md`) for tier classification and conflict resolution

**Auto-loaded alongside:**
- **`superRA:econ-data-analysis`** — Data discipline (auto-loaded by `implementer` / `reviewer` agents whenever the stage involves analysis code)
- **`superRA:script-to-notebook`** — Notebook formatting (same auto-load)
