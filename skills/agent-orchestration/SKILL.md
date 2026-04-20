---
name: agent-orchestration
description: Use when dispatching multiple agents and unsure how to size or parallelize the work; when tasks are independent vs iterative and the right dispatch pattern is not obvious; when choosing implementer + reviewer roles for a multi-step workflow; when adjudicating reviewer feedback as orchestrator. Triggers include "dispatch N agents", "run these in parallel", "who should do the review", a multi-step workflow that needs coordination across roles, or a session handoff where workflow state must survive. Usable in any phase of the superRA workflow (PLAN / IMPLEMENT / VALIDATE / INTEGRATE).
---

# Agent Orchestration

## Overview

You delegate tasks to specialized agents with isolated context. This skill carries the **high-level orchestrator guidance** — when to dispatch, what dispatch shape to use, how to read the resulting state from `PLAN.md`, and how to adjudicate reviewer feedback.

**Core principle:** parallel-dispatch independent tasks; serialize iterative
loops; do trivial work inline. See §Workload Balancing for how to size each
dispatch.

## Workload Balancing

Every dispatch has spawn cost — skill-load, context hydration, per-turn
overhead. Treating every sub-task as dispatch-worthy wastes tokens and
serializes work that could run inline; treating every bundle as "split
it up" over-spawns. Pick the tier that matches the work:

### Tier 1 — Trivial: do it inline

The orchestrator executes the task itself, no subagent. Use when the
task fits in a single edit, reads no unfamiliar files, and needs no
domain skill beyond what the orchestrator already has loaded.

- Typo or comment fix in one file.
- A 2-line constant change the orchestrator has already read.
- Removing a known-dead import.

Dispatch cost > work content. Just do it.

### Tier 2 — Slightly involved: bundle and delegate

Group multiple small-to-medium tasks that share context (same file, same
skill load, same domain references) into one dispatch. One agent does the
whole bundle in a single turn.

- Three edits in the same skill file.
- A reviewer sweep over two sibling agent files.
- Updating a template plus its one consumer.

The agent pays the spawn cost once and amortizes it across the bundle.

### Tier 3 — Complicated: one dedicated agent per task

One agent owns one task. Use when the task needs deep context (cross-file
grep, multi-step refactor, full skill-load chain), or its deliverable
will be reviewed in isolation.

- A refactor that touches >5 files across skills + agents + tests.
- A new feature that requires full domain-skill engagement.
- Any task where bundle-context would exceed ~150k tokens.

### Rules of thumb

**≤150k tokens per agent.** When estimating: manifest skill loads (~5–15k
each), `PLAN.md` + `RESULTS.md` (5–50k depending on stage), plus per-task
file reads. If an agent's projected context exceeds ~150k, split the work
across two agents even when the individual items are small — context
thrash degrades output quality more than the cost of a second spawn.


**Parallelize independent tasks.** Tasks whose `Depends on:` lines (see
`planning-workflow` §Task Dependencies) are all satisfied and that share
no mutable state are encouraged to be dispatched in parallel to separate agents.


---

## Concurrent Writers Require Worktree Isolation

When a parallel dispatch batch contains **≥2 implementers**, each runs in its own git worktree on a `parallel/<analysis-branch>/<slug>` branch (slug is orchestrator-chosen — `a`, `b`, `alpha`, a bundle name). Two implementers sharing a worktree race on `PLAN.md` / `RESULTS.md` and any shared output path; worktree isolation is the only safe concurrency model for parallel writes.

Applies to implementers by default. Reviewers typically run post-merge on the analysis branch; read-only research subagents return findings to the orchestrator, which does the single write.

The same pattern generalizes to parallel reviewers when the diff to be walked is large enough that a single reviewer's context would exceed the ~150k threshold (see §Workload Balancing). The orchestrator splits the diff into disjoint slices (by task ID, by file subtree, or by commit range), dispatches one reviewer per slice on its own worktree, and aggregates the per-slice verdicts into a single overall verdict. The `Worktree:` dispatch field applies to reviewers in this configuration as well. Disjoint scoping is the invariant — two reviewers must not walk the same hunk, and their union must cover the whole diff.

### Ownership split

