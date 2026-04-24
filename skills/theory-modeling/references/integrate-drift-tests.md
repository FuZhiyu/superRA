# Drift Tests for Theory-Modeling Results

Load at the **INTEGRATE phase** when preparing drift tests that guard a
theory/modeling project's key results before merge.
`integration-workflow` Phase A invokes this reference alongside the
quality checklist.

This reference answers the theory/modeling-specific questions:

1. **What should a drift test for this project actually protect?**
2. **What are the conventions for symbolic and numerical tolerances?**
3. **How do I pull candidate invariants out of `RESULTS.md`?**

For the implementation-level quality checklist (coverage,
independence, clarity, robustness, test format, cross-cutting
integrity Red Flags), load
`result-protection/references/drift-test-quality.md`. This file
and that checklist are both read at drift-test creation and review.

---

## Why Drift Tests Are Part of Theory-Modeling Discipline

Model results drift silently too. A refactor can switch a branch of a
closed-form solution, strengthen an unstated parameter restriction,
change a normalization, or move a numerical baseline away from the case
the derivation was claiming to illustrate. Most of these failures still
"look right" in prose. Drift tests catch them.

The Iron Law protects the derivation from unnamed objects and unstated
assumptions during implementation. Drift tests protect the finalized
model from hidden algebraic, numerical, and normalization changes after
implementation is complete. They are the integration-phase analogue.

---

## Identifying Key Results from `RESULTS.md`

Drift tests should protect **headline findings**, not every intermediate
line of scratch algebra. Before writing tests, read `RESULTS.md` and
extract candidates.

**Strong candidates** (should usually get a test):
- closed-form policy rules, value functions, equilibrium mappings, or fixed-point identities that the final argument depends on
- theorem claims and comparative-statics signs that drive the paper's interpretation
- calibrated or worked-example numeric values that appear in a headline table, figure, or markdown result block
- residual checks showing that a reported solution satisfies first-order conditions, feasibility constraints, or equilibrium conditions
- any result the researcher would read aloud when presenting the model

**Weak candidates** (probably skip):
- intermediate algebraic rewrites that are only stepping stones to a final identity
- notation-only rewrites that do not change the underlying object
- exploratory parameter sweeps that are not part of the reported findings
- formatting details of rendered equations

**Always ask the researcher to confirm the candidate list** before
writing tests. Drift-test coverage is a researcher-owned decision
because it encodes what counts as a key result.

---

## Tolerance Conventions for Modeling Results

Set tolerances based on **the mathematical object being protected**, not
on arbitrary defaults.

| Result type | Typical tolerance | Rationale |
|---|---|---|
| Symbolic identities | Exact after canonical simplification; if equivalent forms differ syntactically, evaluate equivalence on approved parameter draws | The object should be invariant even if the printed form changes |
| Comparative-statics signs / rankings | Exact directional check | Sign flips are the failure mode the test most needs to catch |
| Residuals for FOCs, constraints, or fixed points | Absolute residual on the order of `1e-8` to `1e-6`, or a scale-aware equivalent | Allows solver noise while catching economically meaningful failure |
| Reported numeric values from a baseline example | Relative tolerance around `1e-6` to `1e-4`, depending on conditioning and solver stability | Protects the published value without overfitting to floating-point noise |
| Thresholds or regime boundaries | Check a small neighborhood on both sides of the threshold | Branch-selection drift often hides exactly at regime changes |

If a tolerance needs to be looser than this table suggests, justify it
in the test and in `RESULTS.md`.

---

## Theory-Modeling-Specific Failure Modes

When a drift test fails after a refactor or merge, four common causes in
modeling code and notes are:

1. **Hidden-assumption drift.** The result now needs a stronger
   positivity, boundedness, interiority, or regularity assumption than
   the assumption map currently states. Fix: update the map and the
   derivation together, or revert the step that introduced the stronger
   requirement.

2. **Normalization drift.** The same economics is written under a
   different numeraire, scale, or approximation point. Fix: canonicalize
   the protected object and test the invariant economic quantity, not
   the surface notation.

3. **Branch-selection drift.** A solver or symbolic simplification now
   picks a different root, corner, or equilibrium branch. Fix: make the
   branch rule explicit and test it directly.

4. **Verification-case drift.** The parameter baseline or special case
   used for the numerical check moved away from the documented example.
   Fix: keep the documented parameter set under version control and call
   it from the test instead of retyping it.

If a failure matches one of these, the drift test is usually correct and
the refactor is usually the cause. If the failure does not match any of
them, escalate to the researcher - it may be a real model change rather
than a tolerance issue.

---

## Cross-Cutting Integrity Rules

The Red Flags that protect drift-test integrity during creation,
refactor, merge, and semantic-merge live in
`result-protection/references/drift-test-quality.md`
`# Cross-cutting Red Flags - drift test integrity`. They apply wherever
drift tests are in play. Do not restate them here; load that section and
follow it.
