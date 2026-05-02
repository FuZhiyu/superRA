# Semantic Sync Integration Redesign Plan

> **For agentic workers:** Use `superRA:handoff-doc` for PLAN.md / RESULTS.md editing. Treat skill and agent instruction edits as skill creation: load `skill-creator`, preserve RA framing and review gates, and keep instructions concise.
>
> **Branch-local skill source:** This branch redesigns superRA's workflow skills. During this integration, read the skill files directly from this repo (`skills/<name>/SKILL.md` and `skills/<name>/references/*.md`) rather than loading an installed plugin copy.
>
> **Required gate:** Main landed the "Teach the Protocol, Don't Prescribe Each Action" gate. Every surviving edit under `skills/*` or `agents/*` must pass the DRY and Necessity tests line by line. Implementers run the minimum-net-diff self-check against `BASE_HEAD_SHA..HEAD`; reviewers verify the same diff before approval.
>
> **Generated artifacts - do not hand-edit:** `skills/using-superRA/references/direct-mode-implementer.md`, `skills/using-superRA/references/direct-mode-reviewer.md`, `.codex/agents/superra_implementer.toml`, and `.codex/agents/superra_reviewer.toml` are generated from `agents/implementer.md`, `agents/reviewer.md`, and `skills/codex-superra-setup/scripts/sync_codex_agents.py`. Regenerate with `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project`, then verify with `--check` and `python3 skills/codex-superra-setup/scripts/test_sync_codex_agents.py`.

**Objective:** Redesign superRA integration so semantic sync is a standalone utility skill, workflow Sync uses generic agents plus semantic-merge mode references, and downstream task agents receive sync intent through task-local annotations.

**Methodology:** Keep one source of truth per concern: `semantic-merge` owns semantic sync and sync review discipline; `integration-workflow` owns choreography; `refactor-and-integrate` owns post-sync codebase quality and uses Sync Map / task-impact notes as context.

**Domain Vertical:** Skill design / workflow refactor. No data-analysis vertical applies.

**Data Inventory:** Not applicable.

**Conventions:** Canonical behavior lives in root `skills/`; canonical role specs live in `agents/`. Generated Codex role files and direct-mode references are refreshed only through `skills/codex-superra-setup/scripts/sync_codex_agents.py`. Avoid role-specific exceptions in canonical implementer/reviewer files when a skill-owned reference can carry the behavior.

**Output:** Updated workflow, semantic-merge mode references, handoff anatomy, role docs, generated Codex artifacts, tests, and public/contributor documentation.

**Expected Results / Hypotheses:** Workflow Sync dispatches `Stage: sync` generic sync author/reviewer agents that load semantic-merge mode references. `## Sync Map` records incoming intent, resolution thesis, and sync clusters; affected task blocks carry short `**Sync impact:**` pointers. Semantic-merge lands one merge commit plus any propagation commits needed for semantic coherence; refactor-and-integrate handles codebase coherence.

**Sensitivity Analysis:** Verify the surviving diff does not preserve legacy sync-stage, upstream-intent, one-commit, sync-obligation, or boundary-wrapper prose except in intentional tests or current blocker notes.

**Pipeline:** Not applicable. Verification commands are listed in Task 11.

---

## Workflow Status

- [x] **Plan approved** - current semantic-sync redesign captured below.
- [x] **Execution complete** - all task and integration review gates are approved.
- [x] **Drift tests created** - not applicable for this skill-design change; no drift-test-bearing outputs changed.
- [x] **Integrated** - Tasks 8-11 received trusted integration approval after the branch-wide pruning pass.
- [x] **Docs finalized** - PLAN.md and RESULTS.md archived under `docs/plans/`.
- [ ] **Finished** - final merge / publish not performed in this session.

---

## Project Conventions

Walked at planning time on 2026-04-23; refreshed in this consolidation on 2026-04-24 for current contributor guidance.

