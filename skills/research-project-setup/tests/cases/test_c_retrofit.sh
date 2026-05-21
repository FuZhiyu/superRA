#!/usr/bin/env bash
# Test C — Retrofit Overleaf into an existing scaffolded project.
#
# Scaffold a project WITHOUT --with-overleaf, then ask the agent (permissive
# profile) to add Overleaf sync. Assert that overleaf-sync/ appears, the
# .gitignore is updated, and a new commit lands.
#
# Usage: test_c_retrofit.sh claude|codex

set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/../lib/common.sh"

CLI="${1:-claude}"

WORK=$(mktemp -d /tmp/rps-test-C-XXXX)
PROJ_DIR="$WORK/RetroFooProj"
SHARE="$WORK/RetroFoo-Share"
_register_cleanup "$WORK"

trap 'cleanup_paths "$WORK"' EXIT

scaffold_project "$PROJ_DIR" "$SHARE" >/dev/null || exit 1

# Sanity: no overleaf-sync yet.
[ ! -e "$PROJ_DIR/overleaf-sync" ] || { log_fail "Test C: overleaf-sync/ already exists pre-retrofit"; exit 1; }

# Record initial commit hash so we can detect a new commit.
HEAD_BEFORE=$(cd "$PROJ_DIR" && git rev-parse HEAD 2>/dev/null || echo "none")

SKILL_TEMPLATE="$SKILL_ROOT/template"

PROMPT="Add Overleaf sync to this project using the research-project-setup skill's retrofit playbook for Overleaf. Copy the overleaf-sync/ helper from the skill template at $SKILL_TEMPLATE/overleaf-sync to the project root (preserve executable bit), update .gitignore per the playbook (.Paper-pre-subtree-backup/), and commit the change as a single feature commit titled 'add: Overleaf subtree sync'. Use bypassed permissions; just do it."

case "$CLI" in
    claude)
        OUT=$(run_claude "$PROJ_DIR" permissive "$PROMPT") || { log_fail "Test C claude: CLI exited non-zero"; exit 1; }
        ;;
    codex)
        OUT=$(run_codex "$PROJ_DIR" permissive "$PROMPT") || { log_fail "Test C codex: CLI exited non-zero"; exit 1; }
        ;;
    *) log_fail "Test C: unknown CLI '$CLI'"; exit 1 ;;
esac

assert_file_exists "$PROJ_DIR/overleaf-sync" || { log_fail "Test C $CLI: overleaf-sync/ not created"; exit 1; }
# .gitignore should contain at least one overleaf-related entry now.
if ! grep -qiE "overleaf" "$PROJ_DIR/.gitignore"; then
    log_fail "Test C $CLI: .gitignore missing overleaf entries"
    exit 1
fi
HEAD_AFTER=$(cd "$PROJ_DIR" && git rev-parse HEAD 2>/dev/null || echo "none")
if [ "$HEAD_AFTER" = "$HEAD_BEFORE" ] || [ "$HEAD_AFTER" = "none" ]; then
    log_fail "Test C $CLI: no new commit (HEAD unchanged: $HEAD_AFTER)"
    exit 1
fi

log_pass "Test C ($CLI): Overleaf retrofit applied with new commit $HEAD_AFTER"
exit 0
