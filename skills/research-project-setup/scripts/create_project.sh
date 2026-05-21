#!/bin/bash

# Project template generator for academic research projects.
#
# Usage:
#   ./create_project.sh <project-name-or-path> [flags]
#
# Flags (all optional):
#   --share-path PATH    Where the share folder (Data/Notes/Output) lives.
#                        Default: sibling <Name>-Share/.
#   --no-superra         Skip the superRA plugin declaration in .claude/settings.json
#                        and .codex/config.toml.
#   --no-codex           Skip copying .codex/ entirely.
#   --with-overleaf      Copy overleaf-sync so Paper/ can sync to an Overleaf project.
#   --with-ci            Copy GitHub Actions workflows (LaTeX auto-compile + publish).
#
# Defaults: superRA + Codex on, Overleaf + CI off.

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Defaults
SHARE_PATH=""
NO_SUPERRA="false"
NO_CODEX="false"
WITH_OVERLEAF="false"
WITH_CI="false"
PROJECT_PATH=""

# Flag parser
while [ $# -gt 0 ]; do
    case "$1" in
        --share-path)
            SHARE_PATH="$2"
            shift 2
            ;;
        --no-superra)
            NO_SUPERRA="true"
            shift
            ;;
        --no-codex)
            NO_CODEX="true"
            shift
            ;;
        --with-overleaf)
            WITH_OVERLEAF="true"
            shift
            ;;
        --with-ci)
            WITH_CI="true"
            shift
            ;;
        -h|--help)
            sed -n '3,18p' "$0"
            exit 0
            ;;
        --*)
            echo "error: unknown flag '$1'" >&2
            exit 1
            ;;
        *)
            if [ -z "$PROJECT_PATH" ]; then
                PROJECT_PATH="$1"
            else
                echo "error: unexpected extra positional arg '$1'" >&2
                exit 1
            fi
            shift
            ;;
    esac
done

if [ -z "$PROJECT_PATH" ]; then
    echo "error: project name (or path) is required" >&2
    sed -n '3,18p' "$0" >&2
    exit 1
fi

