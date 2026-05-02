---
author: "[[Julie Zhiyu Fu]]"
date: 2026-04-22
timestamp: "2026-04-22T23:24:06"
session_id: "session-20260422-phase-c-results-maturation"
git_commit: "bdd8cf99e0d73ca6fa84ddeb250f3d1b3ea05014"
git_message: "results: relocate RESULTS.md to docs/plans"
git_dirty: false
branch: "tighten-integration-rules"
merge_base: "addc9ca7fe1bdbedb080d92095facb649074c1e4"
tags: ["report", "results", "superRA", "phase-b", "integration-workflow"]
project: "[[superRA]]"
permalink: "docs/plans/2026-04-22-phase-b-upstream-intent-contract-results"
---

# Tighten Phase B Upstream-Intent and Minimum-Net-Diff Contract — Results

**Status:** Complete — Tasks 1-4 are approved, Phase B integration review returned zero task annotations, and this file is the Phase C permanent record for the branch's results. [`2026-04-22-phase-b-upstream-intent-contract-plan.md`](./2026-04-22-phase-b-upstream-intent-contract-plan.md)
**Branch:** `tighten-integration-rules`
**Frozen merge base:** `addc9ca7fe1bdbedb080d92095facb649074c1e4` against `origin/main`. [`2026-04-22-phase-b-upstream-intent-contract-plan.md`](./2026-04-22-phase-b-upstream-intent-contract-plan.md)
**Companion plan:** [`2026-04-22-phase-b-upstream-intent-contract-plan.md`](./2026-04-22-phase-b-upstream-intent-contract-plan.md)

## Objective

Recast Phase B around a frozen-base upstream-intent contract so the base branch is authoritative by default, branch deltas survive only when they serve approved task objectives, and implementers receive task-local upstream-intent instructions without reconstructing git history. [`2026-04-22-phase-b-upstream-intent-contract-plan.md`](./2026-04-22-phase-b-upstream-intent-contract-plan.md)

## Source Surfaces

No empirical dataset was used. The source material for this refactor is the repository itself:

- Handoff and role surfaces: [`skills/handoff-doc/references/plan-anatomy.md`](../../skills/handoff-doc/references/plan-anatomy.md), [`agents/implementer.md`](../../agents/implementer.md), and [`agents/reviewer.md`](../../agents/reviewer.md)
- Phase B choreography: [`skills/integration-workflow/SKILL.md`](../../skills/integration-workflow/SKILL.md)
- Generic integration and merge rules: [`skills/refactor-and-integrate/SKILL.md`](../../skills/refactor-and-integrate/SKILL.md), [`skills/refactor-and-integrate/references/codebase-integration.md`](../../skills/refactor-and-integrate/references/codebase-integration.md), [`skills/refactor-and-integrate/references/merge-quality.md`](../../skills/refactor-and-integrate/references/merge-quality.md), and [`skills/semantic-merge/SKILL.md`](../../skills/semantic-merge/SKILL.md)
- Verification surface: [`tests/test-phase-b-upstream-intent-contract.sh`](../../tests/test-phase-b-upstream-intent-contract.sh), [`tests/check-harness-compatibility.sh`](../../tests/check-harness-compatibility.sh), [`skills/codex-superra-setup/scripts/test_sync_codex_agents.py`](../../skills/codex-superra-setup/scripts/test_sync_codex_agents.py), and [`skills/codex-superra-setup/scripts/sync_codex_agents.py`](../../skills/codex-superra-setup/scripts/sync_codex_agents.py)

## Methodology

The integration pass covered three layers. First, the handoff and role surfaces were checked for the branch-wide `## Upstream Intent` contract and the reviewer / implementer ownership split. [`skills/handoff-doc/references/plan-anatomy.md`](../../skills/handoff-doc/references/plan-anatomy.md) [`agents/reviewer.md`](../../agents/reviewer.md) [`agents/implementer.md`](../../agents/implementer.md) Second, the Phase B workflow choreography was checked for frozen-anchor recording, no-overlap cleanup on re-entry, and the surviving-diff confirmation pass. [`skills/integration-workflow/SKILL.md`](../../skills/integration-workflow/SKILL.md) Third, the reusable integration and merge references were checked for the base-owned-by-default rule on Phase B paths and the governing-baseline fallback elsewhere. [`skills/refactor-and-integrate/SKILL.md`](../../skills/refactor-and-integrate/SKILL.md) [`skills/refactor-and-integrate/references/codebase-integration.md`](../../skills/refactor-and-integrate/references/codebase-integration.md) [`skills/refactor-and-integrate/references/merge-quality.md`](../../skills/refactor-and-integrate/references/merge-quality.md) [`skills/semantic-merge/SKILL.md`](../../skills/semantic-merge/SKILL.md)

## Results

### Approved branch state

The approved Phase B round used `origin/main` as the integration base and froze merge base `addc9ca7fe1bdbedb080d92095facb649074c1e4`. That round ended with zero task annotations, and the merge step was a no-op because `origin/main` still matched the frozen base. [`2026-04-22-phase-b-upstream-intent-contract-plan.md`](./2026-04-22-phase-b-upstream-intent-contract-plan.md)

Because the approved round found no material overlap, this branch did not carry an active `## Upstream Intent` section into Phase C. The permanent record therefore documents the shipped contract surfaces rather than a live branch-specific overlap log. [`2026-04-22-phase-b-upstream-intent-contract-plan.md`](./2026-04-22-phase-b-upstream-intent-contract-plan.md) [`skills/integration-workflow/SKILL.md`](../../skills/integration-workflow/SKILL.md)

