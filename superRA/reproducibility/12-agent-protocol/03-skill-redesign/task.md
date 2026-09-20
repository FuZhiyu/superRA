---
title: "Restructure the Reproducibility Skill by Moment and Wire the Role Skills"
status: not-started
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
