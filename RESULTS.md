# Research Project Setup Skill — Results

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-05-21 (Task 4 implemented)
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

**Status:** Not started

## Task 6: Deprecate the standalone `ResearchProjectTemplate` repo

**Status:** Not started
