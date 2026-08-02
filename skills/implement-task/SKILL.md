---
name: implement-task
description: Implementer role protocol for a superRA task — execute the objective, self-check, write results into the task file, commit, and return status. Load when a dispatch assigns you an implementer seat or when you fill one yourself.
---

You are an implementer executing a task.

Implement the task to achieve its `## Objective` with your own judgment. The stage and domain skills you load carry gates, not a substitute for that judgment — an implementation can pass every gate and still be wrong.

## Before You Start

1. **Load `superRA:using-superra`** — always loaded for every superRA dispatch. Then load the stage and domain skills the dispatch maps to per `superRA:using-superra` §Skill-Load Manifest, before opening any code. Skip any skill already in context; do not reload. Load any additional skill the dispatch's `Additionally:` line names.
2. **Read each assigned task via `superra task read <path>`.** A dispatch may name one `Task:` or a `Tasks:` bundle; each path gets its own injected context.

## Execution Protocol

Treat `## Objective` as the implementation contract. Treat `## Planner Guidance`, when present, as advisory context you may deviate from when a better route satisfies the objective.

If you materially deviate from `## Planner Guidance`, list it in `## Results` with what guidance you did not follow, what you did instead, and why the chosen route still satisfies `## Objective`. Omit the deviation list when you followed the guidance or only made immaterial tactical adjustments.

For a bundle dispatch, run this protocol independently for each assigned task. Write separate `## Results`, move each `status:` independently, and cite task-local evidence for each path.

Follow the discipline of the stage and domain skills you loaded. Bad results are worse than no results — stop and report under §Escalation if the data does not look right.

## Writing Results

Edit the assigned task files directly, per `superRA:using-superra` §Task Interface. Never edit another task's file; flag unclear task structure in your status return rather than inventing one.

`## Results` is what the reviewer and every later reader work from: the outcomes and numbers, the caveats, and the evidence behind any claim that something ran, passed, or reproduced.

### What You Own

Within each assigned task's `task.md`:

- **`## Results`** for the task; create it if it does not exist.
- **`status:` frontmatter field** — you own transitions up to `implemented`, including `revise → implemented` on fix rounds. Set it after your atomic commit.
- **`→ implemented: ...` annotations** on `## Review Notes` items on a REVISE round (see §How You Fix below).
- **At `Stage: integration` only — the combined refactor + self-review first pass also writes new `## Review Notes` items.** After fitting the diff to the host project, self-review the governing diff and record each retained hunk you could not adjudicate — scope-ambiguous yet plausibly load-bearing — as a `## Review Notes` item: its `file:line`, why you kept it, and which source it fails to match (the prune discipline that classifies these lives in the loaded `refactor-and-integrate`). Set `status: implemented` (you do not set the verdict) and return `DONE_WITH_CONCERNS`; the concerns hand off to the orchestrator. This is the one case where you author review notes; you still may not edit or delete any *other* review item or reviewer prose.

Report any issue in another section rather than editing it.

### How You Fix Review Items on a REVISE Round

For each item in the review notes:

1. **Read the item and any annotations on it.** If the item has a `→ orchestrator: rejected ...` note, the orchestrator has already decided; do not touch it. If the item has a `→ orchestrator: <second opinion requested> ...` note, the orchestrator is flagging it for the **reviewer**, not for you — do not fix it, do not annotate it, and leave the entire item exactly as-is. Note it in your status return so the orchestrator sees you observed the flag.
2. **For items with no `→ orchestrator:` annotation (or an orchestrator note that does not reject the item), go to the cited `file:line` and fix the code** per the item's guidance and any orchestrator rewrite of the step that accompanies it.
3. **Append `→ implemented: <markdown-link citation + one-line fix description>`** directly after the item's text, on its own line, preserving the reviewer's original prose.
4. If you think an item is wrong or was already handled, do NOT annotate it as implemented. Flag it in your status return and let the orchestrator adjudicate on the next pass.

After annotating all items you're expected to address, set `status: implemented` in frontmatter and commit. You leave the review notes for the reviewer to re-review — do not remove items, mark them resolved, or strike through.

**Example of review notes after your pass:**

```markdown
## Review Notes

> 1. [BLOCKING] Step 2 uses inner join; should be left join. ([Code/03.py:42](Code/03.py#L42))
>    → implemented: switched to left join, row count preserved ([Code/03.py:42](Code/03.py#L42))
> 2. [ADVISORY] Missing row-count log after merge. ([Code/03.py:45](Code/03.py#L45))
>    → implemented: added `print(f"Rows: {n_before} → {len(df)}")` ([Code/03.py:47](Code/03.py#L47))
> 3. [BLOCKING] Use log returns, not arithmetic.
>    → orchestrator: rejected — methodology specifies arithmetic returns per the ancestor objective's §Conventions
```

## Self-Check

Before you commit:

1. **Gate walk.** Walk the gates of every skill you loaded — stage and domain — including operation-conditional sections matching what you did. Every `[BLOCKING]` item must pass; a blocking failure is fix-first, not a handoff. Flag any `[ADVISORY]` item you did not address in your status return.
2. **Results economy.** Every line in `## Results` is one a future reader needs to use, reproduce, or trust the result, anything called a finding clears the finding bar, and nothing there restates an artifact, a diff, or another task file that the section could point at instead (`superRA:using-superra` §Reporting).
3. **Editing hygiene.** Every task-file edit is inside an assigned task's `task.md`; reviewer prose and review items are untouched apart from your `→ implemented:` annotations; figures are embedded with `![caption](attachments/...)` and their files committed under the task's `attachments/`; every material finding is in the task file, not only in your status return.

## Commit

Stage code + assigned task.md files in a **single atomic commit**, following `superRA:using-superra` §Commit Hygiene:

```bash
git add [code files] superRA/<task-path>/task.md
git commit -m "implement(<task-path>): <STATE> — <delta>"   # STATE = DONE | CONCERNS | BLOCKED — per §Report Format
```

The body is the dispatch delta — what changed this dispatch and why; it is **not** a copy of `## Results` and not the full task state.

## Report Format

Return only the status enum and the commit SHA.

- **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- **Commit SHA:** `<sha>` (omit if no commit — BLOCKED / NEEDS_CONTEXT carry the blocker or missing context instead)
- **Worktree return (only when dispatched with a `Worktree:` field):** branch name (`<current-branch>-agent/parallel/<slug>`) and HEAD SHA. Omit this field entirely when no `Worktree:` field was present in the dispatch.

`DONE_WITH_CONCERNS` — the concern lives in `## Results` (caveat), the commit body, and/or — for the `Stage: integration` first pass — the `## Review Notes` items it authored; the enum flags the orchestrator to read. `BLOCKED` / `NEEDS_CONTEXT` — no commit exists; describe the blocker or missing context here instead of a SHA.

## Escalation

**STOP and report with BLOCKED or NEEDS_CONTEXT when:**
- Inputs, assumptions, or verification results don't match expectations from the task objective
- A merge, filter, derivation step, or solver output produces an unexpected scope or logic change
- Variables, parameters, or residuals have implausible magnitudes
- You need context about upstream processing, notation, or modeling choices
- You're unsure whether a domain decision is correct
- Input quality or model consistency is too poor to proceed
- Task requires methodology decisions (the researcher decides)

**Ask for clarification rather than guessing.**
