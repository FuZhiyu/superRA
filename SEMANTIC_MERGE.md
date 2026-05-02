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

---

# Semantic Merge Record — 2026-05-02

**Operation:** `merge`
**Current branch:** `domain/writing-skills`
**Incoming ref:** `main`
**Governing baseline:** `addc9ca7fe1bdbedb080d92095facb649074c1e4` (merge base)
**Merge commit:** *(this commit)*
**Propagation commits:** None — every resolution lands in the merge commit itself, with stale-reference fixes inside `skills/writing/` bundled in.

## Current Branch Intent

Ship `skills/writing/` as a new superRA domain vertical parallel to `econ-data-analysis` — Iron Law (respect the author's intent), three concurrent disciplines (Preserve / Improve / Verify), four standalone usage modes (direct-edit / pure-review / review-edit-loop / full-workflow), eight per-dimension consistency reference files dispatched to parallel reviewers, plus routing rows in the inventory/manifest/categories surfaces. See `PLAN.md` and `RESULTS.md` for full details.

## Incoming Intent

Major restructuring of superRA workflow scaffolding while the writing branch was idle:

- `execution-workflow` renamed to `implementation-workflow` (commit `828ac00`).
- `integration-workflow` rewritten around five phases: **Protect, Sync, Integrate, Document, Finish** (replacing the older Phase A–D shape).
- `refactor-and-integrate` narrowed to codebase-coherence; drift-test content moved to a new dedicated skill `result-protection/` (with `references/drift-test-quality.md`); the references `codebase-integration.md`, `drift-test-quality.md`, `merge-quality.md` deleted.
- `semantic-merge` gained three mode references — `standalone-merge.md`, `workflow-sync-author.md`, `workflow-sync-reviewer.md` — with the SKILL.md as the shared scaffold.
- `using-superRA` lost the `## Universal Principles` block (commits `564021b` simplified, `72c38e3` cut and redistributed). Added `references/direct-mode-implementer.md`, `references/direct-mode-reviewer.md`, `references/codex-instructions.md` (replacing `codex-tools.md`).
- `CLAUDE.md` substantially rewritten around adaptive-composable-workflow design principles, ownership-boundary table, and "teach the protocol, don't prescribe each action" gate.
- Codex named-agent generation, marketplace metadata, and harness compatibility tests advanced.

## Resolution Thesis

Take main verbatim on every shared infrastructure surface (the writing branch had no design intent for any of those files). Re-thread writing-vertical additions onto the surfaces main reshaped, in the spots where main's restructure left explicit hooks for new verticals. Drop the renamed/deleted artifacts from the branch. Refresh stale references inside `skills/writing/` so they point at main's current structure rather than the pre-restructure structure they were authored against.

This is the strict minimum-net-diff path the user requested in PLAN.md §Decisions (2026-04-22 and 2026-05-02): main owns shared content; branch owns only writing-vertical additive surface.

## File / Script Impact Map

| Path or path cluster | Incoming intent | Resolution | Codebase context |
|---|---|---|---|
| `CLAUDE.md` | Rewritten contributor guide; `## Internal Design Philosophy` already states "Domain and utility skills stand alone." | Took main verbatim. The original Task 7 standalone-usability amendment is subsumed by main's text — no re-thread needed. | Sole writing concern (standalone-usability) is already covered in main. |
| `README.md` | New skill inventory and Codex install instructions. | Took main verbatim, added a `writing` row to the Domain Skills table, updated the two roadmap mentions to list writing as implemented. | Domain table updated; future verticals list shrunk by one. |
| `skills/CATEGORIES.md` | Domain section restructured; `result-protection` added as a Utility skill. | Took main verbatim, added a `writing` row to the Domain table, removed writing from the future-verticals list. | — |
| `skills/using-superRA/SKILL.md` | `## Universal Principles` removed; Skill-Load Manifest reshaped with Generic + Domain add-on tables. | Took main verbatim; added a `Domain | writing` row to §Skill Inventory and a writing row to the Domain add-on table. | Removed writing from the example "introducing a vertical" parenthetical. |
| `skills/planning-workflow/SKILL.md` | Phase 1 vertical table is now the routing surface for new domains. | Took main verbatim; added a `Writing` row pointing at `superRA:writing` + `references/planning.md`, with a note that most writing tasks (modes a/b/c) skip this workflow entirely. | — |
| `skills/integration-workflow/SKILL.md` | Phases renamed to Protect/Sync/Integrate/Document/Finish; drift tests are the current/default protection mechanism. | Took main verbatim; added one sentence to §Protect noting the writing-vertical substitutes build + outline-stability for drift tests, and one bullet to §When to Lighten describing how writing modes a/b/c skip this workflow. | The writing additions are anchored on main's `current/default protection mechanism` language and §When to Lighten extension point. |
| `skills/execution-workflow/` | Renamed to `implementation-workflow/` on main. | Removed the directory; took main's `implementation-workflow/SKILL.md` verbatim. | — |
| `skills/refactor-and-integrate/references/{codebase-integration,drift-test-quality,merge-quality}.md` | Deleted on main; drift-test content moved to `result-protection/references/drift-test-quality.md`. | Accepted deletions. Updated `skills/writing/references/integration.md` to point at `superRA:refactor-and-integrate` (skill-level) instead of the deleted reference file. | — |
| `skills/result-protection/`, `skills/semantic-merge/references/*`, `skills/using-superRA/references/{direct-mode-*,codex-instructions}.md` | New on main. | Accepted as-is. | — |
| `skills/using-superRA/references/codex-tools.md` | Deleted on main (superseded by `codex-instructions.md`). | Accepted deletion. | — |
| `skills/{agent-orchestration,econ-data-analysis,handoff-doc,refactor-and-integrate,report-in-markdown,semantic-merge,worktree-data-sync}/...` | Substantial restructuring on main. | Took main verbatim — branch had no writing-vertical content in any of these. | — |
| `agents/{implementer,reviewer}.md`, `.codex/agents/superra_*.toml`, `.codex/INSTALL.md`, `.codex-plugin/plugin.json` | Codex named-agent updates and dispatch-prompt refinements on main. | Took main verbatim. Branch had no writing-specific content here. | — |
| `hooks/merge-guard`, `tests/check-harness-compatibility.sh`, `tests/test-sync-integration-contract.sh` | Hook and test updates on main. | Took main verbatim. | — |
| `skills/writing/references/{workflow,integration,planning,collaboration}.md`, `skills/writing/SKILL.md` | Stale references to pre-restructure names. | Refreshed: `execution-workflow` → `implementation-workflow`; `merge-workflow` → folded into `integration-workflow` Finish; `§Universal Principles #N` references rephrased generically (the principle still holds, but the named anchor no longer exists on main); deleted-file pointer in `integration.md` redirected to `superRA:refactor-and-integrate`. | All stale references inside the writing skill resolved within this merge commit. |
| `PLAN.md`, `RESULTS.md` | Branch-only handoff docs. | Updated with a new §Decisions entry (2026-05-02) and a new RESULTS bullet describing the re-sync. | — |

## User Decisions

- **2026-04-22 (carried forward):** "Refresh `domain/writing-skills` against `main`; prioritize the minimum-net-diff path. A semantic merge is acceptable, and rebase/reapply is also authorized if it proves cleaner during conflict resolution." Settled on semantic merge.
- **2026-04-22 (carried forward):** "Undo the prior 2026-04-22 sync because it carried forward `## Universal Principles` even though main intentionally removed it." This sync respects that decision: `using-superRA/SKILL.md` is taken from main verbatim with no re-introduction of the deleted block.
- **2026-05-02:** "Sync this branch with the main." Implemented as the strict take-main-verbatim resync described above.

## Checks

- Conflict-marker sweep across all originally conflicting files — clean.
- Stale-reference sweep inside `skills/writing/` for `execution-workflow`, `merge-quality`, `merge-workflow`, `§Universal Principles`, `references/codex-tools`, deleted refactor-and-integrate references — all refreshed.
- `git status` — no remaining `UU` / `UD` / `DU` / `AA` entries before the merge commit.
- Independent reviewer dispatch is scheduled by the orchestrator after this commit per integration-workflow Sync discipline.

## Codebase Context

The next caller — whoever opens a PR for this branch — should still walk `superRA:refactor-and-integrate` to look for codebase-coherence work the merge could not address (writing-skill files inevitably accumulated branch-local conventions while main was advancing its own; codebase-coherence is out of scope for semantic-merge per `semantic-merge/SKILL.md §Semantic Coherence Checklist §Scope boundary`). Specific suspects to inspect during Integrate: writing's reference-file naming alongside `econ-data-analysis/references/*` (consistent suffix conventions?), and whether any writing-stage pitfalls subsection now duplicates `result-protection` content.

---

# Semantic Merge Record — 2026-05-02 (correction commit)

**Operation:** correction follow-up to the 2026-05-02 entry above
**Current branch:** `domain/writing-skills`
**Triggering review:** the sync reviewer dispatched after `fde4751` returned `REVISE`. The merge had applied "take main verbatim on shared infrastructure" only to files that had three-way merge conflicts; files where the branch had pre-merge drift from main (no conflict, but content already diverged) were silently kept at the branch state.

## Scope of the Correction

The sync reviewer enumerated the divergent surface. After filtering for the legitimate writing-vertical allowlist — `skills/writing/**`, `docs/writing-references/**`, `PLAN.md`, `RESULTS.md`, `SEMANTIC_MERGE.md`, and the five surgically-rethreaded routing surfaces (`README.md`, `skills/CATEGORIES.md`, `skills/using-superRA/SKILL.md`, `skills/planning-workflow/SKILL.md`, `skills/integration-workflow/SKILL.md`) — 50 paths still needed resolution. For each:

- if main has the file: `git checkout main -- <path>` (= take main verbatim)
- if main does not have the file: `git rm <path>` (= accept main's "this should not exist" state)

This brings the post-merge tree to a clean minimum-net-diff state: every difference between `domain/writing-skills` and `main` is now a writing-vertical artifact, a routing-rethread row, or a branch handoff doc.

## File / Script Impact Map (correction)

| Path or path cluster | Resolution | Reason |
|---|---|---|
| `.agents/skills/{agent-orchestration,codex-superra-setup,econ-data-analysis,handoff-doc,implementation-workflow,integration-workflow,planning-workflow,refactor-and-integrate,report-in-markdown,semantic-merge,using-superRA,worktree-data-sync}` | Restored from main (symlinks for harness skill discovery). | Branch had stripped these in earlier work; main's harness-compatibility surface depends on them. |
| `.agents/plugins/marketplace.json` | Restored from main. | Marketplace metadata for agents harness. |
| `.codex/INSTALL.md` | Removed from HEAD (not on main). | Stale install doc; main's Codex install flow lives in `docs/README.codex.md` + `codex-superra-setup`. |
| `.gitattributes` | Took main verbatim. | — |
| `AGENT.md` | Restored from main (symlink → `CLAUDE.md`). | Codex-facing alias for contributor guide. |
| `GEMINI.md` | Took main verbatim. | Branch had stale `using-superpowers` import; main's `using-superra` is correct. |
| `docs/README.codex.md` | Took main verbatim. | Branch had pre-rebrand "Superpowers for Codex" content; main has the current "superRA for Codex" content. |
| `docs/drafts/workflow-diagram.mmd` | Took main verbatim. | — |
| `docs/plans/2026-04-{16,17,19,21}-*.md` (14 files) | Took main verbatim where main has them. | Plan/results archive of completed initiatives. |
| `docs/process-issues-2026-04-16.md` | Took main verbatim. | — |
| `hooks/{autoload-superra,ensure-agent-orchestration,ensure-using-superra}` | Restored from main. | The three superRA-autoload hooks listed in `README.md §Hooks`; runtime would have been broken without them. |
| `hooks/{exit-plan-mode,hooks-cursor.json,hooks.json}` | Took main verbatim. | Branch had pre-autoload-hook content; main has the autoload wiring in `hooks.json`. |
| `hooks/session-start` | Removed from HEAD (not on main). | Main intentionally dropped this hook; branch retained it. |
| `skills/report-in-markdown/references/baseline-io.md` | Took main verbatim. | Branch had an extra paragraph main had since removed. |
| `skills/using-superRA/references/claude-tools.md` | Restored from main. | Branch had deleted it; main has the Claude harness adapter reference. |
| `skills/using-superRA/references/gemini-tools.md` | Took main verbatim. | Branch text still said "single-session execution via `execution-workflow`" — silent restoration of the rename main had completed. |
| `tests/hooks/{test-autoload-superra,test-e2e-cli,test-ensure-agent-orchestration,test-ensure-using-superra}.sh` | Restored from main. | Hook test harness for the three autoload hooks. |
| `tests/structural-invariants.sh` | Removed from HEAD (not on main). | Main dropped this test surface. |

## User Decisions

- 2026-05-02: User invoked the post-merge sync reviewer per integration-workflow §Sync, which surfaced the take-main-verbatim violation. User instruction: "you should also update the PLAN.md per integration instruction" implicitly authorizes the correction. No new decision was needed beyond the original "sync this branch with main" intent.

## Checks

- `git diff --name-only main..HEAD` — every surviving entry is in the legitimate allowlist (writing skill, writing-references docs, PLAN.md / RESULTS.md / SEMANTIC_MERGE.md, the five rethreaded routing surfaces).
- Conflict-marker sweep — clean.
- Stale-reference sweep inside `skills/writing/` — clean (no surviving `execution-workflow` / `merge-workflow` / `§Universal Principles` / deleted-reference pointers).

## Codebase Context

The "minimum-net-diff" intent recorded in `PLAN.md §Decisions` is now actually satisfied — only legitimate writing-vertical surface area diverges from main. Codebase-coherence work for the writing skill itself remains out of scope for semantic-merge and is deferred to `superRA:refactor-and-integrate` during integration.
