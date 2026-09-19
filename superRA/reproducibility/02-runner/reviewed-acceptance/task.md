---
title: "Reuse Reviewed Results Without Unnecessary Rebuilds"
status: approved
depends_on: []
---

## Objective

Implement dependency-impact inspection and scoped stale-result acceptance under the [0.5 design](../../attachments/v05-design.md#narrow-dependencies-before-accepting-stale-results). Accepted results are `fresh` for routine use, with durable reasons and evidence accessible through explain/details; successful execution history stays truthful.

- Deliver impact, accept preview/apply, and revoke operations with JSON support and exact target selection. Capture trustworthy baseline evidence for explaining changes, including dirty-source runs, and disclose unavailable historical diffs.
- Make status and ordinary serial/parallel builds agree on accepted freshness. Revalidate immediately before skipping a producer; preserve descendant execution, force scope, failures, output-integrity checks, and atomic records. No-op commands or rewritten successful locks cannot stand in for acceptance.
- Exercise every acceptance, fan-out, cascade, force, failure, sidecar, concurrency, and baseline scenario in the [verification matrix](../../attachments/v05-design.md#verification-and-upgrade), including real pytask runs against the pinned engine. Demonstrate a reviewed shared-helper change skipping one consumer while an independently changed consumer runs.
- Update state/acceptance command and record documentation in the task-tree references after the graph task's changes land. Agent decision discipline belongs to [workflow integration](../../07-workflow-integration/unified-dependency-workflow/task.md).

## Details

- **Ownership:** [_repro_state.py](../../../../skills/task-tree/scripts/_repro_state.py), [repro_run.py](../../../../skills/task-tree/scripts/repro_run.py), an acceptance-record helper if needed, runner tests, and state/acceptance reference sections. The parent's dependency on [graph contract](../../01-section-contract/task.md) supplies the validated effective graph.
- `pytask.lock` stores hashes, not historical source text. A Git revision is useful only when its blobs match the recorded hashes; an arbitrary `git diff HEAD` is not a successful-run comparison.
- Exploration of installed pytask 0.6 found that a setup hook raising `SkippedUnchanged` can avoid state updates without suppressing descendants. Verify this against dry-run, threaded execution, and predecessor failures; ordinary skip/skipif and no-op tasks have unsuitable semantics.
- Capture successful receipts only after product verification. The existing subprocess run record is written before sidecar/stamp completion, so command exit alone is insufficient evidence.
- A sidecar proves only the state it actually encodes. Acceptance needs trustworthy output equality, not merely unchanged arbitrary sidecar text.


## Results

- [Impact and acceptance](../../../../skills/task-tree/scripts/_repro_acceptance.py) expose exact task/step previews, per-changed-node rationale, hashed evidence references, atomic token-checked apply, and scoped revoke. The committed ledger binds successful baseline/output identities without embedding raw research inputs; local source snapshots support verified dirty-source diffs and disclose unavailable history.
- [Engine hooks](../../../../skills/task-tree/scripts/_repro_hooks.py) make valid acceptance `fresh` and skip execution without changing successful locks, check stamps, or actual-run history. Serial/thread builds preserve independently dirty descendants, force scope, predecessor failures, and identical-output cutoff. Verified session-local completion evidence lets an accepted child skip after an upstream rerun with identical output bytes.
- [Runner receipts](../../../../skills/task-tree/scripts/repro_run.py) are captured after product verification, including actual sidecar-backed output digests. Concurrent input or graph-declaration changes fail the attempt; unrelated task prose and active-status rollups do not interrupt execution; failed or interrupted work cannot establish success. Real execution removes that step's acceptance before running, so local cache loss cannot revive a failed override. Mutation coordination uses a local POSIX process lock and atomic record replacement.
- [Behavioral fixtures](../../../../skills/task-tree/scripts/test_repro_acceptance.py) exercise reviewed shared-helper fan-out, deterministic per-consumer configuration cutoff, portable acceptance, exact target expansion, chained acceptance/revoke, missing/changed outputs, arbitrary sidecars, failed forces, dirty-source history, malformed/unavailable evidence, preview/setup races, and source-snapshot privacy. The full task-tree suite passed **1,115 tests, 9 skipped**; final acceptance/runner/CLI/dependency regressions passed **186 tests**, including **47 acceptance scenarios** on pytask 0.6.0. The repository's live-source dependency check and mechanics Markdown integrity checks were clean.
- Mechanics are documented in [commands](../../../../skills/task-tree/references/commands.md#reviewed-acceptance), [the record contract](../../../../skills/task-tree/references/task-file-contract.md#acceptance-and-successful-baseline-records), and [engine integration](../../../../skills/task-tree/references/internals.md#reviewed-reuse-execution). Legacy normal-output locks remain eligible with unavailable source history; a legacy sidecar baseline without a verified actual-output digest needs one successful run of that step.
