# Shared helpers for the research-project-setup test suite.
#
# Source from `tests/run_tests.sh` and from `tests/cases/test_*.sh`.
# Exports: scaffold_project, cleanup_paths, run_claude, run_codex,
# assert_file_exists, assert_file_contains, assert_no_permission_denials,
# assert_output_mentions, with_timeout, log_info, log_pass, log_fail.

set -u

# ---------------------------------------------------------------------------
# Defaults
#
# CLAUDE_MODEL defaults to the cheapest production-tier Claude (Haiku 4.5).
# CODEX_MODEL defaults to `gpt-5.4-mini` — the cheapest tier exposed by
# `codex doctor` / models_cache.json on a ChatGPT-account install (the
# nominal `gpt-5-mini` alias from the PLAN.md draft is not exposed to
# ChatGPT-account users — see RESULTS.md Task 8 for the discovery).
# ---------------------------------------------------------------------------
: "${CLAUDE_MODEL:=claude-haiku-4-5-20251001}"
: "${CODEX_MODEL:=gpt-5.4-mini}"
: "${AGENT_TIMEOUT:=300}"  # 5 minutes per agent invocation
: "${VERBOSE:=0}"

# Locate the skill root (this file's grandparent: tests/lib/.. -> tests/.. -> skill root).
_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$_LIB_DIR/../.." && pwd)"
CREATE_PROJECT="$SKILL_ROOT/scripts/create_project.sh"

# Track artifacts to clean up on exit.
_CLEANUP_PATHS=()
_register_cleanup() {
    _CLEANUP_PATHS+=("$@")
}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
log_info() { echo "[INFO] $*" >&2; }
log_pass() { echo "[PASS] $*" >&2; }
log_fail() { echo "[FAIL] $*" >&2; }
log_verbose() { [ "$VERBOSE" = "1" ] && echo "[ ... ] $*" >&2 || true; }

# ---------------------------------------------------------------------------
# Scaffold and cleanup
# ---------------------------------------------------------------------------

# scaffold_project <project-path> <share-path> [extra create_project.sh flags...]
# Echoes the absolute project path on success.
scaffold_project() {
    local proj="$1"; shift
    local share="$1"; shift
    log_verbose "scaffold_project $proj --share-path $share $*"
    mkdir -p "$share"
    if ! bash "$CREATE_PROJECT" "$proj" --share-path "$share" "$@" >/dev/null 2>&1; then
        log_fail "scaffolder failed: $proj"
        return 1
    fi
    echo "$proj"
}

# cleanup_paths <paths...> — rm -rf with guard that each path lives under
# $HOME/rps-tests/. Anything else is refused (loud failure) so a mistake in
# a case script can't wipe unrelated state. The narrow allowlist also matches
# the path discipline that keeps Test A load-bearing: scratch dirs MUST live
# outside the template's default writable_roots (which include /tmp,
# /private/tmp, /var/folders, ~/.venvs, ~/.cache, ~/.local/share/uv).
cleanup_paths() {
    [ "${KEEP_ARTIFACTS:-0}" = "1" ] && { log_info "KEEP_ARTIFACTS=1 — leaving $*"; return 0; }
    local p
    for p in "$@"; do
        case "$p" in
            "$HOME/rps-tests/"*) rm -rf "$p" ;;
            *) log_fail "refusing to rm -rf outside \$HOME/rps-tests/: $p" ;;
        esac
    done
}

# ---------------------------------------------------------------------------
# Agent runners
#
# run_claude <cwd> <profile> <prompt>
#   profile = strict | permissive
#   strict     -> --permission-mode acceptEdits
#                 Empirically the ONLY headless mode that makes
#                 permissions.additionalDirectories load-bearing for Write:
#                   - default / auto / dontAsk: Write to ANY path outside the
#                     workspace is recorded as a permission_denial in headless
#                     mode (even when the path is in additionalDirectories or
#                     additionalDirectories carries an explicit Write(...) allow
#                     rule). The default mode silently denies headless because
#                     there is no human to approve a tool-use prompt.
#                   - acceptEdits: writes INSIDE workspace+additionalDirectories
#                     succeed; writes OUTSIDE that set are still recorded as
#                     permission_denials. So if register_share_path_with_agents
#                     did not register the absolute share path, the write to
#                     <share>/Notes/test.txt is denied — verified against a
#                     surgically-broken project (denials > 0).
#                   - bypassPermissions: would accept everything and defeat the test.
#                 See RESULTS.md Task 8 for the empirical sweep that produced
#                 this choice; the PLAN.md draft assumed default mode honored
#                 additionalDirectories in headless, which it does not.
#   permissive -> --permission-mode bypassPermissions; use for Tests B/C/D
#   Emits JSON on stdout; non-zero exit on CLI failure.
#
# run_codex <cwd> <profile> <prompt>
#   profile = strict | permissive
#   strict     -> -s workspace-write -c approval_policy="never"
#                 (model-generated commands run sandboxed; writes outside the
#                  workspace + the .codex/config writable_roots fail; agent
#                  cannot escalate because approval_policy=never)
#   permissive -> --dangerously-bypass-approvals-and-sandbox
# ---------------------------------------------------------------------------