### Repo root
- `/CLAUDE.md` and `/AGENTS.md`: Contributor guidance for superRA internals. Skill, hook, agent, and internal-doc edits are behavior-shaping skill creation work. The DRY / Necessity gate is blocking for `skills/*` and `agents/*` edits.
- `/README.md`: User-facing overview of the PLAN -> IMPLEMENT -> INTEGRATE workflow, utility skills, agents, hooks, and installation. Keep public skill descriptions aligned with runtime behavior.

### Module-level docs walked
- `tests/claude-code/README.md`: Claude Code skill tests are shell-based and focus on skill loading and expected behavior. Fast tests are preferred by default; integration tests are slow and optional.

### Not walked
- No nested module guidance docs under `skills/` or `agents/` beyond the skill files and references read for this plan.

## Decisions

> **User decision (2026-04-23, current semantic-sync design):** Redesign Sync around generic sync author/reviewer agents plus semantic-merge mode references. Keep branch-level Sync Map context, task-local or standalone file-local impact annotations, mode-owned formats, and shared semantic-coherence guidance in `semantic-merge`.
> **Question asked:** How should semantic sync agents, reviewers, and Sync Map / task-impact responsibilities be structured?
> **Rationale (if given):** Avoid branch-level sync-stage exceptions in canonical roles; keep semantic-merge standalone; keep integration reviewers from loading full semantic-merge; preserve task-scoped sync context.

> **User decision (2026-04-23, semantic-vs-codebase boundary):** Split `semantic-merge` and `refactor-and-integrate` at the semantic coherence vs codebase coherence boundary. Semantic-merge carries through to semantic coherence with one merge commit plus propagation commits as needed; refactor-and-integrate handles convention fit, utility reuse, Project Doc Audit, PR-friendly diff, and minimum net diff.
> **Question asked:** Should semantic-merge finish semantic propagation itself, or defer propagation to refactor-and-integrate?
> **Rationale (if given):** The boundary is semantic meaning vs host-project fit. Each skill carries the techniques its scope requires without forcing cross-skill dispatch for small semantic fixes.

> **User decision (2026-04-23, mode split):** `semantic-merge/SKILL.md` teaches shared principles only: core intent rule, mode selection, Shared Steps, Semantic Coherence Checklist, and the parallel-worktree exception. Mode references carry boundary, inputs, mode-specific process, format, and status/report instructions.
> **Question asked:** Where should workflow/standalone boundaries and the semantic-coherence checklist live?
> **Rationale (if given):** Boundary sections are mode scope statements. The checklist is loaded on every semantic-merge path, so it belongs in `SKILL.md`.

> **User decision (2026-04-23, integration source and Sync context):** Integrate against `origin/main` at `30d6c91` with `PRE_SYNC_BASE_SHA=b6e0640` and `BASE_HEAD_SHA=30d6c91`. During this integration, agents read in-repo skill files directly. Workflow-mode Sync Maps record incoming intent and resolution thesis, not current-branch intent already carried by PLAN.md / RESULTS.md. Sync Map clusters, task-local `**Sync impact:**`, and standalone `SEMANTIC_MERGE.md` records are context for Integrate, not unresolved work queues.
> **Question asked:** Which base and skill source should this branch integrate against, and how should Sync notes be consumed afterward?
> **Rationale (if given):** The installed plugin copy is stale relative to this branch. Sync review approves semantic coherence; Integrate reviews codebase coherence against `BASE_HEAD_SHA..HEAD`.

> **User decision (2026-04-23, integration gate failure):** Do not proceed from the latest Integrate approval. Replan and re-audit the surviving diff before closeout.
> **Question asked:** Should we keep patching current wording or document the issue and replan?
> **Rationale (if given):** The reviewer self-audit did not inspect every hunk line by line. A direct violation remains in `skills/refactor-and-integrate/SKILL.md`: boundary-wrapper prose explains ownership already carried by authoritative workflow and skill surfaces.

