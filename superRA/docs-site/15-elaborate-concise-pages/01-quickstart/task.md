---
title: "Quickstart: Polish the Reordered Narrative and Resolve Inline Markers"
status: approved
depends_on: []
tags: []
created: 2026-06-18
---

## Objective

**Second pass (depth).** Re-read this page against the parent's [Revision standard](../task.md) and the worktree-data-sync reference (`git show db54356c`). The quickstart is a narrative, not a mechanism page, so apply the bar selectively: where the walkthrough names a concept or step a brand-new adopter would not follow (what `superra` triggers, what a milestone/dashboard pill is showing, why a separate branch), explain it plainly; where the prose is already clean (it passed first-pass review), leave it — do not pad the narrative to hit a depth quota. If you judge no real adopter gap remains, say so and supersede `## Results` with that finding rather than inventing elaboration.

Resolve the researcher's markers on [docs/site/02-quickstart/task.md](../../../../docs/site/02-quickstart/task.md) and smooth the prose the condensing/reordering left rough. The running-example description (CAPM vs FF3 on the 25 size-B/M portfolios, then the GRS test) was moved into the "A typical workflow" section; make sure that framing still reads coherently after the move.

Marker-by-marker:

- **`<!-- polish. -->`** on the new paragraph: *"During implementation, agents make atomic commits by default. In this way we ensure every meaningful change is tracked. To avoid overload the main branch hence we recommend working in a separate branch."* Rewrite into clean docs prose conveying two things — agents commit atomically so every meaningful change is tracked in history, and because that produces many commits you are advised to work on a separate branch rather than directly on the shared base. Keep it adopter-level.
- **Milestone ordering.** The mid-implement export link (`[Open the study mid-implement →]`) now sits *before* the paragraph that introduces it, unlike the after-planning and finished milestones where the paragraph leads and the link follows. Reorder so each export link is introduced by its explanatory paragraph, matching the other two milestones.
- **`<!-- ummm they should not live in read me. -->`** after the sentence pointing at the project README for the full install reference. Resolve the marker by cleaning the pointer prose. Whether the install reference should physically move out of the README is a separate docs-architecture question, not part of this prose pass — leave the README structure as is and do not relocate install docs here. (The orchestrator is raising that question with the researcher separately; do not block on it.)
- **Rollup-count consistency.** The WIP removed the "rollup reading 0 of 3" and "reads 3 of 3" phrasings from the dashboard milestones. Confirm the remaining status-pill descriptions read consistently without those counts; do not reintroduce them.

Success: every marker removed, prose clean and consistent with the page's voice, the milestone links each introduced by their paragraph, page passes the inherited agent-first / no-AI-prose gates.

## Planner Guidance

Atomic-commit and branch-workflow framing is owned by `superimplement` / the workflow pages — keep the quickstart's mention short and link-deep rather than re-explaining. Source for the install pointer is [README.md](../../../../README.md).

## Results

**Second pass (depth).** Re-read the page against the parent's [Revision standard](../task.md) and the worktree-data-sync reference (`db54356c`). The first pass had already resolved all four markers (none remain — grep clean) and the orchestrator had corrected the install-pointer claim, so the prose was clean. Applying the depth bar selectively — this is a narrative, not a mechanism page — one real adopter gap remained, and I closed it; the rest I left alone.

- **Gap closed — undefined "rollup."** The dashboard milestones used "the parent rollup" ([docs/site/02-quickstart/task.md:67](../../../../docs/site/02-quickstart/task.md#L67)) and "the parent has rolled up to `in-progress`" (line 102) without ever defining the term. The quickstart is the day-one page; a brand-new adopter meets "rollup" here long before the [status-and-frontier page](../../../../docs/site/04-utility-skills/01-task-tree/03-status-and-frontier/task.md) that owns the full algorithm. Per the bar (define a term that would stop a non-expert at first use, plainly, leading with what the reader sees), I gave it a one-clause gloss at line 67: a parent's pill is "not set by hand — it is **rolled up** from its children, so the root reflects the state of the whole subtree under it and you can read overall progress off the top of the tree," and tied the freshly-planned screenshot to it ("the root rolls up to `not-started` too"). Line 102's "rolled up to `in-progress`" now reads naturally. Kept to one clause plus the concrete tie-in; the exact rollup algorithm stays owned by the status-and-frontier page the quickstart already links to, so this adds the concept the reader needs without re-narrating the mechanism.
- **Left alone deliberately.** The rest of the page passed first-pass review and reads cleanly for an adopter at the narrative level: the `superra` trigger, the implementer–reviewer pair / APPROVE-REVISE verdicts, the status colors (grey/yellow/green, each tagged inline at first use), the dependency-graph and Kanban views (each explained inline), the five integrate stages (each a one-line gloss), and the "next ready task whose dependencies are satisfied" framing of the frontier all define their concepts where they appear. I did not pad these toward a depth quota; the bar explicitly does not loosen the non-obvious-only gate.

Page is a Markdown doc (no compile step); `check_markdown.py` reports clean. Prose still passes the agent-first / no-AI-prose gates: the added sentence is plain, verb-led, no hype or AI tics.

## Review Notes

1. **MAJOR** — install-pointer accuracy. [docs/site/02-quickstart/task.md:30](../../../../docs/site/02-quickstart/task.md#L30) claims "The full install reference — updating and the local-clone path for forking — lives in the project README." Checked against [README.md](../../../../README.md): the README's Installation section carries the **update** steps ([README.md:78-82](../../../../README.md#L78-L82)) ✓, but the **local-clone path for forking** does *not* live in the README — [README.md:85](../../../../README.md#L85) only redirects it ("For Codex setup and a local-clone install (to track or modify superRA itself), see `docs/README.codex.md`"). The actual local-clone steps live in `docs/README.codex.md`, not the README. So the pointer makes a false location claim, and the `## Results` assertion "verified the README actually carries … the local-clone/fork path the pointer claims, so the pointer is accurate" is wrong. Fix the pointer prose so the claim is true — e.g. attribute updating to the README and the local-clone/fork path to the Codex notes, or phrase the pointer so it does not assert the README itself carries the local-clone instructions. This is prose-cleaning, in scope; do not relocate any docs. The marker the researcher placed here ("they should not live in read me") was flagging exactly this mismatch.
   → resolved (orchestrator): finding confirmed against README.md:85. Pointer rewritten to attribute updating to the README and the local-clone/fork path to the Codex install notes; the false Results claim corrected. One-line prose fix verified inline, re-review skipped.

The other three marker items check out and need no change: markers all removed (grep clean); all three milestones now read paragraph-then-link in chronological order; rollup-count phrasings confirmed absent and the status-pill descriptions read consistently on color alone; the atomic-commit rewrite is clean, grounded in the implementer spec, and link-deep.
