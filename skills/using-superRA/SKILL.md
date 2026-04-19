---
name: using-superRA
description: Master skill every agent reads. Carries the universal workflow principles, code-change defaults, skill inventory, composable-design map, Skill-Load Manifest, Execution Modes, and instruction priority. Main agents also load `references/main-agent.md` at session start for cross-session detection, autonomy, and the default handoff-doc load; subagents inherit task context from dispatch and skip that reference.
---

This is the one skill every superRA agent reads — main agents at session start, dispatched subagents at dispatch time. It establishes the universal workflow principles, names the other skills in the plugin, and tells you exactly what to load for your current Stage. The plugin's `CLAUDE.md` is contributor-only and is NOT visible to agents running the plugin in a user's repo; everything agents need to know is restated here.

## Universal Principles

Four load-bearing principles apply to **every** superRA workflow, regardless of domain.

1. **Implementer–reviewer pair at every step.** No result ships without adversarial review. One comprehensive review pass per task returning `APPROVE` / `REVISE`; the reviewer walks the full checklist regardless of early failures, and the re-review after REVISE is narrow (verify cited fixes + any finding annotated as depending on an upstream fix). Review is never skipped, regardless of perceived triviality. The reviewer is adversarial by design — thorough, skeptical, erring toward over-flagging. The orchestrator is the arbitrator — it made the plan, talks to the researcher, and overrules with documented reasoning when the reviewer is wrong.

2. **Handoff docs are the auditable record AND the continuation point.** Findings, decisions, methodology notes, and results land in committed `PLAN.md` / `RESULTS.md` **before** they appear in any chat message or status report. Any fresh agent can open the repo and resume work from the docs + git state alone — no prompt history required. Atomic commits bundle code + doc edits so every git SHA reconstructs a coherent state. If a result exists only in a status message, it does not exist.

3. **Fast early, strict before merge. Semantic merges always.** Interim work is optimized for speed — no codebase-fit checks at per-task checkpoints. Integration discipline (drift tests, refactor, doc finalization) runs only when the user chooses to merge, inside `integration-workflow`. Every merge into main goes through `semantic-merge`, never a bare `git merge` / `rebase` / `cherry-pick`.

4. **Autonomous with human in the loop.** Drive the workflow forward on your own power between legitimate stop points. An `APPROVED` task dispatches the next without a check-in; a completed workflow step proceeds without "shall I continue?". Stop only for: (a) a hard blocker the RA cannot resolve from code and data, (b) a decision beyond the RA's authority that belongs to the researcher (methodology, scope, sample/variable definitions, research-intent calls), or (c) a user-defined milestone baked into a workflow. Use `AskUserQuestion` when the harness exposes it. Log every user decision in `PLAN.md` per `handoff-doc` §User Decisions Log **before** acting on it. The full main-agent autonomy contract — proceed-without-asking patterns, stop-and-ask classes, banned phrasings — lives in `references/main-agent.md` (loaded by the main agent at session start; subagents inherit autonomy from their dispatch boundary).

## Code-Change Defaults

These defaults apply whenever you write, review, or refactor code. They govern micro-level execution and do not replace the workflow rules above.

1. **Surface assumptions and ambiguity early.** Do not silently choose between materially different interpretations. State the assumption you are making, name meaningful tradeoffs, and point out a simpler path when one exists. Ask only when the ambiguity changes correctness, scope, or a decision that belongs to the researcher.

2. **Prefer the minimum code that solves the task.** No speculative features, abstractions, configurability, or defensive branches that were not requested. If a straightforward implementation works, use it.

3. **Keep edits surgical.** Touch only what the task requires. Match the surrounding style. Do not refactor adjacent code, comments, or formatting unless the task requires it. Remove imports, variables, and helper code only when your own change made them unused; mention unrelated dead code instead of deleting it.

## Shared-Repo Commit Discipline

Multiple agents (main/orchestrator plus subagents, or parallel subagents in the same worktree) may be writing in the same repo. Any agent that stages a commit — including the main agent dispatching other agents — MUST respect this discipline.

Other agents' uncommitted edits may land in your `git status` output. **Only commit the files you or your subagents modified this turn.** Never commit sweeps.

Before staging:

1. Run `git status` and list every modified/new file. For each, decide: did I touch this file (directly via Write/Edit) in this turn?
2. If yes -> stage it by exact path: `git add path/to/file`.
3. If no -> leave it untouched. Do NOT `git add -A`, `git add .`, or `git add -u`. Those stage other agents' in-flight work and produce cross-agent commit contamination that is hard to unwind.
4. Before `git commit`, run `git diff --cached` and confirm only your edits are staged. If you see unexpected content, unstage it with `git restore --staged path/to/file`.

