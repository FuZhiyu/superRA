#!/bin/bash

# Setup script for Mac users.
# - Installs uv (if missing)
# - Syncs Python dependencies
# - Reads .share-path (prompts if missing); recreates Data/Notes/Output symlinks
# - Installs superRA Codex agents at project scope (if .codex/ exists and a
#   local superRA clone is available)
# - Initializes git on first run

set -e

PROJECT_NAME="$(basename "$PWD")"

echo "Setting up $PROJECT_NAME project..."

# --- Homebrew check ---
if ! command -v brew &> /dev/null; then
    echo "Error: Homebrew is not installed. Please install Homebrew first: https://brew.sh"
    exit 1
fi

# --- uv install ---
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    brew install uv
else
    echo "uv is already installed, skipping installation"
fi

# Consistent venv location outside the project (so Dropbox sync doesn't break hard-links)
export UV_PROJECT_ENVIRONMENT="$HOME/.venvs/$PROJECT_NAME"

# --- Share folder resolution (do this early so symlinks exist regardless of dep failures) ---
SHARE_PATH=""
if [ -f .share-path ]; then
    SHARE_PATH="$(cat .share-path)"
    echo "Using share folder from .share-path: $SHARE_PATH"
else
    # Try sibling fallback for backward compatibility
    SIBLING="../${PROJECT_NAME}-Share"
    if [ -d "$SIBLING" ]; then
        SHARE_PATH="$(cd "$SIBLING" && pwd)"
        echo "Found sibling share folder: $SHARE_PATH"
        echo "$SHARE_PATH" > .share-path
    else
        echo ".share-path is missing and no sibling ${PROJECT_NAME}-Share/ found."
        read -p "Path to share folder (will be created if missing): " SHARE_PATH
        # Expand ~
        SHARE_PATH="${SHARE_PATH/#\~/$HOME}"
        # Make absolute
        case "$SHARE_PATH" in
            /*) ;;
            *) SHARE_PATH="$(pwd)/$SHARE_PATH" ;;
        esac
        echo "$SHARE_PATH" > .share-path
    fi
fi

# Ensure standard subdirs exist
mkdir -p "$SHARE_PATH"/{Data,Notes,Output}

# Recreate symlinks
echo "Creating symlinks..."
for sub in Data Notes Output; do
    ln -sfn "$SHARE_PATH/$sub" "./$sub"
    echo "  $sub -> $SHARE_PATH/$sub"
done

# --- superRA Codex agents (project scope) ---
# The upstream sync_codex_agents.py writes into <repo-root>/.codex/agents/, where
# repo-root is *superRA's* own clone (it carries the source specs). To make the
# agents available in THIS project, we run the installer against the superRA
# clone (refreshing those generated TOMLs) and then copy them into our project's
# .codex/agents/. Two-step because the upstream installer doesn't yet separate
# source location from install target.
if [ -d .codex/agents ]; then
    echo "Installing superRA Codex agents (project scope)..."
    SUPERRA_CANDIDATES=(
        "$HOME/package_dev/superRA"
        "$HOME/Dropbox/package_dev/superRA"
    )
    SUPERRA_DIR=""
    for candidate in "${SUPERRA_CANDIDATES[@]}"; do
        if [ -d "$candidate" ]; then
            SUPERRA_DIR="$candidate"
            break
        fi
    done

    if [ -z "$SUPERRA_DIR" ]; then
        echo "  superRA local clone not found in:"
        printf '    %s\n' "${SUPERRA_CANDIDATES[@]}"
        echo "  Skipping Codex agent install. To enable later: clone superRA and re-run setup_mac.sh,"
        echo "  or invoke the codex-superra-setup skill manually."
    else
        INSTALLER="$SUPERRA_DIR/skills/codex-superra-setup/scripts/sync_codex_agents.py"
        if [ -f "$INSTALLER" ]; then
            python3 "$INSTALLER" --scope project --repo-root "$SUPERRA_DIR" \
                >/dev/null 2>&1 \
                && {
                    cp "$SUPERRA_DIR/.codex/agents/superra_implementer.toml" .codex/agents/ \
                    && cp "$SUPERRA_DIR/.codex/agents/superra_reviewer.toml" .codex/agents/ \
                    && echo "  Installed superra_implementer and superra_reviewer into .codex/agents/"
                } || echo "  Codex agent install failed; check that $INSTALLER is current"
        else
            echo "  Installer not found at $INSTALLER — superRA clone may be outdated"
        fi
    fi
fi

# --- Python dependencies (last; isolated so failures don't block the steps above) ---
echo "Installing Python packages..."

# Set +e for the dep install block — these can fail (e.g., upstream package
# rename) without breaking the rest of setup. The user can `uv add` manually later.
set +e
uv add jupyter pandas matplotlib polars pyarrow

# zotero-mcp git source (best-effort; some upstream revisions have rename issues)
if ! grep -q "^zotero-mcp.*git" pyproject.toml; then
    if grep -q "\[tool.uv.sources\]" pyproject.toml; then
        sed -i '' 's/^# *zotero-mcp = { git.*/zotero-mcp = { git = "https:\/\/github.com\/54yyyu\/zotero-mcp.git" }/' pyproject.toml
    else
        printf '\n[tool.uv.sources]\nzotero-mcp = { git = "https://github.com/54yyyu/zotero-mcp.git" }\n' >> pyproject.toml
    fi
fi

# Claude skill dependencies
uv add pypdf reportlab pdf2image pillow mistralai python-dotenv
uv add zotero-mcp || echo "  zotero-mcp install failed (upstream package rename); skipping. Add manually later if needed."

uv sync || true
set -e

# .venv symlink
if [ ! -e ".venv" ]; then
    ln -s "$HOME/.venvs/$PROJECT_NAME" .venv
    echo "Created .venv -> $HOME/.venvs/$PROJECT_NAME symlink"
fi

# --- Git init ---
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: $PROJECT_NAME research project setup"
else
    echo "Git repository already initialized"
fi

echo "Setup complete!"
