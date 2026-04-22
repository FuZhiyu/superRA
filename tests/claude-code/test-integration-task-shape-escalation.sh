#!/usr/bin/env bash
# Test: integration-stage task-shape escalation in superRA
# Verifies that task-boundary changes are recommended upward rather than rewritten unilaterally.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/test-helpers.sh"

echo "=== Test: integration task-shape escalation ==="
echo ""

prompt=$(cat <<'EOF'
Under superRA integration-stage rules, suppose an integration reviewer realizes
that Task 4 and Task 5 were planned as separate tasks, but the merged tree shows
they should really be recomposed into one different task shape. What should the
reviewer or refactor do, and who decides whether the task boundary actually
changes? Answer briefly.
EOF
)

output=$(run_claude "$prompt" 90)

if assert_contains "$output" "recommend\\|surface\\|report\\|raise" "Surfaces the task-shape issue upward"; then
    :
else
    exit 1
fi

if assert_contains "$output" "planning-workflow\\|changing plans\\|orchestrator" "Routes the change through the planning protocol"; then
    :
else
    exit 1
fi

if assert_contains "$output" "user\\|researcher\\|discretion\\|decide" "Leaves the task-boundary decision to user discretion"; then
    :
else
    exit 1
fi

echo ""
echo "=== Integration task-shape escalation test passed ==="