run_claude() {
    local cwd="$1"; local profile="$2"; local prompt="$3"
    local -a args
    # stream-json carries tool-use events (Bash command invocations, file
    # reads, etc.) which the assert_output_mentions check needs to find the
    # skill name / scaffolder path even when the model's final summary text
    # doesn't echo them verbatim. The single-object `json` format would hide
    # tool details inside the harness.
    args=(-p "$prompt" --model "$CLAUDE_MODEL" --output-format stream-json --verbose)
    # --plugin-dir loads the in-development superRA repo so the tests exercise
    # the local research-project-setup skill (not whatever version of superRA
    # is registered under ~/.claude/plugins/cache/). Without this, Test D
    # (trigger discovery from an unrelated CWD) cannot find the skill.
    local superra_root
    superra_root="$(cd "$SKILL_ROOT/../.." && pwd)"
    args+=(--plugin-dir "$superra_root")
    if [ "$profile" = "permissive" ]; then
        args+=(--permission-mode bypassPermissions)
    else
        # strict: acceptEdits is the only headless mode that makes
        # additionalDirectories load-bearing (see comment block above).
        args+=(--permission-mode acceptEdits)
    fi
    log_verbose "claude (cwd=$cwd profile=$profile): ${args[*]}"
    (cd "$cwd" && with_timeout "$AGENT_TIMEOUT" claude "${args[@]}")
}

run_codex() {
    local cwd="$1"; local profile="$2"; local prompt="$3"
    local -a args
    args=(-m "$CODEX_MODEL" --skip-git-repo-check --json -C "$cwd")
    if [ "$profile" = "permissive" ]; then
        args+=(--dangerously-bypass-approvals-and-sandbox)
    else
        args+=(-s workspace-write -c 'approval_policy="never"')
    fi
    args+=("$prompt")
    log_verbose "codex (cwd=$cwd profile=$profile): ${args[*]}"
    with_timeout "$AGENT_TIMEOUT" codex exec "${args[@]}"
}

# with_timeout <seconds> <cmd...>
# Portable timeout with a hard SIGKILL guarantee.
#   - GNU coreutils: gtimeout/timeout --kill-after=10 — SIGTERM at <secs>, SIGKILL 10s later.
#   - Pure-bash fallback (macOS without coreutils): run the child in its own
#     process group, SIGTERM the whole group at <secs>, SIGKILL the group
#     10s later. This kills subprocess trees and children that ignore
#     SIGTERM (the perl-alarm fallback we replaced did not).
with_timeout() {
    local secs="$1"; shift
    if command -v gtimeout >/dev/null 2>&1; then
        gtimeout --kill-after=10 "$secs" "$@"; return $?
    fi
    if command -v timeout >/dev/null 2>&1; then
        timeout --kill-after=10 "$secs" "$@"; return $?
    fi
    set -m
    ( "$@" ) &
    local pid=$!
    # Watcher redirects to /dev/null so its `sleep` child doesn't hold the
    # parent's command-substitution pipe open after the main child exits.
    ( sleep "$secs" && kill -TERM -"$pid" 2>/dev/null && sleep 10 && kill -KILL -"$pid" 2>/dev/null ) >/dev/null 2>&1 &
    local watcher=$!
    wait "$pid"; local rc=$?
    # Kill the watcher's whole process group (it's its own group leader under
    # set -m) so the inner `sleep` is reaped — otherwise an orphan sleep keeps
    # the function returning but lets the surrounding $(...) capture hang.
    kill -TERM -"$watcher" 2>/dev/null
    wait "$watcher" 2>/dev/null
    return $rc
}

# ---------------------------------------------------------------------------
# Assertions
# ---------------------------------------------------------------------------

