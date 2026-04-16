# superRA Design Coherence Refactor — Results

> Mirrors PLAN.md structure. Updated after each task with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-16 (pre-Task-1)
**Status:** In Progress

**Domain vertical:** Plugin-development (skills/hooks/docs refactor). Not a data-analysis task — no row-counts, no figures, no regression outputs. "Key Findings" captures edits made, orphan-reference grep results, and any skill-description triggering check outcomes.

---

## Task 1: Consolidate Stage names + remove dispatch re-statements

**Status:** IMPLEMENTED

### Key Findings

**Canonical Stage set after the refactor** (matches `using-superRA` §Skill-Load Manifest 1:1): `implementation`, `refactoring`, `drift-test`, `integration-review`, `merge`, `documentation`, `planning-review`. One new manifest row added — `integration-review` — because integration review's reference set differs from `refactoring` (it runs the same loads today, but the two are semantically distinct stages and Tasks 3 / 6 will refine them independently). The `Fallback rule` that silently mapped unknown `Stage:` values to `implementation` defaults is replaced by an explicit halt-and-report policy — drift through guessed fallbacks is no longer a failure mode.

**Dispatch templates collapsed to canonical shape.** Every dispatch across `integration-workflow`, `merge-workflow`, `semantic-merge`, and `refactor-and-integrate` now emits only `Stage:` + `Task:` (+ `Git range:` for reviewers) + the "Follow the standard stage-relevant workflow" prefix + `Additionally:` steering. The redundant `Skills:` / `Domain reference(s):` / free-form context fields (`Key results to protect:`, `Tests under review:`, `Merge context:`, etc.) are gone — the manifest specifies the loads and the agent reads task content from `PLAN.md` / `RESULTS.md` directly. Dispatch-line count dropped sharply across the four skills.

**Three per-workflow Agent-Types tables deleted.** `integration-workflow` (the 8-row domain-reference table), `semantic-merge` (`## Agent Types and Domain References`), and `execution-workflow` (`## Agent Types`) all had tables enumerating what each Stage loads — those tables duplicated the manifest and were drift sources. Each is replaced with a 2-3-line `## Agent Loads` section pointing at `superRA:using-superRA` §Skill-Load Manifest and naming which manifest rows the workflow runs.

**Agent files stop loading dispatch-named references.** `agents/implementer.md` and `agents/reviewer.md` previously step-3-loaded "additional skills specified in your dispatch prompt" and step-4-loaded "the domain reference file specified in your dispatch prompt." Both steps assumed dispatches named references — they no longer do. Step 3 is rewritten to "load any additional skill the dispatch's `Additionally:` line names (rare — overrides only)." Step 4 is deleted; remaining steps renumber; the in-paragraph cross-reference updates from "step 7 below" to "step 6 below." Both agents' stage-loading paragraph is also updated: the old fallback-to-`implementation` for unknown Stages is replaced with halt-and-report.

**One description frontmatter change, one writing-skills triggering check.** Per override #3, only `skills/refactor-and-integrate/SKILL.md`'s `description:` field was modified — its old trailing enumeration listed deprecated Stage names (`drift test creation`, `drift test review`, `integration review`, `merge proposer`, `merge review`) that no longer exist anywhere in the plugin. Updated to name the canonical manifest rows (`drift-test`, `refactoring`, `integration-review`, `merge`). Triggering check: the description still fires on its original triggers — "creating drift tests", "refactoring analysis code", "writing clean merge integration commits" — so no discovery surface is lost; the change only synchronizes the enumeration with the new manifest, an inline correctness fix.

**Task 1 preserved the coupled-chain precondition.** Per override #5, the `integration-review` manifest row carries the same reference load as `refactoring` (domain §Refactor integrity; `codebase-integration.md`; `integration.md`; `integrate-drift-tests.md` if drift tests exist). Tasks 3 and 6 will refine that row later — Task 1's responsibility was only to establish the row with current loads so downstream tasks have a target to refine.

### Validation

