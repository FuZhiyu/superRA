---
title: "report-in-markdown"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Without a shared style guide, a bare agent cites source as a bare backtick path like `` `src/estimate.py` `` — no line, not clickable — and pastes math that renders fine in a `.tex` file but silently breaks in the dashboard: a `\Var` operator KaTeX leaves undefined, or a display `$$` block flush against the line above that gets swallowed and never renders, with no error to warn anyone. Across a task tree, every agent guesses, and nothing reads alike.

This skill is the one house style they all follow: source files cited as clickable line anchors (`[estimate.py:42](estimate.py#L42)`), KaTeX math, small tables inlined and large ones linked, raw HTML only where markdown cannot express the layout. Every superRA agent loads it before writing a task file, status return, or standalone markdown. Load it directly to hold your own markdown to the same style — a results file, notes, a report you are drafting:

```
Apply report-in-markdown to analyses/example/RESULTS.md
```

To catch the two silent-render traps before you commit, run the self-diagnose CLI on any markdown file. It only reports, never edits:

```
uv run --script <skill-dir>/scripts/check_markdown.py path/to/file.md
```

where `<skill-dir>` is the directory holding the skill's `SKILL.md`. It is stdlib-only, so `python3 <skill-dir>/scripts/check_markdown.py …` works as a uv-free fallback.

Two references load on demand: [`references/rich-content.md`](skills/report-in-markdown/references/rich-content.md) for markdown that contains figures, and [`references/baseline-io.md`](skills/report-in-markdown/references/baseline-io.md) for permanent standalone artifacts that need frontmatter, a dated filename, and a resolved output path.

See [`report-in-markdown`](skills/report-in-markdown/SKILL.md) for the full style guide.
