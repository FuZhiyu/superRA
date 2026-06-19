---
title: "Add the Explorable Export + Framing-Page Entry"
status: approved
depends_on: []
tags: []
created: 2026-06-17
---

## Objective

Add the real asset-pricing tree as a third standalone, full-chrome export alongside the demo tree and the dev tree, and introduce it on the showcase framing page.

- **Build script.** Add a fourth `run_gen` call to [docs/build_site.sh](../../../../docs/build_site.sh) that exports the showcase tree to `<out>/showcase-analysis-tree.html` with full chrome (non-doc-mode):
  `--plan-root superRA --root showcase-analysis --repo-file-base "$repo_file_base" --repo-file-prefix superRA/showcase-analysis`.
  Add it to the output-existence verification the script already does for the other three files. Also register the new export as a doc-local link on the **doc-mode `index.html` build** — add `--doc-local-link showcase-analysis-tree.html` to that `run_gen` call (alongside the existing `--doc-local-link demo-tree.html --doc-local-link superra-dev-tree.html`), so the framing-page link below stays a relative href instead of being rebased to the GitHub blob base.
- **CI trigger.** Add `superRA/showcase-analysis/**` to the push path filter in [.github/workflows/docs-site.yml](../../../../.github/workflows/docs-site.yml) so changes to the analysis tree rebuild the site.
- **Framing page.** On [docs/site/06-showcase/task.md](../../../../docs/site/06-showcase/task.md), add a short section introducing the real tree next to the existing demo/dev entries: what the study is (the canonical CAPM-vs-FF3 / GRS test), that it was produced by actually running the superRA workflow, and a relative link `[Open the asset-pricing study →](showcase-analysis-tree.html)`. Follow the page's existing voice and link conventions; link down into the analysis tree's concepts via the established hash-link pattern where useful.

**Validation:** run `docs/build_site.sh` to a scratch output dir and confirm `showcase-analysis-tree.html` is produced, is non-empty, opens offline, renders the analysis tree with full task-tracker chrome (status pills, DAG, kanban), and inlines its figures. Confirm the framing-page link resolves as a plain relative href in the built `index.html` (not rebased to a GitHub blob URL). Confirm the other three exports still build.

## Results

The real asset-pricing tree is now wired into the docs site as a third full-chrome standalone export alongside the demo and dev trees.

- **Build script** ([docs/build_site.sh](../../../../docs/build_site.sh)). Added a fourth `run_gen` call that scopes the full repo tree to the study subtree — `--plan-root superRA --root showcase-analysis --repo-file-prefix superRA/showcase-analysis` (reusing the existing `$dev_tree` variable, which is `superRA`) — writing `showcase-analysis-tree.html` in non-doc-mode (full chrome). Extended the output-existence verification loop and the header comment to cover the fourth file, and registered `--doc-local-link showcase-analysis-tree.html` on the doc-mode `index.html` build so the framing link stays a relative href.
- **CI trigger** ([.github/workflows/docs-site.yml](../../../../.github/workflows/docs-site.yml)). Added `superRA/showcase-analysis/**` to the push path filter so analysis-tree changes rebuild the site.
- **Framing page** ([docs/site/06-showcase/task.md](../../../../docs/site/06-showcase/task.md)). Renamed the section to "The three trees", added an entry framing the study as the finished, real, executed counterpart to the mid-flight demo (canonical CAPM-vs-FF3 / GRS test on Ken French's 25 size–B/M portfolios, run end-to-end through the workflow) with the relative link `[Open the asset-pricing study →](showcase-analysis-tree.html)`, and added its build invocation to "How these are built".

**Validation** (`docs/build_site.sh /tmp/showcase_site_build`):

- All four exports built non-empty: `index.html` (2.0 MB), `demo-tree.html` (1.2 MB), `superra-dev-tree.html` (13 MB), `showcase-analysis-tree.html` (1.9 MB).
- `showcase-analysis-tree.html` carries full task-tracker chrome (kanban, DAG, status pills, rollup markers all present) and 6 base64-inlined PNG figures (`data:image/png;base64`).
- The framing link resolves as a plain relative basename `showcase-analysis-tree.html` in the built `index.html` — grep confirmed no `https://github.com/.../showcase-analysis-tree.html` blob rebasing, matching the existing `demo-tree.html` link behavior.
- `report-in-markdown` self-diagnose on the framing page: clean.