Step-7 greps after the refactor:
- `Stage:` across `skills/` + `agents/` — every live emission is canonical: `drift-test`, `integration-review`, `refactoring`, `merge`, `documentation`. (Manifest rows: `implementation`, `refactoring`, `drift-test`, `integration-review`, `merge`, `documentation`, `planning-review`.)
- `Skills:` / `Domain reference(s):` in dispatch blocks — zero. The two remaining `Skills:` hits in the wider grep (`agent-orchestration:77`, `refactor-and-integrate:36`) are meta references describing where override lines *would* go and the fact that dispatches do not restate them; neither is a live dispatch line.
- `Agent Types` tables — zero remaining anywhere.
- Stale Stage names as live `Stage:` field emissions in dispatch blocks across `skills/` + `agents/` — zero (every `Stage:` value matches a manifest row). Stale stage-name *prose* references remain in files outside Task 1's Files-affected list: `README.md` architectural diagram (5 `Stage:` strings in the user-facing flow); role-description enumerations in `skills/agent-orchestration/SKILL.md:127`, `agents/reviewer.md:6,109`, `skills/execution-workflow/SKILL.md` graphviz labels at 69/88/89/91, `skills/report-in-markdown/SKILL.md:33`, `skills/refactor-and-integrate/SKILL.md:17,80,82`, `skills/econ-data-analysis/SKILL.md:327`, `skills/econ-data-analysis/references/integration.md:3,5`; plus the old `drift test creation` row-name in `tests/structural-invariants.sh:431,433,435`. Deferred to Task 16 Step 6 per PLAN.md (line 453 explicitly names these strings for the final sweep). Historical audit enumerations in `PLAN.md` Step 1 and release notes in `RELEASE-NOTES.md` also retain the old names, both legitimate as record.

### Notes

The `integration-review` manifest row currently replicates the `refactoring` row verbatim. Tasks 3 and 6 split and refine it. Task 6 also drops `handoff-doc` from most rows (superseded by `using-superRA` §Handoff Doc Discipline) — Task 1 leaves the `handoff-doc` loads intact because Task 6 owns that sweep.

---

## Task 2: Drop Agent Teams "recipe" framing

**Status:** *(not started)*

### Key Findings
*(to be populated)*

---

## Task 3: Slim `econ-data-analysis/SKILL.md` + extract disciplines reference

**Status:** *(not started)*

### Key Findings
*(to be populated)*

---

## Task 4: Move `script-to-notebook` into `econ-data-analysis` as a reference

**Status:** *(not started)*

### Key Findings
*(to be populated)*

---

## Task 5: Cache project conventions in PLAN.md header

**Status:** *(not started)*

### Key Findings
*(to be populated)*

---

## Task 6: Centralize agent-shared discipline in `using-superRA`

**Status:** *(not started)*

### Key Findings
*(to be populated)*

---

## Task 7: Stop restating User Decisions Log discipline

**Status:** *(not started)*

### Key Findings
*(to be populated)*

---

## Task 8: Step 0b — explicit handoff to `planning-workflow`

**Status:** IMPLEMENTED

### Key Findings

**`skills/execution-workflow/SKILL.md` Step 0b** now halts and invokes `superRA:planning-workflow` when the existence check fails, instead of inlining a bootstrap procedure. Old body (3 paragraphs: "Before any task dispatch" / "Step 0 ... Task 0 cannot silently land" / "If the docs exist, are tracked ...") → new body (2 paragraphs: the halt-and-invoke instruction + the revised Step-0 cross-reference that no longer uses "Task 0" framing). The inline "satisfy the domain-specific planning gate (for data analysis: the Data Inventory hard gate ...)" wording is gone — that work happens inside planning-workflow's Phase 1 now, not inline here.

**`skills/planning-workflow/SKILL.md` Overview** gains a second paragraph acknowledging the invocation path from execution-workflow Step 0b: "May be invoked from `execution-workflow` Step 0b when an existing branch lacks committed `PLAN.md` / `RESULTS.md` (or carries uncommitted edits to them). The bootstrap path is identical to a fresh start — run the full Phase 1 / Phase 2 / Self-Review, satisfy any domain-specific planning gate, commit the docs, and hand control back. No shortcut." The wording "no shortcut" closes the design question — there is no lightweight bootstrap mode, just the normal planning flow.

**Validation:** `grep "Task 0\b" skills/execution-workflow/SKILL.md` returns zero matches after the edit. Both skills re-read end-to-end flow cleanly — execution-workflow's failure branch becomes a one-sentence halt, and planning-workflow's overview reads as a natural entry point whether arrived-at fresh or invoked via execution-workflow.

---

## Task 9: Move project doc audit into integration Stage 2

**Status:** *(not started)*

### Key Findings
*(to be populated)*

---

## Task 10: Subdivide RESULTS.md maturation into ordered commits

**Status:** *(not started)*

### Key Findings
*(to be populated)*

---

## Task 11: Skip post-merge integration review on Tier 1 clean merges

**Status:** *(not started)*

### Key Findings
*(to be populated)*

---

## Task 12: Clarify `semantic-merge` standalone vs delegated

**Status:** *(not started)*

### Key Findings
*(to be populated)*

---

## Task 13: Distribute `verification-before-completion` + delete the skill

**Status:** IMPLEMENTED

### Key Findings

**Skill folder deleted:** `skills/verification-before-completion/SKILL.md` (143 lines) removed via `git rm -r`.

**Distribution of unique content:**

