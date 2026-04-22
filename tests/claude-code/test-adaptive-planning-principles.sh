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
the `Script` / `Input` / `Output` for a task, but does not yet know the best
implementation route. Reply with exactly two bullets:
- Scope: ...
- Steps: ...
Should the planner fill PLAN.md with detailed code-like steps anyway?
EOF
)

output=$(run_claude "$prompt" 90)

scope_label="Scope:\\|\\*\\*Scope\\*\\*:"
steps_label="Steps:\\|\\*\\*Steps\\*\\*:"

if assert_contains "$output" "$scope_label" "Uses the requested Scope line"; then
    :
else
    exit 1
fi

if assert_line_contains "$output" "$scope_label" "task heading\\|Script\\|Input\\|Output" "Emphasizes objective-defined task scope"; then
    :
else
    exit 1
fi

if assert_contains "$output" "$steps_label" "Uses the requested Steps line"; then
    :
else
    exit 1
fi

if assert_line_contains "$output" "$steps_label" "omit\\|optional\\|leave" "Allows the steps section to stay open"; then
    :
else
    exit 1
fi

if assert_line_contains "$output" "$steps_label" "do not\\|don't\\|should not\\|avoid\\|fabricat\\|invent\\|not.*code\\|code-like\\|exact code\\|fake specificity" "Rejects fake code-like specificity"; then
    :
else
    exit 1
fi

if assert_not_contains "$output" '```' "Does not answer by writing code"; then
    :
else
    exit 1
fi

echo ""
echo "=== Adaptive planning principles test passed ==="
