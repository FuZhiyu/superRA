# superRA — Contributor Guidelines

This repo is **superRA**, a fork of [Superpowers](https://github.com/obra/superpowers) adapted for economic research. It ships a complete **iterative** PLAN → IMPLEMENT → INTEGRATE workflow for AI agents acting as disciplined Research Assistants — the phases are a cycle, not a one-shot pipeline, and re-entering PLAN mid-execution or after integration is the normal case. `planning-workflow §User Feedback and Changing Plans` is the hinge that makes re-entry safe (full DAG cascade over downstream tasks, full drift-test suite always runs on re-entry, prefer updating existing task blocks over appending new ones). See `README.md` for the user-facing overview and `skills/CATEGORIES.md` for the Workflow / Domain / Utility / Meta grouping.

This file is the contributor-facing entry point. If you are modifying superRA itself — skills, hooks, agents, or internal docs — treat the work as **skill creation** and load the `skill-creator` skill alongside the superRA workflow skills before editing any `skills/*/SKILL.md`. User-facing onboarding lives in `README.md`; anything developer-internal belongs here.

## Working in This Repo

When you are modifying superRA itself (skills, hooks, agents, docs), you are editing behavior-shaping content. Treat it with care.

- **Read before you change.** Skill content has been tuned through real sessions. Understand why a piece of text exists before rewording it. Red Flags tables, rationalization lists, and the "your human partner" / RA-framing language are deliberate.
- **One problem per commit.** Keep commits focused. Don't bundle unrelated edits.
- **Describe the problem, not just the change.** Commit messages should explain what was broken or missing, not just what moved.
- **Test on at least one harness** (Claude Code is primary) before claiming a change works. Skills are code — verify behavior, don't just read the diff.

## Skill Changes

Skills are not prose. If you modify skill content:

- Edit skills directly, test on a real session in Claude Code, and iterate based on observed behavior. For upstream skill-writing guidance, see the [Superpowers project docs](https://github.com/obra/superpowers).
- Run the skill through a realistic session to confirm it triggers when it should and doesn't when it shouldn't.
- Be cautious editing carefully-tuned content (Red Flags tables, rationalization lists, RA-framing language, severity protocols). Changes here should be driven by observed failures, not stylistic preference.

## Design Principles

superRA has a tested philosophy that every skill, hook, and agent file is built around. **Evaluate every proposed change against all of these principles.** If a change weakens any of them, the commit message must justify why and what compensates. These are not stylistic — they are the load-bearing structure of the plugin.

### Workflow principles (load-bearing across all domains)

These principles are domain-agnostic. They shape every workflow skill and apply to data analysis today and to any future vertical (theory, literature review, simulation, writing) tomorrow.

1. **Enforced implementer–reviewer pair at every step.** No result is accepted until a reviewer has signed off. One comprehensive review pass per task during execution (the reviewer walks the active domain skill's gated checklist top to bottom plus any operation-conditional sections matching operations performed, and returns `APPROVE` / `REVISE`); a drift-test review, a dedicated semantic-sync review, and an integration review before merge. Review is never skipped, regardless of perceived triviality. A change that would let a step ship without review violates this principle.

   The reviewer's role is **adversarial** — it should be thorough, skeptical, and err on the side of over-flagging. A false positive costs one iteration; a missed issue can ship wrong results. The orchestrator is the **arbitrator**: it made the plan, communicates with the researcher, and has big-picture context the reviewer lacks. It evaluates each review finding independently, understands the reviewer's over-critical bias, and overrules with documented reasoning when the reviewer is wrong. Neither role works without the other — adversarial review surfaces issues, informed arbitration filters them.

2. **Handoff docs are the auditable record AND the continuation point.** All material findings, decisions, methodology notes, and results land in committed `PLAN.md` / `RESULTS.md` *before* they appear in any status report or chat message. Any fresh agent can open the repo and resume work from the docs + git state alone — no prompt history required. Atomic commits bundle code + doc edits so every git SHA reconstructs a coherent state. A change that creates out-of-doc state (findings only in chat, caveats only in reports, decisions only in dispatch prompts) violates this principle.

3. **Fast early, strict before finish. Semantic sync always.** Work is carried forward for speed during the IMPLEMENT phase — no codebase-fit checks at interim checkpoints. Codebase integration, drift tests (for data analysis) or their domain equivalent, refactoring, and documentation finalization (maturing RESULTS.md into its permanent form + auditing project-level CLAUDE.md / AGENTS.md / README.md via a dedicated doc-writer + doc-reviewer pair) happen only when the user chooses to finish, inside `integration-workflow`. Research-aware branch syncs run through `semantic-merge`, never a bare `git merge` / `rebase` / `cherry-pick`. A change that front-loads integration concerns onto interim tasks, or bypasses semantic-merge during Sync, violates this principle.

4. **Autonomous with human in the loop.** The agent drives the workflow forward under its own power between legitimate stop points. It does not ask permission to continue, re-confirm approved plans, or solicit reassurance — an `APPROVED` task dispatches the next task without a check-in, and a completed workflow step moves to the next step without a "shall I proceed?". It **does** stop, and uses the `AskUserQuestion` tool when the harness exposes it (plain text otherwise), for exactly three classes of pause: (a) a hard blocker the RA cannot resolve from the code and data (missing access, corrupted inputs, ambiguous upstream dependency), (b) a decision that is beyond the RA's authority because it belongs to the researcher — methodology choices, research intent, scope changes, sample/variable definition calls, any tradeoff where the "right" answer depends on the research question, and (c) user-defined milestones explicitly baked into a workflow (e.g., implementation-workflow Step 4's four completion options, integration-workflow's drift-test selection and doc disposition). Every user decision produced at a stop point is written into `PLAN.md` (or `RESULTS.md` where relevant) **before** the agent acts on it, and committed atomically with the work it unblocks — so the handoff doc remains the record of record and the next session can reconstruct *why* the work took the shape it did. A change that inserts gratuitous "should I continue?" prompts, decides a methodology question unilaterally, or lets a user decision live only in chat violates this principle. See `handoff-doc` §User Decisions Log for the logging format.

### RA framing (cross-cutting)

The agent is a Research Assistant implementing the researcher's ideas, not judging methodology. Challenges to methodology are escalated to the human partner, never decided unilaterally. This applies to every domain vertical.

### Architectural pattern

- **Lean agents, rich references.** Two prototype agents (implementer, reviewer) load stage-specific domain references at dispatch time. The Skill-Load Manifest in `superRA:using-superra` is the authoritative map from `Stage:` value to required skills + stage-scoped references; `agents/implementer.md` / `agents/reviewer.md` carry one-line pointers at it.
- **Composable by category.** Workflow, domain, and utility skills compose; they do not duplicate. Domain and utility skills are usable **stand-alone** outside the workflow — their language stays workflow-neutral so a researcher (or a different orchestrator) can load them directly. Workflow skills assemble these pieces at dispatch time rather than restating their content.
- **Flat `skills/` layout.** No nested subfolders — every skill lives at `skills/<name>/SKILL.md`. Grouping into Workflow / Domain / Utility / Meta is documented in `skills/CATEGORIES.md` and mirrored in `README.md`, not in the filesystem. This preserves compatibility with Claude Code, Copilot CLI, Gemini CLI, and Codex skill loaders.

### Skill Design Patterns

- **Activate `skill-creator` when editing skills.** Any agent modifying a `skills/*/SKILL.md` should have `skill-creator` (or an equivalent skill-authoring skill) loaded, alongside the superRA workflow skills. Skill writing has its own discipline (description triggers, frontmatter shape, references-one-level-deep) and this is where that discipline lives.
- **Prefer positive instructions over negative ones.** Tell the agent what to do, not what to avoid. Example: write "Describe the data before transforming it" rather than "Don't transform data without describing it first." Positive instructions are easier to follow and easier to verify.
- **Give the minimum instruction needed — skip the design reasoning.** Agents need to know *what* to do; the *why* belongs in commit messages and contributor docs, not in skill bodies. Include rationale only when it meaningfully helps the agent execute better.

  Avoid this anti-pattern:

  > This skill is **domain-agnostic**. Today's only implemented domain vertical is data analysis; future verticals (theory / modeling, literature review, simulation, writing) plug in by providing their own domain skill with a `references/planning.md`. The procedure here stays the same.

  The agent does not need to know the skill is domain-agnostic or what future verticals might look like — they only need to plan and load the plan. Design reasoning in the instruction body bloats context and dilutes the signal.
- **Agents only load what they need.** When adding a new instruction, think carefully about which agent(s) actually need it and place it where only those agents will pick it up (e.g., inside a stage-scoped reference, not in the top-level SKILL.md). Instructions that apply to one role should not be read by every role.

### Codex design

- **Canonical instructions stay shared.** Keep the authoritative workflow text in root `skills/` and the authoritative role specs in `agents/`. Do not create Codex-only copies of workflow behavior.
- **Harness differences live in adapter references.** When a workflow needs harness-specific tool naming or runtime behavior, put that in the owning adapter reference under `skills/using-superRA/references/` (for example `codex-instructions.md` or `claude-tools.md`) rather than forking the workflow skill body.
- **Direct mode reads skill-owned role references.** Main-agent direct mode loads `skills/using-superRA/references/direct-mode-implementer.md` and `direct-mode-reviewer.md`, not raw `agents/*.md`, because cross-repo plugin use cannot assume the main session can open repo-relative agent files outside the shared skill surface.
- **Direct-mode role references are generated artifacts.** `agents/implementer.md` and `agents/reviewer.md` remain canonical. `skills/codex-superra-setup/scripts/sync_codex_agents.py` generates the direct-mode role references from those canonical role specs; do not hand-edit the generated refs.
- **Codex skill discovery uses additive surfaces.** Repo-local discovery comes from `.agents/skills/` symlinks back to canonical `skills/`. Plugin packaging comes from `.codex-plugin/plugin.json`, which points directly at `./skills/`.
- **Codex named agents are generated artifacts.** `agents/implementer.md` and `agents/reviewer.md` remain canonical. The generated Codex custom-agent files live in `.codex/agents/` and are produced by `skills/codex-superra-setup/scripts/sync_codex_agents.py`, which also refreshes the generated direct-mode role references.
- **Cross-repo Codex use depends on global custom agents.** The plugin installs skills; `codex-superra-setup` installs the named agents into `~/.codex/agents/` for normal cross-repo work, or into `.codex/agents/` for repo-local testing and development.
- **Do not rely on plugin-managed agent installation.** Codex's documented plugin surface packages skills, apps, and MCP configuration; custom named agents use `.codex/agents/` or `~/.codex/agents/`.
- **Codex contributor docs live here.** `AGENTS.md` is the canonical Codex-facing filename and remains a symlink to this file. `AGENT.md` is also kept as a convenience alias pointing here so the repo exposes the same contributor guidance through either name.

### DRY, composability, extensibility

**One source of truth per concern.** When a piece of content appears in more than one skill, at most one copy is authoritative; the rest are one-line pointers. Duplicated content is a code smell and a source of drift — future edits will update one copy and miss the others. When adding content, first ask: *what concern does this describe?* Put it in the one skill that owns that concern, and reference it from everywhere else.

Concerns and their owners:

- **Workflow skills** own *choreography* — what steps run in what order, what stop points exist, what status transitions apply. `planning-workflow`, `implementation-workflow`, and `integration-workflow` each own the choreography of their phase and nothing else.
- **`agent-orchestration`** owns *cross-stage orchestration* — dispatch-prompt shape (required-fields-first, `Additionally:` anchor-last), the "Follow the standard stage-relevant workflow" prefix, the relay protocol between orchestrator and subagent (what-changed deltas, review-notes annotation mechanics), and verdict-adjudication discipline (how to handle `REVISE` findings). Execution Modes (subagent dispatch vs direct) are owned by `superRA:using-superra`.
- **Domain skills** own *domain discipline* — the Iron Law for data analysis, the gated checklist for that domain (§Three Concurrent Disciplines, domain-specific integration reference), pitfall catalogs, stage-scoped references. Adding a new vertical means adding a domain skill, not forking workflow skills.
- **`semantic-merge`** owns *techniques for semantic coherence* — intent investigation, role classification, conflict resolution, intent-changing escalation, detect-and-resolve stale references, and propagation commits landed until semantic coherence (`sync-quality.md §Scope boundary`) is reached. Also owns the workflow sync author/reviewer mode references, standalone full-merge mode, and Sync Map / impact formats.
- **`refactor-and-integrate`** owns *techniques for codebase coherence* — convention fit, utility reuse, PR-friendly diffs, Project Doc Audit walk-up, minimum net diff against the host, plus drift-test construction and propagation of task-local Sync impact obligations. Domain-specific integration content lives alongside the domain skill (for data analysis: `econ-data-analysis/references/integration.md`).
- **`handoff-doc`** owns *handoff-doc mechanics* — latest-state-only, inline-edit rule, task-block structure, `## Decisions` section shape. It does NOT own role permissions or dispatch/status-return protocols — those are orchestration concerns and live in `agent-orchestration` + the agent files.

**Shared-flow checklists.** Implementer and reviewer always walk the **same file** for any gated checklist. `[BLOCKING]` / `[ADVISORY]` markers encode severity — blocking items must be fixed to earn APPROVE; advisory items MAY be flagged as MINOR but do not block. The implementer walks the checklist as pre-handoff self-check; the reviewer walks the same checklist as verification criteria. Same content, two perspectives — no drift possible because there is no second document. Applies to `econ-data-analysis/SKILL.md` §Three Concurrent Disciplines (and conditionally the relevant §Pitfalls subsections) and to every other gated checklist in the plugin (domain-specific integration references, future vertical checklists).

**Composition at the workflow edge.** A workflow step's content is assembled at dispatch time from: (a) the workflow skill for sequencing, (b) `agent-orchestration` for dispatch shape + verdict adjudication, (c) the agent file for execution / review protocol, (d) the domain skill + stage-scoped references for what to check. None of these pieces duplicate what the others carry.

**Extension path.** Adding a new vertical (theory, literature review, simulation, writing) is composing existing pieces, not forking workflow skills. Create `skills/<vertical>/SKILL.md` with its Iron-Law-equivalent, add the vertical's gated checklist (§Review + §Integration), add stage-scoped references for the phases the vertical touches, add the vertical to the planning-workflow routing table. The workflow skills, `agent-orchestration`, and the agent files carry over unchanged.

### Domain verticals

superRA's workflow scaffolding is domain-agnostic. Domain-specific discipline lives in **domain skills**, one per vertical, each organized with stage-scoped references so the right chunk loads at the right phase.

**Currently implemented:**

- **Data analysis** — `superRA:econ-data-analysis`. Load-bearing rule: **Iron Law — NO TRANSFORMATION WITHOUT PRIOR DESCRIPTION.** Non-negotiable; protected by the Common Rationalizations table in the skill body and the inline severity-marked checklist in §Three Concurrent Disciplines. Stage-scoped references: `references/planning.md` (Data Inventory hard gate + sensitivity design), `references/integrate-drift-tests.md` (drift-test construction), `references/integration.md` (data-specific integration gates), `references/data-robustness-checklist.md`.

Data analysis is the flagship vertical, not the whole product. The workflow skills do not assume data analysis; they route to the domain skill only when the task matches.

Before proposing structural changes to skill design, workflow phases, or agent orchestration, read the existing skills in `skills/` and the workflow skills they reference, and verify the proposal strengthens (or at least preserves) all four workflow principles.

## Roadmap: Extending Beyond Data Analysis

Adding a new vertical means adding a domain skill — not forking the workflow. The four workflow principles, the implementer/reviewer pair, the handoff-doc discipline, semantic-merges, and the autonomous-with-human-in-loop stop-point pattern all carry over unchanged. A new vertical plugs in by providing:

1. **A domain skill** at `skills/<vertical>/SKILL.md` carrying the cross-cutting discipline of that domain.
2. **Stage-scoped references** inside the domain skill: at minimum a `references/planning.md` consumed by `planning-workflow` Phase 1. Other stage references as the vertical needs.
3. **A row in `skills/CATEGORIES.md` and `README.md`** under Domain.
4. **An entry in `planning-workflow` Phase 1's vertical routing table** so the workflow dispatches correctly when it sees a task in that domain.

**Planned verticals (hooks for future work, not commitments):**

- **Theory / modeling.** Derivation discipline (step-by-step algebra, symbol tracking), notation consistency, proof checks, simulation or numerical verification of derived formulas.
- **Literature review.** Citation integrity (every claim traces to a cited source with the page / line), claim-evidence mapping, coverage audit across a reading list, systematic note-taking format.
- **Simulation.** Seed discipline, stochastic reproducibility across platforms, sensitivity to parameter grids, convergence diagnostics, calibration-vs-estimation separation.
- **Writing / paper drafting.** Figure and table consistency with the underlying code, cross-reference integrity (labels, citations), narrative coherence across sections, versioning of the manuscript alongside the analysis branch.

When you pick one up, create the domain skill first, then do one real project end-to-end with the existing workflow skills to find the gaps. The workflow skills are meant to bend; the principles are not.

## General

- Keep `README.md`, `skills/CATEGORIES.md`, and the skill inventory in `superRA:using-superra` in sync when adding or renaming skills.
- Prefer editing existing skills over creating new ones. New skills should carve out a clearly distinct concern.
- Domain-specific or project-specific configuration does not belong in core superRA — publish it as a separate plugin.
