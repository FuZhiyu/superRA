---
title: "Harness Loading Fixture Root"
status: in-progress
depends_on: []
tags: [fixture, harness-loading]
created: 2026-06-19
---

## Objective

This disposable task tree exists only for agent instruction-following tests.
Any assigned agent must use `superra task read` before acting.

ROOT_CONTEXT_SENTINEL_ALPINE

### Context

The agent should gather sentinel strings from task-read context, explicit
marker-file reads, and the final artifact schema. It should not run a test
suite or edit source code.
