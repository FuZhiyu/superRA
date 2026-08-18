---
title: "Repo Sweep: Restyle Remaining Skill Prose to the Terse Style"
status: approved
depends_on: []
---

## Objective

Every instruction file under skills/ matches the terse style at implement-task / review-task density. Behavior-preserving restyle only: protocol content, gates, and ordering constraints survive verbatim in meaning. Done so far: implement-task and using-superra (2e1fbdaa), review-task (f525b63e), superintegrate mature-consolidate.md (35832fe7), using-superra task-companion-files.md (f46265a5). Remaining: workflow skills, stage references, domain and utility skills.

## Details

Per file: apply the CLAUDE.md DRY/Necessity gate first (delete lines that fail), then compress to the style (CLAUDE.md §Skill Prose Style). The daea6ae3 failure mode is the check: if the word count barely moves, the pass cut connectives, not clauses.

## Results

80 files restyled across five groups plus the two-file spec test, cutting prose from 61,638 words to 53,551 — **13% overall**, ranging from 10% to 17% per group. Every remaining `.md` under `skills/` is explicitly out of scope: the two contributor `CLAUDE.md` files, the hand-managed [vendor README](../../../../skills/task-tree/scripts/vendor/README.md), and the deprecated `handoff-doc` redirect stubs, which are two lines each and already at the style.

**Behavior was preserved, and it was checked rather than assumed.** `tests/harness-instruction-following` passed 126/126 at every group. Every gate, `[BLOCKING]`/`[ADVISORY]` item, status enum, commit-subject grammar, dispatch template, code block, and inventory table survived intact apart from the DRY deletions each group's commit records. For the reference-heavy group the check was mechanical: all fenced blocks were extracted from `HEAD` and from the working tree and the sets diffed — 37 of 44 byte-identical, 6 deleted as duplicate examples, one re-indented with content unchanged.

**Three REVISE rounds found four classes of loss**, which are what the density target costs unreviewed:

1. A DRY deletion resting on a premise false on this branch — `main-agent.md §Workflow Map` was the last agent-loaded copy of the phase model, not a duplicate.
2. Protocol facts dropped as if they were wording — the dispatched-sync commit verb in `sync.md`, the "existing" qualifier on protection mechanisms in `protect.md`.
3. Decision-carrying hedges cut as filler — the drift-test failure-attribution rule, which unqualified would have collapsed a three-way classification.
4. Unverified factual claims written into `## Results`, including a false `load_contract.json` anchor claim.

Group 1 showed the compression failure mode directly: two edits removed the imperative verb instead of the clause around it, leaving a section body with no instruction. Group 4's three findings were the same shapes — a dropped "only" that inverted an advisory, a live citation lost alongside a dangling one, two miscounts in `## Results` — and were fixed in the Group 5 commit. The rule the rounds settled, now in [CLAUDE.md §Skill Prose Style](../../../../CLAUDE.md): a hedge that carries a decision branch is protocol content, not filler.

**The spec test came first and validated the spec.** A main agent applying the fresh style cut [superplan/SKILL.md](../../../../skills/superplan/SKILL.md) 1047 → 756 words and its decomposition reference 708 → 539, with every phase gate, the tier table, the dispatch template, and all self-review items surviving.

Counts are prose only — fenced blocks and tables excluded — because several swept files are mostly dispatch templates and shell snippets that must survive verbatim; whole-file counts understate the cut by up to 10 points. Per-file counts and the deletion-by-deletion record are in the group commits.
