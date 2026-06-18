---
title: "report-in-markdown"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Ask a bare agent to write up a regression and it cites the source as a backtick string like `` `src/estimate.py` `` — no line number, not clickable, so a reader has to grep for the function. The next agent on the next task writes `(see estimate.py around line 40)`. A third pastes a `\Var(\hat\beta)` operator that renders fine in a `.tex` file but shows up as a red KaTeX error in the dashboard, and a display equation sitting flush against the line above it gets swallowed into that paragraph and never renders at all, with no error to warn anyone. Across a task tree, every agent guesses at citation form, math, and table layout, and nothing reads alike.

This skill is the one style guide they all follow, so the tree stays consistent and every source reference is a clickable line anchor. Every superRA agent loads it before it writes a task file, a status return, or any standalone markdown. You also load it directly whenever you are writing markdown you want held to the same house style — point it at a results file, a notes document, or a report you are drafting:

```
Apply report-in-markdown to analyses/example/RESULTS.md
```

The rules it enforces:

Source files are cited as **markdown links with line anchors**, never backtick-wrapped paths: `[estimate.py:42](estimate.py#L42)` for a line, `[estimate.py:40-50](estimate.py#L40-L50)` for a range, `[estimate.py](estimate.py)` for a whole file. Paths resolve relative to the markdown file's own directory, so a citation from a `task.md` uses `../` to reach a sibling output. Follow the link and you land on the exact line in the dashboard or on GitHub.

Math uses KaTeX: `$...$` inline, `$$...$$` for display blocks, `\text{...}` for words inside math, and LaTeX over Unicode for anything with subscripts, superscripts, fractions, sums, or integrals. Two patterns render as silently broken output in the dashboard, and the skill names both. A display `$$` block must have a blank line above and below it and none inside, or it is absorbed into the preceding paragraph and never renders as a block. Operators that KaTeX leaves undefined — `\Var`, `\Cov`, `\E`, `\plim`, `\argmax`, `\tr`, and the rest — must be written as `\operatorname{Var}`, `\operatorname{Cov}`, and so on, even though they compile in a `.tex` document.

Tables under about 15 rows are inlined as markdown with consistent alignment and units in the headers; larger or code-generated tables link to their output file rather than being pasted in. Raw HTML is reserved for layouts markdown cannot express (flow diagrams, side-by-side cards, styled callouts). It is dashboard-first: the dashboard keeps `class` and `style` but strips scripts, iframes, and event handlers, and GitHub strips the styling entirely, so anything HTML-heavy must still read correctly unstyled.

To catch the two silent-render traps before you commit, run the self-diagnose CLI on any markdown file. It only reports, never edits:

```
uv run --script <skill-dir>/scripts/check_markdown.py path/to/file.md
```

where `<skill-dir>` is the directory holding the skill's `SKILL.md`. It is stdlib-only, so `python3 <skill-dir>/scripts/check_markdown.py …` works as a uv-free fallback.

Two references load on demand. Load [`references/rich-content.md`](skills/report-in-markdown/references/rich-content.md) when the markdown contains figures — it covers the `attachments/` directory, PDF-to-PNG conversion, descriptive captions, and citing the original source path so a reader can regenerate the figure. Load [`references/baseline-io.md`](skills/report-in-markdown/references/baseline-io.md) when you are producing a permanent standalone artifact that needs frontmatter, a dated filename, git-state metadata, and a resolved output path; task files and status returns do not need it.

See [`report-in-markdown`](skills/report-in-markdown/SKILL.md) for the full style guide.
