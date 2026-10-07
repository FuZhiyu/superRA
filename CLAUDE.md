# superRA — Contributor Guidelines

How contributors keep superRA's skills, hooks, harness adapters, and internal docs coherent. `README.md` owns the user-facing product model; read it first and keep that explanation there.

## Contributor Discipline

- **Treat skill edits as skill creation.** Load `skill-creator` before editing any `skills/*/SKILL.md`; load the relevant superRA workflow skills before changing workflow behavior.
- **Change one concern at a time.** One design, workflow, or harness concern per commit.
- **Describe the problem.** Commit messages and PR notes say what was broken, duplicated, rigid, or unclear.
- **Verify behavior, not just prose.** For a skill or workflow change, run at least one realistic harness session or script-level check that exercises the changed path.

## Developing Locally

Run the task-tree CLI from live source; each entry script carries a PEP 723 dependency block, so edits apply on the next run:

```bash
uv run --script skills/task-tree/scripts/cli.py task frontier
uv run --script skills/task-tree/scripts/plan_dashboard.py dashboard
uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts
```

- **uv-free fallback:** `python3 skills/task-tree/scripts/cli.py …` — the core is stdlib-only.
- **`./superRA/superra` wrapper:** prefers this checkout's `skills/task-tree`, then an installed plugin, then a GitHub clone. The resolution chain lives in `skills/task-tree/scripts/wrapper_resolver.py`.

## Releasing

- **Bump with `scripts/bump-version.sh X.Y.Z`** — it updates every manifest listed in `.version-bump.json`; `--check` reports drift.
- **Move the `## [Unreleased]` notes in `RELEASE-NOTES.md` into `## [X.Y.Z] - YYYY-MM-DD`**, directly below an empty `## [Unreleased]`. Pushing the bump to `main` creates the `vX.Y.Z` GitHub release from that section.

## Design Principles

superRA gives agents mechanisms they assemble for the current research situation, not a scenario tree for every contingency.

- **Mechanisms over contingency trees.** Prefer reusable mechanisms — task revision, stage-scoped references, dispatch templates, gated checklists — over "if this happens, do that" prose.
- **Re-entry is normal.** A phase, mechanism, or utility is enterable from different stages, re-enterable after discoveries, and skippable when the user invokes only part of the workflow.
- **Keep choreography simple.** Workflow skills state the sequence and safety stop points, then delegate domain, dispatch, and document mechanics to their owners.
- **Gates are local discipline.** Once a workflow or task is entered, its status transitions and blocking checklist items are enforced, and any review that runs enforces its gates. Whether a review runs is an execution-time call (`using-superra/references/main-agent.md` §Deciding on Review).
- **Domain and utility skills stand alone.** They may mention task files, implementers, or reviewers as optional context, but must work when loaded directly by a researcher or another orchestrator.
- **Compose at the workflow edge.** A step assembles the workflow skill, `agent-orchestration`, the role skill, the domain skill, and utilities; none restates another.
- **Put instructions where they are loaded.** Role guidance in role skills, stage guidance in stage references, cross-stage guidance in the smallest owning skill. `SKILL.md` routes to references, kept one level deep.
- **Write positive, executable instructions.** "Describe the data before transforming it," not "Do not transform data without describing it." Rationale goes in commits and PRs, not skill bodies.

### Teach the Protocol, Don't Prescribe Each Action

**This is a gate.** Every implementer editing any file under `skills/*` self-applies all three tests below line by line before committing. Every reviewer walking such a diff verifies them line by line on every pass. A line that fails any test is a `[BLOCKING]` finding, not a stylistic preference.

The bar for every line: **without this line, would the agent's behavior be unstable?** If not, delete it. Apply in order:

1. **DRY.** Already carried by another skill, reference, dispatch field, or handoff doc the agent reads: point to it, never paraphrase. A one-line echo is tolerable only when the alternative is forcing a redundant file load.
2. **Same-file restatement.** Already said earlier in this file, in any phrasing: merge into the form the section already uses, or point to the earlier line. Rewording a restatement does not pass. Test pairs: two lines that could swap positions without any fact reading as missing are one fact stated twice.
3. **Necessity.** The agent would do this unprompted by default competence: delete it. Keep only a non-default constraint, a safety invariant, a non-default load, or an ordering the agent would not infer.

Common failures:

- **Wrappers around authoritative content** — "If the dispatch includes a `Worktree:` field, follow its `Additionally:` tail."
- **"Here is what you will receive"** — describing a dispatch prompt, task file, or review blockquote to the agent that reads it.
- **Reminders of runtime defaults** — "If you are asked to load a skill, load the skill."
- **Restating the Skill-Load Manifest** or the standard Before-You-Start inside a dispatch prompt or role body.

When in doubt, delete the copy furthest from the authoritative source.

### Skill Prose Style

Writing or restyling a skill file is two passes, in order: the gate above deletes lines; then compress the survivors. Exemplars: `skills/implement-task/SKILL.md`, `skills/review-task/SKILL.md`.

