---
title: "GitHub Actions Dashboard Artifact Publisher"
status: not-started
depends_on: 
  - self-contained-export

tags: []
created: 2026-06-04
---

## Objective

Add a task-system dashboard setup tool that installs a GitHub Actions workflow for publishing the current branch's superRA dashboard as a workflow artifact. The tool must generate or update a repository workflow under `.github/workflows/` without hand-editing this repository's workflow only. The installed workflow must run on pushes and `workflow_dispatch`, export the checked-out branch's `superRA/` task tree using the existing static dashboard export path, upload exactly one dashboard artifact for that branch, and delete older dashboard artifacts for the same branch before uploading the replacement. This is an artifact-based sharing mode: it is repo-access-gated by GitHub Actions artifact permissions, download-oriented rather than hosted, and branch-scoped so WIP branches can share their current task tree snapshot.

### Context

GitHub Actions artifacts are scoped to workflow runs. Reusing an artifact name or `upload-artifact` overwrite behavior is not sufficient to guarantee one surviving artifact per branch across older runs. The workflow must explicitly list and delete older artifacts whose name matches the branch-stable dashboard artifact before uploading the new one. Use GitHub's `GITHUB_TOKEN` with the minimum permissions needed for artifact deletion/upload.

### Constraints

The generated workflow must not publish to GitHub Pages or any public URL. It must not require repository secrets for the default path. It must operate on the branch/commit that triggered the workflow and export only that branch's `superRA/` tree.

## Planner Guidance

Likely implementation shape: add a packaged workflow template under skills/task-system, add a CLI subcommand under superra dashboard for installing it, and include a cleanup step using GitHub API before actions/upload-artifact. Keep the artifact name branch-stable after sanitizing the ref name, e.g. superra-dashboard-<branch-slug>.

## Results
