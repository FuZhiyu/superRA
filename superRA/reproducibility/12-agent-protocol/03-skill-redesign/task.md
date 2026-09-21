---
title: "Restructure the Reproducibility Skill by Moment and Wire the Role Skills"
status: implemented
depends_on:
  - 01-cli-decision-support
  - 02-agent-signals
---

## Objective

Rewrite [skills/reproducibility/](../../../../skills/reproducibility/SKILL.md) so each agent loads the model plus the one reference for the moment it is in, and carry the [group decisions](../task.md#decisions-researcher-2026-09-20) as the behavior it teaches. Implementers and reviewers meet the protocol through their role skills.

- **SKILL.md is what every agent touching retained results needs, about 400 words:**
  - the model first, about five lines, leaning on what agents already know about pytask:
    - steps belong to tasks: a step is one command with its deps and outs, declared in the owning task's `## Reproduction` section; outs feeding deps order steps and tasks;
    - the engine is pytask: each step becomes a generated pytask task, and freshness is pytask's content-hash comparison against `pytask.lock`;
    - what superRA adds on top: task-scoped targets with saved inputs at the edge, and reviewed acceptance as a second route to `fresh`;
  - the routine loop: registration follows placement, build the recorded result, check status, state what the evidence covers in `## Results`;
  - the gates;
  - a routing table keyed by the agent's moment.
- **One reference per moment:**

  | Reference | Moment | Carries |
  |---|---|---|
  | `designing-the-graph.md` | planning a task's steps, or declaring them | what earns a step, the step unit, the dependency trade-off, declaring from the script, the boundary, step lifecycle |
  | `rerun-or-accept.md` | a step is stale | preview cost and cause, classify the step's role, the stale rule, what proves a change superficial, the accept recipe, what acceptance never covers |
  | `diagnosing.md` | a state is unexpected | the rerun model, cascade stoppers, the `explain` reading table, environment changes |
  | `protect-and-completion.md` | `Stage: protection`, completion gate | unchanged in scope |
  | `adoption.md` | first use in a project | bounded start, cheap path discovery, declared paths agree with the producer's routing |

- **`designing-the-graph.md` teaches code and graph as one design.** The step unit follows the script, so the agent shapes scripts and helper modules to get the graph it wants: split a script at a saved artifact when stages differ in cost and edit frequency, split helper modules by consumer set, and keep a script whole when its stages always run together.
- **The dependency trade-off is stated as a ladder:** declare every true read, since a missing dep is a silently wrong result and an extra dep is only cost; measure fan-out with `impact` and recorded durations; split scripts or modules the task owns when the waste is real, and report the ones it does not own; resolve what remains through the stale rule. Dropping a true dep is never a rung.
- **Planning draws script boundaries.** [build-and-review.md](../../../../skills/superplan/references/build-and-review.md) §Artifact Pipeline routes the planner to `designing-the-graph.md` when mapping scripts, so expensive and frequently edited stages start in separate scripts.
- **Recipes, not flag semantics.** Each recipe names the situation and the command once and links [commands.md §Reproduction](../../../../skills/task-tree/references/commands.md#reproduction); SKILL.md §Build and Status stops restating target and scope semantics.
- **Role skills carry the pointer.** [implement-task](../../../../skills/implement-task/SKILL.md) §Self-Check and [review-task](../../../../skills/review-task/SKILL.md) each gain one line routing to the skill's gates; the reviewer's line covers registration of retained code, the run route, and the recorded reason behind any acceptance. The `using-superra` §Task Interface trigger attaches registration to its file-placement rule.
- **Companions stay downstream.** [task-companion-files.md](../../../../skills/using-superra/references/task-companion-files.md) states that a companion is never upstream of main work and moves §Promote's trigger from "before integration review" to the moment another task, pipeline, or document consumes it; `designing-the-graph.md` points there instead of restating it.
- **Session start reports staleness.** `using-superra/references/main-agent.md` §Session Start Actions gains one `repro status .` summary on trees with reproduction config; the main agent applies the stale rule to what it shows, so steps staled by the researcher's own edits, git operations, or earlier sessions reach the researcher.
- **Inventories stay in sync:** `CLAUDE.md` ownership table, `skills/CATEGORIES.md`, `README.md`, and every inbound link to a renamed reference or anchor across `skills/`.
- **Validation:** every changed file under `skills/` passes the [CLAUDE.md](../../../../CLAUDE.md) three-test gate line by line and the terse style, measured in words; every command and output named matches the CLI the sibling tasks ship; `task check --category links` passes. Behavioral verification is deferred to real-project use by researcher decision.

## Details

- Load `skill-creator` and `superRA:communicate` before editing. Style exemplars: `skills/implement-task/SKILL.md`, `skills/review-task/SKILL.md`.
- Current content mostly survives; the work is re-homing and the new judgment content. Suggested mapping: SKILL.md §What Gets a Step and §Step Lifecycle → `designing-the-graph.md`; §Environment Changes → `diagnosing.md`; rerun-model §Reviewed acceptance → `rerun-or-accept.md`; the rest of rerun-model → `diagnosing.md`; graph-authoring → `designing-the-graph.md`.
- `adoption.md` replaces [pilot-acceptance.md](../../../../skills/reproducibility/references/pilot-acceptance.md): keep the bounded start, the discovery-latency measurement, and the routing-agreement check; the matrix rows that retest the runner's own suite fail the Necessity test.
- Pilot lessons missing from the skill today: per-step process start-up cost, and enumerating outs from disk picks up leftovers ([08-pilot-treasurygiv](../../08-pilot-treasurygiv/task.md)).
- Inbound links to check: `superimplement/references/completion.md`, `superintegrate/references/{protect,integrate,finish,mature-consolidate}.md`, `superplan/references/{build-and-review,changing-the-tree}.md`, `task-tree/references/{commands,task-file-contract}.md`, `using-superra/SKILL.md`, and the two domain `planning.md` files.
- A subagent cannot ask the researcher: the stale rule's "ask" is a return to the orchestrator, per `superimplement` §pausing.

## Results

[skills/reproducibility/](../../../../skills/reproducibility/SKILL.md) now opens with the model and routes by moment. SKILL.md's body is 414 words, down from 621, and the three old references are replaced by five, one per situation an agent can be in.

### SKILL.md carries the model, the loop, the gates, and the routing table

- **The model is three bullets.** Steps belong to tasks; pytask 0.6 executes them, generated in memory; superRA adds task-scoped targets with saved inputs at the edge and reviewed acceptance as a second route to `fresh`.
- **The loop is the group decisions in order** — registration follows placement, produce through `repro build`, read the status you are about to claim, state what the evidence covers.
- **A third blocking gate.** Beside registration and verification-before-a-claim: a stale step is run, accepted with a recorded reason, or reported, never left silently stale.
- **§Build and Status is gone.** Its target and scope semantics restated [commands.md §Reproduction](../../../../skills/task-tree/references/commands.md#reproduction); what survives names a situation and its command and links there.

### Where the content went

| Reference | Moved in | Added |
|---|---|---|
| [designing-the-graph.md](../../../../skills/reproducibility/references/designing-the-graph.md) | old SKILL.md §What Gets a Step and §Step Lifecycle, all of `graph-authoring.md` | the step unit follows the script; the dependency ladder; companions stay downstream; two pilot lessons — per-step interpreter start-up, and enumerating outs from disk picking up leftovers |
| [rerun-or-accept.md](../../../../skills/reproducibility/references/rerun-or-accept.md) | `rerun-model.md` §Reviewed acceptance | preview the cost and the cause; role classification; the stale rule; the superficial-change exception |
| [diagnosing.md](../../../../skills/reproducibility/references/diagnosing.md) | the rest of `rerun-model.md`, old SKILL.md §Environment Changes | — |
| [protect-and-completion.md](../../../../skills/reproducibility/references/protect-and-completion.md) | unchanged in scope; three links repointed | — |
| [adoption.md](../../../../skills/reproducibility/references/adoption.md) | `pilot-acceptance.md`'s bounded start, latency measurement, and routing-agreement check | — |

`pilot-acceptance.md`'s 15-row verification matrix is deleted except the routing-agreement row. The other 14 rows — timestamp-only change, unchanged build, identical regeneration, forced check, missing output, acceptance semantics — assert the runner's own behavior, which its test suite already covers; asking an adopting project to re-derive them fails the Necessity test.

### The judgment the skill now teaches

- **The stale rule is a three-row table** keyed on the step's role, then its cost: leave a task-local step stale and say so; run a cheap significant one; ask the researcher about a costly one, carrying the diagnosis and a build / accept / leave recommendation. The exception — a diff that proves no result can move — is accepted on the agent's own authority with the reason recorded. "Cheap" is written as about a minute, explicitly a guideline and not a rule, and a subagent's "ask" is its return.
- **Significance is inferred, not marked.** Task-local means the producer sits under `attachments/` and nothing outside consumes its outs; any of a maintained-path producer, an outside consumer, a completion target, or a selected check makes it significant. The reference states that a selected check is significant at zero outside readers, matching what [01-cli-decision-support](../01-cli-decision-support/task.md) shipped: `status` prints the `outside readers: N` count as a fact and never a verdict.
- **Graph design is script design.** One step per script is the default and the script boundary is the lever — split at a saved artifact when stages differ in cost and edit frequency, merge only what always runs together, split helper modules by consumer set. The cost side is named: each step pays a fresh interpreter, which dominates a chain of short scripts.
- **The dependency trade-off is a ladder,** with "drop a true dep" explicitly off it: declare every true read, measure the fan-out with `impact` and `build --dry-run` durations before calling it waste, split what your task owns and report what it does not, then resolve the rest through the stale rule.

### Wiring

- **[implement-task](../../../../skills/implement-task/SKILL.md) §Self-Check** gains a fourth item routing a result recorded from retained code to the skill's gates; **[review-task](../../../../skills/review-task/SKILL.md) §Review Protocol** gains one line checking registration, the run route, and the reason behind any acceptance.
- **[using-superra](../../../../skills/using-superra/SKILL.md) §Task Interface** now states registration as a consequence of placement, directly after the file-placement rule, instead of as an unrelated paragraph above it.
- **[task-companion-files.md](../../../../skills/using-superra/references/task-companion-files.md)** says in §Classify that a companion feeds only its own task's results, and §Promote fires as soon as a companion meets the permanent-project definition rather than at integration review — keeping all three routes that definition covers, not only consumption by another task. `designing-the-graph.md` points there and adds only the reproduction-side instruction: do not draw a dep edge into another task's `attachments/`.
- **[main-agent.md](../../../../skills/using-superra/references/main-agent.md) §Session Start Actions** runs `repro status .` on a tree with reproduction config and reports through the stale rule.
- **[build-and-review.md](../../../../skills/superplan/references/build-and-review.md) §Artifact Pipeline** routes the planner to `designing-the-graph.md` when mapping scripts, replacing the generic skill pointer.

### Inventories and links

`CLAUDE.md`'s ownership row and the `skills/CATEGORIES.md` entry now name graph and script design and the stale-step judgment among the skill's concerns; neither enumerates the references, which would be a second copy of SKILL.md's routing table. Four inbound links to renamed targets were repointed: `changing-the-tree.md` and `mature-consolidate.md` to `designing-the-graph.md`, `commands.md` and `task-file-contract.md` to `diagnosing.md`. The `superintegrate` step files, `superimplement/references/completion.md`, and `README.md` needed no change — they cite `protect-and-completion.md` or `SKILL.md`, both of which kept their paths. The two domain `planning.md` files cite the skill generically and are correct as they stand.

### Validation

A link checker over all 101 markdown files under `skills/` plus `CLAUDE.md` and `README.md` resolves every relative target and heading anchor; its 24 remaining misses are pre-existing illustrative placeholders (`file.py#L42`, `ATTACH_DIR/description.png`). `superra task check --category links` passes, and full `task check` reports 0 errors with only the 11 coverage warnings [02-agent-signals](../02-agent-signals/task.md) documented. `check_markdown.py` reports all six skill files clean. Every command and output named was checked against `./superRA/superra repro <subcommand> --help` in this worktree.

No `## Reproduction` step is registered for this task: it ships no executable code, and `repro impact` confirms no existing step reads any file it touched, so nothing was staled. Behavioral verification is deferred to real-project use by researcher decision.

## Review Notes

Tier: thorough (read all six skill files and every wiring edit in full; ran the link check; grepped the repository for links to the deleted references). Focus: correctness, scope-fidelity, and the [CLAUDE.md](../../../../CLAUDE.md) three-test gate. Reviewer: main agent.

1. `[BLOCKING]` **A named command fails.** [designing-the-graph.md:64](../../../../skills/reproducibility/references/designing-the-graph.md#L64) tells the agent to rerun `superra repro status` with no target; `status` requires one. Name the target form.

   → implemented: [designing-the-graph.md:60](../../../../skills/reproducibility/references/designing-the-graph.md#L60) — now `superra repro status <task>`, the form a step comment's owning task takes.
2. `[BLOCKING]` **Four lines fail the three-test gate.**
   - [designing-the-graph.md:28](../../../../skills/reproducibility/references/designing-the-graph.md#L28) — same-file restatement and DRY: rung 3 of the ladder already tells the implementer to split the scripts its task owns, and [build-and-review.md](../../../../skills/superplan/references/build-and-review.md) already tells the planner to draw the boundaries. Cut the sentence.

     → implemented: [designing-the-graph.md:24-26](../../../../skills/reproducibility/references/designing-the-graph.md#L24-L26) — sentence cut; the section now ends on the start-up-cost line.
   - [designing-the-graph.md:15](../../../../skills/reproducibility/references/designing-the-graph.md#L15) — Necessity: the `task check` warning and the `implemented` reminder both already end "leave it if the file has none". Cut the paragraph.

     → implemented: [designing-the-graph.md:13-15](../../../../skills/reproducibility/references/designing-the-graph.md#L13-L15) — paragraph cut; §What earns a step now ends on the companion line.
   - [task-companion-files.md:8](../../../../skills/using-superra/references/task-companion-files.md#L8), [21](../../../../skills/using-superra/references/task-companion-files.md#L21), [23](../../../../skills/using-superra/references/task-companion-files.md#L23) — one fact three times: the Classify clause, the permanent-artifact definition ("consumed by another task"), and the second §Promote paragraph, whose last sentence is rationale. Keep the Classify clause and make §Promote one imperative that carries the timing.

     → implemented: [task-companion-files.md:21](../../../../skills/using-superra/references/task-companion-files.md#L21) — §Promote is one imperative carrying the timing ("as soon as it meets the permanent-project definition, not at integration review"); the second paragraph is gone and the Classify clause stands.
   - [main-agent.md:10](../../../../skills/using-superra/references/main-agent.md#L10) — the clause after the dash is rationale. Cut it.

     → implemented: [main-agent.md:10](../../../../skills/using-superra/references/main-agent.md#L10) — clause cut; the bullet ends at the stale-rule link.
3. `[ADVISORY]` The [CATEGORIES.md:52](../../../../skills/CATEGORIES.md#L52) row lists every reference and its contents, a second copy of the skill's routing table. One sentence on what the skill provides is enough.

   → implemented: [CATEGORIES.md:52](../../../../skills/CATEGORIES.md#L52) — the row names the skill's concerns and drops the per-reference enumeration, matching the shape of its sibling rows.
4. `[ADVISORY]` Seven task files under `superRA/reproducibility/` still link to the three deleted references, [06-skill](../../06-skill/task.md) and the [group task](../task.md) among them. `task check --category links` validates step citations only, so it passes over them.
