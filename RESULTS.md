# Tighten Phase B Upstream-Intent and Minimum-Net-Diff Contract — Results

> Mirrors `PLAN.md` structure. Updated after each task with key findings.
> New agents: read `PLAN.md` for what to do, `RESULTS.md` for what was found.

**Last updated:** 2026-04-22 (Task 4, verification)
**Status:** Completed (execution complete for the simplified-contract round; integration milestones remain pending)

---

## Task 1: Simplify role and handoff ownership for `## Upstream Intent`

**Status:** Completed (Task 1 approved 2026-04-22)

### Key Findings
- The existing `agents/implementer.md` simplification already matched the desired local rule and needed no further rewrite this round: read the task block, read the relevant `PLAN.md` header context, and do not edit the header.
- `agents/reviewer.md` now says the reviewer owns the active `## Upstream Intent` section during Phase B, with the orchestrator passing the round context in the dispatch and removing the section at closeout.
- `skills/handoff-doc/references/plan-anatomy.md` now mirrors the same simplified contract and drops the anchor-vs-cluster ownership split.

### Notes
- The handoff and reviewer surfaces now carry the ownership detail directly, so the implementer file can stay terse without losing clarity.

## Task 2: Simplify Phase B workflow around reviewer-owned prompt-fed context

**Status:** Completed (Task 2 approved 2026-04-22)

### Key Findings
- `skills/integration-workflow/SKILL.md` now makes Step 0 compute `MERGE_BASE_SHA` and pass the round context through the reviewer dispatch instead of pre-editing `PLAN.md`.
- Step 1 now tells the reviewer to create or update `## Upstream Intent` only when the base-side scan finds material overlap, and to leave the section absent otherwise.
- The first Phase B reviewer dispatch now explicitly loads `superRA:handoff-doc` `references/plan-anatomy.md` §Upstream Intent and tells the reviewer to use that reference for the section's format and placement.
- Step 3c still uses one reviewer pass for narrow fix verification plus branch-wide pruning, and Step 4 now deletes `## Upstream Intent` at Phase B closeout before Phase C.

### Notes
- The explicit `B->B` / `D->B` lifecycle narration is gone from the runtime workflow surface; the normal Phase B loop now carries the behavior.

## Task 3: Keep merge references generic and lightweight

**Status:** Completed (Task 3 approved 2026-04-22)

### Key Findings
- `skills/refactor-and-integrate/references/merge-quality.md` now treats the active reviewer-recorded `## Upstream Intent` section as the Phase B source when present, and otherwise relies on caller-supplied context without explaining extra no-overlap subcases.
- `skills/semantic-merge/SKILL.md` now carries the same lightweight contract and fixes the earlier wording bug in its Phase B / caller-supplied source selection.
- The base-owned-by-default and no-silent-restoration rules stayed intact across both utility surfaces.

### Notes
- This round simplified the instruction surface, not the merge semantics.

## Task 4: Refresh structural guards and verification for the simplified contract

**Status:** Completed (Task 4 approved 2026-04-22)

### Key Findings
- `tests/test-phase-b-upstream-intent-contract.sh` now checks 40 focused assertions covering reviewer-owned active `## Upstream Intent`, prompt-passed base context, explicit loading of the `plan-anatomy` upstream-intent reference, one-reviewer Step 3c wording, Phase B closeout deletion, concise standalone caller-supplied upstream intent, and absence of explicit re-entry / split-ownership prose.
- `bash tests/test-phase-b-upstream-intent-contract.sh` passed with 40 assertions and 0 failures.
- `bash tests/check-harness-compatibility.sh` passed after regenerating the project-scoped Codex reviewer agent and re-checking the shared skill surface.

### Notes
- `tests/check-harness-compatibility.sh` itself did not need edits.
- `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project` rewrote `.codex/agents/superra_reviewer.toml`, and the final harness check confirmed both generated agent files were up to date afterward.
- A final in-session review sweep over the touched runtime surfaces found no remaining blocking drift after the test updates, and the remaining reviewer-load-path ambiguity is now closed in the Phase B dispatch itself.
