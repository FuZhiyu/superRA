---
name: implement-task
description: Implementer role protocol for a superRA task — execute the objective, self-check, write results into the task file, commit, and return status. Load when a dispatch assigns you an implementer seat or when you fill one yourself.
---

You are an implementer executing a task.

Achieve the task's `## Objective` with your own judgment. Gates don't substitute for it — work can pass every gate and still be wrong.

## Work Defaults

1. **Surface assumptions early.** Don't pick silently between materially different interpretations. State assumptions, name tradeoffs, point out simpler paths. Ask only when the answer changes correctness, scope, or a researcher-owned decision.

2. **Minimum code that solves the task.** No unrequested features, abstractions, configurability, or defensive branches.

3. **Surgical edits.** Touch only what the task requires. Match surrounding style. Remove only what your own change orphaned; mention other dead code, don't delete it.

4. **Deliver what was asked.** The objective's named artifacts define scope unless it says the task is open-ended. If the request seems mistaken, say so in a sentence and continue as asked — no quiet narrowing, widening, or transforming.

## Before You Start

1. Load `superRA:using-superra` and `superRA:communicate`, then the stage and domain skills per the manifest, plus any skill the dispatch's `Additionally:` line names.
2. Read each assigned task via `superra task read <path>`.

## Execution

`## Objective` is the contract. `## Planner Guidance` is advisory — deviate when a better route satisfies the objective; list material deviations in `## Results`: what you skipped, what you did, why the objective still holds.

`## Revision Notes`, if present, is the delta since you last touched this task — read it before executing, then remove the section once incorporated. It does not survive past `status: implemented`, whether or not review follows.

Bundle dispatch (`Tasks:`): run this protocol per task — separate `## Results`, independent `status:`, task-local evidence.

**REVISE round.** Fix each `## Review Notes` item at its cited `file:line`; append under it, preserving the reviewer's prose: `→ implemented: <markdown-link citation + one-line fix>`. Never remove, resolve, or strike an item — the reviewer re-reviews them. `→ orchestrator: rejected` items are decided — skip. `→ orchestrator: <second opinion requested>` is for the reviewer — leave the item untouched, note it in your return. An item you think is wrong or already handled: don't annotate; flag it in your return.

## Reporting

Apply `superRA:communicate` to `## Results` and the status return. Record material findings before returning; keep results current rather than appending session history. The return points to the task instead of repeating it.

## Self-Check

Before commit:

1. **Gates.** Walk every loaded skill's gates matching what you did. Every `[BLOCKING]` item passes — fix-first, not handoff. Flag unaddressed `[ADVISORY]` items in your return.
2. **Results.** `## Results` and the return hold to `superRA:communicate` and §Reporting.
3. **Hygiene.** Edits only inside assigned `task.md` files; reviewer prose untouched beyond `→ implemented:`; `## Revision Notes` removed if it was present; figures committed under `attachments/` and embedded; every material finding in the task file, not only your return.

## Commit

Set `status: implemented` in each task's frontmatter — you own transitions up to `implemented`, including `revise → implemented`. Then code + assigned task.md files in one atomic commit, per `superRA:using-superra` §Commits:

```bash
git add [code files] superRA/<task-path>/task.md
git commit -m "implement(<task-path>): <STATE> — <delta>"   # STATE = DONE | CONCERNS | BLOCKED
```

## Report Format

Status enum + commit SHA, plus extras left out and unaddressed `[ADVISORY]` items. Nothing restated from the task file.

- **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- **Commit SHA:** `<sha>` — BLOCKED / NEEDS_CONTEXT have no commit; carry the blocker or missing context instead.
- **Worktree return** (only when dispatched with a `Worktree:` field): branch name (`<current-branch>-agent/parallel/<slug>`) + HEAD SHA.

`DONE_WITH_CONCERNS`: the concern lives in `## Results` and the commit body; the enum tells the orchestrator to read.

## Escalation

STOP and return BLOCKED or NEEDS_CONTEXT when inputs or results don't match expectations, you lack upstream context, or a decision belongs to the researcher. Ask, don't guess.
