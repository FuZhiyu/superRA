# Jupytext Percent Format Guide

How to write and render analysis scripts in jupytext percent format.

## Why percent format

- **Git-friendly**: `.py`/`.jl` files diff cleanly; notebooks do not
- **Human-readable**: code + narrative in one file, no JSON wrapping
- **Executable**: runs as a normal script or converts to a notebook
- **Same syntax** for Python and Julia

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
- Markdown cell before each operation explaining what and why
- `print()` for text diagnostics (row counts, shape, messages) — works in
  both direct-script and notebook execution
- Bare last expression for **rich objects** (DataFrames, figures) — only
  that position triggers HTML / image MIME rendering

### Rich display — Python specifics

**DataFrames and summary tables.** Pandas registers `_repr_html_` so a
DataFrame as the cell's final expression renders as an HTML table with
column alignment, scroll overflow, and Jupyter theming. Wrapping it in
`print()` falls back to the text `__repr__`:

```python
# good — HTML table
df[["mv", "w"]].describe(percentiles=[.01, .5, .99])

# bad — ASCII, loses formatting
print(df[["mv", "w"]].describe())
```

When tables get truncated, adjust display options once at the top of the
notebook rather than per-cell:

```python
import pandas as pd
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)
```

**Matplotlib figures.** Prefer returning the `Figure` object as the cell's
last expression over calling `plt.show()`:

```python
# preferred — Jupyter chooses retina/SVG/PNG via _repr_html_
fig, ax = plt.subplots()
ax.plot(x, y)
fig
```

`plt.show()` also works in a notebook but bypasses the MIME negotiation;
stick to the trailing-`fig` form unless you explicitly need `show()`'s
blocking behavior in a script context.

**Mid-cell rich output.** The "one rich object per cell" rule is the
default. When you genuinely need two rich objects in the same cell, use
`IPython.display.display` as the explicit escape hatch:

```python
from IPython.display import display
display(df_top)
display(df_bottom)
```

Reach for this sparingly — splitting the cell is almost always cleaner.

## Execution

Convert and execute in one step. `--set-kernel` is always required — it
writes the kernel name into the notebook metadata (list available names
with `jupyter kernelspec list`).

### Python

If `uv` is available, prefer `uv run` — it activates the project's `.venv`
so the kernel uses the correct packages. Requires `jupytext`, `nbconvert`,
and `ipykernel` as dev dependencies in `pyproject.toml`.

```bash
uv run jupytext --set-kernel python3 --to notebook --execute script.py

# Without uv (uses whichever environment jupytext is installed in):
jupytext --set-kernel python3 --to notebook --execute script.py
```

### Julia

The IJulia kernel spec includes `--project=@.`, which activates the nearest
`Project.toml` automatically. Just match the installed kernel name:

```bash
jupytext --set-kernel julia-1.12 --to notebook --execute script.jl
```

### Output path

Use `-o` to write the notebook to a specific location (e.g., a project's
output directory):

```bash
jupytext --set-kernel python3 --to notebook --execute script.py -o Output/script.ipynb
```

### Working directory

Jupytext sets the working directory to the script's parent directory by default.
Relative paths like `Data/file.csv` resolve relative to where the script lives.

### Sandbox note

Execution requires a Jupyter kernel, which binds local sockets. In Claude Code,
the sandbox blocks socket binding. Two options:
1. Suggest the user type `! uv run jupytext ...` (the `!` prefix bypasses sandbox)
2. Run with sandbox disabled (Claude Code will prompt for permission)

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
- **Optionally commit `.ipynb`** for rendered outputs, or `.gitignore` and
  re-render on demand

## Setup

### Installation

```bash
# Python (global)
uv pip install jupytext jupyter nbconvert ipykernel
python -m ipykernel install --user --name python3

# Python (per-project — add to pyproject.toml dev-dependencies)
# jupytext, nbconvert, ipykernel

# Julia (run in Julia REPL)
# using Pkg; Pkg.add("IJulia")
```

Verify: `jupyter kernelspec list`

### Troubleshooting

- **"No kernel found"**: use `--set-kernel <name>` with a name from `jupyter kernelspec list`
- **Sandbox blocks execution**: kernels need sockets — use `!` prefix or disable sandbox
- **Wrong Python packages**: use `uv run jupytext ...` to activate the project `.venv`
- **Format not recognized**: ensure file starts with `# %%` and jupytext is installed
- **Pairing not working**: check `jupytext.toml` or notebook metadata for correct `formats` string
