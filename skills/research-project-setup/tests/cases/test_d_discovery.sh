#!/usr/bin/env bash
# Test D — Trigger discovery from an unrelated empty CWD.
#
# From a completely empty tmp dir (no scaffolded project), prompt the
# agent with the canonical trigger phrase. Assert the agent's response
# references the research-project-setup skill or create_project.sh.
#
# Usage: test_d_discovery.sh claude|codex

set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/../lib/common.sh"

CLI="${1:-claude}"

WORK=$(mktemp -d /tmp/rps-test-D-XXXX)
_register_cleanup "$WORK"

trap 'cleanup_paths "$WORK"' EXIT

# Use a deliberately under-specified prompt: the trigger phrase only.
# The agent should surface the research-project-setup skill (or its
# scaffolder script) in its response. Do not actually run it.
PROMPT="I want to create a new research project. Which skill or script in this installation handles that, and what command would I run? Do not actually create anything — just tell me the skill name and the command."

case "$CLI" in
    claude)
        # claude discovers the dev skill via --plugin-dir <superRA-root>,
        # injected by run_claude.
        OUT=$(run_claude "$WORK" permissive "$PROMPT") || { log_fail "Test D claude: CLI exited non-zero"; exit 1; }
        ;;
    codex)
        # codex has no per-invocation plugin-dir flag, so symlink the dev
        # skill into ~/.codex/skills/ for discovery. Teardown via trap.
        codex_install_skill_link
        trap 'codex_uninstall_skill_link; cleanup_paths "$WORK"' EXIT
        OUT=$(run_codex "$WORK" permissive "$PROMPT") || { log_fail "Test D codex: CLI exited non-zero"; exit 1; }
        ;;
    *) log_fail "Test D: unknown CLI '$CLI'"; exit 1 ;;
esac

assert_output_mentions "$OUT" "research-project-setup" "create_project.sh" \
    || { log_fail "Test D $CLI: output references neither skill nor scaffolder"; exit 1; }

log_pass "Test D ($CLI): trigger phrase surfaced research-project-setup"
exit 0
