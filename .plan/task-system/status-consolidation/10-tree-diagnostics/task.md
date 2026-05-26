---
title: "Build task_check.py diagnostic and fix tool"
status: not-started
review_status: ~
integration_status: ~
depends_on:
  - 02-data-layer
tags: [code, tooling]
script: ""
input: []
output: []
created: 2026-05-26
updated: 2026-05-26
---

## Objective

Build a `task_check.py` CLI tool that validates tree integrity and auto-fixes common issues. Two modes: `--check` (read-only diagnostic) and `--fix` (auto-repair).

### Diagnostic checks (`--check`)

1. **Status validity.** All `status` values are in the valid enum (`not-started`, `in-progress`, `implemented`, `revise`, `approved`, `archived`). Flag any stale `review_status` or `integration_status` fields still present in frontmatter.
2. **Rollup consistency.** For branch tasks: stored `status` matches `compute_status()` from children. Report mismatches.
3. **Dependency integrity.** All `depends_on` references resolve to existing sibling directories. No circular dependencies in the DAG.
4. **Archived dependency logic.** Flag tasks whose `depends_on` includes an archived sibling — the dependency is effectively void and should be removed or the task re-evaluated.
5. **Frontmatter completeness.** Required fields present (`title`, `status`). `created` ≤ `updated`. No unknown fields that suggest typos.
6. **Orphan directories.** Subdirectories of a task dir that contain no `task.md` (possible incomplete task creation).

Output: structured report (text by default, `--json` for machine consumption). Exit code 0 if clean, 1 if issues found.

### Auto-repair (`--fix`)

1. Rewrite stored parent statuses to match `compute_status()`.
2. Strip stale fields (`review_status`, `integration_status`) from frontmatter.
3. Remove `depends_on` entries pointing to archived siblings.
4. Update `updated:` dates on modified tasks.
5. Supports `--dry-run` to preview changes without writing.

Report what changed, how many tasks touched.

### Agent integration

The tool should be runnable by agents (implementers, reviewers, orchestrators) as a health check. The output format should be clear enough that an agent can parse it and decide what to fix manually vs what `--fix` handles.

## Results
