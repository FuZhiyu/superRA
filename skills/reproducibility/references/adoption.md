# Adopting Reproduction in a Project

**Start with one task.** Register one producer and one meaningful `kind: check` step, reading named saved or external inputs. Leave the upstream producers unregistered in that first pass unless the researcher asks for them.

**Keep path discovery out of the analysis environment.** Every `superra` command evaluates the `shell:` variables in `superRA/config.yaml`. A variable that boots the language runtime or loads the project makes every `status` as slow as a build. After the first registration, time `status` and `build` with nothing changed; a warm `status` under a second is the target for a small tree, not a gate.

Then follow [designing-the-graph.md](designing-the-graph.md) for the rest of the tree.
