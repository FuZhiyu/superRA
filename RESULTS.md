# Unified Integration-Workflow Refactor — Results

> Mirrors PLAN.md structure. Updated after each task with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-19 (bootstrap)
**Status:** In Progress

---

## Task 1: Rebuild `refactor-and-integrate` as a gated checklist

**Status:** IMPLEMENTED

**Summary:** `skills/refactor-and-integrate` restructured with a clean separation between **principle-level body** (SKILL.md) and **how-to + checklist references** — one source of truth per concern. SKILL.md describes what each of the three concurrent disciplines (Drift-Test Integrity, Codebase Integration, Merge Quality) is *for*, names the severity-marker convention (`[BLOCKING]` / `[ADVISORY]`), carries the load-bearing **Minimum net diff to merge base** top item, the two-verdict reviewer protocol (APPROVE / REVISE + dependent-finding prose + narrow re-review), and the pre-commit **Implementer Self-Check** (`git diff <merge-base>..HEAD`). All tuned content lives in the three references, reached via stage-scoped required loads per `superRA:using-superRA` §Skill-Load Manifest.

**Key structural choices:**

- **SKILL.md = principles + cross-cutting gates.** No verbatim Red Flags Never-list, no Tier 3 escalation blockquote, no RA-framing blockquotes. Principle descriptions may *name* concepts ("Tier 3 conflicts", "Red Flags") but the tuned prose lives only in references. Body retained items: load-bearing top item, reviewer verdict protocol, Implementer Self-Check, dispatch convention, integration-pointers.
- **References restructured as §How-To + §Gated Checklist.** Each reference now opens with a how-to section (procedures, worked examples, Red Flags rationale, Tier 3 escalation procedure + Never-list, Project Doc Audit walk-up algorithm, two-commit commit-message templates, integration-map format) and closes with the gated checklist — severity-marked items whose prose points back into §How-To.
  - `drift-test-quality.md` §How-To: tolerance calibration worked examples, red-green cycle, test format conventions, Cross-cutting Red Flags (four-bullet "Never" list, verbatim).
  - `codebase-integration.md` §How-To: handling-inconsistencies decision tree (RA-framing wording preserved verbatim), Project Doc Audit walk-up.
  - `merge-quality.md` §How-To: two-commit templates, Research-Meaningful Escalation (Tier 3) prose + five-conflict-type list + four-bullet "Never" list (verbatim), integration-map format.
- **Tuned wording preserved verbatim.** All Red Flags, rationalization bullets, Tier 3 escalation prose, and RA-framing sentences were relocated with no paraphrasing, per `/CLAUDE.md §Skill Changes`.
- **Shared-flow checklist, one source of truth.** Implementer walks each reference's §Gated Checklist as self-check before commit; reviewer walks the same items as verification. No parallel review-only document exists; no content is duplicated between SKILL.md body and references.
- **Manifest wording tight.** `integration` / `drift-test` / `merge` rows in `using-superRA/SKILL.md` §Skill-Load Manifest already name the specific references as required (`codebase-integration.md`, `drift-test-quality.md`, `merge-quality.md`). No manifest edit needed.

**Scope notes:**

- Caller-side wording in `integration-workflow/SKILL.md`, `merge-workflow/SKILL.md`, and `using-superRA/SKILL.md` still references the filenames directly; those pointers remain valid.
- `[BLOCKING] Handoff-doc coherence` in merge-quality is deferred to Task 4 per plan.

**Verification:**

- `grep` for "Silently update drift", "Tier 3", and "Never:" in SKILL.md shows the verbatim blockquotes are gone from the body; same strings present verbatim in the references.
- `git diff 92a685b..HEAD` on this task's commit touches exactly four files: SKILL.md and the three references under `skills/refactor-and-integrate/`. No unrelated hunks (Minimum-net-diff self-check passes).



## Task 2: Unify `integration-workflow` — Phases A–D with iterative Phase B

**Status:** Not started

## Task 3: Delete `skills/merge-workflow/`

**Status:** Not started

## Task 4: Update `semantic-merge` caller paths and handoff-doc coherence rule

**Status:** Not started

## Task 5: Minimal `planning-workflow §Changing Plans` extension

**Status:** Not started

## Task 6: Sync peripheral surfaces

**Status:** Not started

## Task 7: End-to-end dry-run verification

**Status:** Not started