- **`agents/implementer.md` §Self-Review Before Reporting** — added the 5-step Gate Function (IDENTIFY → RUN → READ → VERIFY → claim) as a new opening subsection, followed by the bottom-line one-liner "Run the command, read the output, then claim the result." Preserved the existing Completeness / Reproducibility / Domain §Review checks beneath it.
- **`agents/implementer.md` §Pre-Commit Self-Check** — appended a red-flag wording block ("should", "probably", "seems to", "Great!", "Done!", "Perfect!") at the end of the checklist, instructing the implementer to stop and verify if any of those words show up without fresh verification evidence.
- **`agents/reviewer.md` §Verify Claims Independently** — prepended a "DO NOT take the implementer's word" paragraph with the new diff-vs-status-return framing ("check the git diff, not just the status return — agents can report 'success' for partial work").
- **`agents/reviewer.md` §Pre-Commit Self-Check** — appended the same red-flag wording block as the implementer, scoped to the reviewer's verdict instead of the commit claim.
- **`skills/refactor-and-integrate/references/drift-test-quality.md`** — added a new `## Red-Green Verification` section between Robustness and Test Format, carrying the Write → Green → Revert → Red → Restore → Green cycle with the rationale "a drift test that passes once is not verified — it might always pass."
- **`skills/execution-workflow/SKILL.md` Step 3 preamble** — inserted a bold one-sentence reminder: "Run every check. Don't trust 'looks committed' — execute `git status` and read the output. The five checks below are the orchestrator's verification gate: evidence before claims, no shortcuts."

**Reference sweep results (grep `verification-before-completion` across `skills/`, `agents/`, `README.md`, `CLAUDE.md`):** zero matches. Also cleaned:
- `skills/using-superRA/SKILL.md` §Skill Inventory — row removed.
- `skills/CATEGORIES.md` Utility table — row removed.
- `README.md` Utility table — row removed.
- `skills/writing-skills/SKILL.md:401` — updated "TDD, verification-before-completion, designing-before-coding" to "TDD, designing-before-coding".

**Intentionally not touched:**
- `PLAN.md` (this refactor plan) and `RESULTS.md` (this dev log) retain references as historical record of the refactor.
- `docs/plans/2025-11-28-skills-improvements-from-user-feedback.md` is an archived prior plan document, not current inventory.

**Note on §Skill Types.** PLAN.md Step 7 anticipated removing the skill from a §Skill Types "Rigid" example list in `using-superRA`. That section does not currently exist in `using-superRA/SKILL.md` (apparently removed in the pre-plan commit `e5c8b58` which stripped EXTREMELY-IMPORTANT / Red Flags / Skill Types sections). The `writing-skills` Discipline-Enforcing example list was the only remaining "types-like" enumeration — updated as documented above.

---

## Task 14: Consolidate worktree skills (drop `using-analysis-worktrees`)

**Status:** *(not started)*

### Key Findings
*(to be populated)*

---

## Task 15: Remove deprecated commands

**Status:** IMPLEMENTED

### Key Findings

**Files deleted (3):**
- `commands/brainstorm.md` — stub pointing at `superpowers:brainstorming`.
- `commands/execute-plan.md` — stub pointing at `superpowers:executing-plans`.
- `commands/write-plan.md` — stub pointing at `superpowers:writing-plans`.

The `commands/` directory is now empty and git treats it as removed (no tracked files remain in it).

**Grep sweep (`execute-plan|write-plan|brainstorm` across `skills/`, `commands/`, `README.md`, `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `CATEGORIES.md`, `agents/`, `hooks/`):** zero matches after the deletion. No inventory-table rows or skill-body references to clean up — the stubs were referenced only by the plugin runtime's command discovery, not by any skill body or README table.

**Intentionally not touched:**
- `RELEASE-NOTES.md` and `CHANGELOG.md` carry upstream superpowers release history mentioning these commands (lines documenting their introduction, deprecation, and removal in prior upstream versions). These are historical release records, not current inventory, so they stay. superRA's own release-note entry for this refactor lands in Task 16 Step 4.

**Task-1 overlap check:** grep surfaced no references inside any of Task 1's files (`skills/using-superRA/SKILL.md`, the 4 workflow skills, `skills/semantic-merge/SKILL.md`, `skills/refactor-and-integrate/SKILL.md`, `agents/implementer.md`, `agents/reviewer.md`). No deferred edits for Task 1 to absorb.

### Notes
The PLAN's Step 2 mentioned "Remove the 'Deprecated — use superpowers:* instead' rows from any inventory tables (likely in README.md or CHANGELOG)." None existed in superRA's README or anywhere under skill / agent / command files — the stubs self-describe their deprecation in their own frontmatter only. Clean deletion.

---

## Task 16: Final consistency pass

**Status:** *(not started)*

### Key Findings
*(to be populated)*

---

## Task 17: Document agent-reuse vs fresh-dispatch heuristic in agent-orchestration

**Status:** *(not started)*

### Key Findings
*(to be populated)*
