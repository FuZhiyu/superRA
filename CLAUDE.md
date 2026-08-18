# superRA — Contributor Guidelines

This file is the contributor-facing entry point for superRA internals. Read `README.md` first for the user-facing product model; keep that overview there rather than duplicating it here.

When modifying superRA itself — skills, hooks, harness adapters, or internal docs — treat the work as skill creation. Load `skill-creator` before editing any `skills/*/SKILL.md`, and load the relevant superRA workflow skills before changing workflow behavior.

## Contributor Discipline

- **Read the owning files before editing.** Skill and agent text changes behavior. Understand the owning skill, its references, and the call sites that load it before rewriting.
- **Change one concern at a time.** Keep commits focused on one design, workflow, or harness concern.
- **Describe the problem.** Commit messages and PR notes should explain what was broken, duplicated, rigid, or unclear.
- **Verify behavior, not just prose.** For skill or workflow changes, run at least one realistic harness session or script-level verification that exercises the changed path.
- **Preserve user-facing/internal separation.** `README.md` explains what superRA is and why a researcher would use it. This file explains how contributors keep the internals coherent.

## Local Task-Tree CLI Development

When developing this checkout, run the task-tree CLI from the live source via `uv run --script` on the loose entry scripts (there is no installable package; each entry script carries a PEP 723 dependency block):

```bash
uv run --script skills/task-tree/scripts/cli.py task frontier
uv run --script skills/task-tree/scripts/plan_dashboard.py dashboard
```

`uv run --script` is script-scoped: it never provisions this repo's environment and reflects source edits on the next run with no cache-bust. The core is stdlib-only (lazy `pyyaml`), so `python3 skills/task-tree/scripts/cli.py …` works as a uv-free fallback. The optional repo-local wrapper `./superRA/superra` follows the same rule by resolving the task-tree source — preferring this checkout's `skills/task-tree`, then an installed Claude/Codex plugin, then a shallow GitHub clone — and running the resolved entry script via `uv run --script` (python3 fallback); the resolution chain and run-line are single-sourced in `skills/task-tree/scripts/wrapper_resolver.py`. To run the test suite, supply its deps with `--with`, e.g. `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts`.

## Internal Design Philosophy

superRA should be adaptive and composable rather than rigid. It gives agents mechanisms and protocols they can assemble for the current research situation; it should not encode a scenario tree for every contingency.

### Adaptive, Composable Workflows

- **Mechanisms over contingency trees.** Prefer reusable mechanisms such as plan revision, stage-scoped references, dispatch templates, and gated checklists over long branches of "if this happens, then do that" workflow prose.
- **Re-entry is normal.** A phase, mechanism, or utility should be enterable from different stages, re-enterable after discoveries, and skippable when the user intentionally invokes only part of the workflow.
- **Keep choreography simple.** Workflow skills should state the sequence and stop points needed for safety, then delegate domain discipline, dispatch mechanics, and document mechanics to their owning skills.
- **Gates are local discipline.** Adaptability does not mean optional quality control. Once a workflow/task is entered, its status transitions and blocking checklist items are enforced, and a review that runs enforces its gates. Whether an independent review runs at all is an execution-time call — see the triggers in `using-superra/references/main-agent.md` §Deciding on Review.
- **Domain and utility skills stand alone.** They may mention workflow artifacts such as `PLAN.md`, `RESULTS.md`, implementers, or reviewers as optional context, but their main instructions should work when loaded directly by a researcher or another orchestrator.
- **Compose at the workflow edge.** A workflow step is assembled from the workflow skill, `agent-orchestration`, the role skill, the active domain skill, and any needed utility skills. Do not restate those pieces inside each other.

### Minimal, Targeted Instructions

- **Put instructions where they are loaded.** Place role-specific guidance in the role skills, stage-specific guidance in stage references, and cross-stage guidance in the smallest owning skill.
- **Load only what is needed.** Top-level `SKILL.md` files should route to references instead of carrying every detail. References stay one level deep from the skill unless there is a strong reason.
- **Prefer positive instructions.** Write the action agents should take: "Describe the data before transforming it" is better than "Do not transform data without describing it first."
- **Skip design essays in skill bodies.** Skills need executable guidance. Keep rationale in contributor docs, commit messages, PRs, or short comments only when it helps the agent adapt correctly.

### Teach the Protocol, Don't Prescribe Each Action

**This is a gate.** Every implementer editing any file under `skills/*` self-applies all three tests below line by line before committing. Every reviewer walking such a diff verifies them line by line on every pass. A line that fails any test is a `[BLOCKING]` finding, not a stylistic preference. New instruction lines added without passing the tests are the most common source of drift in this repo, and this gate exists to block them at the edit site rather than the next audit round.

