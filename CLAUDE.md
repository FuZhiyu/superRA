# superRA — Contributor Guidelines

This file is the contributor-facing entry point for superRA internals. Read `README.md` first for the user-facing product model; keep that overview there rather than duplicating it here.

When modifying superRA itself — skills, hooks, agents, harness adapters, or internal docs — treat the work as skill creation. Load `skill-creator` before editing any `skills/*/SKILL.md`, and load the relevant superRA workflow skills before changing workflow behavior.

## Contributor Discipline

- **Read the owning files before editing.** Skill and agent text changes behavior. Understand the owning skill, its references, and the call sites that load it before rewriting.
- **Change one concern at a time.** Keep commits focused on one design, workflow, or harness concern.
- **Describe the problem.** Commit messages and PR notes should explain what was broken, duplicated, rigid, or unclear.
- **Verify behavior, not just prose.** For skill or workflow changes, run at least one realistic harness session or script-level verification that exercises the changed path.
- **Preserve user-facing/internal separation.** `README.md` explains what superRA is and why a researcher would use it. This file explains how contributors keep the internals coherent.

## Internal Design Philosophy

superRA should be adaptive and composable rather than rigid. It gives agents mechanisms and protocols they can assemble for the current research situation; it should not encode a scenario tree for every contingency.

### Adaptive, Composable Workflows

- **Mechanisms over contingency trees.** Prefer reusable mechanisms such as plan revision, stage-scoped references, dispatch templates, and gated checklists over long branches of "if this happens, then do that" workflow prose.
- **Re-entry is normal.** A phase, mechanism, or utility should be enterable from different stages, re-enterable after discoveries, and skippable when the user intentionally invokes only part of the workflow.
- **Keep choreography simple.** Workflow skills should state the sequence and stop points needed for safety, then delegate domain discipline, dispatch mechanics, and document mechanics to their owning skills.
- **Gates are local discipline.** Adaptability does not mean optional quality control. Once a workflow/task is entered, its review gates, status transitions, and blocking checklist items are enforced.
- **Domain and utility skills stand alone.** They may mention workflow artifacts such as `PLAN.md`, `RESULTS.md`, implementers, or reviewers as optional context, but their main instructions should work when loaded directly by a researcher or another orchestrator.
- **Compose at the workflow edge.** A workflow step is assembled from the workflow skill, `agent-orchestration`, the role spec, the active domain skill, and any needed utility skills. Do not restate those pieces inside each other.

### Minimal, Targeted Instructions

- **Put instructions where they are loaded.** Place role-specific guidance in role specs or role references, stage-specific guidance in stage references, and cross-stage guidance in the smallest owning skill.
- **Load only what is needed.** Top-level `SKILL.md` files should route to references instead of carrying every detail. References stay one level deep from the skill unless there is a strong reason.
- **Prefer positive instructions.** Write the action agents should take: "Describe the data before transforming it" is better than "Do not transform data without describing it first."
- **Skip design essays in skill bodies.** Skills need executable guidance. Keep rationale in contributor docs, commit messages, PRs, or short comments only when it helps the agent adapt correctly.

### Teach the Protocol, Don't Prescribe Each Action

**This is a gate.** Every implementer editing any file under `skills/*` or `agents/*` self-applies both tests below line by line before committing. Every reviewer walking such a diff verifies them line by line on every pass. A line that fails either test is a `[BLOCKING]` finding, not a stylistic preference. New instruction lines added without passing the tests are the most common source of drift in this repo, and this gate exists to block them at the edit site rather than the next audit round.

Give agents mechanisms and the evidence they need to act predictably; do not narrate what they will see, wrap authoritative content in meta-commentary, or remind them of defaults the runtime already teaches. The bar for every line of instruction is: **without this line, would the agent's behavior be unstable?** If the answer is no, delete it.

Two tests, applied in order:

1. **DRY.** If the information is already carried by another skill, reference, dispatch field, or handoff doc the agent reads, do not restate it here. A pointer is acceptable; a paraphrase is not. One-line echoes are tolerable only when the alternative is forcing a redundant file load — otherwise point and trust.
2. **Necessity.** If the instruction only tells the agent to do what it would already do with the content in front of it, delete it. Keep the line only when it shapes behavior the agent would not produce on its own (a non-default constraint, a safety invariant, a protocol step that must happen in a specific order).

**Anti-patterns to watch for:**

- **Wrapper instructions around authoritative content.** "If the dispatch includes a `Worktree:` field, follow the canned steering in its `Additionally:` tail." The canned steering is already authoritative and self-explanatory — the wrapper adds nothing and doubles the maintenance surface.
- **"Here is what you will receive" descriptions.** Explaining the shape of the dispatch prompt, the fields in `PLAN.md`, or the structure of a review blockquote to the agent that will read them. The agent reads the thing; describing it is overhead.
- **Reminders of defaults the harness or runtime already enforces.** "If you are asked to load a skill, load the skill." "Read the task before implementing it." These are not instructions; they are throat-clearing.
- **Restating the Skill-Load Manifest or standard Before-You-Start inside a dispatch prompt or role body.** The manifest is the authoritative map; repeating it invites drift.

