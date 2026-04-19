---
name: refactor-and-integrate
description: Utility skill (any phase). Use when creating drift tests, refactoring analysis code for codebase integration, or writing clean merge integration commits. Carries the gated checklist — Drift-Test Integrity, Codebase Integration, Merge Quality — shared by implementer (self-check before commit) and reviewer (verification). Standalone-invokable — usable outside the integration phase for any refactoring task. Dispatched implementer/reviewer subagents load this skill when their Stage is `drift-test`, `integration`, or `merge` (per `superRA:using-superRA` §Skill-Load Manifest).
---

# Refactor and Integrate

Utility skill carrying the domain knowledge for three closely related tasks in the INTEGRATE phase:

1. **Creating drift tests** that guard key results from unintended changes during refactoring or future modifications.
2. **Refactoring analysis code** for codebase integration — making the code fit the host project's conventions, utilities, and style without losing data discipline or results.
3. **Writing clean merge integration commits** that preserve intent and research integrity when combining branches.

This is a utility skill, not a workflow skill. Workflow skills (`superRA:integration-workflow`, `superRA:merge-workflow`) own procedural choreography — when to dispatch agents, how to sequence stages, how to handle iteration loops. This skill owns the content: what a good drift test looks like, what "refactored for codebase fit" means, what a clean merge commit structure is.

The body below is the **shared gated checklist** that both implementer and reviewer walk. The implementer walks it as self-check before committing; the reviewer walks the same items as verification. Severity markers encode the gate:

- `[BLOCKING]` — must be satisfied for the reviewer to return APPROVE. A failing `[BLOCKING]` is a fix-first, not a handoff.
- `[ADVISORY]` — best-practice. The reviewer MAY flag as MINOR; does not block APPROVE.

Long-form operational procedures (tolerance-calibration worked examples, Project Doc Audit walk-up algorithm, two-commit commit-message templates, Red Flags rationale) live in the three references and are pointed at from the checklist items below — load the reference whose stage you are working in.

**Used by:**
- Dispatched `superRA:implementer` agents during drift-test creation, refactoring, and merge proposal stages
- Dispatched `superRA:reviewer` agents during drift-test review, integration review, and merge review stages
- Anyone invoking this skill directly for an ad-hoc refactoring task outside the formal integration workflow

## When to Load Which Reference

| Stage you are working in | Load reference |
|---|---|
| Creating or reviewing a drift test | `references/drift-test-quality.md` |
| Refactoring analysis code or reviewing a refactor for codebase fit | `references/codebase-integration.md` |
| Proposing a merge or reviewing a proposed merge | `references/merge-quality.md` |

Some tasks cross stages (a refactor during a merge; a drift-test review that flags a refactor-caused sign-flip). Load every reference whose stage your task touches — the checklist sections compose.

The runtime announces this skill's base directory when it loads. Read the relevant reference from `<base_dir>/references/<basename>`.

## Dispatch Convention

Dispatches follow the canonical template in `superRA:agent-orchestration` §Dispatch Templates. The Skill-Load Manifest (`superRA:using-superRA`) names this skill and its reference files on the `drift-test`, `integration`, and `merge` rows — the dispatch prompt does not restate `Skills:` or reference lines. The agent loads this skill, receives the base directory, reads the manifest-named reference, and walks the gated checklist below alongside the domain skill (for data analysis: `superRA:econ-data-analysis`).

---

## The Load-Bearing Top Item

Every round of drift-test creation, refactoring, and merge integration shares one top-level constraint:

- `[BLOCKING]` **Minimum net diff to merge base.** Cumulative refactor across all integration rounds touches only what drift-test preservation, convention fit, handoff-doc coherence, and documentation demand. No unrelated cleanup, no speculative abstractions, no "while I'm here" edits. Implementer runs `git diff <merge-base>..HEAD` before each commit and reviews the cumulative diff; reviewer computes the same diff as evidence.

This item sits at the top because it frames every other item below it — any hunk in the cumulative diff must be justifiable against one of the three disciplines' checklists. A hunk that is not tied to drift-test integrity, codebase integration, or merge quality is out of scope and must be reverted or re-justified. The `Implementer Self-Check` subsection at the end of this file restates the pre-commit procedure.

---

## Three Concurrent Disciplines: Drift-Test Integrity · Codebase Integration · Merge Quality

The three disciplines are **concurrent, not sequential** — a single integration pass typically exercises at least two of them, and the checklists compose. Walk every item in every discipline whose stage the task touches. Never halt on a failure — one comprehensive pass every time.

