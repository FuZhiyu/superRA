---
title: "communicate"
status: not-started
depends_on: []
---

## Objective

`communicate` makes human-facing output dense and skimmable without sacrificing meaning. Agents load it throughout superRA; you can also invoke it directly to write, distill, review, or repair an existing report:

```
Use communicate to rewrite analyses/example/RESULTS.md for a cold reader.
```

## What the output looks like

- The opening gives the answer or honest current state.
  - Evidence, caveats, and the next action follow.
  - Linked implementation details come last.
- Short nested lists are the default.
  - Headings and top-level bullets state the main points.
  - Paragraphs remain for connected reasoning, narrative, or causality.
- Sentences are direct and concrete: each names the actor and action and uses one term per concept.
- A rewrite preserves exact literals, meaning, claim strength, and your voice. It changes a pattern only when that pattern makes the text slower to understand.

## Ask for an interactive page when a fixed figure is not enough

Ask for a page when you want to filter, hover, or switch specifications, as in "make an interactive explorer of these alphas":

- **The page is one self-contained HTML file** the agent saves under the task's `attachments/` and links from `## Results`. It supplements the PNG figures, which stay.
- **Each page leads with its answer.** Before you touch it, the page shows its main point, what is plotted, and the units. Exact values, definitions, and full tables wait behind hover, toggles, or expandable sections, while a caveat that changes how you read the result stays in view. Reviewers flag a page that hides either.
- **The dashboard shows each page inline, beside the text it supports.** Each embed holds one plot and fits about one phone screen, so a result with several plots becomes several embeds. An interactive version of a figure takes that figure's place in the dashboard, while GitHub still shows the PNG. Only an explorer whose views share state opens in the reading pane instead. Either way, the page runs in a sandbox that cuts it off from the dashboard and admits only pinned CDN scripts, and it follows the dashboard's light or dark theme. The standalone export carries it too.
- **A generator script writes the page** from the saved results, so the numbers stay reproducible. The showcase study's [alpha explorer](superRA/showcase-analysis/02-analysis/attachments/alpha-explorer.html) is built this way: a click or tap on any of the 25 portfolios shows CAPM and FF3 alphas, t-statistics, and loadings side by side.
- **Publishing is separate.** Say "publish it" and an agent with an artifact-publishing tool, such as the one in Claude, publishes the same file and records the link beside the attachment.

The authoring rules are in [html.md](skills/communicate/references/html.md).

## Check Markdown math before it breaks

The Markdown checker catches display-math and KaTeX failures that render silently broken:

```
uv run --script <skill-dir>/scripts/check_markdown.py path/to/file.md
```

`<skill-dir>` is the directory holding the skill's `SKILL.md`. The always-loaded core is [communicate](skills/communicate/SKILL.md); on-demand references cover [rewriting](skills/communicate/references/rewrite.md) and [Markdown mechanics](skills/communicate/references/markdown.md).
