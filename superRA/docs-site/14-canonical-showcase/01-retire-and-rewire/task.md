---
title: "Retire the Demo Tree and Rewire the Build to Two Files"
status: not-started
depends_on: []
tags: []
created: 2026-06-17
---

## Objective

Delete the simulated demo tree and reduce the site build to two exports: `index.html` (docs, doc-mode) and `showcase-analysis-tree.html` (real study, full chrome).

- **Delete** the entire `docs/showcase-demo/` directory (the simulated tree, its `make_figure.py`, and the committed figure under `03-size-sort-returns/attachments/`).
- **Rewrite** [docs/build_site.sh](../../../../docs/build_site.sh):
  - Drop the `demo-tree.html` and `superra-dev-tree.html` `run_gen` calls and the `demo_tree` variable. The `showcase-analysis-tree.html` export still scopes the full repo tree with `--plan-root superRA --root showcase-analysis`, so keep whatever variable that call needs.
  - On the doc-mode `index.html` build, drop `--doc-local-link demo-tree.html` and `--doc-local-link superra-dev-tree.html`; keep `--doc-local-link showcase-analysis-tree.html`.
  - Update the required-input existence check (no longer needs `docs/showcase-demo`), the output-existence verification loop, the header comment block, and the final echo so they all reference exactly `index.html` and `showcase-analysis-tree.html`.
- **CI** ([.github/workflows/docs-site.yml](../../../../.github/workflows/docs-site.yml)): remove `docs/showcase-demo/**` from the push path filter. Leave `docs/site/**`, `superRA/showcase-analysis/**`, and `docs/build_site.sh`.

**Validation:** run `docs/build_site.sh <scratch-dir>` and confirm it produces exactly `index.html` and `showcase-analysis-tree.html`, both non-empty; the study renders with full task-tracker chrome (status pills, DAG, kanban) and inlines its figures; the framing-page link to `showcase-analysis-tree.html` resolves as a plain relative href in the built `index.html`. Confirm no dangling references to `demo-tree.html`, `superra-dev-tree.html`, or `docs/showcase-demo` remain in the build script or CI.
