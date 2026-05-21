# Writing Review Retrofit Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for PLAN.md editing. This is a retroactive review plan for an already-implemented superRA internals change. Use `superRA:writing` for writing-skill behavior and `skill-creator` discipline for skill-authoring changes.

**Objective:** Fix the writing vertical so large writing work has a planning reference and long-form review uses PLAN.md task-local review notes rather than a separate staged findings document.

**Methodology:** Retain workflow ownership boundaries: planning-workflow routes writing to a writing-owned planning reference; implementation-workflow remains generic; writing owns the PLAN-only long-form review retrofit exception.

**Generated artifacts:** None touched. If later changes affect generated direct-mode role references or Codex named-agent files, regenerate through `skills/codex-superra-setup/scripts/sync_codex_agents.py`.

**Output:** Updated writing skill/reference docs and structural contract tests.

**Expected Results / Hypotheses:** The reviewer should find no surviving `REVIEW.md` / Stage 1 / Stage 2 long-form-review lifecycle, no implementation-workflow ownership of the writing-specific exception, and a writing planning reference that supplies the missing planning hard gate.

**Pipeline:** `bash tests/check-harness-compatibility.sh`

---

## Workflow Status

- [x] **Plan approved** — retroactive plan records the already-implemented user direction.
- [x] **Execution complete** — Task 1 approved in review commit `e94bf1f`; verification passed.
- [x] **Drift tests created** — protected by contract/harness checks for skill behavior; no separate RESULTS.md exists for this retrofit.
- [ ] **Integrated** — pending post-sync integration review against `origin/main` at `15755310cf4c32e91a67e1bd79989c57f1406b26`.
- [ ] **Docs finalized** — pending Sync Map cleanup after post-sync integration review; no RESULTS.md is created for this writing-review retrofit.
- [ ] **Finished** — pending final branch action.

---

## Project Conventions

Walked at planning time (2026-05-20). Re-walk on-demand only.

### Repo root
- `/CLAUDE.md` (HEAD `c36f31a` before this plan): superRA internals changes are skill creation; load `skill-creator` before editing `skills/*/SKILL.md`; keep workflow behavior in owning workflow skills, domain behavior in domain skills, generated artifacts generated, and apply the DRY/Necessity line gate to every instruction-bearing edit under `skills/*` or `agents/*`.
- `/AGENTS.md`: symlink/alias to `/CLAUDE.md`.
- `/README.md`: user-facing product overview; do not duplicate contributor or workflow-internal rationale there unless user-facing surfaces need it.

### Module-level docs walked
- `skills/writing/CLAUDE.md` (pre-change branch state): writing is a domain add-on, not a workflow fork; `SKILL.md` owns unconditional principles and mode routing; references own mode-specific details; workflow dispatch/status mechanics stay in workflow/orchestration owners unless behavior is writing-specific.

---

## Decisions

> **User decision (2026-05-20):** Use PLAN.md only for this retroactive review; no RESULTS.md.
> **Question asked:** How should the missing durable review surface be handled after the ad-hoc branch review?
> **Rationale (if given):** The review finding can state there is no RESULTS.md; the serious fix is adding a writing planning reference and making long-form review interact with PLAN.md.

> **User decision (2026-05-20):** Integrate against `origin/main`.
> **Question asked:** Which base should the current branch be reviewed and integrated against?
> **Rationale (if given):** The user requested review of the current branch against main.

---

## Sync Map

**Base branch:** `origin/main`
**Pre-sync merge base:** `8c3db7db058539c5cde7e7ffdc360d8d936fe866`
**Synced base head:** `15755310cf4c32e91a67e1bd79989c57f1406b26`
**Incoming range:** `8c3db7db058539c5cde7e7ffdc360d8d936fe866..15755310cf4c32e91a67e1bd79989c57f1406b26`
**Sync commits:** `78c12669c7f38dd3b6ed192357a0bb5952f9fdd1`, `6b99803fcd73d0c1e4ca67b92c5fb9f5f3d1a1aa`
**Sync review status:** `APPROVED`

### Branch Summary

**Incoming intent:** `origin/main` makes `report-in-markdown` the always-loaded markdown style guide, adds markdown-link citation rules to canonical agent and handoff examples, regenerates Codex agent artifacts, and archives the completed markdown-style-guide plan/results.
**Resolution thesis:** Keep incoming markdown-style-guide behavior on generic/shared surfaces while preserving the branch's writing vertical. The sync is additive: branch-owned writing planning and PLAN-only long-form review remain the task intent, and incoming file-citation/report-in-markdown ownership becomes the base convention those writing changes now sit on top of.

### Sync Clusters

