#!/usr/bin/env bash
# Test: objective-first task semantics in superRA
# Verifies that missing within-task checks are treated as necessary work.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/test-helpers.sh"

echo "=== Test: objective-first task semantics ==="
echo ""

prompt=$(cat <<'EOF'
Under superRA implementation-stage rules, suppose PLAN.md has this task:

### Task 9: Build a firm-month panel for downstream leverage analysis
**Script:** `Code/build_panel.py`
**Input:** `raw/firms.csv` and `raw/monthly.csv`
**Output:** `build/panel.csv` with one row per firm-month

- [ ] Load both input files.
- [ ] Merge them on `firm_id` and `month`.
- [ ] Save `build/panel.csv`.

The listed steps forgot to include an obvious duplicate-key validation after the merge.
What should the implementer do, and how should the reviewer treat an implementation
that followed the listed steps mechanically but skipped that validation? Answer briefly.
EOF
)

output=$(run_claude "$prompt" 90)

if assert_contains "$output" "objective\\|scope contract\\|heading\\|Script\\|Input\\|Output" "Treats task scope as the real contract"; then
    :
else
    exit 1
fi

if assert_contains "$output" "duplicate\\|validation\\|check\\|verify" "Adds the missing within-task check"; then
    :
else
    exit 1
fi

if assert_contains "$output" "reviewer\\|REVISE\\|flag\\|finding\\|missing necessary check" "Reviewer flags mechanical omission"; then
    :
else
    exit 1
fi

echo ""
echo "=== Objective-first task semantics test passed ==="
