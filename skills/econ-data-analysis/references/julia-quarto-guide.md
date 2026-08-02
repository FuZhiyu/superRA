# Julia Notebook Rendering with QuartoNotebookRunner

## Why Not Jupytext

Jupytext renders Julia through a Jupyter kernel where `@__DIR__` resolves to `pwd()`, breaking two patterns:

1. **`include("sibling.jl")`** — looks in `pwd()`, not the script's directory
2. **Project-root-relative data paths** — `pwd()` at project root and `@__DIR__` at the script's directory cannot hold at once

## QuartoNotebookRunner.jl

[QuartoNotebookRunner](https://github.com/PumasAI/QuartoNotebookRunner.jl) executes `.jl` scripts as Julia files, preserving both path contexts:

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

API notes:

- `run!` takes a `Server()` object first — not a bare path string.
- `options` must be `Dict{String,Any}`; values are heterogeneous.
- No `close(s)` — the Julia process exits when the `-e` block finishes.
- `cwd => pwd()` resolves data paths against the project root while `@__DIR__` independently resolves to the script's directory.

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

An object renders with its HTML / image MIME **only** as the cell's final expression; `println` and `print` force the text MIME and lose formatting.

**DataFrames.** `DataFrames.jl` registers `show(io, MIME"text/html"(), df)`, which the kernel picks up for last-expression values:

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

- Do **not** wrap in `display(p)` — it bypasses MIME negotiation; the bare form lets the kernel pick PNG/SVG/HTML.
- `savefig(p, "Output/fig.png")` produces a standalone image file, not notebook output. Both at once: `savefig(p, "Output/fig.png"); p`.

**One rich object per cell.** Split the cell for two tables or two figures.

**Direct-script fallback.** Under plain `julia --project=. script.jl`, rich objects emit their text repr to stdout. Acceptable — the rendered notebook is the authoritative artifact for tables and figures; direct-script output only confirms the object was produced without erroring.

### Path Convention

- **Data files** — relative to `pwd()` / project root: `"Data/filename.csv"`
- **Included scripts** — relative to script location: `joinpath(@__DIR__, "sibling.jl")`
- **Output** — explicit in the `output` kwarg