Give agents mechanisms and the evidence they need to act predictably; do not narrate what they will see, wrap authoritative content in meta-commentary, or remind them of defaults the runtime already teaches. The bar for every line of instruction is: **without this line, would the agent's behavior be unstable?** If the answer is no, delete it.

Three tests, applied in order — each asks "what's actually new here?" against a different source of already-known:

1. **DRY.** Already carried by another skill, reference, dispatch field, or handoff doc the agent reads: do not restate it here. A pointer is acceptable; a paraphrase is not. One-line echoes are tolerable only when the alternative is forcing a redundant file load — otherwise point and trust.
2. **Same-file restatement.** Already said earlier in this file, in any phrasing — a bullet re-deriving a test the file states elsewhere, two sentences giving the same inclusion rule once as a definition and again as a rejection test: merge into whichever form the section already uses, or point to the earlier line. A restatement in new words is exactly as cuttable as a verbatim repeat; compressing its wording without cutting it doesn't pass this test. Find candidates by testing pairs: two lines that could swap positions without any fact reading as missing are one fact stated twice.
3. **Necessity.** The agent would already do this unprompted, with no upstream line to point at — just default competence: delete it. Keep the line only when it shapes behavior the agent would not produce on its own (a non-default constraint, a safety invariant, a protocol step that must happen in a specific order).

**Anti-patterns to watch for:**

- **Wrapper instructions around authoritative content.** "If the dispatch includes a `Worktree:` field, follow the canned steering in its `Additionally:` tail." The canned steering is already authoritative and self-explanatory — the wrapper adds nothing and doubles the maintenance surface.
- **"Here is what you will receive" descriptions.** Explaining the shape of the dispatch prompt, the fields in `PLAN.md`, or the structure of a review blockquote to the agent that will read them. The agent reads the thing; describing it is overhead.
- **Reminders of defaults the harness or runtime already enforces.** "If you are asked to load a skill, load the skill." "Read the task before implementing it." These are not instructions; they are throat-clearing.
- **Restating the Skill-Load Manifest or standard Before-You-Start inside a dispatch prompt or role body.** The manifest is the authoritative map; repeating it invites drift.

**Keep:** behavior-shaping instructions — things like "treat paraphrased dispatch content as over-specification and go to authoritative sources," a specific non-default skill/reference load, a safety invariant, or an ordering constraint the agent would not infer.

**Maintenance cost is the tell.** Every restated rule is a place where the two copies can drift. When in doubt, delete the copy furthest from the authoritative source.

## Terminology

**"Plan" is the verb, not the noun.** "Planning" refers to the superplan process — scoping and decomposing work. Everything in `superRA/` is a **task** — top-level tasks sit directly under `superRA/`, nested tasks are their dispatchable children. `superRA/` is "the task tree," not "the plan." There is no separate "plan" artifact type. Use "task tree" when referring to the `superRA/` artifact, "planning" when referring to the process.

## Ownership Boundaries

Use one source of truth per concern. Duplicated behavior text is a drift risk; when content appears in more than one place, one copy must be authoritative and the others should point to it.

| Concern | Owner |
| --- | --- |
| Phase choreography, stop points, task/status transitions | `superplan`, `superimplement`, `superintegrate`; default IMPLEMENT choreography in `using-superra/references/interactive-mode.md` |
| Planning-review reviewer mechanics (mode, verdict, note ownership at `Stage: planning-review`) | `skills/superplan/references/planning-review.md`; the planning-review **dispatch template** lives in `superplan` SKILL.md §Agent Review, with the design-decision context to provision in `thorough-planning.md` §Planning Review |
| Cross-stage orchestration, generic dispatch-prompt shape, relay protocol, verdict adjudication | `agent-orchestration` (the `Stage: planning-review` dispatch is the exception — see the Planning-review row) |
| Skill-Load Manifest | `using-superra` |
| Execution modes, the review trigger, and the interactive canvas loop | `using-superra/references/main-agent.md` (§Execution Modes, §Deciding on Review) and `references/interactive-mode.md` |
| Domain discipline, domain gates, pitfalls, stage-scoped domain references — including, for `theory-modeling`, both creation-time four-gate discipline and task-level rewriting and document-internal coherence (objective-first structural rewriting, per-step local obviousness, notation/prior-result reuse, reader-perspective discipline) | The relevant domain skill, e.g. `econ-data-analysis` or `theory-modeling` |
| Semantic-coherence techniques — intent investigation, role classification, conflict resolution, intent-changing escalation, stale-reference sweep, workflow/standalone sync modes, task-local `## Sync Impact` format (temporary) | `semantic-merge` |
| Result-protection techniques — key-result selection support, drift/regression test quality, red-green verification, expectation-update escalation | `result-protection` |
| Codebase-coherence techniques — convention fit, utility reuse, consolidation toward host conventions, PR-friendly diffs, Project Doc Audit walk-up, minimum net diff, and supplied Sync impact as justification evidence | `refactor-and-integrate` |
| Universal task read/edit interface — read a task with injected context, edit mechanics, per-role ownership | `using-superra` (§Task Interface) and each role skill's §Self-Check |
| Human-facing communication — selection, pyramid structure, rewriting, distillation, review, and Markdown mechanics | `communicate`; academic manuscripts compose it with `academic-writing` |
| Task-local companion-file lifecycle — classify, reproduce, promote, mature | `using-superra/references/task-companion-files.md` |
| Tree tooling — concepts, query/frontier/DAG, dashboard, migration; full mutation command surface | `task-tree/SKILL.md` (load-on-demand), commands in `references/commands.md` |
| Task-tree design — objective/guidance writing, splitting, placement, durable homes, scope expansion, update-task lifecycle, context distillation, retroactive task-tree creation | `superplan` (references/task-tree-design.md) |
| Task-file contract — anatomy, field notes, results shape, status enum/lifecycle, body-section vocabulary, stale-content rules, planner-owned fields | `task-tree` (references/task-file-contract.md) |
| Harness-specific tool names and runtime differences | Adapter references under `skills/using-superra/references/` |
| Canonical role behavior, including each role's concrete task ownership (what it owns + status transitions) | `skills/implement-task` and `skills/review-task` |

