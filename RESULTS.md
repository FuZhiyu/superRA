# Research Project Setup Skill — Results

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-05-21 (Task 5 partially implemented — automated steps passed; manual steps pending researcher action)
**Status:** In Progress

---

## Task 1: Scaffold skill directory + move templates

**Status:** IMPLEMENTED

Scaffolded `skills/research-project-setup/` with the four subdirectories (`scripts/`, `template/`, `template-share/`, `references/`) and populated it from the source `/Users/zhiyufu/Dropbox/package_dev/ResearchProjectTemplate` repo.

**Moves and outcomes:**
- `ProjectExample/` → [skills/research-project-setup/template/](skills/research-project-setup/template) via `cp -a` (preserves symlinks across repo boundary).
- The three internal symlinks (`Data`, `Notes`, `Output`) were retargeted from `../ProjectExample-Share/...` to `../template-share/...` so they resolve inside the skill. Verified with `readlink` and `ls -LA`: e.g. `Notes` → `../template-share/Notes`, which resolves to `.env` + `.gitkeep`.
- `ProjectExample-Share/` → [skills/research-project-setup/template-share/](skills/research-project-setup/template-share) via `cp -a`. Final contents: `Data/.gitkeep`, `Notes/.env`, `Notes/.gitkeep`, `Output/.gitkeep` (verified with `find`).
- `create_project.sh` → [skills/research-project-setup/scripts/create_project.sh](skills/research-project-setup/scripts/create_project.sh), `chmod +x` preserved.

**Single-source fold (`*-template.md` → in-skill `CLAUDE.md`/`README.md`):**
- [skills/research-project-setup/template/CLAUDE.md](skills/research-project-setup/template/CLAUDE.md) — dropped the example-specific "For Codex Only" block (lines 79–87 of the original `ProjectExample/CLAUDE.md`); kept the share-folder paragraph at line 29 (more informative variant).
- [skills/research-project-setup/template/README.md](skills/research-project-setup/template/README.md) — adopted the generic template-style phrasing from `README-template.md` at the seven diverging lines (intro paragraph, two-folder description, share-folder section header, "publication-quality" → "publication quality" punctuation).