### Reviewer verdict protocol

**Walk top to bottom through every discipline your task touches, plus the load-bearing top item above. Never halt on a failure.** One comprehensive pass every time — halting early forces a full re-review on the next pass, and reviewer dispatches are costly.

Two verdicts:

- **APPROVE** — no `[BLOCKING]` findings.
- **REVISE** — at least one `[BLOCKING]` finding.

**Handling dependent findings.** When a later finding's assessment depends on an earlier `[BLOCKING]` item being fixed first (e.g., "couldn't fully assess the refactor until the drift tests are passing"), say so in plain prose alongside the finding. No separate verdict, no formal tag.

**Re-review after REVISE.** Implementer fixes all `[BLOCKING]` findings and re-dispatches. Reviewer then (1) verifies each fix is correct, and (2) re-checks any finding the first pass annotated as depending on an upstream fix. Everything else is accepted from the first pass — no third full walk. APPROVE once all `[BLOCKING]` findings are resolved.

---

### Drift-Test Integrity

Load `references/drift-test-quality.md` for tolerance-calibration worked examples and the red-green verification cycle.

**Coverage:**

- `[BLOCKING]` Every user-confirmed key result has at least one test — main findings (coefficients, magnitudes, significance), sample statistics where they define scope.
- `[BLOCKING]` No key result skipped or left unprotected.
- `[ADVISORY]` Focus on KEY results — findings that define analysis conclusions, not every intermediate number.

**Tolerance calibration (set tolerances on economic reasoning, not arbitrary thresholds; see reference for worked examples):**

- `[BLOCKING]` Point estimates, standard errors, counts, signs/significance each carry a tolerance matched to the type of quantity. Too tight → false positives on harmless changes; too loose → misses real drift.
- `[BLOCKING]` Every tolerance choice documented with a comment explaining why (the economic reasoning, not a number-pulled-from-the-air justification).

**Independence:**

- `[BLOCKING]` Tests run without re-executing the full analysis pipeline — load from saved outputs.
- `[BLOCKING]` Test file is self-contained and executable on its own.

**Clarity and robustness:**

- `[BLOCKING]` Test names describe what result they protect (e.g., `test_market_cap_coefficient_sign_and_magnitude`).
- `[BLOCKING]` Floating-point comparisons use tolerance functions (`pytest.approx`, `isapprox`), not exact equality.
- `[ADVISORY]` Tests grouped logically; header comment explains what they protect and when created.
- `[ADVISORY]` Tests would not break from irrelevant changes (file moves, comment edits, import reordering).

**Red-green verification:**

- `[BLOCKING]` Every drift / regression test verified with the red-green cycle before committing — write test, PASS, perturb the protected input, FAIL, restore, PASS. A test that does not turn red on perturbation is a passing no-op. "I've written a regression test" without the cycle is not evidence the test works.

**Test format:**

- `[BLOCKING]` Project testing conventions followed (pytest in `tests/` for Python; Test module in `test/` for Julia; match existing structure).

**Cross-cutting Red Flags (verbatim — applies wherever drift tests are in play during creation, refactor, merge, or rebase):**

> **Never:**
>
> - **Silently update drift test expectations for meaningful result changes.** A test failure after a refactor, merge, or rebase means one of three things: (a) the change broke something and must be fixed, (b) the change revealed a tolerance too tight and must be justified with economic reasoning and an `AskUserQuestion` confirmation from the researcher, or (c) the change meaningfully shifted a result, which is a research conversation with the researcher — surface it via `AskUserQuestion` (plain text fallback when unavailable), log the answer per `handoff-doc` §User Decisions Log, and commit the log entry before updating the expectation. Never a silent expectation bump.
> - **Proceed past failing drift tests without assessment.** Failing tests block the workflow until explicitly adjudicated.
> - **Remove or weaken existing drift tests during refactoring or merge integration.** Tests are part of the analysis contract.
> - **Treat the drift tests as the only safety net.** They protect key results; they do not replace the one-pass review or the data-discipline protocol.

When a drift test fails, follow the orchestrator discipline in `superRA:agent-orchestration` §Handling Reviewer Feedback — read the cited output, classify the failure, and either fix, justify, or escalate.

---

### Codebase Integration

