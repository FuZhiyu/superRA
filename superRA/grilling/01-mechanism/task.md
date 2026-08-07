---
title: "Author the grilling mechanism and route superplan into it"
status: revise
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

## Results

The mechanism ships in [grilling.md](../../../skills/superplan/references/grilling.md), 34 lines under five headings: the design tree and frontier, the three facts rules, the round, and landing. `superplan/SKILL.md` grew 103 → 105 lines, so the spine held.

- **The round.** `AskUserQuestion` batched call after call until the frontier is empty, never holding a question back for want of slots; recommended answer first, labeled `(Recommended)`; a decision with no discrete alternatives rides the same round as plain numbered `❓`/`➡️` text; each question carries the survey finding that raises it.
- **Facts split three ways.** The environment's facts are the agent's to read or explore; the researcher's own facts are questions; a fact only work can produce is a task boundary, split with `depends_on` and open-ended dependents, re-grilled when the evidence lands.
- **Landing and stopping.** Settled decisions reach the tree as contract, and an empty frontier goes straight to decomposition with no confirmation round.
- **Routing.** [§Grilling](../../../skills/superplan/SKILL.md) replaces §Substantive Questions and carries the depth rule; §Entry Assessment runs a scoping round when the request is too vague to aim exploration; Phase 3 opens with "Grill before decomposing"; the frontmatter description now names grill, stress-test, and interrogate as triggers.

**Verification.** `grep -rn "Substantive Questions"` over `skills/` and `docs/site` is clean — the only surviving mentions are historical task records in `superRA/`. The §Depth Tiers thorough row and [thorough-planning.md §Reconciliation](../../../skills/superplan/references/thorough-planning.md) now cite §Grilling, and `test_superplan_routed_references_exist`'s existence assertion covers the new path.

`tests/harness-instruction-following/test_contract.py` has two failures that also fail on the parent commit: `test_superplan_routed_references_exist` asserts `references/decomposition.md`, renamed to `build-and-review.md` before this task, and `test_superimplement_executes_each_selected_seat_filler`. Neither involves grilling.

The `skill-creator` load that `CLAUDE.md` requires before editing a skill is unavailable in this environment — no such skill is installed. The edits were held to `CLAUDE.md` §Skill Prose Style and the §Teach the Protocol three tests instead, applied line by line: two rationale clauses were cut from the spine edits during self-review.

## Review Notes

Tier `quick`. Focus: `CLAUDE.md` §Teach the Protocol three tests and §Skill Prose Style, line by line over the new instruction prose.

1. `[BLOCKING]` **One exit for three entry points.** [grilling.md:34](../../../skills/superplan/references/grilling.md#L34) sends every empty frontier to Phase 3 decomposition, but [grilling.md:3](../../../skills/superplan/references/grilling.md#L3) declares three entry points. An agent that runs the §Entry Assessment scoping round and empties that frontier is told to decompose — skipping Phase 1 exploration and the Phase 2 domain hard gate, which [SKILL.md:52](../../../skills/superplan/SKILL.md#L52) makes a stop. Scope the exit to the caller: the main round's empty frontier goes to decomposition; a scoping round returns to §Entry Assessment, a re-entry round to the step that reopened scope.

2. `[BLOCKING]` **The retired mechanism still lives at §User Review.** [SKILL.md:91](../../../skills/superplan/SKILL.md#L91) — "surface open questions — design tradeoffs, unresolved ambiguities, choices that could reasonably go another way — as options, not assertions. No genuine questions: the presentation itself is the review" — is the §Substantive Questions standard this task replaced, restated in a second place (test 1). It also contradicts finding 1's neighbor rule, `**Frontier empty ends the session**`: grilling settles decisions before decomposition, so Phase 4 has no open questions to surface as options. Cut the question-surfacing clause and keep §User Review to presenting the tree, or point it at §Grilling.

3. `[BLOCKING]` **Re-entry routes nowhere.** [grilling.md:3](../../../skills/superplan/references/grilling.md#L3) claims a load "on any tree change that reopens scope", but no file a tree-changing agent reads points at §Grilling: [SKILL.md:105](../../../skills/superplan/SKILL.md#L105) routes to [changing-the-tree.md](../../../skills/superplan/references/changing-the-tree.md), whose protocol step 1 asks only for intent confirmation. The objective's "Re-entry on a tree change routes through the same section" needs the route stated where the agent stands — one line at [changing-the-tree.md:42](../../../skills/superplan/references/changing-the-tree.md#L42) or in §Grilling.

4. `[BLOCKING]` **"Ask the whole frontier, never truncate" is stated three times** across [grilling.md:21](../../../skills/superplan/references/grilling.md#L21) ("Ask the whole frontier in one round."), :23a ("batched call after call until the frontier is empty"), and :23b ("Never hold a question back for want of slots in a call.") — the objective states it once. L21 is the sentence announcing the list that §Skill Prose Style deletes; :23b is :23a's rejection test (test 2). Keep :23a alone.

5. `[ADVISORY]` **Frontier defined, then re-derived.** [grilling.md:9](../../../skills/superplan/references/grilling.md#L9) gives the inclusion rule ("every decision whose prerequisites are already settled") and then its rejection test ("A question depending on one still open belongs to a later round") — the pair test 2 names by example; the two sentences swap with nothing missing, and [grilling.md:28](../../../skills/superplan/references/grilling.md#L28) already carries deferral into the next round. Cut the second sentence.

6. `[ADVISORY]` **The landing menu paraphrases what it points at.** [grilling.md:32](../../../skills/superplan/references/grilling.md#L32) lists objective bullet / scoped `### Context` / `## Planner Guidance` in the same sentence that cites `task-tree-design.md` §Writing Objectives and Planner Guidance, which the planner has loaded by Phase 3 — a pointer, not a paraphrase (test 1). "git carries the date" is a rationale clause.

7. `[ADVISORY]` **Depth rule stated twice.** [SKILL.md:101](../../../skills/superplan/SKILL.md#L101): standard and thorough grill by default, so "A `grill me` request grills at any depth" bites only at quick, which "quick depth skips it unless the researcher asks" already covers.

8. `[ADVISORY]` **Narration before the imperative.** [grilling.md:28](../../../skills/superplan/references/grilling.md#L28) — "Answers settle decisions and push the frontier outward" derives what the §The design tree definition already implies; the instruction is "Recompute it and ask the next round."