> **User decision (2026-04-24, PLAN consolidation):** Keep PLAN.md as current operational state, not a changelog. Preserve current design decisions, Sync anchors, task statuses, active review blocker, and generated-artifact warning; let git history and RESULTS.md carry detailed implementation history.
> **Question asked:** How should PLAN.md be consolidated without losing important information?
> **Rationale (if given):** The plan had overlapping task outputs and stale rationale that obscured the active blocker and the required guideline.

> **User decision (2026-04-24, result protection split and minimum-net-diff refactor):** Split result protection out of `refactor-and-integrate` into its own general utility: Protect should mean protecting key results, with drift tests as the current/default mechanism. Rebuild `refactor-and-integrate` around codebase coherence and minimum net diff. Integration implementers must leave a compact final diff self-check trail even when they make no code change; suspicious hunks may carry explicit justification, and the orchestrator removes temporary trails with the Sync Map at Integrate closeout. The repo-specific DRY / Necessity gate remains mandatory for `skills/*` and `agents/*`; the general minimum-net-diff discipline should be framed as avoiding unjustified scope, defensive edits, and overengineering rather than exporting this repo's "no overprescription" label everywhere.
> **Question asked:** How should the failed Task 8 integration review be repaired structurally?
> **Rationale (if given):** A reviewer can verify an implementer trail, but reviewing reviewers creates another prose surface. The durable mechanism is an implementer self-check that the reviewer can compare against the actual governing diff.

> **User decision (2026-04-24, release prep):** Archive `PLAN.md` and `RESULTS.md` under `docs/plans/`, bump all plugin/package manifests to `0.1.2`, and prepare release notes for merge/release without performing the final merge or publish action.
> **Question asked:** What release version and final document disposition should be used?
> **Rationale (if given):** Keep the closeout narrow: archive the handoff record, update release metadata, and leave the branch ready for release.

## Sync Map

**Base branch:** `origin/main`
**Pre-sync merge base:** `b6e0640efce48e9dbf2ca9cec9ac1e310aaf82b3`
**Synced base head:** `30d6c911c9a2fb62582ad948fd4de82b0b2bf150`
**Incoming range:** `b6e0640..30d6c91`
**Sync commits:** `865339c` (merge commit), `e7acf40` (Sync Map SHA propagation), `ff082f4` (generator follow-through)
**Sync review status:** APPROVED

### Branch Summary

**Incoming intent:** Main landed `improve-design-principle`, which redesigned the Workflow Frontier Resolver around a reusable re-entry mechanism and made "Teach the Protocol, Don't Prescribe Each Action" a gated contributor rule.

**Resolution thesis:** Adopt main's lean contributor contract and DRY / Necessity gate while preserving this branch's redesigned integration vocabulary: Protect / Sync / Integrate / Document / Finish, semantic coherence as the Sync stopping rule, and Sync Map + task-local Sync impact as temporary Sync/Integrate context.

### Sync Clusters

> **Sync cluster `S1-teach-the-protocol-clean-rewrite` (2026-04-23):** path `CLAUDE.md`; affects branch-level contributor contract. **Incoming intent:** Lean contributor guide with Ownership Boundaries and the DRY / Necessity gate. **Sync resolution:** Adopted main's rewrite and extended ownership rows for the semantic-merge / refactor-and-integrate boundary. **Integration context:** Review `30d6c91..HEAD` line by line for overprescription.

> **Sync cluster `S2-role-spec-trim-overlap` (2026-04-23):** paths `agents/implementer.md`, `agents/reviewer.md`, generated direct-mode refs, generated Codex TOMLs, and `skills/codex-superra-setup/scripts/sync_codex_agents.py`; affects branch-level role contract. **Incoming intent:** Trim role-wrapper instructions and regenerate derived artifacts. **Sync resolution:** Kept the trim, adjusted the generator cleanup hook for this branch's Sync Map / Sync impact design, and regenerated artifacts. **Integration context:** Canonical role edits must keep only behavior-shaping instructions; regenerate artifacts if canonical roles change.

