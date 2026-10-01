---
title: "Quickstart: Show the Graph and Start Existing Projects with Onboarding"
status: implemented
depends_on: [01-showcase-graph, 02-repro-page]
---

## Objective

Update [the Quickstart](../../../../docs/site/02-quickstart/task.md) so a first-time reader sees what the reproduction graph looks like on the showcase study and how its features work, and so an existing project enters through onboarding.

- **A graph beat in the walkthrough,** placed where the showcase's results land: the Graph view of the showcase study (screenshot under the page's `attachments/` and a link into the live `showcase-analysis-tree.html`), what the freshness marks mean, the Run/build button, and "ask which results an edit affects". It links to [the reproducibility page](../02-repro-page/task.md) for the mechanics instead of re-explaining them.
- **The `## Results` excerpt** no longer cites `run_all.sh`; it reflects the registered graph.
- **Existing projects start with onboarding.** The "point it at work you already have" prompt routes to the `onboarding` skill and says in one or two sentences what it produces (task tree, reproduction graph, optional git and isolated rerun) and that it touches nothing outside `superRA/` until approved; link [skills/onboarding/SKILL.md](../../../../skills/onboarding/SKILL.md).
- The Quickstart stays a walkthrough: the graph beat adds at most a few short paragraphs.

## Details

- Current Quickstart sections: Prerequisite → Install + set up a project → A typical workflow (Superplan / Implement / Watch progress / Superintegrate / Composable) → Where to go next. The adoption prompt sits in "Install + set up a project"; the `run_all.sh` excerpt in "Implement".
- The dashboard's build route and Graph workspace are in `skills/task-tree/scripts/plan_dashboard.py` (`/api/repro/build`, `/api/repro/explain`); verify the button and labels against a live `./superRA/superra dashboard` before describing them.

## Results

The [Quickstart](../../../../docs/site/02-quickstart/task.md) now shows the showcase's reproduction graph, starts an existing project with onboarding, and describes only 0.5 dashboard views.

- **A new "See which results are current" subsection follows "Watch progress and read results".** It has three short paragraphs, the agent prompt "Which results does an edit to 01_build_panel.py affect?", and a link to [the reproducibility page](../../../../docs/site/04-utility-skills/09-reproducibility/task.md) for the mechanics.
  - **Screenshot:** [showcase-graph.png](../../../../docs/site/02-quickstart/attachments/showcase-graph.png) is the Graph view of the showcase in a live dashboard on this branch, with the two step-holding tasks expanded and every step `fresh`. It is a hand capture with no producer step, so `task check` warns about it by design.
  - **Live link:** `showcase-analysis-tree.html#/?repro={"expanded":["01-data","02-analysis"],"layout":"graph"}`, URL-encoded, opens the export in the Graph view with both tasks expanded. The built site keeps it relative.
  - **Freshness marks:** the text explains `fresh` and the downstream spread of `stale`, and leaves the other states to the reproducibility page.
  - **Build button:** each task and step card in a live dashboard has a **Build** button. The text says the published exports are snapshots without it; the export renders no controls (`REPRO_ACTIONS`).
- **The `## Results` excerpt quotes the current 01-data Results.** It names the registered `build-panel` step in place of `run_all.sh`, and its numbers come from the 202608 release: 758 months over 1963-07 to 2026-08, 1202 merged rows, market premium 0.602%/mo, volatility 4.46%/mo.
- **The adoption prompt routes to onboarding.** "Use superRA to onboard this project and show me the dashboard." is followed by two sentences on what [onboarding](../../../../skills/onboarding/SKILL.md) produces and that nothing outside `superRA/` changes until the researcher agrees. The "Composable and iterative" closing line now points back to it.
- **Pre-0.5 dashboard views are gone.** The Kanban sentence is deleted, "Workspace" view became "Tree" (the default button in [base.html:83](../../../../skills/task-tree/scripts/templates/base.html#L83)), and "renders a dependency DAG" is dropped because the new Graph subsection covers it.
- **Verified against a live dashboard and the real graph.**
  - Card labels (`▶ Build`, `fresh`, `fresh · check`, task summaries like `fresh 2`) and the hover card come from the live dashboard. A temporary comment edit to `01_build_panel.py` showed all three steps `stale`, and the hover card on `build-panel` named the changed script. The edit was reverted.
  - `repro impact` on `01_build_panel.py` lists all three steps.
  - `superra task check --root docs/site` is clean, `check_markdown.py` reports both pages clean, and `docs/build_site.sh` exits 0 with the screenshot inlined.
- **Deviation: one screenshot, in the fresh state.** A stale-state screenshot with the hover card would show more, but the linked export reads `fresh`, so the screenshot matches what the reader opens.

