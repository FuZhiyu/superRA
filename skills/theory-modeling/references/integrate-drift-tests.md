# Drift Tests for Theory-Modeling Results

Load during Protect when preparing selected drift tests for a theory/modeling project.

---

## Identifying Key Results from Task Results

Drift tests protect **headline findings**, not every line of scratch algebra. Extract candidates from task `## Results` sections first.

**Strong candidates** (get a test):
- closed-form policy rules, value functions, equilibrium mappings, or fixed-point identities the final argument depends on
- theorem claims and comparative-statics signs driving the paper's interpretation
- calibrated or worked-example numeric values appearing in a headline table, figure, or markdown result block
- residual checks that a reported solution satisfies first-order conditions, feasibility constraints, or equilibrium conditions
- any result the researcher would read aloud when presenting the model

**Weak candidates** (usually skip):
- intermediate algebraic rewrites — stepping stones to a final identity
- notation-only rewrites leaving the underlying object unchanged
- exploratory parameter sweeps outside the reported findings
- formatting details of rendered equations

## Tolerance Conventions for Modeling Results

Set tolerances from **the mathematical object being protected**, not arbitrary defaults.

| Result type | Typical tolerance | Rationale |
|---|---|---|
| Symbolic identities | Exact after canonical simplification; if equivalent forms differ syntactically, evaluate equivalence on approved parameter draws | The object should be invariant even if the printed form changes |
| Comparative-statics signs / rankings | Exact directional check | Sign flips are the failure mode the test most needs to catch |
| Residuals for FOCs, constraints, or fixed points | Absolute residual on the order of `1e-8` to `1e-6`, or a scale-aware equivalent | Allows solver noise while catching economically meaningful failure |
| Reported numeric values from a baseline example | Relative tolerance around `1e-6` to `1e-4`, depending on conditioning and solver stability | Protects the published value without overfitting to floating-point noise |
| Thresholds or regime boundaries | Check a small neighborhood on both sides of the threshold | Branch-selection drift often hides exactly at regime changes |

A tolerance looser than this table: justify it in the test and in the task's `## Results`.

---

## Theory-Modeling-Specific Failure Modes

Four common causes when a drift test fails after a refactor or merge:

1. **Hidden-assumption drift.** The result now needs a stronger positivity, boundedness, interiority, or regularity assumption than the map states. Fix: update the map and the derivation together, or revert the step that introduced the stronger requirement.

2. **Normalization drift.** The same economics written under a different numeraire, scale, or approximation point. Fix: canonicalize the protected object and test the invariant economic quantity, not the surface notation.

3. **Branch-selection drift.** A solver or symbolic simplification picks a different root, corner, or equilibrium branch. Fix: make the branch rule explicit and test it directly.

4. **Verification-case drift.** The parameter baseline or special case for the numerical check moved off the documented example. Fix: keep the documented parameter set under version control and call it from the test instead of retyping it.

A failure matching one of these is usually the refactor, not the result — confirm before updating anything. A failure matching none: escalate to the researcher — possibly a real model change, not a tolerance issue.

---

## Generic Integrity Red Flags

See `result-protection/references/drift-test-quality.md` §Cross-cutting Red Flags — drift test integrity.
