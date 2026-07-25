---
title: "Always-Loaded Behavior Fixture Root"
status: not-started
depends_on: []
tags:
  - fixture
  - always-loaded-canary
created: 2026-06-19
---

## Objective

Disposable task tree for the always-loaded skill live coverage. It
exercises the Codex role-spec body-load path: a Codex agent has no skill autoload,
so it loads the always-loaded skills (`superRA:using-superra` and
`superRA:report-in-markdown`) from the role-spec body before acting. The single
leaf task produces a schema-identified output mutation while the harness records
the available command-execution evidence.
