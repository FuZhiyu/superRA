#!/usr/bin/env bash
# Build the superRA documentation site into a single output directory.
#
# Produces three self-contained HTML files the GitHub Pages deploy serves:
#   index.html             the docs tree (docs/site) in doc-mode  — the site entry
#   demo-tree.html         the curated showcase demo tree (full chrome)
#   superra-dev-tree.html  superRA's own task tree (full chrome)
#
# The showcase framing page links to the two *-tree.html files by relative
# basename, so they must sit beside index.html; --doc-local-link keeps those
# links relative instead of rebasing them to the repo blob base.
#
# Repo-file authority links on the docs site resolve repo-root-relative against
# --repo-file-base (the GitHub blob URL at the built ref). The ref defaults to
# the current commit so a local preview matches CI.
#
# Usage:
#   docs/build_site.sh [OUTPUT_DIR]
# Env:
#   REPO_FILE_BASE  override the GitHub blob base (default: derived from origin + HEAD)
#   GITHUB_SHA      commit to pin file links to (default: git rev-parse HEAD)
#   GITHUB_REPOSITORY  owner/repo (default: parsed from `git remote get-url origin`)
#
# Fails loudly on any export error or missing input; no silent partial site.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

out_dir="${1:-_site}"
gen="skills/task-tree/scripts/plan_dashboard.py"

docs_tree="docs/site"
demo_tree="docs/showcase-demo"
dev_tree="superRA"

# --- Resolve the repo-file base (GitHub blob URL at the built ref) ----------
sha="${GITHUB_SHA:-$(git rev-parse HEAD)}"
if [ -n "${GITHUB_REPOSITORY:-}" ]; then
  repo_slug="$GITHUB_REPOSITORY"
else
  origin="$(git remote get-url origin 2>/dev/null || true)"
  # Normalize git@github.com:owner/repo.git and https://github.com/owner/repo(.git)
  repo_slug="$(printf '%s' "$origin" \
    | sed -E 's#^git@github.com:##; s#^https://github.com/##; s#\.git$##')"
fi
repo_file_base="${REPO_FILE_BASE:-https://github.com/${repo_slug}/blob/${sha}}"

# --- Verify every required input exists before touching the output ----------
for tree in "$docs_tree" "$demo_tree" "$dev_tree"; do
  if [ ! -d "$tree" ]; then
    echo "build_site: missing task tree: $tree" >&2
    exit 1
  fi
done

echo "build_site: output    = $out_dir"
echo "build_site: file base  = $repo_file_base"
rm -rf "$out_dir"
mkdir -p "$out_dir"

run_gen() {
  # uv run --script is the committed invocation; python3 is a uv-free fallback
  # (the generator needs the web-stack deps, so prefer uv when present).
  if command -v uv >/dev/null 2>&1; then
    uv run --script "$gen" generate "$@"
  else
    python3 "$gen" generate "$@"
  fi
}

# --repo-file-prefix is each tree's path relative to the repo root, so
# --repo-file-base links keep their leading path (docs/site, not site). The build
# runs from the repo root, so the tree paths above are already repo-relative.

# --- 1. The docs site (doc-mode, repo-root-relative authority links) --------
run_gen \
  --plan-root "$docs_tree" \
  --output "$out_dir/index.html" \
  --doc-mode \
  --repo-file-base "$repo_file_base" \
  --repo-file-prefix "$docs_tree" \
  --doc-local-link demo-tree.html \
  --doc-local-link superra-dev-tree.html

# --- 2. Showcase exports (full task-tracker chrome, never doc-mode) ---------
run_gen \
  --plan-root "$demo_tree" \
  --output "$out_dir/demo-tree.html" \
  --repo-file-base "$repo_file_base" \
  --repo-file-prefix "$demo_tree"

run_gen \
  --plan-root "$dev_tree" \
  --output "$out_dir/superra-dev-tree.html" \
  --repo-file-base "$repo_file_base" \
  --repo-file-prefix "$dev_tree"

# --- Verify the three files landed ------------------------------------------
for f in index.html demo-tree.html superra-dev-tree.html; do
  if [ ! -s "$out_dir/$f" ]; then
    echo "build_site: export produced no $f" >&2
    exit 1
  fi
done

echo "build_site: wrote $out_dir/{index,demo-tree,superra-dev-tree}.html"
