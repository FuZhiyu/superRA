---
title: "Define Zotero Skill Contract"
status: implemented
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

Both output files are written. The contract is complete for task 02 (tooling implementation) and task 03 (paper-reading workflow) to build on.

**[`skills/zotero-paper-reader/SKILL.md`](../../skills/zotero-paper-reader/SKILL.md)** — five-step paper-reading workflow (search → children → pdf → mistral-pdf-to-markdown → read/analyze) plus a library-query command table covering all capabilities the objective requires. The PDF-to-Markdown handoff names the skill (`mistral-pdf-to-markdown`) and delegates conversion entirely to it, with no hardcoded script path. The `zotero_tool.py` invocation uses `${CLAUDE_SKILL_DIR}` throughout so the skill is install-location-independent. No MCP tools appear anywhere.

**[`skills/zotero-paper-reader/references/access-modes.md`](../../skills/zotero-paper-reader/references/access-modes.md)** — local vs. web access rules: how to enable the local API in Zotero Desktop, Web API credential variables (`ZOTERO_LIBRARY_ID`, `ZOTERO_LIBRARY_TYPE`, `ZOTERO_API_KEY`) and where to set them, a capability boundary table (read/write, local/web, full-text indexed vs. not), the PDF retrieval fallback logic, and troubleshooting for the four most common failure modes.

Key design decisions made during implementation:

- **Local API as default, Web API as fallback** — matches planner guidance and root task constraint. The tool script's `health` command detects availability and the reference documents the detection boundary.
- **PDF-to-Markdown pointer only** — `SKILL.md` instructs agents to invoke the `mistral-pdf-to-markdown` skill by name (not by script path), satisfying the install-location-independence constraint from the task dispatch and the root task.
- **`${CLAUDE_SKILL_DIR}` for script invocation** — consistent with the pattern already established in the `agent-contract` plugin's version of this skill and in the `mistral-pdf-to-markdown` skill itself.
- **All expanded pyzotero capabilities covered** — the command table in `SKILL.md` and the capability matrix in `access-modes.md` enumerate: metadata search, full-text search, item lookup, child-item lookup, collection listing, tag listing, DOI-to-key index, attachment full-text retrieval, and PDF retrieval. This maps directly to the objective's expanded-capability list.
- **Full-text search vs. attachment full-text retrieval kept distinct** — these are two different pyzotero calls. Library-wide full-text *search* is `items(q=..., qmode="everything")`; per-attachment full-text *retrieval* is `fulltext_item(attachment_key)`. The capability matrix and SKILL.md command rows name each call separately. Full-text *search* is documented as Web-API-backed with the local API marked "verify in task 02" (local mode is a thin proxy to Zotero Desktop's HTTP server, which historically has not exposed `qmode=everything`), so task 02 must verify and fall back to the Web API when local cannot serve it.

## Review Notes

1. **MAJOR** — [access-modes.md:45](../../skills/zotero-paper-reader/references/access-modes.md#L45) misattributes the local full-text *search* mechanism. The capability table cell reads `Full-text search | yes (via fulltext_item)`, but `fulltext_item(itemkey)` is a per-attachment full-text *retrieval* call (correctly the basis for row 51, "Attachment full-text retrieval"), not a library-wide search. Library full-text search is `items(q="term", qmode="everything")` on the Web API. This conflation is a contract/spec defect: task 02 builds `zotero_tool.py search --fulltext` against this capability table, and an implementer reading row 45 may wire the search subcommand to `fulltext_item` (which cannot search). Separately, whether the Zotero *local* API actually serves the `qmode=everything` full-text-search path is uncertain — pyzotero's local mode is a thin proxy to Zotero's local HTTP server, which has historically not exposed full-text search the way the Web API does. The contract asserts local full-text search as a flat "yes" without that caveat. Fix: (a) describe the correct search mechanism (`q` + `qmode=everything`) rather than `fulltext_item` in the full-text-search row, and (b) state the local-vs-web boundary for full-text *search* honestly — if local full-text search is not reliably available, mark it as web-only or "verify in task 02" rather than an unqualified "yes". The matching `--fulltext` claim in [SKILL.md:23-24](../../skills/zotero-paper-reader/SKILL.md#L23) and Library-Query row [SKILL.md:69](../../skills/zotero-paper-reader/SKILL.md#L69) should reflect the corrected boundary.
   → implemented: Capability table now splits the two operations — full-text *search* row reads `items(q=..., qmode="everything")` with Local API marked "verify in task 02" and Web API "yes (indexed content only)"; attachment full-text *retrieval* row reads `fulltext_item(attachment_key)`, "yes" in both modes. Added a two-bullet explainer distinguishing search from retrieval and instructing task 02 to verify local `qmode=everything` and fall back to Web API otherwise ([access-modes.md:42-58](../../skills/zotero-paper-reader/references/access-modes.md#L42-L58)). Corrected the local-mode overview line so it no longer claims unqualified full-text support ([access-modes.md:5](../../skills/zotero-paper-reader/references/access-modes.md#L5)). In SKILL.md, the Step-1 `--fulltext` example now says "indexed PDF content, Web API mode" with a follow-up sentence on the local-mode TBD boundary ([SKILL.md:23-26](../../skills/zotero-paper-reader/SKILL.md#L23-L26)), and the Library-Query rows now read "Full-text search (indexed content; Web API, local TBD task 02)" and "Attachment full-text retrieval (one attachment)" ([SKILL.md:71](../../skills/zotero-paper-reader/SKILL.md#L71), [SKILL.md:74](../../skills/zotero-paper-reader/SKILL.md#L74)).
