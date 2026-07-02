---
title: "Docs Branch/Version Switcher (Reuse Worktree-Switch UI)"
status: postponed
depends_on: []
---

## Objective

Let a visitor switch the published docs site between branch/version builds, reusing the dashboard's existing worktree-switch mechanism as the UI (researcher-proposed 2026-06-11; scoped post-launch).

- CI builds the site once per published ref into URL subdirectories (e.g. `/<default-branch>/`, `/dev/`), extending the docs-site deploy workflow (`.github/workflows/docs-site.yml`); one ref remains the root/default.
- The standalone export grows a version dropdown in the same header slot as the live server's worktree switcher; selecting a version swaps the URL path prefix while preserving the current `#/<page>` hash (the live `applyWorktree` behavior, retargeted from the `?wt=` token to the path prefix).
- The available-version list is build-time data injected by CI; a version with no build for the current page falls back to that version's landing page.
- Additive: single-version builds (the v1 deploy) render no dropdown; the live dashboard's worktree switcher is unchanged.

Success criteria: a two-ref CI build where switching versions on a deep-linked page lands on the same page in the other version (or its landing fallback), verified on the published site; single-ref builds remain visually unchanged.

## Planner Guidance

The worktree-switch plumbing to study: `ACTIVE_WT`, `applyWorktree`, and the `?wt=` token handling in `base.html`, plus the multi-worktree discovery in `cli.py`. The version list is the static analog of the live worktree list.
