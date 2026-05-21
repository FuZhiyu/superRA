#!/usr/bin/env bash
# Test A — Sandbox write to share folder under STRICT permission profile.
#
# Scaffold a project with a NON-SIBLING share path so the share folder
# resolves to a directory outside the project tree. The agent is given a
# write task into Notes/test.txt (which symlinks into the share folder).
# In strict mode the agent has no bypass — if create_project.sh did not
# register the absolute share path in .claude/settings.local.json /
# .codex/config.toml writable_roots, the write fails.
#
# Usage: test_a_sandbox.sh claude|codex
#
# Exits 0 on PASS, 1 on FAIL.

set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/../lib/common.sh"

CLI="${1:-claude}"

PROJ=$(mktemp -d /tmp/rps-test-A-XXXX)
PROJ_DIR="$PROJ/Proj"
# The share path MUST sit outside both the project root and Codex's default
# writable_roots (/tmp, /private/tmp, /var/folders, ~/.venvs, ~/.cache,
# ~/.local/share/uv — see template/.codex/config.toml). Otherwise the codex
# strict-profile assertion passes whether or not register_share_path_with_agents
# ran, defeating the point of Test A. ~/.local/share/rps-share-A-* is outside
# the default writable_roots so the registration becomes load-bearing.
mkdir -p "$HOME/.local/share"
SHARE=$(mktemp -d "$HOME/.local/share/rps-share-A-XXXX")
_register_cleanup "$PROJ" "$SHARE"

# Custom cleanup since SHARE is outside /tmp.
_test_a_cleanup() {
    [ "${KEEP_ARTIFACTS:-0}" = "1" ] && return 0
    rm -rf "$PROJ"
    case "$SHARE" in
        "$HOME/.local/share/rps-share-A-"*) rm -rf "$SHARE" ;;
    esac
}
trap _test_a_cleanup EXIT

scaffold_project "$PROJ_DIR" "$SHARE" >/dev/null || exit 1

# Sanity: the project's Notes/ should symlink into the SHARE dir.
[ -L "$PROJ_DIR/Notes" ] || { log_fail "Test A: Notes is not a symlink"; exit 1; }
TARGET=$(readlink "$PROJ_DIR/Notes")
[ "$TARGET" = "$SHARE/Notes" ] || { log_fail "Test A: Notes target $TARGET != $SHARE/Notes"; exit 1; }

# Use the ABSOLUTE share-folder path (not the in-project Notes/ symlink) so the
# write target resolves to a path *outside* the project root. This is what makes
# the registration load-bearing: only an entry in additionalDirectories /
# writable_roots makes the absolute path part of the agent's writable set.
PROMPT="Create a file at the absolute path $SHARE/Notes/test.txt containing exactly the word hello (one word, no quotes, no trailing newline beyond what your editor adds). Use the absolute path I gave; do not use any relative path or symlink. Do not print anything else."

case "$CLI" in
    claude)
        OUT=$(run_claude "$PROJ_DIR" strict "$PROMPT") || { log_fail "Test A claude: CLI exited non-zero"; exit 1; }
        assert_no_permission_denials "$OUT" || { log_fail "Test A claude: permission denial recorded"; exit 1; }
        ;;
    codex)
        OUT=$(run_codex "$PROJ_DIR" strict "$PROMPT") || { log_fail "Test A codex: CLI exited non-zero"; exit 1; }
        assert_no_codex_sandbox_violation "$OUT" || { log_fail "Test A codex: sandbox violation event"; exit 1; }
        ;;
    *) log_fail "Test A: unknown CLI '$CLI'"; exit 1 ;;
esac

# The write must have succeeded.
assert_file_exists "$SHARE/Notes/test.txt" || { log_fail "Test A $CLI: share-folder write did not occur"; exit 1; }
assert_file_contains "$SHARE/Notes/test.txt" "hello" || { log_fail "Test A $CLI: file content missing 'hello'"; exit 1; }

log_pass "Test A ($CLI): strict-profile share-folder write succeeded"
exit 0