**Keep:** behavior-shaping instructions — things like "treat paraphrased dispatch content as over-specification and go to authoritative sources," a specific non-default skill/reference load, a safety invariant, or an ordering constraint the agent would not infer.

**Maintenance cost is the tell.** Every restated rule is a place where the two copies can drift. When in doubt, delete the copy furthest from the authoritative source.

## Ownership Boundaries

Use one source of truth per concern. Duplicated behavior text is a drift risk; when content appears in more than one place, one copy must be authoritative and the others should point to it.

| Concern | Owner |
| --- | --- |
| Phase choreography, stop points, task/status transitions | `planning-workflow`, `implementation-workflow`, `integration-workflow` |
| Cross-stage orchestration, dispatch-prompt shape, relay protocol, verdict adjudication | `agent-orchestration` |
| Execution modes and Skill-Load Manifest | `using-superra` |
| Domain discipline, domain gates, pitfalls, stage-scoped domain references | The relevant domain skill, e.g. `econ-data-analysis` |
| Semantic-coherence techniques — intent investigation, role classification, conflict resolution, intent-changing escalation, stale-reference sweep, workflow/standalone sync modes, Sync Map + task-local Sync impact formats | `semantic-merge` |
| Result-protection techniques — key-result selection support, drift/regression test quality, red-green verification, expectation-update escalation | `result-protection` |
| Codebase-coherence techniques — convention fit, utility reuse, PR-friendly diffs, Project Doc Audit walk-up, minimum net diff, and supplied Sync impact as justification evidence | `refactor-and-integrate` |
| Handoff-doc mechanics, templates, stale-content rules, User Decisions Log | `handoff-doc` |
| Report formatting for figures, math, tables, and final-form markdown | `report-in-markdown` |
| Harness-specific tool names and runtime differences | Adapter references under `skills/using-superRA/references/` |
| Canonical role behavior | `agents/implementer.md` and `agents/reviewer.md` |

## Architectural Patterns

- **Lean agents, rich references.** Prototype agents carry role protocol and load stage/domain references at dispatch time. The Skill-Load Manifest in `using-superra` is the authoritative map from `Stage:` values to required skills.
- **Flat skill layout.** Every skill lives at `skills/<name>/SKILL.md`. Grouping lives in `skills/CATEGORIES.md`, `README.md`, and the skill inventory, not in nested directories.
- **Shared gated checklists.** Implementers and reviewers use the same checklist files. `[BLOCKING]` items must be fixed for approval; `[ADVISORY]` items may be reported as minor findings without blocking.
- **Generated artifacts stay generated.** Direct-mode role references and Codex named-agent files are produced from canonical agent specs. Update the generator or source spec, then regenerate.

## Skill Authoring Guidelines

- Load `skill-creator` before editing any `skills/*/SKILL.md`.
- Keep frontmatter descriptions explicit about trigger conditions; Codex and other harnesses use metadata for discovery.
- Keep `SKILL.md` concise and procedural. Move stage details, examples, checklists, and harness variants into references.
- Add references only when they have a clear load condition from `SKILL.md`.
- Preserve standalone usability for domain and utility skills.
- Add new skills only for distinct concerns. Prefer improving an owning skill when the concern already has an owner.
- Update `skills/CATEGORIES.md`, `README.md`, and the `using-superra` skill inventory when adding, renaming, or removing skills.

## Codex and Harness Design

- **Canonical instructions stay shared.** Workflow behavior lives in root `skills/`; role behavior lives in `agents/`. Do not create Codex-only copies of shared behavior.
- **Harness differences live in adapters.** Put tool-name mappings and runtime differences in the owning adapter reference under `skills/using-superRA/references/`, such as `codex-instructions.md` or `claude-tools.md`.
- **Direct mode reads skill-owned role references.** Cross-repo plugin use cannot assume raw repo-relative agent files are available, so direct mode loads the generated role references under `skills/using-superRA/references/`.
- **Codex named agents are generated.** `.codex/agents/` and global `~/.codex/agents/` files come from `skills/codex-superra-setup/scripts/sync_codex_agents.py`.
- **Surface generated artifacts in PLAN.md.** When a plan touches `skills/*` or `agents/*`, list the generated files and the generator command in the PLAN.md header so every dispatched agent knows on arrival which files must go through `sync_codex_agents.py` rather than being hand-edited. Currently generated: `skills/using-superRA/references/direct-mode-implementer.md`, `skills/using-superRA/references/direct-mode-reviewer.md`, `.codex/agents/superra_implementer.toml`, `.codex/agents/superra_reviewer.toml`.
- **Codex plugin packaging installs skills, not named agents.** `codex-superra-setup` owns named-agent installation.
- **Contributor aliases point here.** `AGENTS.md` and `AGENT.md` remain aliases for this file so Codex-facing contributor guidance has one source.

## Domain Vertical Extension

Adding a new vertical means composing existing workflow pieces with a new domain skill. Create `skills/<vertical>/SKILL.md`, add its domain discipline and gated checklists, add stage-scoped references only for stages it touches, then add the vertical to routing/inventory surfaces.

The workflow skills, agent files, orchestration skill, and generic utility skills should carry over unchanged unless the new vertical exposes a genuinely generic gap.

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
