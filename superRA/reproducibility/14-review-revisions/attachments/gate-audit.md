# Gate audit — reproducibility skill + task-tree reproduction mechanics

Branch `skills/reproducibility` vs `main`. Read-only. Paths relative to repo root.
Abbrev: SK = skills/reproducibility/SKILL.md; DG = references/designing-the-graph.md; RA = rerun-or-accept.md;
DX = diagnosing.md; PC = protect-and-completion.md; AD = adoption.md; TFC = skills/task-tree/references/task-file-contract.md;
CMD = skills/task-tree/references/commands.md.

Word counts: skill 2,790 (SK 450, DG 869, DX 606, RA 457, PC 242, AD 166). TFC §Effective Dependencies→end 2,226 (records subsection alone 686). CMD §Reproduction→§Explain 1,681 (§Explain 464).

---

## 1. BLOCKING gate failures — duplicate clusters (one authoritative home each)

### C1. Saved-input scope / `--upstream` meaning — 10 copies
- SK:12 "Targets are task-scoped: a file from a producer outside the scope is a saved input, used as it sits on disk."
- SK:20 "with `--upstream` when the claim covers the producer chain."
- PC:22 "`--upstream` adds their producer chains."
- DX:36 "A locally fresh result can stay stale in the full graph: default status assesses saved inputs, `--upstream` assesses their producers."
- RA:43 "Producers outside the targets stay saved inputs, so accepting a consumer says nothing about its upstream."
- CMD:108 "Inputs from out-of-scope producers use existing files … `--upstream` adds transitive file-producer ancestors"
- CMD:116 "Default status certifies only selected work against saved inputs; `status --upstream` assesses the chain."
- CMD:134 "producers outside the selection remain saved inputs. Acceptance certifies the selection, not those producers."
- CMD:150 "A matching scoped status does not certify upstream producers; add `--upstream` to assess the chain."
- TFC:239 "Outside producers remain saved-input boundaries."
Tests: CMD:116/134/150 fail Test 2 against CMD:108 (same file, 4 statements). DX:36 s1, PC:22 clause, RA:43 fail Test 1 against SK:12+SK:20. TFC:239 fails Test 1 vs CMD:108.
Home: mechanic (what a scope selects) = CMD:108 (one sentence). Discipline (when a claim needs `--upstream`) = SK loop step 3. Definition of "saved input" = SK §The Model.
Edit: delete CMD:116 s2, CMD:134 last sentence, CMD:150 s2, TFC:239 "Outside producers…" sentence, DX:36 s1, PC:22 "`--upstream` adds their producer chains". RA:43 → keep only as the action "Accepting a consumer covers nothing upstream: accept or build the producer too."

### C2. Acceptance executes nothing / checks must run — 7 copies
- SK:12 "recording why current results stand instead of executing them"
- RA:42 "It executes nothing. A check that has never run must run; acceptance supplies no missing check stamp."
- CMD:146 last s. "Checks require an existing successful baseline and unchanged check stamp; a never-run check must execute."
- CMD:148 "Last actual execution metadata, `pytask.lock`, and check stamps remain unchanged."
- TFC:239 "Acceptance does not change workflow task statuses, successful lock entries, check stamps, or actual-run metadata."
- TFC:258 "Check acceptance requires its previous successful baseline and unchanged stamp; missing stamps require execution." and "it does not claim those bytes were executed."
- DX:33 "`passed at these inputs in lock <rev>; not run here` | Run the check here."
Tests: CMD:146/148 fail Test 1 vs TFC:239/258; TFC:258 check sentence fails Test 2 vs TFC:239 ("unsuccessful executions cannot be covered").
Home: record semantics = TFC §Acceptance (one sentence); discipline = RA §What acceptance never covers. CMD keeps only flags.
Edit: cut CMD:146 last sentence, CMD:148 s3; merge TFC:258 check sentence into TFC:239.

Also rejection conditions triple: CMD:146 "Invalid graphs, missing declared inputs/outputs, unavailable supplied evidence, concurrent edits, and failed or interrupted runs reject acceptance" vs TFC:239 "Invalid graphs, missing inputs/products, and unsuccessful executions cannot be covered." Keep CMD (fuller, CLI-facing), cut TFC copy.

