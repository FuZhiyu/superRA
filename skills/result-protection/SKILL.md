---
name: result-protection
description: Protect key research results from unintended drift. Use when selecting, creating, refreshing, or reviewing regression or drift tests for important outputs.
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