> **Sync cluster `RIM-2026-05-20` (2026-05-20):** commits `1575531`; paths `CLAUDE.md`, `README.md`, `agents/*`, `.codex/agents/*`, `skills/CATEGORIES.md`, `skills/agent-orchestration/SKILL.md`, `skills/handoff-doc/*`, `skills/report-in-markdown/*`, `skills/theory-modeling/references/integration.md`, `skills/using-superRA/*`, `docs/plans/2026-05-20-markdown-style-guide-*`; affects Tasks `1`.
> **Incoming intent:** Make `report-in-markdown` the markdown style guide for all agents, teach markdown-link source citations across canonical examples, and preserve generated Codex artifacts from the regenerated agent specs.
> **Sync resolution:** Accepted the incoming markdown-style-guide updates on shared utilities, role specs, generated direct-mode/Codex artifacts, and archived markdown-style-guide docs; preserved the branch's writing vertical, writing planning reference, PLAN-only long-form review retrofit, and related contract test.
> **Integration context:** Later codebase review should evaluate the writing vertical against the new always-loaded `report-in-markdown` base convention; no broader convention-fit refactor is performed in Sync.
> **User decision:** None.

### Task 1: Writing Planning Reference and PLAN-Only Long-Form Review
**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:** IMPLEMENTED
**Sync impact:** Cluster `RIM-2026-05-20` explains the incoming markdown-style-guide base change that overlaps Task 1's writing-skill routing and shared instruction surfaces. Source: `PLAN.md ## Sync Map`.

> **Review notes (integration):**
> 1. **[BLOCKING] MAJOR** — [skills/writing/references/consistency/citations.md:92](skills/writing/references/consistency/citations.md#L92), [skills/writing/references/consistency/cross-references.md:75](skills/writing/references/consistency/cross-references.md#L75), [skills/writing/references/consistency/numerical.md:104](skills/writing/references/consistency/numerical.md#L104), [skills/writing/references/consistency/terminology.md:85](skills/writing/references/consistency/terminology.md#L85), and [skills/writing/references/consistency/code-paper.md:98](skills/writing/references/consistency/code-paper.md#L98) still teach writing reviewers to report source locations as raw `file.tex:<line>` / `file.ext:<line range>` fields. That conflicts with the synced-base convention that `report-in-markdown` is always loaded and owns source-file citation style: [skills/report-in-markdown/SKILL.md:13](skills/report-in-markdown/SKILL.md#L13) requires markdown links with line anchors. Fix the writing output templates and nearby review guidance, including [skills/writing/references/review.md:11](skills/writing/references/review.md#L11), so they either use markdown-link citation examples or explicitly defer source-file citation formatting to `report-in-markdown`; do not create a writing-owned competing citation style.
>    → implemented: updated the writing review guidance to defer source-location formatting to `report-in-markdown`, replaced raw source-location placeholders in the cited consistency templates with markdown-link examples, and added a contract guard for retired raw placeholders ([skills/writing/references/review.md:11](skills/writing/references/review.md#L11), [skills/writing/references/consistency/citations.md:92](skills/writing/references/consistency/citations.md#L92), [tests/test-sync-integration-contract.sh:92](tests/test-sync-integration-contract.sh#L92)).

**Files:** `skills/writing/references/planning.md`, `skills/writing/references/long-form-review.md`, `skills/writing/SKILL.md`, `skills/writing/CLAUDE.md`, `skills/writing/references/polish.md`, `skills/planning-workflow/SKILL.md`, `skills/CATEGORIES.md`, `tests/test-sync-integration-contract.sh`

**Input:** Existing branch diff against `main`, user direction to keep implementation-workflow generic and move the exception into writing.

**Output:** Writing-owned planning hard gate and long-form review retrofit protocol, with contract tests enforcing the ownership boundary.

- [x] **Step 1: Add writing planning reference**

  Added `skills/writing/references/planning.md` with a writing plan header, hard gate, PLAN-only long-form review retrofit rows, and writing-side project convention guidance.

- [x] **Step 2: Rework long-form review protocol**

  Replaced staged `REVIEW.md` / `## Findings` lifecycle with a PLAN.md retrofit: reviewers inspect the existing draft through task-local review notes and normal `Review status` values.

- [x] **Step 3: Keep workflow ownership boundaries**

  Routed `planning-workflow` to the writing planning reference for large writing work, but left `implementation-workflow` unchanged. The writing reference owns how the PLAN-only exception is entered.

- [x] **Step 4: Update nearby writing guidance**

  Updated writing skill routing, contributor notes, and polish-mode language to remove stale `REVIEW.md` / Stage 2 references.

- [x] **Step 5: Verify contract**

  Ran `bash tests/test-sync-integration-contract.sh`, `bash tests/check-harness-compatibility.sh`, and `git diff --check`; all passed before review dispatch.

**Protection:** `bash tests/test-sync-integration-contract.sh` (including the raw source-location placeholder guard), `bash tests/check-harness-compatibility.sh`, `rg -n "file\\.(tex|ext):<line" skills/writing/references tests/test-sync-integration-contract.sh`, and `git diff --check` passed after the Task 1 integration fix. These checks protect the writing retrofit behavior, synced markdown citation ownership, and generated-artifact contract for this skill-instruction branch.

**Final diff self-check:** `git diff 15755310cf4c32e91a67e1bd79989c57f1406b26..HEAD`; surviving-change classes are the approved writing-skill branch, writing reference docs, planning/using/integration workflow routing for the writing vertical, generated/packaging surfaces, and contract tests. Suspicious hunks in writing review-output templates and `tests/test-sync-integration-contract.sh` are justified by the accepted integration review item aligning Task 1 with the synced `report-in-markdown` citation owner.
