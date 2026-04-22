#!/usr/bin/env bash
# Test: adaptive planning principles in superRA
# Verifies that planners use objective-defined tasks and omit fake step detail.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/test-helpers.sh"

echo "=== Test: adaptive planning principles ==="
echo ""

prompt=$(cat <<'EOF'
Under superRA planning-stage rules, suppose the planner knows the objective and
the file boundary for a task, but does not yet know the best implementation
route. Should the planner fill PLAN.md with detailed code-like steps anyway?
What should the task block emphasize, and what should happen to the steps
section? Answer briefly.
EOF
)

output=$(run_claude "$prompt" 90)

if assert_contains "$output" "objective\\|task heading\\|Script\\|Input\\|Output" "Emphasizes objective-defined task scope"; then
    :
else
    exit 1
fi

if assert_contains "$output" "omit\\|optional\\|leave.*step\\|no step" "Allows the steps section to stay open"; then
    :
else
    exit 1
fi

if assert_contains "$output" "invent\\|fake\\|exact code\\|pseudo" "Rejects fake specificity"; then
    :
else
    exit 1
fi

echo ""
echo "=== Adaptive planning principles test passed ==="
