---
title: "Build UV-Managed Pyzotero Tooling"
status: not-started
depends_on:
  - 01-skill-contract
tags: [python, uv, pyzotero]
script: skills/zotero-paper-reader/scripts/zotero_tool.py
input:
  - skills/zotero-paper-reader/scripts/zotero_tool.py
output:
  - skills/zotero-paper-reader/scripts/zotero_tool.py
created: 2026-06-04
---

## Objective

Implement a skill-owned Python command surface that agents can run with `uv` to query Zotero without MCP. The tooling must support local-first reads through pyzotero, fall back to the Zotero Web API when configured, emit structured JSON for agent consumption, and report the pyzotero version in diagnostic output. It must never print API keys or secrets.

### Required Commands

The command surface must cover at least: health/check-access, search metadata, search full text, get item, get children, list collections, list tags, DOI index, get attachment full text, and get PDF path or download path. The PDF command must preserve the old local-storage-first behavior and use pyzotero/web API rather than raw MCP calls.

### Configuration Contract

Read configuration from environment variables and, when present, a project-local `Notes/.env` without exposing values to the agent transcript. Required or optional variables must be documented in the skill reference: `ZOTERO_LIBRARY_ID`, `ZOTERO_LIBRARY_TYPE`, `ZOTERO_API_KEY`, and any local-mode override or storage-path override introduced by the implementation.

## Planner Guidance

Prefer a single self-contained script with subcommands over multiple small scripts if that keeps invocation stable. Use PEP 723 inline script metadata so agents can run the bundled file from wherever the skill is installed, for example `uv run --script <skill-root>/scripts/zotero_tool.py ...`. Pin pyzotero in that script metadata and make the `version` or health command print the resolved package version so drift is visible.

## Results

### Key Findings

- Pending.

## Revision Notes

Planner update on 2026-06-04: the command surface must not rely on `uv run --project skills/zotero-paper-reader` because plugin-installed users will not have that repo-relative path. Use a bundled script that resolves from the skill installation path instead.
