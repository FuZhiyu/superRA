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

- The opening gives the answer or honest current state.
  - Evidence, caveats, and the next action follow.
  - Linked implementation details come last.
- Short nested lists are the default pyramid.
  - Headings and top-level bullets state the main points.
  - Paragraphs remain for connected reasoning, narrative, or causality.
- Sentence style is direct and concrete, and lives in the always-loaded core.
  - Each sentence names the actor and action, keeps relationships explicit, and uses one term per concept.
- Rewriting preserves exact literals, meaning, claim strength, dependencies, and useful voice.
  - The friction audit changes a pattern only when it makes text slower to understand; it does not try to detect AI authorship.

Structure, sentence style, and the content test all live in the always-loaded core. On-demand references cover [rewriting and friction audits](skills/communicate/references/rewrite.md), [Markdown mechanics](skills/communicate/references/markdown.md), and [standalone Markdown files](skills/communicate/references/baseline-io.md). The Markdown checker still catches display-math and KaTeX failures:

```
uv run --script <skill-dir>/scripts/check_markdown.py path/to/file.md
```

See [`communicate`](skills/communicate/SKILL.md) for the authoritative load map.
