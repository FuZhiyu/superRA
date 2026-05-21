#!/usr/bin/env bash
# Test B — Fresh setup via the agent (permissive profile).
#
# Run the agent from an empty CWD and ask it to scaffold a new project at
# specific absolute paths. Assert that the scaffolded tree, .claude/.codex
# config, and Notes/setup_decisions.md exist, and that the agent output
# references the skill or create_project.sh.
#
# Usage: test_b_fresh.sh claude|codex

set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/../lib/common.sh"

CLI="${1:-claude}"

WORK=$(mktemp -d /tmp/rps-test-B-XXXX)
PROJ_DIR="$WORK/VerifyBar"
SHARE="$WORK/VerifyBar-Share"
_register_cleanup "$WORK"

trap 'cleanup_paths "$WORK"' EXIT

PROMPT="Use the research-project-setup skill to create a new research project named VerifyBar.

Required actions, in order:
1. Run the scaffolder at exactly this path: bash \"$CREATE_PROJECT\" \"$PROJ_DIR\" --share-path \"$SHARE\"
2. After it completes, write the setup decision log to $SHARE/Notes/setup_decisions.md per the skill's fresh-setup procedure. Include at least one blockquote recording the user decisions (project name VerifyBar, share path $SHARE, no Overleaf, no CI, both superRA plugins enabled).
3. Report what was created.

Use the absolute paths above verbatim. Do not enable Overleaf sync. Do not enable GitHub Actions CI. Keep both superRA plugins enabled (the default)."

case "$CLI" in
    claude)
        OUT=$(run_claude "$WORK" permissive "$PROMPT") || { log_fail "Test B claude: CLI exited non-zero"; exit 1; }
        ;;
    codex)
        OUT=$(run_codex "$WORK" permissive "$PROMPT") || { log_fail "Test B codex: CLI exited non-zero"; exit 1; }
        ;;
    *) log_fail "Test B: unknown CLI '$CLI'"; exit 1 ;;
esac

assert_file_exists "$PROJ_DIR" || { log_fail "Test B $CLI: project dir not created"; exit 1; }
assert_file_exists "$PROJ_DIR/.claude" || { log_fail "Test B $CLI: .claude/ missing"; exit 1; }
assert_file_exists "$PROJ_DIR/.codex" || { log_fail "Test B $CLI: .codex/ missing"; exit 1; }
assert_file_exists "$PROJ_DIR/Notes" || { log_fail "Test B $CLI: Notes symlink missing"; exit 1; }
[ -L "$PROJ_DIR/Notes" ] || { log_fail "Test B $CLI: Notes is not a symlink"; exit 1; }
assert_file_exists "$SHARE/Notes/setup_decisions.md" || { log_fail "Test B $CLI: setup_decisions.md missing"; exit 1; }

# Output must mention either the skill name or the scaffolder.
assert_output_mentions "$OUT" "research-project-setup" "create_project.sh" \
    || { log_fail "Test B $CLI: output references neither skill nor scaffolder"; exit 1; }

log_pass "Test B ($CLI): agent scaffolded VerifyBar"
exit 0
