---
title: "Setup CLI for Dashboard Artifact Workflow"
status: approved
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