> **Sync cluster `S3-workflow-vocabulary-overlap` (2026-04-23):** paths across workflow, handoff-doc, report, econ-data, refactor-and-integrate, and semantic-merge skills; affects Tasks 1, 2, and 7. **Incoming intent:** Main trimmed workflow and utility/domain instructions around the new Workflow Frontier Resolver. **Sync resolution:** Kept main's trims where they removed wrapper prose, preserved this branch's Sync / Integrate vocabulary where it is the feature under design, and aligned plan anatomy with task-local Sync impact. **Integration context:** Integrate uses Sync notes as context and reviews the surviving diff against `BASE_HEAD_SHA..HEAD`.

**Advancing base note:** `origin/main` advanced to `61588d9` after this Sync round. Re-enter Sync before Finish if the recorded `BASE_HEAD_SHA` differs from the current base.

---

### Task 1: Refactor semantic-merge around shared principles and mode references
**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:** APPROVED
**Sync impact:** Cluster `S3-workflow-vocabulary-overlap` explains why the surviving semantic-merge diff is lean after main's teach-the-protocol trim. Source: `PLAN.md ## Sync Map`.

**Files:** `skills/semantic-merge/SKILL.md`, `skills/semantic-merge/references/workflow-sync-author.md`, `skills/semantic-merge/references/workflow-sync-reviewer.md`, `skills/semantic-merge/references/standalone-merge.md`.
**Output:** Semantic-merge now has a lean shared body plus mode references for workflow sync authoring, workflow sync review, and standalone merge use.

---

### Task 2: Rewrite integration-workflow Sync choreography for generic agents
**Depends on:** Task 1
**Review status:** APPROVED
**Integration status:** APPROVED
**Sync impact:** Cluster `S3-workflow-vocabulary-overlap` explains why the Protect / Sync / Integrate / Document / Finish structure survives. Source: `PLAN.md ## Sync Map`.

**Files:** `skills/integration-workflow/SKILL.md`.
**Output:** Integration workflow computes base anchors, dispatches generic sync author/reviewer agents with semantic-merge mode references, and gates Integrate on sync review approval.

---

### Task 3: Define Sync Map, task-local Sync impact, and standalone file-impact anatomy
**Depends on:** Task 1, Task 2
**Review status:** APPROVED
**Integration status:** APPROVED

**Files:** `skills/handoff-doc/references/plan-anatomy.md`, `skills/semantic-merge/references/workflow-sync-author.md`, `skills/semantic-merge/references/standalone-merge.md`.
**Output:** Workflow Sync Map and task-local Sync impact formats live with workflow sync author mode; standalone merge record format lives with standalone mode. PLAN anatomy owns purpose, lifecycle, placement, and the temporary-removal rule.

---

### Task 4: Simplify canonical role docs and post-sync integration consumption
**Depends on:** Task 1, Task 2, Task 3
**Review status:** APPROVED
**Integration status:** APPROVED

**Files:** `agents/implementer.md`, `agents/reviewer.md`, `skills/using-superRA/SKILL.md`, generated direct-mode refs, generated Codex TOMLs.
**Output:** Canonical role contracts stay task-oriented; Sync-specific behavior lives in semantic-merge references. Generated role artifacts were refreshed from canonical sources.

---

### Task 5: Update public docs and verify the revised design
**Depends on:** Task 1, Task 2, Task 3, Task 4
**Review status:** APPROVED
**Integration status:** APPROVED

**Files:** `README.md`, `skills/CATEGORIES.md`, `CLAUDE.md`, `tests/test-sync-integration-contract.sh`, `tests/check-harness-compatibility.sh`.
**Output:** Public/contributor docs and harness checks describe generic Sync dispatch, standalone semantic-merge behavior, sync review, task-local Sync impact context, and retirement of legacy phase-B upstream-intent / merge-quality assumptions.

**Verification:** `bash tests/test-sync-integration-contract.sh`, `bash tests/check-harness-compatibility.sh`, Codex generator `--check`, generator tests, `git diff --check`, and the legacy-sync-term scan passed for the Task 5 design.

---

