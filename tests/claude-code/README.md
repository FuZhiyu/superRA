# Claude Code Skills Tests

Automated tests for superRA skills using Claude Code CLI.

## Overview

This test suite verifies that skills are loaded correctly and Claude follows them as expected. Tests invoke Claude Code in headless mode (`claude -p`) and verify the behavior.

## Requirements

- Claude Code CLI installed and in PATH (`claude --version` should work)
- Run the suite from a local clone of this repo
- No separate plugin install is required for the default local-development path; these tests exercise the repo-local superRA checkout
- If you want to compare against an installed plugin instead, install `superRA` using the root README first

## Running Tests

### Run all supported fast tests (recommended):
```bash
./run-skill-tests.sh
```

This default path is the supported green smoke suite for the current superRA checkout.

### Run the focused planning-principles test directly:
```bash
./run-skill-tests.sh --test test-adaptive-planning-principles.sh
```

### Run the focused objective-first execution test directly:
```bash
./run-skill-tests.sh --test test-objective-first-task-semantics.sh
```

### Run the focused integration escalation test directly:
```bash
./run-skill-tests.sh --test test-integration-task-shape-escalation.sh
```

### Run legacy integration coverage manually (slow, archival pre-superRA coverage):
```bash
./run-skill-tests.sh --integration
```

### Run a legacy manual-only test explicitly:
```bash
./run-skill-tests.sh --test test-subagent-driven-development.sh
```

### Run with verbose output:
```bash
./run-skill-tests.sh --verbose
```

### Set custom timeout:
```bash
./run-skill-tests.sh --timeout 1800  # 30 minutes for legacy integration tests
```

## Test Structure

### test-helpers.sh
Common functions for skills testing:
- `run_with_timeout SECONDS cmd ...` - Run a command with a portable timeout wrapper
- `run_claude "prompt" [timeout]` - Run Claude with prompt
- `assert_contains output pattern name` - Verify pattern exists
- `assert_not_contains output pattern name` - Verify pattern absent
- `assert_count output pattern count name` - Verify exact count
- `assert_order output pattern_a pattern_b name` - Verify order
- `create_test_project` - Create temp test directory
- `create_test_plan project_dir` - Create sample plan file

### Test Files

Each test file:
1. Sources `test-helpers.sh`
2. Runs Claude Code with specific prompts
3. Verifies expected behavior using assertions
4. Returns 0 on success, non-zero on failure

## Example Test

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/test-helpers.sh"

echo "=== Test: My Skill ==="

# Ask Claude about the skill
output=$(run_claude "What does the my-skill skill do?" 30)

# Verify response
assert_contains "$output" "expected behavior" "Skill describes behavior"

echo "=== All tests passed ==="
```

## Current Tests

### Fast Tests (run by default)

#### test-objective-first-task-semantics.sh
Focused coverage for the objective-first task/step rule (~30 seconds):
- Treats the task heading plus `Script` / `Input` / `Output` as the real scope contract
- Requires the implementer to add an omitted within-task validation check
- Requires the reviewer to flag mechanical step-following that misses a necessary check

#### test-adaptive-planning-principles.sh
Focused coverage for adaptive planning principles (~30 seconds):
- Keeps the task objective and scope fields as the center of the plan
- Allows the step section to stay open when the route is exploratory
- Rejects fake specificity such as invented exact-code planning steps

#### test-doc-before-report-task-shape.sh
Focused coverage for handoff-doc priority (~30 seconds):
- Keeps durable task-shape concerns and current-route state in `PLAN.md`
- Uses the status report for rationale and summary after the doc is updated
- Ensures the orchestrator still routes actual task-boundary changes through `planning-workflow`

#### test-integration-task-shape-escalation.sh
Focused coverage for integration-stage task-shape escalation (~30 seconds):
- Requires reviewers or refactors to record a better task-shape recommendation in the handoff docs
- Routes the recommendation through `planning-workflow` rather than rewriting the task boundary directly
- Keeps the final task-boundary decision under user discretion

### Legacy Manual Tests (not run by default)

#### test-subagent-driven-development.sh
Archived pre-superRA smoke test (~2 minutes):
- Skill loading and accessibility
- Workflow ordering (spec compliance before code quality)
- Self-review requirements documented
- Plan reading efficiency documented
- Spec compliance reviewer skepticism documented
- Review loops documented
- Task context provision documented

This file still targets the historical `subagent-driven-development` skill naming. It is retained as an archival reference only and is not part of the supported green default suite.

### Legacy Integration Tests (use `--integration` only when intentionally auditing archived coverage)

#### test-subagent-driven-development-integration.sh
Archived pre-superRA full-workflow execution test (~10-30 minutes):
- Creates real test project with Node.js setup
- Creates implementation plan with 2 tasks
- Executes plan using subagent-driven-development
- Verifies actual behaviors:
  - Plan read once at start (not per task)
  - Full task text provided in subagent prompts
  - Subagents perform self-review before reporting
  - Spec compliance review happens before code quality
  - Spec reviewer reads code independently
  - Working implementation is produced
  - Tests pass
  - Proper git commits created

**What it tests:**
- The workflow actually works end-to-end
- Our improvements are actually applied
- Subagents follow the skill correctly
- Final code is functional and tested

Like the legacy fast test above, this script still targets the historical `subagent-driven-development` workflow naming and is not part of the supported green path for current superRA development.

## Adding New Tests

1. Create new test file: `test-<skill-name>.sh`
2. Source test-helpers.sh
3. Write tests using `run_claude` and assertions
4. Add to test list in `run-skill-tests.sh`
5. Make executable: `chmod +x test-<skill-name>.sh`

## Timeout Considerations

- Default timeout: 5 minutes per test
- Claude Code may take time to respond
- Adjust with `--timeout` if needed
- Tests should be focused to avoid long runs

## Debugging Failed Tests

With `--verbose`, you'll see full Claude output:
```bash
./run-skill-tests.sh --verbose
```

Without verbose, only failures show output.

## CI/CD Integration

To run in CI:
```bash
# Run with explicit timeout for CI environments
./run-skill-tests.sh --timeout 900

# Exit code 0 = success, non-zero = failure
```

## Notes

- The supported green local-development path is `./run-skill-tests.sh`
- Legacy `subagent-driven-development` scripts remain in-tree only as historical reference coverage and are manual-only
- Tests verify skill *instructions*, not full execution
- Full workflow tests would be very slow
- Focus on verifying key skill requirements
- Tests should be deterministic
- Avoid testing implementation details
