# Research Project Setup Skill — Results

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-05-21 (Task 1 implemented)
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

**Status:** Not started

## Task 3: Write `SKILL.md` + reference files

**Status:** Not started

## Task 4: Update superRA inventory surfaces

**Status:** Not started

## Task 5: End-to-end verification

**Status:** Not started

## Task 6: Deprecate the standalone `ResearchProjectTemplate` repo

**Status:** Not started
