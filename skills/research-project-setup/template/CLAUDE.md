
# Academic Research Project Instructions for Claude

## Working Directory Context

You are working in the `ProjectExample/` folder, which is a Git repository. This folder contains:
- Git-tracked folders: `Code/`, `Paper/` (containing `Paper/Figures/` and `Paper/Tables/`), `Slides/`
- Symlinked folders: `Data`, `Notes`, `Output` (these point to a user-declared share folder recorded in `.share-path`, typically a Dropbox-synced directory outside the Git repo)

You can access all folders normally - the symlinks are transparent. Files in symlinked folders are NOT tracked by Git but are synced via Dropbox.

## Project Structure

This project follows a two-folder structure designed for academic research collaboration:

### Git Repository (ProjectExample/)
- `Code/` - All analysis scripts organized by task (e.g., DataCleaning/)
- `Paper/` - LaTeX documents for academic papers. Contains:
  - `Paper/Figures/` - Final presentable charts and visualizations (version-tracked)
  - `Paper/Tables/` - Final presentable result tables (version-tracked)
- `Slides/` - LaTeX presentations
- `Data`, `Notes`, `Output` - Symlinks to the share folder (path in `.share-path`, gitignored)

### Share Folder (location declared at setup, recorded in `.share-path`)
- `Data/` - Raw and processed datasets (read-only, not version-tracked)
- `Notes/` - Research notes and documentation
- `Output/` - Intermediate results organized by task matching Code/ structure

The share folder typically lives under Dropbox (or any synced storage) and can be anywhere on disk — the absolute path is per-machine. `setup_mac.sh` reads `.share-path` and recreates the three symlinks accordingly. Working with non-Git coauthors? Put the share folder alongside the Git repo or anywhere Dropbox-synced; they don't need to clone Git.

## Subfolder Organization

### Code/ Directory
Organize scripts by research tasks, not by individual runs. Examples:
- `Code/DataCleaning/` - Scripts for data preparation and cleaning
- `Code/Analysis/` - Main analysis scripts
- `Code/Robustness/` - Robustness checks and sensitivity analyses
- `Code/Visualization/` - Scripts generating figures and tables

**Important**: Edit existing scripts rather than creating new ones for variations of the same task.

### Output/ Directory
Mirror the Code/ structure with corresponding output folders:
- `Output/DataCleaning/` - Cleaned datasets, processing logs
- `Output/Analysis/` - Regression results, statistical outputs
- `Output/Robustness/` - Alternative specification results
- `Output/Visualization/` - Draft figures and tables (not final versions)

Within each Output subfolder, optionally organize by script name:
- `Output/Analysis/main_regression.py/` - Outputs from main_regression.py
- `Output/Analysis/heterogeneity.py/` - Outputs from heterogeneity.py


## Coding Style

- Code is for academic research and **NOT** meant for production-ready. Therefore, write **concise** and efficient code without safety check (`try...catch...`, `if...else`) unless it's necessary or specifically requested
- Interactive code with `# %%` cells is fine when useful; not required
- Document only when necessary, but be concise
- When producing outputs, save in `Output/` following the subfolder convention. Do **NOT** save outputs in `Paper/Figures/` or `Paper/Tables/` unless explicitly requested — those are publication-quality only
- The project is version controlled with Git. Hence, when adding new analysis, Do **NOT** create a new script per task, but **DO** edit the existing files directly
- Always execute at the project root rather than `cd` into subfolders
- When running scripts non-interactively, redirect stdout+stderr to a per-script log so each run leaves an auditable trail:
  `uv run python Code/<Module>/<script>.py 2>&1 | tee Output/<Module>/logs/<script>_stdout.txt`
- For exploratory or temporary scripts, use `scratch/` at the project root. It is gitignored. Promote anything worth keeping into `Code/<Module>/`.

## Python Environment

- Uses `uv` for dependency management
- Virtual environment located at `~/.venvs/ProjectExample`
- Run commands with `uv run <command>` (e.g., `uv run python script.py`)
- Add dependencies with `uv add package`

Whenever calling Python-related programs, use `uv` unless it is infeasible.

## superRA Workflow (Optional)

This template declares [superRA](https://github.com/FuZhiyu/superRA) as a Claude plugin (via `.claude/settings.json`) and Codex plugin (via `.codex/config.toml`). When invoking the workflow, load `superRA:using-superRA` as the master skill. The canonical handoff documents are `PLAN.md` (task tracker) and `RESULTS.md` (findings) at the project root.