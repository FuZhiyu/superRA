---
title: "Replace Zotero CLI Prose Oracles"
status: not-started
depends_on:  []
---

## Objective

Replace Zotero CLI diagnostic-copy assertions with return codes, typed/unit-level error identities, unchanged target state, JSON fields, and no-secret-leak behavior. Preserve command and field inventories as structural contracts. Success: failure behavior is covered independently of human wording.

## Planner Guidance

Own tests/test-zotero-tool.sh and zotero_tool.py only.

## Results
