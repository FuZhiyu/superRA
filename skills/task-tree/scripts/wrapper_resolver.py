#!/usr/bin/env python3
"""Single source of truth for the task-tree CLI source-resolution chain.

Both committed artifacts that need to find and run the task-tree scripts
without installing anything embed the *same* bash resolver emitted here:

- ``hooks/task-hook`` — the in-plugin PostToolUse shim (generated, committed).
- ``superRA/superra`` — the wrapper a research project's task tree carries,
  written at runtime by ``superra wrapper init``.

The resolver must stay self-contained (the generated wrapper lives in a
research project that cannot ``source`` anything from the plugin before it has
resolved the plugin), so the canonical chain is a single string constant here
and is *embedded* into each artifact rather than sourced. Keeping one copy in
Python and rendering both artifacts from it is what prevents the two shells
from drifting.

Execution model: ``uv run --script <dir>/scripts/<entry>`` with a
``python3 <dir>/scripts/<entry>`` fallback when ``uv`` is unavailable. Each
entry script carries a PEP 723 inline-metadata block as the single source of
truth for its dependencies; there is no installable package and no
``pyproject.toml``. ``uv run --script`` is script-scoped (no project discovery,
so it never provisions the caller's ``.venv``) and reads the file live each run
(no version-keyed build cache), so a source edit is reflected on the next call
with no cache-bust flag.

Resolution priority (returns the dir containing ``scripts/cli.py``):
  1. ``CLAUDE_PLUGIN_ROOT`` / ``PLUGIN_ROOT`` env var → ``$VAR/skills/task-tree``.
  2. Local checkout — ``$REPO_ROOT/skills/task-tree/scripts/cli.py`` if present.
     Ordered above the caches on purpose: a contributor in a checkout gets live
     edits, not the stale copied cache snapshot.
  3. Claude cache — ``~/.claude/plugins/installed_plugins.json`` records the
     authoritative ``installPath``; pick the project-matching record else the
     user-scope record; append ``/skills/task-tree``.
  4. Codex cache — bounded depth-3 glob of ``~/.codex/plugins/cache``; highest
     semver wins; no plugin-slug casing assumption.
  5. GitHub fallback — shallow-clone the repo to a user-cache dir and run
     ``uv run --script <clone>/skills/task-tree/scripts/cli.py``. This is the
     only network step and only fires when nothing local resolves.

Speed gate: each branch is O(1) work — an env read, a few file tests (the
canonical ``task-tree`` plus the legacy ``task-system`` alias, so up to two per
branch), one manifest read (a python3 heredoc) for the Claude branch, and one
fixed-depth glob for the Codex branch. No full-disk search. The first matching
branch short-circuits, so a resolved local checkout never reaches the manifest
read or the glob.
"""

from __future__ import annotations

import argparse
import os
import stat
import sys
from pathlib import Path

if __package__:
    from ._task_io import TASK_ROOT_DIRNAME, resolve_plan_root_arg
else:  # pragma: no cover - direct-script path
    sys.path.insert(0, str(Path(__file__).parent))
    from _task_io import TASK_ROOT_DIRNAME, resolve_plan_root_arg

GITHUB_REPO = "https://github.com/FuZhiyu/superRA.git"
CANONICAL_SKILL_SUBDIR = "skills/task-tree"
LEGACY_SKILL_SUBDIR = "skills/task-system"
GITHUB_SUBDIR = CANONICAL_SKILL_SUBDIR
# Pin lives only here. It may lag the installed version; it is a last resort
# used only when no local checkout and no installed plugin cache exist.
# Deliberately tracks `main`, the eventual public default branch: this work
# merges there later. Until then `main` does not yet carry skills/task-tree,
# which is acceptable because the fallback only fires when no local install
# exists at all. Do NOT repoint to a feature/trunk branch.
GITHUB_REF = "main"

# Flip to "1" once GITHUB_REF actually carries CANONICAL_SKILL_SUBDIR. Until
# then the GitHub branch fails fast (no shallow clone) rather than cloning the
# whole repo only to fail the cli.py existence test — the clone is pure waste
# while the pinned ref lacks the subdir.
GITHUB_REF_HAS_SUBDIR = "0"

