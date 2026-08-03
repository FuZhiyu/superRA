# Drift Test Quality Standards

Drift-test creation and review. The implementer walks the gated checklist below; the reviewer walks what its focus covers.

## How-To

### Tolerance calibration

Tolerance calibration is domain-specific — load the active domain skill's drift-test reference (per its stage-load table) for its conventions.

### Red-green verification cycle

A test that passes once is not verified. Run the red-green cycle on every drift or regression test before committing it:

```
1. Write the test against the current correct output.
2. Run it; it must pass.
3. Perturb the protected input, output, or expectation.
4. Run it; it must fail.
5. Restore the input, output, or expectation.
6. Run it; it must pass again.
```

### Test format conventions

- Python: pytest in `tests/`.
- Julia: `Test` module in `test/`.
- Match existing naming and structure.
- No existing tests: use the language's standard test framework.

### Cross-Cutting Red Flags

These apply wherever drift tests protect key results: Protect, Sync, Integrate, Finish, standalone `semantic-merge`, future maintenance.

**Never:**

- **Silently update expectations for meaningful result changes.** A failure after a refactor, merge, or rebase is one of three: the change broke something and must be fixed; the tolerance is too tight and needs domain justification plus researcher confirmation; the result meaningfully shifted and needs a research conversation. Fold the decision into the relevant task objective before updating expectations.
- **Proceed past failing drift tests without assessment.** Failing tests block the workflow until classified and resolved.
- **Remove or weaken existing drift tests during Sync or Integrate.** Tests are part of the results contract.
- **Treat drift tests as the only safety net.** They protect key results; they never replace review or domain discipline.

## Gated Checklist

`[BLOCKING]` items must pass for approval; `[ADVISORY]` items are recorded and do not block.

**Coverage:**

- `[BLOCKING]` Every result selected for drift-test protection has at least one test.
- `[BLOCKING]` No result selected for drift-test protection is skipped.
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
