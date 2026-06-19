#!/usr/bin/env bash
# Build the superRA documentation site into a single output directory.
#
# Produces four self-contained HTML files the GitHub Pages deploy serves:
#   index.html                   the docs tree (docs/site) in doc-mode — the site entry
#   showcase-analysis-tree.html  the real CAPM-vs-FF3 study tree, complete state (full chrome)
#   showcase-after-planning.html the same study right after planning, all tasks not-started
#   showcase-mid-implement.html  the same study mid-implement, mixed task statuses + figures
#
# The two progression pages are built from FROZEN HISTORICAL FIXTURES under
# docs/showcase-fixtures/, not from the live tree: they capture the
# showcase-analysis subtree as it stood at two past commits (after-planning and
# mid-implement) so the Quickstart can link live, explorable views of the study
# at three workflow moments. These fixtures are deliberately NOT kept in sync
# with later edits to the live superRA/showcase-analysis prose — the staleness
# is the point (each page shows the tree at a past moment). Do not "fix" the
# drift. Regenerate a fixture only to re-pin it to a (different) source commit;
# the capture commands are recorded in the task that built them
# (superRA/docs-site/14-canonical-showcase/02-progression-exports/task.md).
#
# The showcase framing/quickstart pages link to the three showcase exports by
# relative basename, so they must sit beside index.html; --doc-local-link keeps
# those links relative instead of rebasing them to the repo blob base.
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
dev_tree="superRA"
fixture_after_planning="docs/showcase-fixtures/after-planning"
fixture_mid_implement="docs/showcase-fixtures/mid-implement"

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
for tree in "$docs_tree" "$dev_tree" \
            "$fixture_after_planning/showcase-analysis" \
            "$fixture_mid_implement/showcase-analysis"; do
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
  --doc-local-link showcase-analysis-tree.html \
  --doc-local-link showcase-after-planning.html \
  --doc-local-link showcase-mid-implement.html

# --- 2. Showcase export (full task-tracker chrome, never doc-mode) ----------
# The real asset-pricing study is a subtree of superRA, so scope the full repo
# tree to it with --root and prefix its file links accordingly.
run_gen \
  --plan-root "$dev_tree" \
  --root showcase-analysis \
  --output "$out_dir/showcase-analysis-tree.html" \
  --repo-file-base "$repo_file_base" \
  --repo-file-prefix "$dev_tree/showcase-analysis"

# --- 3 & 4. Progression exports from frozen historical fixtures -------------
# Built from docs/showcase-fixtures/, not the live tree, so each captures the
# study at a past workflow moment. --repo-file-prefix points the in-task repo
# links at the live superRA/showcase-analysis tree, matching the complete-state
# export above. Full chrome (never --doc-mode), exactly like the complete state.
# These fixtures are intentionally frozen and NOT synced to later live edits —
# see the header comment before "fixing" any drift.
run_gen \
  --plan-root "$fixture_after_planning" \
  --root showcase-analysis \
  --output "$out_dir/showcase-after-planning.html" \
  --repo-file-base "$repo_file_base" \
  --repo-file-prefix "$dev_tree/showcase-analysis"

run_gen \
  --plan-root "$fixture_mid_implement" \
  --root showcase-analysis \
  --output "$out_dir/showcase-mid-implement.html" \
  --repo-file-base "$repo_file_base" \
  --repo-file-prefix "$dev_tree/showcase-analysis"

# --- Verify all four files landed -------------------------------------------
for f in index.html showcase-analysis-tree.html \
         showcase-after-planning.html showcase-mid-implement.html; do
  if [ ! -s "$out_dir/$f" ]; then
    echo "build_site: export produced no $f" >&2
    exit 1
  fi
done

echo "build_site: wrote $out_dir/{index,showcase-analysis-tree,showcase-after-planning,showcase-mid-implement}.html"
