---
title: "Glossary"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

superRA uses a small set of terms with precise meanings.
Each is defined once here; other pages link back rather than redefine.

**Task tree**
The `superRA/` directory of `task.md` files that represents a project's work.
The filesystem hierarchy is the task hierarchy: subdirectories are child tasks, sibling `depends_on` fields wire execution order, and parent status rolls up from children automatically.
See [Concepts: The Task Tree](#/03-concepts/02-the-task-tree) for the full model.

**Task**
A single `task.md` file together with its directory.
A leaf task has no child tasks and carries `script`, `input`, and `output` frontmatter.
A branch task has children and frames their shared context in its `## Objective`.
Every task has a `status` and, optionally, `depends_on` siblings.

**Frontier**
The set of leaf tasks that are ready to dispatch right now — their status is `not-started` (or an interrupted `in-progress`) and all `depends_on` siblings are `approved`.
The orchestrator dispatches frontier tasks; as they reach `approved`, their downstream dependents join the frontier.
See [Status and Frontier](#/05-reference/03-status-and-frontier).

**Status rollup**
The automatic propagation of child statuses up to their parent.
A branch task's displayed status is computed from its children, not stored independently — `approved` only when all active children are `approved`.

**Stage**
The `Stage:` field in an agent dispatch that determines which skills are loaded.
Valid values: `implementation`, `planning-review`, `protection`, `sync`, `integration`, `documentation`.
See [Skills and Agents Reference](#/05-reference/04-skills-and-agents) and [skills/using-superra/SKILL.md §Skill-Load Manifest](skills/using-superra/SKILL.md).

**Domain skill**
A skill that carries vertical-specific discipline for a research domain (data analysis, theory/modeling, writing).
Domain skills load on top of the workflow skill when the task touches their domain, adding field-specific protocols without forking the workflow.
See [Concepts: Skills and Agents](#/03-concepts/04-skills-and-agents).

**Drift test**
A lightweight regression check committed alongside a result to guard it from unintended future changes.
Drift tests are the default mechanism of the `result-protection` skill and are created during the Protect step of INTEGRATE.
See [Concepts: Integration and Protection](#/03-concepts/05-integration-and-protection).

**Semantic merge**
An intent-aware branch integration performed by the `semantic-merge` skill.
Instead of accepting every incoming change blindly, semantic merge classifies conflicts by intent, escalates intent-changing decisions to the researcher, sweeps stale references, and leaves a propagation trail so the post-sync diff is coherent and every commit leaves existing protection tests passing.
See [Concepts: Integration and Protection](#/03-concepts/05-integration-and-protection).

**Direct mode**
An execution mode where the main agent implements a task itself rather than dispatching a subagent implementer/reviewer pair.
Direct mode is appropriate for small, clearly-scoped tasks; subagent mode is the recommended default.
See [skills/using-superra/SKILL.md §Execution Modes](skills/using-superra/SKILL.md).

**Subagent mode**
The default execution mode: the main agent dispatches a separate implementer subagent and a separate reviewer subagent for each task, enforcing adversarial review.
See [Concepts: Roles and Review](#/03-concepts/03-roles-and-review).

**Implementer**
The agent role that executes a task — writes the code, fills `## Results`, and sets `status: implemented`.
See [agents/implementer.md](agents/implementer.md).

**Reviewer**
The agent role that independently verifies an implemented task and renders a verdict of `APPROVE` (sets `status: approved`) or `REVISE` (sets `status: revise` with `## Review Notes`).
See [agents/reviewer.md](agents/reviewer.md).

**APPROVE / REVISE**
The two verdicts a reviewer can render.
`APPROVE` advances the task to `approved`; `REVISE` returns it to the implementer with findings recorded in `## Review Notes`.
