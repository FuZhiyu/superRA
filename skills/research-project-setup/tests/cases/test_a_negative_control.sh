#!/usr/bin/env bash
# Test A negative control — confirms Test A's strict-profile assertion is
# load-bearing.
#
# Scaffold a project + share under $HOME/rps-tests/, then SURGICALLY STRIP
# the registration that `register_share_path_with_agents` writes:
#   - .claude/settings.local.json   additionalDirectories=[]
#   - .codex/config.toml            remove absolute share-path lines from writable_roots
# then replay Test A's prompt+assertions against the broken project.
#
# Expected outcome on each CLI:
#   - <share>/Notes/test.txt is NOT created, AND
#   - claude: at least one permission_denial in the result event; OR
#     codex: a sandbox violation event in the JSONL
# This is "expected FAIL got FAIL ✓" — the script EXITS 0.
#
# If the write succeeds (file present, no denial), Test A is NOT load-bearing
# — print "UNEXPECTED PASS" and exit 1.
#
# Usage: test_a_negative_control.sh [claude|codex|both]   (default: both)

set -u
# Tighter per-invocation timeout BEFORE sourcing common.sh so its default (300s)
# does not win. A denied write may retry / stall — kill quickly.
: "${AGENT_TIMEOUT:=90}"
export AGENT_TIMEOUT

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/../lib/common.sh"

WHICH="${1:-both}"
case "$WHICH" in claude|codex|both) ;; *) echo "usage: $0 [claude|codex|both]" >&2; exit 2 ;; esac

mkdir -p "$HOME/rps-tests"
PROJ=$(mktemp -d "$HOME/rps-tests/neg-proj-XXXX")
PROJ_DIR="$PROJ/NegCtrl"
SHARE=$(mktemp -d "$HOME/rps-tests/neg-share-XXXX")

# Cleanup is guarded — case "$path" in "$HOME/rps-tests/"*) only.
cleanup() {
    local p
    for p in "$PROJ" "$SHARE"; do
        case "$p" in
            "$HOME/rps-tests/"*) rm -rf "$p" ;;
            *) log_fail "refusing to rm -rf outside \$HOME/rps-tests/: $p" ;;
        esac
    done
}
trap cleanup EXIT

# 1. Scaffold normally — should produce a working registration.
log_info "neg-ctrl: scaffolding $PROJ_DIR with share=$SHARE"
scaffold_project "$PROJ_DIR" "$SHARE" >/dev/null || { log_fail "neg-ctrl: scaffolder failed"; exit 1; }

# 2. Surgically strip the registration on BOTH sides.
log_info "neg-ctrl: stripping additionalDirectories from .claude/settings.local.json"
python3 - "$PROJ_DIR/.claude/settings.local.json" <<'PY'
import json, sys
p = sys.argv[1]
with open(p) as f: cfg = json.load(f)
cfg.setdefault('permissions', {})['additionalDirectories'] = []
with open(p, 'w') as f: json.dump(cfg, f, indent=2)
PY

log_info "neg-ctrl: removing absolute share-path entries from .codex/config.toml writable_roots"
# Strip every writable_roots entry whose path begins with $SHARE (handles both
# the bare share dir and its Data/Notes/Output children). The scaffolder may
# append entries on the tail of an existing line (no leading newline), so we
# strip the quoted token + optional comma + optional surrounding whitespace
# anywhere it occurs — not just on its own line.
python3 - "$PROJ_DIR/.codex/config.toml" "$SHARE" <<'PY'
import re, sys
p, share = sys.argv[1], sys.argv[2]
with open(p) as f: txt = f.read()
# Match: optional leading whitespace, quoted token starting with $SHARE, optional
# trailing comma, optional trailing whitespace/newline. Strip the whole hunk.
pat = re.compile(r'\s*"' + re.escape(share) + r'[^"]*"\s*,?')
new = pat.sub('', txt)
with open(p, 'w') as f: f.write(new)
PY

