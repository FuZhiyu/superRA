---
name: superintegrate
description: "Integrate code-complete superRA work. Requires superRA:using-superra. Use for result protection, base sync, codebase-fit refactors, permanent records, cleanup, or PR preparation."
---

# superintegrate — the INTEGRATE phase

Workflow skill for the **INTEGRATE** phase. It takes a reproducibility-verified branch through five steps:

```
Protect              -> protect key results (default: drift tests)
Sync                 -> bring the branch onto the current base via semantic-merge
Integrate            -> refactor with Sync context (do-then-verify), then pass integration review
Mature & Consolidate -> distil each touched task: where its content lands + how
                        much of its ## Results survives, decided as one act
Finish               -> final freshness check, PR or fast-forward, and cleanup

Any step -> superplan §User Feedback and Changing the Task Tree
           when scope, methodology, task structure, or task status changes materially
```

**Announce at start:** "I'm using the superintegrate skill to prepare this work for integration."

## Stop Points

The Workflow Frontier Resolver chooses where to enter. Once entered, run the selected step's local gates; do not redo task-local approvals outside the affected frontier. INTEGRATE keeps no progress checkboxes — each step's completion is recorded by its commit and the per-task `status` it leaves behind, so a resumed session reads progress from git and statuses, not from a tracker section. INTEGRATE is one multi-step phase, so its commit subjects carry the step name in the scope per `using-superra` §Commit Hygiene: `integrate(<step>): <summary>`, where `<step>` is one of `protect | sync | fit | mature | finish`.

Legitimate stop points (fold every answer into the relevant task objective **before** acting):

- **Protect:** key-result protection confirmation.
- **Sync:** target base confirmation when no prior decision records it; intent-changing conflicts surfaced by `semantic-merge`.
- **Integrate:** meaningful drift after sync or refactor; user-owned choices surfaced by the first-pass self-review or the integration reviewer.
- **Mature & Consolidate:** the distillation question, one per touched subtree, always fires before any execution — even a clean subtree gets an explicit confirm.
- **Finish:** hard blockers only, such as target base advancing again after Integrate.

## Dispatch Convention

**Load `superRA:agent-orchestration` before writing any dispatch prompt.** Task-scoped dispatches use the Stage values in `superRA:using-superra` §Skill-Load Manifest; do not restate load lists in prompts.

A non-trivial Sync uses `Stage: sync` with generic sync author / sync reviewer agents and the relevant `semantic-merge` mode reference; a trivial Sync lands inline in Direct mode (Step 3).

## Protect

Drift tests are the default protection mechanism, guarding key results through Sync, Integrate, Finish, and future work. For the writing vertical, "key results" are the manuscript artifacts; protection is satisfied by document-build success plus outline stability across the merged state — see `skills/writing/references/integration.md`.

**Always run the full drift-test suite on every integration pass.** Authoring new drift tests is scoped to the tasks this integration reopens or changes — reopened/changed tasks plus orchestrator-declared related tasks from `superplan §User Feedback and Changing the Task Tree`; running the suite is not scoped.

### Steps

1. **Extract key results from task.md `## Results` sections.** Walk the `superRA/` tree (`superra task tree`) and identify main findings across tasks. Protect main findings, not every intermediate number. Reference tasks by path (e.g., `data-preparation/merge`).
2. **Confirm coverage with the researcher.** Stop point:
   ```text
   These results seem like the key findings to protect:
   - [result 1: description and value] (from task-path/subtask)
   - [result 2: description and value] (from task-path/subtask)

   Which should be protected? Any to add or remove?
   ```
3. **Dispatch protection-creator.** `Stage: protection`, canonical implementer template. Drift tests reference task paths, not task numbers.
4. **Dispatch protection-reviewer.** `Stage: protection`, canonical reviewer template. On REVISE, adjudicate and fix per `agent-orchestration` §Handling Reviewer Feedback until APPROVE.
5. **Run tests on the current branch.** If new tests fail on existing code, fix the tests.
6. **Commit tests and task.md updates** once all confirmed key results are protected and the full drift-test suite passes. The protection commit (`integrate(protect): …`) is the record that Protect is done.

## Sync

Sync brings the branch onto the current base before refactor starts. A trivial sync (per Step 3) lands inline in Direct mode; a non-trivial sync is serialized — one generic sync author followed by one generic sync reviewer, no parallelization. A dispatched sync (its own `Stage: sync`) commits under the `sync` stage verb; an inline Direct-mode sync lands as `integrate(sync): …` per §Stop Points.