| Direction | Owner | When | How |
|---|---|---|---|
| Seed-in (inputs → worktree) | Orchestrator | Before dispatch | `worktree-data-sync` §`--mode seed` with `--seed-sync-mode force-symlink` |
| Inside worktree (task execution) | Subagent | During dispatch | Normal file I/O on the `parallel/…` branch |
| Harvest-out (merge back) | Orchestrator | After all siblings return | Plain `git merge --no-ff parallel/<branch>/<slug>` |
| Cleanup | Orchestrator | After merge | Harness worktree tool or `git worktree remove` + `git branch -D` |

Task boundaries are set ex-ante in `PLAN.md`, so `parallel/…` branches are mechanically disjoint and merge without `semantic-merge`. If a conflict surfaces, resolve trivial adjacent edits inline; escalate material ones to the researcher. The `merge-guard` hook exempts `parallel/*` source branches.

Force-symlink seeding is safe because parallel tasks have disjoint write paths by construction. A task that would mutate seeded data either needs a redrawn boundary or `--seed-sync-mode force-cow`.

### Worktree lifecycle

Prefer harness worktree tools (`EnterWorktree`, `ExitWorktree`); fall back to raw git per `references/worktree-harness-fallback.md`, which also covers placement and gotchas.

Transient state (branch names, HEAD SHAs, worktree paths) is not persisted in `PLAN.md` — git (`git worktree list`, `git branch`) is the source of truth.

---

## Dispatch Templates

Every workflow skill that dispatches an `implementer` or `reviewer` subagent uses the canonical template shape defined here. Stage-specific bodies (what goes into `Task:`, `Git range:`, and `Additionally:` for a given stage) live inside each workflow skill — those skills point here for the shape rules.

Every template opens with the canonical prefix **"Follow the standard stage-relevant workflow and load relevant skills and documents to proceed. Additionally, …"**. The prefix tells the agent that its standard Before-You-Start is in effect and it loads what `superRA:using-superRA` §Skill-Load Manifest specifies for its Stage; whatever follows `Additionally,` is task-specific steering on top — focus areas, prior-round adjudication notes, warnings, or additional non-default skill/reference. The dispatch prompt does not repeat the standard protocol, never paraphrases `PLAN.md` content, and never restates checklist items the agent already reads.

**Canonical shape — required fields first, `Additionally:` anchor last:**

**Implementer:**
```
Agent(subagent_type: "superRA:implementer"):
  Stage: <stage-name>
  Task: <task pointer — e.g., "Task N in PLAN.md">
  Worktree: <absolute path>   # optional — parallel-dispatch only

  Follow the standard stage-relevant workflow and load
    relevant skills and documents to proceed. Additionally,
    <optional steering — focus area, prior-round adjudication notes, or
    warnings. Must add information on top of the default; never restate
    what the default protocol, skill-load manifest, or PLAN.md already
    says.>
```

**Reviewer:**
```
Agent(subagent_type: "superRA:reviewer"):
  Stage: <stage-name>
  Task: <task pointer>
  Git range: <BASE_SHA>..<HEAD_SHA>

  Follow the standard stage-relevant workflow and load
    relevant skills and documents to proceed. Additionally,
    <optional steering — focus area, prior-round adjudication notes, or
    warnings. Must add information on top of the default; never restate
    what the default protocol, skill-load manifest, or PLAN.md already
    says.>
```

**Optional steering is strictly additive.** If your `Additionally:` line
only paraphrases the default protocol, the skill-load manifest, or
`PLAN.md` content, delete it — re-statement of content the agent will
read itself is noise that clutters the dispatch without adding signal.

**`Worktree:` field (parallel-dispatch only; implementers always, reviewers when using the parallel-reviewer pattern in §Concurrent Writers).** Absolute path to the dedicated worktree provisioned per §Concurrent Writers. When present, the dispatch **must** include this canned steering in the `Additionally:` tail — the one case where that tail carries required, non-additive content:

> *Work inside the worktree at `<path>`. Enter via `EnterWorktree` if available, otherwise `cd <path>`. Do not edit files outside. Do not merge or push — the orchestrator owns merge-back.*

The agent reads `PLAN.md`, Data Inventory, Conventions, and prior results from `RESULTS.md` directly — the dispatch does not re-state them. If a non-default skill load, an extra domain reference, or an override of the standard handoff is required for this particular call, add `Skills:` and `References:` lines between the required fields and the prefix line.

**Banned in dispatch prompts:**

- `Work from:` — the worker's cwd is the default; stating it is noise.
- Re-statement of `PLAN.md` content, standard protocol, or the manifest's skill/reference loads — the agent reads those itself.

## Handling Reviewer Feedback (Orchestrator Discipline)

