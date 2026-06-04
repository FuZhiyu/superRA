---
title: "Verify Zotero Skill Behavior"
status: not-started
depends_on:
  - 04-inventory-and-packaging
tags: [tests, verification, skill-creation]
input:
  - skills/zotero-paper-reader/SKILL.md
  - skills/zotero-paper-reader/scripts/zotero_tool.py
output:
  - superRA/05-verification/task.md
created: 2026-06-04
---

## Objective

Verify the skill at the script and agent-instruction levels. The verification must prove that local-disabled and missing-credential paths fail with actionable guidance, that commands emit parseable JSON without leaking secrets, that the pyzotero version is logged, and that the paper-reading instructions no longer mention MCP. If a live local Zotero instance with the local API enabled is available, also run a smoke test for health, search, child lookup, and PDF-path retrieval, and confirm the deferred local full-text-search boundary (`items(q=..., qmode="everything")` against the local API) — update `references/access-modes.md` if the live result differs from the current conservative "unverified / Web-API-only" default.

### Constraints

Use deterministic script-level tests where possible so verification does not require a private Zotero library. Any live-library smoke result must record only non-sensitive metadata and must not commit API keys, PDF contents, or private library data.

## Planner Guidance

Consider adding tests that mock pyzotero responses and filesystem storage. Also run text checks over `skills/zotero-paper-reader` to block `mcp__zotero` regressions and stale setup instructions. Record verification commands and outcomes in this task's `## Results`.

## Results

### Key Findings

- Pending.

