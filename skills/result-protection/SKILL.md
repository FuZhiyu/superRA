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
| `references/drift-test-quality.md` | Writing, refreshing, or reviewing drift/regression tests for key results; always for `Stage: protection` when drift/regression tests are the mechanism. |

The active domain skill's stage-load table routes any domain-specific drift-test reference at the `drift-test` (protection) stage; load it per that table.

## Scope Gate

- `[BLOCKING]` Protect researcher-confirmed key results, not every intermediate number.
- `[BLOCKING]` A protection update that changes expected results requires the same escalation as a meaningful result change.
