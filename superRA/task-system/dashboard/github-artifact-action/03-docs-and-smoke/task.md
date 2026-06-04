---
title: "Documentation and Smoke Verification"
status: not-started
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