### Step 1: Resolve the target base

Resolve and record a candidate base ref from prior task context or git. This is a branch/ref name, not a merge-base SHA:

```bash
if git rev-parse --verify --quiet origin/main >/dev/null; then
  BASE_REF=origin/main
elif git rev-parse --verify --quiet origin/master >/dev/null; then
  BASE_REF=origin/master
else
  BASE_REF=
fi
```

If no prior decision records the base, ask:

```text
This integration will sync the branch against <base-ref>.
Is that correct, or did it split from a release branch, co-authored track,
or sibling branch?
```

Confirm `BASE_REF` before fetching, computing anchors, or dispatching. It is a working value for this integration pass, not a stored field — the sync merge commit records which base was synced (and pins `BASE_HEAD_SHA` as its base-side parent), so a resumed session recovers it from git rather than from a task section.

### Step 2: Compute sync anchors

Fetch the confirmed base when it is a remote-tracking ref and record two anchors from that same ref:

```bash
REMOTE=${BASE_REF%%/*}
REMOTE_BRANCH=${BASE_REF#*/}
if git remote get-url "$REMOTE" >/dev/null 2>&1; then
  git fetch "$REMOTE" "$REMOTE_BRANCH:refs/remotes/$REMOTE/$REMOTE_BRANCH"
fi
PRE_SYNC_BASE_SHA=$(git merge-base HEAD "$BASE_REF")
BASE_HEAD_SHA=$(git rev-parse "$BASE_REF")
```

- `PRE_SYNC_BASE_SHA` is evidence for incoming intent: `PRE_SYNC_BASE_SHA..BASE_HEAD_SHA`.
- `BASE_HEAD_SHA` is the post-sync governing baseline for Integrate: `BASE_HEAD_SHA..HEAD`.

### Step 3: Sync the branch when needed

If `git merge-base --is-ancestor "$BASE_HEAD_SHA" HEAD` succeeds, the branch is already synced — proceed to Integrate.

Otherwise size the sync against `semantic-merge §Scope the merge first`. When it scopes trivial, announce the Direct-mode switch and land the merge inline following that section, then skip the author and reviewer dispatch that follow and proceed to Integrate — its reviewer pass over `BASE_HEAD_SHA..HEAD` verifies the landed merge.

When the sync is non-trivial, dispatch one generic sync author:

```text
Agent(generic):
  Stage: sync
  Role: sync author
  References:
    - semantic-merge/references/workflow-sync-author.md

  Task: Sync this branch with <base-ref>
  Base branch: <base-ref>
  PRE_SYNC_BASE_SHA: <PRE_SYNC_BASE_SHA>
  BASE_HEAD_SHA: <BASE_HEAD_SHA>
  Incoming range: <PRE_SYNC_BASE_SHA>..<BASE_HEAD_SHA>

  Use semantic-merge workflow sync author mode. Land the merge commit plus
  any propagation commits needed to reach semantic coherence — `SKILL.md
  §Semantic Coherence Checklist §Scope boundary` is the stopping rule. The
  branch-level sync narrative is the commit messages; add a task-local
  `## Sync Impact` section to each affected task.md whose post-sync diff needs
  task-specific context. Defer codebase coherence — convention fit, utility
  reuse, PR-friendly diffs, Project Doc Audit walk-up, minimum net diff — to
  `refactor-and-integrate` via Integrate.
```

If the sync author returns `NEEDS_CONTEXT` or `BLOCKED` because a user decision is required, the orchestrator asks the user, folds the decision into the relevant task objective, commits, and re-dispatches the sync author with the decision context.

### Step 4: Dispatch the sync reviewer

Before Integrate begins, dispatch one generic sync reviewer:

```text
Agent(generic):
  Stage: sync
  Role: sync reviewer
  References:
    - semantic-merge/references/workflow-sync-reviewer.md

  Task: Review the semantic sync with <base-ref>
  Base branch: <base-ref>
  PRE_SYNC_BASE_SHA: <PRE_SYNC_BASE_SHA>
  BASE_HEAD_SHA: <BASE_HEAD_SHA>
  Incoming range: <PRE_SYNC_BASE_SHA>..<BASE_HEAD_SHA>
  Sync commits: <MERGE_COMMIT_SHA>[, <PROPAGATION_OR_DOC_SHAS>...]

  Use semantic-merge workflow sync reviewer mode. Verify anchors, incoming
  intent, current-branch intent, conflict resolution, user-decision logging,
  task-local `## Sync Impact` coverage, and scope boundary. Record any
  sync-review finding via the standard mechanism (affected task's
  `## Review Notes`, or the REVISE return for a branch-level finding with no
  task home). Return APPROVE or REVISE.