**Verification:**
- `test -L` confirms `Data`, `Notes`, `Output` are symlinks under `template/`.
- `ls -LA template/Notes/` resolves to `.env` and `.gitkeep` via the new `../template-share/Notes` target.
- `Notes/.env` inspected — confirmed it is a placeholder template (`your_mistral_api_key_here`, etc.), no real secrets.
- Initial `git status` revealed the superRA root [.gitignore:3](.gitignore#L3) (`.claude/`) was silently swallowing `template/.claude/settings.json`, agents, and bundled skills (PDF, mistral, zotero, work-summary) — the same files the source `ResearchProjectTemplate` tracks under `ProjectExample/.claude/`. Without the fix Task 5 Step 1's `grep -F '"superRA@superRA"' /tmp/TestProj/.claude/settings.json` would fail because `create_project.sh` copies from an empty in-skill `.claude/`. Added a negation pair at [.gitignore:4-6](.gitignore#L4) to whitelist the bundled template skeleton.
- The `Notes`/`Data`/`Output` folder symlinks under `template/` are intentionally not git-tracked (matches source repo behavior — `create_project.sh` materializes them at scaffold time from `$SHARE_PATH`). They exist in the skill checkout only to document the design.

**Final staged file count:** 39 new files under `skills/research-project-setup/` (plus root `.gitignore`, `PLAN.md`, `RESULTS.md`).

**Notes for downstream tasks:**
- Task 2 will edit `scripts/create_project.sh` path constants (`$SCRIPT_DIR/ProjectExample/...` → `$SCRIPT_DIR/../template[-share]/...`).
- Task 3 will author `SKILL.md` + references from the source `.claude/skills/research-project-setup/SKILL.md`.

## Task 2: Update `create_project.sh` paths and add share-path sandbox registration

**Status:** IMPLEMENTED

Rewired [scripts/create_project.sh](skills/research-project-setup/scripts/create_project.sh) to read from the in-skill `template/` + `template-share/` siblings (instead of the old `$SCRIPT_DIR/ProjectExample/...` and `$SCRIPT_DIR/{CLAUDE,README}-template.md` paths), and added a `register_share_path_with_agents` helper that registers the absolute share-folder path with both Claude (`.claude/settings.local.json` → `permissions.additionalDirectories`) and Codex (`.codex/config.toml` → `[sandbox_workspace_write].writable_roots`). The same helper is mirrored verbatim into [template/setup_mac.sh](skills/research-project-setup/template/setup_mac.sh) for coauthor machines.

**Path constants rewritten** (11 sites in `create_project.sh`):
- `Notes/.env` source → `../template-share/Notes/.env`.
- `pyproject.toml`, `setup_mac.sh`, `.claude/`, `.codex/`, `.mcp.json`, `.gitignore`, `overleaf-sync`, `.github/` → `../template/{...}`.
- `CLAUDE-template.md`, `README-template.md` → `../template/CLAUDE.md`, `../template/README.md`.

**Registration helper placement:**
- `create_project.sh`: helper defined and called right after `.gitignore` is copied, before `./setup_mac.sh` runs — so the per-machine settings exist before the setup invocation.
- `setup_mac.sh`: helper defined and called right after the `Data`/`Notes`/`Output` symlinks are recreated (post-`$SHARE_PATH` resolution), before the superRA Codex agents block — coauthors get the same registration on first setup.

**Smoke test (`/tmp/SmokeProj` with `--share-path /tmp/SmokeShare --with-overleaf --with-ci`):**
- `Code/`, share `Data/`, `Notes` symlink and target all verified.
- `.claude/settings.local.json` contains `additionalDirectories = ["/tmp/SmokeShare", "/tmp/SmokeShare/Data", "/tmp/SmokeShare/Notes", "/tmp/SmokeShare/Output"]`.
- `.codex/config.toml` `writable_roots` block now contains the four absolute paths alongside the existing relative entries.
- `.gitignore` lists `.claude/settings.local.json` (Step 4 confirmed it was already present at [template/.gitignore:93](skills/research-project-setup/template/.gitignore#L93); no edit needed).
- Idempotency: re-running the helper a second time produced no duplicate entries — still exactly 4 `/tmp/SmokeShare` lines in each file.

**Step 4 outcome:** `template/.gitignore` already had `.claude/settings.local.json` on line 93 from the Task 1 move — no change required.

**Caveats:**
- The TOML rewrite in the helper uses a regex against `[sandbox_workspace_write] ... writable_roots = [ ... ]`. If the bundled `template/.codex/config.toml` is ever restructured (e.g., the writable_roots array is split across multiple TOML blocks or rewritten as TOML 1.1 inline tables), the regex would silently no-op. Acceptable for the current single-block layout; flagged here for future maintenance.
- The smoke test exercised the standalone CLI path. The agent-driven path (Task 5 Step 4) and the manual "open scaffolded project in Claude Code, no permission prompt" check (Task 5 Step 3) still need to run as part of end-to-end verification.

## Task 3: Write `SKILL.md` + reference files

**Status:** IMPLEMENTED

Authored the three markdown files for the new skill — [SKILL.md](skills/research-project-setup/SKILL.md), [references/feature-catalog.md](skills/research-project-setup/references/feature-catalog.md), [references/retrofit-playbooks.md](skills/research-project-setup/references/retrofit-playbooks.md) — following the `codex-superra-setup` shape (lean SKILL.md + on-demand references) and applying the `/CLAUDE.md` §"Teach the Protocol, Don't Prescribe Each Action" DRY + Necessity tests on every line.

**SKILL.md (87 lines):**
- Trigger-phrase frontmatter — verbatim from the PLAN.md Task 3 Step 1 spec.
- Body sections: what-the-skill-does paragraph, contributor symlink note (per Task 1 reviewer nuance — `template/{Data,Notes,Output}` are gitignored, materialized by `create_project.sh` at scaffold time), mode detection, fresh-setup procedure (4 sub-steps: collect → run → decision log → flag-dependent next steps), retrofit procedure (one-paragraph routing + 6-item playbook list, body in `retrofit-playbooks.md`), agent self-modification, when-to-ask vs when-to-act.
- Under the ~100–120-line target — the planning spec was nominal, not a floor; the DRY discipline left the body at 87 lines without dropping any required content. Verified by reading each section against the Step 1 spec checklist.
- Avoided wrapper-around-authoritative-content anti-patterns: no "if the user picked X, do Y" recap of the catalog (the catalog itself is loaded on demand); no restatement of the `AskUserQuestion` contract; no preview of what the dispatch will see.

**feature-catalog.md (51 lines):**
- One section per opt-in component, four required sub-fields (What it is / Default / Flag / Wiring after install).
- Four scaffold-time toggles (superRA Claude plugin, superRA Codex plugin, Overleaf, CI) + two retrofit-only entries (Figures/Tables restructure, decoupled `.share-path`) for the catalog's "what's available?" use case. Retrofit-only entries note `Default — N/A` and `Flag — N/A` with a pointer to the matching playbook.

**retrofit-playbooks.md (111 lines):**
- All six playbooks moved from the source `SKILL.md` (Lines 84–170 of `/Users/zhiyufu/Dropbox/package_dev/ResearchProjectTemplate/.claude/skills/research-project-setup/SKILL.md`).
- Path rewrites: `$TEMPLATE_DIR/ProjectExample/...` → `$SKILL_DIR/template/...` (with `$SKILL_DIR` defined as "the active superRA install's `skills/research-project-setup/`" at the file head).
- "Where this skill ships" source-side section dropped entirely (superseded by the new install-via-superRA model).
- Playbook 6 (decoupled `.share-path`) extended per Task 3 Step 3 spec: added Step 6 — register the new absolute `$SHARE_PATH` with both `.claude/settings.local.json` (`permissions.additionalDirectories`) and `.codex/config.toml` (`[sandbox_workspace_write].writable_roots`), mirroring `create_project.sh`'s `register_share_path_with_agents` helper.
- Playbook 5 (Figures/Tables restructure) — fixed the LaTeX-path bullet that was nonsensical in the source (`\includegraphics{Figures/...}` → `\includegraphics{Figures/...}`, a no-op) by rewriting it as a concrete inside-`Paper/` vs outside-`Paper/` distinction. Behavior-shaping correction, not a scope change.

**Verification:**
- `wc -l` on all three files: 87 / 51 / 111.
- Walked the SKILL.md DRY check against `/CLAUDE.md` §anti-patterns list — no wrapper instructions, no harness-default reminders, no restatement of the Skill-Load Manifest or the `AskUserQuestion` shape.
- Cross-checked SKILL.md trigger-phrase list against the PLAN.md Step 1 spec — verbatim.
- Cross-checked retrofit-playbooks.md feature list against PLAN.md Step 3 list — six playbooks, in the listed order.

## Task 4: Update superRA inventory surfaces

**Status:** IMPLEMENTED

Registered `research-project-setup` in the three inventory surfaces with one-liners derived from [skills/research-project-setup/SKILL.md](skills/research-project-setup/SKILL.md) (the authoritative source written in Task 3). The skill does not participate in the Skill-Load Manifest (no workflow Stage); confirmed in [skills/using-superRA/SKILL.md](skills/using-superRA/SKILL.md) — the Skill-Load Manifest tables were left untouched.

**Rows added:**
- [skills/CATEGORIES.md:45](skills/CATEGORIES.md#L45) — Utility table, inserted between `report-in-markdown` and `semantic-merge` (alphabetic). Long-form one-liner covering scaffolder + skeleton + six playbooks + standalone-invokable note.
- [README.md:86](README.md#L86) — Utility-skill table, inserted between `refactor-and-integrate` and `semantic-merge` (alphabetic for this table's existing ordering). Consistent wording with CATEGORIES.md.
- [skills/using-superRA/SKILL.md:61](skills/using-superRA/SKILL.md#L61) — Skill Inventory, Utility section, inserted between `refactor-and-integrate` and `report-in-markdown`. Tight one-line summary (this table's column width is narrow).

**Intro feature list extended:**
- [README.md:8](README.md#L8) — added a fourth axis to the top-of-README feature list: "Interactive project scaffolding + feature retrofit", listing the six playbooks. Sits below the existing workflow / domain-skills / utility-skills items.

**Verification:**
- `grep -n "research-project-setup" skills/CATEGORIES.md README.md skills/using-superRA/SKILL.md` returns one row per file (no duplicates).
- Alphabetic placement holds in each table (`report-in-markdown` < `research-project-setup` < `semantic-merge`).
- Skill-Load Manifest tables (`Generic` + `Domain add-ons` in `using-superRA/SKILL.md`) were not modified — the skill is user-trigger-invoked, not Stage-driven, per the plan.

## Task 5: End-to-end verification

**Status:** IMPLEMENTED (partial — automated steps passed; Steps 3, 4, 5, 7 require a fresh Claude Code / Codex session in a different working directory and must be run by the researcher).

### Step 1: Standalone scaffolder with arbitrary share path — PASS

Ran `bash skills/research-project-setup/scripts/create_project.sh /tmp/TestProj --share-path /tmp/TestShareDropbox --with-overleaf --with-ci`. Scaffolder completed (one upstream package failure during `uv sync` — `zotero-mcp` upstream rename, the script catches and skips per design; not caused by this PR).

Assertions (each command + the matching matched line):

- `find /tmp/TestProj -maxdepth 2 -type d` produced `Code/`, `Paper/Figures`, `Paper/Tables`, `Slides`, `.claude/`, `.codex/`, `.github/workflows/` — full expected tree.
- `test -L /tmp/TestProj/Data && [ "$(readlink Data)" = "/tmp/TestShareDropbox/Data" ]` → ok (target matches).
- `test -L /tmp/TestProj/Notes` → ok; target `/tmp/TestShareDropbox/Notes`.
- `test -L /tmp/TestProj/Output` → ok; target `/tmp/TestShareDropbox/Output`.
- `test -d /tmp/TestProj/Paper/Figures` → ok.
- `test -d /tmp/TestProj/.github/workflows` → ok.
- `test -x /tmp/TestProj/overleaf-sync` → ok.
- `cat /tmp/TestProj/.claude/settings.local.json` printed the expected JSON with `permissions.additionalDirectories` containing exactly four entries — `/tmp/TestShareDropbox`, `/tmp/TestShareDropbox/Data`, `/tmp/TestShareDropbox/Notes`, `/tmp/TestShareDropbox/Output`.
- `grep -F '/tmp/TestShareDropbox' /tmp/TestProj/.claude/settings.local.json` → lines 4–7 matched.
- `grep -F '/tmp/TestShareDropbox' /tmp/TestProj/.codex/config.toml` → lines 18–21 matched inside `[sandbox_workspace_write].writable_roots`.
- `grep -xF '.claude/settings.local.json' /tmp/TestProj/.gitignore` → matched line 93.
- `grep -F '"superRA@superRA"' /tmp/TestProj/.claude/settings.json` → matched line 59 (`"superRA@superRA": true`).
- `grep -F 'plugins."superra@superra"' /tmp/TestProj/.codex/config.toml` → matched line 34 (`[plugins."superra@superra"]`).

**Minor cosmetic observation (Task 2 territory, not a blocker for Task 5):** the Codex registration helper appends the new entries on the same line as the last pre-existing entry — `/tmp/TestProj/.codex/config.toml` line 18 reads `"~/.local/share/uv",    "/tmp/TestShareDropbox",` instead of placing the first new entry on its own line. The TOML is syntactically valid and parses identically, but the layout is uneven. If this matters cosmetically, the fix is to add a leading newline in the helper's `additions` join (`'\n' + '\n'.join(additions)`); flagged here so the integration pass can decide.

### Step 2: Opt-out flags strip declarations — PASS

Ran `bash skills/research-project-setup/scripts/create_project.sh /tmp/TestProjNoSR --no-superra --no-codex`.

- `grep -F '"superRA@superRA"' /tmp/TestProjNoSR/.claude/settings.json` → exit 1, no match (printed `ok — superRA not declared`). The settings.json still exists (carries unrelated default permissions), but no superRA enrollment line is present.
- `test ! -d /tmp/TestProjNoSR/.codex` → ok, `.codex/` directory not present (`ls -la /tmp/TestProjNoSR/` confirms — no `.codex` entry; only `.claude`, `.git`, `.gitignore`, `.mcp.json`, `.share-path`, `.venv`).

### Step 3: Open scaffolded project in Claude Code, write into share folder without prompt — PENDING (researcher)

Requires a fresh Claude Code session opened in the scaffolded project directory. Concrete reproduction for the researcher:

```bash
rm -rf /tmp/TestProj /tmp/TestShareDropbox && mkdir -p /tmp/TestShareDropbox
bash /Users/zhiyufu/package_dev/superRA-project-template/skills/research-project-setup/scripts/create_project.sh \
    /tmp/TestProj --share-path /tmp/TestShareDropbox --with-overleaf --with-ci
# Then open a fresh Claude Code session with cwd=/tmp/TestProj and ask:
#   "touch a file at Notes/test.txt and stage it"
# PASS = no permissions prompt for writing into the share folder; the file is created.
# FAIL = a permission prompt appears for /tmp/TestShareDropbox/Notes/test.txt.
```

If FAIL: the share-path registration in `.claude/settings.local.json` is not being honored — re-inspect Task 2 Step 2 helper and Claude's `additionalDirectories` semantics.

### Step 4: Agent fresh-setup path — PENDING (researcher)

Requires a fresh Claude Code or Codex session in an empty directory.

```bash
mkdir -p /tmp/AgentFreshSetup && cd /tmp/AgentFreshSetup
# Open Claude Code or Codex with cwd here. Then ask:
#   "create a new research project named VerifyFoo"
```

Expected:
- Agent invokes `research-project-setup` skill (mode = fresh-setup).
- Asks the four-checkbox opt-in question (superRA Claude plugin / Codex / Overleaf / CI) exactly once.
- Runs `create_project.sh` with the resulting flags.
- Writes `<share-path>/Notes/setup_decisions.md` with a three-line user-decision blockquote.

### Step 5: Agent retrofit path — PENDING (researcher)

In the project produced by Step 4 (or any existing scaffolded project), open a fresh agent session there and ask:

```
add Overleaf sync to this project
```

Expected:
- Agent invokes `research-project-setup` skill (mode = retrofit).
- Applies the Overleaf playbook from [skills/research-project-setup/references/retrofit-playbooks.md](skills/research-project-setup/references/retrofit-playbooks.md) — copies `overleaf-sync` from `skills/research-project-setup/template/overleaf-sync`, updates `.gitignore`, commits a single feature-scoped commit.

### Step 6: superRA-internal regression — PASS

Ran `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check`.

Output:
```
All generated agent files are up to date in /Users/zhiyufu/package_dev/superRA-project-template/.codex/agents
All generated direct-mode role references are up to date
```
Exit code: `0`. Confirms the existing codex-superra-setup tooling still functions and the newly-added skill did not perturb the generated agent files.

### Step 7: Inventory discoverability — PENDING (researcher)

Requires a fresh Claude Code session (any directory) with superRA installed. Type a trigger phrase such as:

```
create a new research project
```

Expected: the harness surfaces `research-project-setup` in its skill auto-trigger or skill list. Inspect via `/skills` or by triggering an invocation.

### Step 8: Cleanup — DONE

`rm -rf /tmp/TestProj /tmp/TestShareDropbox /tmp/TestProjNoSR /tmp/TestProjNoSR-Share` executed; `ls /tmp/ | grep -E '(TestProj|TestShare)'` returns no matches.

**Note for researcher:** when running Steps 3–5 / 7 later, re-clean these paths afterward; Step 4 will create a `VerifyFoo` project that should be moved or deleted post-verification.

## Task 6: Bundle LaTeX templates (manuscript + slides + references.bib)

**Status:** IMPLEMENTED

### Files added

- [skills/research-project-setup/template/Paper/manuscript.tex](skills/research-project-setup/template/Paper/manuscript.tex) — article-class manuscript stub. Preamble mirrors the IntermediaryDemand source for the portable, generic subset: 12pt article + geometry 1in margins + biblatex (biber, authoryear, natbib=true) + standard math (`amsmath`, `amssymb`, `amsthm`), figure (`graphicx`, `caption`, `subcaption`, `placeins`, `float`), table (`booktabs`, `multirow`, `makecell`), tikz/pgfplots, and hyperref. Operator macros `\argmax \argmin \diag \sgn \Var \Cov \Corr`. Generic colored note macros `\NOTEA \NOTEB \NOTEC` (placeholders for coauthor initials). Title placeholder `\title{ProjectExample}` is rewritten by the scaffolder.
- [skills/research-project-setup/template/Slides/slides.tex](skills/research-project-setup/template/Slides/slides.tex) — beamer + metropolis theme stub. Mirrors the LSE slides preamble: 16:9 aspect ratio, progressbar frame title, `\metroset{titleformat=smallcaps, numbering=fraction}`, mirrored math operators, shared bib via `\addbibresource{../references.bib}`, three TODO frames + `[allowframebreaks]` references frame in `\appendix`.
- [skills/research-project-setup/template/references.bib](skills/research-project-setup/template/references.bib) — empty bib at project root, shared by both `Paper/` and `Slides/` via `\addbibresource{../references.bib}`. Carries a commented-out example article entry so authors see the expected format.

### Files updated

- [skills/research-project-setup/SKILL.md](skills/research-project-setup/SKILL.md) — added one sentence after the "skill bundles three things" paragraph describing the bundled LaTeX scaffolding and the `\title{ProjectExample}` sed substitution.
- [skills/research-project-setup/scripts/create_project.sh](skills/research-project-setup/scripts/create_project.sh) — added a 12-line block after `mkdir -p Code Paper/...` that copies the three new template files into the scaffolded project, applying the `sed s/ProjectExample/$PROJECT_NAME/g` substitution to the two `.tex` files. This wiring is implicit in PLAN.md Step 5 (the smoke-test assertions check for these files at the scaffolded paths) but was not enumerated as an explicit step.

### Additions beyond the PLAN.md preamble

The dispatch steering allowed adding packages the user clearly relies on that are portable to a generic template. The implementation added:

- `\usepackage{comment}` — utility for block comments; present in source.
- Standard theorem environments (`\newtheorem{theorem}{Theorem}` plus `proposition`, `lemma`, `corollary`, `definition`, `assumption`) — heavily relied upon in the source manuscript and effectively universal for econ papers.

Items in the source that were intentionally NOT included (per dispatch steering or for portability): `\NOTEZ`/`\NOTEJ`/`\NOTEM` (replaced by generic `\NOTEA`/`\NOTEB`/`\NOTEC`), `\jane`/`\manav`/`\zhiyu` colored-text macros, `output-myclipboard.cpy` clipboard package, `xr` cross-doc package, `\definecolor{...}` block (project-specific palette), `\usepackage{epsf}` (legacy), `\usepackage{alphabeta}` / `blkarray` / `dsfont` / `soul` / `mathrsfs` (used only in IntermediaryDemand-specific contexts), and the IntermediaryDemand-specific tikz library imports beyond pgfplots defaults.

### Verification

Smoke test (PLAN.md Step 5) executed against `/tmp/LatexProj`:

| Assertion | Result |
| --- | --- |
| `Paper/manuscript.tex` present in scaffolded project | pass |
| `Slides/slides.tex` present | pass |
| `references.bib` present at project root | pass |
| `\title{LatexProj}` in `Paper/manuscript.tex` (sed substitution worked) | pass |
| `\title{LatexProj}` in `Slides/slides.tex` | pass |

LaTeX compile (soft check):

| Document | Toolchain | Result |
| --- | --- | --- |
| `Paper/manuscript.tex` | `latexmk -pdf -interaction=nonstopmode` (pdfLaTeX + biber) | compiled cleanly to a 1-page PDF (75 KB); bibliography pass via biber |
| `Slides/slides.tex` | same | compiled cleanly to a 5-page PDF (43 KB); bibliography pass via biber |

Both compile under the default pdfLaTeX toolchain on the local TeX Live 2026 install. The metropolis beamer theme often requires LuaLaTeX/XeLaTeX in other environments — the soft-check note in PLAN.md Step 5 still applies to coauthors with different LaTeX installs.

`/tmp/LatexProj` and `/tmp/LatexProj-Share` cleaned after verification.

## Task 7: Deprecate the standalone `ResearchProjectTemplate` repo

**Status:** Not started
