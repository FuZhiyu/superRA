---
title: "Per-Domain Skill-Load Fixture Root"
status: not-started
depends_on: []
tags:
  - fixture
  - domain-loads
created: 2026-06-19
---

## Objective

Disposable task tree for the per-domain skill-load live coverage (task 12). A single
shared leaf task below carries no domain of its own; the live dispatch supplies the
domain-triggering wording in its prompt, and the dispatched implementer loads every
domain skill the Skill-Load Manifest maps that wording to before acting. One body is
reused across every domain — only the dispatch wording differs — so adding a future
domain is a one-row change in the harness table, not a new fixture. The multi-domain
dispatch supplies wording matching more than one domain at once, proving the
"load every matching domain" rule rather than only first-match.
