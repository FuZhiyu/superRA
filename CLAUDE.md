# superRA — Contributor Guidelines

This repo is **superRA**, a fork of [Superpowers](https://github.com/obra/superpowers) adapted for economic research. It ships a complete PLAN → IMPLEMENT → VALIDATE → INTEGRATE workflow for AI agents acting as disciplined Research Assistants. See `README.md` for the full skill inventory and `skills/CATEGORIES.md` for the Workflow / Domain / Utility / Meta grouping.

## Working in This Repo

When you are modifying superRA itself (skills, hooks, agents, docs), you are editing behavior-shaping content. Treat it with care.

- **Read before you change.** Skill content has been tuned through real sessions. Understand why a piece of text exists before rewording it. Red Flags tables, rationalization lists, and the "your human partner" / RA-framing language are deliberate.
- **One problem per commit.** Keep commits focused. Don't bundle unrelated edits.
- **Describe the problem, not just the change.** Commit messages should explain what was broken or missing, not just what moved.
- **Test on at least one harness** (Claude Code is primary) before claiming a change works. Skills are code — verify behavior, don't just read the diff.

## Skill Changes

Skills are not prose. If you modify skill content:

- Use `superRA:writing-skills` to develop and test changes.
- Run the skill through a realistic session to confirm it triggers when it should and doesn't when it shouldn't.
- Be cautious editing carefully-tuned content (Red Flags tables, rationalization lists, RA-framing language, severity protocols). Changes here should be driven by observed failures, not stylistic preference.

## Design Principles

superRA has a tested philosophy that every skill, hook, and agent file is built around. **Evaluate every proposed change against all of these principles.** If a change weakens any of them, the commit message must justify why and what compensates. These are not stylistic — they are the load-bearing structure of the plugin.

### Workflow principles (load-bearing across all domains)

These principles are domain-agnostic. They shape every workflow skill and apply to data analysis today and to any future vertical (theory, literature review, simulation, writing) tomorrow.

1. **Enforced implementer–reviewer pair at every step.** No result is accepted until a reviewer has signed off. Two-stage review (data integrity then implementation correctness) during execution; a drift-test review and an integration review before merge; a fresh integration review after semantic-merge. Review is never skipped, regardless of perceived triviality. A change that would let a step ship without review violates this principle.

   The reviewer's role is **adversarial** — it should be thorough, skeptical, and err on the side of over-flagging. A false positive costs one iteration; a missed issue can ship wrong results. The orchestrator is the **arbitrator**: it made the plan, communicates with the researcher, and has big-picture context the reviewer lacks. It evaluates each review finding independently, understands the reviewer's over-critical bias, and overrules with documented reasoning when the reviewer is wrong. Neither role works without the other — adversarial review surfaces issues, informed arbitration filters them.

2. **Handoff docs are the auditable record AND the continuation point.** All material findings, decisions, methodology notes, and results land in committed `PLAN.md` / `RESULTS.md` *before* they appear in any status report or chat message. Any fresh agent can open the repo and resume work from the docs + git state alone — no prompt history required. Atomic commits bundle code + doc edits so every git SHA reconstructs a coherent state. A change that creates out-of-doc state (findings only in chat, caveats only in reports, decisions only in dispatch prompts) violates this principle.

3. **Fast early, strict before merge. Semantic merges always.** Work is carried forward for speed during the IMPLEMENT phase — no codebase-fit checks at interim checkpoints. Codebase integration, drift tests (for data analysis) or their domain equivalent, refactoring, and documentation finalization (maturing RESULTS.md into its permanent form + auditing project-level CLAUDE.md / AGENTS.md / README.md via a dedicated doc-writer + doc-reviewer pair) happen only when the user chooses to merge, inside `integration-workflow`. Every merge into main runs through `semantic-merge`, never a bare `git merge` / `rebase` / `cherry-pick`. A change that front-loads integration concerns onto interim tasks, or bypasses semantic-merge, violates this principle.

4. **Autonomous with human in the loop.** The agent drives the workflow forward under its own power between legitimate stop points. It does not ask permission to continue, re-confirm approved plans, or solicit reassurance — an `APPROVED` task dispatches the next task without a check-in, and a completed workflow step moves to the next step without a "shall I proceed?". It **does** stop, and uses the `AskUserQuestion` tool when the harness exposes it (plain text otherwise), for exactly three classes of pause: (a) a hard blocker the RA cannot resolve from the code and data (missing access, corrupted inputs, ambiguous upstream dependency), (b) a decision that is beyond the RA's authority because it belongs to the researcher — methodology choices, research intent, scope changes, sample/variable definition calls, any tradeoff where the "right" answer depends on the research question, and (c) user-defined milestones explicitly baked into a workflow (e.g., execution-workflow Step 4's four completion options, integration-workflow's drift-test selection and doc disposition). Every user decision produced at a stop point is written into `PLAN.md` (or `RESULTS.md` where relevant) **before** the agent acts on it, and committed atomically with the work it unblocks — so the handoff doc remains the record of record and the next session can reconstruct *why* the work took the shape it did. A change that inserts gratuitous "should I continue?" prompts, decides a methodology question unilaterally, or lets a user decision live only in chat violates this principle. See `handoff-doc` §User Decisions Log for the logging format.

### RA framing (cross-cutting)

The agent is a Research Assistant implementing the researcher's ideas, not judging methodology. Challenges to methodology are escalated to the human partner, never decided unilaterally. This applies to every domain vertical.

### Architectural pattern

- **Lean agents, rich references.** Two prototype agents (implementer, reviewer) load stage-specific domain references at dispatch time. One source of truth per concern — protocol skills redirect to agent files, workflow skills delegate to reference files, duplicated content is a code smell. When adding content, first ask where its authoritative home already is.
- **Flat skills/ layout.** No nested subfolders — every skill lives at `skills/<name>/SKILL.md`. Grouping into Workflow / Domain / Utility / Meta is documented in `skills/CATEGORIES.md` and mirrored in `README.md`, not in the filesystem. This preserves compatibility with Claude Code, Copilot CLI, Gemini CLI, and Codex skill loaders.

### Domain verticals

superRA's workflow scaffolding is domain-agnostic. Domain-specific discipline lives in **domain skills**, one per vertical, each organized with stage-scoped references so the right chunk loads at the right phase.

**Currently implemented:**

- **Data analysis** — `superRA:econ-data-analysis`. Load-bearing rule: **Iron Law — NO TRANSFORMATION WITHOUT PRIOR DESCRIPTION.** Non-negotiable; protected by Red Flags tables and rationalization lists in the skill body. Stage-scoped references: `references/planning.md` (Data Inventory hard gate + sensitivity design), `references/integrate-drift-tests.md` (drift-test construction), `references/data-robustness-checklist.md`.

Data analysis is the flagship vertical, not the whole product. The workflow skills do not assume data analysis; they route to the domain skill only when the task matches.

Before proposing structural changes to skill design, workflow phases, or agent orchestration, read the existing skills in `skills/` and the workflow skills they reference, and verify the proposal strengthens (or at least preserves) all four workflow principles.

## Roadmap: Extending Beyond Data Analysis

Adding a new vertical means adding a domain skill — not forking the workflow. The four workflow principles, the implementer/reviewer pair, the handoff-doc discipline, semantic-merges, and the autonomous-with-human-in-loop stop-point pattern all carry over unchanged. A new vertical plugs in by providing:

1. **A domain skill** at `skills/<vertical>/SKILL.md` carrying the cross-cutting discipline of that domain.
2. **Stage-scoped references** inside the domain skill: at minimum a `references/planning.md` consumed by `planning-workflow` Phase 1. Other stage references as the vertical needs.
3. **A row in `skills/CATEGORIES.md` and `README.md`** under Domain — data analysis (or under a new vertical heading).
4. **An entry in `planning-workflow` Phase 1's vertical table** so the workflow routes correctly when it sees a task in that domain.

**Planned verticals (hooks for future work, not commitments):**

- **Theory / modeling.** Derivation discipline (step-by-step algebra, symbol tracking), notation consistency, proof checks, simulation or numerical verification of derived formulas.
- **Literature review.** Citation integrity (every claim traces to a cited source with the page / line), claim-evidence mapping, coverage audit across a reading list, systematic note-taking format.
- **Simulation.** Seed discipline, stochastic reproducibility across platforms, sensitivity to parameter grids, convergence diagnostics, calibration-vs-estimation separation.
- **Writing / paper drafting.** Figure and table consistency with the underlying code, cross-reference integrity (labels, citations), narrative coherence across sections, versioning of the manuscript alongside the analysis branch.

When you pick one up, create the domain skill first, then do one real project end-to-end with the existing workflow skills to find the gaps. The workflow skills are meant to bend; the principles are not.

## General

- Keep `README.md`, `RELEASE-NOTES.md`, `skills/CATEGORIES.md`, and skill tables in sync when adding or renaming skills.
- Prefer editing existing skills over creating new ones. New skills should carve out a clearly distinct concern.
- Domain-specific or project-specific configuration does not belong in core superRA — publish it as a separate plugin.
