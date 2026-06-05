---
title: "Workflow Template and Artifact Contract"
status: implemented
depends_on:  []
tags: []
created: 2026-06-04
---

## Objective

Create the GitHub Actions workflow template that exports a branch-scoped superRA dashboard artifact. The template must check out the triggering ref, install/use the task-system CLI from the repository checkout, run the existing dashboard static export against `superRA/`, and upload the exported dashboard as a GitHub Actions artifact with a branch-stable name. Before upload, it must delete older dashboard artifacts with the same branch-stable name so the repository has at most one current dashboard artifact per branch after a successful run.

The template must define safe defaults: push and `workflow_dispatch` triggers, concurrency scoped by branch/ref to avoid cleanup/upload races, minimal `GITHUB_TOKEN` permissions needed for reading contents and deleting/listing artifacts, failure when `superRA/` is absent unless the setup command exposes an explicit opt-out, and a short retention default that can be configured by the setup command.

Validation: add unit-level or script-level checks that render the template with representative branch names and verify the cleanup/upload contract is present, the artifact name is sanitized, and the export command targets the checked-out branch's `superRA/` tree.

## Planner Guidance

Consider a template file under skills/task-system/scripts/templates or a task-system resource path. For deletion, use either actions/github-script or gh api to list repository artifacts and delete entries matching the computed artifact name before actions/upload-artifact runs. Do not depend on upload-artifact overwrite for old workflow runs.

## Results

### Key Findings

- Added `dashboard_artifact_workflow.py` with the managed workflow marker, default artifact naming config, branch/ref slug sanitizer, and template renderer.
- Added `templates/superra-dashboard-artifact.yml`, a GitHub Actions workflow template that checks out the triggering ref, exports `superRA/` through `uv run --project skills/task-system superra dashboard export`, deletes older artifacts with the same branch-stable name through `github.rest.actions.deleteArtifact`, and uploads the new artifact with `actions/upload-artifact@v4`.
- Updated package data so the YAML workflow template is included with the task-system package.
- Added focused tests for slugging, branch-stable artifact naming, cleanup-before-upload, upload contract, configurable export paths, retention days, and missing-root behavior.

### Verification

- `uv run --project skills/task-system --with pytest python -m pytest skills/task-system/scripts/test_task_system.py -k DashboardArtifactWorkflow` — 4 passed.
- `uv run --project skills/task-system --with pytest python -m pytest skills/task-system/scripts/test_task_system.py` — 240 passed, 11 skipped, 1 expected invalid-status warning from the existing diagnostic test.

## Review Notes

1. [MAJOR] The branch-scoped artifact name can collide across distinct legal branch names. The helper builds names as prefix plus a sanitized slug [dashboard_artifact_workflow.py:47-49](../../../../../skills/task-system/scripts/dashboard_artifact_workflow.py#L47-L49), and the workflow deletes every repository artifact whose name equals that value before upload [superra-dashboard-artifact.yml:51-68](../../../../../skills/task-system/scripts/templates/superra-dashboard-artifact.yml#L51-L68). Because the sanitizer maps both `feature/foo` and `feature-foo` to `feature-foo`, a successful run on one branch can delete the other branch artifact and upload with the same name. That violates the task contract of one current artifact per branch. Make the branch-stable name collision-resistant for distinct refs, for example by including a stable hash of the original ref in addition to the readable slug, and add a test covering a slash-vs-hyphen branch collision.
   → implemented: artifact names now append a 12-character SHA-256 prefix of the original ref in both the Python helper and workflow shell step, with a slash-vs-hyphen collision regression test ([dashboard_artifact_workflow.py](../../../../../skills/task-system/scripts/dashboard_artifact_workflow.py), [superra-dashboard-artifact.yml](../../../../../skills/task-system/scripts/templates/superra-dashboard-artifact.yml), [test_task_system.py](../../../../../skills/task-system/scripts/test_task_system.py)).
