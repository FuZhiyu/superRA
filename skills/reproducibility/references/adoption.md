# Adopting Reproduction in a Project

**Agree the scope with the researcher:**

- **Whole project** — existing work entering superRA, such as `superRA:onboarding`: declare every task's steps back to external inputs, then build by slice.
- **One task** — a first trial in a project already on superRA: register one producer and one meaningful `kind: check` step, reading named saved or external inputs. Leave the upstream producers unregistered unless the researcher asks for them.

## Declaring an existing project

- **Declare the scripts as they are,** per [designing-the-graph.md](designing-the-graph.md#declare-from-the-script-not-from-memory); edit no code. A script the graph cannot describe cleanly — hard-coded machine paths, several scripts writing one directory, reads routed at runtime: note it in the task's `## Details` for the first build.
- **Present the graph** per [designing-the-graph.md §Presenting a graph for review](designing-the-graph.md#presenting-a-graph-for-review).

## The first build

**Build upstream-first, in slices the researcher chooses:** `superra repro build <task>` over one task or a cheap chain at a time, each long estimation as its own slice. The recorded durations then price the next slice through `build --dry-run`.

**Keep path discovery out of the analysis environment.** Every `superra` command evaluates the `shell:` variables in `superRA/config.yaml`. A variable that boots the language runtime or loads the project makes every `status` as slow as a build. After the first build, time `status` and `build` with nothing changed; a warm `status` under a second is the target for a small tree, not a gate.
