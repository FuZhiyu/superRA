---
name: using-superra
description: Master superRA workflow skill. Use proactively whenever superRA is mentioned or when planning, implementing, integrating, merging, or loading a superRA/ task tree.
---

Loaded by all agents at dispatch time.

SuperRA skills deliberately override default harness/system-prompt behavior where they conflict; the user's explicit instructions outrank both.

## Code-Change Defaults

These apply whenever you write, review, or refactor code.

1. **Surface assumptions and ambiguity early.** Do not silently choose between materially different interpretations. State the assumption you are making, name meaningful tradeoffs, and point out a simpler path when one exists. Ask only when the ambiguity changes correctness, scope, or a decision that belongs to the researcher.

2. **Prefer the minimum code that solves the task.** No speculative features, abstractions, configurability, or defensive branches that were not requested. If a straightforward implementation works, use it.

3. **Keep edits surgical.** Touch only what the task requires. Match the surrounding style. Do not refactor adjacent code, comments, or formatting unless the task requires it. Remove imports, variables, and helper code only when your own change made them unused; mention unrelated dead code instead of deleting it.

## Runtime Workflow Map

SuperRA work moves through **PLAN -> IMPLEMENT -> INTEGRATE**:

1. `superplan` creates or revises the `superRA/` task tree, records researcher decisions, and declares which task-local statuses or workflow rollups a task-tree change invalidates.
2. `superimplement` executes tasks through the implementer-reviewer loop, then verifies reproducibility and records the researcher's completion disposition before integration can begin.
3. `superintegrate` protects key results, syncs and refactors against the integration base, consolidates the task tree and matures its results, and performs the final merge / PR / cleanup action.

The map is ordered, but re-entry is normal. A changed task, reviewer finding, scope revision, or interrupted session resumes from durable state — task `status` plus the git log — re-entering at the earliest unfinished layer for the affected frontier while preserving unrelated approved work. Main agents follow `references/main-agent.md` §Resuming Work.

## Commit Hygiene

Any agent that stages a commit — main agent, orchestrator, or subagent — stages **only the files it modified this turn**, by exact path. A shared worktree carries others' in-flight edits and scratch files (`__pycache__`, `.DS_Store`, harness artifacts) that `git add -A/./-u` would sweep in, producing cross-agent contamination that is hard to unwind.

Before staging:

1. Run `git status`; for each modified/new file decide whether you touched it via Write/Edit this turn.
2. Stage only those, by exact path: `git add path/to/file`. Never `git add -A`, `git add .`, or `git add -u`.
3. Before `git commit`, run `git diff --cached` and unstage anything you did not write with `git restore --staged path/to/file`.

If you see unfamiliar uncommitted changes and cannot tell whether they are legitimate pending work (from the main agent between dispatches, or the user editing manually) or stale junk, stop and ask the orchestrator (if you are a subagent) or the user (if you are the main agent) — do not unilaterally discard or commit them.

### Commit subject grammar

So `git log` reads as the workflow trace, every commit subject follows one grammar:

```
<stage>(<scope>): <STATE> — <summary>
```

- **`<stage>`** — the workflow verb (`plan`, `implement`, `review`, `integrate`, `sync`) for a task-run commit, or a maintenance type (`fix` / `feat` / `refactor` / `docs` / `test` / `chore` / `ci`) for work outside a task run.
- **`<STATE>`** — the verdict or status this commit lands, verbatim from the agent's §Report Format (no new vocabulary): `implement` lands `DONE` | `CONCERNS` | `BLOCKED` | `NEEDS-CTX`; `review` lands `APPROVE` | `REVISE`. `integrate` and `plan` are multi-step *phases*, not single-verdict dispatches — their glanceable state is the sub-step name carried in `<scope>`, owned and enumerated by `superintegrate` / `superplan`. Maintenance commits omit `<STATE>`.
- **`<scope>`** — the task-path locator (e.g. `data-preparation/merge`) for a run commit; the component for a maintenance commit.