### Task 6: Restructure semantic-merge as a tool skill at the semantic-vs-codebase coherence boundary
**Depends on:** Task 1, Task 2, Task 3, Task 4, Task 5
**Review status:** APPROVED
**Integration status:** APPROVED

**Files:** `skills/semantic-merge/SKILL.md`, semantic-merge mode references, `skills/refactor-and-integrate/SKILL.md`, `skills/integration-workflow/SKILL.md`, `skills/handoff-doc/references/plan-anatomy.md`, `skills/using-superRA/SKILL.md`, `CLAUDE.md`, `README.md`, `skills/CATEGORIES.md`.
**Output:** Semantic-merge owns techniques for semantic coherence and commit chains; refactor-and-integrate owns techniques for codebase coherence and minimum net diff. Format specs live in their owning mode references.

**Verification:** Targeted legacy-term scans returned no live design matches. Codex generator checks and `git diff --check` passed.

---

### Task 7: Clarify shared-vs-mode-specific content in semantic-merge
**Depends on:** Task 6
**Review status:** APPROVED
**Integration status:** APPROVED
**Sync impact:** Cluster `S3-workflow-vocabulary-overlap` explains why `semantic-merge/SKILL.md §Choose a Mode`, §Exception, and the Semantic Coherence Checklist carry the surviving shared guidance. Source: `PLAN.md ## Sync Map`.

**Files:** `skills/semantic-merge/SKILL.md`, `skills/semantic-merge/references/workflow-sync-author.md`, `skills/semantic-merge/references/workflow-sync-reviewer.md`, `skills/semantic-merge/references/standalone-merge.md`, `skills/integration-workflow/SKILL.md`, `CLAUDE.md`.
**Output:** `semantic-merge/SKILL.md` carries shared content only. Mode references carry boundary, inputs, mode-specific process, format, and status/report. The Semantic Coherence Checklist lives in `SKILL.md`.

**Verification:** Targeted legacy-term scans returned zero live matches. Codex generator checks and `git diff --check` passed.

---

### Task 8: Reframe Sync notes as post-sync context, not integration targets
**Depends on:** Task 7
**Review status:** APPROVED
**Integration status:** APPROVED

**Files:** `skills/semantic-merge/SKILL.md`, semantic-merge mode references, `skills/integration-workflow/SKILL.md`, `skills/refactor-and-integrate/SKILL.md`, `skills/handoff-doc/references/plan-anatomy.md`, `skills/using-superRA/SKILL.md`, `skills/CATEGORIES.md`, `README.md`, `CLAUDE.md`, `RESULTS.md`.
**Output:** Sync Map clusters, task-local `**Sync impact:**`, and standalone `SEMANTIC_MERGE.md` records explain the approved post-sync diff. Integrate / refactor-and-integrate use those notes as context while reviewing codebase coherence against `BASE_HEAD_SHA..HEAD`.

---

### Task 9: Split result protection out of refactor-and-integrate
**Depends on:** Task 8
**Review status:** APPROVED
**Integration status:** APPROVED

**Files:** `skills/result-protection/SKILL.md`, `skills/result-protection/references/*`, `skills/using-superRA/SKILL.md`, `skills/integration-workflow/SKILL.md`, `skills/econ-data-analysis/SKILL.md`, `skills/econ-data-analysis/references/integrate-drift-tests.md`, tests that route Protect / drift-test behavior.
**Input:** User decision above; existing `skills/refactor-and-integrate/references/drift-test-quality.md`; `skills/econ-data-analysis`'s stage-scoped-reference style.
**Output:** Result protection is a standalone utility skill. Integration Protect dispatches this skill for key-result protection; drift tests are documented as the current/default protection mechanism, not the whole concept. `refactor-and-integrate` no longer owns drift-test quality.

- [x] **Step 1: Create the result-protection skill**
  Created `skills/result-protection/` with a lean skill body and a drift-test quality reference carrying red-green, tolerance, independence, and expectation-update gates. The legacy `refactor-and-integrate` copy remains untouched in this worktree because Task 10 owns that cleanup.

