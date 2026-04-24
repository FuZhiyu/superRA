# Semantic Sync Integration Redesign - Results

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-23 (Task 5 compatibility fix approved in PLAN; Task 4 role-doc pruning fix implemented and awaiting narrow re-review)
**Status:** Tasks 1-3 and 5-8 integration-approved; Task 4 integration fix implemented and awaiting re-review

---

## Task 1: Refactor semantic-merge around shared principles and mode references

**Status:** Implemented; awaiting review

`skills/semantic-merge/SKILL.md` now carries only shared semantic-sync principles and mode selection. New references split workflow sync authoring, workflow sync review, standalone full merge, Sync Map / impact formats, and shared sync-quality checks.

## Task 2: Rewrite integration-workflow Sync choreography for generic agents

**Status:** Implemented; awaiting review

`skills/integration-workflow/SKILL.md` keeps base/ref anchoring in the workflow, dispatches a generic sync author, dispatches a generic sync reviewer before Integrate, and starts Integrate only after sync review approval.

## Task 3: Define Sync Map, task-local Sync impact, and standalone file-impact anatomy

**Status:** APPROVED (Task 3 consolidated format ownership; Task 6 later relocated the format to its owning mode reference, see Task 6 section below).

`skills/semantic-merge/references/workflow-sync-author.md` owns the authoritative format templates for the branch-level `## Sync Map` and the task-local `**Sync impact:**` field (moved from `sync-map-format.md` in Task 6). `skills/handoff-doc/references/plan-anatomy.md` describes the section's purpose, ownership (including the sync-reviewer minimal-map exception), lifecycle, and placement, and points at the format reference rather than duplicating the templates. Standalone mode uses `SEMANTIC_MERGE.md` with a file / script impact map defined in `skills/semantic-merge/references/standalone-merge.md` when no PLAN.md task structure exists.

## Task 4: Simplify canonical role docs and post-sync integration consumption

**Status:** Integration pruning fix implemented; awaiting narrow re-review

Canonical implementer/reviewer docs no longer carry `Stage: sync` branch-level exceptions. `using-superRA` removes Sync from the task-scoped Skill-Load Manifest and records Sync as a generic semantic-merge dispatch. `refactor-and-integrate` now consumes task-local Sync impact and referenced Sync Map clusters without reloading full semantic-merge. Generated Codex agents and direct-mode role references were refreshed.

Integration pruning removed the broad "task-scoped stages" wording from canonical role handoff instructions. The role docs now express ownership in terms of assigned PLAN.md task blocks, and generated direct-mode / Codex role files were regenerated from the canonical sources.

## Task 5: Update public docs and verify the revised design

**Status:** Integration-approved after compatibility fix

README, CATEGORIES, CLAUDE.md, Codex adapter instructions, and generator tests now describe generic Sync dispatch, standalone semantic-merge mode behavior, sync review, and task-local Sync impact context.

The harness compatibility suite now tests the current Sync / Integrate contract directly: `tests/check-harness-compatibility.sh` invokes `tests/test-sync-integration-contract.sh`, which asserts generic sync author/reviewer dispatch, Sync Map + task-local Sync impact context, `BASE_HEAD_SHA..HEAD` as the integration baseline, retirement of Phase B / `## Upstream Intent` / `MERGE_BASE_SHA`, and line-by-line no-overprescription gates.

Verification passed on 2026-04-23:

```bash
bash tests/test-sync-integration-contract.sh
bash tests/check-harness-compatibility.sh
python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check
python3 skills/codex-superra-setup/scripts/test_sync_codex_agents.py
git diff --check
rg -n "Stage: sync|At sync stage|branch-level sync review|sync implementer|sync reviewer agent uses|Upstream Intent|merge-quality|NEEDS_USER_DECISION" skills agents README.md CLAUDE.md .codex tests -g '*.md' -g '*.toml' -g '*.py'
```

The targeted terminology scan returned only the expected negative assertions in `skills/codex-superra-setup/scripts/test_sync_codex_agents.py`.

## Task 6: Restructure semantic-merge as a tool skill at the semantic-vs-codebase coherence boundary

