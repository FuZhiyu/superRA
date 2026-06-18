---
title: "GitHub Actions Dashboard Artifact Publisher"
status: approved
depends_on:
  - self-contained-export
tags: []
created: 2026-06-04
---

## Objective

Add a task-tree dashboard setup tool that installs a GitHub Actions workflow for publishing the current branch's superRA dashboard as a workflow artifact. The tool must generate or update a repository workflow under `.github/workflows/` without hand-editing this repository's workflow only. The installed workflow must run on pushes and `workflow_dispatch`, export the checked-out branch's `superRA/` task tree using the existing static dashboard export path, upload exactly one dashboard artifact for that branch, and delete older dashboard artifacts for the same branch before uploading the replacement. This is an artifact-based sharing mode: it is repo-access-gated by GitHub Actions artifact permissions, download-oriented rather than hosted, and branch-scoped so WIP branches can share their current task tree snapshot.

### Context

GitHub Actions artifacts are scoped to workflow runs. Reusing an artifact name or `upload-artifact` overwrite behavior is not sufficient to guarantee one surviving artifact per branch across older runs. The workflow must explicitly list and delete older artifacts whose name matches the branch-stable dashboard artifact before uploading the new one. Use GitHub's `GITHUB_TOKEN` with the minimum permissions needed for artifact deletion/upload.

### Constraints

The generated workflow must not publish to GitHub Pages or any public URL. It must not require repository secrets for the default path. It must operate on the branch/commit that triggered the workflow and export only that branch's `superRA/` tree.

## Planner Guidance

Likely implementation shape: add a packaged workflow template under skills/task-tree, add a CLI subcommand under superra dashboard for installing it, and include a cleanup step using GitHub API before actions/upload-artifact. Keep the artifact name branch-stable after sanitizing the ref name, e.g. superra-dashboard-<branch-slug>.

## Results

- GitHub Actions artifact exports pass a repository blob URL rooted at `${{ github.sha }}` into the static dashboard exporter, so downloaded HTML opens file links and task-file buttons on GitHub instead of local editor paths. Plain local exports keep the existing local editor-link behavior unless `--repo-file-base` is provided.

## Review Notes

*(Retrospective audit, 2026-06-10 — MINOR items only; status stays `approved`.)*

1. **MINOR** — the parent `## Results` is a single `--repo-file-base` bullet and never states the headline deliverables the three approved children shipped: the managed workflow template with delete-before-upload artifact cleanup ([01-workflow-template](01-workflow-template/task.md)), the `superra dashboard artifact setup` installer CLI ([02-setup-cli](02-setup-cli/task.md)), and docs/smoke ([03-docs-and-smoke](03-docs-and-smoke/task.md)). Add a rollup linking down to the children.
2. **MINOR** — the installed workflow's export step hardcodes `uv run --script skills/task-tree/scripts/plan_dashboard.py …` ([superra-dashboard-artifact.yml](../../../../skills/task-tree/scripts/templates/superra-dashboard-artifact.yml)), but `artifact setup --repo-root` installs into arbitrary repositories; a consumer repo that uses superRA as a plugin (no vendored `skills/task-tree/`) gets a workflow that fails at the export step with no setup-time warning. Verify the script path exists under the target repo at install time (warn or refuse), or make the CLI source line configurable.
