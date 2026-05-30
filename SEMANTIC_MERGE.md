# Semantic Merge Record

**Operation:** `merge`
**Current branch:** `better-handoff`
**Incoming ref:** `origin/main` (commit `3e0de35`, PR #30)
**Governing baseline:** merge-base `d861089`
**Merge commit:** _(this commit)_
**Propagation commits:** None (all propagation landed in the merge commit)

## Current Branch Intent

`better-handoff` (265 commits since the merge base) is the task-system / dashboard / status-consolidation workstream: `.plan/` directory-tree task system replacing `PLAN.md`/`RESULTS.md`, unified `status` field (status-consolidation), `handoff-doc` deprecation toward `task-system`, dashboard server + worktree selector, and the dynamic-workflows planning workstream. Its content for the workflow skills, agent specs, and references is the newest on both sides.

## Incoming Intent

A single commit (#30): a **pure mechanical rename** of the three workflow phase skills to escape a namespace collision with Claude Code's new Workflow tool / `/workflows` — `planning-workflow → superplan`, `implementation-workflow → superimplement`, `integration-workflow → superintegrate`. It renames the skill directories, frontmatter `name:` fields, and every cross-reference repo-wide, plus a `0.2.0` version bump across all plugin/package manifests and a RELEASE-NOTES entry. It carries no behavioral content that `better-handoff` lacks; in fact its skill bodies are the *old* pre-`better-handoff` content with only the names changed.

## Resolution Thesis

No genuine content fork existed, so resolution is uniform: **adopt the rename (incoming's entire intent) on top of `better-handoff`'s newer content.**

- **Every content conflict resolved to ours (`better-handoff`)** — its bodies strictly supersede incoming's old-content-renamed versions (incoming still carried `PLAN.md`/`RESULTS.md`, the old Self-Review section, and `handoff-doc` references that `better-handoff` already removed).
- **Rename re-applied repo-wide to the live tree** — including `better-handoff`'s *new* files that commit #30 never saw (`skills/task-system/SKILL.md`, `skills/superplan/references/*`, `CLAUDE.md` terminology note, etc.). This is the load-bearing stale-reference step: incoming's intent extended onto the newer base.
- **Directory rename completed by hand** where git's rename detection could not: `better-handoff`'s newly-added references (`consolidation.md`, `harness-plan-mode.md`, `thorough-planning.md`) were relocated from `skills/planning-workflow/references/` to `skills/superplan/references/`.
- **Generated artifacts regenerated** from the swept sources via `sync_codex_agents.py --scope project` (`--check` clean).
- **Version bumps + RELEASE-NOTES** (`0.2.0`) taken from incoming (auto-merged cleanly).

### Scope decision: historical records preserved

The rename sweep deliberately **excluded** `docs/plans/**`, `docs/process-issues-*`, `.plan/**`, `PLAN.md`, `RELEASE-NOTES.md`, and `README.md`'s migration banner. These are historical/archival records or the rename documentation itself; commit #30's own file scope excluded them for the same reason, and renaming them would falsify the record (e.g. `.plan/task-system/agent-interface/planning-workflow/` is a *task directory* identifier, not a skill reference). Old skill names surviving there are intentional and accurate-at-the-time.

## File / Script Impact Map

| Path or path cluster | Incoming intent | Resolution | Codebase context |
|---|---|---|---|
| `skills/{planning-workflow,implementation-workflow,integration-workflow}/` | renamed to `super*` | Dirs renamed; `SKILL.md` bodies = ours; old dirs removed | New refs relocated into `superplan/references/` |
| `skills/superplan/SKILL.md`, `superimplement/SKILL.md`, `superintegrate/SKILL.md` | rename + old body | Ours (newer body) + rename applied | — |
| `skills/{using-superRA,CATEGORIES,semantic-merge,writing,refactor-and-integrate,report-in-markdown,theory-modeling,task-system,handoff-doc}` | rename references | Ours + rename swept | `handoff-doc` is mid-deprecation on this branch |
| `agents/reviewer.md` | rename one ref | Ours + rename swept | — |
| `.codex/agents/*.toml`, `skills/using-superRA/references/direct-mode-*.md` | regenerated | Regenerated from sources (`--check` clean) | Generated — do not hand-edit |
| `.cursor-plugin/plugin.json` | version bump | **Kept `better-handoff`'s deletion** (commit `adc75d1` removed the cursor plugin); incoming's bump on a deleted file is moot | — |
| `package.json`, `.claude-plugin/*`, `.codex-plugin/plugin.json`, `gemini-extension.json` | bump to `0.2.0` | Theirs (auto-merged) | — |
| `RELEASE-NOTES.md` | add `0.2.0` entry | Theirs stacked on ours (auto-merged); old names retained as rename documentation | — |
| `hooks/*`, `tests/*` | rename references | Auto-merged + swept | — |
| `docs/**`, `.plan/**`, `PLAN.md` | (untouched by #30) | Excluded from sweep — historical records | See scope decision above |

## User Decisions

None required. The rename is the user's stated intent ("sync with origin/main"); merge-vs-rebase (merge, given 265-vs-1 divergence) and the historical-records scope decision are non-intent-changing judgment calls, documented above rather than escalated. No data contract, test expectation, or published result changed.

## Checks

- No conflict markers anywhere in the tree.
- No live old skill-name references remain (`git grep` across the tree minus the excluded historical set: clean).
- Frontmatter `name:` fields = `superplan` / `superimplement` / `superintegrate`; `.agents/skills/super*` symlinks resolve; `superplan/references/*` pointers resolve.
- `tests/check-harness-compatibility.sh` and `tests/test-sync-integration-contract.sh`: 48 pass / 6 fail — **identical to pre-merge `better-handoff` baseline** (verified by running against `git archive HEAD`). The 6 failures are pre-existing, from `better-handoff`'s in-progress `handoff-doc`/Sync-contract deprecation, not from this merge.
- `tests/hooks/test-autoload-superra.sh` (20), `test-ensure-using-superra.sh` (16), `test-ensure-agent-orchestration.sh` (16): all pass.
- `sync_codex_agents.py --scope project --check`: clean. Generator self-test (`test_sync_codex_agents.py`): 6/6 pass.

## Codebase Context

- The 6 pre-existing harness-compat failures (Plan-anatomy Sync Map / Sync-impact assertions, integration-review semantic-coherence, planning-workflow writing-route) belong to `better-handoff`'s unfinished `handoff-doc → task-system` deprecation. They are unrelated to the rename and out of this sync's scope.
- `docs/plans/**` and `.plan/**` retain old skill names by design (historical records). If a future task wants the task-tree prose updated to the new names, that is a separate, non-merge edit.

---

## Prior Merge Record (historical — internal `worktree-dashboard-redesign ← better-handoff`)

# Semantic Merge Record

**Operation:** `merge`
**Current branch:** `worktree-dashboard-redesign`
**Incoming ref:** `better-handoff`
**Governing baseline:** `c1bf384`
**Merge commit:** `5e98008`
**Propagation commits:** None (all propagation work landed in the merge commit)

## Current Branch Intent

Status consolidation: merged `review_status` + `integration_status` into a single `status` field, added `archived` status, `--cascade` flag for branch tasks, and `task_check.py` diagnostic tool. The unified status model simplifies the task lifecycle by removing the three-field status triple in favor of a single progression: `not-started -> in-progress -> implemented -> revise -> approved -> archived`.

## Incoming Intent

81 commits adding: worktree selector (discovery, server routes, selector UI, tests), planning redesign subtasks (entry-and-placement, thorough-planning, consolidation), status rollup propagation (`propagate_parent_status`, `--propagate-all`, `--fix`), revision-cleanup task, serve-shortcut and serve-docs tasks, and numerous dashboard fixes (deterministic port, math rendering, relative path resolution, section rendering, status consistency, root task rendering, comment badge walkup).

## Resolution Thesis

Both sides are valid and complementary. The status consolidation (ours) is the governing model change; the incoming features (theirs) are additive. The merge keeps all incoming features but adapts them to the unified status model:

- **Kept from ours:** Unified `status` field, `archived` status, `--cascade`, `task_check.py`, forward-compatible reading tests, stale field detection.
- **Kept from theirs:** Worktree selector, planning redesign, all dashboard fixes, `propagate_parent_status`, `--propagate-all`, `--fix`, Revision Notes handling in reviewer.md.
- **Adapted:** All incoming functions that referenced `review_status`/`integration_status` (`propagate_parent_status`, `fix_status_consistency`, `propagate_all`) rewritten to work with unified status only. Incoming tests rewritten similarly. Dashboard template badge for `review_status` removed.
- **Migrated:** 20 incoming task files had stale `review_status`/`integration_status` in frontmatter; stripped via `plan_migrate.py --upgrade-status`.

## File / Script Impact Map

| Path or path cluster | Incoming intent | Resolution | Codebase context |
|---|---|---|---|
| `.plan/` task files (10 conflicted) | better-handoff status fields | Ours wins; unified status field | Stale fields stripped from 20 additional incoming files |
| `agents/reviewer.md` | Added Revision Notes handling | Synthesized: our unified `status:` + their `## Revision Notes` removal at APPROVE | None |
| `skills/task-system/scripts/_task_io.py` | Added `propagate_parent_status`, `compute_review_status`, `validate_status_consistency` | Kept `propagate_parent_status` (simplified for unified status); removed `compute_review_status` and `validate_status_consistency`; fixed duplicate `ready` declaration from auto-merge | None |
| `skills/task-system/scripts/task_update.py` | Added `--propagate-all`, `--fix`, propagation call | Synthesized: our `--cascade` + their propagation features, all adapted for unified status | None |
| `skills/task-system/scripts/test_task_system.py` | Added tests for propagation, fix, consistency | Kept both sides' tests; rewrote incoming tests to use unified status only; dropped `TestStatusConsistency` and `TestComputeReviewStatus` (test removed functions) | None |
| `skills/task-system/scripts/task_hook.py` | Added `propagate_parent_status` call | Kept as-is; works with our adapted function | None |
| `skills/task-system/scripts/templates/task_node.html` | Had `review_status` badge | Removed stale badge; `badge-review` CSS left as dead CSS | Dead CSS in `base.html` could be cleaned in codebase-coherence pass |
| `skills/task-system/scripts/_worktree_discovery.py` (new) | Worktree discovery module | Auto-merged, no conflicts | None |
| `skills/task-system/scripts/test_worktree_selector.py` (new) | Worktree selector tests | Auto-merged, no conflicts | None |
| `skills/planning-workflow/references/` (new files) | thorough-planning.md, consolidation.md | Auto-merged, no conflicts | None |

## User Decisions

Resolution plan was approved by user before execution. Key decisions:
1. Unified status model (ours) governs all task files
2. Incoming propagation features (`propagate_parent_status`, `--propagate-all`, `--fix`) kept but adapted
3. Both sides' tests kept (incoming tests rewritten for unified model)

## Checks

- `python3 -c "import _task_io, task_update, task_check, task_hook"` -- all modules import cleanly
- Manual propagation test: `propagate_parent_status` correctly rolls up unified status to parents
- Manual rollup test: `compute_status` correctly handles archived children
- `task_check.py --plan-root .plan` -- 0 status issues, 0 rollup issues; 16 pre-existing dependency errors from relative `../` paths in better-handoff's task tree
- No conflict markers in tree
- No stale `review_status`/`integration_status` in code files (only intentional references in migration/check/test tooling)
- pytest not available in environment (no network access to install); targeted manual verification passed

## Codebase Context

- Dead CSS: `base.html` still has `.badge-review*` CSS rules that are now unused after removing the review badge from `task_node.html`. Harmless but could be cleaned.
- Pre-existing dependency errors: 16 `depends_on` entries in better-handoff's live-server task tree use `../` relative paths that `task_check.py` does not resolve. Not caused by this merge.
