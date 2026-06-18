---
title: "Merge Proportionality: Trivial-Sync Fast Path in semantic-merge + superintegrate"
status: approved
depends_on: []
tags: []
created: 2026-06-17
---

## Objective

Make branch integration scale its effort to the merge's actual risk, so a trivial sync is not forced through the full intent-investigation discipline or the slow author→reviewer dispatch round-trip.

**Why this exists.** `semantic-merge` framed every merge as a deep one — all modes walk the six shared steps and the full Semantic Coherence Checklist, with the checklist preamble stating "Walk every item." Its only bypass was the parallel-worktree Exception. `superintegrate` Sync had a single bypass too — the already-synced ancestor no-op — and otherwise always dispatched a generic sync author followed by a generic sync reviewer in series. There was no middle ground: a clean fast-forward or an independent merge got the same heavyweight treatment as a genuine conflicting one, paying both full investigation and the slow dispatch ceremony.

The two gaps live in different homes and are fixed separately:

- **Merge *depth*** is owned by `semantic-merge` (and must be fixed there so the standalone path, which has no orchestrator above it, also benefits).
- **Dispatch *ceremony*** is owned by `superintegrate` Sync.

**Done when:** a merge that applies with no conflicts, touches no file the current branch also changed since the merge base, and renames/moves/redefines nothing current-branch code references — is landed inline with only a bounded stale-reference sweep, skipping intent synthesis / resolution plan / escalation; and in the workflow path the orchestrator lands it in Direct mode and skips the sync author + sync reviewer dispatch, with Integrate's reviewer pass over `BASE_HEAD_SHA..HEAD` as the verification. Any failed condition, or genuine doubt about whether overlap/a rename reaches current-branch code, returns to the full deliberate path.

### Constraints

- **Predicate defined once, pointed to elsewhere (DRY).** The trivial-merge predicate lives in `semantic-merge §Scope the merge first`; `superintegrate` Step 3 points to it rather than restating it.
- **The gate stays honest.** The fast path is a proportionality clause, not an opt-out of quality control. The stale-reference sweep still runs (bounded to the near-empty reach) and is what validates the trivial scoping; the moment any predicate clause fails the merge gets full treatment. When unsure, treat as non-trivial.
- **Skill authoring discipline.** Both files are workflow skills: `skill-creator` loaded before editing; every added instruction line self-applied against the repo `CLAUDE.md` "Teach the Protocol" two-test gate (DRY + Necessity).

### Context

- `semantic-merge` Shared Steps and Semantic Coherence Checklist are authoritative for merge depth across all three modes (workflow sync author, workflow sync reviewer, standalone). The new scoping clause sits after Step 1 grounding (which yields conflict status, touched-file set, incoming range — the inputs the predicate needs) and is non-numbered to avoid renumbering the existing Step 2–6 cross-references.
- `superintegrate` Sync Step 3 already had the already-synced ancestor no-op; the triage is added between that no-op and the author dispatch. Integrate's existing reviewer pass over `BASE_HEAD_SHA..HEAD` is the safety net for a Direct-mode-landed trivial sync, consistent with the very-minor-fix re-review allowance (commit `5af4c27d`).

## Results

### Key Findings

Branch integration is now proportional to merge risk. The trivial-merge predicate (clean apply, empty file overlap, no cross-cutting rename) is defined once in `semantic-merge` and referenced from `superintegrate`; failing any clause, or doubt, falls back to full treatment.

- **`skills/semantic-merge/SKILL.md`** — added a non-numbered `### Scope the merge first` subsection after Step 1 that defines the trivial predicate and authorizes landing such a merge with only the bounded Step 6 stale-reference sweep, skipping intent synthesis / resolution plan / escalation. The Semantic Coherence Checklist preamble (was a flat "Walk every item") now states that a trivially-scoped merge satisfies the intent-preservation and resolution items by construction and need only confirm the verification items, with the stale-reference sweep validating the scoping. This fixes the standalone path as well, which has no orchestrator to triage above it.
- **`skills/superintegrate/SKILL.md`** — the Sync section intro now distinguishes a trivial sync (lands inline in Direct mode) from a non-trivial one (serialized author→reviewer). Step 3 sizes the sync against `semantic-merge §Scope the merge first` (pointer, not restatement); on trivial it announces the Direct-mode switch, lands inline, skips the author + reviewer dispatch, and proceeds to Integrate whose reviewer pass over `BASE_HEAD_SHA..HEAD` verifies the landed merge. Non-trivial dispatches the author as before.

### Notes

- The three `semantic-merge` mode references were checked for contradicting "always full treatment" language; none conflict. The sync-reviewer's "every kept/dropped/synthesized hunk has a rationale" line only applies when a reviewer is actually dispatched (the non-trivial path), so it needed no change.
- Independent review APPROVED (no CRITICAL/MAJOR). Confirmed the predicate closes the same-file auto-merge and incoming-only-rename holes, the doubt-fallback covers residual risk, and Integrate's `BASE_HEAD_SHA..HEAD` pass is a real backstop for the skipped sync reviewer. Two MINOR coherence nits were folded in: the superintegrate Dispatch Convention now qualifies "a non-trivial Sync uses …" rather than over-claiming the author/reviewer agents for all syncs, and the Sync Step 3 heading is "Sync the branch when needed" (it may land inline without dispatch).