**Status:** APPROVED. Ran in two commit passes — Part A (owner-located formats + procedural symmetry) and Part B (tool-skill reframe at the semantic-vs-codebase coherence boundary) — consolidated per the 2026-04-23 consolidation decision.

### Part A: Owner-located formats and symmetric procedural richness

Restructured the semantic-merge skill so format specs live with their owning mode and shared procedural richness lives in the SKILL.md body. Changes file-by-file:

- `skills/semantic-merge/SKILL.md` — expanded from a lean 42-line body to a 103-line body. Retained Core principle, Choose a Mode, Workflow Boundary, Standalone Boundary, and Exception. Replaced "Shared Rules" with a six-step "Shared Procedure" section covering repo-state grounding (branch / worktree / mid-operation / merge base / incoming range / touched files), dirty-state handling via reversible named stash, intent research with role classification (behavior/API, data/schema, docs/narrative, generated outputs, tests, config/build), resolution-plan construction with synthesis and regeneration preferences, research-meaningful escalation (with `handoff-doc §User Decisions Log` pointer), resolve-and-land with commit-shape deferred to mode refs, and a stale-reference sweep at verification. RA framing preserved throughout.

- `skills/semantic-merge/references/workflow-sync-author.md` — now owns the Workflow Sync Map and Task-Local Sync Impact format blocks inlined next to the process steps that write them. Opens with a pointer to `SKILL.md §Shared Procedure` for the shared flow. Process bullets trimmed to mode-specific content: operation run, Sync Map authorship condition, task-local annotation rule, single-commit constraint, and post-sync context recording.

- `skills/semantic-merge/references/workflow-sync-reviewer.md` — dropped the `sync-map-format.md` load. Added a one-line pointer at the top to `workflow-sync-author.md §Workflow Sync Map Format` / `§Task-Local Sync Impact Format` for shape recognition. Process step 4 now references `SKILL.md §Shared Procedure` role-classification; added a verification step for the stale-reference sweep.

- `skills/semantic-merge/references/standalone-merge.md` — now owns the `SEMANTIC_MERGE.md` merge-record format (headers + File / Script Impact Map) inlined next to the step that writes it. Opens with a pointer to `SKILL.md §Shared Procedure`. Process bullets trimmed to mode-specific content: merge record authorship, decision logging without PLAN.md, operation run, one minimal merge commit, drift-test handling, deferral of broader propagation to the caller or `refactor-and-integrate` (post-Task-6 clarification — see the `Decisions` log).

- `skills/semantic-merge/references/sync-quality.md` — trimmed to the gated checklist only. Opening paragraph points at `SKILL.md §Shared Procedure` for the procedure and at the owning mode references for format specs. Added checklist items for role classification, stale-reference sweep, and stash reporting so reviewers walk what the expanded procedure teaches.

- `skills/semantic-merge/references/sync-map-format.md` — deleted via `git rm`.

- `skills/handoff-doc/references/plan-anatomy.md` — §Sync Map format pointer and §Task-local Sync impact format pointer now target `workflow-sync-author.md §Workflow Sync Map Format` / `§Task-Local Sync Impact Format`. The section still carries only purpose / ownership / lifecycle / placement + one-line format pointer, preserving DRY (no re-introduced Task 3 violation).

- `skills/integration-workflow/SKILL.md` — dropped `semantic-merge/references/sync-map-format.md` from both sync-author and sync-reviewer dispatch reference lists. No other changes.

Verification on 2026-04-23:

```bash
rg -n "sync-map-format" skills agents README.md CLAUDE.md .codex tests  # zero matches
python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check  # up to date
python3 skills/codex-superra-setup/scripts/test_sync_codex_agents.py  # 6/6 passed
git diff --check  # clean
```

### Part B: Tool-skill reframe at the semantic-vs-codebase coherence boundary

Reframed both skills as tool skills split at the semantic vs codebase coherence boundary. Semantic-merge now teaches techniques for reaching semantic coherence (1 merge commit + N propagation commits as needed within that scope); refactor-and-integrate teaches techniques for codebase coherence (convention fit, utility reuse, PR-friendly diffs, Project Doc Audit, minimum net diff). `sync-quality.md §Scope boundary` is the gated stopping rule for semantic coherence. Every commit landed by semantic-merge must still leave existing protection passing — that is the per-commit lower bound, not the whole-mode stopping rule.

