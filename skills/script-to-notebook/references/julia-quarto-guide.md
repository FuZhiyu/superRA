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

### Path Convention

- **Data files**: relative to `pwd()` / project root — `"Data/filename.csv"`
- **Included scripts**: relative to script location — `joinpath(@__DIR__, "sibling.jl")`
- **Output**: specify explicitly in the `output` kwarg
