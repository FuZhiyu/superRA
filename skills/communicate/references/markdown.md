# Markdown Mechanics

## Cite files as links with line anchors, never as backticked paths

| Use case | Form |
|---|---|
| Single line | [file.py:42](file.py#L42) |
| Line range | [file.py:40-50](file.py#L40-L50) |
| Whole file | [file.py](file.py) |

Resolve paths relative to the markdown file's directory (use `../` as needed).

## Math renders through KaTeX

- Inline: `$...$` — e.g., `The return $r_t$ is defined as ...`
- Display: `$$...$$`:

```
$$
r_t = \frac{p_t - p_{t-1}}{p_{t-1}}
$$
```

- Use `\text{...}` for words inside math mode.
- Prefer LaTeX math over Unicode for subscripts, superscripts, fractions, sums, integrals.

Three patterns render broken in the dashboard with no error:

- **Blank-line-separate every display `$$` block.** A blank line above and below the `$$` fence lines, none inside. The dashboard's `markdown-it-texmath` (`delimiters: 'dollars'`) `$$` block rule cannot interrupt an open paragraph, so a text line directly above the opening `$$` swallows the equation into that paragraph.
- **Write KaTeX-undefined operators as `\operatorname{...}`.** `\diag`, `\cov`, `\var`, `\corr`, `\Cov`, `\Var`, `\E`, `\plim`, `\argmin`, `\argmax`, `\sgn`, `\tr`, `\rank` work in a `.tex` document but are undefined in KaTeX and render as an error. Use `\operatorname{diag}`, `\operatorname{Cov}`, etc.
- **Keep each inline `$…$` span on a single line.** Never hard-wrap between an opening `$` and its closing `$` — the inline rule has no dotAll flag, so a split span renders as raw literal text with visible backslashes. Escape a literal `$` in prose as `\$`.

The task hook runs this check on edited `.md` files under a task root and surfaces non-blocking feedback. For standalone Markdown, or when no hook ran, use the self-diagnose CLI; it reports but never edits:

```
uv run --script <skill-dir>/scripts/check_markdown.py path/to/file.md
```

where `<skill-dir>` is the directory holding this `SKILL.md`. Stdlib-only, so `python3 <skill-dir>/scripts/check_markdown.py …` also works.

## Inline small tables, link large ones

Under ~15 rows goes inline. Larger or code-generated tables become a link:

```markdown
See [output/summary_stats.csv](../output/summary_stats.csv).
```

When inlining, keep alignment syntax consistent and put units in the headers:

```markdown
| Variable      | Mean   | SD    | N       |
|---------------|-------:|------:|--------:|
| Return (%)    |   0.08 |  1.24 | 252,341 |
| Volume (M)    |  12.40 |  8.15 | 252,341 |
```

## Figures

### The attachments directory (`ATTACH_DIR`)

The caller supplies the target `attachments/` directory — substitute the actual path when embedding. No caller value: default to `attachments/` next to the output file:

- Task `## Results` → next to the task's `task.md` (see `task-tree/references/task-file-contract.md` §Figure Embedding).
- Matured task results → next to the task's `task.md`.
- Standalone report → next to the report file.

```bash
mkdir -p "${ATTACH_DIR}"
```

### Materialize figures

Task figures are written directly into the task's `attachments/` by the analysis script — no copying. Permanent and standalone reports copy figures into a new attachments folder so the artifact is self-contained:

**PDF figures:** convert to PNG first, then save:

```bash
uv run --no-project --with pdf2image python -c "
from pdf2image import convert_from_path
images = convert_from_path('path/to/figure.pdf')
images[0].save('${ATTACH_DIR}/description.png')
"
```

**PNG / JPG / other raster:** copy directly:

```bash
cp path/to/figure.png "${ATTACH_DIR}/description.png"
```

### Embed

```markdown
![Descriptive caption](ATTACH_DIR/description.png)

Source: [Original](relative/path/to/original/figure.pdf)
```

- **Caption:** describe the figure, never "Figure 1" — it is the figure's documentation for skimmers.
- **Source line:** the original path the analysis script produced, not the copy in `ATTACH_DIR`, so a future reader can regenerate the figure.

## Raw HTML is dashboard-only

Reach for it only for layouts markdown cannot express — flow diagrams, side-by-side cards, styled callouts. Prose, lists, tables, code, and math stay plain markdown.

The dashboard renders task markdown with `html: true` and sanitizes the result with DOMPurify before display, so:

- **`class` and `style` survive** — style inline with `style="..."`, or reach the dashboard CSS tokens (`var(--text)`, `var(--bg-alt)`, etc.) via `class`/`style` so a diagram themes with the page.
- **Scripts, iframes, event handlers (`onclick=`, `onerror=`), and `javascript:` URLs are stripped.** Nothing interactive survives — build static layouts, not widgets.

GitHub's renderer strips `style` and most attributes, so a block that looks right in the dashboard renders unstyled there. Keep the meaning legible without the styling, or keep such content out of GitHub-read files.
