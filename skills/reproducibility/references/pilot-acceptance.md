# Bounded Adoption

Start with one producer and one meaningful `kind: check` in an `on-demand` task, with a named saved-input boundary. Keep upstream reconstruction and promotion outside that pilot unless requested. Follow [graph authoring](graph-authoring.md) and [scoped verification](../SKILL.md#build-and-status).

## Acceptance Recipe

Use a disposable fixture or isolated copies for perturbations. Record reported state and actual execution separately: descendants can report stale before an upstream rebuild, then skip after identical regeneration.

| Change | Required evidence |
|---|---|
| First build | Declared outputs exist; producer and numerical check succeed; scoped status is fresh. |
| Unchanged build | Neither step executes. |
| Force the fresh check | `--force` executes only the check; `--force-all` executes producer and check. Both dry-run previews leave build evidence unchanged. |
| Timestamp-only change | Neither step executes. |
| Producer or included-helper edit | Its consumer is invalidated; the expected code executes. |
| Undeclared environment-file edit | Neither step executes automatically; apply [environment-change judgment](../SKILL.md#environment-changes). |
| Missing output | The producer recreates it. |
| Identical regeneration | The downstream check skips if its own deps are unchanged. |
| Corrupted output | The numerical check rejects the altered value when run against it directly; a graph build may repair the output before checking it. |
| Branch or sandbox-input availability change, when routed dynamically | Discovery still agrees with the producer's actual reads and writes. |
| Restoration | Original boundary bytes are intact; final scoped status is fresh; temporary edits are removed. |

Measure unchanged status and build wall time after registration. Separate resolver, graph, hashing, and execution costs when diagnosing latency. Subsecond warm status is a useful target for a tiny fixture, not a universal gate.

Ordinary registrations need checks targeted to the changed path.
