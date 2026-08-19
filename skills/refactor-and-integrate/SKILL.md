---
name: refactor-and-integrate
description: Codebase integration discipline. Use when refactoring for local conventions, reviewing post-sync quality, auditing project docs, pruning diffs, or using Sync Impact evidence.
---

# Refactor and Integrate

A human has to read, trust, and maintain this work after you leave — code, but also prose, notes, or slides. Every technique here serves that human through two concrete ends:

1. **Consistency** — the result reads as if one author produced the whole project. New work follows the host's existing conventions (names, utilities, and patterns in code; terminology, notation, and structure in prose), so a reader cannot tell it from what was already there.
2. **Minimum reviewable diff** — the surviving change is the smallest one that achieves the task. A reviewer reads only what the task needed, with no incidental noise to wade through.

Hold both ends in mind when you hit a change no rule below anticipated: keep what reads as one author's work and serves the task, prune what does not, and raise what you cannot judge.

Load whichever domain skill(s) the work actually touches; each routes its own domain-specific integration reference at the `integration` stage.

---

## Establish the baseline first

Before triaging anything, fix the governing diff — the playing field for every decision below. It is the set of changes made on *this branch* since it diverged from the base: `git diff BASE...HEAD` (three-dot), equivalently `git diff $(git merge-base BASE HEAD)..HEAD`. When a dispatch hands you an explicit range, use that range.

The **minimum net diff** is the smallest set of surviving hunks that supports the protected record when one exists, or achieves the task objective in standalone use. Everything below works toward it.

## Apply the reviewed refactoring task

When the dispatch supplies a researcher-reviewed temporary refactoring task, execute its objective against the linked permanent documentation, result files, and mature task results. Those artifacts define the protected record; their documented reproduction, validation, interpretation, and presentation paths justify supporting carriers.

The reviewed task is the action boundary. Apply its pruning and other refactoring mechanically. If new evidence requires a materially different protected outcome or refactoring action, return to the owning workflow gate so the record and task can be revised before that work runs.

## Fit the host project

Before keeping a change, read its neighbors — the surrounding functions and sibling files in code, the adjacent sections and paragraphs in a document. Find how the host already names the concept you are touching, which utilities or shared definitions already exist, which patterns it follows. Then match them, so a reader cannot tell your work from what was already there:

- name things the way the surrounding work already names the same concept;
- reuse an existing utility or definition instead of rolling your own;
- follow the local pattern for the same kind of work.

An intentional deviation is fine when the local convention does not fit, but it carries a one-line reason at the deviation site so the next reader knows it was a choice, not an oversight.

## Triage every hunk

Walk the governing diff hunk by hunk.

**With a protected record:** only a result shown in the permanent documentation, result files, or mature task results—or a reproduction, validation, interpretation, or presentation path explicitly documented there—excludes an in-scope hunk from the automatic pruning list. Before researcher approval, put every unmatched hunk in the temporary task as a pruning action. Task objectives, checklist items, task-file coherence, matching documentation, logged decisions, and Sync Impact may explain the hunk or shape its proposed action; they do not exempt it. After approval, execute that task and return to the researcher gate before materially changing its actions.

**Standalone:** confident junk is reverted; a hunk justified by the objective, checklist, task-file coherence, matching documentation, a logged decision, or Sync Impact is kept; a scope-ambiguous but plausibly load-bearing hunk is kept and raised.

The same mode-specific boundary gates base-current deletions and relocations.

## Consolidate for maintainability

Minimum net diff is not only deletion. Look across the surviving changes and ask whether the same objective reaches a simpler, more host-consistent shape. Train the eye on concrete cues:

- a procedure or passage repeated across the work → state it once (extract a helper; consolidate the duplicated text);
- a near-duplicate of an existing module, dataset, or section → extend it minimally rather than fork a parallel copy;
- nested conditionals that can flatten → flatten them;
- comments or prose that restate what is already plain → cut them.

Keep abstractions that aid clarity; clarity over brevity. Two guardrails, because the obvious "safe" reading of each is wrong for research integration:

- **Target the net-minimum diff, not the files you happened to touch.** The smallest change that leaves the codebase consistent often means reaching into existing shared code to extend a utility minimally, rather than leaving it untouched and duplicating its logic alongside. The minimal extension *is* the net-min-diff move; "only refine code you already touched" is not the boundary.
- **The selected protection is the behavior guardrail.** A refactor must preserve the permanent record and pass every automated mechanism selected at Protect. Investigate any movement rather than silently revising documentation or test expectations.

This is the domain-agnostic eye. Domain-specific consolidation rules (redundant intermediary datasets, variable-construction consistency, and the like) live in the domain `integration.md` references; load the domain skill for those.

## Project Doc Audit

Integrate-step refactoring and integration review both cover project-level docs reachable from the diff.