# TTL (seconds) gating the refresh `git fetch` once a clone exists. Without it,
# every `superra` call and every PostToolUse hook fire in fallback mode is a
# network round-trip; with it, a reused clone refreshes at most once per window.
GITHUB_FETCH_TTL_SECONDS = "86400"

# The canonical resolution chain. `_superra_resolve_source` prints the resolved
# local package dir on stdout prefixed with "DIR:" and exits 0, OR prints the
# "GIT:<repo>@<ref>" spec for the GitHub fallback and exits 0. The embedding
# artifact then runs the resolved scripts with `uv run --script` (or shallow-
# clones first, for the GIT branch). The run-line is single-sourced in
# `_superra_run_entry` below so the wrapper and hook cannot drift.
RESOLVER_SNIPPET = r'''
# ---- superRA task-tree source resolver (generated; edit wrapper_resolver.py) ----
# Resolves the task-tree package dir from the already-installed plugin on disk
# and runs its scripts with `uv run --script` (python3 fallback), so the CLI
# never installs anything, never creates a cwd venv, and always reflects the
# live source (no version-keyed build cache).
_superra_pick_highest_semver() {
  # stdin: one candidate dir per line whose parent name is a version.
  # stdout: the dir whose version sorts highest (sort -V).
  local best="" best_v="" dir v
  while IFS= read -r dir; do
    [ -n "$dir" ] || continue
    v="${dir%/skills/task-tree}"
    v="${v%/skills/task-system}"
    v="${v##*/}"
    if [ -z "$best" ]; then
      best="$dir"; best_v="$v"
    else
      if [ "$(printf '%s\n%s\n' "$best_v" "$v" | sort -V | tail -n1)" = "$v" ]; then
        best="$dir"; best_v="$v"
      fi
    fi
  done
  [ -n "$best" ] && printf '%s\n' "$best"
}

_superra_claude_install_path() {
  # Reads ~/.claude/plugins/installed_plugins.json and prints the installPath
  # for the project-matching record, else the user-scope (projectPath null)
  # record. Single manifest read, no disk walk.
  local manifest="$HOME/.claude/plugins/installed_plugins.json"
  [ -f "$manifest" ] || return 1
  command -v python3 >/dev/null 2>&1 || return 1
  python3 - "$manifest" "$PWD" <<'PYEOF'
import json, os, sys
manifest, cwd = sys.argv[1], sys.argv[2]
try:
    with open(manifest) as f:
        data = json.load(f)
except Exception:
    sys.exit(1)
records = (data.get("plugins") or {}).get("superRA@superRA") or []
def matches(rec):
    pp = rec.get("projectPath")
    return bool(pp) and (cwd == pp or cwd.startswith(pp.rstrip("/") + "/"))
chosen = next((r for r in records if matches(r)), None)
if chosen is None:
    chosen = next((r for r in records if r.get("projectPath") in (None, "")), None)
# Deliberately no records[0] fallback: an arbitrary record may belong to another
# project and resolve to a stale/wrong install path. Fall through to the next
# resolution branch instead of guessing.
path = (chosen or {}).get("installPath")
if not path:
    sys.exit(1)
print(path)
PYEOF
}

_superra_resolve_source() {
  # 1. Explicit harness env var.
  local env_root="${CLAUDE_PLUGIN_ROOT:-${PLUGIN_ROOT:-}}"
  if [ -n "$env_root" ]; then
    if [ -f "$env_root/skills/task-tree/scripts/cli.py" ]; then
      printf 'DIR:%s\n' "$env_root/skills/task-tree"
      return 0
    fi
    if [ -f "$env_root/skills/task-system/scripts/cli.py" ]; then
      printf 'DIR:%s\n' "$env_root/skills/task-system"
      return 0
    fi
  fi

  # 2. Local checkout (preferred over caches so dev edits win).
  if [ -n "${SUPERRA_REPO_ROOT:-}" ]; then
    if [ -f "$SUPERRA_REPO_ROOT/skills/task-tree/scripts/cli.py" ]; then
      printf 'DIR:%s\n' "$SUPERRA_REPO_ROOT/skills/task-tree"
      return 0
    fi
    if [ -f "$SUPERRA_REPO_ROOT/skills/task-system/scripts/cli.py" ]; then
      printf 'DIR:%s\n' "$SUPERRA_REPO_ROOT/skills/task-system"
      return 0
    fi
  fi

  # 3. Claude cache (authoritative manifest).
  local claude_path
  claude_path="$(_superra_claude_install_path 2>/dev/null || true)"
  if [ -n "$claude_path" ]; then
    if [ -f "$claude_path/skills/task-tree/scripts/cli.py" ]; then
      printf 'DIR:%s\n' "$claude_path/skills/task-tree"
      return 0
    fi
    if [ -f "$claude_path/skills/task-system/scripts/cli.py" ]; then
      printf 'DIR:%s\n' "$claude_path/skills/task-system"
      return 0
    fi
  fi

  # 4. Codex cache (bounded depth-3 glob; highest semver; slug-case agnostic).
  local codex_cache="$HOME/.codex/plugins/cache"
  if [ -d "$codex_cache" ]; then
    local picked
    picked="$(
      for d in "$codex_cache"/*/*/*/skills/task-tree "$codex_cache"/*/*/*/skills/task-system; do
        [ -f "$d/scripts/cli.py" ] && printf '%s\n' "$d"
      done | _superra_pick_highest_semver
    )"
    if [ -n "$picked" ]; then
      printf 'DIR:%s\n' "$picked"
      return 0
    fi
  fi

  # 5. GitHub fallback (the only pin; needs network on first clone). Fail fast
  #    while the pinned ref does not yet carry skills/task-tree — cloning the
  #    whole repo only to fail the cli.py test is pure waste.
  if [ "__GITHUB_REF_HAS_SUBDIR__" = "1" ]; then
    printf 'GIT:%s@%s\n' "__GITHUB_REPO__" "__GITHUB_REF__"
    return 0
  fi
  return 1
}

_superra_github_clone() {
  # Shallow-clone the GitHub fallback to a stable user-cache dir and print the
  # task-tree source dir inside it. `uv run --script` cannot fetch a git
  # subdirectory, so the clone is the carrier for the loose scripts. Reuses an
  # existing clone (one fetch to refresh the pinned ref) so repeat calls do not
  # re-clone. Prints the dir on stdout; returns non-zero on failure.
  command -v git >/dev/null 2>&1 || return 1
  local cache_root="${XDG_CACHE_HOME:-$HOME/.cache}/superra"
  local clone="$cache_root/superRA-__GITHUB_REF__"
  mkdir -p "$cache_root" || return 1
  if [ -d "$clone/.git" ]; then
    # TTL-gate the refresh: only fetch when the clone's last refresh is older
    # than the window, so a reused clone is not a network round-trip on every
    # `superra` call / PostToolUse hook fire. The stamp file records last fetch.
    local stamp="$clone/.superra-fetch-stamp" now ts age
    now="$(date +%s 2>/dev/null || echo 0)"
    ts=0
    [ -f "$stamp" ] && ts="$(cat "$stamp" 2>/dev/null || echo 0)"
    age=$(( now - ts ))
    if [ "$now" = "0" ] || [ "$ts" = "0" ] || [ "$age" -ge "__GITHUB_FETCH_TTL_SECONDS__" ]; then
      git -C "$clone" fetch --depth 1 origin "__GITHUB_REF__" >/dev/null 2>&1 || true
      git -C "$clone" reset --hard "origin/__GITHUB_REF__" >/dev/null 2>&1 || true
      [ "$now" != "0" ] && printf '%s\n' "$now" > "$stamp" 2>/dev/null || true
    fi
  else
    rm -rf "$clone"
    git clone --depth 1 --branch "__GITHUB_REF__" "__GITHUB_REPO__" "$clone" >/dev/null 2>&1 || return 1
    # Stamp a fresh clone so the TTL window starts now, not at the next call.
    local fresh; fresh="$(date +%s 2>/dev/null || echo 0)"
    [ "$fresh" != "0" ] && printf '%s\n' "$fresh" > "$clone/.superra-fetch-stamp" 2>/dev/null || true
  fi
  [ -f "$clone/__GITHUB_SUBDIR__/scripts/cli.py" ] || return 1
  printf '%s\n' "$clone/__GITHUB_SUBDIR__"
}

_superra_resolve_dir() {
  # Resolve to a concrete on-disk task-tree dir, cloning the GitHub fallback
  # if that is the only branch that resolves. Prints the dir; returns non-zero
  # if nothing resolves.
  local resolved kind value
  resolved="$(_superra_resolve_source)" || return 1
  kind="${resolved%%:*}"
  value="${resolved#*:}"
  if [ "$kind" = "DIR" ]; then
    printf '%s\n' "$value"
    return 0
  fi
  _superra_github_clone
}

_superra_run_entry() {
  # $1: entry script basename under <dir>/scripts (e.g. cli.py, plan_dashboard.py,
  #     task_hook.py). Remaining args are forwarded to the script.
  # Runs via `uv run --script` (script-scoped: no project discovery, no cwd
  # venv, live source) and falls back to `python3` when uv is unavailable.
  local entry="$1"; shift
  local dir script
  dir="$(_superra_resolve_dir)" || {
    echo "superra: could not resolve task-tree source (no env var, checkout, installed plugin, or GitHub clone)" >&2
    return 1
  }
  script="$dir/scripts/$entry"
  if command -v uv >/dev/null 2>&1; then
    exec uv run --script "$script" "$@"
  elif command -v python3 >/dev/null 2>&1; then
    exec python3 "$script" "$@"
  else
    echo "superra: neither uv nor python3 found on PATH" >&2
    return 127
  fi
}

_superra_run() {
  # Route the first argument: `dashboard` → plan_dashboard.py (carries the web
  # stack so the task hot path stays minimal); everything else → cli.py.
  if [ "${1:-}" = "dashboard" ]; then
    shift
    _superra_run_entry plan_dashboard.py dashboard "$@"
  else
    _superra_run_entry cli.py "$@"
  fi
}
# ---- end superRA task-tree source resolver ----
'''.replace("__GITHUB_REPO__", GITHUB_REPO).replace("__GITHUB_REF__", GITHUB_REF).replace(
    "__GITHUB_SUBDIR__", GITHUB_SUBDIR
).replace(
    "__GITHUB_REF_HAS_SUBDIR__", GITHUB_REF_HAS_SUBDIR
).replace(
    "__GITHUB_FETCH_TTL_SECONDS__", GITHUB_FETCH_TTL_SECONDS
)