# Extract directory and project name
if [[ "$PROJECT_PATH" == */* ]]; then
    PROJECT_DIR=$(dirname "$PROJECT_PATH")
    PROJECT_NAME=$(basename "$PROJECT_PATH")
    mkdir -p "$PROJECT_DIR"
    cd "$PROJECT_DIR"
else
    PROJECT_NAME="$PROJECT_PATH"
    PROJECT_DIR="."
fi

# Resolve share path (default: sibling <Name>-Share/)
if [ -z "$SHARE_PATH" ]; then
    SHARE_PATH="$(pwd)/${PROJECT_NAME}-Share"
else
    # Convert to absolute path if relative
    case "$SHARE_PATH" in
        /*) ;;
        *) SHARE_PATH="$(pwd)/$SHARE_PATH" ;;
    esac
fi

echo "Creating project: $PROJECT_NAME"
echo "  Code location:  $(pwd)/$PROJECT_NAME"
echo "  Share location: $SHARE_PATH"
echo "  Flags: superRA=$([ "$NO_SUPERRA" = "true" ] && echo off || echo on), codex=$([ "$NO_CODEX" = "true" ] && echo off || echo on), overleaf=$WITH_OVERLEAF, ci=$WITH_CI"

# Create share folder
mkdir -p "$SHARE_PATH"/{Notes,Data,Output}

# Copy .env to Notes/ in the share folder
if [ -f "$SCRIPT_DIR/ProjectExample/Notes/.env" ]; then
    cp "$SCRIPT_DIR/ProjectExample/Notes/.env" "$SHARE_PATH/Notes/.env"
    sed -i '' "s/ProjectExample/$PROJECT_NAME/g" "$SHARE_PATH/Notes/.env"
fi

# Create code repository
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

echo "Creating code project directories..."
mkdir -p Code Paper/Figures Paper/Tables Slides
touch Paper/Figures/.gitkeep Paper/Tables/.gitkeep

# Record share path (per-machine, gitignored)
echo "$SHARE_PATH" > .share-path

# Create Python pyproject.toml from template
echo "Creating Python environment..."
if [ -f "$SCRIPT_DIR/ProjectExample/pyproject.toml" ]; then
    cp "$SCRIPT_DIR/ProjectExample/pyproject.toml" pyproject.toml
    sed -i '' "s/projectexample/$(echo $PROJECT_NAME | tr '[:upper:]' '[:lower:]' | tr ' ' '-')/g" pyproject.toml
    sed -i '' "s/ProjectExample/$PROJECT_NAME/g" pyproject.toml
fi

# Create setup_mac.sh from template
echo "Creating setup script..."
if [ -f "$SCRIPT_DIR/ProjectExample/setup_mac.sh" ]; then
    cp "$SCRIPT_DIR/ProjectExample/setup_mac.sh" setup_mac.sh
    sed -i '' "s/ProjectExample/$PROJECT_NAME/g" setup_mac.sh
    chmod +x setup_mac.sh
fi

# Create README from template
echo "Creating README..."
if [ -f "$SCRIPT_DIR/README-template.md" ]; then
    cp "$SCRIPT_DIR/README-template.md" README.md
    sed -i '' "s/ProjectExample/$PROJECT_NAME/g" README.md
fi

# Create CLAUDE.md from template
echo "Creating CLAUDE.md..."
if [ -f "$SCRIPT_DIR/CLAUDE-template.md" ]; then
    cp "$SCRIPT_DIR/CLAUDE-template.md" CLAUDE.md
    sed -i '' "s/ProjectExample/$PROJECT_NAME/g" CLAUDE.md
fi

# Copy .claude folder
echo "Copying .claude configuration..."
if [ -d "$SCRIPT_DIR/ProjectExample/.claude" ]; then
    cp -r "$SCRIPT_DIR/ProjectExample/.claude" .claude
    find .claude -type f \( -name "*.md" -o -name "*.json" -o -name "*.toml" -o -name "*.sh" \) \
        -exec sed -i '' "s/ProjectExample/$PROJECT_NAME/g" {} \;
fi

# Strip superRA from .claude/settings.json if --no-superra
if [ "$NO_SUPERRA" = "true" ] && [ -f .claude/settings.json ]; then
    python3 - <<'PY'
import json
p = '.claude/settings.json'
with open(p) as f: cfg = json.load(f)
cfg.pop('enabledPlugins', None)
cfg.pop('extraKnownMarketplaces', None)
with open(p, 'w') as f: json.dump(cfg, f, indent=2)
PY
fi

# Copy .codex/ unless --no-codex
if [ "$NO_CODEX" != "true" ] && [ -d "$SCRIPT_DIR/ProjectExample/.codex" ]; then
    echo "Copying .codex configuration..."
    cp -r "$SCRIPT_DIR/ProjectExample/.codex" .codex
    find .codex -type f \( -name "*.md" -o -name "*.json" -o -name "*.toml" \) \
        -exec sed -i '' "s/ProjectExample/$PROJECT_NAME/g" {} \;
    # Strip superRA plugin from .codex/config.toml if --no-superra
    if [ "$NO_SUPERRA" = "true" ] && [ -f .codex/config.toml ]; then
        python3 - <<'PY'
import re
p = '.codex/config.toml'
with open(p) as f: txt = f.read()
# Drop the marketplaces.superra, plugins."superra@superra", and both
# agents.superra_* blocks. Each TOML block runs until the next [section] header.
for header in (r'\[marketplaces\.superra\]',
               r'\[plugins\."superra@superra"\]',
               r'\[agents\.superra_implementer\]',
               r'\[agents\.superra_reviewer\]'):
    txt = re.sub(rf'^{header}[^\[]*', '', txt, flags=re.MULTILINE)
# Collapse triple-blank-line runs
txt = re.sub(r'\n{3,}', '\n\n', txt)
with open(p, 'w') as f: f.write(txt)
PY
    fi
fi

# AGENTS.md symlink
[ -f CLAUDE.md ] && ln -sfn CLAUDE.md AGENTS.md

# Copy .mcp.json
if [ -f "$SCRIPT_DIR/ProjectExample/.mcp.json" ]; then
    cp "$SCRIPT_DIR/ProjectExample/.mcp.json" .mcp.json
    sed -i '' "s/ProjectExample/$PROJECT_NAME/g" .mcp.json
fi

# Optional: Overleaf sync script
if [ "$WITH_OVERLEAF" = "true" ] && [ -f "$SCRIPT_DIR/ProjectExample/overleaf-sync" ]; then
    cp "$SCRIPT_DIR/ProjectExample/overleaf-sync" overleaf-sync
    chmod +x overleaf-sync
    echo "Copied overleaf-sync. Wire it up with: git remote add overleaf <Overleaf-git-URL>"
fi

# Optional: GitHub Actions CI workflows
if [ "$WITH_CI" = "true" ] && [ -d "$SCRIPT_DIR/ProjectExample/.github" ]; then
    cp -r "$SCRIPT_DIR/ProjectExample/.github" .github
    echo "Copied .github/workflows/. Configure repo variables (PAPER_DIR, PAPER_TEX, PAPER_TARGET_REPO) on GitHub as needed."
fi

# Create symlinks from share folder
echo "Creating symlinks to share folder..."
for sub in Data Notes Output; do
    if [ -d "$SHARE_PATH/$sub" ]; then
        ln -sfn "$SHARE_PATH/$sub" "./$sub"
        echo "  $sub -> $SHARE_PATH/$sub"
    fi
done

# Initialize git repository
echo "Initializing git repository..."
git init

# Create .gitignore from template
if [ -f "$SCRIPT_DIR/ProjectExample/.gitignore" ]; then
    cp "$SCRIPT_DIR/ProjectExample/.gitignore" .gitignore
fi

# Automatically run setup
echo ""
echo "🔧 Running automatic setup..."
./setup_mac.sh

echo ""
echo "✅ Project template created and set up successfully!"
echo ""
echo "📁 Project structure:"
echo "📁 $SHARE_PATH/             - Share folder (data, notes, intermediate outputs)"
echo "   ├── Notes/                - Research notes"
echo "   ├── Data/                 - Datasets"
echo "   └── Output/               - Analysis results"
echo ""
echo "📁 $PROJECT_NAME/            - Git repository"
echo "   ├── Code/                 - Source code"
echo "   ├── Paper/                - LaTeX manuscript"
echo "   │   ├── Figures/          - Publication-quality figures"
echo "   │   └── Tables/           - Publication-quality tables"
echo "   ├── Slides/               - Presentation materials"
echo "   ├── Data, Notes, Output   - Symlinks to share folder"
echo "   ├── .share-path           - Records share folder location (gitignored)"
echo "   ├── pyproject.toml        - Python environment"
echo "   ├── setup_mac.sh          - Setup script"
echo "   └── README.md             - Setup instructions"
[ "$WITH_OVERLEAF" = "true" ] && echo "   ├── overleaf-sync         - Overleaf subtree sync"
[ "$WITH_CI" = "true" ]       && echo "   └── .github/workflows/    - LaTeX CI"
echo ""
echo "🎉 Next steps:"
echo "1. Share folder is at $SHARE_PATH — share via Dropbox or similar"
echo "2. Push $PROJECT_NAME/ to GitHub and share with coauthors"
echo "3. Coauthors: clone the repo, run ./setup_mac.sh (will prompt for their machine's share path)"
[ "$WITH_OVERLEAF" = "true" ] && echo "4. Wire up Overleaf: git remote add overleaf https://git@git.overleaf.com/<PROJECT_ID>"
echo ""
echo "Ready to start coding in $PROJECT_NAME/Code/"