Load `references/codebase-integration.md` for the full Project Doc Audit walk-up algorithm and handling-inconsistencies decision tree. For data-analysis work, **also** load `econ-data-analysis/references/integration.md` — the data-analysis-specific integration gates (variable-construction consistency, transformation-pattern consistency, preserved describe steps / row-count prints / validation checks, drift-test pass-through) are owned there; the items below are the generic cross-cutting code-quality companion that applies regardless of domain.

**Code integration:**

- `[BLOCKING]` **Naming consistency:** Variable, function, and file names follow codebase conventions.
- `[BLOCKING]` **Utility usage:** Existing utility functions reused where appropriate instead of hand-rolled equivalents.
- `[BLOCKING]` **No debug artifacts:** No leftover debug prints, commented-out experiments, or temporary variables.
- `[BLOCKING]` **Minimal existing-file changes:** Modifications to files outside the analysis scope are minimal and justified (adding an import to a shared module is fine; restructuring a shared module is not).
- `[ADVISORY]` **Code simplification:** Redundant code removed, repeated patterns consolidated, readability improved — only where the refactor or integration map demanded the touch.
- `[ADVISORY]` **PR-friendly diffs:** Avoid unnecessary reformatting that obscures substantive changes.

**Handling inconsistencies (see reference for the decision tree):**

- `[BLOCKING]` **Methodological questions escalated, not resolved.** Different control variable sets, different variable definitions, different sample filters — these are research decisions, not code-quality decisions. Flag for the user; do not choose silently. Domain-specific methodological gates for data analysis live in `econ-data-analysis/references/integration.md`.
- `[ADVISORY]` **Clear convention exists:** follow the convention. **Ambiguous or conflicting conventions:** use best judgment and document the choice.

**PR quality:**

- `[BLOCKING]` **Focused diff:** Changes limited to analysis scope; no unrelated formatting or restructuring. (Reinforced by the Minimum-net-diff top item.)
- `[BLOCKING]` **Self-contained:** The analysis can be understood from the code and its documentation without external context.
- `[ADVISORY]` **Clean commits:** Commit history is logical and messages are descriptive.
- `[ADVISORY]` **Appropriate tolerances** documented and economically reasonable (where drift tests exist).

**Documentation currency:**

- `[BLOCKING]` **Module CLAUDE.md / AGENTS.md / README.md** do not reference files, functions, outputs, or methodology that no longer exist or have been superseded by the refactored code.
- `[BLOCKING]` **No stale output lists:** Every output file mentioned in documentation is actually produced by the current code.
- `[BLOCKING]` **Dates and version claims** ("as of ...") reflect the current commit, not a prior state.

**Project Doc Audit:**

- `[BLOCKING]` Walk up from every file in the diff `<BASE_SHA>..<HEAD_SHA>` to the repo root; collect every `CLAUDE.md` / `AGENTS.md` / `README.md` encountered; always also check the repo-root `README.md` and root `CLAUDE.md`. For each: update stale claims, add new patterns at the correct level, do not duplicate parent-level content, create missing `CLAUDE.md` + `AGENTS.md` pair for new module directories. Do **not** propagate upward for the sake of it: leave docs above the affected area alone unless something in them is stale. Full walk-up algorithm in `references/codebase-integration.md` §Project Doc Audit.

---

### Merge Quality

Load `references/merge-quality.md` for the two-commit commit-message templates and the full integration-map format.

**Intent preservation:**

- `[BLOCKING]` **Incoming intent understood.** Correctly identified what the incoming changes were trying to accomplish — read commits and diffs to understand WHY, not just WHAT.
- `[BLOCKING]` **Current branch preserved** where intended.
- `[BLOCKING]` **No silent losses.** No changes from either side silently dropped without justification.
- `[ADVISORY]` **Synthesis coherent.** Where both sides were combined, result is logically consistent.

**Research integrity:**

- `[BLOCKING]` **No silent result changes.** Analysis outputs are either unchanged, or the change was flagged to the user.
- `[BLOCKING]` **Variable definitions consistent** across merged code.
- `[BLOCKING]` **Sample construction preserved.** Sample filters and data sources are correct in the merged result.
- `[BLOCKING]` **User decisions implemented correctly** (Tier 3) — the researcher's decisions on research-meaningful conflicts were implemented as stated.

**Two-commit structure (templates in reference):**

- `[BLOCKING]` **Commit 1 (mechanical merge):** lowest-assumption reconciliation; preserves information from both sides; restores a buildable, runnable state; no opportunistic cleanup or reinterpretation.
- `[BLOCKING]` **Commit 2 (integration):** adapts code, docs, tests, and generated artifacts so the branch incorporates the incoming objective; rewrites stale names, labels, paths, and references; regenerates derived outputs from merged source code (not hand-edited).

