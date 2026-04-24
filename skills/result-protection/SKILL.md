---
name: result-protection
description: Utility skill for protecting key research results from unintended changes, especially during integration, branch sync, refactoring, or future maintenance. Use when selecting, creating, refreshing, or reviewing key-result protection; the current/default mechanism is drift or regression tests.
---

# Result Protection

Tool skill for protecting key results from unintended changes. Drift tests are the current/default mechanism.

## References

Load only the reference needed for the protection mechanism in use:

| Reference | Load when |
|---|---|
| `references/drift-test-quality.md` | Writing, refreshing, or reviewing drift/regression tests for key results; always for `Stage: drift-test`. |

For data-analysis result protection, also load `econ-data-analysis/references/integrate-drift-tests.md` for key-result selection, tolerance calibration, and data-analysis failure modes.

## Scope Gate

- `[BLOCKING]` Protect researcher-confirmed key results, not every intermediate number.
- `[BLOCKING]` A protection update that changes expected results requires the same escalation as a meaningful result change.
