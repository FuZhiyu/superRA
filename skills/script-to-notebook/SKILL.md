---
name: script-to-notebook
description: >
  Utility (IMPLEMENT+VALIDATE phase, auto-loaded alongside econ-data-analysis
  by implementer/reviewer agents when the stage touches analysis code). Use
  when writing analysis scripts intended for notebook rendering, or when
  rendering existing scripts as notebooks. Covers cell organization, markdown
  narrative, equation formatting, and language-specific rendering (Python via
  jupytext, Julia via QuartoNotebookRunner).
user-invocable: true
---

# Script to Notebook

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

## Favor Explicit Printing

Always use `print()`/`println()` for diagnostics — row counts, shape, summary
statistics, validation checks. This ensures agents running the script directly
(not as a notebook) see the same output as rendered notebooks.

Last-expression display only works in notebook/REPL contexts. Don't rely on it
as the sole output mechanism. When in doubt, `print()`.

```python
# Good — works in both script and notebook
print(f"Shape: {df.shape}")
print(f"Funds: {df['fund_id'].nunique()}")
print(df[["market_value", "weight"]].describe(percentiles=[.01, .05, .5, .95, .99]).to_string())

# Avoid as sole output — invisible when running as script
df.describe()  # only displays in notebook/REPL
```

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