## Architectural Patterns

- **Roles are skills.** A dispatch prompt names the role skill (`implement-task` / `review-task`); that skill carries the role protocol and pulls the stage/domain loads. The Skill-Load Manifest in `using-superra` is the authoritative map from role, `Stage:` value, and task domain to required skills.
- **Flat skill layout.** Every skill lives at `skills/<name>/SKILL.md`. Grouping lives in `skills/CATEGORIES.md` and `README.md`, not in nested directories.
- **Shared gated checklists.** Implementers and reviewers use the same checklist files. `[BLOCKING]` items must be fixed for approval; `[ADVISORY]` items are recorded and never block.
- **Vendored assets are re-fetched, not generated.** CDN-mirrored third-party files under `skills/task-tree/scripts/vendor/` are hand-managed and re-fetchable per their own `vendor/README.md`; do not treat them as generated-from-spec.

## Agent Load Surface

What each agent loads in a session. This section documents the architecture for contributors auditing instruction weight; the **Skill-Load Manifest in `using-superra` remains the authoritative runtime map** — change behavior there, not here. "Mandatory" = required by the workflow, a frontmatter autoload, or a hook; "typical" = most sessions, conditional on the work.

**Main agent (orchestrator):**

| Load | When | Weight |
|---|---|---|
| `using-superra` + `communicate` + `using-superra/references/main-agent.md` | session start (`using-superra` hook-reminded on any superRA mention; `communicate` required before human-facing writes) | Mandatory |
| Phase workflow skill (`superplan` / `superintegrate`) | phase entry | Mandatory |
| `using-superra/references/interactive-mode.md` | executing a task in the default interactive mode | Typical |
| `superimplement` | autonomous execution, on researcher request or an accepted recommendation | On demand |
| `agent-orchestration` | before writing any dispatch prompt; hook-gated for `superimplement`/`superintegrate` (`superplan` and the interactive loop are ungated — each instructs the load at its own dispatch point) | Mandatory when dispatching |
| One `superintegrate/references/<step>.md` | INTEGRATE step entry (protect / sync / integrate / mature-consolidate / finish) | Mandatory per step |
| `task-tree` | session-start wrapper + dashboard, tree surgery, migration | Typical |
| Domain skill(s) per the manifest | when the work touches that domain | Typical |
| `superplan/references/task-tree-design.md` | planning, replan, consolidation screening | Typical |
| `agent-orchestration/references/parallel-dispatch.md` | only when parallel-dispatching or isolating a worktree | On demand |

**Dispatched subagent (implementer / reviewer):**

| Load | How | Weight |
|---|---|---|
| Role skill (`implement-task` / `review-task`) | dispatch-prompt load line | Mandatory |
| `using-superra` + `communicate` | role-skill §Before You Start load instruction | Mandatory |
| Stage reference per the manifest `Stage:` row | manifest | Mandatory when the row lists one |
| Domain skill(s) per the manifest | manifest | Typical |
| Helper skills named in the dispatch `Additionally:` line or the task's ancestor chain | dispatch | On demand |

