---
title: "Workflow Template and Artifact Contract"
status: approved
depends_on:  []
tags: []
created: 2026-06-04
---

## Objective

Create the GitHub Actions workflow template that exports a branch-scoped superRA dashboard artifact. The template must check out the triggering ref, install/use the task-tree CLI from the repository checkout, run the existing dashboard static export against `superRA/`, and upload the exported dashboard as a GitHub Actions artifact with a branch-stable name. Before upload, it must delete older dashboard artifacts with the same branch-stable name so the repository has at most one current dashboard artifact per branch after a successful run.

The template must define safe defaults: push and `workflow_dispatch` triggers, concurrency scoped by branch/ref to avoid cleanup/upload races, minimal `GITHUB_TOKEN` permissions needed for reading contents and deleting/listing artifacts, failure when `superRA/` is absent unless the setup command exposes an explicit opt-out, and a short retention default that can be configured by the setup command.

Validation: add unit-level or script-level checks that render the template with representative branch names and verify the cleanup/upload contract is present, the artifact name is sanitized, and the export command targets the checked-out branch's `superRA/` tree.

## Planner Guidance

Consider a template file under skills/task-tree/scripts/templates or a task-tree resource path. For deletion, use either actions/github-script or gh api to list repository artifacts and delete entries matching the computed artifact name before actions/upload-artifact runs. Do not depend on upload-artifact overwrite for old workflow runs.

## Results

### Key Findings

- Added `dashboard_artifact_workflow.py` with the managed workflow marker, default artifact naming config, branch/ref slug sanitizer, and template renderer.
- Added `templates/superra-dashboard-artifact.yml`, a GitHub Actions workflow template that checks out the triggering ref, exports `superRA/` through `uv run --project skills/task-tree superra dashboard export`, deletes older artifacts with the same branch-stable name through `github.rest.actions.deleteArtifact`, and uploads the new artifact with `actions/upload-artifact@v4`.
- Updated package data so the YAML workflow template is included with the task-tree package.
- Added focused tests for slugging, branch-stable artifact naming, cleanup-before-upload, upload contract, configurable export paths, retention days, and missing-root behavior.

### Verification

- `uv run --project skills/task-tree --with pytest python -m pytest skills/task-tree/scripts/test_task_tree.py -k DashboardArtifactWorkflow` — 4 passed.
- `uv run --project skills/task-tree --with pytest python -m pytest skills/task-tree/scripts/test_task_tree.py` — 240 passed, 11 skipped, 1 expected invalid-status warning from the existing diagnostic test.

## Review Notes

*(Retrospective audit, 2026-06-10 — MINOR item only; status stays `approved`.)*

1. **MINOR** — the Results say the template exports through `uv run --project skills/task-tree superra dashboard export`, but the current [superra-dashboard-artifact.yml](../../../../../skills/task-tree/scripts/templates/superra-dashboard-artifact.yml) runs `uv run --script skills/task-tree/scripts/plan_dashboard.py dashboard export --root … --repo-file-base …` (changed when CLI source resolution moved to `uv run --script`). Refresh the command claim in place so the record matches the shipped template.
