---
name: report-in-markdown
description: Markdown style guide for agents writing task files, status reports, or standalone markdown reports, with inline rules for source-file citations, LaTeX math, and tables, plus optional references for figures and standalone-report IO.
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


## References

- `references/rich-content.md` — figure handling (PDF→PNG, relative-path embedding). Load when the output includes figures.
- `references/baseline-io.md` — frontmatter spec, filename convention, output-path resolution. Load for permanent standalone artifacts (reports, rendered notes, dashboards); not required for task files or status returns.
