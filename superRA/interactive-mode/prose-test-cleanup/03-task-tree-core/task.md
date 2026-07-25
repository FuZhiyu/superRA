---
title: "Replace Task-Tree Core Prose Oracles"
status: implemented
depends_on:  []
---

## Objective

Replace task-tree core and CLI tests that assert rendered diagnostics, warnings, labels, or Finding.message prose with stable codes and structured fields plus observable exit codes, mutations, filesystem state, parser wiring, and call arguments. Preserve rule IDs as structured identities. Success: task-tree core exposes structured finding/error data, human text is presentation-only, and targeted/full task-tree tests pass with red-green evidence.

## Planner Guidance

Own test_cli.py, test_task_tree.py, _task_validate.py, task_check.py, and directly related core diagnostic producers. Do not touch dashboard/comment presentation, hook adapter, or other cleanup children.

## Results

- Replaced raw validation strings with structured findings carrying stable
  `code`, `subject`, `actual`, `path`, and `related_nodes` fields. String
  conversion remains available only for human-facing warning presentation
  ([`_task_validate.py`](../../../../skills/task-tree/scripts/_task_validate.py#L18-L51)).
- Extended task-check findings and JSON output with the same structured
  operands for invalid/stale status fields, missing/archived/postponed
  dependencies, cycles, rollup mismatches, and lingering Sync Impact sections.
  Rollup mismatches expose both stored `actual` and computed `expected` status.
  The original `task_path` JSON key remains as a compatibility alias for
  `path`; human `message` text remains presentation-only
  ([`task_check.py`](../../../../skills/task-tree/scripts/task_check.py#L44-L82)).
- Replaced core CLI and task-tree prose oracles with exit codes, unchanged or
  mutated filesystem/task state, parser registration, invoked module arguments,
  structured JSON, rule codes, paths, and related-node identities
  ([`test_cli.py`](../../../../skills/task-tree/scripts/test_cli.py#L150-L310),
  [`test_task_tree.py`](../../../../skills/task-tree/scripts/test_task_tree.py#L1657-L1827),
  [`test_task_tree.py`](../../../../skills/task-tree/scripts/test_task_tree.py#L3378-L3729)).
  Dashboard/comment and hook-adapter presentation tests were left to their
  assigned cleanup tasks.
- Red evidence: the focused structured-contract run failed as designed with
  23 failures and 21 passes because validation still returned strings and
  `Finding` lacked the new fields. Green evidence: the focused run passed 44
  tests; the two owned modules passed 308 tests; the full task-tree suite passed
  723 tests with zero failures. On the review fix, the two focused rollup/JSON
  tests first failed on the missing `expected` field, then passed 2 tests; the
  owned modules passed 308 tests and the full task-tree suite passed 723 tests.

## Review Notes

1. **MAJOR** — [`task_check.py:241-253`](../../../../skills/task-tree/scripts/task_check.py#L241-L253): the `rollup.mismatch` finding exposes the stored status as `actual`, but the computed expected status remains available only inside `message`. This leaves a semantic operand in presentation prose, contrary to the objective that human text be presentation-only, and forces JSON consumers either to parse wording or re-walk the tree to learn the expected value. Add a structured expected value (or an equivalent structured actual/expected pair), serialize it without removing the legacy keys, and assert it in the rollup and JSON contract tests.
   → implemented: added and serialized `expected`, populated it from the computed rollup, and asserted the value plus JSON schema while retaining `task_path` and all other legacy keys ([`task_check.py`](../../../../skills/task-tree/scripts/task_check.py#L44-L79), [`test_task_tree.py`](../../../../skills/task-tree/scripts/test_task_tree.py#L3543-L3615)).
2. **MINOR** — [`_task_validate.py:18-26`](../../../../skills/task-tree/scripts/_task_validate.py#L18-L26): `ValidationFinding` is only shallowly frozen because `actual: Any` can hold mutable lists or mappings (for example, a malformed `depends_on` list), so the Results description of the findings as immutable is not generally true. Either canonicalize mutable operands into immutable values or narrow the Results claim.
   → implemented: narrowed the Results description to “structured findings,” matching the shallowly frozen data model without adding unneeded operand canonicalization ([`task.md`](task.md#L17-L20)).
