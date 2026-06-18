---
title: "Rewrite the Showcase Page Around the Real Study Only"
status: approved
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

## Results

Rewrote [docs/site/06-showcase/task.md](../../../../docs/site/06-showcase/task.md) as a single-study showcase.

- **Single-tree intro.** Replaced the "The three trees" framing. The opening paragraph now refers to "a live export of a real superRA task tree" (singular), and the real-study paragraph (CAPM/FF3, Ken French 25 portfolios, GRS joint test, all-`approved` completed handoff) moved up as the page's single introduction, immediately followed by `[Open the asset-pricing study →](showcase-analysis-tree.html)` ([docs/site/06-showcase/task.md:13-17](../../../../docs/site/06-showcase/task.md#L13-L17)).
- **Dropped demo + dev-tree sections** and their `demo-tree.html` / `superra-dev-tree.html` links entirely. No dangling reference to either tree remains (grep for `demo-tree`, `superra-dev-tree`, "three trees", "mid-flight" returns nothing).
- **Kept the element walkthrough and deep-link note.** Status pills, rollup, DAG, kanban, inside-a-task bullets and the deep-link paragraph are unchanged; they describe the tracker chrome generically. The only contrast-removal edit: "Each export is a self-contained page" → "The export is a self-contained page" ([docs/site/06-showcase/task.md:21](../../../../docs/site/06-showcase/task.md#L21)). The rollup bullet's `revise` example describes the rollup *mechanism* abstractly, not the study tree, so it stays.
- **"How these are built" → "How this is built"** now shows the single fenced command `uv run --script skills/task-tree/scripts/plan_dashboard.py generate --plan-root superRA --root showcase-analysis`, matching [docs/build_site.sh:86-91](../../../../docs/build_site.sh#L86-L91). The `--root` rationale is kept as one trailing sentence ([docs/site/06-showcase/task.md:31-39](../../../../docs/site/06-showcase/task.md#L31-L39)).

**Verification:**

- All five `#/` hash targets (`02-quickstart`, `04-utility-skills`, `05-reference/03-status-and-frontier`, `05-reference/01-task-file`) and both repo-file links (`skills/task-tree/SKILL.md`, `skills/task-tree/scripts/plan_dashboard.py`) resolve — checked each path exists on disk.
- `report-in-markdown` self-diagnose: `docs/site/06-showcase/task.md: clean`.
- Build command verbatim-matches the approved `docs/build_site.sh` showcase export (`--plan-root superRA --root showcase-analysis`).
- Voice held: no rhetorical hooks or AI-flavored intensifiers added; reused the existing real-study prose.
