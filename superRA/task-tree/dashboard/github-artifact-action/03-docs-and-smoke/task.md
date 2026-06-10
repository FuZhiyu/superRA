---
title: "Documentation and Smoke Verification"
status: approved
depends_on:
  - 02-setup-cli

tags: []
created: 2026-06-04
---

## Objective

Document and smoke-test the artifact-based dashboard sharing mode. Update the relevant user-facing docs so researchers can install the workflow, push a branch, find the branch's current dashboard artifact in GitHub Actions, and understand the access model: artifacts require GitHub sign-in and repository read access but are downloaded rather than hosted as live webpages. Document that one branch maps to one current artifact name and that the workflow deletes older same-branch dashboard artifacts.

Add verification that exercises the setup command and template without requiring live GitHub credentials: render/install the workflow in a temporary fixture, parse the YAML enough to confirm the expected triggers/permissions/steps, and run the dashboard export command against a minimal task tree fixture so the artifact payload path is known-good. If live GitHub API behavior is not exercised, state that limitation in the task results and keep the workflow cleanup logic covered by static assertions.

Validation: run the targeted task-tree tests covering the setup command/template plus existing dashboard export tests. Run `task_check` on `superRA` after updating this task tree.

## Planner Guidance

Docs likely belong in README.md's dashboard/task-tree section and/or skills/task-tree/SKILL.md / references/internals.md depending on whether the text is user-facing command usage or contributor internals. Keep README focused on the user flow; keep workflow mechanics in task-tree references.

## Results

### Key Findings

- Documented the artifact workflow user flow in `README.md`: install the managed workflow, push a branch, download the repo-access-gated artifact from GitHub Actions, and open the exported dashboard HTML locally.
- Added task-tree internals documentation for the artifact setup command, branch-pattern options, artifact naming, cleanup behavior, access model, and download-oriented limitation.
- Added static workflow-contract smoke tests for triggers, permissions, cleanup-before-upload ordering, and upload step presence.
- Added a minimal task-tree export smoke test proving the artifact payload path produces a standalone dashboard HTML file.

### Notes

- No live GitHub API run was performed in this task. The artifact cleanup behavior is covered by static assertions against the generated workflow's `github.rest.actions.listArtifactsForRepo` / `deleteArtifact` steps and by the tested template renderer.

### Verification

- `uv run --project skills/task-tree --with pytest python -m pytest skills/task-tree/scripts/test_task_tree.py -k 'DashboardArtifactWorkflow or test_generate_dashboard or test_generate_is_standalone'` — 15 passed.
- `uv run --project skills/task-tree --with pytest python -m pytest skills/task-tree/scripts/test_task_tree.py` — 249 passed, 11 skipped, 1 expected invalid-status warning from the existing diagnostic test.
- `uv run --project skills/task-tree superra task check --root superRA` — all checks passed.
- Temp-repo smoke: installed the artifact workflow with branch filters, created a minimal `superRA/task.md`, exported `.superra-dashboard/dashboard.html`, and verified the output file exists and is non-empty.
