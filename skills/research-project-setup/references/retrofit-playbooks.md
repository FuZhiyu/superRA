# Retrofit Playbooks

Six playbooks for adding template features to an existing project. Each is independent; commit per feature so the user can review.

`$SKILL_DIR` below refers to the active superRA install's `skills/research-project-setup/` directory.

---

## 1. Add superRA Claude plugin

Goal: declare `superRA@superRA` in `.claude/settings.json`.

1. Read existing `.claude/settings.json` (or create one if missing). If it exists but lacks `enabledPlugins`, merge.
2. Add:
   ```json
   "enabledPlugins": { "superRA@superRA": true },
   "extraKnownMarketplaces": {
     "superRA": { "source": { "source": "github", "repo": "FuZhiyu/superRA" } }
   }
   ```
3. Commit titled `add: superRA Claude plugin declaration`.
4. Tell the user to restart Claude Code so the plugin loads.

Reference: `$SKILL_DIR/template/.claude/settings.json` is the canonical example.

---

## 2. Add superRA Codex plugin + named agents

Goal: declare the Codex plugin in `.codex/config.toml` and install `superra_implementer` / `superra_reviewer` into `.codex/agents/`.

1. Create or merge `.codex/config.toml` with:
   - `[marketplaces.superra]` pointing at `https://github.com/FuZhiyu/superRA.git`
   - `[plugins."superra@superra"] enabled = true`
   - `[agents.superra_implementer]` and `[agents.superra_reviewer]` registry entries
   - `sandbox_mode = "workspace-write"` and a matching `[sandbox_workspace_write]` block (if no existing sandbox block)
   - Copy from `$SKILL_DIR/template/.codex/config.toml` verbatim and adjust for project specifics.
2. Create `.codex/agents/` directory.
3. Invoke `superRA:codex-superra-setup` (or run the installer directly):
   ```bash
   cd <project>
   python3 $HOME/package_dev/superRA/skills/codex-superra-setup/scripts/sync_codex_agents.py \
       --scope project --repo-root $HOME/package_dev/superRA
   ```
4. Verify `.codex/agents/superra_implementer.toml` and `.codex/agents/superra_reviewer.toml` exist.
5. Commit titled `add: superRA Codex plugin + named agents`.

---

## 3. Add Overleaf sync

Goal: ship the `overleaf-sync` script + document the wiring.

1. Confirm there is a `Paper/` directory at the project root (the subtree prefix). If the project predates the v2 layout and has top-level `Figures/`/`Tables/`, ask before restructuring — see playbook 5.
2. Copy `$SKILL_DIR/template/overleaf-sync` to the project root. `chmod +x`.
3. Add `.Paper-pre-subtree-backup/` to `.gitignore`.
4. Optionally update README with the Overleaf section (see `$SKILL_DIR/template/README.md` for wording).
5. Commit titled `add: Overleaf subtree sync`.
6. Tell the user the one-time wiring step:
   ```bash
   git remote add overleaf https://git@git.overleaf.com/<PROJECT_ID>
   ```
   And the daily commands: `./overleaf-sync {status,pull,push}`.

---

## 4. Add GitHub Actions CI

Goal: ship `.github/workflows/render-pdfs.yml` and `publish-paper.yml`.

1. Copy `$SKILL_DIR/template/.github/workflows/render-pdfs.yml` and `publish-paper.yml` to `<project>/.github/workflows/`.
2. Optionally update README with the CI section.
3. Commit titled `add: GitHub Actions CI workflows`.
4. Tell the user, on GitHub:
   - Set repo variables: `PAPER_DIR` (default `Paper`), `PAPER_TEX` (or leave for auto-detect), `PAPER_TARGET_REPO` (only if publishing PDF to a separate public repo).
   - Set repo secret: `PAPER_PAT` (PAT with write access to `PAPER_TARGET_REPO`), only if publishing.

---

## 5. Restructure Figures/Tables under Paper/

Goal: move top-level `Figures/`, `Tables/` (pre-v2 layout) under `Paper/`. **Breaking change** — confirm with the user first.

1. Ask via `AskUserQuestion` whether to proceed; warn that LaTeX `\includegraphics` / `\input` paths in the manuscript will need updating.
2. If yes:
   ```bash
   git mv Figures Paper/Figures
   git mv Tables Paper/Tables
   ```
3. Update LaTeX paths: from inside `Paper/`, `\includegraphics{Figures/...}` and `\input{Tables/...}` remain correct (manuscript-relative). From outside `Paper/`, `\input{../Tables/...}` becomes `\input{../Paper/Tables/...}`.
4. Update `.gitignore` whitelist: `!Paper/Figures/*.{png,pdf}`, `!Paper/Tables/*.{tex,pdf}`.
5. Commit titled `restructure: Figures/ and Tables/ under Paper/`.

---

## 6. Switch from sibling-Share to decoupled `.share-path`

Goal: replace the old `../<Name>-Share/` assumption with a `.share-path` file + idempotent symlinks, and register the new absolute share path with the Claude and Codex sandboxes so agents can write into it.

1. Read the existing symlinks (`Data`, `Notes`, `Output`) — resolve targets via `readlink`. Confirm a single common parent; treat that as the new `$SHARE_PATH`.
2. Write the absolute path to `.share-path`.
3. Recreate symlinks idempotently:
   ```bash
   for sub in Data Notes Output; do
       ln -sfn "$SHARE_PATH/$sub" "./$sub"
   done
   ```
4. Add `.share-path` and `.claude/settings.local.json` to `.gitignore` if not already listed.
5. Search `.claude/settings.json`, `.codex/config.toml`, and any other config files for hard-coded `../<Name>-Share` references; replace with `./Data`, `./Notes`, `./Output` (symlink-relative).
6. Register `$SHARE_PATH` with the Claude and Codex sandboxes — merge into `.claude/settings.local.json` (`permissions.additionalDirectories`) and `.codex/config.toml` (`[sandbox_workspace_write].writable_roots`), four entries each (`$SHARE_PATH` + the three subdirectories). This mirrors what `create_project.sh` does at scaffold time; reuse the `register_share_path_with_agents` helper from `$SKILL_DIR/scripts/create_project.sh` if extracting it into a one-off script is easier than rewriting.
7. Commit titled `switch: decoupled share-folder via .share-path`.
