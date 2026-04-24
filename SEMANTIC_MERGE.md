# Semantic Merge Record

**Operation:** `merge`
**Current branch:** `tighten-integration-rules`
**Incoming ref:** `origin/main`
**Governing baseline:** `30d6c911c9a2fb62582ad948fd4de82b0b2bf150`
**Merge commit:** `4e3b9e57f42c35446092f84a48c2768acdfa221b`
**Propagation commits:** Record-only commit adding this file.

## Current Branch Intent

Generalize superRA Sync and semantic-merge behavior: owner-located mode references, standalone semantic-merge records, result-protection split-out, refactor-and-integrate scope boundaries, direct-mode and Codex generated-agent updates, and release metadata for `0.1.2`.

## Incoming Intent

Bring in two `main` updates:

- Header-field handling in `planning-workflow` during plan-change protocol.
- Parallel worktree branch naming changed from `<branch>/parallel/<slug>` to `<current-branch>-agent/parallel/<slug>` across role specs, orchestration docs, `merge-guard`, and Codex agent generation.

Incoming `main` also carried root `PLAN.md` and `RESULTS.md` from the branch-naming work.

## Resolution Thesis

The merge kept the current branch's semantic-merge and integration-workflow restructuring, applied the incoming parallel-branch naming convention to the surviving rewritten surfaces, and omitted root `PLAN.md` / `RESULTS.md` per user instruction. Generated Codex agent files remained consistent with their sources.

## File / Script Impact Map

| Path or path cluster | Incoming intent | Resolution | Codebase context |
|---|---|---|---|
| `agents/implementer.md`, `.codex/agents/superra_implementer.toml` | Report `<current-branch>-agent/parallel/<slug>` from parallel worktree dispatch. | Kept current branch's leaner handoff wording and applied the new branch pattern. | `.codex/agents` was checked with `sync_codex_agents.py --scope project --check`. |
| `skills/agent-orchestration/**`, `hooks/merge-guard` | Use and exempt the new `-agent/parallel` branch naming convention. | Applied incoming branch pattern to the current branch's dispatch-template wording and worktree fallback examples. | No broader codebase-coherence work needed. |
| `skills/codex-superra-setup/scripts/sync_codex_agents.py` | Generate implementer handoff text with the new branch pattern. | Applied the incoming pattern while preserving current branch cleanup behavior. | Generator tests passed. |
| `skills/semantic-merge/SKILL.md` | Update parallel-worktree exception for the new branch pattern. | Kept the current branch's mode-reference structure and updated the bottom exception to `<current-branch>-agent/parallel/<slug>`. | Conflict resolved by synthesis. |
| `PLAN.md`, `RESULTS.md` | Incoming root handoff docs from branch-naming work. | Removed from the merge result by user decision. | Root handoff docs are absent after sync. |

## User Decisions

- 2026-04-24: User instructed to delete root `PLAN.md` and `RESULTS.md` from `main`; they are not needed. Implemented by omitting both files from the merge result and recording the decision in the merge commit body.

## Checks

- `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check` - passed.
- `python3 skills/codex-superra-setup/scripts/test_sync_codex_agents.py` - passed.
- `bash tests/check-harness-compatibility.sh` - passed.
- `bash tests/test-sync-integration-contract.sh` - passed.
- `bash tests/hooks/test-ensure-agent-orchestration.sh` - passed.
- `bash tests/hooks/test-ensure-using-superra.sh` - passed.
- Conflict-marker sweep over touched surfaces - passed.

## Codebase Context

No broader refactor-and-integrate work was identified for this sync. The only semantic follow-through was applying the new branch naming convention consistently and preserving the current branch's rewritten semantic-merge structure.