### C3. Content-not-timestamp / root relocation / rerun model — mechanics living in the skill
- DX:5 "Changed content, never a timestamp. `touch` reruns nothing…"
- DX:7 "A root change invalidates through changed file content or resolved command text; relocation to identical bytes preserves freshness."
- TFC:191 "Root changes invalidate through changed content or resolved command text; relocation to equal bytes alone preserves freshness." (near-verbatim of DX:7)
- CMD:169 "Root relocation and command-resolution changes follow the [rerun model](../../reproducibility/references/diagnosing.md#what-makes-a-step-rerun)." — mechanics doc routing into a discipline doc for a mechanic (ownership inversion + wrapper).
- DX:19 "A Dropbox re-sync that changes only mtime causes a rehash without invalidation." (third content-not-mtime)
- DX:6 Julia include expansion = TFC:203. DX:8 env_deps = TFC:188. DX:7 "A `cmd` or `params` edit invalidates its step" = TFC:154 params row + CMD:123 stale row.
- DX:5 "A failed forced rerun still requires a successful retry." = CMD:125 verbatim idea.
- SK:11 "freshness is pytask's content-hash comparison"
Test 1 across the board. Ownership table: rerun/invalidation rules are "Reproduction-graph mechanics" → TFC §Reproduction Section (subagent-loadable). "Diagnosis" (what to do) → DX.
Edit: add a 5-bullet "Invalidation" subsection under TFC §Reproduction Section (content hashing, touch/mtime no-op, cmd/params/root rules, env_deps, failed-forced retry); delete DX §What makes a step rerun except the actionable residue ("`touch` does not rerun: use `--force`"; "declare unresolved includes and non-Julia helpers"); delete CMD:169 and TFC:191 s3 duplicates.

### C4. Identical-output cutoff — 3 copies
DG:22 "stops the cascade on unchanged bytes"; DG:40 "a directory out holding them defeats identical-output cutoff"; DX:13 "Identical regeneration … Volatile bytes defeat that cutoff…: sort before writing and keep run timestamps out of tracked outs."; plus CMD:110 "downstream execution remains conditional on regenerated bytes", CMD:132 "unchanged regenerated outputs can stop execution downstream".
Home: define once in DG §Declare (it drives declaration choices); DX:13 keep only "sort before writing; keep timestamps out of tracked outs"; cut CMD:110 clause and CMD:132 s3.

### C5. `--dry-run`/`explain`/`status` output described to the agent ("here is what you will receive")
- RA:5 "lists what would execute, each with its last recorded duration — `unknown` when the step has never run." = CMD:110 = DG:29 "`build --dry-run` prints what each last cost".
- RA:6 "`superra repro explain <target>` names each changed node's cause and source" = DX:23 "resolves where each changed hash came from" = CMD:100 = CMD:154.
- RA:7 "`superra repro status <targets>` reports each selected step's freshness and its `outside readers: N` count." = CMD:114.
- CMD:112 "When any reported step is not fresh, `status` ends with `Why not fresh: …`" — pure output narration.
- CMD:144 "Without `--json`, `accept` prints the steps it covered and what changed under each."
- CMD:157-159 (Sources / Builder environment / Output, 251 words) — full output anatomy.
Edit: RA §Preview → one line "Before applying the rule: `build --dry-run` for cost, `explain` for cause (act per DX §Read what explain names)". Delete CMD:112, CMD:144 s3. Collapse CMD:157-159 to "`--diff` shows the full diff; `--json` carries full hashes and sources." (cut ~220 words).

### C6. Acceptance one-shot / `--dry-run` / `--apply` — 2 near-verbatim copies
RA:36 "One call previews, revalidates, and writes. `--dry-run` prints a token and writes nothing; `--apply <token>` then accepts exactly that preview, when review and apply want separating." vs CMD:146 "The one-shot call runs every consistency check inside it and writes all selected records atomically. `--dry-run` previews and prints a token instead of writing; `--apply <token>` then accepts exactly that preview, for a deliberately separated review and apply." Also CMD:138-140 shows the same in code.
Test 1. Home CMD. Edit: RA:36 → delete s1–s2, keep pointer. (But see §3: the pointer drags subagents into CMD.)

