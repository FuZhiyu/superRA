# Julia Notebook Rendering with QuartoNotebookRunner

## Why Not Jupytext

Jupytext renders Julia scripts through a Jupyter kernel where `@__DIR__`
resolves to `pwd()`, not the script's directory. This breaks two patterns:

1. **`include("sibling.jl")`** — looks in `pwd()` instead of the script's directory
2. **Project-root-relative data paths** — can't set `pwd()` to project root
   AND have `@__DIR__` point to the script's directory simultaneously

## QuartoNotebookRunner.jl

[QuartoNotebookRunner](https://github.com/PumasAI/QuartoNotebookRunner.jl)
executes `.jl` scripts as Julia files, preserving both path contexts:

- `@__DIR__` → script's parent directory (for `include()`)
- `pwd()` → configurable via `cwd` option (for data paths)

### Setup

```julia
using Pkg
Pkg.add("QuartoNotebookRunner")
```

### Render

From the project root:

```bash
julia --project=. -e '
  using QuartoNotebookRunner
  s = QuartoNotebookRunner.Server()
  QuartoNotebookRunner.run!(s,
      "Code/Analysis/01_clean.jl";
      output = "Output/Analysis/01_clean.ipynb",
      options = Dict{String,Any}("cwd" => pwd()),
  )
'
```

Notes on the API:

- `run!` requires a `Server()` object as its first argument — it does not accept a bare path string.
- `options` must be typed `Dict{String,Any}`, not `Dict{String,String}` — values are heterogeneous.
- No `close(s)` is needed; the Julia process exits when the `-e` block finishes.

`cwd => pwd()` ensures data paths resolve relative to the project root
while `@__DIR__` independently resolves to the script's directory.

### Script Format

Same percent-format cell markers as Python:

```julia
# %% [markdown]
# ## Load Data
# Source: Penn World Table 10.0

# %%
using CSV, DataFrames
df = CSV.read("Data/pwt.csv", DataFrame)
println("Shape: $(size(df))")

# Include shared utilities — @__DIR__ resolves correctly
include(joinpath(@__DIR__, "utils.jl"))
```

### Rich display: tables and figures

Julia's rich-display pipeline works the same way as Python's: an object
renders with its HTML / image MIME **only** when it is the cell's final
expression. `println` and `print` force the text MIME and lose formatting.

**DataFrames.** `DataFrames.jl` registers `show(io, MIME"text/html"(), df)`,
which the notebook kernel picks up for last-expression values:

```julia
# good — HTML table
describe(df[:, [:mv, :w]])

# bad — text fallback
println(describe(df[:, [:mv, :w]]))
```

**Plots.jl / Makie.jl / CairoMakie.jl.** Leave the plot object bare:

```julia
using Plots
p = plot(x, y, title = "Returns")
p
```

- Do **not** wrap in `display(p)` — that bypasses MIME negotiation. The
  bare form lets the kernel pick PNG/SVG/HTML.
- `savefig(p, "Output/fig.png")` is for producing standalone image files
  (figures committed to `Output/`), not for notebook rendering. You can
  do both: `savefig(p, "Output/fig.png"); p` saves to disk **and** returns
  `p` as the last expression so the notebook also shows it inline.

**One rich object per cell.** Same rule as Python — split the cell if you
need to show two tables or two figures.

**Direct-script fallback.** When the same `.jl` file runs under plain
`julia --project=. script.jl` (no QuartoNotebookRunner), rich objects emit
their text repr to stdout. That is acceptable: for tables and figures, the
rendered notebook is the authoritative artifact; direct-script output only
needs to confirm the object was produced without erroring.

### Path Convention

- **Data files**: relative to `pwd()` / project root — `"Data/filename.csv"`
- **Included scripts**: relative to script location — `joinpath(@__DIR__, "sibling.jl")`
- **Output**: specify explicitly in the `output` kwarg
