---
title: "Prune Prose-Specific Tests Conservatively"
status: not-started
depends_on:  []
---

## Objective

Remove tests that treat authored instruction prose, labels, layout, or diagnostic wording as regression oracles. Keep existing cheap checks for important behavior that is easy to miss: destructive or missing file mutations, exit status, generated schemas/identities, tool or dispatch ordering, and secret exposure. Prefer deleting a prose assertion over building new test infrastructure. Success: the cleanup changes tests and fixtures only, adds no live/network/agent execution, introduces no production API or helper framework, has a net-negative test diff, and retains the existing high-value behavioral suite.

## Planner Guidance

Budget: use an existing observable field or state only when the replacement is local and simpler than the prose assertion. Otherwise delete the assertion or its test. Do not add subprocesses, live harness calls, network access, structured diagnostic APIs, new error taxonomies, or production changes solely for testability. Preserve tests for branch-specific interactive routing and review behavior already protected before this task.

## Results
