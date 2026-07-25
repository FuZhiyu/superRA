---
title: "Replace Zotero CLI Prose Oracles"
status: revise
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

## Review Notes

1. **MAJOR** — The suite does not protect the stated ordering invariant that a
   missing draft or marker leaves the master bibliography unchanged. The CLI
   guard cases snapshot the bibliography only for failures that occur before
   client construction
   ([test-zotero-tool.sh:279-310](../../../../tests/test-zotero-tool.sh#L279-L310)),
   while the missing-draft and missing-marker checks call only
   `check_draft_target` in isolation
   ([test-zotero-tool.sh:368-400](../../../../tests/test-zotero-tool.sh#L368-L400)).
   Moving `sync_bib` ahead of `check_draft_target` in `cmd_cite` would therefore
   leave all 26 checks green while violating the objective
   ([zotero_tool.py:848-876](../../../../skills/zotero-paper-reader/scripts/zotero_tool.py#L848-L876)).
   Add a credential-free handler-level probe with stubbed Zotero resolution that
   exercises missing-draft and missing-marker failures and verifies the
   bibliography and draft targets remain byte-for-byte unchanged.

2. **MAJOR** — The `Notes/.env` no-secret check never exercises the new redaction
   path: `health` sees the fake credentials as configured and neither its
   success JSON nor its diagnostics contain the key to redact
   ([test-zotero-tool.sh:196-225](../../../../tests/test-zotero-tool.sh#L196-L225)).
   Only the environment-variable branch injects a secret into an exception
   message
   ([test-zotero-tool.sh:402-419](../../../../tests/test-zotero-tool.sh#L402-L419)).
   Removing the `.env` lookup from `redact_secrets` would thus keep the suite
   green despite invalidating the claimed protection
   ([zotero_tool.py:87-96](../../../../skills/zotero-paper-reader/scripts/zotero_tool.py#L87-L96)).
   Add a deterministic failure whose exception text contains an API key loaded
   solely from a temporary `Notes/.env`, then assert the JSON identity and the
   key's absence from both streams.

3. **MINOR** — The newly stable `ItemNotFoundError` / `item_not_found` identity
   is not covered by either a CLI or unit assertion
   ([zotero_tool.py:71-72](../../../../skills/zotero-paper-reader/scripts/zotero_tool.py#L71-L72),
   [zotero_tool.py:750-762](../../../../skills/zotero-paper-reader/scripts/zotero_tool.py#L750-L762)).
   Add a credential-free `select_item_keys` probe with a missing DOI so this
   structural error identity cannot drift unnoticed.
