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
they should really be recomposed into one different task shape. Reply with
exactly three bullets:
- Record: ...
- Decision: ...
- Do not: ...
EOF
)

output=$(run_claude "$prompt" 90)

record_label="Record:\\|\\*\\*Record\\*\\*:"
decision_label="Decision:\\|\\*\\*Decision\\*\\*:"
do_not_label="Do not:\\|\\*\\*Do not\\*\\*:"

if assert_contains "$output" "$record_label" "Uses the requested Record line"; then
    :
else
    exit 1
fi

if assert_line_contains "$output" "$record_label" "PLAN.md\\|review-notes\\|review notes\\|REVISE\\|Upstream Intent\\|handoff doc\\|RESULTS.md" "Records the issue in the current durable Phase B locations"; then
    :
else
    exit 1
fi

if assert_not_contains "$output" "Integration Intent" "Rejects retired Integration Intent wording"; then
    :
else
    exit 1
fi

if assert_contains "$output" "$decision_label" "Uses the requested Decision line"; then
    :
else
    exit 1
fi

if assert_line_contains "$output" "$decision_label" "planning-workflow\\|orchestrator\\|user\\|researcher" "Routes the boundary decision through orchestrator and planning"; then
    :
else
    exit 1
fi

if assert_contains "$output" "$do_not_label" "Uses the requested Do not line"; then
    :
else
    exit 1
fi

if assert_line_contains "$output" "$do_not_label" "rewrite\\|change\\|merge\\|recompose\\|recomposition\\|rename\\|reorder\\|combine\\|split\\|re-scop\\|unilateral" "Forbids unilateral task-structure rewrites"; then
    :
else
    exit 1
fi

if assert_line_contains "$output" "$do_not_label" "heading\\|Script\\|Input\\|Output\\|boundary\\|task block\\|task\\|tasks\\|recompose\\|recomposition\\|change shape\\|restructure\\|structural\\|combine\\|split\\|re-scop\\|rewrite the task boundary\\|unilateral" "Names the protected task structure or boundary"; then
    :
else
    exit 1
fi

echo ""
echo "=== Integration task-shape escalation test passed ==="
