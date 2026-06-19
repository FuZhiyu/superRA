---
title: "Always-Loaded Canary Fixture Root"
status: not-started
depends_on: []
tags:
  - fixture
  - always-loaded-canary
created: 2026-06-19
---

## Objective

Disposable task tree for the always-loaded skill live coverage (task 10). It
exercises the Codex role-spec body-load path: a Codex agent has no skill autoload,
so it loads the always-loaded skills (`superRA:using-superra` and
`superRA:report-in-markdown`) from the role-spec body before acting. The single
leaf task below asks for skill-unique canary side effects that are only producible
once those skill bodies are in context.
