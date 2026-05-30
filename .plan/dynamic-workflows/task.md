---
title: "Dynamic Workflows — Learn & Integrate"
status: not-started
depends_on: []
tags: []
created: 2026-05-30
updated: 2026-05-30
---

# Dynamic Workflows — Learn & Integrate

## Objective

Adopt, into superRA's harness-agnostic skill text (skill text that works across any agent harness, not just Claude Code), the quality patterns that make Claude Code dynamic workflows trustworthy, and record the architectural relationship between the two systems. The `## Analysis` section below is the deliverable that answers the two motivating questions (compatibility/integration; design lessons); the per-change rationale each child needs is inlined in that child's own objective, so a dispatched agent reads only its slice.

Settled scope decisions (from the researcher):
- **Borrow patterns, keep them harness-agnostic.** Adopt a pattern as a behavior-changing skill instruction only where it passes the DRY + Necessity gate (the repo's rule: a line stays only if no other file already carries it and removing it would change what an agent does); understanding-only framing stays here in the analysis or in `CLAUDE.md`, never in skill bodies.
- **Keep the human in the loop.** This is the non-negotiable principle the borrowing must preserve (see Analysis §2.1).
- **Naming coexistence is out of scope here** — already handled on the `rename-workflow-skills` branch (`planning-workflow → superplan`, etc.).
- **Runtime-level delegation (handing a workflow the job of execution engine) is documented as a future Claude-adapter option, not built** — it is Claude-only and would break harness-agnosticism.

Children (the concrete changes):
- `01-review-and-tier-patterns` — perspective-diverse review, the no-silent-caps line, and a wide-fan-out tier, all in `agent-orchestration`.
- `02-domain-lenses` — expose each domain skill's existing gates as named review lenses the new review shape can dispatch. (Feeds perspective-diverse review.)
- `03-loop-until-dry` — loop-until-dry sweep discipline in `semantic-merge` and `writing`.
- `04-contributor-note` — the externalize-state principle plus the workflow-eligible-segment boundary, in `CLAUDE.md`.

---

## Analysis

Sources: Claude Code Workflow tool description (system prompt + Piebald mirror), [code.claude.com/docs/en/workflows](https://code.claude.com/docs/en/workflows), [alexop.dev](https://alexop.dev/posts/claude-code-workflows-deterministic-orchestration/), [Ken Huang](https://kenhuangus.substack.com/p/claude-code-orchestration-dynamic), plus ground truth from a completed run journal in this repo.

### 1. What a dynamic workflow is

A dynamic workflow is a **JavaScript script the model writes and a runtime executes in the background**. Its defining move: the orchestration plan — loops, branching, fan-out, and intermediate results — lives in *script variables*, not in the model's context window. The model's context receives only the final, verified answer.

Primitives: `agent(prompt, {schema, label, phase, model, isolation, agentType})`, `parallel(thunks)` (barrier), `pipeline(items, ...stages)` (no barrier — items flow independently), `phase()`, `log()`, `args`, `budget`. Structured output via JSON `schema`. Resume via cached prefix (requires pure execution — no `Date.now`/`Math.random`). Caps: 16 concurrent, 1000 agents/run. **No mid-run user input** — only permission prompts pause a run; "for sign-off between stages, run each stage as its own workflow."

The three Claude-Code primitives, by *who holds the plan*: **subagents** (model decides turn-by-turn, results land in context), **skills** (instructions the model follows, results in context), **workflows** (a script holds the loop, results in variables).

### 2. The architectural relationship to superRA

superRA and dynamic workflows are **not competitors — they sit at different layers**, and they independently discovered the same core insight from opposite ends.

| | superRA | Dynamic workflows |
|---|---|---|
| What it is | A research *methodology/governance* layer | An *execution substrate* |
| Orchestrator | An LLM, reasoning turn-by-turn | A JS script the LLM wrote |
| Orchestration state | `.plan/` filesystem task tree | script variables |
| Durability | Cross-session, git-tracked, human-readable | Within-session, resume-journal only |
| Human-in-the-loop | **Central** — the three pause classes (the only decision types that stop a run for the human), gates, menus | **Absent mid-run** by design |
| Determinism | Emergent (LLM picks next step) | Guaranteed (script controls flow) |
| Scale per run | A few dispatches | Dozens–hundreds of agents |
| Verification | One implementer → one reviewer | Adversarial N-voter, judge panels |

**The shared insight, discovered twice.** Both move orchestration state *out of the context window*. Workflows move it into *script variables* — ephemeral, in-runtime, optimized for scale and within-run determinism. superRA moves it into the *`.plan/` tree* — durable, cross-session, human-auditable, git-tracked. For a research RA whose work spans sessions and must be provenance-auditable, superRA's choice is the stronger one; for a 500-file single-run sweep, the workflow's choice is. The single most important framing: **superRA already does the workflow architecture's headline move, but persisted to disk instead of to RAM.**

#### 2.1 Autonomy vs. human-in-the-loop is downstream of state location

Describing the contrast as "workflows are autonomous; superRA is human-in-the-loop" is a fair first cut but imprecise in a way that matters. Three refinements:

**The real axis is *where the human sits relative to the run*, not whether a human is present.** Workflows put the **human at the edges**: approve the plan, the run goes dark (the runtime forbids mid-run input — *"only agent permission prompts can pause a run; for sign-off between stages, run each stage as its own workflow"*), then read the final report. superRA puts the **human at genuine decision points interleaved with execution**: the three pause classes, the completion menu, drift-test selection, intent-changing-conflict escalation.

**That posture is *forced* by the state-location decision — not an independent choice.** Script-variable state (RAM) cannot pause for a human and survive, so workflows had to choose edge-only interaction to get scale + journal-resume. The durable `.plan/` tree is re-enterable, cross-session, and human-editable, which is precisely what *enables* mid-run pausing, the dashboard, per-block comments, and agent-cli comment resolution. superRA's interactivity is not a bolt-on; it is what the durable-state architecture buys.

**Do not over-rotate into "superRA stops a lot."** Its `Proceed Without Asking` / Banned Phrasings rules are an aggressive anti-pestering stance — fully autonomous on anything resolvable from code and data, pause **only** for the three real decision classes. The accurate contrast is **human-at-the-edges (workflow) vs. human-at-real-decision-points (superRA)**; both reject check-in theater.

**This is why human-in-the-loop and borrowing are not in tension.** The pause-class boundary — whether a segment of work contains any decision that should stop for the human — is the mechanism that lets superRA adopt the autonomous fan-out engine *without* losing the human: a segment is workflow-delegatable only if it contains zero such pause-class decisions. The runtime only ever gets handed the pause-free interior of a stage; every genuine decision stays in the superRA loop, and the orchestrator folds the verified return back into `.plan/`. The human-in-the-loop principle *is* the gate that decides what is borrowable.

#### 2.2 How dynamic workflows persist state — ground truth from a run journal

The docs say workflows are "resumable" but are vague on the mechanism. A completed run on disk (`~/.claude/projects/<project>/<session>/workflows/wf_*.json`) makes it concrete and confirms the state-location argument with evidence rather than inference.

**The entire state of a run is a single per-run JSON file.** It holds the full script source (inlined), a copy at `scriptPath`, the final `result`, top-line stats (`agentCount`, `totalTokens`, `durationMs`, `status`), and a `workflowProgress` array with **one entry per `agent()` call** — each recording `agentId`, `label`, `phaseIndex`, `state`, `promptPreview`, **`resultPreview`** (the structured output), `tokens`, `toolCalls`, `model`.

**Mechanically it is a memoization cache keyed by position in the script.** Resume re-executes the script top to bottom; for each `agent()` call whose `(prompt, opts)` matches the journal, the runtime returns the cached `resultPreview` instead of spawning; the first changed call and everything downstream runs live. This is why `Date.now()`/`Math.random()` are banned (replay must be deterministic) and why resume is **same-session only** (exit Claude Code mid-run and the next session starts fresh — the file persists, the resume binding does not).

**The decisive contrast with superRA handoff is not durable-vs-ephemeral — both touch disk — but *what the persisted unit is for*:**

| | Workflow journal | superRA `.plan/task.md` |
|---|---|---|
| Persisted unit | Nth `agent()` call → its JSON result | A task: objective, results, review notes, status |
| Addressed to | The runtime, for replay | A human and the next agent, for handoff |
| Form | Position-keyed memo cache | Semantic prose, human-readable |
| Human edits it to steer? | No — edit the *script*, journal is replayed | Yes — editing the task *is* steering |
| Per-step inspection | Watch progress (read-only) | Read / comment / edit every step |
| Lifespan | Same session only | Cross-session, git-tracked, cross-machine |

Three properties that sound alike are independent: **resumable**, **inspectable per step**, **steerable mid-run**. The workflow journal delivers *resumable only*. superRA delivers all three, because its state unit is a handoff document rather than a replay log. The workflow proves resumability is achievable while inspection and steering are absent — the trade it makes for 16-concurrent / 1000-agent scale. "Designed around handoff" is the correct description of superRA's distinctive choice, and handoff is **orthogonal** to resumability, not a stronger form of it.

### 3. Question 1 — Compatibility / integration

Three relationships, in increasing ambition:

**(a) Naming coexistence — DONE.** Claude Code reserves `workflow` as a keyword trigger and feature name. The `rename-workflow-skills` branch removes the collision. Nothing further needed except landing that branch.

**(b) Architectural compatibility — they don't conflict.** Because superRA is governance and workflows are execution, a researcher can run `/deep-research` or a `workflow`-keyword run *inside* a superRA session with no contradiction. superRA's only requirement is its invariant: **durable findings live in `.plan/`.** A workflow's results are ephemeral until the orchestrator folds them back into a task's `## Results` / status. No protocol change needed.

**(c) Functional integration — workflow as an optional execution engine for pause-free fan-out segments.** A dynamic workflow is an excellent engine for segments of a superRA stage that are simultaneously (i) fan-out-heavy, (ii) verification-heavy, and (iii) **free of any decision belonging to the three pause classes**. Candidates: multi-lens parallel review of one task; reproducibility sweep across leaf tasks; stale-reference / consistency sweep across many files; drift-test red-green verification across many key results; thorough-planning parallel exploration. The boundary: the main agent remains orchestrator and human-gate holder, delegating only a bounded pause-free segment and folding the verified return into `.plan/`. **(c) is documented-but-deferred** (task `04`) — it is Claude-only, so it lives behind the Claude adapter, while the *patterns* (just parallel `Agent` dispatch) get lifted into harness-agnostic skill text now.

### 4. Question 2 — What we learn

**Behavior-changing — adopt into skills** (the children implement these):
- **Quality patterns beat scale.** The leverage is repeatable verification structure, not agent count. → perspective-diverse review (task `01` + `02`), loop-until-dry sweeps (task `03`), judge-panel framing for thorough-planning.
- **No silent caps.** When a sweep is bounded (top-N, sampled, no-retry), state what was dropped. (Task `01`.)
- **A workflow tier above "dedicated agent."** Wide pause-free fan-out is a distinct tier, gated on the segment containing no pause-class decision. (Task `01`.)

**Understanding-only — stays in analysis / `CLAUDE.md`, never in skill bodies** (would fail the Necessity test there):
- **Externalize orchestration state; durable for research.** The lesson "who holds the plan determines repeatability" *validates* `.plan/`-as-source-of-truth; the Frontier Resolver (superRA's mechanism for computing the next action from the durable task tree rather than turn-by-turn) is our determinism move. Already our architecture — articulate as shared principle (task `04`), not a skill instruction.
- **Resume = cached prefix.** superRA's analog is the Frontier Resolver plus git plus task statuses. Validates the durable-state choice; nothing to add.
- **fan-out → reduce → synthesize** is the recurring shape — a recognition aid for humans; as a skill line it fails Necessity.

**Explicitly do NOT adopt:** the no-mid-run-input constraint (correct for batch, wrong for a research RA — it would erode the pause classes) and ephemeral script-variable state (wrong for cross-session research).

### 5. Concrete example in this repo — `verify-workflow-skill-rename.js`

`.claude/workflows/verify-workflow-skill-rename.js` adversarially verifies the rename diff and **already embodies almost exactly the perspective-diverse review and loop-until-dry patterns**, written for a harness that can execute it:

```
Review     3 agents  → one per LENS (reference-integrity / prose-coherence / completeness), schema: FINDINGS
                       agentType:'Explore' (read-only), all parallel
   reduce            → flatMap findings, log candidate count (plain JS)
Verify     N agents  → one per finding, "default isReal=false, read the cited file/line", schema: VERDICT
   reduce            → filter isReal && correctedSeverity !== 'INVALID' (plain JS)
Synthesize 1 agent   → SHIP / FIX-FIRST markdown report for the human
```

Lessons, concretely: (1) the fan-out axis is *distinct lenses* — this is perspective-diverse review, arrived at independently, validating the abstraction; (2) find-then-verify is two layers, the second a fresh agent that opens the cited file:line with an adversarial `isReal=false` default — `agent-orchestration §Handling Reviewer Feedback` rule 1 operationalized per-finding, with a `correctedSeverity` INVALID enum to kill false positives; (3) JSON schemas make the reduce steps pure code, the structured-return idea made tangible; (4) a shared `intent` block states approved scope + archive exclusions + "empty findings is correct" up front — the no-silent-caps discipline in its healthiest form; (5) read-only `Explore` agents match superRA's reviewer-never-edits stance.

Ground-truth proof the verify layer earns its keep, from the run journal: the `completeness` reviewer raised a `BLOCKING` finding (broken `.agents/skills/` symlinks); the per-finding verify agent opened the repo, found them correctly recreated, and returned `isReal: false` — a false positive killed before reaching the human (5 agents, ~239k tokens, verdict SHIP). Side observation: `Explore` agents ran on Haiku while synthesize ran on Opus — `agentType` carries its own model default, a cheap-recon / expensive-synthesis split worth noting for perspective-diverse review. The one gap the script does not close: folding the verdict back into `.plan/` is still the orchestrator's job — the durable-state invariant the runtime deliberately does not own.

## Results

Analysis complete (this session): architectural relationship (§2, incl. autonomy-from-state-location §2.1 and run-journal ground truth §2.2), compatibility/integration answer (§3), design-lessons answer split behavior-changing vs understanding-only (§4), concrete in-repo example with run-journal evidence (§5). Children carry the concrete changes; each inlines the rationale slice it needs.
