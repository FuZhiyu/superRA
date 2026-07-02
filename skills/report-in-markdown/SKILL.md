---
name: report-in-markdown
description: Markdown style guide for task files, status reports, and standalone reports. Use when writing or revising Markdown with source citations, figures, math, or tables.
user-invocable: true
---

# Report in Markdown

Apply the rules below to any markdown you write. Load references only for figures or standalone-report IO.

## File-reference rule

**Always** cite source files as **markdown links with line anchors**, not backtick-wrapped paths.

| Use case | Form |
|---|---|
| Single line | [file.py:42](file.py#L42) |
| Line range | [file.py:40-50](file.py#L40-L50) |
| Whole file | [file.py](file.py) |

Resolve paths **relative to the markdown file's directory** (use `../` as needed). 

## Math

Use KaTeX syntax for better compatibility:

- Inline: `$...$` — e.g., `The return $r_t$ is defined as ...`
- Display: `$$...$$`:

```
$$
r_t = \frac{p_t - p_{t-1}}{p_{t-1}}
$$
```

- Use `\text{...}` for words inside math mode.
- Prefer LaTeX math over Unicode for any expression that includes subscripts, superscripts, fractions, sums, or integrals.

Three patterns render as broken output in the dashboard with no error, so the renderer cannot warn you about them:

- **Blank-line-separate every display `$$` block.** Put a blank line above and below the `$$` fence lines, and none inside the block. The dashboard renders with `markdown-it-texmath` `delimiters: 'dollars'`, whose `$$` block rule cannot interrupt an open paragraph. A text line directly above the opening `$$` leaves a paragraph open, and the equation is swallowed into that paragraph instead of rendering as a standalone block.
- **Write KaTeX-undefined operators as `\operatorname{...}`.** Operators that work in a LaTeX `.tex` document — `\diag`, `\cov`, `\var`, `\corr`, `\Cov`, `\Var`, `\E`, `\plim`, `\argmin`, `\argmax`, `\sgn`, `\tr`, `\rank` — are undefined in KaTeX and render as an error. Use `\operatorname{diag}`, `\operatorname{Cov}`, etc.
- **Keep each inline `$…$` span on a single line.** Do not hard-wrap prose between an opening `$` and its closing `$`. The inline rule matches with `.` and no dotAll flag, so a span cannot close on a later line; a split span renders as raw literal text with visible backslashes. Escape a literal `$` in prose as `\$`.

The task hook runs this same check automatically on edited `.md` files under a task root and surfaces non-blocking feedback. For standalone markdown, or when no hook ran, use the self-diagnose CLI (it only reports, never edits):

```
uv run --script <skill-dir>/scripts/check_markdown.py path/to/file.md
```

where `<skill-dir>` is the directory holding this `SKILL.md`. Stdlib-only, so `python3 <skill-dir>/scripts/check_markdown.py …` also works.

## Tables

Inline small results (< ~15 rows) as markdown tables. For larger or code-generated tables, link to the output file instead:

```markdown
See [output/summary_stats.csv](../output/summary_stats.csv).
```

When inlining, keep alignment syntax consistent and include units in headers:

```markdown
| Variable      | Mean   | SD    | N       |
|---------------|-------:|------:|--------:|
| Return (%)    |   0.08 |  1.24 | 252,341 |
| Volume (M)    |  12.40 |  8.15 | 252,341 |
```


## Raw HTML

Reach for raw HTML only for layouts markdown cannot express — flow diagrams, side-by-side cards, styled callouts. Prefer plain markdown for prose, lists, tables, code, and math; it is more portable and easier to review.

The dashboard renders task markdown with `html: true` and sanitizes the result with DOMPurify before display, so:

- **`class` and `style` survive** — style inline with `style="..."`, or reach the dashboard CSS tokens (`var(--text)`, `var(--bg-alt)`, etc.) via `class`/`style` so a diagram themes with the page.
- **Scripts, iframes, event handlers (`onclick=`, `onerror=`), and `javascript:` URLs are stripped.** Anything interactive silently will not survive — build static layouts, not widgets.

HTML-heavy content is **dashboard-first**: GitHub's own markdown renderer strips `style` (and most attributes), so a styled HTML block that looks right in the dashboard renders unstyled on GitHub. Keep the meaning legible without the styling, or keep such content out of files meant to be read on GitHub.

## References

- `references/rich-content.md` — figure handling (PDF→PNG, relative-path embedding). Load when the output includes figures.
- `references/baseline-io.md` — frontmatter spec, filename convention, output-path resolution. Load for permanent standalone artifacts (reports, rendered notes, dashboards); not required for task files or status returns.