### Handoff and role contract

[`skills/handoff-doc/references/plan-anatomy.md`](../../skills/handoff-doc/references/plan-anatomy.md) now defines `## Upstream Intent` as the Phase B branch-wide contract. The section records `Base branch`, `Frozen merge base SHA`, and `Reviewed upstream range`, and each change cluster records `Upstream change cluster`, `Upstream intent`, and `Default merged expectation`. [`skills/handoff-doc/references/plan-anatomy.md`](../../skills/handoff-doc/references/plan-anatomy.md)

[`agents/reviewer.md`](../../agents/reviewer.md) writes the branch-wide clusters and the task-local overlap notes, including the upstream file / commit / change being honored, the upstream intent in plain language, the minimal allowed branch delta, and stale branch-side content that must not survive. [`agents/reviewer.md`](../../agents/reviewer.md) [`agents/implementer.md`](../../agents/implementer.md) reads the branch-wide section before integration edits, treats an absent section after D->B re-entry as the current no-overlap path, and does not edit the reviewer-owned contract. [`agents/implementer.md`](../../agents/implementer.md)

### Phase B choreography

[`skills/integration-workflow/SKILL.md`](../../skills/integration-workflow/SKILL.md) freezes `MERGE_BASE_SHA` before reviewer dispatch and records the active-round anchor in the companion plan. The reviewer writes `## Upstream Intent` only when the base-side scan finds material overlap; if a new round finds no material overlap, a stale prior-round section is deleted in the same review pass instead of being re-anchored. [`skills/integration-workflow/SKILL.md`](../../skills/integration-workflow/SKILL.md)

The review loop no longer treats an empty branch-wide section as the completion criterion. The completion condition is that in-scope tasks reach `Integration status: APPROVED` and the reviewer confirms that every surviving hunk in `git diff <MERGE_BASE_SHA>..HEAD` is justified by approved task objectives plus the recorded upstream contract. [`skills/integration-workflow/SKILL.md`](../../skills/integration-workflow/SKILL.md)

### Generic integration and merge rules

[`skills/refactor-and-integrate/SKILL.md`](../../skills/refactor-and-integrate/SKILL.md) narrows the frozen merge-base diff rule to Phase B / upstream-contract paths and uses the governing git range or touched-file diff as the baseline elsewhere. [`skills/refactor-and-integrate/references/codebase-integration.md`](../../skills/refactor-and-integrate/references/codebase-integration.md) makes base-diff pruning part of every integration review pass and treats upstream deletions and relocations as the default merged state unless an approved task objective and reviewer note authorize restoration. [`skills/refactor-and-integrate/references/codebase-integration.md`](../../skills/refactor-and-integrate/references/codebase-integration.md)

[`skills/refactor-and-integrate/references/merge-quality.md`](../../skills/refactor-and-integrate/references/merge-quality.md) and [`skills/semantic-merge/SKILL.md`](../../skills/semantic-merge/SKILL.md) apply the same base-owned-by-default rule when Phase B calls semantic merge: current-branch hunks survive only when approved task objectives or reviewer-recorded allowed deltas require them. [`skills/refactor-and-integrate/references/merge-quality.md`](../../skills/refactor-and-integrate/references/merge-quality.md) [`skills/semantic-merge/SKILL.md`](../../skills/semantic-merge/SKILL.md)

## Verification

`bash tests/test-phase-b-upstream-intent-contract.sh` passed 31 assertions and 0 failures on the current tree. The guard checks the retired-label removal, the upstream-intent anchor lines, the no-overlap cleanup path, the branch-wide pruning sweep wording, the governing-baseline fallback outside Phase B, and the Phase B semantic-merge contract. [`tests/test-phase-b-upstream-intent-contract.sh`](../../tests/test-phase-b-upstream-intent-contract.sh)

`bash tests/check-harness-compatibility.sh` also passed. That run includes the Phase B contract guard, the three tests in [`skills/codex-superra-setup/scripts/test_sync_codex_agents.py`](../../skills/codex-superra-setup/scripts/test_sync_codex_agents.py), and the project-scoped up-to-date assertion in [`skills/codex-superra-setup/scripts/sync_codex_agents.py`](../../skills/codex-superra-setup/scripts/sync_codex_agents.py). The current generated agents in [`.codex/agents/superra_implementer.toml`](../../.codex/agents/superra_implementer.toml) and [`.codex/agents/superra_reviewer.toml`](../../.codex/agents/superra_reviewer.toml) matched the canonical role specs during that run. [`tests/check-harness-compatibility.sh`](../../tests/check-harness-compatibility.sh)

## Limitations

This branch changes workflow, handoff, and verification instructions only. It does not produce an empirical dataset, analysis table, or figure output.

The workflow scaffold is archived alongside this permanent results record as [`2026-04-22-phase-b-upstream-intent-contract-plan.md`](./2026-04-22-phase-b-upstream-intent-contract-plan.md). This document is the permanent results record for the branch's outcome; the companion plan preserves the prescriptive handoff state that produced it.

## Reproducibility

Reproduce the permanent-record state documented here from commit `bdd8cf99e0d73ca6fa84ddeb250f3d1b3ea05014` with `bash tests/test-phase-b-upstream-intent-contract.sh && bash tests/check-harness-compatibility.sh`.