For every file in the governing diff, walk up from its directory to the repo root and collect every `CLAUDE.md` / `AGENTS.md` / `README.md` encountered. Always also check the repo-root `README.md` and root `CLAUDE.md`.

For each doc in the set:

- update stale claims contradicted by the diff;
- add new patterns at the nearest appropriate level;
- link rather than duplicate parent-level content;
- create a missing `CLAUDE.md` + relative `AGENTS.md -> CLAUDE.md` pair for new module directories.

Leave docs above the affected area alone unless they are stale.

## Sync Impact Context

In standalone use, a task-local `## Sync Impact` section can justify an existing hunk; it does not create new refactor targets or excuse unrelated codebase changes.

## Final Diff Self-Check

Implementers run this immediately before every return or commit, including no-change cases:

1. **Recompute the governing diff** using the range from §Establish the baseline first.
2. **Leave a compact trail.** In the assigned task's `## Results` when one exists, write or refresh `**Final diff self-check:** <command/range>; <protected record or standalone objective>; <removed and surviving change classes>; <suspicious hunk justifications or none>`. Without a task file, put the same line in the status return.
3. **Summarize ordinary hunks by class.** Examples: "utility reuse in task scripts", "module README currency", "test contract wording". Do not justify every line when the class is already covered by the task objective or checklist.
4. **Justify suspicious hunks by file and line/hunk.** Suspicious cases are: `skills/*` or `agents/*` instruction edits, prior overprescription or scope-creep findings, base-side restorations or relocations, touched tasks already marked `status: approved`, broad formatting or rewrite hunks, and changes justified only by Sync impact. Apply any local instruction-prose gate only to files that local guidance covers.
5. **Triage** per §Triage every hunk: with a protected record, every survivor traces to that record or an explicit support path and every unmatched hunk appears in the approved pruning actions; standalone work records kept, reverted, and raised classes.
6. **Respect the dispatch scope.** Refactor implementer and integration reviewer act on the reopened or changed tasks in the dispatch, plus any `approved` task the branch-wide surviving-diff sweep reopens when it surfaces an unjustified hunk touching that task.

The integration reviewer recomputes the same governing diff and compares it with the self-check trail. A missing or stale trail is `[BLOCKING]`, including when no code changed.

## Checklist

Walk every item. `[BLOCKING]` items must be satisfied for APPROVE; `[ADVISORY]` items may be flagged as MINOR. The method lives in the sections above; these items are the pass/fail points, not a restatement.

**Code integration:**

- `[BLOCKING]` **Final Diff Self-Check present and fresh** per §Final Diff Self-Check.
- `[BLOCKING]` **Reviewed refactoring task honored when supplied:** every proposed action was executed or returned to the researcher gate before the proposal changed.
- `[BLOCKING]` **Protected record preserved:** permanent documentation, mature task results, and their required support paths remain coherent and reproducible.
- `[BLOCKING]` **Triage performed hunk by hunk** per §Triage every hunk: protected-record survivors trace only to the record or an explicit support path, every unmatched hunk entered the approved pruning actions, and no hunk was silently deleted.
- `[BLOCKING]` **Base-current deletions / relocations honor the active boundary:** protected-record workflows use only the record or an explicit support path; standalone work uses its justification sources.
- `[BLOCKING]` **Host-project fit** per §Fit the host project: names, utility reuse, and patterns match the host; deviations carry a reason.
- `[BLOCKING]` **No debug artifacts:** no leftover debug prints, commented-out experiments, or temporary variables.
- `[ADVISORY]` **Consolidation** per §Consolidate for maintainability, where the task or codebase-coherence review demanded the touch.
- `[ADVISORY]` **PR-friendly diffs:** avoid unnecessary reformatting that obscures substantive changes.

**Handling inconsistencies:**

- `[BLOCKING]` **Methodological questions escalated, not resolved.** Different control variable sets, variable definitions, sample filters, equilibrium concepts, or normalization choices are research decisions.
- `[ADVISORY]` **Clear convention exists:** follow it. **Ambiguous or conflicting conventions:** use judgment and document the choice.

**PR quality:**

- `[BLOCKING]` **Focused diff:** changes are limited to task scope.
- `[BLOCKING]` **Self-contained:** the work can be understood from the code and documentation.
- `[ADVISORY]` **Clean commits:** commit history is logical and messages are descriptive.

**Docs match the code:**

- `[BLOCKING]` Module `CLAUDE.md` / `AGENTS.md` / `README.md` files do not reference files, functions, outputs, or methodology that no longer exist or have been superseded.
- `[BLOCKING]` Every output file mentioned in documentation is produced by the current code.
- `[BLOCKING]` Dates and version claims reflect the current commit.

**Project Doc Audit:**

- `[BLOCKING]` The §Project Doc Audit walk-up was executed for every file in the governing diff, applying all four rules listed there.
