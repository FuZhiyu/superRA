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

- The first layer gives the outcome, decision, or honest present state.
  - Evidence, material caveats, and the next action follow.
  - Linked mechanics and optional detail come last.
- Short nested lists are the default pyramid.
  - Conclusion headings and top-level bullets carry takeaways.
  - Paragraphs remain for connected reasoning, narrative, or causality.
- Rewriting preserves exact literals, meaning, claim force, dependencies, and useful voice.
  - The friction audit changes a pattern only when it creates observable reader cost; it does not try to detect AI authorship.

On-demand references cover [structures](skills/communicate/references/structures.md), [rewriting](skills/communicate/references/rewrite.md), [friction audits](skills/communicate/references/friction-audit.md), and [Markdown mechanics](skills/communicate/references/markdown.md). The Markdown checker still catches display-math and KaTeX failures:

```
uv run --script <skill-dir>/scripts/check_markdown.py path/to/file.md
```

See [`communicate`](skills/communicate/SKILL.md) for the authoritative load map.
