#!/usr/bin/env bash
# Run the full research-project-setup CLI test matrix
# (4 scenarios × 2 CLIs = up to 8 cases).
#
# Flags:
#   --only claude|codex   Run only one CLI's rows.
#   --case A|B|C|D        Run only one scenario.
#   --keep                Skip cleanup of /tmp artifacts.
#   --verbose             Echo every CLI invocation.
#
# Env overrides:
#   CLAUDE_MODEL          default claude-haiku-4-5-20251001
#   CODEX_MODEL           default gpt-5.4-mini
#   KEEP_ARTIFACTS=1      same as --keep

set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/lib/common.sh"

ONLY_CLI=""
ONLY_CASE=""

while [ $# -gt 0 ]; do
    case "$1" in
        --only) ONLY_CLI="$2"; shift 2 ;;
        --case) ONLY_CASE="$2"; shift 2 ;;
        --keep) export KEEP_ARTIFACTS=1; shift ;;
        --verbose) export VERBOSE=1; shift ;;
        -h|--help)
            sed -n '2,16p' "$0"; exit 0 ;;
        *) echo "unknown flag: $1" >&2; exit 2 ;;
    esac
done

preflight_scaffolder || exit 1
CLAUDE_OK=0; preflight_claude && CLAUDE_OK=1
CODEX_OK=0; preflight_codex && CODEX_OK=1

if [ "$CLAUDE_OK" = "0" ] && [ "$CODEX_OK" = "0" ]; then
    log_fail "neither claude nor codex CLI is usable — abort"
    exit 1
fi

CASES=(A B C D)
[ -n "$ONLY_CASE" ] && CASES=("$ONLY_CASE")

CLIS=()
if [ -n "$ONLY_CLI" ]; then
    CLIS=("$ONLY_CLI")
else
    [ "$CLAUDE_OK" = "1" ] && CLIS+=(claude)
    [ "$CODEX_OK" = "1" ] && CLIS+=(codex)
fi

declare -a RESULTS  # rows: "CASE CLI STATUS SECONDS"
PASS=0; FAIL=0; SKIP=0

for c in "${CASES[@]}"; do
    case_lower=$(echo "$c" | tr '[:upper:]' '[:lower:]')
    case "$case_lower" in
        a) script="$HERE/cases/test_a_sandbox.sh" ;;
        b) script="$HERE/cases/test_b_fresh.sh" ;;
        c) script="$HERE/cases/test_c_retrofit.sh" ;;
        d) script="$HERE/cases/test_d_discovery.sh" ;;
        *) log_fail "unknown case '$c'"; continue ;;
    esac
    for cli in "${CLIS[@]}"; do
        log_info "==== Case $c × $cli ===="
        t0=$(date +%s)
        if bash "$script" "$cli"; then
            t1=$(date +%s)
            RESULTS+=("$c $cli PASS $((t1-t0))s")
            PASS=$((PASS+1))
        else
            t1=$(date +%s)
            RESULTS+=("$c $cli FAIL $((t1-t0))s")
            FAIL=$((FAIL+1))
        fi
    done
done

echo
echo "==== Summary ===="
printf "%-6s %-8s %-6s %s\n" CASE CLI STATUS TIME
for r in "${RESULTS[@]}"; do
    set -- $r
    printf "%-6s %-8s %-6s %s\n" "$1" "$2" "$3" "$4"
done
echo
echo "PASS=$PASS  FAIL=$FAIL"

[ "$FAIL" = "0" ]
