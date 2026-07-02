---
title: "Primary Loading Evidence Task"
status: not-started
depends_on:
  - 01-approved-dependency
tags: [fixture, primary]
output:
  - loading-evidence.json
created: 2026-06-19
---

## Objective

Read this task with `superra task read
agent-loading-bundle/02-primary-loading-task`, inspect the surfaced context,
then read the marker files listed below. Do not edit code or run tests.

PRIMARY_TARGET_SENTINEL_COBALT

Record these values in `loading-evidence.json` at the fixture root:

- root context sentinel from the ancestor context
- parent context sentinel from the ancestor context
- this primary target sentinel
- unresolved comment sentinel surfaced by task-read
- dependency title/status metadata surfaced by task-read
- marker value from `markers/primary-marker.txt`
- marker value from `markers/shared-marker.json`
- artifact sentinel `ARTIFACT_SENTINEL_QUARTZ`

The dependency's `## Results` sentinel is intentionally excluded from this
task-read context. Set the artifact field `dependency_results_excluded` to
`true` only if that sentinel did not appear in the target task-read output.
