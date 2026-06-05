---
title: "Migrate Paper Reading Workflow"
status: approved
depends_on:
  - 02-pyzotero-tooling
  - 06-vendor-mistral-skill
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

### What was done

Rewrote the paper-reading workflow in two files:

**[skills/zotero-paper-reader/SKILL.md](../../skills/zotero-paper-reader/SKILL.md)** — slimmed the workflow section to a 7-step summary and routes detailed procedure to the new reference. The `mistral-pdf-to-markdown` conversion step (Step 6) points at the in-repo skill vendored in [06-vendor-mistral-skill](../06-vendor-mistral-skill/task.md), so the capability is self-contained with no external-plugin dependency. The `uv run --script <skill-dir>/scripts/zotero_tool.py` invocation uses the harness-neutral `<skill-dir>` placeholder (replacing the earlier Claude-only `${CLAUDE_SKILL_DIR}`) for install-location and cross-harness independence.

**[skills/zotero-paper-reader/references/paper-reading.md](../../skills/zotero-paper-reader/references/paper-reading.md)** — new detailed reference containing:

- Exact command invocations for all 7 steps, each with annotated JSON output showing the fields an agent must inspect (`data.itemType`, `data.parentItem`, `data.contentType`, `key`, `path`, `source`).
- **Attachment-parent hydration** (Step 2): full-text search returns items where `data.itemType == "attachment"` with `data.parentItem` pointing to the top-level key; the reference shows the exact hydration pattern (`item PARENT_KEY`) and an example payload.
- **Disambiguation** (Step 3): concise display format for multiple matches; asks the user only when the intended paper cannot be inferred from context.
- **Reading discipline** (Step 7): offset/limit pattern, grep-for-section pattern, abstract-first rule.
- **Troubleshooting** covering all six specified cases: local API disabled (distinguishes Zotero not running vs. API option off), no PDF child, missing local file (linked-file vs. missing-credentials sub-cases), missing Web API credentials, full-text attachment hits needing hydration, full-text requiring Web API.

### Constraints check

- Output path convention `Notes/PaperInMarkdown/Author_Year_ShortTitle.md` preserved (matching the prior skill's actual `ShortTitle` pattern; the task constraint's `Author_Year_Title.md` was a paraphrase of the same convention).
- PDF conversion details not duplicated — reference delegates to `mistral-pdf-to-markdown` skill by name.
- Large-paper reading discipline enforced: abstract/introduction first, grep-then-offset for sections, no whole-file load.