```

On REVISE, adjudicate sync-review findings per `superRA:agent-orchestration` §Handling Reviewer Feedback, re-dispatch the sync author for accepted items, then re-dispatch the sync reviewer. Integrate starts only after sync review APPROVES.

## Integrate

Integrate is the post-sync quality gate, and it runs do-then-verify: a combined refactor + self-review pass first produces the codebase-fit work and the Final-Diff-Self-Check trail, the orchestrator adjudicates that pass's first-round concerns, and only then does an independent reviewer verify the result. It uses task-local `## Sync Impact` sections plus the sync commit messages (git log) as context for the approved post-sync diff, fits the code to the host project, audits project docs, and verifies the surviving diff against the current base.

**Governing diff:** `git diff BASE_HEAD_SHA..HEAD`. Do not use the old merge base for minimum-net-diff review after Sync.

The number of integration implementers and reviewers is discretionary, scaled to the post-sync delta per `agent-orchestration §Workload Balancing`: a small single-subtree delta takes one implementer pass (or an inline sweep) plus one reviewer; a large or multi-subtree delta fans out per subtree.

### Step 1: Run the full drift-test suite

Run the full suite after Sync and before refactor. Failing drift tests block Integrate until classified per `result-protection/references/drift-test-quality.md`.

### Step 2: Integration implementer pass (refactor + self-review)

Dispatch `Stage: integration` implementer(s) to fit the post-sync diff to the host project and run the Final-Diff-Self-Check. A trivial post-sync diff collapses to an orchestrator-inline pruning sweep in Direct mode instead of a dispatch.

```text
Agent(subagent_type: "superRA:implementer"):
  Stage: integration
  Task: Post-sync codebase-fit refactor and self-review for <task-path-list>
  Tasks in scope: <task paths touched or Sync-impact-affected>
  BASE_HEAD_SHA: <BASE_HEAD_SHA>

  Additionally: read task-local `## Sync Impact` sections and the sync commit messages
    as context, fit `git diff <BASE_HEAD_SHA>..HEAD` to the host project, and run the
    Final-Diff-Self-Check; self-review and surface concerns per §What You Own. Commit
    code + task.md atomically. Do not touch tasks outside `Tasks in scope`.
```

### Step 3: Orchestrator adjudication

For each first-pass concern returned in `## Review Notes`:

- **fix** — dispatch an implementer to revert the junk or address the finding; or
- **amend** — fold the justification into the relevant task objective via `superplan §User Feedback and Changing the Task Tree`, dropping the concern.

The resolving commit clears the now-moot first-pass note so the independent reviewer in Step 4 starts from a clean `## Review Notes`. Batch all user-owned questions into one stop point; route substantive task-tree restructures through `superplan §User Feedback and Changing the Task Tree`.

### Step 4: Dispatch the independent integration reviewer

Dispatch fresh `Stage: integration` reviewer(s) for a full first review of the codebase-fit pass against its trail:

```text
Agent(subagent_type: "superRA:reviewer"):
  Stage: integration
  Task: Post-sync integration review for <task-path-list>
  Tasks in scope: <task paths touched or Sync-impact-affected>
  Git range: <BASE_HEAD_SHA>..HEAD
  BASE_HEAD_SHA: <BASE_HEAD_SHA>
  Sync context: task-local `## Sync Impact` sections plus the sync commit messages (git log)

  Additionally: read task-local `## Sync Impact` sections and the sync commit messages
    as context, then review `git diff <BASE_HEAD_SHA>..HEAD` against the Final-Diff-Self-Check
    trail. For every in-scope task, either set `status: approved` in its frontmatter or
    write review notes in `## Review Notes` and set `status: revise`. Findings should
    cover minimum surviving branch delta, codebase fit, project-doc audit,
    drift-test implications, and task-file coherence. Do not recreate
    incoming-intent research or re-review semantic coherence already approved
    by sync review.
