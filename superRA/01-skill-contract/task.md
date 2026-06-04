---
title: "Define Zotero Skill Contract"
status: not-started
depends_on: []
tags: [planning, skill-creation, zotero]
output:
  - skills/zotero-paper-reader/SKILL.md
  - skills/zotero-paper-reader/references/access-modes.md
created: 2026-06-04
---

## Objective

Define the user-facing and agent-facing contract for the new `zotero-paper-reader` skill. The contract must preserve the existing workflow of finding a Zotero paper, locating its PDF, converting it to markdown, saving under `Notes/PaperInMarkdown`, and analyzing it in sections. It must also expose expanded local-library capabilities that pyzotero supports: metadata search, full-text search, item lookup, child-item lookup, collection and tag listing, DOI-to-key indexing, and attachment full-text/PDF retrieval where available.

### Constraints

Keep `SKILL.md` concise and procedural. Put API details, access-mode fallback rules, CLI examples, and troubleshooting in one-level-deep references. Do not duplicate the Mistral PDF-to-Markdown skill's conversion instructions beyond a pointer and the handoff contract needed to call it. Do not instruct agents to use MCP tools anywhere in the new skill.

## Planner Guidance

Use the existing personal skill at `/Users/zhiyufu/Dropbox/app_settings/dotfiles/claude/.claude/skills/zotero-paper-reader` as the behavioral baseline. Use pyzotero documentation for exact local/web capability boundaries. Treat local API as the default for reads and web API as the fallback for unavailable local Zotero, non-public remote libraries, and any future write operation.

## Results

### Key Findings

- Pending.

