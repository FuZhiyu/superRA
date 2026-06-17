---
title: "Context Model and Point-vs-Distill in Task Files"
status: approved
depends_on: []
tags: []
created: 2026-06-17
---

## Objective

Correct how superRA instructs planners to put context/conventions into a task file: replace the "self-contained / zero project context" framing with the real working-context model, and make the point-vs-distill choice explicit so planners point to authoritative sources instead of copying them — without losing human readability for reviewers.

### Context

superRA's task-context guidance currently implies a task must be a self-contained context bubble. Two lines drive that and conflict with how the repo actually works:

- `skills/superplan/references/task-tree-design.md:18` — "implementer with zero project context can work … after reading the task objective plus the ancestor chain." Too absolute: it ignores that the agent already has auto-loaded `CLAUDE.md`/`AGENTS.md` (project-level plus nested ones in directories it reads), manifest-loaded skills, and on-demand directory walking.
- `skills/task-tree/references/task-file-contract.md:34` — "they do not need to re-walk project guidance docs when the governing objectives already contain the needed conventions." This pushes planners to copy conventions into objectives.

The repo's own contracts already contradict the bubble: the direct-mode role specs (`skills/using-superRA/references/direct-mode-implementer.md:19`, `direct-mode-reviewer.md:19`) tell agents to walk directories on-demand when the ancestor chain does not cover a needed convention. The point-over-copy principle is the same one superRA's contributor gate states for skill prose — but these four files **ship as distributed skills and run in arbitrary projects** where superRA's repo-internal `CLAUDE.md` does not exist. So the shipped prose must state the principle in its own voice and justify it on its own terms (a second copy drifts; a concise pointer keeps the task readable), never by citing superRA's repo-internal contributor docs.

Researcher design intent (this session): when a convention is in an auto-loaded `CLAUDE.md`, point to it — copying only adds drift and maintenance cost — but a human reviewer reading the task should not have to click through to grasp the basics, so pointers must be self-orienting.

### The model and rule to encode

Agent working context = (a) auto-loaded `CLAUDE.md` / `AGENTS.md` — the project-level ones, plus any nested in a directory the agent reads, (b) manifest-loaded skills, (c) the assigned task + ancestor chain via `superra task read`, (d) on-demand directory walking when a touched file needs a convention not yet covered. The task's job is to make that assembled set sufficient — by pointing into it — not to reproduce it.

Planner's choice for a behavior-changing convention:

1. Already in the agent's standing context (auto-loaded `CLAUDE.md` / `AGENTS.md`, manifest-loaded skills) → point with a self-orienting line and path/anchor. Do not copy.
2. Reachable but not standing context, or living in one coherent doc (e.g. a data-directory `README`) → point with a self-orienting line and the location.
3. Scattered across multiple files / not reliably discoverable → distill a behavior-stating summary into the scoped `### Context` / `### Conventions` / `### Constraints` subsection, with a source pointer; stamp the walk date.
4. Task-specific context that lives nowhere else → state inline; no tradeoff.

A **self-orienting line states the convention's substance concisely** — the gist of what it requires and how it bears on this task — so a human reviewer grasps it without opening the link; the link carries full detail. A bare "see X" that names only a location is not self-orienting. This concise-substance line is what lets a pointer satisfy human readability in tiers 1–2 without reproducing the full rule text. Reserve inline reproduction of a rule's text for context that is task-specific or is itself the thing under review.

### Files to change

- `skills/superplan/references/task-tree-design.md` — reframe L18 to the working-context model (not "zero project context"); rewrite §Context Distillation to carry the point-vs-distill tiering above, keeping the "distill a behavior summary, not a verbatim excerpt" + walk-date guidance for the distill branch. State the point-over-copy principle in the section's own voice — remove the citation to superRA's root `CLAUDE.md` gate. Write the docs-walk guidance as a direct instruction (no "still happens" / past-referencing narration).
- `skills/task-tree/references/task-file-contract.md` — reframe §Context Inheritance L34 so it states the working-context model and that scoped subsections may hold pointers, not only distilled copies.
- `skills/superplan/SKILL.md:78` — the "Walk the project guidance docs and distill them into scoped objective context" line: make it "distill or point" consistent with the tiering.
- `skills/superplan/references/planning-review.md:11` — clarify that the handoff-readiness "human readability" gate is satisfied by self-orienting pointers; a correct pointer is not an under-distillation finding.

### Conventions

- Skill-authoring change: load `skill-creator` before editing any `SKILL.md`. Self-apply the DRY and Necessity tests to every added line (this is the superRA contributor-gate discipline applied to the *edit process* — it governs how you edit, and is not itself shipped prose).
- **Standalone usability.** The four reference files ship as distributed skills used by agents planning in other projects. Shipped prose must not cite superRA repo-internal docs (the root `CLAUDE.md` / `AGENTS.md` contributor gate), because they are absent in those projects; state any needed principle self-containedly. Cross-references to sibling skills/references that ship in the same bundle are fine. Sweep all four files for any reference that only resolves inside the superRA repo and remove/rephrase it.
- **Executable, non-narrating prose.** Write direct instructions. Do not use past-referencing or meta narration — "still happens", "as before", "we used to", "now also" — that presumes an instruction history the reading agent never saw.
- The direct-mode references (`direct-mode-*.md`) already align (they teach on-demand walking) and are generated files — do not hand-edit them; no change is needed there.

### Validation

