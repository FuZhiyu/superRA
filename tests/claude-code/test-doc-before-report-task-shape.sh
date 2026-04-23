#!/usr/bin/env bash
# Test: doc-before-report for task-shape concerns in superRA
# Verifies that durable concerns are documented before status-report summary.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/test-helpers.sh"

echo "=== Test: doc before report for task-shape concerns ==="
echo ""

prompt=$(cat <<'EOF'
Under superRA execution and integration rules, suppose an implementer realizes
the current route is still inside the task objective, but the task probably
needs to be split later through `planning-workflow §User Feedback and Changing
Plans`. The implementer also wants to explain why the current route changed.
Reply with exactly two bullets:
- PLAN.md: include both the durable task-shape recommendation/concern and the
  current-route note that future agents need in the handoff doc.
- Status report: include both the rationale/summary for the route change and
  the upward pointer that this planning decision belongs with the
  orchestrator/researcher via `planning-workflow §User Feedback and Changing
  Plans`.
Do not merge the two surfaces together.
EOF
)

output=$(run_claude "$prompt" 90)

plan_label="PLAN.md:\\|\\*\\*PLAN.md\\*\\*:"
status_label="Status report:\\|\\*\\*Status report\\*\\*:"

if assert_contains "$output" "$plan_label" "Uses the requested PLAN.md line"; then
    :
else
    exit 1
fi

if assert_line_contains "$output" "$plan_label" "task block\\|review-notes\\|current route\\|document\\|record" "Documents the durable concern in the handoff doc"; then
    :
else
    exit 1
fi

if assert_line_contains "$output" "$plan_label" "task-shape\\|split\\|recommendation\\|concern\\|boundary\\|change shape\\|restructure" "Keeps the task-shape concern in PLAN.md"; then
    :
else
    exit 1
fi

if assert_line_contains "$output" "$plan_label" "current route\\|route change\\|steps\\|task block\\|review-notes\\|handoff doc\\|PLAN.md" "Keeps the durable current-route note in PLAN.md"; then
    :
else
    exit 1
fi

if assert_contains "$output" "$status_label" "Uses the requested Status report line"; then
    :
else
    exit 1
fi

if assert_line_contains "$output" "$status_label" "summary\\|rationale\\|why\\|uncertainty\\|pointer\\|status message\\|status report\\|explain\\|context\\|route changed\\|recommend" "Uses the status report for explanation, summary, or an upward recommendation"; then
    :
else
    exit 1
fi

if assert_line_contains "$output" "$status_label" "orchestrator\\|planning-workflow\\|changing plans\\|researcher" "Uses the report to point the planning decision upward"; then
    :
else
    exit 1
fi

echo ""
echo "=== Doc before report task-shape test passed ==="
