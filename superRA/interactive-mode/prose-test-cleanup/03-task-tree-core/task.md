---
title: "Replace Task-Tree Core Prose Oracles"
status: not-started
depends_on:  []
---

## Objective

Replace task-tree core and CLI tests that assert rendered diagnostics, warnings, labels, or Finding.message prose with stable codes and structured fields plus observable exit codes, mutations, filesystem state, parser wiring, and call arguments. Preserve rule IDs as structured identities. Success: task-tree core exposes structured finding/error data, human text is presentation-only, and targeted/full task-tree tests pass with red-green evidence.

## Planner Guidance

Own test_cli.py, test_task_tree.py, _task_validate.py, task_check.py, and directly related core diagnostic producers. Do not touch dashboard/comment presentation, hook adapter, or other cleanup children.

## Results
