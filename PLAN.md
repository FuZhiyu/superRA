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
- [ ] **Execution complete** — pending reviewer approval.
- [ ] **Drift tests created** — N/A for this skill-instruction edit unless integration later chooses a protection mechanism.
- [ ] **Integrated** — pending integration review if this branch proceeds to integration closeout.
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

---

### Task 1: Writing Planning Reference and PLAN-Only Long-Form Review
**Depends on:** *(none)*
**Review status:** REVISE
**Integration status:** *(unset)*

> **Review notes:**
> 1. **MAJOR** — `skills/planning-workflow/SKILL.md:12`, `skills/planning-workflow/SKILL.md:19`, `skills/planning-workflow/SKILL.md:105`, and `skills/planning-workflow/SKILL.md:191`: `planning-workflow` now directly names and explains the writing long-form review PLAN-only / no-`RESULTS.md` exception. That violates the task decision and root DRY/Necessity gate: `planning-workflow` should route large writing work to `skills/writing/references/planning.md`, while the exception itself is owned by writing skill/reference surfaces only. Fix by removing the writing-specific exception prose from `planning-workflow`; if the workflow needs an extension point, phrase it generically as obeying the active domain planning reference rather than restating this writing exception.
>    → implemented: removed writing-specific exception prose from `skills/planning-workflow/SKILL.md`; the workflow now only exposes a generic active-domain durable-record extension point and routes writing to `skills/writing/references/planning.md`.
> 2. **MAJOR** — `tests/test-sync-integration-contract.sh:278`: the new contract tests assert that `planning-workflow` routes to the writing planning reference and that `implementation-workflow` does not name the retrofit, but they do not fail when `planning-workflow` itself carries the PLAN-only / no-`RESULTS.md` exception. This allowed finding 1 to pass the test suite. Add a contract guard that prevents `skills/planning-workflow/SKILL.md` from owning the writing-specific PLAN-only / no-`RESULTS.md` exception, while still allowing the generic route to the writing planning reference.
>    → implemented: added contract guards in `tests/test-sync-integration-contract.sh` that fail if `skills/planning-workflow/SKILL.md` contains `Long-form review retrofit`, `PLAN-only`, or `no RESULTS.md`.

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
