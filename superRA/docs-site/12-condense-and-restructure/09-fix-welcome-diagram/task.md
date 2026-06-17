---
title: "Rework the Three-Phase Diagram on the Welcome Page"
status: approved
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

**Approach: one self-contained inline SVG mimicking the README's Mermaid flow (not Mermaid itself).** Doc-mode does not render Mermaid in task bodies — they are rendered client-side by `renderMarkdown` via markdown-it ([base.html:2162](../../../../skills/task-tree/scripts/templates/base.html#L2162)), which does no Mermaid post-processing; Mermaid is wired only into the dedicated DAG tab's `.mermaid` div ([dag.html:81](../../../../skills/task-tree/scripts/templates/dag.html#L81)). Raw inline HTML/SVG *is* passed through, so the fix is a single inline `<svg>` that reproduces the look of the README's Mermaid diagram.

**Change** ([01-welcome/task.md](../../../01-welcome/task.md)): replaced the prior hand-built flex/HTML diagram (and its earlier free-floating left-gutter bracket) with one `<svg viewBox="0 0 560 324" style="width:100%;height:auto">`. Because the whole figure is a single SVG scaled by `viewBox` (default `xMidYMid meet`), it scales uniformly like Mermaid's own output — nothing reflows, so every element stays aligned at any width. Contents mirror the README Mermaid: three phase boxes (`<rect>` + left accent tick + `<text>`/`<tspan>`) for PLAN/IMPLEMENT/INTEGRATE, three muted down-arrows (`<line marker-end>`) into a green `finished` pill, and **two** dashed accent return edges drawn as cubic `<path>`s curving up the left side — one from IMPLEMENT's left edge, one from INTEGRATE's left edge — each ending in an arrowhead `<marker>` on PLAN's left edge, with an italic "plan change" label masked by a `var(--bg)` rect. Color tokens reuse the page variables (`--accent` for edges/titles/ticks/arrowheads, `--text-mute` for down-arrows, `--st-ok`/`--st-ok-t` for the pill, `--border`/`--bg-card`/`--text-mid` for the boxes). Surrounding prose and the Design Philosophy section are untouched.

Why a single full SVG and not HTML boxes + an overlay: HTML boxes reflow at narrow widths (the long INTEGRATE line wraps), which changes box heights and breaks any fixed-coordinate return edge — the failure mode behind the earlier rejected renders. A single uniformly-scaled SVG never reflows, so the edge endpoints are deterministic, exactly as Mermaid achieves it.

**Verification against the live rendered output.** A reviewer rendered the served page (`http://localhost:8995/#/01-welcome`) headlessly (Playwright/Chromium) at widths 820/560/420 and measured actual screen geometry — APPROVE. Key measurements (SVG user units, from rendered `getBBox` + path `d`):

- **IMPLEMENT→PLAN edge:** start `(170, 122)` on IMPLEMENT's left edge → end `(168, 46)` into PLAN; rendered bbox x∈[129, 170] (curves left, never enters the box interior x>170); accent arrowhead lands on PLAN's left edge.
- **INTEGRATE→PLAN edge:** start `(170, 214)` on INTEGRATE's left edge → end `(168, 34)` into PLAN; rendered bbox x∈[96, 170]; bulges wider (x=96) than the IMPLEMENT edge (x=129) so the two never overlap.
- **Down arrows** at x=356 connect each box bottom→next top (70→94, 162→186, 254→278); the last lands on the `finished` pill (top y=282).
- **Uniform scaling:** aspect ratio 560/324 held at all three widths — no distortion, no reflow, non-zero bbox everywhere. All phase-text right edges ≤423 < box right 542 (no clipping). Theme colors resolve (accent `rgb(180,77,45)`, pill `rgb(212,232,212)`); no black/unstyled fallback.

Rendered result (full, uncropped, 560px — the diagram's `max-width`):

![The reworked three-phase diagram: PLAN, IMPLEMENT, INTEGRATE boxes in a single column with down-arrows to a green "finished" pill, and two dashed "plan change" edges curving up the left side into PLAN, each with an arrowhead.](attachments/welcome-diagram-rendered.png)
