#!/usr/bin/env bash
# Shared setup for the opt-in live agent-loading smokes.
#
# These smokes drive a real Claude or Codex agent through the bundled
# `bundle-two-tasks` fixture and then assert structural transcript evidence
# with the shared Python parser under this directory. They are manual-only:
# nothing here runs in default CI. Every entry script gates on RUN_LIVE_HARNESS
# (see require_live_gate) so a bare invocation in CI is a documented no-op.
#
# The fixture, the expected artifact, the marker files, and the transcript
# parser are all single-sourced — this library only copies the committed
# fixture into a throwaway workspace and writes a `superRA/superra` wrapper
# that forwards to the live task-tree CLI. It does not re-derive the mock
# scenario.

# Resolve repo root from this file's location (tests/harness-instruction-following).
SMOKE_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SMOKE_LIB_DIR/../.." && pwd)"
FIXTURE_ROOT="$REPO_ROOT/tests/fixtures/task-trees/bundle-two-tasks"
TASK_TREE_CLI="$REPO_ROOT/skills/task-tree/scripts/cli.py"

# require_live_gate <gate-var-name>
# Exit 0 (documented no-op) when the named gate env var is not "1".
require_live_gate() {
  local var="${1:-RUN_LIVE_HARNESS}"
  if [ "${!var:-0}" != 1 ]; then
    echo "SKIP  $var is not set to 1 — live harness smoke is opt-in and never runs in CI."
    echo "      Set $var=1 (with a logged-in CLI) to run it."
    exit 0
  fi
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "FAIL: $1 not on PATH" >&2
    exit 2
  fi
}

# seed_workspace <dest-dir>
# Copy the committed fixture's superRA tree and marker files into <dest-dir>
# and drop a `superRA/superra` wrapper that forwards to the live task-tree CLI,
# so the agent can run `./superRA/superra task read <path>` and read
# `markers/...` exactly as in a real project. <dest-dir> must already exist.
seed_workspace() {
  local dest="$1"
  cp -R "$FIXTURE_ROOT/superRA" "$dest/superRA"
  cp -R "$FIXTURE_ROOT/markers" "$dest/markers"
  # Intentionally NOT copying expected/: the agent must produce loading-evidence.json
  # from task-read context and marker reads, not by copying the expected artifact.
  mkdir -p "$dest/superRA"
  cat >"$dest/superRA/superra" <<EOF
#!/usr/bin/env bash
# Disposable smoke wrapper: forward to the live task-tree CLI.
exec python3 "$TASK_TREE_CLI" "\$@"
EOF
  chmod +x "$dest/superRA/superra"
}

# expected_artifact_path
expected_artifact_path() {
  echo "$FIXTURE_ROOT/expected/loading-evidence.expected.json"
}

# The shared mock-task prompt. Identical text for Claude and Codex so both
# harnesses exercise the same bundled multi-requirement scenario: two task
# reads, three marker reads, dependency-result exclusion, and one JSON write.
# The prompt asks only for sentinel collection plus one JSON write — no code,
# no installs, no test runs.
smoke_task_prompt() {
  cat <<'EOF'
You are an implementer assigned a bundle of two superRA tasks in this workspace:
agent-loading-bundle/02-primary-loading-task and
agent-loading-bundle/03-secondary-loading-task.

Do exactly this, in order, and nothing else:

1. Run `./superRA/superra task read agent-loading-bundle/02-primary-loading-task`.
2. Run `./superRA/superra task read agent-loading-bundle/03-secondary-loading-task`.
3. Read the files markers/primary-marker.txt, markers/secondary-marker.txt, and
   markers/shared-marker.json.
4. Write loading-evidence.json at the workspace root with exactly this JSON,
   filling each value from the sentinel strings you saw in the task-read output
   and the marker files (every value is a literal sentinel string already
   present in that output — do not invent or transform values):

{
  "schema_version": 1,
  "task_read_context": {
    "root": "<root context sentinel from the ancestor context>",
    "parent": "<parent context sentinel from the ancestor context>",
    "primary_target": "<primary target sentinel>",
    "secondary_target": "<secondary target sentinel>",
    "open_comment": "<unresolved comment sentinel surfaced by task read>"
  },
  "dependency_metadata": {
    "slug": "<dependency slug surfaced by task read>",
    "status": "<dependency status surfaced by task read>",
    "title_sentinel": "<dependency title sentinel surfaced by task read>"
  },
  "dependency_results_excluded": true,
  "marker_files": {
    "primary": "<value from markers/primary-marker.txt>",
    "secondary": "<value from markers/secondary-marker.txt>",
    "shared": "<shared_marker value from markers/shared-marker.json>"
  },
  "artifact_content": "ARTIFACT_SENTINEL_QUARTZ"
}

Set dependency_results_excluded to true only if the dependency's ## Results
sentinel did NOT appear in either task-read output. Do not edit any code, do not
install anything, and do not run any test suite. This is the only work.
EOF
}

# Orchestrator prompt: ask the main agent to run the superimplement workflow on
# the seeded frontier. The frontier is intentionally cheap (the same shallow
# sentinel-collection leaf tasks), so the smoke tests dispatch behavior, not
# implementation quality.
orchestrator_prompt() {
  cat <<'EOF'
superimplement

Run the superimplement workflow on the superRA task tree in this workspace. The
dispatchable frontier is the two leaf tasks under agent-loading-bundle
(02-primary-loading-task and 03-secondary-loading-task); they are a same-parent
bundle and each is a shallow sentinel-collection task that writes loading-evidence.json.

Follow the documented default dispatch path: dispatch an implementer subagent for
the frontier, then dispatch a reviewer subagent to review the implementation. Do
not implement the task inline yourself unless a documented direct-mode exception
applies; if you do fall back to direct mode, state the documented reason and still
dispatch a reviewer subagent.
EOF
}