def render_resolver_snippet() -> str:
    """Return the canonical bash resolver chain (no shebang, no invocation)."""
    return RESOLVER_SNIPPET.strip("\n") + "\n"


def render_wrapper() -> str:
    """Render the self-contained `superRA/superra` wrapper a task tree carries.

    It detects a local checkout from its own location (so this repo's own
    wrapper keeps the dev-edits-win behavior) and otherwise falls through the
    shared chain to the installed plugin caches.
    """
    return (
        "#!/usr/bin/env bash\n"
        "# superRA task-tree CLI wrapper (generated by `superra wrapper init`).\n"
        "# Resolves the task-tree scripts from the installed plugin at runtime and\n"
        "# runs them with `uv run --script` (python3 fallback); never installs\n"
        "# anything, never creates a cwd venv, always reflects the live source.\n"
        "# Regenerate rather than hand-edit: `superra wrapper init`.\n"
        "\n"
        "set -euo pipefail\n"
        "\n"
        "case \"$0\" in\n"
        "  */*) _superra_script_dir=${0%/*} ;;\n"
        "  *) _superra_script_dir=. ;;\n"
        "esac\n"
        "_superra_script_dir=\"$(cd \"$_superra_script_dir\" && pwd)\"\n"
        "\n"
        "# If this wrapper sits inside a checkout (…/skills/task-tree present one\n"
        "# level up), prefer that checkout so contributor edits win.\n"
        "if [ -f \"$_superra_script_dir/../skills/task-tree/scripts/cli.py\" ] || [ -f \"$_superra_script_dir/../skills/task-system/scripts/cli.py\" ]; then\n"
        "  SUPERRA_REPO_ROOT=\"$(cd \"$_superra_script_dir/..\" && pwd)\"\n"
        "  export SUPERRA_REPO_ROOT\n"
        "fi\n"
        "\n"
        + render_resolver_snippet()
        + "\n"
        "_superra_run \"$@\"\n"
    )


