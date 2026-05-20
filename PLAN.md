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
- [x] **Integrated** — Task 1 integration review approved in `069c543`; post-review verification passed.
- [ ] **Docs finalized** — pending branch disposition.
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

### Task 1: Writing Planning Reference and PLAN-Only Long-Form Review
**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:** APPROVED

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

**Protection:** `bash tests/test-sync-integration-contract.sh`, `bash tests/check-harness-compatibility.sh`, and `git diff --check origin/main..HEAD` passed on 2026-05-20. These checks protect the writing retrofit behavior and generated-artifact contract for this skill-instruction branch.

**Sync:** No-op against `origin/main`; `BASE_HEAD_SHA=8c3db7db058539c5cde7e7ffdc360d8d936fe866`, `PRE_SYNC_BASE_SHA=8c3db7db058539c5cde7e7ffdc360d8d936fe866`, and `origin/main` is already an ancestor of `HEAD`.

**Final diff self-check:** `git diff origin/main..HEAD`; surviving-change classes are the approved writing-skill branch, writing reference docs, planning/using/integration workflow routing for the writing vertical, generated/packaging surfaces, and contract tests. Suspicious hunks are justified as skill-authoring behavior under the approved Task 1 objective plus the pre-existing branch objective to add the writing vertical.
