# Jupytext Percent Format Guide

Writing and rendering analysis scripts in jupytext percent format. Same syntax for Python and Julia; the `.py`/`.jl` file runs as a normal script and converts to a notebook.

## Syntax

### Cell markers

```
# %%                        ← code cell
# %% [markdown]             ← narrative cell
# %% Optional title         ← named code cell
```

### Markdown cells

Line-comment style:
```python
# %% [markdown]
# ## Section Heading
#
# Narrative text.
```

Triple-quote style (preferred for longer blocks):
```python
# %% [markdown]
"""
## Section Heading

Longer narrative with multiple paragraphs.
"""
```

### Writing tips

- One cell per logical operation (load, merge, filter, construct)
- Markdown cell before each operation: what and why
- `print()` for text diagnostics (row counts, shape, messages) — works in direct-script and notebook execution alike
- Bare last expression for **rich objects** (DataFrames, figures) — only that position triggers HTML / image MIME rendering

### Rich display — Python specifics

**DataFrames and summary tables.** A DataFrame as the cell's final expression renders as an HTML table (column alignment, scroll overflow, Jupyter theming) via pandas' `_repr_html_`. `print()` falls back to the text `__repr__`:

```python
# good — HTML table
df[["mv", "w"]].describe(percentiles=[.01, .5, .99])

# bad — ASCII, loses formatting
print(df[["mv", "w"]].describe())
```

Truncated tables: adjust display options once at the top of the notebook, not per-cell:

```python
import pandas as pd
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)
```

**Matplotlib figures.** Return the `Figure` object as the cell's last expression rather than calling `plt.show()`:

```python
# preferred — Jupyter chooses retina/SVG/PNG via _repr_html_
fig, ax = plt.subplots()
ax.plot(x, y)
fig
```

`plt.show()` works too but bypasses MIME negotiation — use the trailing-`fig` form unless you need `show()`'s blocking behavior in a script context.

**Mid-cell rich output.** Two rich objects in one cell: `IPython.display.display` is the explicit escape hatch.

```python
from IPython.display import display
display(df_top)
display(df_bottom)
```

Splitting the cell is almost always cleaner.

## Execution

Convert and execute in one step. `--set-kernel` is always required — it writes the kernel name into notebook metadata (names from `jupyter kernelspec list`).

### Python

Execution needs one environment holding both the rendering tools (`jupytext`, `nbconvert`, `ipykernel`) and the script's analysis packages, so the kernel's imports resolve. How it is provided is project-specific — activated venv, global install, or `uv run` against the project. Match the project's existing setup.

```bash
jupytext --set-kernel python3 --to notebook --execute script.py
```

`uv run` (without `--script`) discovers the surrounding project and provisions its `.venv` — fine when rendering inside a research project, not for throwaway project-independent commands.

### Julia

The IJulia kernel spec includes `--project=@.`, activating the nearest `Project.toml`. Match the installed kernel name:

```bash
jupytext --set-kernel julia-1.12 --to notebook --execute script.jl
```

### Output path

`-o` writes the notebook to a specific location:

```bash
jupytext --set-kernel python3 --to notebook --execute script.py -o Output/script.ipynb
```

### Working directory

Jupytext defaults the working directory to the script's parent, so `Data/file.csv` resolves relative to the script's location.

### Sandbox note

Kernels bind local sockets, which the Claude Code sandbox blocks. Two options:
1. Suggest the user type `! jupytext ...` — the `!` prefix runs in the user's own session, so their project environment applies
2. Run with sandbox disabled (Claude Code prompts for permission)

## Pairing and Sync

Auto-sync a script with its notebook counterpart:

```bash
jupytext --set-formats ipynb,py:percent script.py   # Python
jupytext --set-formats ipynb,jl:percent script.jl   # Julia
jupytext --sync script.py                           # sync after editing
jupytext --sync script.py -o Output/script.ipynb    # sync to specific path
```

## Export

```bash
jupyter nbconvert --to html script.ipynb
jupyter nbconvert --to html script.ipynb --output-dir Output/
```

## Version Control

- **Commit the `.py`/`.jl` script** — diffs cleanly
- **`.ipynb` optional** — commit for rendered outputs, or `.gitignore` and re-render on demand

## Setup

### Installation

```bash
# Python (global)
uv pip install jupytext jupyter nbconvert ipykernel
python -m ipykernel install --user --name python3

# Python (per-project — add jupytext, nbconvert, ipykernel to the project's
# own dependency manifest, following whatever setup that project uses)

# Julia (run in Julia REPL)
# using Pkg; Pkg.add("IJulia")
```

Verify: `jupyter kernelspec list`

### Troubleshooting

- **"No kernel found"** — `--set-kernel <name>` with a name from `jupyter kernelspec list`
- **Sandbox blocks execution** — kernels need sockets; use the `!` prefix or disable sandbox
- **Wrong Python packages** — run jupytext in the environment holding the project's packages (project venv or the project's runner)
- **Format not recognized** — file must start with `# %%`, jupytext installed
- **Pairing not working** — check `jupytext.toml` or notebook metadata for the correct `formats` string
