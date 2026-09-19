# Project map navigation

The graph is one map of the active project. Only explicit task expansion changes the level of detail; selecting or inspecting never filters nodes.

## Navigation

- Project overview is always visible. It collapses groups and fits all top-level tasks, preserving selected-step details.
- Task chevrons expand/collapse one level in place, preserving other branches and nested expansion choices.
- Clicking a task or step selects it in the shared reader without changing the viewport or map contents.
- Global search and linked steps reveal the target's ancestors and bring the target into view without removing peers.
- Folding an ancestor retains selected-step details and marks the containing collapsed task. Show in graph reveals it again.
- Pan, pinch, zoom buttons, Fit, and keyboard navigation remain available.

## Connections and inspection

One arrow represents each visible endpoint pair. Arrow evidence retains every connecting file and logical prerequisite. Uses and Used by group direct connections by step and list their files. Selection highlights related arrows without hiding unrelated nodes.

The shared reader retains declaration/comments, task status, reproduction state and reason, command, inputs, outputs, tier, checks, accepted evidence, actual run metadata, and logs. Reproduction tier belongs in details, not a visibility filter.

## State and compatibility

Shareable graph state contains selection and expansion. Legacy scope/trace/tier URLs normalize to the full map, retaining valid selection and expansion and revealing legacy selected targets. New links preserve deliberately folded selection. Back/Forward and worktree switching restore their own navigation and viewport. Status-only refresh preserves layout and selection.

Step citations use relative Markdown links to `task.md#step-<name>` or same-task `#step-<name>`. The step name is the existing declaration identity; the target file must own that step. Dashboard URLs use `#/<task>?step=<name>` and retain the worktree selector. Missing steps or wrong owners produce an explicit message. Rendered step rows expose matching HTML anchors; generic Markdown viewers open the task file without guaranteed step jumping.

## Acceptance

- Overview is available from deep legacy URLs, selected steps, and collapsed groups.
- Selection preserves siblings, nodes, camera position, and unrelated expansions.
- Folding retains selected-step details; Show in graph restores the step.
- Search reaches any task/step across tiers; no trace/scope/filter controls remain.
- Grouped arrows and Uses/Used by preserve all evidence.
- Relative, same-task, shared, invalid, and offline step links behave consistently.
- Existing comments, history, refresh, responsive reader sizing, dark mode, keyboard/touch input, logical-only tasks, and error visibility remain intact.
- Exercise synthetic graphs, the 500-step fixture, and a read-only snapshot of the research graph. Record browser availability and limits honestly.