```

### Step 5: Refactor loop

Adjudicate the reviewer's `status: revise` findings per `superRA:agent-orchestration` §Handling Reviewer Feedback, then dispatch implementer(s) for accepted items:

```text
Agent(subagent_type: "superRA:implementer"):
  Stage: integration
  Task: Fix integration review items for <task-path-list>
  Tasks in scope: <task paths with status: revise>
  BASE_HEAD_SHA: <BASE_HEAD_SHA>

  Additionally: read task-local `## Sync Impact` sections and the sync commit messages
    as context, address accepted review findings, and run the minimum-net-diff
    self-check against `git diff <BASE_HEAD_SHA>..HEAD` before each commit. Commit code + task.md
    atomically. Do not touch tasks outside `Tasks in scope` except where required by an accepted
    reviewer finding.
```

For non-minor fixes that require reviewer re-dispatch per `agent-orchestration` §Handling Reviewer Feedback, include narrow re-review plus the branch-wide pruning sweep over `BASE_HEAD_SHA..HEAD`. Iterate until all in-scope tasks have `status: approved` and every surviving hunk is justified by approved objectives, approved semantic-sync context, logged user decisions, or project convention fit.

### Step 6: Close Integrate

Run the full drift-test suite again. When it passes and integration review is APPROVED:

- remove every temporary task-local `## Sync Impact` section, unless a lasting task assumption still belongs in the task.md — in which case fold that assumption into the task's `## Objective` and remove the section. Then run `superra task check` (warn-only `sync-impact` category) and confirm it flags no surviving `## Sync Impact`.
- commit the closeout edit (`integrate(fit): …`); that commit plus the in-scope tasks' `status: approved` is the record that Integrate closed.

## Mature & Consolidate

Once Integrate closes, every task this integration touched is a distillation candidate: its work is settled and verified. For each touched task, decide and execute as **one act** the structural fold (content merged into the parent, kept as its own task, directory removed) together with the results altitude (dropped / a folded pointer or one-line note / a short retained subsection / a matured reader-facing narrative at the durable home). Run this stage once, after Integrate, on final results — the fold actions are atomic over objective + results + directory and must not run on pre-Integrate state.

Screening and the user-facing proposal are orchestrator inline work, not a dispatched implementer, because consolidation is user-involving. Execution is dispatched.

### Step 1: Screen the whole affected tree (mandatory)

Load `superplan/references/task-tree-design.md` and survey every task and subtree the integration touched — including approved and in-flight update tasks — against its parent and other candidate durable owners. Run `superra task tree`, `superra task dag`, and `superra task check --category placement`; treat placement warnings as advisory evidence alongside the manual survey. Identify every update-task, action-verb parent, and misplacement, and per touched subtree draft the distillation: each task's durable home, the structure change that realizes it, and the altitude its `## Results` distils to. Key results selected at Protect are never dropped; when a task's own output *is* a document, distil its `## Results` to a pointer to that document.

### Step 2: Ask the distillation question, one per touched subtree (always fires)

Ask one options-with-recommendation question per touched subtree (`AskUserQuestion`, plain text if unavailable), across as many calls as the harness per-call limit takes. The question always fires — a clean subtree still gets one, with the recommended option carrying no fold ("keep as-is, mature at <home>"). Each question's options are that subtree's candidate consolidation actions plus an explicit keep-as-is option that lets the user veto; mark the orchestrator's screened recommendation first. The recommended option states the proposed structural action(s) and the resulting `## Results` altitude:

```text
Subtree <subtree-path> — consolidate how?
  ▸ [Recommended] Fold <task-a> into <parent> (results → one-line note);
    drop <task-c> (already in <parent> diff); <task-b> matures at <home>
  ▸ Keep all tasks as-is; mature each in place
  ▸ <other meaningful variant — e.g. a different durable home for <task-b>>
```

Material tree changes route through `superplan §User Feedback and Changing the Task Tree` for explicit approval — pruning a task whose result a reader would expect, merging substantive concerns, or a scope-expansion that invalidates downstream. Routine distillation is the recommended default the user can veto. Execution cannot begin before the answer.

### Step 3: Record, then dispatch execution

Fold each subtree's decision into `## Revision Notes` on the affected tasks, then dispatch implementer(s) to execute the distillation — structural folds and results altitude together, per subtree (fan out per subtree when large):

```text
Agent(subagent_type: "superRA:implementer"):
  Stage: maturation
  Task: Execute the distillation for <subtree-path>
  Tasks in scope: <task paths in this subtree>

  Additionally: execute the recorded `## Revision Notes` distillation —
    structural folds per `superplan/references/consolidation.md`, and the
    `## Results` altitude per `task-tree/references/task-file-contract.md`
    §Results Shape (drop / pointer / short subsection / matured narrative),
    materializing figures with `report-in-markdown` where a matured home needs
    them. Edit task.md files in place; land one recoverable commit per task or
    logical group and report which sub-commits landed.
