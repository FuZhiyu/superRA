---
title: "refactor-and-integrate"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

A single-shot agent gets the analysis right and the codebase wrong. It re-implements a winsorizer you already keep in `utils/`, names the new variable `ret_w` while every other file uses `ret_winsor`, leaves the old approach commented out two functions up, and edits a `README.md` that now describes an output the code no longer produces. The whole thing lands as one sprawling diff — reformatted imports, a renamed-for-no-reason helper, three speculative abstractions "for later" — mixed in with the four lines that do the work. You either spend an afternoon untangling it by hand or merge it and let the cruft become permanent.

This skill reworks a correct-but-rough branch so it fits the project and lands as a diff a reviewer can read. Four mechanisms do the work.

**Minimum net diff** is the central gate. It computes the governing diff against the baseline — `git diff <base>..HEAD` — and walks every surviving hunk line by line. Each hunk has to tie back to something concrete: an approved task objective, a convention or checklist fix, a logged user decision, or supplied Sync-impact evidence. Hunks that do not — unrelated reformatting, defensive edits, "while I was in here" abstractions, helper extraction nobody asked for — get reverted. What survives is the change and nothing else.

**Convention fit and helper reuse** are the `[BLOCKING]` checks that make new code read like the rest of the project: names follow the codebase's naming, an existing utility is called instead of hand-rolled, no debug prints or commented-out experiments survive, and edits to files outside the task scope stay minimal. The winsorizer gets called, not rewritten; `ret_w` becomes `ret_winsor`.

**The Project Doc Audit** handles stale docs. For every file the diff touches it walks up from that file's directory to the repo root, collecting each `CLAUDE.md` / `AGENTS.md` / `README.md` along the way plus the repo-root pair, then fixes claims the diff contradicts, adds genuinely new patterns at the nearest level, and creates a `CLAUDE.md` + `AGENTS.md` pair for any new module directory. This is what stops a README from advertising an output your code no longer produces. Docs above the change area are left alone unless they are stale.

**The Final Diff Self-Check** is the trail it leaves before returning. It recomputes the governing range, summarizes the ordinary hunks by class ("utility reuse in scripts", "README currency"), and justifies suspicious ones by file and line — edits to `skills/*` or `agents/*`, base-side restorations, broad rewrites, anything justified only by Sync impact. The trail goes in the task's `## Results` when there is one, otherwise in the status return. A no-change result still leaves the trail; under `superintegrate` the integration reviewer recomputes the same range and a missing or stale trail is blocking even when no code changed.

One boundary worth knowing: it does not resolve methodological questions. Different control sets, variable definitions, sample filters, or normalization choices are research decisions, and it escalates those to you rather than picking one. It prunes form, not method.

Inside the superRA workflow it runs automatically at the `superintegrate` Integrate step, after the base sync, against the post-sync baseline. Standalone, point it at a rough branch and name the range to prune against:

`load refactor-and-integrate, then prune this branch to minimum net diff against main and make it codebase-coherent before I open the PR`

`load refactor-and-integrate: this branch works but it's a mess — reuse our existing helpers, match naming conventions, and run the Project Doc Audit on everything the diff touches`

`load refactor-and-integrate and run the Final Diff Self-Check against origin/main..HEAD; tell me which hunks aren't justified by the task`

When task files carry a `**Sync impact:**` field, it uses that as evidence for why a post-sync hunk already exists — to justify hunks, never to invent new refactor targets.

Reach for it when single-shot output is correct but does not match the surrounding code, before a branch goes up for review. The full gate list, checklist, and self-check format live in [`refactor-and-integrate`](skills/refactor-and-integrate/SKILL.md).
