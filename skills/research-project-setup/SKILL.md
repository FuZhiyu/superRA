---
name: research-project-setup
description: Create a new academic research project from the bundled template, OR add template features to an existing project (superRA Claude plugin, Codex superRA plugin + named agents, Overleaf sync, GitHub Actions CI, decoupled .share-path, Figures/Tables restructure). Use when the user asks to "create a new research project", "scaffold a project", "bootstrap a research repo", "add Overleaf sync", "add CI workflows to this project", "retrofit superRA", or similar. Supports interactive opt-ins and ex-post retrofit on existing projects. Invokable standalone — does not require the PLAN→IMPLEMENT→INTEGRATE workflow.
---

# Research Project Setup

Scaffold a new academic research project from the bundled `template/` + `template-share/` skeleton, or retrofit an existing project with one of the template's opt-in features. The user does not need to remember CLI flags — ask via `AskUserQuestion` and run the right commands.

The skill bundles three things: `scripts/create_project.sh` (the scaffolder), `template/` (Git-side skeleton, with internal `Data`/`Notes`/`Output` symlinks pointing at `../template-share/`), and `template-share/` (share-side skeleton). The two-folder layout mirrors the design `create_project.sh` provisions on disk. Inside this skill, refer to the skill root as `$SKILL_DIR`.

**Symlink note for contributors.** The three internal symlinks under `template/` (`Data`, `Notes`, `Output`) are intentionally gitignored — a fresh `git clone` of superRA will not have them on disk. They are materialized by `create_project.sh` at scaffold time from the resolved `$SHARE_PATH`. The `template/` checkout exists to document the design and ship file content; the symlinks themselves are a scaffold-time artifact.

## Mode detection (always do first)

- **Fresh-setup** — brand-new project. Signals: cwd empty/unrelated, user names a not-yet-existing project, or words like "create" / "scaffold" / "new project".
- **Retrofit** — add features to an existing project. Signals: cwd contains `pyproject.toml` / `Code/` / `setup_mac.sh`, or "add X to this project" / "wire up Overleaf" / "add CI".

Ambiguous → one `AskUserQuestion`.

---

## Fresh-setup mode

1. **Collect inputs** — one `AskUserQuestion` call, multiple questions:
   1. **Project name** (Pascal-case, no spaces). Example: `MyResearchProject`.
   2. **Destination directory** — where the Git repo lands. Default: cwd.
   3. **Share folder path** — where `Data/`/`Notes/`/`Output/` live (typically under Dropbox). Default: sibling `<Name>-Share/`.
   4. **Optional components** (one multi-select with four checkboxes):
      - superRA Claude plugin (default ON)
      - superRA Codex plugin + named agents (default ON)
      - Overleaf sync (default OFF)
      - GitHub Actions CI (default OFF)

   See `references/feature-catalog.md` for what each opt-in installs and the wiring it requires after install.

2. **Run the scaffolder**:
   ```bash
   bash $SKILL_DIR/scripts/create_project.sh <name> [--share-path <PATH>] [--no-superra] [--no-codex] [--with-overleaf] [--with-ci]
   ```
   Pass `--share-path` only when non-default. Pass `--no-*` only when the user opted out. Pass `--with-*` only when the user opted in.

3. **Write the setup decision log** to `<share-path>/Notes/setup_decisions.md`. One blockquote per answered question:
   ```markdown
   > **User decision (YYYY-MM-DD):** <answer>
   > **Question asked:** <restatement>
   > **Rationale:** <only if user gave one>
   ```

4. **Report flag-dependent next steps** to the user:
   - `--with-overleaf` → `cd <project> && git remote add overleaf https://git@git.overleaf.com/<PROJECT_ID>`.
   - `--with-ci` → on GitHub, set repo variables `PAPER_DIR`, `PAPER_TEX`, `PAPER_TARGET_REPO` and (if publishing) secret `PAPER_PAT`.
   - superRA Codex on + no local clone of superRA → mention `git clone https://github.com/FuZhiyu/superRA ~/package_dev/superRA && cd <project> && ./setup_mac.sh` to enable the named Codex agents.

---

## Retrofit mode

Identify the requested feature, then apply the matching playbook in `references/retrofit-playbooks.md`. One commit per feature so the user can review independently.

The six playbooks:

1. Add superRA Claude plugin
2. Add superRA Codex plugin + named agents
3. Add Overleaf sync
4. Add GitHub Actions CI
5. Restructure top-level `Figures/` and `Tables/` under `Paper/` (pre-v2 migration — destructive, confirm first)
6. Switch from sibling-`<Name>-Share/` to decoupled `.share-path` — also rewrites `.claude/settings.local.json` and `.codex/config.toml` for the new absolute share path

If the user names a feature that isn't on this list, ask whether they want one of the above or whether to fall back to ad-hoc edits.

---

## Agent self-modification

After scaffold or retrofit, the agent may edit any of the created files directly per user request — add a `Snakefile`, append a `[tool.jupytext]` block, create a new `Code/<module>/` directory, etc. Mention the relevant file paths so the user can audit.

---

## When to ask vs when to act

- **Always confirm** before destructive operations: directory restructure, file deletions, force-rewrite of existing configs.
- **Always ask** when a flag/option is genuinely ambiguous from the user's request (e.g., they said "add CI" but didn't specify `PAPER_TARGET_REPO`).
- **Don't ask** about things the user clearly already decided ("add Overleaf to this project" → don't re-ask whether they want Overleaf).
- **Don't ask** about cosmetic defaults (commit-message wording) — pick a sensible default and report it.

Prefer one `AskUserQuestion` call with multiple sub-questions over a sequence of single questions.