If you see unfamiliar uncommitted changes and cannot tell whether they are another agent's in-flight work or stale local state, stop and ask (the orchestrator if you are a subagent; the user if you are the main agent) — do not unilaterally discard or commit them.

## Handoff Docs

Every agent edits `PLAN.md` and `RESULTS.md` at some point — implementers rewrite step text and record findings, reviewers write review-notes blockquotes, orchestrators annotate with adjudication notes. The editing discipline (four document principles, inline-edit rule, stale-content checklist, User Decisions Log format, figure-embedding pointer, `## Project Conventions` layout, full `PLAN.md` / `RESULTS.md` anatomy templates) lives in `superRA:handoff-doc`.

## Skill Inventory

Grouped Workflow / Domain / Utility / Meta. See `skills/CATEGORIES.md` for the full grouping index.

| Category | Skill | One-line purpose |
|---|---|---|
| Workflow | `planning-workflow` | PLAN phase: scope check, task decomposition, plan draft. |
| Workflow | `execution-workflow` | IMPLEMENT + VALIDATE: per-task dispatch, one-pass review, reproducibility, completion menu. |
| Workflow | `integration-workflow` | INTEGRATE (pre-merge): drift tests, refactor, doc finalization. |
| Workflow | `merge-workflow` | INTEGRATE (merge): update with main, verify, local merge or PR. |
| Workflow | `agent-orchestration` | Cross-stage dispatch patterns, Dispatch Templates, reviewer-feedback handling, Review Status Reference. |
| Domain | `econ-data-analysis` | Data-analysis vertical: Iron Law, describe-analyze-validate, pitfalls, common rationalizations. |
| Utility | `handoff-doc` | Handoff-doc discipline — four document principles, inline-edit rule, stale-content checklist, User Decisions Log format, figure-embedding pointer, full `PLAN.md` / `RESULTS.md` anatomy templates. Loaded on demand by agents that need the full discipline and always by doc-creators (planning-workflow Phase 2, integration-workflow Step 3 doc-writer); usable standalone by a single author. |
| Utility | `refactor-and-integrate` | Drift-test, codebase-integration, and merge-quality checklists. |
| Utility | `report-in-markdown` | Format discipline for markdown reports — figures, LaTeX math, tables. |
| Utility | `semantic-merge` | Intent-based conflict resolution; escalates methodology conflicts. |
| Utility | `worktree-data-sync` | Isolated git worktrees, non-git data sync between them, and cleanup ritual. |
| Meta | `using-superRA` | This skill — the master skill every agent reads. |
| Meta | `codex-superra-setup` | Codex-only bootstrap for installing or refreshing the named custom agents in project or global scope. |

## Composable Design

Skills compose by category. **Workflow skills** own sequencing — they decide what happens when, and dispatch agents to do it. **Domain skills** own domain discipline — the vertical-specific knowledge a workflow skill invokes when a task touches that domain (today: `econ-data-analysis`). **Utility skills** are called on demand by workflow skills, agent files, or other skills — they are domain-agnostic and reusable. **Meta skills** shape the skill system itself (`using-superRA`). One source of truth per concern: if two skills seem to overlap, one of them should be pointing at the other rather than duplicating content.

## Harness Adapters

The canonical workflow instructions live in shared `skills/` and `agents/`. Harness-specific tool names, named-agent setup, and install surfaces live in adapter references rather than in forked workflow copies.

- **Claude:** `references/claude-tools.md`
- **Codex:** `references/codex-tools.md`
- **Copilot CLI:** `references/copilot-tools.md`
- **Gemini CLI:** `references/gemini-tools.md`

Use the adapter for the harness you are actually running on. Keep the shared workflow behavior in the canonical skill bodies.

## Skill-Load Manifest

For each Stage, load the listed skills and references. The Stage is role-independent; `subagent_type` (implementer vs reviewer) encodes role. Role differentiation shows up explicitly on the `implementation` and `documentation` rows where the implementer and reviewer load different references.

**The "Required skills" column lists what loads *in addition to* `superRA:using-superRA`** — the master skill every agent already loads at dispatch time (implementer / reviewer via frontmatter preload; team teammates via SessionStart injection). `using-superRA` carries §Universal Principles, the Skill Inventory, the composable-design map, and this manifest. Handoff-doc editing discipline is owned by `superRA:handoff-doc`; subagents get a compact etiquette from `agents/implementer.md` / `agents/reviewer.md` step 1 and load the full skill only on demand or when creating docs from scratch.

