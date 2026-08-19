# Refactor-and-Compile — Safe find-replace + build gate

> Load when Polish, Draft, or Review mode performs (or verifies) a find-replace across a document, and for the post-edit build that ends every batch of edits. Severity markers: `[BLOCKING]` must fix; `[ADVISORY]` recorded, never blocks.

---

## §Refactor

Context-aware find-replace across a document — rename a variable, change a term of art, update a convention — inside the requested scope, preserving substance and intent (`SKILL.md §Preserve substance, polish prose`).

**Principle.** Find-replace is cheap to run and expensive to get wrong: naive substitution destroys text that looks like the target but means something else.

### The Four Always

1. **Always preview matches first.** Run a read-only search (`grep -n`, editor find), list every match, mark each *rename* or *leave*. Substitute only after confirming the list.
2. **Always confirm word-boundary.** `estimate` matches inside `underestimate`, `estimates`, `estimator`, `estimation`. `Table` matches inside `acceptable`. Use `\b` (regex word boundary) or `-w` (grep whole-word) where the tool supports it.
3. **Always check case variants.** `Treatment`, `treatment`, `TREATMENT` — the substitution may need all three, or exactly one. Decide explicitly.
4. **Always check plural / inflection variants.** `treatment` vs `treatments`; `ran` vs `run` vs `running` — often all in scope, not always.

### Worked examples of false-positive matches

| Target | False-positive matches | Fix |
|---|---|---|
| `estimate` | `underestimate`, `estimation`, `estimator`, `estimates` | Word-boundary + decide on inflections explicitly |
| `Table` | `Tablespoon`, `TableView`, `turntable` | Word-boundary (`\bTable\b`); or search `Table 1\b` when renumbering a specific table |
| `est` | `estimate`, `underestimate`, `estimator`, `tested`, `manifest` | Almost always a bad target — use a longer, more unique string |
| `y` (variable name) | Every word containing `y` — `policy`, `they`, `yield` | Never substitute a single letter without a mathmode / code-block constraint |
| `OLS` | `ROLS`, `TOOLS` (unlikely but imagine) | Word-boundary; all-caps-only often enough |
| `reg` | `region`, `regardless`, `aggregate` | Almost always a bad target — use a longer, more unique target |
| `r_i` | `r_ij`, `r_{i,t}` | Decide whether the refactor covers the subscripted forms; LaTeX subscripts complicate matching |
| `\cite{foo}` | `\citep{foo}`, `\citet{foo}` | Usually the refactor covers all three; list them and confirm |

### Math-mode refactors

Math-mode identifiers (`\beta`, `x_i`, `\mathbf{x}`) are trap-laden:

- The same letter differs between math and text mode (`\beta` in an equation vs `beta` in prose).
- Subscripts, superscripts, and decorators (`\hat`, `\tilde`, `\bar`) multiply the patterns.
- Renaming `x` → `z` matches every `x` character in every equation — including equations where `x` plays a different role.

Approach:

1. Scope to math-mode only where possible (the tool may support `$...$` matching; otherwise use explicit patterns).
2. List every location first.
3. Decide whether subscripted (`x_i`, `x_{i,t}`) and decorated (`\hat x`, `\bar x`) forms all change. Usually yes.
4. Build after.

### Terminology refactors (prose)

Renaming a term of art (`treatment group` → `treated sample`):

- The new term must be a legitimate synonym *for this paper's audience*. Consult `consistency/terminology.md`.
- Check plural, possessive, hyphenated, and capitalized variants.
- Respect case contextually — sentence-start vs mid-sentence.
- Old term inside a direct quotation (block quote, citation): **do not substitute** — quotes are sacred.

### After any refactor — verify

- **Build the document** (§Compile). Errors introduced by the refactor block the refactor.
- **Cross-reference check.** Any label, citation key, or bib key touched? See `consistency/cross-references.md`.
- **Diff review.** Read the git diff end-to-end; every hunk intended.

### Refactor Gated Checklist

- `[BLOCKING]` Every substitution previewed before it was applied, covering case and plural/inflection variants; no false-positive or word-boundary match survives in the diff.
- `[BLOCKING]` Direct quotations and block quotes not touched (quotes are sacred).
- `[BLOCKING]` Document builds after the refactor (§Compile).
- `[BLOCKING]` Git diff read end-to-end; every hunk intentional.
- `[ADVISORY]` Refactor pre-image list (what changed, how many instances, in which files) recorded in the task or status return.

