---
name: report-in-markdown
description: Utility for producing well-formatted markdown reports that contain figures, LaTeX math, tables, or multi-section prose — lengthy output that reads poorly in a terminal, standalone reports meant for humans, the Stage 2 consolidation of `RESULTS.md` at INTEGRATE Phase C, and any implementer task section in `RESULTS.md` that embeds a figure or a math expression. Not for agent-only handoff text. Caller supplies the content; this skill enforces format discipline via reference files loaded on demand.
user-invocable: true
---

# Report in Markdown

A format-discipline utility. **The caller writes the content; this skill tells you how to structure, embed figures, render math, and (for permanent artifacts) fact-check.** No content modification.

## When to invoke

- You are writing or updating a `RESULTS.md` task section that contains a figure, table, or LaTeX math.
- You are at `integration-workflow` Phase C maturing `RESULTS.md` into its permanent form.
- You are producing a standalone markdown report (figures, math, long prose) that a human will read.
- You are reviewing a matured `RESULTS.md` and need the consolidation checklist.

Skip this skill for agent-only text handoffs with no figures, no math, no tables, and no human audience.

## Invocation contract

1. Decide your caller role from the load map below and load only those references.
2. Write content yourself following the loaded references' rules — this skill defines format, not content.
3. The target `attachments/` directory is a **caller parameter**; this skill does not hard-code it.

## Load map

| Caller | Load |
|---|---|
| Implementer writing a `RESULTS.md` task section with figures / math / tables | `rich-content.md` |
| Implementer writing a text-only `RESULTS.md` task section | nothing beyond this file |
| `implementation-workflow` reviewer (implementation review) | nothing beyond this file |
| `integration-workflow` Phase C doc-writer subagent (maturing `RESULTS.md`) | `baseline-io.md` + `rich-content.md` + `final-form.md` |
| `integration-workflow` Phase C doc-reviewer subagent | `final-form.md` |
| Standalone markdown report (any context) | `baseline-io.md` + `rich-content.md` |

## Figure directory

The target attachments directory is a caller parameter; this skill does not hard-code it. Stage defaults and the "unsure which directory" fallback are in `references/rich-content.md` §Figures → The attachments directory is a caller parameter.

## References

- `references/baseline-io.md` — frontmatter spec, filename convention, output-path resolution, git metadata capture. For permanent artifacts only.
- `references/rich-content.md` — figure handling (PDF→PNG, relative-path embedding), LaTeX math, markdown tables, file references. For any caller with embedded content.
- `references/final-form.md` — consolidation discipline for Stage 2 `RESULTS.md`: fact-check checklist, task-indexed → reader-facing restructure, figure materialization, relocation. For the INTEGRATE Phase C caller and the integration reviewer.