**Research-Meaningful Escalation (Tier 3) — verbatim:**

> These conflicts **MUST** be flagged for the researcher. Ask via `AskUserQuestion` (plain text if unavailable) — when the resolution has a closed set of options (`--ours`, `--theirs`, synthesize, regenerate, roll back), pass them as question options; when it's methodology-level, ask in free-form prose. Mark such rows as `ASK USER` in the integration map while still open, and replace with the researcher's resolution once it comes back. Every answer is a user decision and must be logged per `handoff-doc` §User Decisions Log before the resolution is committed — into `PLAN.md`'s `## Decisions` section if the branch still has `PLAN.md`, otherwise into the integration commit message (which becomes the record of record once `PLAN.md` is gone).
>
> - **Variable definitions:** Incoming changes redefine a variable used in this branch's analysis
> - **Sample construction:** Incoming changes alter sample filters or data sources
> - **Econometric specifications:** Incoming changes alter model specifications, control variables, or clustering
> - **Data processing:** Incoming changes alter merge logic, data cleaning, or transformations
> - **Results:** Incoming changes affect analysis outputs
>
> **Never:**
> - Silently change analysis results
> - Choose ours/theirs for research-meaningful conflicts
> - Remove data discipline artifacts
> - Judge whether a methodology choice is correct

**Integration map:**

- `[BLOCKING]` For each conflict area, document file + location, classification (analysis / data-processing / methodology / infrastructure / docs / generated / config), decision (keep-incoming / keep-current / synthesize / regenerate / ASK USER), and rationale. Present user decisions in terms of **intent and consequences**, not raw diffs.

**Verification:**

- `[BLOCKING]` **Drift tests pass** (or failures appropriately escalated to user per the Drift-Test Integrity Red Flags above).
- `[BLOCKING]` **No stale references:** Old variable names, file paths, function names updated.
- `[BLOCKING]` **Pipeline runs** (if applicable): End-to-end pipeline produces expected outputs.
- `[ADVISORY]` **No outdated labels:** Comments, docstrings, and documentation reflect the merged state.

**Data discipline:**

- `[BLOCKING]` Data discipline artifacts (description steps, row counts, validation checks, documentation cells) preserved through the merge. See loaded `econ-data-analysis` for the full list of artifacts.

---

## Implementer Self-Check (Before Every Commit)

The Minimum-net-diff top item is enforced by a concrete pre-commit procedure. Run it before every commit on the integration branch:

1. **Compute the cumulative diff.** `git diff <merge-base>..HEAD` where `<merge-base>` is the merge base the integration is targeting (e.g., `$(git merge-base HEAD main)` or whatever the workflow specifies).
2. **Review every hunk** against the three disciplines' checklists. For each hunk, ask: *which `[BLOCKING]` or `[ADVISORY]` item justifies this change?* A hunk may be tied to drift-test preservation, codebase-convention fit, handoff-doc coherence, documentation currency, or an explicit item in the integration map.
3. **Any hunk without a justification is out of scope.** Revert it, OR re-justify it by adding the underlying need to the integration map (and the commit message) so the reviewer can check the same evidence.
4. **Stage only files you touched this turn** (per `superRA:using-superRA` §Commit Hygiene); `git diff --cached` before `git commit`.

The verify reviewer runs the same `git diff <merge-base>..HEAD` as evidence and walks each hunk through the same checklist. No separate reviewer-only document — same checklist, two perspectives.

---

## Integration

**Used by workflow skills:**
- **`superRA:integration-workflow`** — Dispatches drift-test creation and review (Drift-Test Integrity section) and the integration review → refactor loop (Codebase Integration section).
- **`superRA:merge-workflow`** — Dispatches post-merge integration review and refactoring (Codebase Integration section) during the refactor-review loop triggered by drift-test failure or reviewer REVISE.
- **`superRA:semantic-merge`** — Dispatches merge proposer (Merge Quality section) and merge reviewer (Merge Quality section) for tier classification and conflict resolution.

**Auto-loaded alongside:**
- **`superRA:econ-data-analysis`** — Data discipline (loaded by `implementer` / `reviewer` agents whenever the stage involves analysis code, per the `superRA:using-superRA` §Skill-Load Manifest); the `implementation` row also loads `econ-data-analysis/references/notebook-format.md` for notebook formatting.
