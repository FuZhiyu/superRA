---
title: "Retire the Demo Tree and Rewire the Build to Two Files"
status: approved
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

## Results

Deleted the simulated demo tree and reduced the site build to two exports.

- **Deleted** the entire `docs/showcase-demo/` directory (`git rm -r`), including its six task subtrees, `make_figure.py`, and the committed figure under `03-size-sort-returns/attachments/`.
- **Rewrote** [docs/build_site.sh](../../../../docs/build_site.sh): removed the `demo_tree` variable and the `demo-tree.html` / `superra-dev-tree.html` `run_gen` calls; kept `dev_tree="superRA"` since the `showcase-analysis-tree.html` export still scopes the repo tree with `--plan-root superRA --root showcase-analysis`. Dropped the two stale `--doc-local-link` flags (kept `--doc-local-link showcase-analysis-tree.html`). Updated the header comment block (now documents two files), the required-input existence check (`$docs_tree $dev_tree`), the output-verification loop, and the final echo — all now reference exactly `index.html` and `showcase-analysis-tree.html`.
- **CI** ([.github/workflows/docs-site.yml](../../../../.github/workflows/docs-site.yml)): removed `docs/showcase-demo/**` from the push path filter; left `docs/site/**`, `superRA/showcase-analysis/**`, `docs/build_site.sh`, and the scripts/workflow filters intact.

**Validation evidence** — ran `docs/build_site.sh /tmp/sitecheck`:

| Check | Result |
|---|---|
| Output files | exactly `index.html` (3.74 MB) + `showcase-analysis-tree.html` (1.95 MB), both non-empty |
| Study full chrome | `showView('kanban')` toggle present, 2 `class="dag…` blocks, kanban markup (65 hits) |
| Study figures inlined | 6 `data:image/png;base64` figures inlined |
| Framing link form | rendered as bare relative markdown link `[Open the asset-pricing study →](showcase-analysis-tree.html)`, not rebased to a github blob URL — `--doc-local-link` working |
| Dangling refs in build script / CI | none (`grep` clean for `demo-tree`, `superra-dev-tree`, `showcase-demo`) |

**Caveat (out of scope for this task):** the showcase page source [docs/site/06-showcase/task.md](../../../../docs/site/06-showcase/task.md) still links to `demo-tree.html` and `superra-dev-tree.html`, so the built `index.html` carries two dangling tree links from that page. Rewriting that page is sibling task `03-rewrite-showcase-page`; this task's validation scopes the dangling-ref check to the build script and CI, both of which are clean.
