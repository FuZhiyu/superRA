# Notebook Format

> Load whenever analysis scripts are being written or rendered. Covers cell organization, markdown narrative, equation formatting, and language-specific rendering. Per-language setup in companion guides `jupytext-guide.md` (Python) and `julia-quarto-guide.md` (Julia).

## When to Use

Analysis scripts that produce diagnostic output — data loading, cleaning,
variable construction, summary statistics. Format these for notebook rendering
so code, narrative, and outputs are interleaved in one readable document.

**NOT** for runner scripts, utility scripts, or pipeline orchestrators. Those
use standard script format.

## Cell Organization

- One logical operation per code cell (load, merge, filter, construct variable)
- Markdown cell before each code cell: what you're about to do and why
- Group tightly coupled lines in one cell (e.g., load + immediate shape check)
- Separate diagnostic output from transformation code

## Markdown Cells

- Section headers (`##`) for major analysis stages
- Narrative explaining **intent**, not restating code
- Document **expectations** before operations ("Expect ~4.7M rows, ~12K funds")
- Document **findings** after operations ("Lost 3.2% of observations in merge")
- Equations: inline `$formula$`, display `$$formula$$` — define variables
  before first use

## Writing Discipline

Writing the narrative is part of the work, not an afterthought. Documentation runs continuously alongside Describe, Analyze, and Validate (see `SKILL.md` §Three Concurrent Disciplines); the notebook-format mechanics above are the shape it takes. The rules below fix *where* each kind of reasoning lands.

- **Markdown cells** frame each block: what, why, expected result.
- **Inline comments** for minor decisions (winsorization percentile, filter
  threshold).
- **Markdown cells with reasoning** for major decisions (excluding countries,
  choosing sample period, variable definition).
- **Figures**: save alongside notebook renders; see `SKILL.md` §Describe for
  what to plot (distributions, relationships, temporal patterns) and the
  rendering sections below (Python jupytext / Julia QuartoNotebookRunner) for
  how to render.

The major-vs-minor-decision split is load-bearing: minor decisions inside a cell document *the choice*; major decisions in a markdown cell document *the reasoning that led to the choice*. A reviewer tracing how the analysis got to its current shape reads the markdown cells first, then the code.

## Output: diagnostics vs rich display

Two idioms, pick by what you're showing.

- **Text diagnostics** (row counts, shapes, messages) — always
  `print()` / `println()`. Must work in both notebook and direct-script
  execution.
- **Rich objects** (DataFrames, figures) — bare as the cell's last
  expression. HTML / image MIME only fires in that position; `print(df)`
  or `println(p)` collapses to ASCII and destroys formatting.

```python
print(f"Shape: {df.shape}")        # diagnostic
df.describe()                      # table, last expression
fig, ax = plt.subplots(); ax.plot(x, y); fig   # figure, last expression
```

```julia
println("Rows: ", nrow(df))        # diagnostic
describe(df)                       # table, last expression
p = plot(x, y); p                  # figure, last expression
```

One rich object per cell — split the cell if you need two. Language-specific
idioms (pandas options, `plt.show` vs `fig`, `savefig(p, ...); p`,
`IPython.display.display`) live in the reference files.

## Rendering: Python

Use **jupytext percent format**. `# %%` for code cells, `# %% [markdown]`
for narrative.

```bash
uv run jupytext --set-kernel python3 --to notebook --execute script.py
uv run jupytext --set-kernel python3 --to notebook --execute script.py -o Output/script.ipynb
```

Full syntax, pairing, setup, and troubleshooting: `references/jupytext-guide.md`.

## Rendering: Julia

**Do NOT use jupytext for Julia.** Jupytext breaks `include()` and `@__DIR__`
because Jupyter kernels collapse the two path contexts (script location vs
working directory) into one.

Use **QuartoNotebookRunner.jl** instead — it preserves `@__DIR__` for
`include()` and `pwd()` for data paths.

Details and setup: `references/julia-quarto-guide.md`.

## Environment and Paths

- **Python**: `uv run` activates project `.venv`; kernels use project packages
- **Julia**: `--project=.` activates nearest `Project.toml`
- **Data paths**: project-root-relative; confirm working directory matches
  expectations before rendering
- **Sandbox note**: notebook rendering requires socket binding — in Claude Code,
  suggest `! uv run jupytext ...` (the `!` prefix bypasses sandbox) or run
  with sandbox disabled

## Version Control

- **Commit** the `.py`/`.jl` script — diffs cleanly
- `.ipynb` optional — commit for rendered output review, or `.gitignore`
  and re-render on demand
