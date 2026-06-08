# Polish Mode

> Load when the request is to clean up existing prose — "polish §X", "tighten", "proofread", "clean up these edits", "apply these review findings". Sentence-scope by default; structural-scope only when the loaded reference set includes `structure.md`.

## Input shapes

Across all three shapes: if `## Project Conventions` is in play in a handoff doc, treat its writing-side rows as the established choice during triage — divergences from them are findings to fix or surface, not free authorial calls (per `SKILL.md §Project Conventions in the handoff doc / CLAUDE.md`).

### A — Unstaged edits

Author has been editing the file; `git status` shows it modified, `git diff` shows the in-flight changes. The polish target is the working tree (or, if the request specifies, only the diff hunks).

1. Read `git diff` first to see what the author was attempting; the polish should land *with* the author's direction, not against it.
2. Edit in place. Inline `TODO`s and crude phrasing in the diff are part of the work — clean them up.
3. If the diff includes a `DO NOT EDIT` block or fences, leave that range alone.

### B — Named target

The request names a file, section, or paragraph and asks for polish — no in-flight edits. Read the target end-to-end once before editing; the second pass is the edit pass.

### C — Review-findings list

The request hands over an accepted-findings scope and asks to apply it. The scope **is** the work — apply each accepted finding as a minimal edit; do not silently extend to nearby issues. If a finding is ambiguous or incorrect, raise it; do not silently reinterpret.

**When polish follows long-form review**, shape-C input is accepted task-local `## Review Notes`. The task names a bounded sweep (e.g., "all typos", "all citation-format issues") and points to the review items it applies — apply that batch, do not re-batch. **When polish is standalone** (a free-floating findings list), apply per finding from the raw list.

In both cases, each accepted finding carries a `Fix:` tier (`review.md §Fix tiers`); polish-shape-C apply behavior follows the tier:

- `mechanical` — apply silently; group according to the task's issue-class batch.
- `conventional` — apply, but write one finding-line per item in the commit message naming the choice made.
- `authorial` — surface for the author; do not apply.

An accepted-but-deferred `authorial` item stays in the findings list with a note recording why it was not applied.

## Edit vs propose vs ask

For any contemplated edit, route it through this matrix:

| The edit is… | And the request… | Action |
|---|---|---|
| Within scope, on stable lines | Polish / proofread | **Edit** minimally. |
| Within scope, on a line the author touched in the last commit or the unstaged diff | Polish / proofread | **Ask** — "I see you touched line N; include it in the polish?" |
| On a line marked `DO NOT EDIT` (or equivalent) | Any | **Skip with note.** |
| Outside explicit scope, sentence-level | Could be argued as polish | **Propose** — "I noticed §4 has the same nominalization pattern; want me to apply the same polish there?" |
| Outside scope, structural (reorder, merge, add subsection) | Polish / proofread | **Propose, do not perform** — structural edits require `structure.md` loaded *and* an explicit authorization. |
| Would change meaning, claim, or argument | Any | **Ask.** Meaning preservation is sovereign. |

## Intent comments

An intent comment on the line above a paragraph (`% intent: …` in `.tex`, `<!-- intent: … -->` in `.md`/`.qmd`) records what the paragraph is trying to do for the reader, not what it currently says.

**Read pre-existing intent comments before editing** — they expose what the current wording may obscure. **If text and intent conflict, the text wins**: the author may have rewritten the paragraph and not yet updated the comment. Ask whether to align the intent to the new text or rework the text toward the older intent; if asking is impractical, update the intent to match the text and flag it. Priority chain: **user's current request > current text > intent comment > agent's own judgment**.

**Do not invent intent comments.** A paragraph without one stays without one. If polish surfaces an ambiguity an intent comment would resolve, ask the author and write the comment from their answer.

## Triage

In shapes A and B, every diagnosed issue is implicitly tiered per `review.md §Fix tiers`. Apply `mechanical` and `conventional` tier issues as minimal edits in place. **Surface `authorial`-tier issues** to the author — chat reply for standalone polish; the task-system editing convention when polish rides a workflow. Not silently fixing is a recognized outcome, not under-editing. The §Edit-vs-propose-vs-ask matrix already routes meaning-changing edits to **Ask**; triage names the surface path for issues that diagnose cleanly but need author input on the right answer — canonically a claim-evidence gap, also a topic-sentence rewrite that would move the paragraph's sequence.

In shape C, the findings list arrives pre-tiered; apply per the shape-C tier rules above.

## Minimal-edit discipline

Use the smallest edit that resolves each issue — a nominalization fix replaces one noun with one verb, not the whole sentence. Over-editing (drifting past scope) and under-editing (shipping only typo/grammar fixes while leaving a weak topic sentence or broken parallelism as silent omissions) are equal failure modes. **The rule constrains the size of each fix, not the number of fixes:** diagnose thoroughly per `style.md §Gated Checklist`, tier and route per §Triage, apply each fix minimally.

After the edit batch, build (`refactor-and-compile.md` §Compile) and check no cross-reference broke. A diff that doesn't compile is not a polished diff.
