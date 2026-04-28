---
name: report-in-markdown
description: Markdown style guide for any agent writing PLAN.md, RESULTS.md, status reports, or standalone markdown reports. Carries the always-applicable file-link citation rule plus a load map pointing to references for figures, LaTeX math, tables, and Stage 2 RESULTS.md final-form discipline.
user-invocable: true
---

# Report in Markdown

The markdown style guide. Every agent loads this skill — every agent writes markdown.

Always-applicable rules below. Details for figures / math / tables / Stage 2 maturation live in references; load only the reference your output needs.

## File-reference rule

Cite source files as **markdown links with line anchors**, not backtick-wrapped paths.

| Use case | Form |
|---|---|
| Single line | `[file.py:42](file.py#L42)` |
| Line range | `[file.py:40-50](file.py#L40-L50)` |
| Whole file | `[file.py](file.py)` |

Resolve paths **relative to the markdown file's directory** (use `../` as needed). For files at the worktree root, the relative path equals the project-root path. Wrong/correct contrast and edge cases: `references/rich-content.md` §File references.

## Load map

| Caller | Load |
|---|---|
| Implementer / reviewer writing routine task-block citations only | nothing beyond this file |
| Implementer writing a `RESULTS.md` task section with figures / math / tables | `rich-content.md` |
| `integration-workflow` Document doc-writer subagent (maturing `RESULTS.md`) | `baseline-io.md` + `rich-content.md` + `final-form.md` |
| `integration-workflow` Document doc-reviewer subagent | `final-form.md` |
| Standalone markdown report (any context) | `baseline-io.md` + `rich-content.md` |

The `attachments/` directory is a caller parameter; defaults and fallbacks are in `references/rich-content.md` §Figures.

## References

- `references/baseline-io.md` — frontmatter spec, filename convention, output-path resolution. Permanent artifacts only.
- `references/rich-content.md` — figure handling (PDF→PNG, relative-path embedding), LaTeX math, markdown tables, full file-reference discipline.
- `references/final-form.md` — Stage 2 `RESULTS.md` consolidation: fact-check checklist, task-indexed → reader-facing restructure, figure materialization, relocation.
