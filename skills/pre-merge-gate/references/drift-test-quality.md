# Drift Test Quality Standards

Shared domain reference for drift test creation and review. Both the implementer (test creator) and reviewer use this checklist.

## Coverage

- [ ] Every user-confirmed key result has at least one test
- [ ] Main findings (coefficients, magnitudes, significance) tested
- [ ] Sample statistics (observation counts, unique entities) tested where they define the analysis scope
- [ ] No key result skipped or left unprotected
- [ ] Focus on KEY results — findings that define analysis conclusions, not every intermediate number

## Tolerance Calibration

Set tolerances based on **economic reasoning**, not arbitrary thresholds.

**Point estimates** (coefficients, means, portfolio returns):
- Allow minor variation from data ordering, floating-point arithmetic, rounding
- Typical tolerance: 1-5% of estimate magnitude, or a few units in the last reported decimal place

**Standard errors:**
- Wider tolerance than point estimates — sensitive to small changes in sample composition, clustering, numerical precision
- Typical tolerance: 5-10% of the standard error

**Counts and categoricals** (observations, firms, periods):
- Exact or near-exact — should not change unless sample construction changes
- Tolerance: 0 or very small integer

**Signs and significance:**
- Write directional tests ("coefficient is positive", "t-statistic exceeds 1.96") in addition to magnitude tests
- These catch the most important drift — sign flip or significance loss

**Too tight** → false positives on harmless changes (merge order, floating-point platform differences).
**Too loose** → misses real drift. Use economic judgment.

**Document every tolerance choice** with a comment explaining why:
```
# Coefficient on market_cap: 0.035 +/- 0.002
# Tolerance: ~5% of estimate. Allows for floating-point variation
# in OLS solver but catches meaningful coefficient drift.
```

## Independence

- [ ] Tests can run without re-executing the full analysis pipeline
- [ ] Tests load from saved outputs (files, serialized objects)
- [ ] Test file is self-contained and executable on its own
- [ ] Dependencies are minimal and clearly stated

## Clarity

- [ ] Test names describe what result they protect (e.g., `test_market_cap_coefficient_sign_and_magnitude`)
- [ ] Tests grouped logically (main regression results together, sample statistics together)
- [ ] Header comment explains the analysis being protected and when tests were created
- [ ] A new contributor could understand what each test guards

## Robustness

- [ ] Tests would not break from irrelevant changes (file moves, comment edits, import reordering)
- [ ] Tests reference stable output locations
- [ ] Floating-point comparisons use appropriate tolerance functions (`pytest.approx`, `isapprox`), not exact equality

## Test Format

Follow the project's testing conventions:
- Python: pytest in `tests/` directory
- Julia: Test module in `test/` directory
- Match naming and structure patterns of existing tests
- If no existing tests: use standard framework conventions
