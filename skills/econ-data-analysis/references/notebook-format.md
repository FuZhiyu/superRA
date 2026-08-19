# Notebook Format

> Load whenever analysis scripts are being written or rendered. Per-language setup: `jupytext-guide.md` (Python), `julia-quarto-guide.md` (Julia).

## When to Use

Analysis scripts producing diagnostic output — data loading, cleaning, variable construction, summary statistics. Notebook rendering interleaves code, narrative, and outputs in one readable document.

**NOT** for runner scripts, utility scripts, or pipeline orchestrators — those use standard script format.

## Cell Organization

- One logical operation per code cell (load, merge, filter, construct variable)
- Markdown cell before each code cell: what you're about to do and why
- Tightly coupled lines share a cell (load + immediate shape check)
- Diagnostic output separate from transformation code

## Markdown Cells

- Section headers (`##`) for major analysis stages
- Narrative explaining **intent**, not restating code
- **Expectations** before operations ("Expect ~4.7M rows, ~12K funds")
- **Findings** after operations ("Lost 3.2% of observations in merge")
- Equations: inline `$formula$`, display `$$formula$$`; define variables before first use

## Writing Discipline

Where each kind of reasoning lands:

- **Markdown cells** frame each block: what, why, expected result.
- **Inline comments** for minor decisions (winsorization percentile, filter threshold) — they document *the choice*.
- **Markdown cells with reasoning** for major decisions (excluding countries, sample period, variable definition) — they document *the reasoning behind the choice*.
- **Figures** saved alongside notebook renders. What to plot: `SKILL.md` §Describe. How to render: the sections below.

## Output: diagnostics vs rich display

Two idioms, pick by what you're showing.

- **Text diagnostics** (row counts, shapes, messages) — always `print()` / `println()`; must work in notebook and direct-script execution alike.
- **Rich objects** (DataFrames, figures) — bare as the cell's last expression. HTML / image MIME fires only in that position; `print(df)` or `println(p)` collapses to ASCII.

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

One rich object per cell — split the cell for two. Language-specific idioms (pandas options, `plt.show` vs `fig`, `savefig(p, ...); p`, `IPython.display.display`) live in the companion guides.

## Rendering: Python

Use **jupytext percent format**: `# %%` for code cells, `# %% [markdown]` for narrative.

```bash
jupytext --set-kernel python3 --to notebook --execute script.py
jupytext --set-kernel python3 --to notebook --execute script.py -o Output/script.ipynb
```

Full syntax, pairing, setup, and troubleshooting: `references/jupytext-guide.md`.

## Rendering: Julia

**Do NOT use jupytext for Julia.** Jupyter kernels collapse script location and working directory into one path context, breaking `include()` and `@__DIR__`.

Use **QuartoNotebookRunner.jl** — it preserves `@__DIR__` for `include()` and `pwd()` for data paths.

Details and setup: `references/julia-quarto-guide.md`.

## Environment and Paths

- **Python** — render in an environment carrying the project's packages so the kernel resolves imports; the project's existing setup decides how
- **Julia** — `--project=.` activates the nearest `Project.toml`
- **Data paths** — project-root-relative; confirm the working directory before rendering
- **Sandbox** — rendering requires socket binding. In Claude Code, suggest `! jupytext ...` (the `!` prefix runs in the user's own session) or run with sandbox disabled

## Version Control

- **Commit** the `.py`/`.jl` script — diffs cleanly
- `.ipynb` optional — commit for rendered-output review, or `.gitignore` and re-render on demand
