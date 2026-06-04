---
title: "Migrate Paper Reading Workflow"
status: not-started
depends_on:
  - 02-pyzotero-tooling
tags: [zotero, pdf, markdown]
input:
  - skills/zotero-paper-reader/scripts/zotero_tool.py
  - skills/zotero-paper-reader/SKILL.md
output:
  - skills/zotero-paper-reader/SKILL.md
  - skills/zotero-paper-reader/references/paper-reading.md
created: 2026-06-04
---

## Objective

Rewrite the paper-reading workflow so agents search Zotero through the new UV-managed pyzotero tooling, identify the selected top-level item and PDF attachment, retrieve a local or downloaded PDF path, invoke the existing PDF-to-Markdown conversion skill, and read/analyze the markdown file in sections. The workflow must handle multiple search matches by presenting concise metadata and asking the user to choose only when the intended paper cannot be inferred.

### Constraints

Preserve the old output convention `Notes/PaperInMarkdown/Author_Year_Title.md` unless a project-specific convention overrides it. Do not duplicate PDF conversion implementation details that belong to the PDF-to-Markdown skill. Keep large-paper reading discipline: inspect abstract/introduction first, use search for target sections, and avoid loading whole converted papers into context.

## Planner Guidance

Include examples for exact command invocations and JSON fields an agent should inspect. Add troubleshooting for local API disabled, Zotero Desktop not running, no PDF child attachment, missing local file, missing web credentials, and full-text search returning attachment hits that need parent-item hydration.

## Results

### Key Findings

- Pending.

