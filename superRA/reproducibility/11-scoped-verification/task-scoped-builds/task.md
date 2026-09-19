---
title: "Build selected tasks against saved inputs by default"
status: implemented
depends_on: []
---

## Objective

Implement one task/step selection contract for reproduction build, status, and preview: execute only the selected steps by default using existing upstream inputs, expand to upstream producers explicitly, and report scoped success separately from upstream freshness. The [CLI and evidence design](attachments/design.md) defines the contract; existing boundary inputs require neither an override nor successful-build evidence.

- Preserve the complete declared graph, step identities, and existing successful-run evidence. A run boundary never rewrites dependencies or accepts a stale producer as fresh.
- Concurrent edits outside the selected execution contract must not abort a build. Guard selected declarations, resolved execution paths, ownership of consumed/produced artifacts, and actual input bytes; unrelated task creation, statuses, prose, and configuration entries are not invalidation signals.
- Cover the CLI, engine bridge, scoped evidence, task-reader/dashboard reporting, workflow loads and completion gates, documentation, and migration under the design's ownership map. Register executable support for retained results by default, including interactive work and initially unconfigured trees.
- Verify the design's behavioral matrix in disposable fixtures and one isolated existing-project pilot; record actual commands executed, boundary fingerprints, build/status agreement, and unchanged-run latency. No project-wide analysis runs during development of this feature.

## Details

The [CLI and evidence design](attachments/design.md) records the researcher decisions and acceptance matrix. This update keeps selection, execution, and status under one task because their evidence contract crosses the same files. Logical task prerequisites remain separate from executable file edges; initial graph validation and task readiness remain global. Acceptance retains its separate transaction guard.

## Reproduction

```yaml
tier: on-demand
steps:
  - name: task-scoped-builds-check
    kind: check
    cmd: uv run --with pytest --with pyyaml --with 'pytask>=0.6,<0.7' --with pytask-parallel --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts/test_repro_scope.py skills/task-tree/scripts/test_repro_runner.py skills/task-tree/scripts/test_repro_acceptance.py skills/task-tree/scripts/test_task_dependencies.py -q
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
      - skills/task-tree/scripts/conftest.py
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
      - skills/task-tree/scripts/test_repro_scope.py
      - skills/task-tree/scripts/test_repro_runner.py
      - skills/task-tree/scripts/test_repro_acceptance.py
      - skills/task-tree/scripts/test_task_dependencies.py
  - name: task-scoped-builds-pilot
    cmd: uv run --with pytest --with pyyaml --with 'pytask>=0.6,<0.7' --with pytask-parallel python superRA/reproducibility/11-scoped-verification/task-scoped-builds/attachments/pilot.py --output superRA/reproducibility/11-scoped-verification/task-scoped-builds/attachments/pilot-results.json
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
      - skills/task-tree/scripts/conftest.py
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
      - skills/task-tree/scripts/test_dashboard.py
      - skills/task-tree/scripts/tests/test_navigation_projection.py
      - skills/task-tree/scripts/tests/navigation_browser.py
      - skills/task-tree/scripts/templates
      - skills/task-tree/scripts/vendor
      - superRA/reproducibility/04-dashboard-view/scalable-navigation/task.md
      - superRA/reproducibility/11-scoped-verification/task-scoped-builds/attachments/pilot.py
    outs:
      - superRA/reproducibility/11-scoped-verification/task-scoped-builds/attachments/pilot-results.json
```

## Results

Task-scoped builds now execute the selected task/step union against saved inputs, with explicit `--upstream` expansion and `--force` over the resulting scope. The [runner](../../../../skills/task-tree/scripts/repro_run.py) and [scope/evidence helper](../../../../skills/task-tree/scripts/_repro_scope.py) preserve upstream uncertainty in global task-reader/dashboard state and allow unrelated declaration edits during execution. The [command reference](../../../../skills/task-tree/references/commands.md#reproduction) owns syntax and migration.

The [reproducibility skill](../../../../skills/reproducibility/SKILL.md#what-gets-a-step) owns default registration of executable support for retained results; the shared task interface loads it during planning, implementation, and review, including unconfigured trees. Task-tree revision points there, and completion/integration explicitly verify upstream.

- Verification: the full script suite passed **1,159 tests, 34 skipped**. After review fixes, the registered scoped check passed **175 tests**, including missing-sidecar, acceptance/cache-loss, batch-acceptance, and relocation regressions. The final registered check is fresh in this checkout, and the final pilot passed in an isolated source/task copy. Both also passed together in this checkout before the last review fix. A later local pilot retry hit the concurrent dashboard edit’s failing `test_accepted_step_keeps_fresh_state_and_actual_run_details` (17 projection tests passed); that in-flight UI change is outside this task. Harness compatibility, skill validation, and Markdown checks passed. Repository task checking found no errors; two dashboard status-rollup warnings belong to the concurrent dashboard update.
- The [pilot script](attachments/pilot.py) runs an existing registered dashboard projection check in a disposable source/task copy with neutral grouping ancestors. Its generated [record](attachments/pilot-results.json) reports only the selected step executing, unchanged evidence after repeat/dry-run, and warm median build/status times of **0.347 s / 0.062 s**. Regenerate with `task-scoped-builds-pilot` above; declared inputs identify its source. This is an existing repository check, not a research-analysis or browser-capture pilot.
- [Behavioral regressions](../../../../skills/task-tree/scripts/test_repro_scope.py) exercise missing/unverified/changed saved inputs, failed upstream, sidecar byte changes, target unions and collisions, force/preview, frozen selection, and concurrent unrelated/relevant edits with one and two workers. Full-byte boundary receipts are local evidence; a missing sidecar baseline causes the selected consumer to rerun without rebuilding its producer.

The design is hand-authored from the researcher discussion and code inspection. Independent review found two sidecar-boundary issues and a dependent metadata-transition gap; their fixes and regression evidence are ready for narrow re-review; the separate dashboard redesign is outside this change.

## Review Notes

Tier: thorough. Focus: correctness, scope-fidelity.

1. **[BLOCKING] Restoring missing sidecar metadata invalidates unchanged saved-input evidence.** The [dependency fallback](../../../../skills/task-tree/scripts/_repro_state.py#L295-L302) records `saved-input:<digest>` while a sidecar is absent, then returns the sidecar hash after the producer runs. Reproduced by building B from saved A bytes without a sidecar, then building A with identical bytes: B becomes stale despite its unchanged boundary digest and reruns unnecessarily. Preserve dependency equivalence across that metadata transition in build and status, as required by the [identical upstream regeneration contract](attachments/design.md#scoped-freshness-and-upstream-freshness-are-separate-facts). This is a dependent gap in the missing-sidecar fix; the original missing-sidecar and acceptance failures are fixed. → implemented: [metadata-transition regressions](../../../../skills/task-tree/scripts/test_repro_scope.py#L167) preserve full-byte status and unchanged successful locks after an identical producer build, for scoped and upstream execution. Forced execution still runs and records current canonical state. The registered check passes 175 tests.
