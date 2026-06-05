---
title: "Mobile phone & iPad touch UI"
status: approved
depends_on: []
tags: []
created: 2026-06-04
---

## Objective

Make the HTML dashboard genuinely usable on iPhone and iPad without regressing the desktop experience. The responsive model shipped by [`view-navigation/a11y-responsive`](../view-navigation/a11y-responsive/task.md) (approved) was built for a desktop mouse plus a narrow-*width* drawer fallback. It breaks on real touch devices in two ways:

- **The unpinned sidebar is hover-reveal only.** Unpinned mode retracts the sidebar to a pointer-transparent rail and reveals it on `mouseenter`, hiding on `mouseleave`. A touch device has no hover, so an unpinned sidebar is **unreachable by tap** — the user is stuck with no navigation.
- **Mode is chosen by raw width (`window.innerWidth <= 860`).** So iPad landscape (1024–1366px) and a 12.9" iPad held in portrait (1024×1366) fall into the desktop hover chrome rather than a touch-appropriate layout.

This workstream replaces the width-only model with a capability- and orientation-aware one for touch devices, and adds the touch ergonomics (tap targets, safe areas, scroll containment, reachable search) the desktop build never needed.

**Scope decisions (set with the researcher):**

- **Touch/responsive adaptation only** — preserve the dashboard's current visual identity; this is not a restyle.
- **Touch sidebar is pinned-or-drawer, never hover** — the hover-reveal unpinned mode is desktop-mouse only.
- **Phone search/filter stays reachable** behind an icon, not dropped.

Two leaves: [`01-touch-sidebar`](01-touch-sidebar/task.md) does the load-bearing sidebar/breakpoint/orientation model (the piece most likely to break); [`02-touch-polish`](02-touch-polish/task.md) layers tap targets, the phone search affordance, safe-area content insets, and scroll ergonomics on top of it.

### Conventions

- **Single source of truth:** every UI change goes in [`skills/task-system/scripts/templates/base.html`](../../../../skills/task-system/scripts/templates/base.html). It is the one dashboard source — the live FastAPI server renders it directly, and the static export (`uv run --project skills/task-system superra dashboard export`) renders the same file in standalone mode. Do not hand-edit the generated `superRA/dashboard.html`; regenerate it with the export command to spot-check the static path.
- **Load `frontend-design:frontend-design`** before touching markup or CSS.
- Reuse the existing theme tokens, transition curves, and the `@media (prefers-reduced-motion: reduce)` discipline already in `base.html`. Keep the htmx/router boundary intact — no `setActive` from the SSE channel.

### Constraints

- **Preserve the existing visual identity.** Fonts, color tokens, spacing density, and the desktop sidebar chrome stay as they are. Touch/responsive adaptation, not a new mobile aesthetic.
- **Desktop mouse behavior must be unchanged in effect.** The existing pinned / unpinned-hover-reveal / drawer model on a fine-pointer + hover device stays exactly as it is. All touch behavior is **additive and guarded by capability detection** (`matchMedia('(hover: none)')` / `'(pointer: coarse)'`), never by rewriting the mouse paths.

### Context — verification (real device path, not CSS-only)

Playwright (Python, 1.60.0) with device descriptors is available; per the project's UI-verification discipline, assert the **rendered touch behavior**, not just that a CSS rule exists. Drive the live server (`uv run --project skills/task-system superra dashboard --foreground --no-open --port <p>`) with `hasTouch`/`isMobile` contexts at representative sizes — iPhone (≈390×844), iPad portrait (768×1024 and 1024×1366), iPad landscape (1024×768 and 1366×1024) — and check the DOM/behavior (which mode class is on `.workspace`, that the sidebar is reachable by tap, that hover handlers never fire). Then confirm a desktop mouse context is unchanged. Keep the baseline green: `cd skills/task-system/scripts && pytest test_dashboard.py test_task_system.py`, and run `node --check` on the extracted client JS. Cheap template-level regression assertions in `test_dashboard.py` (e.g. `viewport-fit=cover` present, safe-area / coarse-pointer CSS present in the rendered output) are welcome but the behavioral Playwright drive is the gate.

## Results

The dashboard is now touch-correct on iPhone and iPad with the desktop mouse experience unchanged in effect. Both leaves are approved; all changes live in the single dashboard source [`base.html`](../../../../skills/task-system/scripts/templates/base.html) (served live and exported identically), plus regression tests in `test_dashboard.py`. The test baseline rose 365 → 383.

- **[`01-touch-sidebar`](01-touch-sidebar/task.md)** — closed the hover-reveal dead end: a cached, reactive `sbIsTouch()`/`sbIsPortrait()` capability check routes `applySidebarMode()` down a touch path that never enters the unreachable `.sb-unpinned` state. On touch the pin toggle is **pinned ↔ drawer**; mode is chosen by capability + orientation, so a 1024×1366 portrait iPad gets tablet behavior while a true 1024px desktop window keeps mouse chrome. Hover-rail and drag-resizer are inert on touch; `viewport-fit=cover` + header/drawer safe-area insets added. A real bug was caught here — the hamburger is a sibling of `#workspace`, so drawer mode is mirrored onto `<body>` to keep it reachable. Reviewer re-drove the full touch matrix; desktop verified unchanged.
- **[`02-touch-polish`](02-touch-polish/task.md)** — ≥44px tap targets gated behind `@media (pointer: coarse)` (desktop density untouched); the phone search/filter sheet **adopts** the existing `#search-box`/`#filter-status` so `applyFilters()` stays single-sourced; content safe-area insets; overscroll containment, tap-highlight suppression, and DAG/Kanban scroll affordances. Two MAJOR cascade defects (the phone trigger leaking onto iPad via a coarse `display` group, and the caret's 44px hit area defeated by a later unconditional rule) were caught in review and fixed with red-green regression tests.

**Verification:** Playwright touch drive across iPhone / iPad portrait 768 & 1024 / iPad landscape 1024 & 1366 / desktop mouse, plus rotation and reduced-motion cases; `pytest test_dashboard.py test_task_system.py` green (orchestrator re-run: 381 passed locally, 2 playwright-rendered tests skip without a browser and were red-green-verified in the agent env); `node --check` on the extracted client JS passes.