- **Bolded imperative + short elaboration.** No lead-in sentence before the imperative.
- **Definition bullets over framing sentences.** Drop the sentence that announces a list; each bullet is `**term** — definition`, defaults inline: "`quick` (default): …".
- **Condition as a noun phrase, colon, action fragments.** "Unclear task structure: flag in your return, don't invent one."
- **No rationale or derivation clauses.** Keep a purpose clause only when it changes what the agent produces.
- **Trust the earlier mention.** Second references shorten; cut examples an adjacent line already carries.
- **Meaning survives verbatim.** Gates, enums, defaults, ordering constraints, and decision-carrying hedges ("usually", "only", "existing", "if any") keep their content exactly. A cut that leaves a section with no instruction went too far.

Measure the pass in words. A pass that barely moves the count compressed connectives, not clauses — redo it. Worked example: `daea6ae3..f525b63e` on `skills/review-task/SKILL.md` (12%, then a further 18% by deleting whole clauses).

### Bounded Agent-Facing Output

Hook feedback and default CLI output land in an agent's context; their size stays fixed however large the task tree gets.

- **Cap by default.** At most `OUTPUT_CAP` (`skills/task-tree/scripts/_task_validate.py`) items per group, or a tighter local cap such as `REPRO_REMINDER_CAP`. Full lists are opt-in (`--all`, `--json`).
- **Count and point.** Elided items collapse to one line with their count and the command that lists them.
- **Errors first.** Truncation never hides an error behind advisories.
- **Scope to the change.** Hooks report on what the tool call touched; whole-tree audits are an explicit command.
- **Remind once** per session or status transition (marker files).
- **Every warning has an exit** — fixing it or recording a decision clears it.

## Terminology

**"Plan" is the verb, not the noun.** "Planning" is the superplan process. Everything in `superRA/` is a **task** — top-level tasks sit directly under `superRA/`, nested tasks are their dispatchable children. Call `superRA/` "the task tree," never "the plan."

## Ownership

One source of truth per concern; other mentions point to it. Skill-level grouping lives in `skills/CATEGORIES.md`. The non-obvious owners:

| Concern | Owner |
| --- | --- |
| Skill-Load Manifest, commit format, task read/edit interface | `using-superra` |
| Execution modes, the review trigger | `using-superra/references/main-agent.md` |
| Phase choreography, stop points, status transitions | `superplan`, `superimplement`, `superintegrate`; the default interactive loop in `using-superra/references/interactive-mode.md` |
| Dispatch-prompt shape, relay, verdict adjudication | `agent-orchestration` — except the planning-review dispatch (`superplan` §Agent Review) and its reviewer mechanics (`superplan/references/planning-review.md`) |
| Role protocol and per-role task ownership | `implement-task`, `review-task` |
| Task-file contract: anatomy, status lifecycle, body sections, `## Reproduction` schema | `task-tree/references/task-file-contract.md` |
| Task-tree design: objectives, splitting, placement, replans | `superplan/references/task-tree-design.md` |
| Reproduction discipline vs. mechanics | `reproducibility` vs. `task-tree` (schema, `superra repro` CLI, hooks) |
| Task companion files | `using-superra/references/task-companion-files.md` |
| Human-facing writing | `communicate`; manuscripts add `academic-writing` |
| Harness tool names and runtime differences | adapter references under `using-superra/references/` |

## Architecture

- **Roles are skills.** A dispatch prompt names `implement-task` or `review-task`; the role skill pulls stage and domain loads through the manifest.
- **Subagents stay off tree tooling.** Outside `Stage: maturation`, subagents never load `task-tree` or `task-tree-design.md` (except `task-file-contract.md` §Reproduction Section, via `reproducibility`); `agent-orchestration` is never subagent-loaded.
- **Flat skill layout.** Every skill is `skills/<name>/SKILL.md`; grouping lives in `skills/CATEGORIES.md` and `README.md`.
- **Shared gated checklists.** Implementers and reviewers use the same checklists: `[BLOCKING]` items must be fixed for approval; `[ADVISORY]` items are recorded and never block.
- **One dispatch mechanism, all harnesses.** Spawn the harness's default agent and name the role skill in the prompt. Shared behavior lives only in root `skills/`; harness differences live in the adapter references. `AGENTS.md` and `AGENT.md` are aliases for this file.
- **Vendored assets are re-fetched.** Files under `skills/task-tree/scripts/vendor/` follow `vendor/README.md`.

## Adding or Changing Skills

- **Prefer improving an owning skill.** Add a skill only for a distinct concern.
- **Frontmatter descriptions state trigger conditions explicitly** — Codex and other harnesses discover skills by metadata.
- **Add a reference only with a clear load condition** from its `SKILL.md`; keep domain and utility skills standalone.
- **A new domain vertical** is `skills/<vertical>/SKILL.md` with its gates and stage-scoped references for the stages it touches; workflow, role, and orchestration skills carry over unchanged.
- **Keep inventories in sync** when adding, renaming, or removing a skill: `skills/CATEGORIES.md`, `README.md`, and, for domain skills, the manifest Domain table.
- **Bound any new hook message or CLI default output** per §Bounded Agent-Facing Output.
