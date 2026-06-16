---
title: "Quickstart Tutorial: First Analysis End to End"
status: approved
depends_on:
  - 01-information-architecture
tags: []
created: 2026-06-10
---

## Objective

Write the single worked walkthrough a new user follows on day one: install superRA (Claude Code as the primary path), start a small hypothetical research analysis, watch superplan produce a ~3-task tree, follow one implementer–reviewer cycle, check progress in the dashboard and `superra task tree`, read the results from the task files, and finish.

- The walkthrough is **actually executed** on a public-safe toy example to produce its transcripts, tree snippets, and dashboard screenshots — no fabricated output.
- Every command shown is copy-pasteable and was run as shown.
- The tutorial ends with pointers into the how-to guides and concept pages for the paths it deliberately skipped.

Validation: a reader with Claude Code and git installed can replicate each step; the captured artifacts match what the current code produces.

## Planner Guidance

Dashboard screenshots are best captured after the `02-dashboard-features` children land so visuals match the shipped site; drafting the prose and transcripts need not wait. If sequencing forces earlier capture, note in `## Results` which screenshots need a refresh pass.

## Results

The quickstart tutorial page is drafted at [docs/site/02-quickstart/task.md](../../../docs/site/02-quickstart/task.md) (rendered as the `#/02-quickstart` page), with three committed dashboard screenshots under [docs/site/02-quickstart/attachments/](../../../docs/site/02-quickstart/attachments/). It follows the IA authoring contract (`docs-site/01-information-architecture` §3): `title`-only frontmatter, page body under `## Objective`, hash cross-links `#/<path>`, and `![caption](attachments/...)` figures the export base64-inlines.

### Walkthrough — actually executed, not fabricated

The toy analysis was really run to produce every transcript, tree snippet, and screenshot. The working files live in a temp directory outside the repo (`/tmp/superra-quickstart-toy/`, not committed per dispatch); only the page, its attachments, and this task file are committed.

- **Toy story aligned with the showcase.** The example is a small simulated size/momentum-style equity analysis — a 3-task tree (`01-simulate-panel` → `02-build-portfolios` → `03-report-spread`) under one root, matching the sibling showcase task's demo story so the two reinforce rather than conflict.
- **Real task tree + frontier.** Built via the `superra` CLI; the `task tree` and `task frontier` blocks on the page are verbatim CLI output. Status was set mid-flight (panel approved, portfolios in progress) so the captured tree shows the rollup glyph and a non-trivial frontier.
- **Real implementer output.** Task `01-simulate-panel` was actually implemented: a seed-42 simulation script (in the uncommitted temp project) produced a 12,000-row panel, and the summary stats quoted in the page's `## Results` excerpt (mean -0.07%, SD 4.05%, etc.) are that script's real output.
- **Real screenshots.** Captured with headless Chromium (Playwright) against the live `superra dashboard` serving the toy tree: Workspace (tree + status pills + `1/3` rollup), Kanban (status columns), and a task-detail page (Objective + Results). Each was retina-rendered and bottom-cropped.

### Real-user-path verification

The page was exported through the actual build path and rendered in a browser, not just lint-checked:

- `superra dashboard export --root docs/site --doc-mode` produces a self-contained HTML; the quickstart page renders with all three screenshots base64-inlined (`naturalWidth` non-zero, confirmed in headless Chromium) and all eight section headings present.
- All hash cross-links (`#/04-how-to/...`, `#/03-concepts/...`, `#/05-reference/01-task-file`, `#/06-showcase`) resolve to scaffolded sitemap nodes.
- `report-in-markdown` render-integrity check (`check_markdown.py`) reports the page clean.

### Caveats / follow-ups

- **Intent comments stripped from the committed page.** Draft mode authors paragraph-level intent comments, but the dashboard renderer runs markdown-it with `html: false`, so `<!-- intent: ... -->` renders as *visible* gray text — a process-internal-artifact leak to the reader. They served their drafting purpose and were removed before commit; the page carries no scaffold. This is a general constraint for every doc page authored under this contract (no HTML comments survive the renderer).
- **Doc-mode chrome.** The `--doc-mode` export still shows a top status bar and a TASKS sidebar in my capture. The exact chrome-suppression behavior and the final build invocation are owned by `02-dashboard-features/doc-mode` and `08-deploy`; the page authoring is correct regardless of how much chrome the final build hides.
- **Screenshot refresh (Planner Guidance).** Screenshots were captured against the dashboard in this base, which already carries the merged `02-dashboard-features` (doc-mode, search, code highlighting), so they reflect the shipped UI. No refresh pass is needed unless later dashboard styling changes the Workspace/Kanban/detail layouts.
- **Codex path is linked, not walked.** The tutorial follows the Claude Code primary path and routes Codex users to `#/04-how-to/01-install-and-set-up` rather than duplicating install detail.