| `Stage:` | Required skills | Stage-scoped references |
|---|---|---|
| `implementation` | active domain skill (for data analysis: `econ-data-analysis`) | domain §Three Concurrent Disciplines (teaching + shared severity-marked checklist). For data analysis: **implementer** additionally loads `econ-data-analysis/references/notebook-format.md`; **reviewer** loads SKILL.md only (the main body carries everything — §Three Concurrent Disciplines for verification, §Pitfalls for operation-specific correctness; if the dispatcher wants a specific Pitfalls subsection highlighted for review, it names it in `Additionally:`). |
| `integration` | `refactor-and-integrate`; domain skill | `codebase-integration.md` (generic); `integration.md` (data-analysis); `integrate-drift-tests.md` if drift tests exist |
| `drift-test` | `refactor-and-integrate`; domain skill | `integrate-drift-tests.md` + `drift-test-quality.md` |
| `merge` | `refactor-and-integrate` + `semantic-merge`; domain skill | `merge-quality.md` |
| `documentation` | `handoff-doc` + `report-in-markdown` | implementer role: `baseline-io.md` + `rich-content.md` + `final-form.md`; reviewer role: `final-form.md` |
| `planning-review` | `handoff-doc` + domain skill | `planning.md` (domain) |


**Main-agent default load.** Main agents additionally load `superRA:handoff-doc` at session start (per `references/main-agent.md`) so that editing discipline is available before the main agent touches PLAN.md, and so `planning-workflow §Changing Plans` cross-references into `handoff-doc` (User Decisions Log, plan-anatomy) resolve. The subagent-side rows in the table above are unaffected — subagents load `handoff-doc` only on `documentation` / `planning-review` stages as listed.

**Unknown Stage values are a dispatch error.** If the dispatch prompt carries a `Stage:` that does not match a row above, halt and report the mismatch in your status return — do not guess. The manifest is the single source of truth for Stage→{skills, references}.

## Execution Modes

**Subagent dispatch (default for multi-step workflows).** The orchestrator uses the `Agent` tool to dispatch an implementer or reviewer subagent per task. Dispatch prompts follow the canonical `Stage:` / `Task:` / `Additionally:` template — see `agent-orchestration` §Dispatch Templates. The subagent reads its dispatch prompt, loads per the Skill-Load Manifest above, does the work, returns a status per `agents/implementer.md` / `agents/reviewer.md` §Report Format.

**Direct mode.** When the orchestrator executes a step itself — no subagent dispatch — it plays the implementer or reviewer role in-session. The discipline is the same; only the dispatch envelope is gone.

- **Read the agent file for the role you are playing.** For an implementation step, read `agents/implementer.md`. For a review step, read `agents/reviewer.md`. Follow the protocol there as written.
- **The Skill-Load Manifest still drives loads.** Consult the manifest row for your Stage and load the listed skills and references yourself in-session.
- **The dispatch-prompt contract does not apply — there is no dispatch.** Task context comes from `PLAN.md`, `RESULTS.md`, and the current session; you do not write an `Additionally:` line to yourself.
- **Self-review gate, handoff-doc edit discipline, and verdict protocol all apply.** Walk the active domain skill's §Three Concurrent Disciplines before committing. Update `PLAN.md` / `RESULTS.md` inline per the handoff-doc editing etiquette in `agents/implementer.md` / `agents/reviewer.md` step 1, or load `superRA:handoff-doc` if you need the full discipline. Reviewer verdicts are still APPROVE / REVISE even when you render them as your own conclusion.
- **Review is never skipped.** If you implemented in direct mode, you still need a review pass — either dispatch a reviewer subagent for the review step, or play the reviewer role in-session against the same discipline. Self-approval without walking the checklist is not a review.

## Tool Discipline

**Tool preference for file inspection.** Use `Read`, `Glob`, and `Grep` instead of Bash `cat`/`head`/`grep`/`find` whenever you need to look at files — faster and avoids unnecessary permission prompts.


## Semantic Merge

When merging, rebasing, or cherry-picking branches, superRA uses intent-based conflict resolution rather than mechanical ours/theirs. Research-meaningful conflicts are always escalated to the user. See `superRA:semantic-merge` for the full process. A PreToolUse hook automatically reminds you to use this skill when a bare `git merge/rebase/cherry-pick` is detected.


## Instruction Priority

SuperRA skills override default system prompt behavior, but **user instructions always take precedence**:

1. **User's explicit instructions** (CLAUDE.md, GEMINI.md, AGENTS.md, direct requests) — highest priority
2. **SuperRA skills** — override default system behavior where they conflict
3. **Default system prompt** — lowest priority

If CLAUDE.md says "skip data description for this dataset" and a skill says "always describe first," follow the user's instructions. The user is in control.
