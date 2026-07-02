---
title: "refactor-and-integrate"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

A single-shot agent gets the analysis right and the codebase wrong: it re-implements a helper you already keep in `utils/`, names a variable `ret_w` where the rest of the code uses `ret_winsor`, leaves a `README.md` describing an output the code no longer produces, and buries the four working lines in one sprawling diff full of reformatting and speculative abstractions. You either untangle it by hand or merge the cruft.

Ask the agent to rework a correct-but-rough branch so it fits the project and lands as a diff a reviewer can read:

`prune this branch to minimum net diff against main and make it codebase-coherent before I open the PR`

`this branch works but it's a mess — reuse our existing helpers, match naming conventions, and fix any docs the diff contradicts`

The core move is **minimum net diff**: it walks the governing diff (`git diff <base>..HEAD`) hunk by hunk and reverts anything not tied to an approved objective, a convention fix, a logged decision, or supplied Sync-impact evidence. Reused helpers, matched names, and a doc audit that walks up from each touched file to the repo root keep new code reading like the rest. It prunes form, not method — different control sets, sample filters, or normalization choices are research decisions, so it escalates those to you.

Inside superRA it runs automatically at the `superintegrate` Integrate step. The full gate list, checklist, doc-audit walk-up, and Final Diff Self-Check format live in [`refactor-and-integrate`](skills/refactor-and-integrate/SKILL.md).
