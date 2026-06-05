---
title: "Setup CLI for Dashboard Artifact Workflow"
status: implemented
depends_on: 
  - 01-workflow-template

tags: []
created: 2026-06-04
---

## Objective

Add a packaged task-system CLI command that installs or updates the dashboard artifact workflow in a target repository. The command must write the rendered template to `.github/workflows/superra-dashboard-artifact.yml` by default, creating `.github/workflows` when needed, and must refuse to overwrite a non-superRA-managed workflow unless the user passes an explicit force flag. It must expose configuration flags for workflow filename, task root path, exported dashboard filename, artifact name prefix, retention days, trigger branch patterns when practical, and whether missing `superRA/` should fail or skip.

The command must be reachable from the existing packaged CLI surface, preferably under `superra dashboard`, and must work when run through the live checkout form: `uv run --project skills/task-system superra ...`. It must print the installed path and the branch-stable artifact naming behavior so users understand where to find the artifact in Actions.

Validation: add CLI tests that install into a temporary repository directory, verify idempotent re-run behavior, verify non-managed overwrite protection, and verify configured flags appear in the generated workflow.

## Planner Guidance

A likely command name is superra dashboard setup-artifact-action or superra dashboard artifact setup. Keep implementation small: template rendering plus managed-file marker plus CLI wiring. Avoid adding a GitHub API client to the setup tool; the generated workflow can own runtime artifact cleanup.

## Results

### Key Findings

- Added `install_workflow()` and `InstallResult` to the dashboard artifact workflow helper, including repository-root containment, managed-file overwrite protection, force overwrite support, and artifact-name preview output.
- Added the packaged CLI command `superra dashboard artifact setup`. It writes `.github/workflows/superra-dashboard-artifact.yml` by default and exposes flags for repository root, workflow path, task root, dashboard output path, artifact prefix, retention days, missing-task-root behavior, force overwrite, and preview ref.
- Added tests for default install, idempotent managed-file reinstall, unmanaged overwrite refusal, force overwrite, and CLI flag propagation into the generated workflow.

### Verification

- `uv run --project skills/task-system --with pytest python -m pytest skills/task-system/scripts/test_task_system.py -k DashboardArtifactWorkflow` — 10 passed.
- `uv run --project skills/task-system --with pytest python -m pytest skills/task-system/scripts/test_task_system.py` — 246 passed, 11 skipped, 1 expected invalid-status warning from the existing diagnostic test.
- `tmpdir=$(mktemp -d); uv run --project skills/task-system superra dashboard artifact setup --repo-root "$tmpdir" --preview-ref Feature/Foo; test -f "$tmpdir/.github/workflows/superra-dashboard-artifact.yml"` — passed and printed the installed workflow path plus branch artifact preview.

## Review Notes

1. [MAJOR] [cli.py:306-347](../../../../../skills/task-system/scripts/cli.py#L306-L347) exposes flags for workflow path, task root, output path, artifact prefix, retention, missing-root behavior, force, and preview ref, but it does not expose the required trigger branch-pattern configuration. The generated workflow remains hard-coded to all branches at [superra-dashboard-artifact.yml:4-8](../../../../../skills/task-system/scripts/templates/superra-dashboard-artifact.yml#L4-L8). The objective asks for trigger branch patterns when practical, and this is a straightforward template/config field rather than an impractical runtime concern. Add a setup flag and workflow config support for one or more branch patterns, keep the default as `"**"`, and cover it in the configured-workflow CLI test.
   → implemented: added `WorkflowConfig.branch_patterns`, template substitution for push branch patterns, repeatable `--branch` setup flag, and CLI/config tests covering `main` plus `analysis/**` ([dashboard_artifact_workflow.py](../../../../../skills/task-system/scripts/dashboard_artifact_workflow.py), [cli.py](../../../../../skills/task-system/scripts/cli.py), [superra-dashboard-artifact.yml](../../../../../skills/task-system/scripts/templates/superra-dashboard-artifact.yml), [test_task_system.py](../../../../../skills/task-system/scripts/test_task_system.py)).

2. [MINOR] [cli.py:128-134](../../../../../skills/task-system/scripts/cli.py#L128-L134) lets `ValueError` and `FileExistsError` from [dashboard_artifact_workflow.py:98-110](../../../../../skills/task-system/scripts/dashboard_artifact_workflow.py#L98-L110) escape as Python tracebacks. The underlying repository-root containment and unmanaged-overwrite protections work, but the task also asks for useful CLI output; `superra dashboard artifact setup --repo-root /tmp/superra-review-probe --workflow-path ../escape.yml` currently prints a traceback instead of a concise `Error: Workflow path escapes repository root: ../escape.yml`. Catch these setup errors, print a short stderr message, and exit non-zero.
   → implemented: `superra dashboard artifact setup` now catches setup `ValueError`/`FileExistsError`, prints `Error: ...` to stderr, exits 1, and has a CLI regression for an escaping workflow path ([cli.py](../../../../../skills/task-system/scripts/cli.py), [test_task_system.py](../../../../../skills/task-system/scripts/test_task_system.py)).
