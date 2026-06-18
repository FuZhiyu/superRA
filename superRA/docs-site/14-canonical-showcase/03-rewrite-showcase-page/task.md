---
title: "Rewrite the Showcase Page Around the Real Study Only"
status: not-started
depends_on:
  - 01-retire-and-rewire
tags: []
created: 2026-06-17
---

## Objective

Rewrite [docs/site/06-showcase/task.md](../../../../docs/site/06-showcase/task.md) so the real CAPM-vs-FF3 study is the single tree the page presents.

- Drop the "A demo analysis — a project mid-flight" section and its `[Open the demo task tree →](demo-tree.html)` link, and the "superRA's own development tree" section and its `[Open superRA's own task tree →](superra-dev-tree.html)` link. Replace the "The three trees" framing with a single-tree introduction built from the existing real-study paragraph.
- Keep the "What you are looking at" element walkthrough (status pills, rollup, the DAG, the Kanban board, inside-a-task) and the deep-link note — these still describe the study tree. Adjust any wording that assumed a contrast between a mid-flight demo and the finished study (the study is the one and only tree now).
- Update "How these are built" to the single export command: `uv run --script skills/task-tree/scripts/plan_dashboard.py generate --plan-root superRA --root showcase-analysis` (the study is a subtree of superRA, scoped with `--root`). Remove the demo and dev-tree build commands. This must match the build script as rewritten by `01-retire-and-rewire`.
- The page links to `showcase-analysis-tree.html` (built by `01`); keep that relative link.

Hold the page's existing voice and the docs audience (academic researchers new to superRA; link to authoritative skill/agent files rather than paraphrasing). Verify every `#/` hash link and every repo-file link still resolves, and that `report-in-markdown` self-diagnose is clean.

**Validation:** the page reads as a single-study showcase with no dangling demo/dev-tree references or links; the build command matches `docs/build_site.sh`; all links resolve; self-diagnose clean.