def render_hook_shim() -> str:
    """Render the in-plugin `hooks/task-hook` PostToolUse shim.

    The shim reads PostToolUse JSON on stdin and forwards it to the packaged
    hook script. It prefers its own plugin checkout (its location is inside the
    plugin) and otherwise resolves through the shared chain. Never blocks:
    always exits 0.
    """
    return (
        "#!/usr/bin/env bash\n"
        "# Stable PostToolUse entry point for task-tree reconciliation (generated\n"
        "# by wrapper_resolver.py). Resolves the task-tree scripts from the\n"
        "# installed plugin at runtime and forwards stdin to the packaged hook via\n"
        "# `uv run --script` (python3 fallback).\n"
        "# Regenerate rather than hand-edit: `superra wrapper render-hook`.\n"
        "\n"
        "set -uo pipefail\n"
        "\n"
        "input=$(cat)\n"
        "\n"
        "case \"$0\" in\n"
        "  */*) _superra_script_dir=${0%/*} ;;\n"
        "  *) _superra_script_dir=. ;;\n"
        "esac\n"
        "_superra_script_dir=\"$(cd \"$_superra_script_dir\" && pwd)\"\n"
        "\n"
        "# The shim ships inside the plugin: its parent dir is the plugin root.\n"
        "if [ -f \"${_superra_script_dir%/hooks}/skills/task-tree/scripts/cli.py\" ] || [ -f \"${_superra_script_dir%/hooks}/skills/task-system/scripts/cli.py\" ]; then\n"
        "  SUPERRA_REPO_ROOT=\"${_superra_script_dir%/hooks}\"\n"
        "  export SUPERRA_REPO_ROOT\n"
        "fi\n"
        "\n"
        + render_resolver_snippet()
        + "\n"
        "# Resolve and run the packaged hook; never block (always exit 0).\n"
        "_superra_dir=\"$(_superra_resolve_dir 2>/dev/null || true)\"\n"
        "if [ -n \"$_superra_dir\" ]; then\n"
        "  _superra_hook=\"$_superra_dir/scripts/task_hook.py\"\n"
        "  if command -v uv >/dev/null 2>&1; then\n"
        "    printf '%s' \"$input\" | uv run --script \"$_superra_hook\" 2>/dev/null || true\n"
        "  elif command -v python3 >/dev/null 2>&1; then\n"
        "    printf '%s' \"$input\" | python3 \"$_superra_hook\" 2>/dev/null || true\n"
        "  fi\n"
        "fi\n"
        "exit 0\n"
    )