Outside `Stage: maturation`, subagents never load `task-tree`, `task-file-contract.md`, or `task-tree-design.md`: their task-file interface is `using-superra` §Task Interface plus their role skill, and the tree references serve tree deciders — the planner and the main agent. Maturation dispatches are the exception because that stage's work *is* tree work; its manifest row loads `task-tree` and `superplan` into the subagent. `agent-orchestration` is never subagent-loaded.

## Skill Authoring Guidelines

- Load `skill-creator` before editing any `skills/*/SKILL.md`.
- Keep frontmatter descriptions explicit about trigger conditions; Codex and other harnesses use metadata for discovery.
- Keep `SKILL.md` concise and procedural. Move stage details, examples, checklists, and harness variants into references.
- Add references only when they have a clear load condition from `SKILL.md`.
- Preserve standalone usability for domain and utility skills.
- Add new skills only for distinct concerns. Prefer improving an owning skill when the concern already has an owner.
- Update `skills/CATEGORIES.md`, `README.md`, and (for domain skills) the `using-superra` Skill-Load Manifest Domain table when adding, renaming, or removing skills.

### Skill Prose Style

Skill prose is terse. Writing or restyling a skill file is two passes, in order: the §Teach the Protocol gate deletes lines; then compress the survivors. The moves, from the accepted exemplars (`skills/implement-task/SKILL.md`, `skills/review-task/SKILL.md`):

- **Bolded imperative + short elaboration.** The bold states the action; what follows sharpens it. No lead-in sentence before the imperative.
- **Definition bullets over framing sentences.** Delete the sentence that announces a list ("Two dispatch fields set the pass:"); each bullet is `**term** — definition`, defaults inline: "`quick` (default): …".
- **Condition as a noun phrase, colon, action fragments.** "Unclear task structure: flag in your return, don't invent one" — not "Flag unclear task structure in your return rather than inventing one."
- **No rationale or derivation clauses.** State the action. Keep a purpose clause only when it changes what the agent produces ("…so the next reader knows what wasn't covered").
- **Trust the earlier mention.** Second reference shortens: "keep the `→ implemented: ...` annotation" becomes "keep the annotation". Cut examples and parentheticals whose content an adjacent line already carries.
- **Meaning survives verbatim.** Gates, enums, defaults, and ordering constraints keep their content exactly; so do decision-carrying hedges and qualifiers ("usually", "only", "existing", "if any") — a hedge that carries a decision branch is protocol content, not filler. Compress wording only, and keep the imperative verb: a cut that leaves a section body with no instruction went too far.

Measure the pass in words, not lines. Worked example: `daea6ae3..f525b63e` on `skills/review-task/SKILL.md` — the first commit restyled the surface and cut 12% of words; the accepted second pass cut another 18% by deleting whole clauses, with no protocol loss. A pass that barely moves the word count compressed connectives, not clauses — redo it.

## Codex and Harness Design

- **Canonical instructions stay shared.** Workflow and role behavior both live in root `skills/`. Do not create Codex-only copies of shared behavior.
- **Harness differences live in adapters.** Put tool-name mappings and runtime differences in the owning adapter reference under `skills/using-superra/references/`, such as `codex-instructions.md`.
- **One dispatch mechanism, both harnesses.** Both spawn the harness's default agent and let the dispatch prompt name the role skill. There are no named custom agents to generate or install; `.codex/agents/` is not a superRA surface.
- **Surface generated artifacts in the task tree.** When a task touches a generated file, list it and its generator command in the relevant `superRA/` task file so every dispatched agent knows on arrival which files must go through the generator rather than being hand-edited. No agent-facing files are generated today.
- **Contributor aliases point here.** `AGENTS.md` and `AGENT.md` remain aliases for this file so Codex-facing contributor guidance has one source.

## Domain Vertical Extension

Adding a new vertical means composing existing workflow pieces with a new domain skill. Create `skills/<vertical>/SKILL.md`, add its domain discipline and gated checklists, add stage-scoped references only for stages it touches, then add the vertical to routing/inventory surfaces.

The workflow skills, role skills, orchestration skill, and generic utility skills should carry over unchanged unless the new vertical exposes a genuinely generic gap.

## Design Audit Checklist

Before proposing structural changes to skills, workflow phases, or agent orchestration, check:

- Does this duplicate README-owned user-facing explanation?
- Does this duplicate behavior already owned by another skill or reference?
- Can the mechanism be entered, re-entered, or used standalone where appropriate?
- Are gates still enforced once a workflow/task is entered?
- Is the instruction placed where only the agents/stages that need it will load it?
- For every line you added, does removing it change what the agent would *do*, or only what it would *understand*? If only understand, delete it.
- Is any harness-specific behavior isolated in an adapter reference?
- Are generated files left untouched or regenerated from their sources?
- Are inventories and category docs kept in sync?
