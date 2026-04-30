# Audience Discipline (Modeling Prose)

Companion to `audience-discipline-writing.md`. Same root failure —
**perspective collapse**, the agent writing from inside its own context
rather than from inside the reader's head — applied to the prose that
surrounds equations: lemma statements, proof bodies, derivation
narrative, theory-appendix subsections.

Loaded on demand whenever a task writes or revises modeling prose
(propositions, lemmas, proofs, derivations, model-section narrative).

## Why modeling prose is especially leak-prone

Two structural reasons:

1. **Modeling work has a natural meta-commentary register.** Sentences
   like "the cleanest illustration is ...", "I prove this in two
   steps", "this is the key step" are *sometimes* legitimate roadmap
   for the reader. So the agent's chat-style commentary slips through
   review by mimicking that register.
2. **Modeling work has a long context tail.** A proof references
   primitives, assumptions, prior lemmas, and a solution concept fixed
   pages earlier. The agent, with everything in context, can lose track
   of which of those are visible to the reader at the current line.

The discipline is the same as in writing: **before writing each
sentence of modeling prose, model what the reader knows at that line
of the paper given only what the paper itself has said up to that
point.** Then write only what passes.

## Two reader contexts to track

When writing modeling prose, two contexts must be honored simultaneously:

- **Document context.** The reader has read up to this line of the
  paper. They have seen whichever definitions, assumptions, and lemmas
  the paper itself introduced; nothing from the chat, the PLAN.md, the
  derivation note, or the agent's working memory.
- **Solution-concept context.** Inside a proof, the reader is operating
  under a stated solution concept (planner problem, competitive
  equilibrium, recursive equilibrium, steady state, ...). Every move
  must be one a reader inside that concept can follow.

Document context maps to the writing-side perspective check. Solution
context is the modeling-specific addition.

## Symptoms — modeling-specific perspective leaks

### 1. Section-level meta-commentary that doesn't survive the reader's perspective

> "The one-tree case is not the main theorem, but it is the cleanest
> comparative-static illustration."

The reader at a subsection header does not have a notion of "the main
theorem" loaded against which this is being contrasted. The sentence is
a chat-register justification of the agent's structural choice. Cut to
the substantive opener: "Consider a one-tree specialization of the
economy in §X. ..."

### 2. Revision-context leaks

> "To study the referee's endogeneity concern, I specialize to ..."

The reader has no referee. Replace with the *economic* motivation a
reader can hold: "To isolate the role of [endogenous object X] from
[confound Y], specialize to the symmetric paired two-asset benchmark of
§X."

### 3. Mid-proof self-narration aimed at the user, not the reader

> "I now solve the symmetric no-flightiness benchmark first because that
> is what the user wanted me to clarify."

vs.

> "Solve the symmetric no-flightiness benchmark first; the asymmetric
> response is then a small perturbation around it."

First-person narration of the proof's *strategy* is fine and often
good. First-person narration of the agent's *choice process* is a leak.

### 4. Forward references the reader cannot resolve

> "This is the cleaner of the two derivations I considered."

The reader has not seen the other derivation and never will. Cut.

> "As I noted in the planning step, [object] satisfies ..."

The reader has not seen the planning step. Either cite a paper section
that establishes the property, or restate the property here.

### 5. Implicit-context assumptions

A proof step that uses a fact established only in chat / RESULTS.md, or
in a derivation note that is not in the paper, is the same failure
class. The reader cannot follow the step. Either lift the fact into the
paper's body / appendix or cite an external source the reader can
actually consult.

## Legitimate modeling-prose moves that look similar

Don't over-correct. The following are reader-facing and stay:

- "The active solution concept is the competitive equilibrium of §X."
  — pins the concept the reader needs to evaluate the proof.
- "Proceed in two steps: first solve the symmetric benchmark, then
  perturb." — proof roadmap, helpful for the reader.
- "It suffices to sign the global-shock channel." — narrows the reader's
  attention; serves the reader, not the agent.
- "We use the envelope theorem to differentiate through the value
  function." — names the rule before applying it (also a four-gate
  Derivations item).

The test that distinguishes legitimate roadmap from leak: **does the
sentence orient a reader who has only the paper, or does it justify a
choice the agent made for someone outside the paper?** Keep the first;
cut the second.

## A pre-save walk for modeling prose

For each subsection or proof, before saving:

1. **Reader-state check.** Read the section opener as if you have only
   read the paper up to that line. Does the first sentence make sense?
   Does it use only objects already introduced or introduced
   immediately?
2. **Solution-concept anchor.** Is the active solution concept named
   before the algebra starts (per the four-gate Derivations rule)? If
   the proof relies on linearization around a benchmark, fixed-point
   selection, or a particular equilibrium, has the reader been told?
3. **Each non-trivial step states a rule and a reader-facing reason.**
   "Differentiate the FOC w.r.t. θ" is a rule. "...because we want the
   sign of the comparative static" is a reader-facing reason.
   "...because the user asked for this case" is a leak.
4. **No leaks of the workflow vocabulary** in
   `audience-discipline-writing.md`.
5. **Forward references resolve inside the document.** Every "as shown
   above", "below", "in §X" points to something the reader can find in
   the paper, not in chat or RESULTS.md.

## Where modeling-side justifications belong

| Content | Right home |
|---|---|
| "The proof goes in two steps because ..." (reader-facing) | Proof body, as roadmap. |
| "I structured this proof this way rather than X because ..." (agent-facing) | `RESULTS.md` task block. |
| "We checked this numerically with parameters {p}" | Paper body / appendix if it's an audience-facing verification; `RESULTS.md` if it's an internal sanity check. |
| "This case responds to Referee 2's concern about Y" | Response letter only. |
| "The benchmark is symmetric because that is what the conjecture in §X requires" | Paper body — the reader can follow this. |
| "The benchmark is symmetric because the asymmetric algebra was too messy to write up in this revision round" | `RESULTS.md`; never the paper. |

## Reviewer-side check

In addition to the writing-side scans, a reviewer of modeling prose
should verify:

- Every proof opens with the active solution concept named.
- Every non-trivial derivation step has a reader-facing reason, not an
  agent-facing one.
- Section openers and subsection openers do not justify the section's
  existence relative to "the main theorem" or "the main case" unless
  that comparison has been set up for the reader.
- All forward references resolve inside the document.

Flag perspective leaks as `[BLOCKING]` when the leak is in the paper
body / appendix; `[ADVISORY]` in working notes.

## See also

- `audience-discipline-writing.md` — root failure mode and the
  three-channel separation.
- The four gates in `SKILL.md` (Objects & Notation / Assumptions /
  Derivations / Verification & Rendering) — perspective discipline
  composes with each gate; a step can be technically correct under the
  four gates and still leak chat context to the reader.
