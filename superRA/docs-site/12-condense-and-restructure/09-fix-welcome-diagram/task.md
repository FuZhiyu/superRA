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

**Change** ([01-welcome/task.md:31-55](../../../01-welcome/task.md#L31-L55)): replaced the free-floating right-hand dashed column with a return edge drawn as a single inline SVG `<path>` inside the left gutter of the same single-column flow. The gutter is a fixed-width (118px) flex child of the `align-items:stretch` diagram container, so it stretches to the full flow height; the SVG fills it (`position:absolute;inset:0;width:100%;height:100%`) with `viewBox="0 0 118 100" preserveAspectRatio="none"` and `vector-effect="non-scaling-stroke"`, so the path geometry maps deterministically to the gutter's actual pixel box regardless of how tall the phase boxes grow. The path traces a closed bracket: a horizontal **bottom arm** from the flow's left edge at the `finished`-pill row, a rounded corner into the **left arm** running up the gutter, a rounded corner into the horizontal **top arm**, ending at PLAN's top-left edge where an HTML `▶` arrowhead points into the box. The italic "plan change loops back to PLAN" label sits centered on the left arm with a `var(--bg)` background mask so the dashes read cleanly behind it. All information is preserved: the three phase boxes with their one-line contents, the `finished` end-state pill, and the feedback edge. Surrounding prose and the Design Philosophy section are untouched. Color tokens reuse the page's existing variables (`--accent` for the edge/arrow, `--bg` for the label mask; the phase boxes keep `--border`, `--bg-card`, `--text-mid`, `--text-mute`, `--st-ok`, `--st-ok-t`, `--shadow-sm`).

Why SVG and not collapsing CSS borders: the previous CSS bracket div used `right:0` with no `width`/`left`, so its content box collapsed to ~2px and the `border-top`/`border-bottom` "arms" rendered as zero-length curls (the rejected render). The SVG path's coordinates are independent of any content-box width, so both horizontal arms have real, deterministic length.

**Verification against the live rendered output.** Rendered the served page (`http://localhost:8995/#/01-welcome`) headlessly (Playwright/Chromium) at widths 820/560/420 and measured the path's actual screen-space endpoints against the box bounding rects. Both ends attach to the flow at every width (numbers below are the 820px render; 560/420 match within a few px):

- **Bottom arm (origin):** the path's bottom endpoint lands at x=137, y=1471 — x=137 is the flow column's left edge (PLAN/IMPLEMENT/INTEGRATE/finished all start there) and y=1471 sits inside the `finished` pill's vertical band (pill y[1436–1475]). So the horizontal bottom arm runs from the gutter across to the flow edge level with the `finished` row: the loop visibly *originates from the end of the flow*, no dangling stub.
- **Top arm (arrival):** the path's top endpoint lands at x=140, y=1059, and the `▶` arrowhead's center sits at x=137, y=1055 — exactly PLAN's top-left corner (PLAN box x[137–580], top y=1055). The arrow points into PLAN.
- **No overlap:** the gutter occupies x≈20–138 and every phase box starts at x=137, so the return edge never overlaps the boxes.
- Layout holds at 420px (text wraps inside boxes; both arms still connect) — see the narrow-width capture description; no broken layout or floating elements at any tested width.

Rendered result (full, uncropped, 560px — the diagram's `max-width`):

![The reworked three-phase diagram: PLAN, IMPLEMENT, INTEGRATE boxes and a finished pill in a single column. A dashed return edge runs as a closed bracket — out from the flow's left edge at the finished-pill row, up the left gutter, and back into PLAN's top-left corner with an arrowhead — labeled "plan change loops back to PLAN" on the left arm.](attachments/welcome-diagram-rendered.png)

## Review Notes

1. **MAJOR** — [01-welcome/task.md:32-35](../../../01-welcome/task.md#L32-L35): The bottom (origin) of the return edge dangles in empty space, so the loop-back is still partly the "free-floating dashed line ... disconnected from the boxes" the objective set out to remove — just relocated from the right sidebar to the bottom-left.

   Verified against the **live** doc-mode render (`http://localhost:8995/#/01-welcome`, headless, widths 820/560/420). The dashed return edge connects cleanly into PLAN at the **top** (arrowhead at the PLAN box's left edge — that end is good), but at the **bottom** it ends in blank space roughly level with the `finished` pill, ~170px to the left of it, with **no horizontal connector** to INTEGRATE, the `finished` pill, or anything in the flow. A reader sees a dashed line emerging from nowhere. The fix needs an actual return path that visibly *originates* from the end of the flow (e.g. a horizontal segment from below INTEGRATE / the `finished` row over to the gutter, then up), not just a vertical stub.

   Root cause: the bracket div ([01-welcome/task.md:33](../../../01-welcome/task.md#L33)) is positioned with `right:0` and **no `width` or `left`**, so its content box collapses (measured bounding box width = 2px). The `border-top` / `border-bottom` you added therefore render as ~0-length corner curls, not the horizontal arms described in `## Results`. The element is effectively a single vertical dashed line with rounded stubs — it is not the "L-shaped bracket (top + left + bottom borders) ... turning into the top-left of the PLAN box" that `## Results` claims. Give the bracket a real width spanning from the gutter to the box edge (or restructure the return path) so the bottom arm actually reaches the flow.
   → implemented: replaced the collapsing-border CSS bracket with an inline SVG `<path>` whose geometry is content-box-independent ([01-welcome/task.md:32-36](../../../01-welcome/task.md#L32-L36)). The path now has a real horizontal bottom arm from the flow's left edge at the `finished`-pill row, up the gutter, into PLAN's top-left with the `▶` arrowhead. Verified on the live render at 820/560/420: bottom endpoint at x=137 (flow left edge), y inside the `finished` band; top endpoint + arrowhead at PLAN's top-left corner — both ends attach, nothing dangles.

2. **MAJOR** — [task.md:30](task.md#L30) and [task.md:35](task.md#L35): `## Results` materially misdescribes the rendered output, so it is not the self-contained, accurate account the task interface requires. Line 30 claims an "L-shaped dashed bracket (top + left + bottom borders ...) ... turning into the top-left of the PLAN box"; line 35 claims the bracket "spans the full flow height ... down to the `finished` pill row, so it reads as returning from the end of the flow back to PLAN." Neither holds: there is no rendered bottom arm and the line stops short of the flow's end with a visible horizontal gap (see item 1). The reported x=426/x=425 connection is true only for the **top** arrival into PLAN. Update `## Results` to describe what actually renders once the origin connection is fixed, and re-capture `attachments/welcome-diagram-rendered.png` (the committed screenshot crops off the dangling bottom, so it does not surface the defect).
   → implemented: rewrote `## Results` to describe the SVG-path approach and the measured endpoints that actually render (bottom arm at flow edge / `finished` row; top arm + arrowhead at PLAN top-left), and replaced `attachments/welcome-diagram-rendered.png` with a full, uncropped 560px capture showing the complete bracket including the bottom arm.

Confirmed sound (no action needed): the Mermaid-unsupported determination (verified against served HTML + `base.html`/`dag.html`); prose paragraph and Design Philosophy section untouched (diff confined to lines 31-55); `docs/build_site.sh` builds clean; no phase-box overlap and layout holds at narrow widths; all information preserved (three phases + contents, `finished` pill, feedback label).
