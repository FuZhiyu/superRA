---
title: "Author the grilling mechanism and route superplan into it"
status: approved
depends_on: []
---

## Objective

Add `skills/superplan/references/grilling.md` as the owner of the frontier-rounds question mechanism, and route the `superplan` spine into it.

The reference states, and nothing else in the repo restates:

- **Design tree and frontier.** Decisions branch into the decisions that hang off them. The frontier is every decision whose prerequisites are already settled.
- **The round asks the whole frontier.** Batch `AskUserQuestion` calls back to back until the frontier is empty. Each question carries the recommended answer as its first option, labeled `(Recommended)`. A decision with no discrete alternatives rides the same round as plain numbered text.
- **Facts the environment holds are the agent's job** — read them, or dispatch exploration per `agent-orchestration/references/parallel-dispatch.md`. A running exploration is an unsettled prerequisite: it defers the questions downstream of it, not the round. A fact only the researcher holds, such as the venue or the research intent, is a question like any other.
- **A fact that only work can produce is a task boundary.** Split there per `task-tree-design.md` §Splitting Tasks, queue the dependents with `depends_on`, write them as deliberately open-ended, and re-enter grilling when the evidence lands.
- **Every settled decision lands in the tree as contract**, per `task-tree-design.md` §Writing Objectives and Details. No decision survives only in conversation.
- **An empty frontier ends the round** and returns to the step that entered it, with no separate confirmation round.

`skills/superplan/SKILL.md` changes:

- §Substantive Questions becomes a slim §Grilling that routes to the reference and states the depth rule: default at standard and thorough, skipped at quick unless the researcher asks.
- Load conditions at §Entry Assessment, for a scoping round when the request is too vague to aim exploration, and at Phase 3 entry for the main round once the facts are in. Re-entry on a tree change routes through the same section, stated where the tree-changing agent stands.
- §User Review keeps to presenting the tree. Question-surfacing belongs to §Grilling, so no second copy of the standard survives at Phase 4.
- The frontmatter `description` carries the grill trigger phrases so a `grill me` request reaches `superplan` at any depth.
- The two internal citations of §Substantive Questions — the §Depth Tiers thorough row and [thorough-planning.md §Reconciliation](../../../skills/superplan/references/thorough-planning.md) — point at the new section.

Name `AskUserQuestion` as the rest of superRA names it, leaving Codex's equivalent to the harness adapter.

Validation: `grep -rn "Substantive Questions" skills/` returns no dangling citation; the reference passes the `CLAUDE.md` §Teach the Protocol three tests line by line; a dry run over an under-specified request produces at least two rounds where the second round's questions were genuinely unaskable in the first.

## Details

- §Substantive Questions is the existing weak version of this concern — it names the standard ("present the options, don't assert one and narrate") but supplies no ordering, no question form, and no stopping rule. Rewriting it as the routing point is the intended landing; a new section beside it is the failure mode.
- The upstream question format is `❓ **Q1** — **<title>**: <body>` followed by `➡️ <recommended answer>`. Its load-bearing part is the recommended answer, which survives here as the `(Recommended)` first option; the glyphs are what the plain-text path can reuse.
- `references/` files sit one level deep with a stated load condition from `SKILL.md`, per `CLAUDE.md` §Skill Authoring Guidelines.

## Results

The mechanism ships in [grilling.md](../../../skills/superplan/references/grilling.md), 32 lines under four headings: the design tree and frontier, the three facts rules, the round, and landing. `superplan/SKILL.md` sits at 105 lines, so the spine held.

- **The round.** `AskUserQuestion` batched call after call until the frontier is empty; recommended answer first, labeled `(Recommended)`; a decision with no discrete alternatives rides the same round as plain numbered `❓`/`➡️` text; each question carries the survey finding that raises it.
- **Facts split three ways.** The environment's facts are the agent's to read or explore; the researcher's own facts are questions; a fact only work can produce is a task boundary, split with `depends_on` and open-ended dependents, re-grilled when the evidence lands.
- **Landing and stopping.** Settled decisions reach the tree as contract. An empty frontier ends the round and returns to whichever step entered it — the Phase 3 round to decomposition, a scoping round to §Entry Assessment, a re-entry round to the change that reopened scope — with no confirmation round.
- **Routing.** [§Grilling](../../../skills/superplan/SKILL.md) replaces §Substantive Questions and carries the depth rule; §Entry Assessment runs a scoping round when the request is too vague to aim exploration; Phase 3 opens with "Grill before decomposing"; [changing-the-tree.md](../../../skills/superplan/references/changing-the-tree.md) step 1 routes unsettled decisions into it; §User Review now only presents the tree; the frontmatter description names grill, stress-test, and interrogate as triggers.

**Verification.** `grep -rn "Substantive Questions"` over `skills/` and `docs/` is clean — the only surviving mentions are historical task records in `superRA/`. The §Depth Tiers thorough row and [thorough-planning.md §Reconciliation](../../../skills/superplan/references/thorough-planning.md) now cite §Grilling, and `test_superplan_routed_references_exist`'s existence assertion covers the new path.

**Review.** One quick pass at tier `quick`, focused on the `CLAUDE.md` §Teach the Protocol tests, returned REVISE with four blocking findings; all four were accepted and fixed, along with all four advisories. The load-bearing one was a behavior conflict: the first draft sent every empty frontier to Phase 3, so a scoping round entered at §Entry Assessment would have skipped exploration and the Phase 2 domain gate. The rest were single-source violations — §User Review still carrying the retired standard, the re-entry route stated only in the reference and not where the tree-changing agent stands, and the whole-frontier rule stated three times. The reference came out 2 lines shorter, with four restated clauses gone.

`tests/harness-instruction-following/test_contract.py` has two failures that also fail on the parent commit: `test_superplan_routed_references_exist` asserts `references/decomposition.md`, renamed to `build-and-review.md` before this task, and `test_superimplement_executes_each_selected_seat_filler`. Neither involves grilling.

The `skill-creator` load that `CLAUDE.md` requires before editing a skill is unavailable in this environment — no such skill is installed. The edits were held to `CLAUDE.md` §Skill Prose Style and the §Teach the Protocol three tests instead, applied line by line: two rationale clauses were cut from the spine edits during self-review.
