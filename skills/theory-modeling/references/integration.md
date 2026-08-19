# Integration Discipline for Theory Modeling — the Rewriting Reference

> Loaded at `Stage: integration` for theory-modeling tasks. The readability layer: ex-post structural rewriting (A), per-step local obviousness (B), cross-document coherence (C), refactor-survival of correctness artifacts (D).
>
> **Scope.** Document-internal coherence and ex-post rewriting. A structural rewrite surfacing a correctness fix: halt and re-dispatch as `Stage: implementation`. Generic codebase-coherence concerns belong to `refactor-and-integrate` — load both at this stage.

Each section runs principle → identification protocol → checklist. Verdict adjudication follows the reviewer protocol in `agent-orchestration`.

---

## Section A — Objective-first structural rewriting

### Principle

A derivation is read forward but built backward. **Start from the object the proof needs, then expand only the terms required to evaluate it** — name the target, identify what it requires, recurse only into terms not already known. Placeholders introduced before the target is named force the reader to hold a symbol with no purpose: the dominant structural failure mode.

The discipline is **recursive**. A multi-step proof signposts its top-level strategy in one sentence; each non-trivial sub-argument signposts its own local strategy the same way; transition prose at major joins names the position in the parent plan ("having established $Y$, we turn to $Z$"). A reader entering at any point recovers the local goal from the surrounding signposts.

`references/objective-first.md` carries the worked walkthrough and identification drills — load on demand before applying the checklist.

### Identification protocol

Walk the derivation top-to-bottom, in the reader's order:

1. **Read the prose preceding the first displayed equation.** Does it name the object the proof targets? A first display asserting an intermediate symbol ("$z_j := \ldots$") with no prior reference to the target is local-detour-first → flag.
2. **For each displayed equation: which named target does this advance?** Answer "we will see in three pages why this matters" → deferred goal → flag.
3. **At every block longer than ~5–10 lines of algebra: does the prose open with a one-sentence local strategy?** No opening signpost → the reader infers scope from algebra → flag. Watch for sub-sections opening with manipulation, and for "we will use this below" — the term should appear when its use is named.
4. **At every section/sub-section join: does the prose name the transition?** ("Having $X$, we turn to $Y$.") Bare juxtaposition of blocks → flag.
5. **For each placeholder symbol introduced** (absent from the canonical Notation Conventions table and not a canonical model object): is it still doing structural work after the rewrite? Surviving placeholders with no independent meaning → flag.

### Checklist

- `[BLOCKING]` **Target named and dependency walk visible in prose before the algebra.** The target is the object the proof computes or signs. The chain from target down to primitives or already-known objects appears as a brief prose walk ("we need $T$ ← $A$ ← $B$, the canonical column from §X") or as recursive sub-argument signposts.
- `[BLOCKING]` **Recursive sub-argument signposts.** Every non-trivial sub-argument opens with its own one-sentence strategy; major transitions name the local position. Test: cover all algebra, read only the prose — can a reader recover the scaffolding? Walls of algebra without strategy prose → REVISE.
- `[BLOCKING]` **Placeholder symbols introduced for detours are removed when the rewrite makes them unnecessary.** A surviving placeholder justifies its place against the per-symbol ledger entry (Gate 1 in `theory-modeling/SKILL.md`), or REVISE.
- `[ADVISORY]` **Onion-style layering.** A result with a clean baseline plus complications: simplest case first, complications in layers.

---

## Section B — Per-step local obviousness

### Principle

Every displayed equation is **obvious** from a roughly half-page window above it. "Derivable in principle" is too weak — reconstructing missing definitions, recalling a 10-page-back assumption, or unpacking three substitutions collapsed into "therefore" loses the reader.

Six fixes for a step that is not obvious:

