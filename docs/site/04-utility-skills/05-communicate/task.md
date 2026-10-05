---
title: "communicate"
status: not-started
depends_on: []
tags: []
created: 2026-06-17
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

## Check Markdown math before it breaks

The Markdown checker catches display-math and KaTeX failures that render silently broken:

```
uv run --script <skill-dir>/scripts/check_markdown.py path/to/file.md
```

`<skill-dir>` is the directory holding the skill's `SKILL.md`. The always-loaded core is [communicate](skills/communicate/SKILL.md); on-demand references cover [rewriting](skills/communicate/references/rewrite.md) and [Markdown mechanics](skills/communicate/references/markdown.md).