```

### Step 4: Whole-tree review

Dispatch one whole-tree reviewer for structure (not parallelized); results distillation may fan out per subtree when large:

```text
Agent(subagent_type: "superRA:reviewer"):
  Stage: maturation
  Task: Verify consolidated structure and distilled results
  Git range: <BASE_SHA>..<HEAD_SHA>
  Tasks in scope: <whole affected tree>

  Additionally: verify the consolidated structure — no update-task or
    action-verb scaffolding left stranded, placement clean, Protect key
    results retained — and the distilled `## Results` per
    `task-tree/references/task-file-contract.md` §Results Shape.
    <prior-round adjudication notes if re-dispatching>
```

On REVISE, adjudicate and fix per `agent-orchestration` §Handling Reviewer Feedback until APPROVE. If a finding traces to the code, re-enter Integrate. On APPROVE, commit the consolidated, matured tree (`integrate(mature): …`).

## Finish

Finish executes the user's completion choice from `superimplement`. The `superRA/` directory is committed as-is — it is part of the permanent branch record; any closeout commit here lands as `integrate(finish): …` per §Stop Points.

### Step 1: Freshness check

`BASE_REF` and `BASE_HEAD_SHA` carry over within a session. On a resumed session, recover them from the sync merge commit: its base-side parent is `BASE_HEAD_SHA`, and the commit message records the base that was synced. If Sync was a no-op (the branch was already current), use the pre-Integrate base ref directly.

Fetch `BASE_REF` when it is a remote-tracking ref and check whether it advanced since Integrate:

```bash
REMOTE=${BASE_REF%%/*}
REMOTE_BRANCH=${BASE_REF#*/}
if git remote get-url "$REMOTE" >/dev/null 2>&1; then
  git fetch "$REMOTE" "$REMOTE_BRANCH:refs/remotes/$REMOTE/$REMOTE_BRANCH"
fi
CURRENT_BASE_HEAD_SHA=$(git rev-parse "$BASE_REF")
```

If `CURRENT_BASE_HEAD_SHA` differs from `BASE_HEAD_SHA`, re-enter Sync before publishing or landing the work.

### Step 2: Publish or land

For a PR:

```bash
git push -u origin <analysis-branch>
gh pr create --title "<title>" --body "<summary, data, reproducibility, quality gates>"
```

For a local fast-forward into the base:

```bash
git checkout <base-branch>
git pull
git merge --ff-only <analysis-branch>
```

Run the project pipeline or targeted verification on the final tree. If it fails, investigate before cleanup.

### Step 3: Cleanup

If the work used a worktree, remove it per `superRA:agent-orchestration/references/worktree-harness-fallback.md`. Seeded non-git data disappears with the worktree; see `superRA:worktree-data-sync` for data teardown.

Report what was published or landed and what was cleaned up.

## When to Lighten

- **Standalone analysis:** Protect still runs. Sync may be a no-op. Integrate often collapses to an inline pruning sweep plus a short reviewer pass.
- **Small changes:** Keep the same five steps, but dispatch fewer agents and add no `## Sync Impact` sections when there is no material sync context.
- **Writing-vertical tasks:** Most writing work runs as standalone Review / Polish / Draft per `skills/writing/SKILL.md` and does not enter this workflow. Only large work (whole-section drafts, whole-paper revisions, R&R passes) reaches Integrate; for those, Protect substitutes build + outline-stability for drift tests, and the Integrate reviewer additionally walks `skills/writing/references/integration.md`.
- **Task tree consolidation:** The distillation question always fires, but a clean subtree's content scales to zero — an explicit confirm, no structural fold — see §Mature & Consolidate.

## Red Flags

- Refactoring before Sync when the base has advanced, or using `PRE_SYNC_BASE_SHA` (not `BASE_HEAD_SHA`) as the post-sync minimum-net-diff baseline.
- Parallelizing Sync, or parallelizing refactor before Sync lands.
- Reviewing the post-sync diff before the codebase-fit pass produced it, or closing Integrate with no Final-Diff-Self-Check trail.
- Reaching Mature & Consolidate execution without the distillation question's answer, or running the fold on pre-Integrate state instead of final results.
- Entering Finish without re-checking whether the base advanced since Integrate.
