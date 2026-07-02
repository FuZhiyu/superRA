---
title: "Approved Dependency DEPENDENCY_TITLE_SENTINEL_BRASS"
status: approved
depends_on: []
tags: [fixture, dependency]
created: 2026-06-19
---

## Objective

This dependency exists so target task reads show sibling dependency metadata.

DEPENDENCY_OBJECTIVE_SENTINEL_SLATE

## Results

DEPENDENCY_RESULTS_EXCLUSION_SENTINEL_NEVER_INHERIT

This result sentinel must not appear in `superra task read` output for sibling
targets unless an agent explicitly reads this dependency task.
