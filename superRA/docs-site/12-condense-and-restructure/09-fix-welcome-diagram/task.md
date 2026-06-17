---
title: "Rework the Three-Phase Diagram on the Welcome Page"
status: implemented
depends_on:
  - 08-polish-prose-and-leaks
tags: []
created: 2026-06-17
---

## Objective

The three-phase (PLAN → IMPLEMENT → INTEGRATE → finished) diagram on `docs/site/01-welcome/task.md` renders badly in doc-mode. The phase boxes and "finished" pill stack fine, but the **"plan change loops back to PLAN"** element — a dashed vertical line + arrow + caption — floats detached to the right, disconnected from the boxes, so the loop-back reads as a stray sidebar rather than a cycle returning to PLAN.

Rework the diagram so the feedback loop reads clearly as "a plan change routes back to PLAN," and the whole thing looks clean in the rendered doc-mode page.

- **Reference the README's diagram** (repo-root `README.md`) — it draws the same PLAN→IMPLEMENT→INTEGRATE flow with Mermaid and reads cleanly. First determine whether the doc-mode dashboard renders Mermaid: if it does, prefer replacing the hand-built HTML with a Mermaid diagram consistent with the README's; if it does not, fix the inline HTML/CSS so the loop-back connects visually to the flow (a proper return edge to PLAN, not a free-floating dashed line).
- Keep the same information: the three phases with their one-line contents, the "finished" end state, and the "plan change loops back to PLAN" feedback edge.
- This is a presentation fix only — do not change the surrounding prose or the Design Philosophy section.

**Verify against the live rendered output, not the source.** The doc-mode preview is already served (`./superRA/superra dashboard --doc-mode --root docs/site`); load the Welcome page and confirm the diagram renders correctly (loop-back connected, no floating/overlapping elements, no broken layout) before declaring done. Record what rendering approach you used (Mermaid vs fixed HTML) and why in `## Results`.

## Planner Guidance

If Mermaid is not supported in doc-mode, the minimal fix is to anchor the loop-back as a labeled return arrow within the same vertical flow (e.g. an edge from INTEGRATE/finished back up to PLAN), rather than a separate right-hand column with a dashed line that has nothing to connect to. Match the page's existing color variables.

## Results

**Approach: fixed inline HTML/CSS (not Mermaid).** Doc-mode does not render Mermaid in task bodies. Task bodies are rendered client-side by `renderMarkdown` via markdown-it ([base.html:2162](../../../../skills/task-tree/scripts/templates/base.html#L2162)), which does no Mermaid post-processing; Mermaid is wired only into the dedicated DAG tab's `.mermaid` div ([dag.html:81](../../../../skills/task-tree/scripts/templates/dag.html#L81)), and the served doc-mode page loads no Mermaid script at all (verified by dumping `http://localhost:8995/` — the only "mermaid" hit is a code comment). A ` ```mermaid ` block in the welcome body would render as a plain code block, so Mermaid was not an option; I fixed the inline HTML/CSS per the planner's fallback guidance.

**Change** ([01-welcome/task.md:31-55](../../../01-welcome/task.md#L31-L55)): replaced the free-floating right-hand dashed column with a left-gutter return edge inside the same single-column flow. The loop-back is now an L-shaped dashed bracket (top + left + bottom borders, rounded corners, `var(--accent)`) running up the left gutter from below the flow and turning into the top-left of the PLAN box, capped by an upward arrowhead (`▲`) that feeds into PLAN. The italic "plan change loops back to PLAN" label sits centered on the return edge. All information is preserved: the three phase boxes with their one-line contents, the `finished` end-state pill, and the feedback edge. Surrounding prose and the Design Philosophy section are untouched. Color tokens reuse the page's existing variables (`--accent`, `--border`, `--bg-card`, `--text-mid`, `--text-mute`, `--st-ok`, `--st-ok-t`, `--shadow-sm`).

**Verification against the live rendered output.** Rendered the served page (`http://localhost:8995/#/01-welcome`) headlessly and measured the diagram's DOM geometry:

- Return-edge right border at x=426 meets the PLAN box left edge at x=425 — the loop-back is visually connected, not floating.
- The dashed bracket spans the full flow height (y≈1118→1486, just below PLAN down to the `finished` pill row), so it reads as returning from the end of the flow back to PLAN.
- The upward arrowhead sits at the PLAN box's left edge pointing into it.
- No element overlaps the phase boxes (all flow boxes start at x=425; the gutter occupies x=308–426).

Rendered result:

![The reworked three-phase diagram: PLAN, IMPLEMENT, INTEGRATE boxes and a finished pill in a single column, with a dashed return edge looping up the left gutter into PLAN labeled "plan change loops back to PLAN".](attachments/welcome-diagram-rendered.png)
