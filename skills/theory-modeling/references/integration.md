# Integration Discipline for Theory Modeling

> This reference is the single source of truth for theory-modeling
> integration discipline at the `integration` stage. The implementer
> walks it as pre-handoff self-check; the reviewer walks it as
> verification criteria. Same content, two perspectives - no drift
> possible. `[BLOCKING]` items must be fixed to earn APPROVE;
> `[ADVISORY]` items are suggestions the reviewer MAY flag as MINOR and
> do not block APPROVE. The verdict protocol is the same as
> `theory-modeling/SKILL.md` `## The Four Gates` - two verdicts
> (`APPROVE` / `REVISE`).

Generic cross-cutting code-integration concerns (naming consistency,
utility reuse, PR-friendly diffs, documentation currency) live in
`refactor-and-integrate/SKILL.md`. Load both skills at the
`integration` stage - this one owns the theory-modeling-specific gates;
the generic file owns the cross-cutting code-quality gates.

## Consistency with the model and codebase

- `[BLOCKING]` **No duplicate notation systems for the same object.** If the codebase or project docs already use a symbol for an economic object, reuse it or document the mapping explicitly.
- `[BLOCKING]` **Assumption-map consistency.** Signs, domains, timing, information structure, normalizations, approximation points, and equilibrium concepts align across the derivation, code, and docs - or the deviation is documented with reason.
- `[BLOCKING]` **Statement-result consistency.** Theorem, lemma, proposition, or claim text refers to the same objects and cases that the derivation and numerical checks actually establish.
- `[BLOCKING]` **Document-code consistency.** If the model feeds papers, slides, notes, or downstream artifacts in the repo, reconcile numerical and methodological inconsistencies between the refactored code and those artifacts. If reconciliation is out of scope, flag the gap in `RESULTS.md`.

## Derivation discipline preserved through refactoring

**Refactored modeling work must be re-validated, not just carried
forward.** Refactoring can silently change assumptions, branch choices,
solver defaults, equation rendering, or which parameter set is used for
verification.

- `[BLOCKING]` **Defined objects and assumptions survive the refactor.** The refactored code and notes still name the primitives, endogenous objects, and active assumptions before using them.
- `[BLOCKING]` **Step-by-step derivation survives.** Algebraic steps, case conditions, and justification notes are still auditable; they were not collapsed into opaque prose or code.
- `[BLOCKING]` **Verification checks survive.** Substitution checks, limiting cases, and simple numerical examples from the original work are present in the refactored code or notes and were rerun successfully.
- `[BLOCKING]` **Drift tests pass post-refactor.** Where drift tests exist, they pass on the refactored work; failures are adjudicated per `references/integrate-drift-tests.md`, never silenced by changing expectations without explanation.
- `[BLOCKING]` **Rendered markdown/LaTeX describes what the refactored code actually does.** Equation blocks, symbols, and case labels match the live derivation and numerical outputs.
- `[BLOCKING]` **No derivation-discipline artifact has been deleted.** Definitions, assumptions, verification notes, and renderable math blocks may be reorganized, but they are not silently dropped.
- `[BLOCKING]` **Stated intuition for new symbols survives.** Every notation entry whose original work carried an intuition or mnemonic (per `SKILL.md` §Objects & Notation) still carries that intuition in the refactored notes — not collapsed into opaque prose or a bare code comment.
- `[BLOCKING]` **Assumption interpretations survive.** Every assumption whose original work carried a plain-language interpretation (per `SKILL.md` §Assumptions) still carries that interpretation in the refactored notes — not reduced to a math restriction without the economic reading, and not silently merged away when assumptions are consolidated.
- `[BLOCKING]` **Per-step reasons survive.** Every non-trivial derivation step whose original work carried both the technical rule and a one-sentence reason for invoking it (per `SKILL.md` §Derivations) still carries both in the refactored notes — mechanical rule-labels without a reason, or reasons silently dropped during consolidation, are REVISE.

## Utility reuse and documented deviations

- `[BLOCKING]` **Reuse the existing markdown/rendering utility.** Human-facing markdown with equations, tables, or figures routes through `superRA:report-in-markdown`; do not invent a parallel rendering utility or formatting convention.
- `[BLOCKING]` **Document notation changes.** Any intentional rename or consolidation of symbols carries an explicit old-to-new mapping so downstream docs and readers can follow it.
- `[BLOCKING]` **Document strengthened assumptions.** If a refactor reveals that a result requires stronger primitive restrictions than previously stated, record the new restriction, where it enters, and why it is needed.
- `[ADVISORY]` **Leave migration pointers when consolidating helpers.** If symbolic or numerical helper code moves to a shared location and older files still reference the old location, leave a one-line pointer so follow-on work does not silently fork the old path.

## Reviewer verdict protocol

Verdict protocol follows the active reviewer role; walk this checklist alongside `refactor-and-integrate/SKILL.md`.