File-by-file changes:

- `skills/semantic-merge/SKILL.md` — renamed `## Shared Procedure` to `## Techniques` with a new opening paragraph stating the tool-skill framing: techniques not prescribed procedure, integration-workflow sequences at macro, within a single merge operation techniques follow a natural micro-order. Technique 5 (Resolve and land) now states "Land one merge commit plus N propagation commits as needed to reach semantic coherence" with per-commit protection-pass as the lower bound and `sync-quality.md §Scope boundary` as the whole-mode stopping rule; codebase-coherence work is named explicitly and deferred to `refactor-and-integrate`. Technique 6 renamed from "Verify — stale-reference sweep" to "Detect and resolve stale references" — resolution of stale references within the merge's semantic reach is now part of semantic coherence, with broader codebase-fit work deferred. `## Workflow Boundary` and `## Standalone Boundary` rewritten around the new coherence boundary.

- `skills/semantic-merge/references/sync-quality.md` — opening paragraph updated to describe the checklist as the semantic-coherence stopping rule and point at `SKILL.md §Techniques`. `**Scope boundary:**` rewritten: the four old `[BLOCKING]` items (one-minimal-commit, protection-pass, deferred-propagation, deferred-recording) replaced with six items defining semantic coherence: stale references within the merge's reach resolved; generated outputs regenerated or escalated; docs describing merged code updated; no conflict markers; protection passes on every commit (per-commit lower bound); codebase-coherence work deferred. Intent preservation, Intent integrity, and Handoff docs sections unchanged. Verification: the stale "regeneration is deferred" bullet was rewritten in a follow-up pass to state that regeneration within semantic reach happens in the skill's commit chain; only regenerations that would change a meaningful result are escalated and recorded as follow-up obligations.

- `skills/semantic-merge/references/workflow-sync-author.md` — opening pointer flipped from `§Shared Procedure` to `§Techniques`; checklist described as encoding the semantic-coherence stopping rule. Process Step 4 now allows the merge commit plus any propagation commits needed to reach semantic coherence, with per-commit protection-pass as the lower bound and `sync-quality.md §Scope boundary` as the stopping rule. The Sync Map records integration context for later codebase review. Workflow Sync Map header broadened from singular `**Sync commit:**` to plural `**Sync commits:** <MERGE_COMMIT_SHA>[, <PROPAGATION_SHA>...]` to match the 1+N design and the standalone merge record. Incidental singular phrasings in Sync cluster template, Status Return, and Report bullet pluralized for consistency.

- `skills/semantic-merge/references/standalone-merge.md` — opening pointer flipped to `§Techniques`; intro reframed around semantic coherence and deferred codebase coherence. Process collapsed to four steps: create merge record, run operation, land merge + propagation commits to semantic coherence, record codebase-coherence obligations. `SEMANTIC_MERGE.md` record format gained a `**Propagation commits:**` header field (1 merge + N propagation SHAs). Report field updated to include propagation-commit SHAs.

- `skills/semantic-merge/references/workflow-sync-reviewer.md` — pointer flip `SKILL.md §Shared Procedure` → `SKILL.md §Techniques`. Inputs list pluralized to `Sync commits (merge commit SHA plus any propagation-commit SHAs)` to match the 1+N dispatch shape; intro + Review Scope + Process Step 4 pluralized to describe the reviewer inspecting the merge commit plus any propagation commits. Process Step 8 rewritten around the semantic-vs-codebase-coherence scope boundary: generated outputs within semantic reach must be regenerated (or escalated and recorded); codebase-coherence work — convention fit, utility reuse, PR-friendly diffs, Project Doc Audit walk-up, minimum net diff — is left for Integrate, with Sync notes kept as context. Reviewer flags scope creep across that line, not regeneration within semantic reach.

- `skills/refactor-and-integrate/SKILL.md` — opening reframed as a tool skill for codebase coherence with the one-line pair-relationship note: "Paired with `semantic-merge`: run `semantic-merge` first to reach semantic coherence; this skill picks up to reach codebase coherence." Listed as three techniques with no prescribed order: drift-test creation, codebase-fit refactoring, and Sync impact context.