# Sanity-check the strip worked.
if grep -F "$SHARE" "$PROJ_DIR/.claude/settings.local.json" >/dev/null 2>&1; then
    log_fail "neg-ctrl: SHARE path still present in .claude/settings.local.json after strip"; exit 1
fi
if grep -F "$SHARE" "$PROJ_DIR/.codex/config.toml" >/dev/null 2>&1; then
    log_fail "neg-ctrl: SHARE path still present in .codex/config.toml after strip"; exit 1
fi

# Sanity: Notes is a symlink into the share dir (created by the scaffolder).
[ -L "$PROJ_DIR/Notes" ] || { log_fail "neg-ctrl: Notes is not a symlink"; exit 1; }

# 3. Replay Test A's prompt + assertions. Expect FAIL (file absent + denial).
PROMPT="Create a file at the absolute path $SHARE/Notes/test.txt containing exactly the word hello (one word, no quotes, no trailing newline beyond what your editor adds). Use the absolute path I gave; do not use any relative path or symlink. Do not print anything else."

# Returns 0 if the run produced the EXPECTED-FAIL signature (no file AND a denial);
# returns 1 if it UNEXPECTEDLY PASSED (file present or no denial recorded).
run_one() {
    local cli="$1"
    local out rc
    # Ensure the file is absent before the run so we're not confused by a prior write.
    rm -f "$SHARE/Notes/test.txt"

    log_info "neg-ctrl: running $cli (strict profile, expecting FAIL)"
    t0=$(date +%s)
    case "$cli" in
        claude)
            out=$(run_claude "$PROJ_DIR" strict "$PROMPT"); rc=$?
            ;;
        codex)
            out=$(run_codex "$PROJ_DIR" strict "$PROMPT"); rc=$?
            ;;
    esac
    t1=$(date +%s)
    local wall=$((t1-t0))

    local file_present=no
    [ -e "$SHARE/Notes/test.txt" ] && file_present=yes

    # Detect denial signature. For claude, the load-bearing positive assertion
    # is assert_no_permission_denials; here we WANT denials >= 1 so the inversion
    # is "the positive assertion failed". For codex, the positive assertion is
    # assert_no_codex_sandbox_violation, but codex sometimes silently declines
    # to write rather than emitting a recognizable sandbox-violation marker —
    # so the load-bearing signal for codex is simply "file absent". A detected
    # sandbox violation is recorded but not required for codex.
    local denial=no
    case "$cli" in
        claude)
            if assert_no_permission_denials "$out" 2>/dev/null; then denial=no; else denial=yes; fi
            ;;
        codex)
            if assert_no_codex_sandbox_violation "$out" 2>/dev/null; then denial=no; else denial=yes; fi
            ;;
    esac

    # Required-FAIL criterion per CLI (matches what Test A's positive path checks):
    #   claude: file_absent AND denials>=1   (assert_no_permission_denials inverted)
    #   codex:  file_absent                  (assert_no_codex_sandbox_violation is supplementary)
    local expected_fail=no
    case "$cli" in
        claude) [ "$file_present" = "no" ] && [ "$denial" = "yes" ] && expected_fail=yes ;;
        codex)  [ "$file_present" = "no" ] && expected_fail=yes ;;
    esac

    if [ "$expected_fail" = "yes" ]; then
        log_pass "negative-control ($cli): expected FAIL got FAIL ✓ (file absent, denial=$denial, wall=${wall}s, cli_exit=$rc)"
        return 0
    fi
    log_fail "negative-control ($cli): UNEXPECTED PASS — file_present=$file_present denial=$denial wall=${wall}s cli_exit=$rc"
    log_fail "  (Test A's assertion is NOT load-bearing for $cli; the registration strip did not block the write.)"
    return 1
}

OVERALL=0
case "$WHICH" in
    claude) run_one claude || OVERALL=1 ;;
    codex)  run_one codex  || OVERALL=1 ;;
    both)
        run_one claude || OVERALL=1
        run_one codex  || OVERALL=1
        ;;
esac

exit $OVERALL
