---
name: academic-writing
description: Use by default for .tex sources. In other formats, use for publication-quality writing such as manuscripts, exhibit notes, footnotes, appendices, and response letters. Covers proofreading, polishing, drafting, reviewing, and citation or consistency checks.
user-invocable: true
---

# Academic Writing

**Scope.** Use [communicate](../communicate/SKILL.md) for READMEs, documentation, working notes, and task files.

## The reader test

**Keep a sentence when the reader needs it** to understand a result, read an exhibit, or judge whether to believe a claim. Identify the venue before editing. Use terms and references the reader can resolve from the paper, cited work, and the venue's background knowledge. Prefer natural phrasing over technical exactness in every mode.

## Substance is the author's

- **Preserve the author's argument, logic, intent, tone, and claim strength.** Ask before changing what a sentence claims. Surface doubts about strength and keep the author's hedging as written.
- **Correct numbers and captions when the message still holds.** A new result that changes the message needs the author's decision.
- **Restructure only with explicit authorization.** Load [structure.md](references/structure.md) before changing the structure of existing text.

## Mode routing

**Use the mode named by the request, dispatch, or governing writing header**, in that order. Otherwise classify by draft state and requested output before loading references.

| Mode | Requests that name it | When no mode is named | Edit bar | Load |
|---|---|---|---|---|
| Proofread | “Proofread §X”, “fix typos” | Text is mostly in place. “Update the paper for the new estimates” and “align the paper with the code” on finished prose land here. | Correct what is wrong or would mislead a reader about a result. Keep imprecision while the meaning holds. | [Proofread](references/proofread.md), [Handbook](references/handbook.md) |
| Polish | “Polish §X”, “tighten this paragraph”, “apply these review findings” | Rough text the author wants recast into proper English. | Each edit fixes a reading problem identified by a style rule or the reader test. | [Polish](references/polish.md), [Style](references/style.md), [Handbook](references/handbook.md). Add [Structure](references/structure.md) for authorized restructuring. |
| Draft | “Draft the methods section”, “write up the results from these notes” | The requested passage is yet to be written. | Each added sentence passes the reader test. Apply the Proofread bar to existing text around the new passage. | [Draft](references/draft.md), [Structure](references/structure.md), [Style](references/style.md), [Handbook](references/handbook.md) |
| Review | “Review §X”, “check my citations”, “find issues in this draft” | The requested output is findings on an existing draft. | Report findings only. | [Review](references/review.md) and the references for the requested lanes. |

## Checks before editing

- **Inspect in-flight author work** with `git status` and `git diff`. The unstaged diff may be the target.
- **Honor inline directives.** Resolve `TODO`, `[fill in]`, `??`, and similar placeholders within scope and at the mode's bar. Leave `DO NOT EDIT` blocks untouched.
- **Read the paper's writing conventions** when recorded. See [conventions.md](references/conventions.md) for their home and inventory triggers.

## Audit your diff

- **Audit your diff before committing or handing off edits.** Compare against the pre-edit working copy. Revert each hunk that fixes nothing at the mode's bar. Apply the reader test to each added sentence and route displaced material using the table below.
- **Review a prose diff against the editor's mode.** Request reverts for hunks that miss its bar. Request corrections for errors the edit introduced and for in-scope text that is still wrong or misleading. Request no rewording.

## Where displaced material goes

| Material | Home |
|---|---|
| Construction mechanics beyond source, sample, and transformation | Replication package |
| Verification output, plausibility checks, sensitivities, and caveats removed from the text | One line each in the editor's `## Results`, or in the commit body without a task |
| Open judgment call for the author | The project's author-note macro if available, otherwise the agent's return |
| Specification difference between exhibits presented as one | Report to the researcher for a code fix |

## Knowledge files

- [Consistency lanes](references/consistency/) for the targeted dimension.
- [Refactor and compile](references/refactor-and-compile.md) for document-wide find-replace and the post-edit build.

## Coupling to superRA workflows

**Standalone.** Finish with edits or findings and commit any authorized changes.

**Workflow.** Use `superplan` and [planning.md](references/planning.md) for whole-section drafts, whole-paper revisions, and response rounds. Use [long-form-review.md](references/long-form-review.md) for multi-lane, deep, full-paper, or pre-submission review. Load [integration.md](references/integration.md) during `superintegrate`.
