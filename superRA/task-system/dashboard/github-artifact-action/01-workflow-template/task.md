---
title: "Workflow Template and Artifact Contract"
status: not-started
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
