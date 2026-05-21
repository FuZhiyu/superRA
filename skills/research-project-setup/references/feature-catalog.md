# Feature Catalog

What the bundled template installs and what each opt-in component requires after install. Loaded on demand when the user asks "what's available?" or when the agent needs to remind itself of a flag's effect.

The first four are toggleable at scaffold time via `create_project.sh` flags. The last two are retrofit-only — they have no opt-in flag because they are layout migrations applied to existing projects.

---

## superRA Claude plugin

- **What it is** — Declares `superRA@superRA` in `.claude/settings.json` so Claude Code loads the superRA marketplace skills (workflow, domain, utility) in this project.
- **Default** — ON.
- **Flag** — `--no-superra` to skip.
- **Wiring after install** — restart Claude Code so the plugin loads. No further configuration needed.

## superRA Codex plugin + named agents

- **What it is** — Declares the superRA Codex plugin in `.codex/config.toml` (`[marketplaces.superra]`, `[plugins."superra@superra"]`, agent registry entries for `superra_implementer` / `superra_reviewer`) and installs the named-agent TOMLs into `.codex/agents/`.
- **Default** — ON.
- **Flag** — `--no-codex` to skip (strips `.codex/` entirely).
- **Wiring after install** — if the user does not already have superRA cloned locally, `git clone https://github.com/FuZhiyu/superRA ~/package_dev/superRA`, then in the new project `./setup_mac.sh` to materialize the named-agent TOMLs via `skills/codex-superra-setup/scripts/sync_codex_agents.py`.

## Overleaf sync

- **What it is** — Copies the `overleaf-sync` script to the project root for git-subtree sync of `Paper/` against an Overleaf project.
- **Default** — OFF.
- **Flag** — `--with-overleaf` to include.
- **Wiring after install** — `cd <project> && git remote add overleaf https://git@git.overleaf.com/<PROJECT_ID>`. Daily commands: `./overleaf-sync {status,pull,push}`.

## GitHub Actions CI

- **What it is** — Copies `.github/workflows/render-pdfs.yml` and `publish-paper.yml` for LaTeX auto-compile on push and PDF publishing to a downstream public repo.
- **Default** — OFF.
- **Flag** — `--with-ci` to include.
- **Wiring after install** — on GitHub set repo variables `PAPER_DIR` (default `Paper`), `PAPER_TEX` (or leave for auto-detect), `PAPER_TARGET_REPO` (only if publishing PDF to a separate public repo). If publishing: set repo secret `PAPER_PAT` (PAT with write access to `PAPER_TARGET_REPO`).

---

## Retrofit-only: restructure Figures/Tables under Paper/

- **What it is** — Moves pre-v2 top-level `Figures/` and `Tables/` directories under `Paper/Figures/` and `Paper/Tables/`. Breaking change: manuscript `\includegraphics` / `\input` paths must be updated.
- **Default** — N/A (retrofit-only, applied on demand).
- **Flag** — N/A.
- **Wiring after install** — see retrofit-playbooks.md §5 for the destructive-confirm protocol.

## Retrofit-only: decoupled `.share-path`

- **What it is** — Replaces the old sibling-`<Name>-Share/` assumption with a `.share-path` file (absolute path, per-machine, gitignored) plus idempotent symlinks. Also rewrites `.claude/settings.local.json` and `.codex/config.toml` so sandboxed agents can write into the new absolute share path.
- **Default** — N/A (retrofit-only — new projects scaffolded by `create_project.sh` already use the decoupled layout).
- **Flag** — N/A.
- **Wiring after install** — see retrofit-playbooks.md §6.
