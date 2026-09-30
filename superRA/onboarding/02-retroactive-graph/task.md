---
title: "Adopt the Reproduction Graph Across an Existing Project"
status: approved
depends_on: []
---

## Objective

Rewrite [adoption.md](../../../skills/reproducibility/references/adoption.md) so it covers declaring the graph for a whole existing project, with the one-task start kept as the bounded option.

- **Declare every task's steps back to external inputs,** from the scripts as they are, without editing code. Agree the external inputs with the researcher and present the DAG for review.
- **Run by slice:** the first build goes upstream-first over targets the researcher chooses from the recorded cost.
- Keep the existing cheap-discovery rule.
- The skill's load-table row for `adoption.md` matches the new scope.
- **Validated without git:** `superra task check`, `repro status`, and the dashboard DAG work on a scratch project with declared steps and no repository; any failure is fixed or reported to [06-empty-root-bootstrap](../06-empty-root-bootstrap/task.md)'s owner.

## Results

[adoption.md](../../../skills/reproducibility/references/adoption.md) now covers declaring a whole existing project, with the one-task trial kept as the other scope the researcher can pick.

- **Declaring:** scripts are declared as they are, with no code edits; a script the graph cannot describe cleanly is noted in the task's `## Details` for the first build. The graph is then presented through the existing review step, which also carries the `task check` validation and the external-input agreement: [designing-the-graph.md](../../../skills/reproducibility/references/designing-the-graph.md), linked rather than restated.
- **First build:** upstream-first, in slices the researcher picks, with recorded durations pricing later slices. The cheap-discovery rule is unchanged except that timing happens after the first build.
- **Load table:** the `adoption.md` row in [SKILL.md](../../../skills/reproducibility/SKILL.md) names both scopes.

### Validated without git

In a scratch project with no repository and one declared step, `task check`, `repro dag`, `repro status`, `build`, and the dashboard's graph and status endpoints all worked, and the build wrote `repro-lock.json`.

**`superra repro status` and `build` write outside `superRA/`:** a hash cache `.superra-repro/` and a `.gitignore` line for it at the project root. `task check`, `repro dag`, and the dashboard write nothing. Onboarding's declare-only stage therefore validates with `task check` and the dashboard, and leaves `status` to the run; this is recorded for [03-onboarding-skill](../03-onboarding-skill/task.md).
