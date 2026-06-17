---
title: "Add the Explorable Export + Framing-Page Entry"
status: not-started
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

*(filled during implementation)*