- L18 and task-file-contract L34 no longer claim self-containment / "no need to walk"; both state the assembled working-context model.
- §Context Distillation carries the four-tier point-vs-distill rule and the self-orienting-pointer requirement; the distill branch keeps the behavior-summary + walk-date guidance.
- Auto-load scope is stated as project-level **plus nested `CLAUDE.md` / `AGENTS.md` in directories the agent reads**, not "project-root" only.
- Every self-orienting pointer the guidance describes carries a concise substance summary (gist of the convention), not just a location; a bare "see X" is explicitly called out as insufficient.
- The shipped prose in all four files cites no superRA repo-internal doc; the point-over-copy principle stands self-containedly. A grep of the four files for `CLAUDE.md` / `AGENTS.md` finds only project-agnostic uses, no citation of superRA's contributor gate.
- No reference uses past-referencing or meta narration ("still happens", "as before", etc.); instructions are direct.
- The four surfaces are mutually consistent — no surface still tells planners to copy auto-loaded conventions.
- No new line fails the DRY/Necessity tests; reviewer self-applies them line by line.
- direct-mode generated files untouched.

## Results

Reframed the task-context guidance across all four surfaces in one pass; the "self-contained / zero project context" framing is gone and the working-context model plus the point-vs-distill tiering now hold consistently.

### Changes

- [`task-tree-design.md:18`](../../../../skills/superplan/references/task-tree-design.md#L18) — replaced "implementer with zero project context … after reading the task objective plus the ancestor chain" with the assembled working-context model (auto-loaded `CLAUDE.md`/`AGENTS.md`, project-level plus nested-on-read; manifest skills; `task read` ancestor chain; on-demand directory walking) and the rule that the objective's job is to make that set sufficient by pointing into it, not to reproduce it. Cross-points to §Context Distillation.
- [`task-tree-design.md` §Context Distillation](../../../../skills/superplan/references/task-tree-design.md#L30) — the section carries the four-tier point-vs-distill rule: (1) standing context → self-orienting pointer, do not copy; (2) reachable / one coherent doc → self-orienting pointer plus the location; (3) scattered / not discoverable → distill a behavior summary with source pointer + walk date; (4) task-specific → inline. The point-over-copy rationale is stated in the section's own voice (a pointer keeps the task readable and leaves one source of truth; a copy drifts) with no citation to superRA's repo-internal contributor gate. The self-orienting line is required to state the convention's *substance* — the gist of what it requires and how it bears on the task — so a reviewer grasps it without clicking through; a bare "see X" naming only a location is explicitly insufficient. The docs-walk is a direct imperative that classifies each convention into a tier. The distill branch retains the behavior-summary + walk-date guidance.
- [`task-file-contract.md:34`](../../../../skills/task-tree/references/task-file-contract.md#L34) — §Context Inheritance no longer says agents "do not need to re-walk project guidance docs when the governing objectives already contain the needed conventions." It now states the working-context model and that a scoped subsection may hold a pointer, not only a distilled copy, deferring point-vs-distill to `task-tree-design.md` §Context Distillation.
- [`superplan/SKILL.md:78`](../../../../skills/superplan/SKILL.md#L78) — "Walk … and distill them into scoped objective context" → "Walk … then point to or distill each relevant convention," consistent with the tiering.
- [`planning-review.md:11`](../../../../skills/superplan/references/planning-review.md#L11) — handoff-readiness "human readability" now states that a correct self-orienting pointer to an auto-loaded doc / manifest skill is not an under-distillation finding; the finding to raise is copied rule text where a pointer would do.

### Standalone-usability sweep

The four files cite no superRA repo-internal contributor doc. The previous gate citation at `task-tree-design.md:34` is gone; the point-over-copy principle stands self-containedly in the section's own voice. A grep of the four files for `contributor gate` / `Teach the Protocol` / `A pointer is acceptable` returns nothing, and the remaining `CLAUDE.md` / `AGENTS.md` mentions are project-agnostic descriptions of auto-load behavior — fine for distributed skills. Cross-references between the four files (e.g. to `task-tree-design.md` §Context Distillation) are sibling-bundle references and ship together.

### DRY/Necessity self-check on added lines

Each added line shapes a non-default behavior (the working-context model, the tier choice, the substance requirement for a self-orienting line, what is/isn't a reviewer finding) or is a one-line echo that points to its owning section. No added line restates content another read surface already carries, and none cites a repo-internal doc.

### Validation

- L18 and task-file-contract L34 no longer claim self-containment / "no need to walk"; both state the assembled working-context model, with auto-load scope as project-level plus nested-on-read. ✓
- §Context Distillation carries the four-tier rule and the self-orienting-substance requirement (bare "see X" called out as insufficient); the distill branch keeps behavior-summary + walk-date. ✓
- Shipped prose cites no superRA repo-internal doc; the point-over-copy principle is self-contained. ✓
- No reference uses past-referencing or meta narration; the docs-walk is a direct imperative. ✓
- The four surfaces are mutually consistent — no surface tells planners to copy auto-loaded conventions; all defer point-vs-distill to one owner (`task-tree-design.md` §Context Distillation). ✓
- direct-mode generated files untouched (they already teach on-demand walking; no change needed). Confirmed not in the diff. ✓

## Planner Guidance

The change is prose-coherence across four tightly-coupled files; keep it as one implementer pass so wording stays consistent. A reviewer should walk all four surfaces together and apply the contributor gate, not just check the primary reference.
