---
title: "task-tree"
status: not-started
depends_on:  []
---

## Objective

The task tree keeps your project's state — what each task is for, how far it got, and what it found — in files under `superRA/` instead of the chat. Git versions it with your code, so a fresh session, a coauthor, or you a week later resumes from the files. The dashboard is how you read and steer it; this site is one.

[Open the example study's dashboard →](showcase-analysis-tree.html)

## Ask in plain language

The agent maintains the tree; you rarely touch a command.

| Say | You get |
|---|---|
| "superra, plan this analysis" | The work broken into a tree of tasks for you to review |
| "open the dashboard" | The live view of the tree in your browser |
| "what can I start now?" | The **frontier**: unfinished tasks whose prerequisites are met |
| "what's blocking the merge?" | An answer read from recorded state, not guessed |
| "drop this task" / "park this task" | The task set to `archived` / `postponed` |
| "which results does this edit affect?" | The steps of the reproduction graph that would go stale |

## Each task is a directory holding a `task.md`

Nesting a directory nests the task. There is no database: the tree is plain Markdown beside your code.

```text
my-project/
├── code/  data/               # your project, laid out as before
└── superRA/
    ├── superra                # the command wrapper the agent writes on first use
    ├── task.md                # optional: conventions every task inherits
    └── showcase-analysis/
        ├── task.md            # parent: status computed from its children
        ├── 01-data/task.md
        ├── 02-analysis/
        │   ├── task.md
        │   └── attachments/   # figures and scripts only this task uses
        └── 03-writeup/task.md
```

- **`depends_on` decides order.** It names the sibling tasks that must finish first; number prefixes such as `01-` only set display order.
- **A parent's status is computed from its children,** never set by hand.

### The task file holds the goal you agree on and the results the agent writes

```markdown
---
title: "Filter Sample"
status: not-started
depends_on:
  - 01-sample-design
---

## Objective

Drop observations before 2000 and require non-missing returns.

## Results

### Key Findings
- Retained 3.8 M of 4.7 M rows after applying filters.
```

Frontmatter has three fields — `title`, `status`, `depends_on` — and the tooling drops any other key. Each body section has one owner:

| Section | Written by | Holds |
|---|---|---|
| `## Objective` | Planner; you review and edit | The goal. Binding: a reviewer rejects work that violates it, so mark exploratory work as open-ended ("explore", "propose options"). |
| `## Details` | Planner, optional | Leads worth passing on: candidate files, data quirks, a suggested route. Never binding, never inherited. |
| `## Reproduction` | Implementer | The commands that produce the task's results, as steps of the reproduction graph below. |
| `## Results` | Implementer | Findings and their evidence. Redoing the task replaces them; [INTEGRATE](#/05-workflows/03-integrate) later distills them. |
| `## Review Notes` | Reviewer | Open findings while the task is at `revise`; the review's depth and any open advisories once `approved`. |

- **Subtasks inherit every ancestor's full `## Objective`.** Put a shared rule — a sample definition, a naming convention — on the lowest task it governs. When the rule already lives in `CLAUDE.md` or a data README, write one line pointing there instead of copying it.
- **Steer by rewriting in place.** Edit the objective to say what it should be now, with no strikethroughs or "Update:" lines; git keeps the history. Widening a finished task's objective reopens it.

Every field and section rule is in the [task-file contract](skills/task-tree/references/task-file-contract.md).

### A task keeps its own supporting files in `attachments/`

A **companion file** is a file one task needs to produce, check, or explain its own results, and nothing else reads: the exploratory script behind a finding, a notebook, a figure, a one-off validation. It lives in the task's `attachments/` folder and travels with the task, so the evidence for a result sits beside the result without cluttering your project.

- **Every companion is recorded.** It is committed and linked from the task's `## Results` with the command that made it, so the result can be reproduced. Output that exists only in a live session, with no saved script, is not kept.
- **A companion becomes a project file once something else uses it.** When another task or the pipeline needs it, the agent moves it to the project's usual path and updates the links.
- **At integration, each companion is kept, moved with the task that absorbs its results, or dropped** once superseded; a file supporting a protected result is never dropped.

Two other kinds of file sit outside the task: scratch from a quick check stays outside `superRA/` and uncommitted, and pipeline code, data other tasks read, and promised deliverables live at the project's usual paths.

The rules are in [task-companion-files.md](skills/using-superra/references/task-companion-files.md).

## Status shows where each task stands

Agents move each leaf task through implementation and review:

```text
not-started → in-progress → implemented → approved
                                        ↘ revise → implemented → approved
```

- **`implemented`** means done with approval still open — a review is running or deferred. **`revise`** means a reviewer sent it back with findings.
- **`archived`** drops a task and its subtree from the active tree; **`postponed`** parks it and blocks its dependents until you set it back to `not-started`.
- **A parent's status summarizes its children's.** Archived and postponed children are left out. The parent is `approved` when every child is approved, and `revise` when any child is in `revise`. Otherwise it is `implemented` once every child is done, `in-progress` once any child has started, and `not-started` before that. When a task's status changes, every task above it updates.
- **The frontier is what to work on next:** unfinished leaf tasks whose prerequisites are `implemented`, `approved`, or `revise`. Being ready says nothing about whether a task's inputs are current; that is the reproduction graph's job.

The exact rollup and frontier rules are in the [task-file contract](skills/task-tree/references/task-file-contract.md#effective-dependencies).

## The dashboard is a live view of the tree

Ask the agent to "open the dashboard"; it starts a local server and refreshes as agents edit the tree. One server serves every git worktree of the repo, one per tab.

### Tree view: read tasks and their results

![The live Tree view mid-study: the data task approved, the analysis task implemented with its review decision open, the writeup in progress, and the analysis task's objective with its math in the reading pane. Each row counts its build steps by state.](../../02-quickstart/attachments/showcase-tree.webp)

- **The sidebar is the task hierarchy** with status pills: green `approved`, yellow `implemented`, red `revise`, blue `in-progress`, grey `not-started`. Each row counts its reproduction steps by state.
- **The reading pane renders the task file** — math, tables, embedded figures — and its attachments.
- **Search and filters** narrow the tree by text, task, or status. The address bar tracks the open task, so a link opens that task.

### Graph view: see what produces what

![The live Graph view after an edit to 02_analysis.py: build-panel reads fresh, estimate-test-plot reads stale with a hover card naming the changed file, and check-grs-headline reads stale through it. Task and step cards carry Build buttons; the analysis task's figures fill the reading pane.](../../02-quickstart/attachments/showcase-graph.webp)

- **Each task is a card;** expand it to show its child tasks and reproduction steps.
- **Solid arrows are files passed between steps; dashed arrows are `depends_on` prerequisites.**
- **Hover a step that is not fresh** to see why; select it for its inputs, outputs, last run, and any acceptance reason.

### Steer and act from the live page

- **Pin a comment.** The `+` beside any block of a task opens a comment — a correction, question, or constraint. The next agent on that task sees it inline when it reads the task; resolve it once addressed.
- **Open files.** On your own machine, file links and **Open** buttons hand a file to its default application, and **VS Code** opens the task's `task.md` (set `SUPERRA_EDITOR`, for example to `cursor`, for a VS Code fork). From any machine, hover a file link for its size and a preview.
- **Build.** Each task and step card has a **Build** button that reruns what is out of date, showing the command and a time estimate from past runs first.

### Share a snapshot as one HTML file

Say "export the dashboard to a file I can send". The export holds the tree, task bodies, math, images, and graph, and opens in any browser with no superRA install, server, or repo; it has no Build, Open, or comment controls.

- **Everything in a task body is in the export.** On a public project, keep subject IDs, private group names, query results, and internal paths out of task bodies.
- **To publish one per push,** `./superRA/superra dashboard artifact setup` installs a GitHub Actions workflow that uploads each branch's export.

## The reproduction graph shows which results are still current

Each task that produces results declares, in its `## Reproduction` section, the commands that produce them. Each command is a **step** that reads input files and writes output files. superRA records what each step read and wrote at its last successful run, and links steps wherever one reads a file another writes. Together the steps form the reproduction graph the Graph view draws.

- **A step is `fresh` while its files and command match its last run.** Any change — your edit, a coauthor's pull, a hand rerun — makes it `stale`, and everything downstream with it. Other states mark a step never built (`missing`), a failed last run (`failed`), or a file this machine cannot check, such as an online-only Dropbox file (`unverified`).
- **The state is separate from workflow status,** so an `approved` task can hold a stale step.
- **Nothing reruns until you or the agent asks.** The agent rebuilds cheap steps, asks before costly ones, and can accept a result without rerunning when the diff cannot move it, such as a comment-only edit.

On a step card, the border and label show the state a build acts on; the fill shows the step's own evidence:

- **Tinted:** the step's own files changed, so the tint marks where staleness starts.
- **Empty:** stale only through an upstream step (labelled `stale · upstream`); it reruns only if rebuilding its producers changes its inputs.
- **Hatched:** some of its files are online-only here, so it reads `unverified`.

The [reproducibility page](#/04-utility-skills/09-reproducibility) walks through an edit to the example study, what a build runs, and when a result is accepted; the [`reproducibility`](skills/reproducibility/SKILL.md) skill owns when to register, rerun, or accept a step.

## The few commands worth knowing

Everything runs through the committed wrapper `./superRA/superra`. The agent runs the rest of the command set for you, and a [hook](#/06-hooks) validates the tree after every agent edit.

```bash
./superRA/superra dashboard                                  # start the live view, or reuse a running one
./superRA/superra dashboard stop                             # shut it down
./superRA/superra dashboard export --output dashboard.html   # write a shareable snapshot
./superRA/superra repro status .                             # every step's state
./superRA/superra repro build <task> --dry-run               # what a build would run, and its last cost
```

- **Edit a field directly; restructure through the agent.** Fix an objective, or drop or park a leaf by setting its status, in its `task.md`. To move or rename a task, ask the agent: `task move` carries the directory and repairs links and dependencies.
- **Every command and flag** is in [commands.md](skills/task-tree/references/commands.md); the full skill is [`task-tree`](skills/task-tree/SKILL.md).