- `skills/integration-workflow/SKILL.md` — Sync-author dispatch `Use semantic-merge...` body updated: agent lands merge + propagation commits to semantic coherence (with `sync-quality.md §Scope boundary` as stopping rule), defers codebase coherence to `refactor-and-integrate`, returns all commit SHAs. Sync-reviewer dispatch `Sync commit:` field broadened to `Sync commits:` (merge + propagation SHAs). References lists unchanged.

- `CLAUDE.md` — §DRY ownership entries for `semantic-merge` and `refactor-and-integrate` rewritten to describe the skills as owning *techniques for semantic coherence* and *techniques for codebase coherence* respectively.

- `README.md` — utility-skill rows for both skills updated: semantic-merge described as tools for semantic coherence with propagation commits as needed; refactor-and-integrate described as tools for codebase coherence (convention fit, utility reuse, PR-friendly diffs, Project Doc Audit walk-up, minimum net diff).

- `skills/CATEGORIES.md` — same utility-skill one-liner updates as README.

- `skills/using-superra/SKILL.md` — same utility-skill one-liner updates in the Skill Inventory table.

Verification on 2026-04-23:

```bash
rg -n "Shared Procedure" skills agents README.md CLAUDE.md .codex tests                                      # zero matches
rg -n "exactly one minimal merge commit|one minimal commit|one sync commit" skills agents README.md CLAUDE.md # zero matches
python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check                       # up to date
python3 skills/codex-superra-setup/scripts/test_sync_codex_agents.py                                          # 6/6 passed
git diff --check                                                                                              # clean
```

## Task 7: Clarify shared-vs-mode-specific content in semantic-merge

**Status:** APPROVED.

Tightened the shared-vs-mode-specific split in the semantic-merge skill. `SKILL.md` now carries only shared content (core principle, Choose a Mode, §Shared Steps, §Semantic Coherence Checklist, Exception); mode references carry §Boundary + §Inputs + §Mode-Specific Process + §Format + §Status/Report. The separate `sync-quality.md` reference is absorbed into `SKILL.md` as §Semantic Coherence Checklist — it was a must-load on every call path, and `SKILL.md` is always loaded when the skill is used, so folding it in removes a file without reducing availability. The researcher's in-flight hand-edits (§Techniques → §Shared Steps with a terse opener, 4-step `workflow-sync-author.md` process, "sync commit range" Status Return) are adopted as the baseline.

File-by-file changes:

- `skills/semantic-merge/SKILL.md` — Choose a Mode updated: the sync-quality bullet removed; the workflow / standalone boundary sentences extended so each mode reference's §Boundary ownership is explicit, and a new line records that all modes walk the §Semantic Coherence Checklist below. `## Workflow Boundary` and `## Standalone Boundary` sections removed. New `## Semantic Coherence Checklist` section added (absorbed from the former `sync-quality.md`) with preserved sub-headings (Intent preservation, Scope boundary, Intent integrity, Handoff docs, Verification) and `[BLOCKING]` / `[ADVISORY]` markers. Shared Steps step 5 stopping-rule pointer updated from `sync-quality.md §Scope boundary` → `§Semantic Coherence Checklist §Scope boundary` below.

- `skills/semantic-merge/references/workflow-sync-author.md` — new §Boundary at the top (moved and carried forward from `SKILL.md ## Workflow Boundary`). Opener dropped the "Also load `sync-quality.md`" line and flipped `Techniques` → `Shared Steps`; points at `SKILL.md §Semantic Coherence Checklist` for the checklist walk. Process Step 4 stopping-rule pointer updated to the new `SKILL.md §Semantic Coherence Checklist §Scope boundary` location. Process remains 4 steps per the researcher's in-flight edit (no codebase-obligation Step 5). Status Return retains the "sync commit range" phrasing.

- `skills/semantic-merge/references/workflow-sync-reviewer.md` — opener replaced the `sync-quality.md` load with pointers to the new `SKILL.md §Semantic Coherence Checklist` and the inherited `workflow-sync-author.md §Boundary`. Process Step 4 `§Techniques` → `§Shared Steps`; Step 5 "Walk `sync-quality.md` top to bottom." → "Walk `SKILL.md §Semantic Coherence Checklist` top to bottom."; Step 8 `§Techniques` → `§Shared Steps`.