---

## §Compile

**Principle.** Every batch of edits ends with a build. Errors block completion; warnings are triaged. Errors absent from the pre-edit build but present after are the edit's responsibility.

### Build commands per engine

**LaTeX (`latexmk -pdf`)**

```bash
latexmk -pdf main.tex         # preferred: handles BibTeX / biber / multiple passes
# fallback:
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```

The third `pdflatex` pass resolves forward references. `latexmk` handles this automatically.

**Quarto (`quarto render`)**

```bash
quarto render paper.qmd       # detects engine from yaml; runs pandoc + PDF engine
```

**Pandoc (`pandoc`)**

```bash
pandoc paper.md -o paper.pdf --citeproc --from markdown
# or with pandoc-crossref for figure/table refs:
pandoc paper.md -o paper.pdf --filter pandoc-crossref --citeproc
```

**Markdown (various)**

For Markdown rendered via a static-site generator (MkDocs, Jekyll, Hugo, Zola), use the project's build command. No universal default.

### Reading build output

After any build, read the log:

1. **Errors.** Halt the build; fix before completion.
2. **Warnings.** Triage each per the table below.
3. **`??` in output.** Unresolved cross-references — treat as errors (see `consistency/cross-references.md`).

### Warning triage heuristics

| Warning class | Default action | Notes |
|---|---|---|
| `Overfull hbox` | Ignore unless egregious | Line overruns the text margin. Cosmetic in draft; fix before submission. |
| `Underfull hbox` | Ignore | Stretched spacing. Cosmetic. |
| `Underfull vbox` | Ignore in drafts | Fixable with manual pagebreaks later. |
| `Reference(s) undefined` | **Escalate** | Unresolved `\ref`. `[BLOCKING]`. |
| `Citation(s) undefined` | **Escalate** | Missing BibTeX entry or stale `.aux`. `[BLOCKING]`. |
| `LaTeX Error: File not found` | **Escalate** | Missing figure, `\input`, or package. `[BLOCKING]`. |
| `Package <X> Warning: ...` | Read and judge | Often signals a real problem; triage case-by-case. |
| `No \title given` / `No \author given` | Ignore if draft; fix before submission | |
| `LaTeX Warning: Label(s) may have changed` | Re-run the build | Normal on first pass; persists → investigate. |
| Pandoc warning `[WARNING] Could not find reference for ...` | **Escalate** | Missing citation. `[BLOCKING]`. |
| Pandoc `[WARNING] This document format requires nonempty ...` | Read and judge | Often a YAML metadata issue. |

### LaTeX-rendering hazards

Failure modes the warning table does not name:

- **Unescaped `%`, `&`, `#`, `_` in text mode.** A dropped literal `%` truncates the line from that point (LaTeX comment); literal `&`, `#`, `_` raise errors or shift table alignment. Escape as `\%`, `\&`, `\#`, `\_` outside math mode.
- **Unclosed math-mode delimiters.** A missing `$`, `\)`, or `\]` cascades into many lines of misleading errors before LaTeX recovers. First error `Missing $ inserted` or `Display math should end with $$` → search for the unmatched delimiter near the cited line.
- **Equation numbering gaps.** A `\label{eq:foo}` inside a starred environment (`equation*`, `align*`) or after `\nonumber` produces `??` at every `\ref{eq:foo}` site — the label exists with no number to print. Remove the star/`\nonumber`, or switch the reference to `\eqref` of a numbered sibling.

### Error-escalation rules

- **Errors introduced by the edit:** the edit is responsible. Fix before completion.
- **Errors already present before the edit:** flag in the task or status return — usually upstream (missing package, bad path); escalate to the researcher unless the edit should include the fix.
- **Warnings newly introduced:** triage per the table. `[BLOCKING]`-class, fix; otherwise report in the task or status return.
- **Warnings present before and after:** note as pre-existing, leave alone unless task scope includes build hygiene.

### Build output record

For non-trivial edits, record:

- Build command used.
- Pass / fail.
- Number of warnings, broken out by class (new vs pre-existing).
- Each new `[BLOCKING]`-class warning listed with file + line.

### Compile Gated Checklist

- `[BLOCKING]` Build command used is recorded.
- `[BLOCKING]` Build runs to completion with no errors — no unresolved `??` references, no undefined citations, and no `File not found` for a figure, `\input`, or package the edit touched.
- `[ADVISORY]` Build warnings enumerated (new vs pre-existing).
