---
title: "Replace Zotero CLI Prose Oracles"
status: implemented
depends_on:  []
---

## Objective

Replace Zotero CLI diagnostic-copy assertions with return codes, typed/unit-level error identities, unchanged target state, JSON fields, and no-secret-leak behavior. Preserve command and field inventories as structural contracts. Success: failure behavior is covered independently of human wording.

## Planner Guidance

Own tests/test-zotero-tool.sh and zotero_tool.py only.

## Results

The Zotero CLI now exposes expected failures as typed `ToolError` subclasses
with stable codes and emits a JSON error envelope containing `code`, `type`, and
presentation-only `message` fields. Unexpected exceptions use the stable
`unexpected_error` code, and API keys loaded from either the environment or
`Notes/.env` are redacted before diagnostic serialization
([zotero_tool.py:53-119](../../../../skills/zotero-paper-reader/scripts/zotero_tool.py#L53-L119)).
Invalid libraries, unavailable access modes, missing selections, invalid citation
target choices, absent drafts, and absent markers now retain distinct identities;
draft validation still occurs before bibliography mutation
([zotero_tool.py:191-244](../../../../skills/zotero-paper-reader/scripts/zotero_tool.py#L191-L244),
[zotero_tool.py:815-876](../../../../skills/zotero-paper-reader/scripts/zotero_tool.py#L815-L876)).

The credential-free suite now treats the exact parser command set and health
JSON keys as structural inventories, parses error JSON for code/class identity,
checks exit codes, verifies secret absence, and checks byte-for-byte unchanged
bibliography and draft targets. It no longer matches human diagnostic wording
([test-zotero-tool.sh:56-240](../../../../tests/test-zotero-tool.sh#L56-L240),
[test-zotero-tool.sh:279-430](../../../../tests/test-zotero-tool.sh#L279-L430)).

Verification:

- `bash -n tests/test-zotero-tool.sh` and Python byte-compilation passed.
- Focused unit probes passed for `InvalidLibraryError`,
  `DraftNotFoundError`, their stable codes, and absent-target non-mutation.
- `bash tests/test-zotero-tool.sh` passed all 26 checks.
- Red-green protection was exercised by perturbing the expected
  `access_unavailable` code: the suite failed with 25 passed and 1 failed; after
  restoring the expectation, all 26 checks passed again.
- A scoped search found no remaining Zotero diagnostic-copy matcher. The
  remaining output searches validate only success sentinels or secret absence.

The suite remains credential-free and does not replace the separate live-library
smoke coverage referenced by its full-text test.
