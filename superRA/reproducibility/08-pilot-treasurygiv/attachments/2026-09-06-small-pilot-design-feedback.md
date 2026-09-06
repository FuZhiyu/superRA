# Keep reproduction declarations local and discovery cheap

The 2026-09-06 TreasuryGIV pilot supports keeping the existing content-based runner while
simplifying graph authoring. The two-step pilot passed its rebuild checks, but its setup
put run-specific directory discovery in global config and made every status command launch
Julia twice. This note proposes instruction changes first; CLI extensions remain candidates,
not implementation decisions.

Evidence: [TreasuryGIV pilot and acceptance record](https://github.com/FuZhiyu/TreasuryGIV/blob/1d1cdfda080b66ddd6e02e81370c0a1965522720/superRA/code-infrastructure-change/reproducibility-pilot/task.md),
[timing measurements](https://github.com/FuZhiyu/TreasuryGIV/blob/1d1cdfda080b66ddd6e02e81370c0a1965522720/superRA/code-infrastructure-change/reproducibility-pilot/attachments/timing.log),
and [draft PR #124](https://github.com/FuZhiyu/TreasuryGIV/pull/124).
The pilot reproduced one holdings CSV from a saved `pooled_1986` panel; upstream panel
construction and the full publication pipeline were outside its scope.

| Measurement | Seconds |
|---|---:|
| Normal status command | 5.841 |
| Unchanged build | 6.164 |
| Graph construction with the same paths already resolved | 0.134 |
| Freshness check with warm hash cache | 0.0024 |
| Freshness check with empty hash cache | 0.0045 |

The config's `POOLED_1986_RUN` and `SANDBOX` shell commands each launched Julia and imported
the estimation IO helpers just to return a directory. In a separate instrumented graph run,
these sequential calls took 4.507 and 2.778 seconds, together 98% of graph-construction time.
Those timings come from different invocations than the normal status measurement and must
not be added to it. They identify discovery overhead in this setup, not a slow hashing engine.

The pilot passed 18 behavior assertions and 1,082 numerical assertions. Unchanged and
timestamp-only builds skipped both steps; helper and environment changes invalidated their
consumers; an identical regenerated CSV stopped the downstream rerun; a missing CSV was
rebuilt; and a deliberately altered share failed the numerical check. All temporary edits
were restored, the boundary input hash was unchanged, and final status reported both steps fresh.

**1. Put each declaration at the smallest useful scope.** The
[graph-authoring reference](../../../../skills/reproducibility/references/graph-authoring.md)
currently says to root every movable path in a config variable. Preserve portable aliases for
actual shared roots, but explicitly permit stable repo-relative boundary inputs in the task,
including untracked inputs. Keep artifact filenames, run selection, dependency edges, and
checks in the owning task. Reserve config for shared runners, environment dependencies, and
roots that need machine or branch resolution. A one-task run is not automatically a shared
configuration concept. Task and config need not duplicate information; the pilot's excessive
indirection was primarily an implementation choice encouraged by an overly broad path rule.

**2. Make discovery latency an authoring constraint.** Add a short instruction to that same
reference: resolve paths without initializing the analysis environment, then measure an
unchanged status and build after registration. Report resolver cost separately from graph,
hashing, and execution cost. Subsecond warm status is a useful target for this small fixture,
not a universal threshold across machines or dataset sizes. The earlier
[TreasuryGIV pilot record](../task.md#what-the-pilot-taught-the-model) already says resolving
variables must stay cheap and describes a shell resolver checked against Julia. This pilot
repeated the mistake because the lesson was absent from the loaded authoring instructions.
Promote that specific lesson into the owning reference rather than adding another design essay
or mandatory workflow.

**3. Bind declared paths to actual reads and writes.** A reader that prefers a sandbox copy
can silently consume a different input from the canonical file named in `deps`. Offer two
supported patterns: inexpensive discovery that follows the same routing policy, or an explicit
task boundary enforced by passing the declared path to the producer or asserting it at execution.
The existing producer must honor that boundary; changing YAML alone does not force a read path.
If discovery uses a separate lightweight helper, share routing logic where practical and verify
agreement with the producer. Avoid solving latency by introducing an unchecked second routing
implementation or a cache that misses branch changes and newly created sandbox inputs.

**4. Provide one reusable pilot acceptance recipe.** Put the existing rerun expectations into
a compact reference checklist: first build and clean status; unchanged build; timestamp-only
change; producer and included-helper edits; environment changes; missing output; identical-output
suppression; corrupted-output rejection; restoration and final cleanliness. Record both reported
staleness and which steps actually executed: downstream status can be stale before an upstream
rebuild yet the downstream step can still skip after identical regeneration. Link this recipe
from the skill instead of requiring each project to reconstruct it from several references.

**5. Make a bounded pilot an explicit entry point.** Start with one producer and one meaningful
check at `tier: local`, with a named saved-input boundary. Distinguish freshness of that declared
slice from numerical validity and from end-to-end reproduction. Keep unrelated task registrations,
canonical promotion, and publication rebuilds outside the pilot unless requested. The original
full-pipeline pilot and this small adoption test serve different purposes and should remain easy
to invoke independently.

The immediate changes belong in
[graph-authoring](../../../../skills/reproducibility/references/graph-authoring.md),
[rerun-model](../../../../skills/reproducibility/references/rerun-model.md), and the
[skill's reference routing](../../../../skills/reproducibility/SKILL.md).
The current schema already supports explicit dependencies, shared runners, and simple root
variables. Consider task-local variables, resolver timing diagnostics, or resolving several roots
in one call only if the simpler authoring patterns prove insufficient. These would be separate
contract/CLI proposals, with clear variable precedence, path identity, and invalidation semantics.

A follow-up should rerun the same acceptance matrix after simplifying discovery, measure the
latency reduction, verify routing after a branch or sandbox-input change, and test whether an
agent using the revised skill chooses the smaller setup without extra coaching. This note records
design feedback only; it does not change the skill, CLI, or prior pilot approval state.