assert_file_exists() {
    local p="$1"
    if [ -e "$p" ]; then return 0; fi
    log_fail "assert_file_exists: $p"
    return 1
}

assert_file_contains() {
    local p="$1"; local needle="$2"
    if [ -e "$p" ] && grep -qF "$needle" "$p"; then return 0; fi
    log_fail "assert_file_contains: $p does not contain '$needle'"
    return 1
}

# assert_no_permission_denials <claude-stream-json-blob>
# Parses each JSONL line and finds the final `result` event, then asserts
# its permission_denials array is empty. With stream-json output the result
# event is the LAST line (it carries the same `permission_denials` field as
# the single-object `json` format).
assert_no_permission_denials() {
    local blob="$1"
    local n
    n=$(printf '%s' "$blob" | python3 -c '
import json, sys
result_obj = None
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    try: ev = json.loads(line)
    except Exception: continue
    if ev.get("type") == "result":
        result_obj = ev
if result_obj is None:
    print(-1); sys.exit(0)
pd = result_obj.get("permission_denials", [])
print(len(pd) if isinstance(pd, list) else -1)
')
    if [ "$n" = "0" ]; then return 0; fi
    log_fail "assert_no_permission_denials: $n denial(s) recorded"
    return 1
}

# assert_no_codex_sandbox_violation <codex-jsonl-blob>
# Scans codex JSONL events for sandbox/permission failure markers. Catches
# both explicit error events and agent_message / command_execution events
# whose payload reports a sandbox-blocked write (Codex tends to surface
# `operation not permitted` and similar phrasing in either the agent's
# narrative or the failing shell command's aggregated_output).
assert_no_codex_sandbox_violation() {
    local blob="$1"
    if printf '%s' "$blob" | grep -qiE '(operation not permitted|blocked by the sandbox|sandbox.*(deny|denied|violation)|writable_roots|EACCES|EPERM|read-only file system|"(error|turn\.failed)"[^}]*(sandbox|permission|writable_roots|denied))'; then
        log_fail "assert_no_codex_sandbox_violation: sandbox/permission failure detected"
        return 1
    fi
    return 0
}

# assert_output_mentions <output-text> <substring-1> [<substring-2> ...]
# Passes if ANY substring is found (case-insensitive). Used for trigger-discovery
# assertions where the surface form varies between LLM responses.
assert_output_mentions() {
    local blob="$1"; shift
    local sub
    for sub in "$@"; do
        if printf '%s' "$blob" | grep -qiF "$sub"; then return 0; fi
    done
    log_fail "assert_output_mentions: none of [$*] found in output"
    return 1
}

# ---------------------------------------------------------------------------
# Preflight
# ---------------------------------------------------------------------------

preflight_claude() {
    command -v claude >/dev/null 2>&1 || { log_info "claude CLI not installed — skipping Claude rows"; return 1; }
    return 0
}

preflight_codex() {
    command -v codex >/dev/null 2>&1 || { log_info "codex CLI not installed — skipping Codex rows"; return 1; }
    codex login status 2>&1 | grep -qiE "(logged in|using)" || { log_info "codex not logged in — skipping Codex rows"; return 1; }
    return 0
}

# Install / uninstall the in-development research-project-setup skill into
# the global Codex skills directory (~/.codex/skills/). Required for Test D
# (trigger discovery from an unrelated CWD) because Codex skill discovery
# walks ~/.codex/skills/ and the marketplace plugin cache, not arbitrary
# project trees. The marketplace `superra@superRA` plugin pre-dates this
# skill, so without this install Test D codex cannot find it.
#
# Idempotent: a no-op if the skill is already discoverable.
codex_install_skill_link() {
    local dest="$HOME/.codex/skills/research-project-setup"
    [ -e "$dest" ] && return 0
    mkdir -p "$HOME/.codex/skills"
    ln -sfn "$SKILL_ROOT" "$dest"
    log_verbose "codex: linked $dest -> $SKILL_ROOT"
}

codex_uninstall_skill_link() {
    local dest="$HOME/.codex/skills/research-project-setup"
    # Only remove if it points at our SKILL_ROOT (don't blow away an existing
    # real install).
    if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$SKILL_ROOT" ]; then
        rm -f "$dest"
        log_verbose "codex: removed $dest"
    fi
}

preflight_scaffolder() {
    [ -x "$CREATE_PROJECT" ] || { log_fail "create_project.sh not executable at $CREATE_PROJECT"; return 1; }
    return 0
}