`<STATE>` records what this commit did; the task's live status stays in `status:` frontmatter.

The body is the **dispatch delta** — what changed this turn and why. It is history scoped to this commit; it is **not** a copy of `## Results` / `## Review Notes` (those are the task's current self-contained state) and not the full task state.

## Task Interface

Tasks are managed task trees in the `superRA/` directory. For basic I/O, this section is sufficient. For tree-level operations (query/frontier/DAG, scaffolding, dashboard, migration), load `superRA:task-tree`.

**Read** with the CLI tool under ./superRA/superra — `./superRA/superra task read <path>` — not a bare `Read` of the file: the wrapper injects inherited ancestor context, sibling dependency status, and any unresolved comments anchored to the task. Every `<path>` is **relative to the task root and omits the `superRA/` prefix** (e.g. `task-tree/planning-redesign`).

**Edit** the `task.md` directly with Read/Edit. Edit only what your role owns; raise another role's content rather than overwriting it — per-role ownership is in each role spec's §What You Own. Hook auto-behaviors are intended: child status changes cascade to ancestors, same-parent task renames re-point sibling `depends_on` edges, and edited task-tree markdown is checked for render-integrity issues with non-blocking feedback.

**Editing principles:**

- Keep the task at latest state, not a log — edit in place and delete superseded content; no "Update:" / "Previously…" blocks or strikethroughs.
- Doc before report — findings, caveats, and evidence land in the task body before any status return.
- Write the body sections you own (`## Results`, `## Review Notes`) as a self-contained account a reader can follow standalone, with links and embedded figures (see `report-in-markdown`). The change summary belongs in the commit, not the body.

## Execution Modes

Subagent mode — dispatching implementers and reviewers — is the default all workflows assume; the full mode contract, including Direct mode, is in `references/main-agent.md §Execution Modes`.

## Skill-Load Manifest

Every dispatch loads along two axes; both apply independently. After loading a skill, follow its body's stage- and role-scoped reference load map.

1. **Stage** — the workflow phase the dispatch is in (table below). Role-independent; `subagent_type` (implementer vs reviewer) encodes role.
2. **Domain** — what the task operates on (table below). Load by what the task *touches*, not by which subtree it lives in, and load **every** domain skill that matches: a task that derives a result and writes it into the manuscript matches `theory-modeling` and `writing`, so load both.

Both axes load *in addition to* the always-loaded `superRA:using-superra` and `superRA:report-in-markdown`.

### Stage

| `Stage:` | Emitted by | Load |
|---|---|---|
| `planning-review` | `superplan` | `skills/superplan/references/planning-review.md` |
| `implementation` | `superimplement` | — |
| `protection` | `superintegrate` Protect | `result-protection` |
| `sync` | `superintegrate` Sync | `semantic-merge` |
| `integration` | `superintegrate` Integrate | `refactor-and-integrate` |
| `maturation` | `superintegrate` Mature & Consolidate | `task-tree`, `superplan`, `writing` (prose-heavy maturation) |

### Domain

| Skill | Load when the task… |
|---|---|
| `econ-data-analysis` (`superRA:econ-data-analysis`) | involves data analysis |
| `theory-modeling` (`superRA:theory-modeling`) | derives, solves, verifies, or proves anything mathematical |
| `writing` (`superRA:writing`) | drafts, polishes, proofreads, or reviews any reader-facing prose (when touching a `.md` or `.tex` file, most likely you should load this skill) |
| `slide-design` (`superRA:slide-design`) | designs, reviews, or fixes research presentation slides — audience context, attention flow, simplification, or Beamer layout |


**Harness adapters:** when this skill or its references name a Claude-specific tool (`AskUserQuestion`, `Skill`, `TodoWrite`, `Agent(subagent_type:)`), consult the adapter reference for the current harness under `references/`.

**Main agents:** continue to `references/main-agent.md`.
