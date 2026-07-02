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

The **minimum net diff** is the smallest set of surviving hunks in the governing diff that achieves the task objective. Everything below works toward it.

## Fit the host project

Before keeping a change, read its neighbors — the surrounding functions and sibling files in code, the adjacent sections and paragraphs in a document. Find how the host already names the concept you are touching, which utilities or shared definitions already exist, which patterns it follows. Then match them, so a reader cannot tell your work from what was already there:

- name things the way the surrounding work already names the same concept;
- reuse an existing utility or definition instead of rolling your own;
- follow the local pattern for the same kind of work.

An intentional deviation is fine when the local convention does not fit, but it carries a one-line reason at the deviation site so the next reader knows it was a choice, not an oversight.

## Triage every hunk

Walk the governing diff hunk by hunk. Every hunk must earn its place by contributing to the task objective; a hunk that does not is pruned. Never silently delete — when you are unsure, keep the hunk and raise it.

Three outcomes, by what justifies the hunk:

- **Confident junk → revert.** Debug prints, reformatting, speculative abstraction, a dead helper — reverting loses no real work.
- **Justified → keep it.** A kept hunk traces to one of the documented sources: an approved task objective, the codebase-coherence checklist below, task-file coherence, docs matching the code, a logged user decision, or supplied Sync impact context.
- **Scope-ambiguous but plausibly load-bearing → keep and raise it.** A hunk you cannot confidently tie to a source yet that looks load-bearing stays in, and you flag it — never revert on your own authority. A hunk genuinely needed but covered by no source is evidence the task tree is stale; route that to `superplan §User Feedback and Changing the Task Tree`.

The same warrant gates base-current deletions and relocations: restore or move base code only when one of the sources above requires it.

## Consolidate for maintainability

Minimum net diff is not only deletion. Look across the surviving changes and ask whether the same objective reaches a simpler, more host-consistent shape. Train the eye on concrete cues:

- a procedure or passage repeated across the work → state it once (extract a helper; consolidate the duplicated text);
- a near-duplicate of an existing module, dataset, or section → extend it minimally rather than fork a parallel copy;
- nested conditionals that can flatten → flatten them;
- comments or prose that restate what is already plain → cut them.

Keep abstractions that aid clarity; clarity over brevity. Two guardrails, because the obvious "safe" reading of each is wrong for research integration:

- **Target the net-minimum diff, not the files you happened to touch.** The smallest change that leaves the codebase consistent often means reaching into existing shared code to extend a utility minimally, rather than leaving it untouched and duplicating its logic alongside. The minimal extension *is* the net-min-diff move; "only refine code you already touched" is not the boundary.
- **The drift suite is the behavior guardrail.** Consolidating toward host conventions can shift a protected result slightly; that is acceptable while the drift tests pass. When a consistency or consolidation fix *does* move a protected result, treat it as a signal to investigate — the inconsistency may have been producing the wrong number — and adjudicate it per the drift-test discipline the workflow runs around Integrate. Never silently revert to preserve the old output, and never silently re-expect the new one.

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

When a task file carries a `## Sync Impact` section, use it as self-contained evidence for why a hunk already exists in the governing diff. Sync impact justifies existing hunks; it does not create new refactor targets or excuse unrelated codebase changes.

## Final Diff Self-Check

Implementers run this immediately before every return or commit, including no-change cases:

1. **Recompute the governing diff** using the range from §Establish the baseline first.
2. **Leave a compact trail.** In the assigned task's `## Results` when one exists, write or refresh `**Final diff self-check:** <command/range>; <no surviving hunks OR surviving-change classes>; <suspicious hunk justifications or none>`. Without a task file, put the same line in the status return.
3. **Summarize ordinary hunks by class.** Examples: "utility reuse in task scripts", "module README currency", "test contract wording". Do not justify every line when the class is already covered by the task objective or checklist.
4. **Justify suspicious hunks by file and line/hunk.** Suspicious cases are: `skills/*` or `agents/*` instruction edits, prior overprescription or scope-creep findings, base-side restorations or relocations, touched tasks already marked `status: approved`, broad formatting or rewrite hunks, and changes justified only by Sync impact. Apply any local instruction-prose gate only to files that local guidance covers.
5. **Triage** per §Triage every hunk: confident junk reverted, justified hunks kept, scope-ambiguous but load-bearing hunks kept and raised (as a `## Review Notes` item when a task file exists, else in the status return).
6. **Respect the dispatch scope.** Refactor implementer and integration reviewer act on the reopened or changed tasks in the dispatch, plus any `approved` task the branch-wide surviving-diff sweep reopens when it surfaces an unjustified hunk touching that task.

The integration reviewer recomputes the same governing diff and compares it with the self-check trail. A missing or stale trail is `[BLOCKING]`, including when no code changed.

## Checklist

Walk every item. `[BLOCKING]` items must be satisfied for APPROVE; `[ADVISORY]` items may be flagged as MINOR. The method lives in the sections above; these items are the pass/fail points, not a restatement.

**Code integration:**

- `[BLOCKING]` **Final Diff Self-Check present and fresh** per §Final Diff Self-Check.
- `[BLOCKING]` **Triage performed hunk by hunk** per §Triage every hunk: every surviving hunk ties to a justification source, and no hunk was silently deleted.
- `[BLOCKING]` **Base-current deletions / relocations honored by default:** base code is restored or moved only when a justification source requires it.
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