The reviewer is adversarial by design — it flags aggressively, and some findings will be false positives. This is the intended dynamic. **You — the orchestrator — are the arbitrator.** You made the plan, you talk to the researcher, and you have big-picture context the reviewer lacks. Your job between a REVISE verdict and re-dispatch is to independently evaluate each issue against that context, not to forward findings mechanically or defer to the reviewer's judgment.

When a reviewer returns REVISE:

1. **Read the actual code at the cited file:line.** Do not trust the reviewer's summary. The reviewer is also a subagent and can be wrong.

2. **For each issue, classify it:**
   - **Real bug** (the code is incorrect or missing required discipline) → forward to implementer
   - **Pedantic but valid** (the issue is real but tiny — missing markdown cell on a trivial step, etc.) → decide whether the fix is worth the cycle. For minors, often yes; for cosmetic minors on a fast-iteration draft, often no
   - **Wrong** (the reviewer misread the code, missed context, or is suggesting a change that conflicts with the methodology you established with the human partner) → push back on the reviewer, do not forward to the implementer

3. **If you reject reviewer feedback, document why in place on the review item.** Append an `→ orchestrator: rejected <reason>` annotation directly under the item in the review-notes blockquote:
   ```markdown
   > **Review notes:**
   > 1. [MAJOR] Use log returns, not arithmetic. (`Code/03.py:42`)
   >    → orchestrator: rejected — methodology specifies arithmetic returns per plan header Section 2. Reviewer lacked methodology context.
   ```
   For items you are flagging for a second opinion, use `→ orchestrator: <second opinion requested> <reason>` instead. The implementer will see these annotations and leave those items alone; the reviewer will see them on re-review and either accept the override (by deleting the item) or escalate.

   This protects you in three ways: (a) the human partner can audit the override, (b) future sessions see why the reviewer's note was ignored, (c) it forces you to articulate the reasoning rather than wave it away.

4. **If you push back on the reviewer (rather than override them), re-dispatch the same reviewer with counter-evidence.** Cite the file:line that proves the reviewer wrong, the methodology section that overrides their suggestion, or the human partner conversation that established the convention. The reviewer should then either retract or escalate.

5. **If you genuinely cannot tell whether the reviewer is right, escalate via `AskUserQuestion`** (plain text if unavailable). Do not flip a coin and hope. Log per `handoff-doc` §User Decisions Log (inside the relevant task's review-notes area); commit the doc edit in the same commit as the re-dispatched implementer's fix (or as the commit that records the override).

**The orchestrator's authority:** You can override any reviewer issue with documented reasoning. You cannot silently ignore one. If you find yourself dismissing reviewer feedback without writing down why, stop — that's the slip that turns a critical filter into an excuse to skip reviews.

**The orchestrator's limits:**
- You cannot override CRITICAL severity without escalating via `AskUserQuestion` first (plain text if unavailable) and logging the researcher's decision per `handoff-doc` §User Decisions Log. CRITICAL means "will produce wrong results"; if the reviewer is wrong about that, it warrants a real discussion, not a unilateral override.
- You cannot override the same reviewer issue twice across re-dispatches. If the reviewer keeps raising the same point and you keep rejecting it, the disagreement is real — escalate via `AskUserQuestion` and let the researcher settle it, then log the answer per `handoff-doc` §User Decisions Log.

This discipline applies equally to all stages of the using superRA workflow. The orchestrator owns the final call in every loop.

## Review Status Reference

Implementer and reviewer agents own their commits and document updates — see `agents/implementer.md` and `agents/reviewer.md` for the full discipline (scope rule, inline-edit rule, stage-specific handoff). The orchestrator only needs to know how to **read** the resulting state from `PLAN.md`:

| Status line | Meaning | Orchestrator action |
|---|---|---|
| *(no line)* | Not started | Dispatch implementer |
| `IMPLEMENTED` | Code committed, awaiting review | Dispatch reviewer |
| `REVISE` | Reviewer found `[BLOCKING]` issue(s) | Adjudicate (see Handling Reviewer Feedback), re-dispatch implementer, then re-dispatch reviewer for a narrow re-review (cited fixes + dependent findings) |
| `APPROVED` | Review passed | Proceed to next task |

**A task is complete only when its status is `APPROVED`.** Do not proceed to the next task while any review has open issues that you have not adjudicated.

For direct mode (orchestrator executes the step itself), see `superRA:using-superRA` §Execution Modes.