- [x] **Step 2: Route Protect to result protection**
  Routed `Stage: protection` to `result-protection` and `Stage: sync` to `semantic-merge` in `using-superRA`, updated Protect choreography to key-result protection vocabulary, and kept drift-test wording for the concrete default mechanism and suite runs.

- [x] **Step 3: Preserve domain add-ons**
  Kept data-analysis key-result selection, tolerance, and failure-mode guidance in `econ-data-analysis`; only the generic drift-test quality pointer moved to `result-protection`.

- [x] **Step 4: Update targeted tests**
  Added contract checks for the Protect route, result-protection drift-test quality reference, and econ add-on pointer.

---

### Task 10: Rebuild refactor-and-integrate around minimum net diff
**Depends on:** Task 8
**Review status:** APPROVED
**Integration status:** APPROVED

**Files:** `skills/refactor-and-integrate/SKILL.md`, `skills/refactor-and-integrate/references/drift-test-quality.md` if removed, tests that inspect refactor-and-integrate wording.
**Input:** Task 8 review note; user decision above; `CLAUDE.md` DRY / Necessity gate for this repo's instruction-bearing files.
**Output:** `refactor-and-integrate` is a codebase-coherence utility centered on minimum net diff. It requires implementer final diff self-check evidence, treats absent pruning as suspicious rather than exempt, and keeps Sync impact as a justification context only when already provided by the workflow.

- [x] **Step 1: Narrow the skill owner**
  Remove drift-test ownership and semantic-boundary wrapper prose. Keep only codebase coherence, convention fit, project-doc audit, utility reuse, and minimum-net-diff discipline.

- [x] **Step 2: Make the governing-diff procedure load-bearing**
  Require implementers to recompute the governing diff before returning, including no-change cases, and leave a compact self-check trail for reviewer verification.

- [x] **Step 3: Define proportionate justification**
  Require summarized surviving-change classes by default. Require explicit hunk/line justification for suspicious cases: `skills/*` or `agents/*`, prior overprescription/scope-creep findings, base-side restoration, touched APPROVED tasks, broad formatting/rewrite hunks, and Sync-impact-only justifications.

- [x] **Step 4: Keep repo-specific gates local**
  For this repo's skill/agent prose, preserve the DRY / Necessity line-by-line gate. For general codebase integration, express the broader rule as minimum net diff: no unjustified cleanup, overengineering, defensive edits, or speculative abstractions.

**Final diff self-check:** `git diff origin/main..HEAD -- skills/refactor-and-integrate/SKILL.md skills/refactor-and-integrate/references/drift-test-quality.md tests/test-sync-integration-contract.sh`; surviving-change classes: refactor-and-integrate owner narrowing, Final Diff Self-Check protocol/checklist folded into the skill body, drift-test reference deletion from refactor-and-integrate, targeted contract-test wording. Suspicious hunk justifications: `skills/refactor-and-integrate/SKILL.md` implements Steps 1-4 by removing drift-test / semantic-boundary ownership, centering codebase minimum net diff, and allowing an explicit caller-provided governing range; deleting `skills/refactor-and-integrate/references/drift-test-quality.md` removes refactor-and-integrate drift-test ownership while Task 9 owns the result-protection target.

---

### Task 11: Re-audit the surviving diff under the current integration gate
**Depends on:** Task 9, Task 10
**Review status:** APPROVED
**Integration status:** APPROVED

**Files:** `skills/*`, `agents/*`, generated artifacts if canonical role specs change, `README.md`, `CLAUDE.md`, `skills/CATEGORIES.md`, `tests/*`, `PLAN.md`, `RESULTS.md`.
**Input:** Task 8 review note, Tasks 9-10, current `BASE_REF=origin/main` at `61588d9`, recorded Sync base `30d6c91`, dispatch governing diff `git diff origin/main..HEAD`, and the current `CLAUDE.md` DRY / Necessity gate for instruction-bearing files.
**Output:** A line-by-line pruning pass over `git diff origin/main..HEAD` that removes wrapper/explanatory instruction lines, preserves behavior-shaping protocol, updates tests/docs only where the current contract requires it, and leaves the branch ready for trusted integration review.