### C7. Significance judgment in mechanics doc (ownership inversion)
CMD:114 "The count is one input to a significance judgment, never the judgment — a selected check, a maintained-path producer, and an out a document cites are significant at zero outside readers." duplicates RA:14 "Any one is enough: a selected check is significant at zero outside readers." Discipline belongs in RA. Delete CMD:114 s2.

### C8. Registration-follows-placement — 3 copies loaded by the same agent
SK:18 "**Registration follows placement.** Exploration lives in scratch or tmp and stays unregistered; code retained … is registered in its owning task." vs using-superra/SKILL.md:34 "**Registration follows that placement.** Retained code — companion or permanent — gets a `## Reproduction` step in its owning task; scratch gets none." (same bold head) vs SK:25 Gate 1. using-superra is mandatory for every agent, so SK:18 is Test 1; SK:25 vs SK:18 is Test 2.
Home: reproducibility (ownership: "what earns a step"). Edit: using-superra:34 → pointer only; SK loop step 1 deleted (Gate 1 carries it).

### C9. SK Loop vs SK Gates (same-file)
SK:19–20 (build then read status) vs SK:26 Gate 2 "its scoped build succeeds and every step the matching status reports is `fresh`"; PC:22 "The gate passes when the build completes and every reported step is `fresh`" repeats Gate 2 again.
Edit: Loop keeps only content the gate lacks (accept an expensive already-produced result; `--upstream` when the claim covers producers; what to write in Results). PC:22: "passes per SK Gate 2".

### C10. Commit-the-records — 3 copies
SK:21 "Commit changed execution and acceptance records with the work." / CMD:128 "Commit `repro-builds.json` with it" / CMD:148 "Commit the project-root `repro-acceptance.json` with the declarations and reviewed changes." / TFC:225 & 241 "committed". Keep file-status facts in TFC (tracked vs gitignored table), discipline in SK:21; delete CMD:148 s1.

### C11. Build guards
DX:36 s2 "Runtime declaration guards freeze the selected commands, paths, and output ownership, so unrelated tree edits do not invalidate running work; a relevant edit … requires retrying" vs TFC:256 (same content, fuller). Also misplaced under the explain table. Keep TFC:256 (or internals); DX keeps only "An edit to a running step's declaration or inputs: retry it."

### C12. Companion never upstream
DG:13 "A task companion is never upstream of main work" = using-superra/references/task-companion-files.md:9 "A companion is never upstream of main work" + :21 promote. Test 1. Keep only the new content: "Output consumed outside its task: promote (link) — never a dep edge into another task's `attachments/`."

### C13. Bind declared paths to routing
DG:42 "Bind declared paths to execution… sandbox preference included ([adoption.md])" vs AD:7 "Check that declared paths agree with the producer's routing…" Pick DG as home; AD:7 → pointer or drop.

### C14. Effective dependencies restated
TFC:111 "File-derived edges also contribute task prerequisites under Effective Dependencies; … Logical prerequisites govern task development and do not add file inputs" restates TFC:99. SK:10 "An out feeding another step's dep orders both steps and their tasks" restates TFC:99 (mechanic in skill). CMD:118 "`task frontier --json` additionally exposes actionable parent-owned steps with `kind: own-work`" = TFC:103. CMD:118 "`--json` returns the complete dependency snapshot so scope does not hide invalidity" ≈ TFC:107 "Task/step target selection cannot bypass global validation."

### C15. Status vocabulary
TFC:239 "The status vocabulary remains `fresh`, `stale`, `missing`, `failed`, and `external`." duplicates CMD:120-126 table; "remains" is change-narration. Delete.

---

## 2. Necessity failures (no duplicate, agent would not need it)

