---
title: "Author the grilling mechanism and route superplan into it"
status: not-started
depends_on: []
---

## Objective

Add `skills/superplan/references/grilling.md` as the owner of the frontier-rounds question mechanism, and route the `superplan` spine into it.

The reference states, and nothing else in the repo restates:

- **Design tree and frontier.** Decisions branch into the decisions that hang off them. The frontier is every decision whose prerequisites are already settled; a question depending on one still open belongs to a later round.
- **The round asks the whole frontier.** Batch `AskUserQuestion` calls back to back until the frontier is empty rather than deferring questions to a later round for want of slots. Each question carries the recommended answer as its first option, labeled `(Recommended)`. A decision with no discrete alternatives rides the same round as plain numbered text.
- **Facts the environment holds are the agent's job** — read them, or dispatch exploration per `agent-orchestration/references/parallel-dispatch.md`. A running exploration is an unsettled prerequisite: it defers the questions downstream of it, not the round. A fact only the researcher holds, such as the venue or the research intent, is a question like any other.
- **A fact that only work can produce is a task boundary.** Split there per `task-tree-design.md` §Splitting Tasks, queue the dependents with `depends_on`, write them as deliberately open-ended, and re-enter grilling when the evidence lands.
- **Every settled decision lands in the tree** as an objective bullet, a scoped `### Context` / `### Constraints`, or `## Planner Guidance`, stated as current contract rather than as a "per user decision" note. No decision survives only in conversation.
- **Frontier empty ends the session** — go straight to Phase 3 decomposition, with no separate confirmation round.

`skills/superplan/SKILL.md` changes:

- §Substantive Questions becomes a slim §Grilling that routes to the reference and states the depth rule: default at standard and thorough, skipped at quick unless the researcher asks.
- Load conditions at §Entry Assessment, for a scoping round when the request is too vague to aim exploration, and at Phase 3 entry for the main round once the facts are in. Re-entry on a tree change routes through the same section.
- The frontmatter `description` carries the grill trigger phrases so a `grill me` request reaches `superplan` at any depth.
- The two internal citations of §Substantive Questions — the §Depth Tiers thorough row and [thorough-planning.md §Reconciliation](../../../skills/superplan/references/thorough-planning.md) — point at the new section.

Name `AskUserQuestion` as the rest of superRA names it, leaving Codex's equivalent to the harness adapter.

Validation: `grep -rn "Substantive Questions" skills/` returns no dangling citation; the reference passes the `CLAUDE.md` §Teach the Protocol three tests line by line; a dry run over an under-specified request produces at least two rounds where the second round's questions were genuinely unaskable in the first.

## Planner Guidance

- §Substantive Questions is the existing weak version of this concern — it names the standard ("present the options, don't assert one and narrate") but supplies no ordering, no question form, and no stopping rule. Rewriting it as the routing point is the intended landing; a new section beside it is the failure mode.
- The upstream question format is `❓ **Q1** — **<title>**: <body>` followed by `➡️ <recommended answer>`. Its load-bearing part is the recommended answer, which survives here as the `(Recommended)` first option; the glyphs are what the plain-text path can reuse.
- `references/` files sit one level deep with a stated load condition from `SKILL.md`, per `CLAUDE.md` §Skill Authoring Guidelines.
