# Polish Mode

> Load when the request is to clean up existing prose — "polish §X", "tighten", "proofread", "clean up these edits", "apply these review findings". Sentence-scope by default; structural-scope only when the loaded reference set includes `structure.md`.

## Input shapes

### A — Unstaged edits

Author has been editing the file; `git status` shows it modified, `git diff` shows the in-flight changes. The polish target is the working tree (or, if the request specifies, only the diff hunks).

1. Read `git diff` first to see what the author was attempting; the polish should land *with* the author's direction, not against it.
2. Edit in place. Inline `TODO`s and crude phrasing in the diff are part of the work — clean them up.
3. If the diff includes a `DO NOT EDIT` block or fences, leave that range alone.

### B — Named target

The request names a file, section, or paragraph and asks for polish — no in-flight edits. Read the target end-to-end once before editing; the second pass is the edit pass.

### C — Review-findings list

The request hands over a findings list (typically from Review mode) and asks to apply the accepted findings. The findings list **is** the scope — apply each accepted finding as a minimal edit; do not silently extend to nearby issues. If a finding is ambiguous or incorrect, raise it; do not silently reinterpret.

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

## Minimal-edit discipline

For each identified problem, apply the smallest edit that fixes it. A nominalization fix replaces one noun with one verb, not the whole sentence. Over-editing is the most common failure mode of polish mode — every word changed beyond the minimum is voice drift.

After the edit batch, run the build (`refactor-and-compile.md` §Compile) and check that no cross-reference broke. A diff that doesn't compile is not a polished diff.
