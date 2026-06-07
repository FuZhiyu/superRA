#!/usr/bin/env python3
"""Single source of truth for the task-system CLI source-resolution chain.

Both committed artifacts that need to find and run the task-system package
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

Resolution priority (returns the dir containing ``pyproject.toml``):
  1. ``CLAUDE_PLUGIN_ROOT`` / ``PLUGIN_ROOT`` env var → ``$VAR/skills/task-system``.
  2. Local checkout — ``$REPO_ROOT/skills/task-system/pyproject.toml`` if present.
     Ordered above the caches on purpose: a contributor in a checkout gets live
     edits, not the stale copied cache snapshot.
  3. Claude cache — ``~/.claude/plugins/installed_plugins.json`` records the
     authoritative ``installPath``; pick the project-matching record else the
     user-scope record; append ``/skills/task-system``.
  4. Codex cache — bounded depth-3 glob of ``~/.codex/plugins/cache``; highest
     semver wins; no plugin-slug casing assumption.
  5. GitHub fallback — ``uvx --from git+…#subdirectory=skills/task-system``.

Speed gate: env read + one file test + one manifest read + one fixed-depth
glob. No full-disk search.
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
GITHUB_SUBDIR = "skills/task-system"
# Pin lives only here. It may lag the installed version; it is a last resort
# used only when no local checkout and no installed plugin cache exist.
# Deliberately tracks `main`, the eventual public default branch: this work
# merges there later. Until then `main` does not yet carry skills/task-system,
# which is acceptable because the fallback only fires when no local install
# exists at all. Do NOT repoint to a feature/trunk branch.
GITHUB_REF = "main"

# The canonical resolution chain. `_resolve_task_system_source` prints the
# resolved local package dir on stdout and exits 0, OR prints the git+ spec for
# the GitHub fallback prefixed with "GIT:" and exits 0, OR exits 1 if nothing
# resolves. The embedding artifact decides how to invoke `uvx --from` with it.
RESOLVER_SNIPPET = r'''
# ---- superRA task-system source resolver (generated; edit wrapper_resolver.py) ----
# Resolves the task-system package dir from the already-installed plugin on disk
# and runs it with `uvx --from`, so the CLI never installs anything, never
# creates a cwd venv, and always matches the installed plugin version.
_superra_pick_highest_semver() {
  # stdin: one candidate dir per line whose parent name is a version.
  # stdout: the dir whose version sorts highest (sort -V).
  local best="" best_v="" dir v
  while IFS= read -r dir; do
    [ -n "$dir" ] || continue
    v="${dir%/skills/task-system}"
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
if chosen is None and records:
    chosen = records[0]
path = (chosen or {}).get("installPath")
if not path:
    sys.exit(1)
print(path)
PYEOF
}

_superra_resolve_source() {
  # 1. Explicit harness env var.
  local env_root="${CLAUDE_PLUGIN_ROOT:-${PLUGIN_ROOT:-}}"
  if [ -n "$env_root" ] && [ -f "$env_root/skills/task-system/pyproject.toml" ]; then
    printf 'DIR:%s\n' "$env_root/skills/task-system"
    return 0
  fi

  # 2. Local checkout (preferred over caches so dev edits win).
  if [ -n "${SUPERRA_REPO_ROOT:-}" ] && [ -f "$SUPERRA_REPO_ROOT/skills/task-system/pyproject.toml" ]; then
    printf 'DIR:%s\n' "$SUPERRA_REPO_ROOT/skills/task-system"
    return 0
  fi

  # 3. Claude cache (authoritative manifest).
  local claude_path
  claude_path="$(_superra_claude_install_path 2>/dev/null || true)"
  if [ -n "$claude_path" ] && [ -f "$claude_path/skills/task-system/pyproject.toml" ]; then
    printf 'DIR:%s\n' "$claude_path/skills/task-system"
    return 0
  fi

  # 4. Codex cache (bounded depth-3 glob; highest semver; slug-case agnostic).
  local codex_cache="$HOME/.codex/plugins/cache"
  if [ -d "$codex_cache" ]; then
    local picked
    picked="$(
      for d in "$codex_cache"/*/*/*/skills/task-system; do
        [ -f "$d/pyproject.toml" ] && printf '%s\n' "$d"
      done | _superra_pick_highest_semver
    )"
    if [ -n "$picked" ]; then
      printf 'DIR:%s\n' "$picked"
      return 0
    fi
  fi

  # 5. GitHub fallback (the only pin; needs network on first build).
  printf 'GIT:git+%s@%s#subdirectory=%s\n' "__GITHUB_REPO__" "__GITHUB_REF__" "__GITHUB_SUBDIR__"
  return 0
}

_superra_run() {
  if ! command -v uvx >/dev/null 2>&1; then
    echo "superra: uvx (uv) is required but not found on PATH" >&2
    return 127
  fi
  local resolved kind source
  resolved="$(_superra_resolve_source)"
  kind="${resolved%%:*}"
  source="${resolved#*:}"
  exec uvx --from "$source" superra "$@"
}
# ---- end superRA task-system source resolver ----
'''.replace("__GITHUB_REPO__", GITHUB_REPO).replace("__GITHUB_REF__", GITHUB_REF).replace(
    "__GITHUB_SUBDIR__", GITHUB_SUBDIR
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
        "# superRA task-system CLI wrapper (generated by `superra wrapper init`).\n"
        "# Resolves the task-system package from the installed plugin at runtime;\n"
        "# never installs anything and never creates a cwd venv. Regenerate rather\n"
        "# than hand-edit: `superra wrapper init`.\n"
        "\n"
        "set -euo pipefail\n"
        "\n"
        "case \"$0\" in\n"
        "  */*) _superra_script_dir=${0%/*} ;;\n"
        "  *) _superra_script_dir=. ;;\n"
        "esac\n"
        "_superra_script_dir=\"$(cd \"$_superra_script_dir\" && pwd)\"\n"
        "\n"
        "# If this wrapper sits inside a checkout (…/skills/task-system present one\n"
        "# level up), prefer that checkout so contributor edits win.\n"
        "if [ -f \"$_superra_script_dir/../skills/task-system/pyproject.toml\" ]; then\n"
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

    The shim reads PostToolUse JSON on stdin and forwards it to
    `superra task hook post-tool-use`. It prefers its own plugin checkout (its
    location is inside the plugin) and otherwise resolves through the shared
    chain. Never blocks: always exits 0.
    """
    return (
        "#!/usr/bin/env bash\n"
        "# Stable PostToolUse entry point for task-tree reconciliation (generated\n"
        "# by wrapper_resolver.py). Resolves the task-system package from the\n"
        "# installed plugin at runtime and forwards stdin to the packaged hook.\n"
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
        "if [ -f \"${_superra_script_dir%/hooks}/skills/task-system/pyproject.toml\" ]; then\n"
        "  SUPERRA_REPO_ROOT=\"${_superra_script_dir%/hooks}\"\n"
        "  export SUPERRA_REPO_ROOT\n"
        "fi\n"
        "\n"
        + render_resolver_snippet()
        + "\n"
        "if ! command -v uvx >/dev/null 2>&1; then\n"
        "  # uv unavailable: fall back to a direct python3 run of the packaged hook\n"
        "  # if a local source dir is reachable, else no-op (never block).\n"
        "  if [ -n \"${SUPERRA_REPO_ROOT:-}\" ] && command -v python3 >/dev/null 2>&1; then\n"
        "    printf '%s' \"$input\" | python3 \"$SUPERRA_REPO_ROOT/skills/task-system/scripts/task_hook.py\" || true\n"
        "  fi\n"
        "  exit 0\n"
        "fi\n"
        "\n"
        "resolved=\"$(_superra_resolve_source)\"\n"
        "source=\"${resolved#*:}\"\n"
        "printf '%s' \"$input\" | uvx --from \"$source\" superra task hook post-tool-use 2>/dev/null || true\n"
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
