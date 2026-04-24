# Drift Test Quality Standards

Shared reference for drift-test creation and review. Implementer (test creator) and reviewer both walk the gated checklist at the bottom; the how-to sections above give procedures, worked examples, and Red Flags rationale the checklist encodes. Loadable by anyone writing or reviewing a drift/regression test.

---

## How-To

### Tolerance calibration

Tolerance calibration is domain-specific — reasonable magnitudes for drift depend on what the numbers mean. For data-analysis work, the worked rubric (point estimates, standard errors, counts, signs/significance, with economic-reasoning examples) lives in `econ-data-analysis/references/integrate-drift-tests.md` §Tolerance Conventions for Econ Results.

### Red-green verification cycle

A drift test that passes once is not verified — it might always pass, regardless of the condition it claims to protect. Verify every drift or regression test with the red-green cycle before committing it:

```
1. Write the test against the current (correct) output.
2. Run it — MUST PASS (green).
3. Revert the fix / perturb the input the test protects.
4. Run it — MUST FAIL (red).
5. Restore the fix / input.
6. Run it — MUST PASS again (green).
```

A test that does not turn red on step 4 is not actually guarding the result — it is a passing no-op. "I've written a regression test" without the red-green cycle is not evidence the test works.

### Test format conventions

Follow the project's testing conventions:
- Python: pytest in `tests/` directory
- Julia: Test module in `test/` directory
- Match naming and structure patterns of existing tests
- If no existing tests: use standard framework conventions

### Cross-cutting Red Flags — drift test integrity

These rules apply wherever drift tests are in play — creation, refactor, post-merge verification, and any `semantic-merge` operation.

**Never:**
- **Silently update drift test expectations for meaningful result changes.** A test failure after a refactor, merge, or rebase means one of three things: (a) the change broke something and must be fixed, (b) the change revealed a tolerance too tight and must be justified with economic reasoning and an `AskUserQuestion` confirmation from the researcher, or (c) the change meaningfully shifted a result, which is a research conversation with the researcher — surface it via `AskUserQuestion` (plain text fallback when unavailable), log the answer per `handoff-doc` §User Decisions Log, and commit the log entry before updating the expectation. Never a silent expectation bump.
- **Proceed past failing drift tests without assessment.** Failing tests block the workflow until explicitly adjudicated.
- **Remove or weaken existing drift tests during refactoring or merge integration.** Tests are part of the analysis contract.
- **Treat the drift tests as the only safety net.** They protect key results; they do not replace the one-pass review or the data-discipline protocol.

When a drift test fails: read the cited output, classify the failure, and either fix, justify, or escalate. Orchestrator discipline in `superRA:agent-orchestration` §Handling Reviewer Feedback (when working inside superRA).

---

## Gated Checklist

Walk every item. `[BLOCKING]` items must be satisfied for the reviewer to return APPROVE; `[ADVISORY]` items MAY be flagged as MINOR but do not block APPROVE. Implementer walks this as self-check before commit; reviewer walks the same items as verification.

**Coverage:**

- `[BLOCKING]` Every user-confirmed key result has at least one test — main findings (coefficients, magnitudes, significance), sample statistics where they define scope.
- `[BLOCKING]` No key result skipped or left unprotected.
- `[ADVISORY]` Focus on KEY results — findings that define analysis conclusions, not every intermediate number.

**Tolerance calibration (domain-specific; worked examples in the domain reference — for data analysis see `econ-data-analysis/references/integrate-drift-tests.md` §Tolerance Conventions for Econ Results):**

- `[BLOCKING]` Tolerances matched to the type of quantity and scaled by domain reasoning. Too tight → false positives on harmless changes; too loose → misses real drift.
- `[BLOCKING]` Every tolerance choice documented with a comment explaining the domain reasoning, not a number-pulled-from-the-air justification.

**Independence:**

- `[BLOCKING]` Tests run without re-executing the full analysis pipeline — load from saved outputs.
- `[BLOCKING]` Test file is self-contained and executable on its own.
- `[ADVISORY]` Dependencies are minimal and clearly stated.

**Clarity and robustness:**

- `[BLOCKING]` Test names describe what result they protect (e.g., `test_market_cap_coefficient_sign_and_magnitude`).
- `[BLOCKING]` Floating-point comparisons use tolerance functions (`pytest.approx`, `isapprox`), not exact equality.
- `[ADVISORY]` Tests grouped logically; header comment explains what they protect and when they were created.
- `[ADVISORY]` Tests reference stable output locations; would not break from irrelevant changes (file moves, comment edits, import reordering).

**Red-green verification (procedure in §How-To → Red-green verification cycle):**

- `[BLOCKING]` Every drift / regression test verified with the red-green cycle before committing. A test that does not turn red on perturbation is a passing no-op.

**Test format (conventions in §How-To → Test format conventions):**

- `[BLOCKING]` Project testing conventions followed (pytest in `tests/` for Python; Test module in `test/` for Julia; match existing structure).

**Cross-cutting Red Flags (rationale and full prose in §How-To → Cross-cutting Red Flags):**

- `[BLOCKING]` None of the four "Never" items in §How-To → Cross-cutting Red Flags have been violated (silent expectation bump, proceeding past failing tests, removing/weakening tests during refactor or merge, treating tests as the only safety net).
