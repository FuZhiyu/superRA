---
title: "Reuse Reviewed Results Without Unnecessary Rebuilds"
status: implemented
depends_on: []
---

## Objective

Provide impact inspection and exact-state acceptance for retained results, including work executed before registration or rerun outside the graph. One `accept` command establishes or replaces a reviewed baseline with a required reason and optional evidence files and per-node notes. Accepted freshness stays distinct from execution evidence.

- Preserve preview/apply concurrency protection, scoped targets, subsequent invalidation, portable records, revoke, serial/threaded build skips, and forced execution. Acceptance never fabricates successful locks, run records, or check stamps; never-run checks require execution.
- Cover first acceptance, changed outputs, saved-input boundaries, sidecars, cache loss, failure/retry, and downstream behavior with real runner fixtures.
- Teach agents to register retained interactive results and accept their reviewed current state without a redundant rerun. Update the owning skill, CLI/record contracts, and public descriptions together.

## Revision Notes

The accepted baseline extends beyond unchanged outputs from a previous runner success. The existing execution history remains authoritative for what the runner actually executed; acceptance records a separate review of current files.

## Details

- **Ownership:** [_repro_state.py](../../../../skills/task-tree/scripts/_repro_state.py), [repro_run.py](../../../../skills/task-tree/scripts/repro_run.py), an acceptance-record helper if needed, runner tests, and state/acceptance reference sections. The parent's dependency on [graph contract](../../01-section-contract/task.md) supplies the validated effective graph.
- `pytask.lock` stores hashes, not historical source text. A Git revision is useful only when its blobs match the recorded hashes; an arbitrary `git diff HEAD` is not a successful-run comparison.
- Exploration of installed pytask 0.6 found that a setup hook raising `SkippedUnchanged` can avoid state updates without suppressing descendants. Verify this against dry-run, threaded execution, and predecessor failures; ordinary skip/skipif and no-op tasks have unsuitable semantics.
- Capture successful receipts only after product verification. The existing subprocess run record is written before sidecar/stamp completion, so command exit alone is insufficient evidence.
- Sidecars do not prove the output bytes. Reviewed baselines hash the actual output; successful-run provenance remains separately available when recorded.


## Reproduction

```yaml
steps:
  - name: reviewed-baseline-regression-check
    kind: check
    cmd: "uv run --with pytest --with 'pytask>=0.6,<0.7' --with pytask-parallel --with pyyaml python -m pytest skills/task-tree/scripts/test_repro_acceptance.py skills/task-tree/scripts/test_repro_runner.py skills/task-tree/scripts/test_repro_scope.py -q -p no:cacheprovider"
    deps:
      - skills/task-tree/scripts/_apply_patch.py
      - skills/task-tree/scripts/_artifacts.py
      - skills/task-tree/scripts/_comments.py
      - skills/task-tree/scripts/_repro.py
      - skills/task-tree/scripts/_repro_acceptance.py
      - skills/task-tree/scripts/_repro_hooks.py
      - skills/task-tree/scripts/_repro_scope.py
      - skills/task-tree/scripts/_repro_state.py
      - skills/task-tree/scripts/_step_links.py
      - skills/task-tree/scripts/_task_dependencies.py
      - skills/task-tree/scripts/_task_io.py
      - skills/task-tree/scripts/_task_snapshot.py
      - skills/task-tree/scripts/_task_validate.py
      - skills/task-tree/scripts/_worktree_discovery.py
      - skills/task-tree/scripts/cli.py
      - skills/task-tree/scripts/dashboard_artifact_workflow.py
      - skills/task-tree/scripts/plan_dashboard.py
      - skills/task-tree/scripts/plan_migrate.py
      - skills/task-tree/scripts/repro_run.py
      - skills/task-tree/scripts/task_add_result.py
      - skills/task-tree/scripts/task_check.py
      - skills/task-tree/scripts/task_comment.py
      - skills/task-tree/scripts/task_create.py
      - skills/task-tree/scripts/task_hook.py
      - skills/task-tree/scripts/task_link.py
      - skills/task-tree/scripts/task_query.py
      - skills/task-tree/scripts/task_read.py
      - skills/task-tree/scripts/task_rename.py
      - skills/task-tree/scripts/task_update.py
      - skills/task-tree/scripts/wrapper_resolver.py
      - skills/task-tree/scripts/test_repro_acceptance.py
      - skills/task-tree/scripts/test_repro_runner.py
      - skills/task-tree/scripts/test_repro_scope.py
```

## Results

[Acceptance](../../../../skills/task-tree/scripts/_repro_acceptance.py) establishes or replaces a reviewed current baseline for newly registered producers, harmless edits, and changed outputs from direct runs. A reason is required; evidence files and per-node notes are optional. Existing legacy records retain their original validation rules.

- **Truthful history:** acceptance writes only its ledger. It leaves successful locks, execution records, receipts, and check stamps intact; initial acceptance creates none of those. Never-run checks, missing files, invalid graphs, and failed/interrupted executions remain blocked.
- **Execution:** ordinary serial/threaded builds skip accepted producers and run outstanding downstream work/checks. Forced attempts remove acceptance and execute. Full output and saved-input fingerprints detect subsequent changes; scoped freshness leaves outside producers unverified. Batch decisions bind selected upstream acceptances and invalidate on revoke.
- **Agent workflow:** [Build and Status](../../../../skills/reproducibility/SKILL.md#build-and-status) routes already-produced interactive results through registration and [reviewed acceptance](../../../../skills/reproducibility/references/rerun-model.md#reviewed-acceptance). [Commands](../../../../skills/task-tree/references/commands.md#reviewed-acceptance), [record schema](../../../../skills/task-tree/references/task-file-contract.md#acceptance-and-successful-baseline-records), and public descriptions match.
- **Validation:** [acceptance, scope, and runner fixtures](../../../../skills/task-tree/scripts/test_repro_acceptance.py) passed **174 tests** through the [registered regression check](#step-reviewed-baseline-regression-check), whose matching status is fresh. The full task-tree suite passed **1,187 tests, 44 skipped**. Skill validation, changed Markdown checks, and dependency/reproduction/link diagnostics passed. Independent review has not run.