def _make_executable(path: Path) -> None:
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def write_wrapper(root: str | None) -> Path:
    """Write `<task-root>/superra` resolver wrapper; idempotent, executable."""
    if root is not None:
        task_root = Path(root)
    else:
        detected = resolve_plan_root_arg(None)
        task_root = detected if detected is not None else Path(TASK_ROOT_DIRNAME)
    task_root.mkdir(parents=True, exist_ok=True)
    wrapper_path = task_root / "superra"
    wrapper_path.write_text(render_wrapper(), encoding="utf-8")
    _make_executable(wrapper_path)
    return wrapper_path


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="superra wrapper",
        description="Generate the resolver-carrying task-tree CLI wrapper.",
    )
    sub = parser.add_subparsers(dest="wrapper_command", required=True)

    init = sub.add_parser("init", help="Write an executable resolver wrapper into the task root")
    init.add_argument(
        "--root",
        default=None,
        help=f"Task root to write the wrapper into (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )

    render_hook = sub.add_parser(
        "render-hook", help="Print the generated hooks/task-hook shim to stdout"
    )
    render_hook.add_argument(
        "--output", default="", help="Write the shim to PATH (and chmod +x) instead of stdout"
    )

    args = parser.parse_args(argv)

    if args.wrapper_command == "init":
        path = write_wrapper(args.root)
        print(f"Wrote {path}")
    elif args.wrapper_command == "render-hook":
        content = render_hook_shim()
        if args.output:
            out = Path(args.output)
            out.write_text(content, encoding="utf-8")
            _make_executable(out)
            print(f"Wrote {out}")
        else:
            sys.stdout.write(content)


if __name__ == "__main__":
    main()
