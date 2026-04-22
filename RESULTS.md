# Tighten Phase B Upstream-Intent and Minimum-Net-Diff Contract Plan — Results

> Mirrors PLAN.md structure. Updated after each task with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-22 (Task 4 verification, agent refresh, and reviewer pass)
**Status:** Completed

---

## Task 1: Replace the branch-wide Phase B record with `## Upstream Intent`

**Status:** Completed (Task 1 approved 2026-04-22)

### Key Findings
- `skills/handoff-doc/references/plan-anatomy.md` now defines `## Upstream Intent` as the Phase B branch-wide contract, with explicit anchor lines for `Base branch`, `Frozen merge base SHA`, and `Reviewed upstream range`.
- The branch-wide cluster format now records `Upstream change cluster`, `Upstream intent`, and `Default merged expectation`, shifting the section from a disappearing todo list to a stable round-level contract.
- `agents/reviewer.md` and `agents/implementer.md` now split section ownership cleanly: orchestrator owns the anchor lines, reviewer owns the change clusters plus stale-section cleanup on no-overlap re-entry, and implementers must read but not edit the section.

### Notes
- The task-local overlap note contract remains explicit in both the anatomy and reviewer protocol: upstream file / commit / change, plain-language upstream intent, minimal allowed branch delta, and stale branch-side content that must not survive. Implementer guidance now also makes the no-material-overlap path explicit: if `## Upstream Intent` is absent after re-entry, no prior-round branch-wide contract survives.

## Task 2: Rewrite `integration-workflow` Phase B around the frozen upstream contract

**Status:** Completed (Task 2 approved 2026-04-22)

### Key Findings
- `skills/integration-workflow/SKILL.md` now freezes a `MERGE_BASE_SHA` for each active Phase B round and threads that anchor through the reviewer dispatch and surviving-diff confirmation.
- The reviewer dispatch now separates the branch-wide upstream-intent pass from the task-local review-note pass, and explicitly preserves the no-material-upstream-change path by deleting any stale prior-round `## Upstream Intent` section when the new base-side scan finds no overlap.
- Phase B completion no longer depends on the branch-wide section draining to empty; instead, the reviewer performs a narrow task re-review plus a branch-wide pruning sweep over `git diff <MERGE_BASE_SHA>..HEAD`, confirming the surviving diff is justified by approved task objectives plus the recorded upstream contract.

### Notes
- D->B re-entry is now defined as a rewrite of the frozen anchor / upstream contract for the new round rather than appending a second round of branch-wide intent beneath the first; if the new round finds no material overlap, the stale section is removed instead of being re-anchored.

## Task 3: Tighten generic integration and merge gates to "base-owned by default"

**Status:** Completed (Task 3 approved 2026-04-22)

### Key Findings
- `skills/refactor-and-integrate/SKILL.md` now narrows the frozen merge-base diff rule to Phase B / upstream-contract paths and adds a governing-baseline fallback for drift-test and standalone refactor / merge uses.
- `skills/refactor-and-integrate/references/codebase-integration.md` now requires base-diff pruning in every integration review pass and adds blocking checks for silent restorations and unjustified surviving hunks.
- `skills/refactor-and-integrate/references/merge-quality.md` and `skills/semantic-merge/SKILL.md` now align Phase B merge behavior with the same rule: preserve base intent by default and let current-branch hunks survive only when approved task objectives or reviewer-recorded allowed deltas require them.

### Notes
- The generic integration and merge surfaces were kept DRY: `integration-workflow` owns the Phase B choreography, while `refactor-and-integrate` and `semantic-merge` own the reusable blocking rules and merge behavior.

## Task 4: Add focused structural invariants and verify the new contract

**Status:** Completed (Task 4 approved 2026-04-22)

### Key Findings
- `tests/test-phase-b-upstream-intent-contract.sh` remains a narrow structural guard over canonical runtime files only, and now additionally asserts the no-overlap re-entry cleanup path and the non-Phase-B governing-baseline fallback.
- Wired the new guard into `tests/check-harness-compatibility.sh` so the repo's top-level compatibility entry point now covers this Phase B contract as part of the standard structural check surface.
- Refreshing `.codex/agents/superra_implementer.toml` and `.codex/agents/superra_reviewer.toml` was necessary after editing `agents/implementer.md` and `agents/reviewer.md`; the existing Codex generation check correctly caught that drift before the rerun passed.

### Notes
- Verification run 1: `bash tests/test-phase-b-upstream-intent-contract.sh` -> `Passed: 31    Failed: 0`.
- Verification run 2: `bash tests/check-harness-compatibility.sh` -> passed after regenerating the project-scoped Codex agent files with `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project`.
- Direct-mode reviewer pass over the touched canonical files found no blocking inconsistencies after the test rerun; all four task blocks are approved with no open review-notes blockquotes.