- `skills/semantic-merge/references/standalone-merge.md` — new §Boundary at the top (moved and carried forward from `SKILL.md ## Standalone Boundary`). Opener dropped the "Also load `sync-quality.md`" line and flipped `Techniques` → `Shared Steps`. Process Step 3 stopping-rule pointer updated to the new `SKILL.md §Semantic Coherence Checklist §Scope boundary` location; `§Techniques` → `§Shared Steps` pointer.

- `skills/semantic-merge/references/sync-quality.md` — deleted via `git rm`.

- `skills/integration-workflow/SKILL.md` — sync-author dispatch references list dropped `semantic-merge/references/sync-quality.md`; dispatch body stopping-rule narration updated from `sync-quality.md §Scope boundary` → `SKILL.md §Semantic Coherence Checklist §Scope boundary`. Sync-reviewer dispatch references list dropped the same entry.

- `CLAUDE.md` — §DRY ownership entry for `semantic-merge` updated: `sync-quality.md §Scope boundary` → `SKILL.md §Semantic Coherence Checklist §Scope boundary`.

Verification on 2026-04-23:

```bash
rg -n "sync-quality" skills agents README.md CLAUDE.md .codex tests      # zero matches
rg -n "Workflow Boundary|Standalone Boundary" skills/semantic-merge/SKILL.md  # zero matches
python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check  # up to date
python3 skills/codex-superra-setup/scripts/test_sync_codex_agents.py  # 6/6 passed
git diff --check  # clean
```

## Task 8: Reframe Sync notes as post-sync context, not integration targets

**Status:** Implemented; awaiting review.

Reframed the Sync / Integrate boundary so semantic-merge resolves semantic coherence and records context, while Integrate reviews codebase coherence. Workflow Sync Map clusters, task-local `**Sync impact:**`, and standalone `SEMANTIC_MERGE.md` records now explain the approved post-sync diff; they are not unresolved semantic-sync or integration work queues.

File-by-file changes:

- `skills/semantic-merge/SKILL.md` — removed obligation language from handoff artifacts. The semantic-coherence checklist now says broader codebase-coherence work is left to refactor/integration, while handoff artifacts may explain codebase-review context.
- `skills/semantic-merge/references/workflow-sync-author.md` — Sync Map and task-local `**Sync impact:**` formats now record integration context and task-specific post-sync context.
- `skills/semantic-merge/references/workflow-sync-reviewer.md` — sync review now checks that Sync impact is accurate context and that unresolved semantic work is not pushed into Integrate.
- `skills/semantic-merge/references/standalone-merge.md` — `SEMANTIC_MERGE.md` uses File / Script Impact Map `Codebase context` and `## Codebase Context`.
- `skills/integration-workflow/SKILL.md` — Integrate reads Sync notes as context and reviews codebase coherence against `BASE_HEAD_SHA..HEAD`; it does not re-review the semantic merge layer.
- `skills/refactor-and-integrate/SKILL.md` and `skills/refactor-and-integrate/references/codebase-integration.md` — refactor/integration uses Sync impact as context for existing post-sync hunks, not as an independent work queue, and applies the minimum-net-diff gate line by line.
- `CLAUDE.md` — Teach-the-Protocol DRY / Necessity gate now explicitly applies line by line to instruction edits under `skills/*` and `agents/*`.
- `skills/handoff-doc/references/plan-anatomy.md` — PLAN anatomy now describes Sync Map / Sync impact as temporary context scaffolding.
- `README.md`, `skills/CATEGORIES.md`, `skills/using-superRA/SKILL.md`, and `CLAUDE.md` — public/contributor summaries aligned with the context-not-obligation contract.

Verification passed on 2026-04-23:

```bash
targeted stale sync-target wording scan across README.md, CLAUDE.md, skills, PLAN.md, and RESULTS.md
python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check
python3 skills/codex-superra-setup/scripts/test_sync_codex_agents.py
git diff --check
```

The terminology scan returned only the intentional historical command record in `PLAN.md`.
