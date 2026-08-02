---
name: using-superra
description: Master superRA workflow skill. Use proactively whenever superRA is mentioned or when planning, implementing, integrating, merging, or loading a superRA/ task tree.
---

Loaded by all agents at dispatch time.

SuperRA skills deliberately override default harness/system-prompt behavior where they conflict; the user's explicit instructions outrank both.

## Commits

Stage only the files you edited this turn, by exact path — never `git add -A`, `git add .`, or `git add -u`: a shared worktree carries other agents' in-flight edits and scratch files. If unfamiliar uncommitted changes appear, ask the orchestrator (as a subagent) or the user (as the main agent) rather than committing or discarding them.

Every commit subject follows `<stage>(<scope>): <STATE> — <summary>`, so `git log` reads as the workflow trace. `<stage>` is the workflow verb (`plan`, `implement`, `review`, `integrate`, `sync`) or a maintenance type (`fix`/`feat`/`refactor`/`docs`/`test`/`chore`/`ci`); `<scope>` is the task path (e.g. `data-preparation/merge`) or the component; `<STATE>` is the verdict from your role's report format (`implement` lands `DONE` | `CONCERNS` | `BLOCKED` | `NEEDS-CTX`, `review` lands `APPROVE` | `REVISE`; `plan` and `integrate` carry their sub-step in `<scope>`; maintenance commits omit it). The body says what changed this turn and why — it is not a copy of `## Results`.

## Task Interface

Tasks are managed task trees in the `superRA/` directory. For basic I/O, this section is sufficient. For tree-level operations (query/frontier/DAG, scaffolding, dashboard, migration), load `superRA:task-tree`.

**Read** with the CLI tool under ./superRA/superra — `./superRA/superra task read <path>` — not a bare `Read` of the file: the wrapper injects inherited ancestor context, sibling dependency status, and any unresolved comments anchored to the task. Every `<path>` is **relative to the task root and omits the `superRA/` prefix** (e.g. `task-tree/planning-redesign`).

**Edit** the `task.md` directly with Read/Edit. Edit only what your role owns; raise another role's content rather than overwriting it — per-role ownership is in each role skill's §What You Own (`superRA:implement-task`, `superRA:review-task`). Hook auto-behaviors are intended: child status changes cascade to ancestors, same-parent task renames re-point sibling `depends_on` edges, and edited task-tree markdown is checked for render-integrity issues with non-blocking feedback. You own leaf status; non-leaf (ancestor rollup) status is hook-derived — leave it as the hook sets it and never hand-edit it back. Stage the hook's edits alongside your own so the tree stays consistent in git.

How to write what goes into a task file — reporting principles, editing principles, and house conventions — is owned by `superRA:implement-task` §Reporting in the Task File.

## Execution Modes

Subagent mode — dispatching implementers and reviewers — is the default all workflows assume; the full mode contract (the two-dial model as named presets plus a seat knob, including interactive) is in `references/main-agent.md §Execution Modes`.

## Skill-Load Manifest

Every dispatch loads along three axes; all apply independently. After loading a skill, follow its body's stage- and role-scoped reference load map.

1. **Role** — `superRA:implement-task` or `superRA:review-task`, named by the dispatch. A seat the main agent fills itself loads the same skill.
2. **Stage** — the workflow phase the dispatch is in (table below). Role-independent.
3. **Domain** — what the task operates on (table below). Load by what the task *touches*, not by which subtree it lives in, and load **every** domain skill that matches: a task that derives a result and writes it into the manuscript matches `theory-modeling` and `writing`, so load both.

All three load *in addition to* this skill, the one every dispatch always loads.

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


**Harness adapters:** when this skill or its references name a Claude-specific tool (`AskUserQuestion`, `Skill`, `TodoWrite`, `Agent`), consult the adapter reference for the current harness under `references/`.

**Main agents:** continue to `references/main-agent.md`.
