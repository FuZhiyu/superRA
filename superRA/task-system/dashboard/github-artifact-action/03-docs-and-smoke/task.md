---
title: "Documentation and Smoke Verification"
status: revise
depends_on: 
  - 02-setup-cli

tags: []
created: 2026-06-04
---

## Objective

Document and smoke-test the artifact-based dashboard sharing mode. Update the relevant user-facing docs so researchers can install the workflow, push a branch, find the branch's current dashboard artifact in GitHub Actions, and understand the access model: artifacts require GitHub sign-in and repository read access but are downloaded rather than hosted as live webpages. Document that one branch maps to one current artifact name and that the workflow deletes older same-branch dashboard artifacts.

Add verification that exercises the setup command and template without requiring live GitHub credentials: render/install the workflow in a temporary fixture, parse the YAML enough to confirm the expected triggers/permissions/steps, and run the dashboard export command against a minimal task tree fixture so the artifact payload path is known-good. If live GitHub API behavior is not exercised, state that limitation in the task results and keep the workflow cleanup logic covered by static assertions.

Validation: run the targeted task-system tests covering the setup command/template plus existing dashboard export tests. Run `task_check` on `superRA` after updating this task tree.

## Planner Guidance

Docs likely belong in README.md's dashboard/task-system section and/or skills/task-system/SKILL.md / references/internals.md depending on whether the text is user-facing command usage or contributor internals. Keep README focused on the user flow; keep workflow mechanics in task-system references.

## Results

### Key Findings

- Documented the artifact workflow user flow in `README.md`: install the managed workflow, push a branch, download the repo-access-gated artifact from GitHub Actions, and open the exported dashboard HTML locally.
- Added task-system internals documentation for the artifact setup command, branch-pattern options, artifact naming, cleanup behavior, access model, and download-oriented limitation.
- Added static workflow-contract smoke tests for triggers, permissions, cleanup-before-upload ordering, and upload step presence.
- Added a minimal task-tree export smoke test proving the artifact payload path produces a standalone dashboard HTML file.

### Notes

- No live GitHub API run was performed in this task. The artifact cleanup behavior is covered by static assertions against the generated workflow's `github.rest.actions.listArtifactsForRepo` / `deleteArtifact` steps and by the tested template renderer.

### Verification

- `uv run --project skills/task-system --with pytest python -m pytest skills/task-system/scripts/test_task_system.py -k 'DashboardArtifactWorkflow or test_generate_dashboard or test_generate_is_standalone'` — 15 passed.
- `uv run --project skills/task-system --with pytest python -m pytest skills/task-system/scripts/test_task_system.py` — 249 passed, 11 skipped, 1 expected invalid-status warning from the existing diagnostic test.
- `uv run --project skills/task-system superra task check --root superRA` — all checks passed.
- Temp-repo smoke: installed the artifact workflow with branch filters, created a minimal `superRA/task.md`, exported `.superra-dashboard/dashboard.html`, and verified the output file exists and is non-empty.

## Review Notes

1. [MAJOR] The static workflow-contract test does not assert the required workflow triggers. It checks branch-pattern lines, permissions, concurrency, and step names, but a template that dropped `workflow_dispatch:` or moved the branch patterns out of `on.push.branches` would still pass [test_task_system.py:1317-1332](../../../../../skills/task-system/scripts/test_task_system.py#L1317-L1332). The task objective explicitly asks for verification of the expected triggers, so add a generated-workflow assertion that inspects the trigger structure enough to prove `push.branches` and `workflow_dispatch` are present.

2. [MAJOR] The minimal export smoke test bypasses the dashboard export command used by the workflow. It calls `plan_dashboard.generate_dashboard()` directly and pre-creates the output directory [test_task_system.py:1334-1345](../../../../../skills/task-system/scripts/test_task_system.py#L1334-L1345), while the installed workflow runs `uv run --project skills/task-system superra dashboard export --root "__TASK_ROOT__" --output "__OUTPUT_PATH__"` and relies on the workflow command path to create the payload [superra-dashboard-artifact.yml:46-50](../../../../../skills/task-system/scripts/templates/superra-dashboard-artifact.yml#L46-L50). Replace or extend the smoke test so it exercises the CLI export command against the minimal task tree and asserts the artifact payload path is created, non-empty, and standalone.
