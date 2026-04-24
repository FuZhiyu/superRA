# Drift Test Quality Standards

Shared reference for drift-test creation and review. Implementer and reviewer both walk the gated checklist below.

## How-To

### Tolerance calibration

Tolerance calibration is domain-specific. For data-analysis work, load `econ-data-analysis/references/integrate-drift-tests.md` section Tolerance Conventions for Econ Results.

### Red-green verification cycle

A drift test that passes once is not verified. Verify every drift or regression test with the red-green cycle before committing it:

```
1. Write the test against the current correct output.
2. Run it; it must pass.
3. Perturb the protected input, output, or expectation.
4. Run it; it must fail.
5. Restore the input, output, or expectation.
6. Run it; it must pass again.
```

### Test format conventions

Follow the project's testing conventions:

- Python: pytest in `tests/`.
- Julia: `Test` module in `test/`.
- Match existing naming and structure.
- If no tests exist, use the language's standard test framework.

### Cross-Cutting Red Flags

These rules apply wherever drift tests protect key results: Protect, Sync, Integrate, Finish, standalone `semantic-merge`, and future maintenance.

**Never:**

- **Silently update expectations for meaningful result changes.** A failure after a refactor, merge, or rebase means one of three things: the change broke something and must be fixed; the tolerance is too tight and needs domain justification plus researcher confirmation; or the result meaningfully shifted and needs a research conversation. Log the decision per `handoff-doc` User Decisions Log before updating expectations.
- **Proceed past failing drift tests without assessment.** Failing tests block the workflow until classified and resolved.
- **Remove or weaken existing drift tests during Sync or Integrate.** Tests are part of the analysis contract.
- **Treat drift tests as the only safety net.** They protect key results; they do not replace review or domain discipline.

## Gated Checklist

Walk every item. `[BLOCKING]` items must pass for approval; `[ADVISORY]` items may be reported as minor findings.

**Coverage:**

- `[BLOCKING]` Every user-confirmed key result has at least one test.
- `[BLOCKING]` No key result is skipped or left unprotected.
- `[ADVISORY]` Tests focus on findings that define conclusions, not every intermediate number.

**Tolerance calibration:**

- `[BLOCKING]` Tolerances match the quantity and are scaled by domain reasoning.
- `[BLOCKING]` Every tolerance choice is documented with domain reasoning.

**Independence:**

- `[BLOCKING]` Tests run without re-executing the full analysis pipeline; load from saved outputs.
- `[BLOCKING]` Each test file is self-contained and executable on its own.
- `[ADVISORY]` Dependencies are minimal and clearly stated.

**Clarity and robustness:**

- `[BLOCKING]` Test names describe the protected result.
- `[BLOCKING]` Floating-point comparisons use tolerance functions, not exact equality.
- `[ADVISORY]` Tests are grouped logically, with a short header comment naming what they protect.
- `[ADVISORY]` Tests reference stable output locations.

**Red-green verification:**

- `[BLOCKING]` Every drift/regression test was verified with the red-green cycle.

**Project conventions:**

- `[BLOCKING]` Project testing conventions are followed.

**Cross-cutting Red Flags:**

- `[BLOCKING]` None of the four Never items above have been violated.
