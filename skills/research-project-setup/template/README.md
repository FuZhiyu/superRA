# ProjectExample

Academic research project created with [ResearchProjectTemplate](https://github.com/FuZhiyu/ResearchProjectTemplate).

For design principles and best practices, see the [template documentation](https://github.com/FuZhiyu/ResearchProjectTemplate).


## Project Organization

Projects use a two-folder structure:

- `ProjectExample/` - Git repository containing code, LaTeX manuscript (with its figures/tables)
- Share folder - any path on disk (typically under Dropbox), containing data, notes, and intermediate outputs

Folders from the share folder are symlinked into `ProjectExample/`, so you work in one place with access to everything. The absolute path to the share folder is recorded in `.share-path` (gitignored, per-machine).


### Core Structure

#### In the Git Repo (`ProjectExample`)
- `Code/` - All analysis scripts and implementation
   - The subfolders are organized around different tasks, e.g., `DataCleaning`.
- `Paper/` - The LaTeX folder containing the manuscript. Final publication-quality assets live here:
  - `Paper/Figures/` - Final presentable charts and visualizations (version-tracked)
  - `Paper/Tables/` - Final presentable result tables (version-tracked)
- `Slides/` - The LaTeX folder containing slides

#### In the Share Folder (path in `.share-path`)
- `Notes/` - Research notes and documentation
- `Data/` - Raw and processed datasets. Typically read-only.
- `Output/` - Generated results and intermediate files
    - This folder is organized with subfolders that have the same names as folders under `Code`.

## Setup Instructions

### Prerequisites

- **macOS**: Homebrew installed ([https://brew.sh](https://brew.sh))
- **Git**: For cloning the repository
- **VSCode/Cursor**: Not necessary but highly recommended

### Installation

1. **Clone the repository and run setup**:
   ```bash
   git clone <repository-url> ProjectExample
   cd ProjectExample
   ./setup_mac.sh
   ```

   The setup script will:
   - Read `.share-path` (or prompt for it) and create symlinks to the share folder's `Data/`, `Notes/`, `Output/`
   - Set up `uv` to manage Python dependencies
   - Install the superRA Codex agents into `.codex/agents/` (if the project ships `.codex/`)

### Manual Setup (Alternative)

If you prefer manual setup or are not on macOS:

#### Python Environment
```bash
# Install uv (if not using macOS setup script)
pip install uv

# Sync dependencies
export UV_PROJECT_ENVIRONMENT="$HOME/.venvs/$(basename "$PWD")"
uv sync

# for vscode, set default virtual environment
cat > .vscode/settings.json << VSCODE_EOF
{
    "python.defaultInterpreterPath": "\${env:HOME}/.venvs/\${workspaceFolderBasename}/bin/python",
    "terminal.integrated.env.osx": {
        "UV_PROJECT_ENVIRONMENT": "\${env:HOME}/.venvs/\${workspaceFolderBasename}"
    },
    "python.analysis.extraPaths": [
        "\${env:HOME}/.venvs/\${workspaceFolderBasename}/lib/python*/site-packages"
    ]
}
VSCODE_EOF
```

#### Create Symbolic Links
```bash
# Record the share folder location, then create the three symlinks
echo "/absolute/path/to/your/share-folder" > .share-path
SHARE_PATH=$(cat .share-path)
for sub in Data Notes Output; do
    ln -sfn "$SHARE_PATH/$sub" "./$sub"
done
```

### Verification

After setup, you should have:
- Python environment ready with `uv sync`
- Symbolic links to shared `Data/`, `Notes/`, and `Output/` folders (resolved to the path in `.share-path`)
- Local `Code/`, `Paper/` (with `Paper/Figures/` and `Paper/Tables/`), and `Slides/` folders in the repository
