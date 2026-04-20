# RESULTS: User-Facing Doc Polish + Initial Release Prep

**Objective.** Turn the committed crude draft of `README.md` + `CLAUDE.md` into shippable documentation and prepare adjacent user-facing docs for an initial release.

**Status.** Plan approved; execution in progress.

---

## Task 1a: Mermaid workflow diagram for README

**Status:** IMPLEMENTED — awaiting review.

**Artifact:** [`docs/drafts/workflow-diagram.mmd`](docs/drafts/workflow-diagram.mmd) — self-contained Mermaid diagram ready for Task 1b to embed verbatim in README §Plan-Implement-Integrate Workflow.

**Design choices:**

- `flowchart TB` with two subgraphs. IMPLEMENT uses `direction LR` to visually compress the implementer ↔ reviewer loop into a tight horizontal pair. INTEGRATE stays `TB` with Phases A → B → C → D as a vertical chain.
- Shows only what the Task 1a constraints require: the three phases, the implementer/reviewer loop with APPROVE/REVISE labels, Phases A–D with one-line labels, two dotted `scope change (§User Feedback and Changing Plans)` arrows from IMPLEMENT and INTEGRATE back to PLAN, and a `merged` terminal node off Phase D. Explicitly excludes: skill-load manifest detail, cross-cutting skills rail, stage → reference mapping (those live in `using-superRA`).
- Density compared to the prior Workflow Map (archived at `git show 3970828^:README.md`): seven phase nodes vs. eight phase nodes + a cross-cutting rail + per-node skill/reference listings. New diagram is ~1/3 the ink of the old one — user-facing onboarding, not architectural reference.

**Validation:** Rendered cleanly via `npx @mermaid-js/mermaid-cli` to `/tmp/diagram-test.svg` (69 KB SVG, no warnings). GitHub Mermaid uses a compatible feature subset — no mermaid-cli-only syntax used (no `icon:`, no `@{ ... }` shorthand, standard `classDef` / `subgraph` / `direction` only).

## Task 1b: Rewrite README.md as a careful user-facing doc

**Status:** Not started

## Task 2: Consolidate CLAUDE.md as the developer / contributor doc

**Status:** Not started

## Task 3: Update plugin.json + marketplace.json descriptions

**Status:** Not started

## Task 4: Verify + modernize installation instructions

**Status:** Not started

## Task 5: Cross-reference + terminology sweep across all docs

**Status:** Not started

## Task 6: Final human read-through + release tag decision

**Status:** Not started
