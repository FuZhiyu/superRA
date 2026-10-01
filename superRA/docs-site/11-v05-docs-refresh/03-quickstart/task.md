---
title: "Quickstart: Show the Graph and Start Existing Projects with Onboarding"
status: not-started
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