- [x] **Step 1: Establish the audit surface**
  Listed changed files with `git diff --name-status origin/main`; inspected the newer `origin/main` commits (`a40613b`, `c337e96`, merge `61588d9`) and found the only newer-main overlap is `skills/planning-workflow/SKILL.md` header-field sweep. Adopted that current-main line without running Sync or merge.

- [x] **Step 2: Apply the owner and necessity gates**
  Split result protection from codebase integration, folded the remaining codebase-integration reference into `refactor-and-integrate/SKILL.md`, removed stale drift-test ownership from public/contributor summaries, kept Sync impact as supplied justification evidence only, removed the stale direct-mode reviewer cleanup hook for retired `## Upstream Intent` wording, trimmed mode-reference wrapper/input prose, and removed the canonical dispatch-template prefix that restated role protocol / manifest loads.

- [x] **Step 3: Preserve generated-artifact discipline**
  Did not hand-edit generated artifacts in this pass. Canonical role files were unchanged, so the existing generated Codex/direct-mode artifacts remain the source-generated branch artifacts and are verified by the generator `--check` command.

- [x] **Step 4: Verify**
  Passed:
  ```bash
  git diff --check
  bash tests/test-sync-integration-contract.sh
  bash tests/check-harness-compatibility.sh
  python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check
  python3 skills/codex-superra-setup/scripts/test_sync_codex_agents.py
  rg -n "Stage: sync|Upstream Intent|merge-quality|sync-quality|sync-map-format|one minimal commit|one sync commit|Sync impact obligations|Post-sync obligations|Remaining Obligations|semantic propagation" skills agents README.md CLAUDE.md .codex tests -g '*.md' -g '*.toml' -g '*.py'
  rg -n "Follow the standard stage-relevant workflow|standard Before-You-Start|Every template opens|prefix tells|The dispatch supplies|Inputs include|future dispatch-only|after workflow Sync" skills agents README.md CLAUDE.md .codex tests -g '*.md' -g '*.toml' -g '*.py'
  ```
  The legacy scan returned only the intentional negative assertion in the Codex generator test. The wrapper/overprescription scan returned only the CLAUDE.md gate definition.

- [x] **Step 5: Review**
  Integration reviewer walks `git diff origin/main..HEAD` line by line before approval, with special attention to `skills/result-protection/SKILL.md`, `skills/refactor-and-integrate/SKILL.md`, `skills/integration-workflow/SKILL.md`, `skills/semantic-merge/SKILL.md`, `skills/planning-workflow/SKILL.md`, and canonical role specs.

**Final diff self-check:** `git diff origin/main..HEAD`; surviving-change classes: result-protection split, refactor-and-integrate owner narrowing, Codebase Integration checklist folded into `SKILL.md`, semantic-merge workflow/standalone mode references, integration-workflow Sync/Integrate choreography, canonical dispatch-template prefix removal, current-main planning header-field preservation, generated role artifact refresh, public/category summary currency, and contract-test updates. Suspicious hunk justifications: instruction edits under `skills/*` and `agents/*` implement Tasks 9-11 and remove duplicated ownership surfaces; `skills/agent-orchestration/SKILL.md` and `skills/agent-orchestration/references/agent-teams.md` remove dispatch prompt wrapper text that restated role protocol / manifest loads; `skills/planning-workflow/SKILL.md` preserves the newer `origin/main` header-field sweep while retaining this branch's Document/Sync vocabulary; `skills/codex-superra-setup/scripts/sync_codex_agents.py` deletes stale direct-mode reviewer cleanup for the retired `## Upstream Intent` role text; generated `.codex/agents/superra_reviewer.toml` follows from `agents/reviewer.md`; deleted `skills/refactor-and-integrate/references/codebase-integration.md` is covered by the user decision to fold the remaining reference into the main skill.
