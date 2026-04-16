# Final form: consolidation discipline for Stage 2 `RESULTS.md`

Load this reference when you are either the **doc-writer subagent maturing `RESULTS.md` at `integration-workflow` Step 3** or the **doc-reviewer subagent reviewing that matured file**. This is the gate that the superRA IMPLEMENT phase deliberately defers so it can stay fast.

The Stage 1 dev-log form of `RESULTS.md` is task-indexed, terse, agent-facing, reviewer caveats inline. The Stage 2 permanent form is reader-facing, fact-checked, and co-located with the analysis code. Consolidation **rewrites the file in place** before relocating it — it does not create a new file.

## The consolidation pass — what changes

1. **Restructure from task-indexed to reader-facing.** Task ordering mirrored execution order, which is rarely the order a reader wants. Reorganize by objective, data source, or result type — whatever flows best for someone reading cold. Task numbering from `PLAN.md` disappears.
2. **Merge related findings.** If two tasks produced pieces of the same result (e.g., Task 3 built the sample, Task 5 ran the regression on it), combine them into one section.
3. **Strip reviewer caveats that were resolved.** Caveats on APPROVED tasks that were addressed should be gone. Caveats flagging unresolved limitations become a "Limitations" section.
4. **Add frontmatter.** Per `baseline-io.md`. Stage 1 had no frontmatter.
5. **Materialize figures.** Copy from `results_attachments/` into a new `attachments/` folder next to the relocated file. Update embed paths. See `rich-content.md` for the mechanics.
6. **Relocate.** Move the file from worktree root to the analysis's permanent code folder, resolved from project guidance (`CLAUDE.md` / `AGENTS.md`). Commit as part of the integration commit.

## Fact-check checklist

Every matured `RESULTS.md` must pass this before integration review APPROVES. Go through it line by line.

### Claims and citations

- [ ] Every number, statistic, or factual claim is **backed by a link** to its source file (script, output CSV, figure, log). Citations are markdown links: `[text](../path/to/source)`.
- [ ] For each cited number, **open the source file** and confirm the number matches. No rounding inconsistencies. No stale values from before the last revision.
- [ ] Unsupported claims are flagged. If a claim cannot be cited, either cite it or remove it.

### Speculation and interpretation

The Stage 2 form documents what was found. It does **not** interpret, recommend, or speculate.

**Prohibited language patterns:**

- Speculation: "suggests", "indicates", "likely", "probably", "appears to", "this means", "implies", "shows that".
- Causal claims without an identification strategy: "because", "caused by", "due to".
- Subjective assessments: "excellent", "poor", "good", "bad", "successful", "failed", "robust", "reliable", "sophisticated".
- Quantitative adjectives without a definition: "significant", "strong", "weak", "accurate", "inaccurate".

**Acceptable alternatives:**

- "difference of X%", "within Y% of benchmark", "error rate of W%".
- "classified Z% of cases as X".
- "the regression coefficient is β = 0.12 (SE 0.04)".

**Exception:** if the researcher explicitly asked for interpretation (e.g., in `PLAN.md`'s objective or methodology section), allow it but flag the location in a reviewer note.

### Methodology

- [ ] Methodology sections **describe what was done**, not why. Why belongs in `PLAN.md`'s objective, not in the findings.
- [ ] Every methodological step links to the code file that implements it.
- [ ] Classification rules, filter criteria, and sample construction are shown in tables if they have branching logic.
- [ ] No evaluation of the methodology ("robust", "rigorous"). Just description.

### Results

- [ ] Tables present precise numbers. Compare against output files — no silent rounding.
- [ ] Units and formatting are consistent.
- [ ] Comparisons are factual ("X vs. benchmark Y: difference Z%"), not narrative ("good agreement", "significantly different").
- [ ] Figures are copied to the new `attachments/` directory and cited back to their original source path.
- [ ] Figure captions are descriptive — not "Figure 1".

### Prohibited sections

The following sections **must not appear** unless the researcher explicitly requested them:

- [ ] "Recommendations"
- [ ] "Conclusions" (interpretive)
- [ ] "Strategic Decision"
- [ ] "Implications"
- [ ] "Future Work"

A "Limitations" section that lists factual caveats (unresolved reviewer notes, data coverage gaps, known biases) is allowed and encouraged.

## Cross-consistency with project docs

The Stage 2 doc-writer matures `RESULTS.md` only; project-level docs (`CLAUDE.md` / `AGENTS.md` / `README.md`) are audited during `integration-workflow` Stage 2 per `refactor-and-integrate/references/codebase-integration.md` §Project Doc Audit. The doc-reviewer still checks that the matured `RESULTS.md` does not contradict project docs:

- [ ] **Methodology descriptions** in the matured RESULTS.md match the current code — no references to dropped approaches, superseded variable definitions, or removed processing steps
- [ ] **Headline results cited in project docs** (if any) match the matured RESULTS.md — no stale numbers from before the last revision
- [ ] **File paths and command names cited in RESULTS.md** are accurate — no references to moved, renamed, or deleted files

If the reviewer finds stale claims in `CLAUDE.md` / `AGENTS.md` / `README.md` themselves, that is a Stage 2 regression — flag it but recognize the primary gate for project-doc accuracy was Stage 2.

## Severity for integration review

When the doc-reviewer applies this checklist, classify issues:

- **Critical** — factual errors, unsupported claims, numbers that don't match sources. Blocks APPROVED.
- **Major** — speculation, interpretation, subjective language, prohibited sections. Blocks APPROVED.
- **Minor** — formatting, typos, citation path issues, missing alt text. Note but do not block.

Report issues in a plain checklist with line numbers and a specific proposed fix. Do not edit the file yourself as a reviewer — propose the fix and let the implementer apply it.

## Output shape after consolidation

A matured `RESULTS.md` typically contains:

1. **Frontmatter** (per `baseline-io.md`).
2. **Title and one-paragraph objective** pulled from `PLAN.md`'s objective section.
3. **Data section** — what data was used, with links to the code that loaded/cleaned it.
4. **Methodology section** — what was done, with links to scripts. Factual only.
5. **Results sections** organized by topic. Tables, figures, cited numbers.
6. **Limitations** (optional) — factual caveats.
7. **Reproducibility pointer** — one line stating the git commit and how to regenerate (e.g., "Reproduce via `make analysis` at commit `abcd123`").

Length: as long as the findings require. A two-page Stage 2 `RESULTS.md` is fine if the analysis was small. A fifteen-page one is fine if it wasn't. Do not pad.