1. **Define inline.** Symbol undefined in the local window: define it at first use in this region (one phrase or one displayed line — the canonical entry stays in the task's `## Results`).
2. **Restate the assumption.** Step depending on an assumption stated far above: restate it in scope at the point of use ("Under the bounded-risk-aversion assumption (§2), …").
3. **Cite-with-form-recall.** Step depending on a prior result too far back to assume the reader holds it: cite by name or equation number **and** restate its operative form inline ("By Lemma 3.1, $f(x,\theta) = g(x) + \theta h(x)$, so …"). A bare "(see §3.2)" is insufficient when the step depends on the specific form.
4. **Split the step.** Multiple substitutions, cancellations, or sign manipulations collapsed into one move: split so each transition is one obvious move with one named rule.
5. **Make the reference precise.** Prose referring to a specific variable uses the math symbol ($\beta$, not "the discount factor"); prose referring to a specific equation or named statement cites it by number or name ("eq. (12)", "Lemma 3.1", not "the equation above"). Carve-out: introduction sites where plain language *is* the definition ("let $\beta$ denote the discount factor"). The rule governs back-references to objects the document already names.
6. **Disambiguate the rendering.** Ambiguous subscript, superscript, fraction, summation limit, or align environment: restructure the LaTeX (explicit braces, displayed `\frac` over inline `/`, aligned multi-line breakdowns of long products). The symbol is defined and the step is one move, but the glyphs hide which object the reader is looking at.

### Identification protocol

The core diagnostic is the **half-page mask test**, per displayed equation:

1. Cover everything except the half page (~25–40 lines) immediately above the equation.
2. Read only that window. Is the equation **obvious** — not merely derivable with effort?
3. If not, map the missing piece to one of the six failure types (undefined symbol / unrestated assumption / uncited or content-less prior result / over-compressed step / imprecise reference / ambiguous rendering) and apply the matching fix above.

Pattern-watch list — grep-able instances:

- "$X = \ldots$" asserted with no preceding definition or named rule.
- "By symmetry" / "by inspection" with no operative-form recall.
- "(see §3.2)" / "(see Lemma X)" where the step depends on the result's form.
- "Therefore" / "thus" / "it follows that" connecting a long chain in one step.
- A symbol last defined more than half a page back, reused with no one-phrase recall.
- A variable named in English ("the discount factor") with a math symbol in scope; an equation pointed at by position ("the equation above") rather than by number.
- Nested subscripts collapsing (`x_{i_j}` → `x_ij`); long fractions or summations on one line with blurred boundaries.

### Checklist

- `[BLOCKING]` **Every displayed equation is obvious from the local window.** Each symbol defined in scope or canonically pointed to with its meaning recalled; each rule named; each prior-result dependency cited with operative form visible. "Derivable with effort" is not enough.
- `[BLOCKING]` **Citations to results outside the local window include content recall when the step depends on the form.** A bare "(see §3.2)" is REVISE when the next move uses the specific form.
- `[BLOCKING]` **Symbol freshness.** Symbols last seen more than half a page back are recalled in one inline phrase at re-use ("$\mathbf{c}_k$, the column-$k$ dividend loading defined at §2.1").
- `[BLOCKING]` **Step granularity.** Over-compressed steps split so each transition is one obvious move with one named rule; long chains broken into aligned steps, not dense one-line algebra.
- `[BLOCKING]` **Precise prose-to-math references.** Math symbols for back-references to defined variables; equation numbers / named statements for back-references to results.
- `[BLOCKING]` **Rendering legibility.** Subscripts, superscripts, fractions, summation limits, and align environments render unambiguously. (Rendering correctness — output matching the computed object — is Gate 4 in `theory-modeling/SKILL.md`.)
- `[ADVISORY]` **Prefer compact inline restatement over forcing the reader to navigate.** A short inline recall serves the reader better than a technically sufficient cross-reference.

---

## Section C — Cross-document coherence

### Principle

A derivation correct in isolation is wrong in a paper when its symbols clash with canonical Notation Conventions, when it re-derives an equation already established, or when its prose breaks the style of surrounding sections. At integration stage the task owes the document a result that fits the document.

Three coherence layers, each with its own authority:

- **Notation.** The canonical Notation Conventions table is authoritative. Prior-task `## Results` ledgers carry symbols introduced upstream and reusable but not yet promoted. Local symbols duplicating either hide the connection.
- **Prior results.** Equations and named statements established earlier in the document or a prior task are cited and reused. Re-deriving an equivalent result forks the document silently.
- **Prose integration.** Terminology, assumption phrasing, formality level, and notation usage match the surrounding sections.

### Identification protocol

1. **Notation pre-flight against the canonical Notation Conventions table and prior task ledgers.** Classify each symbol in the current task:
   - **Canonical** — in the canonical Notation Conventions table; reuse.
   - **Prior-task-promoted** — in a prior task's ledger for the same object; reuse and cite.
   - **Genuinely new** — no prior surface names the object; log a current-task ledger entry per Gate 1, promotion candidate per [superimplement/references/completion.md](../../superimplement/references/completion.md).
   - **Local duplicate** — an existing canonical or prior-task symbol already names the object → flag.
2. **Prior-result pre-flight.** Per derived equation or named statement, search prior tasks for a name match (a prior lemma re-derived under a different name) or a content match (a prior displayed equation algebraically equivalent under canonical notation) → flag.
3. **Prose integration pass.** Re-read the section immediately preceding the new one; compare terminology, assumption phrasing, formality, notation usage. Style breaks at the join → flag.

### Checklist

- `[BLOCKING]` **Notation pre-flight.** Every symbol is canonical, prior-task-promoted, or logged as a completion-menu promotion candidate (per [superimplement/references/completion.md](../../superimplement/references/completion.md)). Local duplicates → REVISE: replace with the upstream symbol, document the rename where relevant.
- `[BLOCKING]` **Prior-result pre-flight.** Equivalent equations and named statements from prior tasks are cited and reused, not re-derived. Specializations state the relationship explicitly ("Lemma 2.3 specialized to the symmetric case yields …").
- `[BLOCKING]` **Prose-integration check.** Terminology, assumption phrasing, formality, and notation conventions match the surrounding sections. Style breaks at section transitions are REVISE.
- `[BLOCKING]` **Document-code consistency.** Model feeding papers, slides, notes, or downstream artifacts in the repo: numerical and methodological inconsistencies between the refactored work and those artifacts are reconciled, or flagged in the task's `## Results` when reconciliation is out of scope.

---

## Section D — Discipline preserved through refactoring

### Principle

Refactoring silently changes assumptions, branch choices, solver defaults, equation rendering, or verification parameters. **Refactored modeling work is re-validated, not carried forward.** Section D guards the derivation-discipline artifacts that already existed — ledger entries, per-step reasons, stated intuitions, verification work.

### Identification protocol

Diff pre- and post-refactor versions of every modified artifact. Per `[BLOCKING]` item below: is the artifact still present, and does it still carry its discipline-bearing content (intuition, interpretation, reason, ledger entry) — or did the refactor collapse it into prose, drop it, or paraphrase it away?

### Checklist

- `[BLOCKING]` **Every four-gate artifact the original work carried survives the refactor**, in a form and place a reader can use: symbol intuitions and mnemonics (Gate 1), plain-language assumption interpretations (Gate 2), the per-task Notation & Assumptions Ledger in `## Results` (Gates 1–2), the technical rule and one-sentence reason on each non-trivial step (Gate 3), and symbolic checks or limiting cases (Gate 4). Internal numerical checks, where used, are rerun successfully, not reported. Reorganize freely; collapsing one into opaque prose, a bare code comment, or a math restriction without its economic reading is deletion.
- `[BLOCKING]` **Drift tests pass post-refactor.** Where drift tests exist, they pass on the refactored work; failures are adjudicated per `references/integrate-drift-tests.md`.
- `[BLOCKING]` **Rendered markdown/LaTeX matches the refactored code.** Equation blocks, symbols, and case labels match the live derivation and numerical outputs.
- `[BLOCKING]` **The canonical Notation Conventions table contains only user-confirmed promotions** (per [superimplement/references/completion.md](../../superimplement/references/completion.md)). Orphan entries — added without a logged user confirmation — are REVISE.

### Utility reuse and documented deviations

- `[BLOCKING]` **Route human-readable equations, tables, and figures through `superRA:communicate`.**
- `[BLOCKING]` **Document notation changes.** Any intentional rename or consolidation carries an explicit old-to-new mapping.
- `[BLOCKING]` **Document strengthened assumptions.** A refactor revealing that a result needs stronger primitive restrictions than stated: record the new restriction, where it enters, and why.
- `[ADVISORY]` **Leave migration pointers when consolidating helpers.** Symbolic or numerical helper code moved to a shared location with older files still referencing the old one: leave a one-line pointer.