- TFC:136 "Generic Markdown viewers can open the task file; exact step jumping requires a renderer that emits the anchor." and dashboard link grammar — renderer trivia. Cut sentence 3; keep link form only if agents write dashboard links.
- TFC:195 pyyaml-vs-subset date/sexagesimal resolver note — the subset keeps strings; no agent action. Cut (~60 words).
- TFC:203 enumerated Julia include forms (~80 words): agent action is only "unresolved includes are reported — declare them". Compress to one sentence; enumerate in internals.md.
- TFC:188 "Existing explicit configurations retain this behavior." — change narration. Cut.
- TFC:219 "Not every retained artifact belongs in the graph, so it never blocks." — rationale clause. Cut to "Advisory; never blocks."
- TFC:99 "retaining both reasons when they coincide"; TFC:103 "avoiding a wait on the containing parent's child-status rollup"; TFC:107 "Structural `task tree` remains available without resolving shell configuration; `task read`, frontier, DAG, dependency checks, and mutation preflight resolve one shared snapshot." — implementation narration. Cut (~70 words).
- TFC:241–254 records internals (`lock_id` hex width, `_probes` key, receipts' 128 KiB/1 MiB snapshot caps, `execution_scope`) — no agent writes these files. Move to task-tree/references/internals.md; keep in TFC a 3-row table: file / committed? / never hand-edit. (~450 words out of the subagent load surface, since TFC §Reproduction Section is the one subagent exception.)
- TFC:258 lock-format history ("Older normal-output locks supply…") — migration trivia. Move to internals.
- CMD:106 error-behavior clauses ("a step name several steps share fails and lists their `task#step` forms. Unknown targets and tasks with no steps fail.") — the error message teaches this. Cut.
- CMD:116 status JSON field list — keep one line for scripting callers; move `local_status` detail to `--help`/internals.
- RA:11 "Significance is inferred from the graph, never marked in the section." — validation already rejects unknown keys (TFC:215). Cut.
- DX:19 "Warm file hashing costs one `stat` per file; variable discovery and graph construction are the other costs." — explanation, no action; AD:5 already carries the timing action. Cut; move "Sidecar tracking is for one measurably slow intermediate, never for an exhibit" to DG §Declare (it is a design rule, not diagnosis).
- DG:33 "Dropping a true dep is never a rung." — Test 2 vs DG:28 rung 1. Cut.
- DG:24 rationale sentence → compress to action: "Keep chains of short scripts in one step: each step pays interpreter start-up."
- PC:5 "(`skills/superintegrate/references/protect.md` step 3)" — protect.md step 2 already points here; circular pointer. Cut.
- CMD:154 "It states facts and a hint, never whether to build or accept." — borderline; the stale rule owns the decision. Cut or keep as one clause.

---

## 3. Opposite failure — compressed past meaning

1. **"boundary" has two meanings.** DG:45 "Stop at the boundary. An input the project receives rather than builds … is a dep with no producing step" (project boundary, status `external`) vs TFC:232/254 and CMD:116 `boundary_inputs` = "consumed artifacts from out-of-scope producers" (scope boundary = saved input). AD:3 "named saved-input boundary", DX:34 "Retrieve an agreed saved input", PC:9, SK:21 "the boundary inputs" use them interchangeably. An agent writing SK:21's Results line cannot tell which set to list. Edit: SK §The Model defines both — **saved input**: a file from a producer outside the selected targets, used as on disk; **external input**: a dep with no producing step, agreed with the researcher at Protect. Rename DG:45 "Stop at external inputs"; DX:34 "Retrieve the agreed external input".
2. **"Potentially significant" is not exhaustive** (RA:13–14): a producer outside `attachments/`, not on a "maintained path" (undefined), with no readers and not selected falls in neither class, so the stale rule has no row. Edit: make task-local the residual: "Everything else is significant."
3. **"maintained path"** (RA:14, CMD:114) undefined; DG:7 "maintained producer of a committed exhibit" is the closest. Point RA:14 at DG §What earns a step.
4. **"completion targets"** used in DG:58 and RA:14 before its only definition at PC:7. At IMPLEMENT exit (PC:15) Protect has not run, so "the Protect completion targets once recorded" (PC:22) leaves the first-pass target set undefined beyond "final deliverable tasks". Edit: define in SK §The Model; PC:22 state who picks targets before Protect (main agent proposes, researcher confirms).
5. **"producer chain"** (SK:20, DG:5, PC:22) — defined only in CMD:108 as "transitive file-producer ancestors". One-clause gloss in SK §The Model.
6. **"own-work"** (TFC:103, CMD:118) — defined only as a JSON kind; fine for tree deciders, but no action attached. Acceptable for the main agent; irrelevant to subagents.
7. SK:25 "a finding recorded in prose with no output file of its own included" — reads as "prose findings must be registered", but a step needs outs or `kind: check`; an agent cannot act. Rewrite: "A prose finding without its own output file still registers the script that produced it."
8. DG:5 "an unchanged script serving a new finding included" — same "X included" inversion. Rewrite: "Reuse the registered producer, even when an unchanged script serves a new finding."
9. DX:15 "Reviewed acceptance also stops upstream uncertainty; independently changed downstream inputs still require work." — "stops upstream uncertainty" is undefined. Rewrite: "An accepted step stops staleness propagating downstream; a downstream step with its own changed inputs is still stale."
10. PC:22 "requested fresh execution follows [the acceptance protocol]" — link goes to #accept for an execution request; contradictory. Rewrite: "When the researcher asks for fresh execution, build with `--force` on those targets."
11. DX:40 "Keep project and lockfiles versioned" — "lockfiles" collides with `pytask.lock`. Say "language environment files (`Project.toml`/`Manifest.toml`, `uv.lock`)".
12. AD:5 "a resolver that boots the language runtime" — "resolver" = a `vars: shell:` entry; undefined at point of load. Name it.
13. DG:22 "Derive configuration per consumer." — which configuration? Rewrite: "Split a shared config file into per-consumer files written by a cheap step, so an edit reruns only the consumers whose slice changed."
14. DG:44 "A published-result check reads the published root." — "published root" undefined.
15. DX:28 "rebuild when outputs are not shared" — shared via what (Dropbox/sync)? Say "when outputs don't sync between machines".
16. TFC:225 "`repro-acceptance.json` is committed separately from `pytask.lock`" — reads as "separate commit", contradicting CMD:148 ("with the declarations"). Say "is a separate committed file".
17. Hidden gate: DG:9 "`[BLOCKING]` for a drift test protecting registered outs" sits outside SK §Gates (the checklist implement-task/review-task walk), and conflicts with PC:8 which registers only drift tests "the researcher selects". Edit: decide one rule and move it into SK §Gates.

---

## 4. Routing / load surface

- **SK:14 routes every loader, including subagents, into commands.md §Reproduction** ("Flags, records, and step states"), and RA:36 → CMD §Reviewed acceptance, DX:23 → CMD §Explain. CLAUDE.md §Agent Load Surface (line 135) names only TFC §Reproduction Section as the subagent exception; subagents never load task-tree otherwise. Either (a) add "`commands.md` §Reproduction" to that exception explicitly, or (b) route subagents to `superra repro --help` (exists: repro_run.py argparse help covers targets, `--upstream`, `--force`) and keep CMD links only in main-agent-facing refs. (a) is simpler; but then CMD §Reproduction must be written as an agent reference and trimmed per §2/C5.
- **DG:48 links TFC §Effective Dependencies** — outside the §Reproduction Section exception, and it is dispatch-readiness mechanics for tree deciders. `task check` already names the cycle; replace link with "`task check` reports the cycle; fix declarations or ownership."
- **DG:13 links using-superra/references/task-companion-files.md** — fine (using-superra is subagent-loaded).
- **SK:22 PC link `../SKILL.md#the-loop`** (PC:22) — reference linking back up to SKILL.md; harmless, but "one level deep" is kept.
- **Mechanics → discipline links**: TFC:188 → DX §Environment changes (fine, pointer); CMD:169 → DX §What makes a step rerun (inverted: mechanic lives in discipline doc; fix via C3).
- **Routing table (SK:32–38)** load conditions are clear. Gap: reviewers get Gates only; Gate 3 links RA §The stale rule, whose table relies on RA §Classify above it — anchor to `#classify-the-steps-role` or merge. `diagnosing.md` "A state is not what you expected" is vague but workable.
- Every reference is one level deep. No reference requires loading `task-tree/SKILL.md`.
- Outside scope but noted: the completion-gate command pair is restated in superimplement/references/completion.md:18, superintegrate/references/integrate.md:9, finish.md:39 alongside pointers to PC — each is a one-line echo with a pointer (tolerable), but three copies of "build --upstream then clean status --upstream" is a drift surface.

## 5. Wrapper / "what you will receive" / default reminders
- RA:6 "act on it per diagnosing.md §Read what explain names before applying the rule below" — wrapper around authoritative table; keep only the link.
- AD:9 "Then follow designing-the-graph.md for the rest of the tree." — wrapper; acceptable routing, 10 words.
- CMD:112, CMD:144 s3, CMD:157–159, RA:5, RA:7, CMD:110 s2 — output narration (C5).
- DG:58 "The dashboard DAG navigator expands tasks into steps." — tells the agent what the UI shows; cut unless the agent must direct the researcher there (then say so).
- SK:11 "pytask 0.6 is the engine… freshness is pytask's content-hash comparison" — the actionable part is "never write `task_*.py`"; the rest is background. Compress.
- DX:23 "act on its rows instead of reconstructing them with `git log -S`, `shasum`, or `stat`" — KEEP: behavior-shaping non-default.

## 6. Cut estimate
- Skill: ~2,790 → ~2,050 words (−26%; ~740 words): DX §What makes a step rerun (−150, moves to TFC), DX §Cache (−45), RA §Preview (−60), RA:36 (−40), SK §Model/Loop (−90), DG:13/24/33/42 (−90), PC:5/22 (−50), AD:7 (−40), other clause trims (−175).
- TFC §Effective Deps→end: ~2,226 → ~1,400 in the agent-loaded file (−37%): records internals to internals.md (−450), YAML/Julia narration (−130), Effective Deps implementation clauses (−90), dashboard/renderer (−40), dup sentences (−110); +~90 for an Invalidation subsection absorbed from DX.
- CMD §Reproduction: ~1,681 → ~1,100 (−35%): §Explain anatomy (−220), dup scope/acceptance sentences (−150), output narration (−60), significance (−35), error behavior (−30), JSON/task read (−80).
- Total ≈ −2,100 words of agent-loaded text (~30%).

## 7. Top 10 edits (value order)
1. Define **saved input** vs **external input** (and completion targets, producer chain) once in SK §The Model; rename DG:45/DX:34/AD:3 accordingly. Fixes the two-meaning "boundary" (§3.1).
2. Collapse C1: one mechanic sentence at CMD:108, one discipline line at SK loop 3; delete the other 8 copies.
3. Move the rerun/invalidation model (DX §What makes a step rerun) into TFC §Reproduction Section; delete TFC:191 dup and CMD:169 inverted pointer (C3).
4. Move TFC:241–258 record internals to task-tree/references/internals.md; leave a 3-row tracked/ignored/never-hand-edit table. Largest subagent-load reduction.
5. Resolve the load-surface conflict: add CMD §Reproduction to CLAUDE.md:135's exception, or route subagents to `superra repro --help`; drop DG:48's §Effective Dependencies link.
6. Collapse CMD §Explain Sources/Builder/Output (−220 words) and the other output narration (CMD:112, CMD:144, RA:5–7).
7. Make the stale-rule classification exhaustive (task-local vs everything else) and define "maintained path" by pointer (§3.2–3).
8. Unify the drift-test registration rule (DG:9 hidden `[BLOCKING]` vs PC:8 "the researcher selects") and put it in SK §Gates.
9. Merge SK Loop steps 1–3 into Gates (C8/C9) and point using-superra:34 at SK Gate 1.
10. Fix the unactionable lines: SK:25 "…included", DG:5 "…included", DX:15 "stops upstream uncertainty", PC:22 "requested fresh execution follows the acceptance protocol", DX:40 "lockfiles", TFC:225 "committed separately".
