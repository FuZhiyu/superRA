---
title: "Build UV-Managed Pyzotero Tooling"
status: not-started
depends_on:
  - 01-skill-contract
tags: [python, uv, pyzotero]
script: skills/zotero-paper-reader/scripts/zotero_tool.py
input:
  - skills/zotero-paper-reader/pyproject.toml
output:
  - skills/zotero-paper-reader/scripts/zotero_tool.py
  - skills/zotero-paper-reader/pyproject.toml
  - skills/zotero-paper-reader/uv.lock
created: 2026-06-04
---

## Objective

Implement a skill-owned Python command surface that agents can run with `uv` to query Zotero without MCP. The tooling must support local-first reads through pyzotero, fall back to the Zotero Web API when configured, emit structured JSON for agent consumption, and report the pyzotero version in diagnostic output. It must never print API keys or secrets.

### Required Commands

The command surface must cover at least: health/check-access, search metadata, search full text, get item, get children, list collections, list tags, DOI index, get attachment full text, and get PDF path or download path. The PDF command must preserve the old local-storage-first behavior and use pyzotero/web API rather than raw MCP calls.

### Configuration Contract

Read configuration from environment variables and, when present, a project-local `Notes/.env` without exposing values to the agent transcript. Required or optional variables must be documented in the skill reference: `ZOTERO_LIBRARY_ID`, `ZOTERO_LIBRARY_TYPE`, `ZOTERO_API_KEY`, and any local-mode override or storage-path override introduced by the implementation.

## Planner Guidance

Prefer a single script with subcommands over multiple small scripts if that keeps invocation stable. Consider `uv run --project skills/zotero-paper-reader zotero-tool ...` or an equivalent console script. Pin pyzotero in the skill-local `pyproject.toml` to the selected minor/patch version and commit `uv.lock` so the shipped dependency is inspectable.

## Results

### Key Findings

- Pending.

