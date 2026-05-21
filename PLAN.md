# Research Project Setup Skill — Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all PLAN.md / RESULTS.md editing. This is contributor work on superRA itself (skill authoring) — no implemented domain vertical applies. Steps use checkbox (`- [ ]`) syntax for tracking and cross-session handoff. Treat skill/agent edits per `/CLAUDE.md` Contributor Discipline (load `skill-creator` before editing any `skills/*/SKILL.md`).

**Objective:** Add a new `skills/research-project-setup/` skill to superRA that owns interactive project scaffolding and feature retrofit, bundling the canonical project skeleton and the `create_project.sh` scaffolder; then deprecate the standalone `ResearchProjectTemplate` repo.

**Methodology:** Move the existing assets (`ProjectExample/`, `ProjectExample-Share/`, `create_project.sh`, `.claude/skills/research-project-setup/SKILL.md`) from `/Users/zhiyufu/Dropbox/package_dev/ResearchProjectTemplate` into a new top-level superRA skill, restructured to match the `codex-superra-setup` pattern (SKILL.md + `scripts/` + references). Consolidate the duplicate `*-template.md` files into single source by folding their unique lines into `template/CLAUDE.md` / `template/README.md`. Extend `create_project.sh` to register the absolute share-folder path in `.claude/settings.local.json` (additionalDirectories) and `.codex/config.toml` (writable_roots) so agents have permission to write into arbitrarily-located share folders. Update superRA inventory surfaces (CATEGORIES.md, README.md, using-superRA SKILL.md). Verify end-to-end with the standalone script path and an agent-driven path.

**Domain vertical gap:** No implemented superRA domain vertical exactly matches "contributor / skill authoring" work. Following the planning-workflow Phase 1 guidance: "If the task is in a domain without an implemented vertical yet: proceed to Phase 2, but flag the gap to the researcher so they know superRA's domain coverage is not complete for this work." Flagged — proceeding with workflow-skill discipline only.

**Output:**
- `skills/research-project-setup/SKILL.md`
- `skills/research-project-setup/scripts/create_project.sh`
- `skills/research-project-setup/template/` (Git-side skeleton, with `Data`/`Notes`/`Output` symlinks preserved)
- `skills/research-project-setup/template-share/` (share-side skeleton)
- `skills/research-project-setup/references/feature-catalog.md`
- `skills/research-project-setup/references/retrofit-playbooks.md`
- Updated `skills/CATEGORIES.md`, `README.md`, `skills/using-superRA/SKILL.md`
- Deprecation commit in the separate `ResearchProjectTemplate` repo (deferred, separate repo, separate commit)

**Expected Results:**
- Installing superRA gives the user both a "create a new research project" interactive capability and the underlying `create_project.sh` they can run directly.
- A scaffolded project with `--share-path "$HOME/Dropbox/.../Foo-Share"` lets Claude Code (and Codex) write into `Notes/`, `Data/`, `Output/` without permission prompts because the absolute share-folder path is registered at scaffold time.
- The standalone `ResearchProjectTemplate` repo carries only a deprecation README pointing at superRA install instructions.

**Sensitivity Analysis:** N/A — this is a refactor + move with verification, not an empirical analysis.

**Pipeline:** N/A (single skill addition; no multi-script dependency).

---

## Workflow Status

- [x] **Plan approved** — researcher approved via ExitPlanMode on 2026-05-21.
- [ ] **Execution complete** — all tasks `APPROVED`, end-to-end verification passes.
- [ ] **Drift tests created** — N/A for skill-authoring work; no key empirical results to lock. Mark satisfied at integration time with a one-line decision note if no drift tests are added.
- [ ] **Integrated** — branch synced with `main` and integration review `APPROVED`.
- [ ] **Docs finalized** — RESULTS.md matured, inventory surfaces audited.
- [ ] **Finished** — branch landed or PR opened; standalone `ResearchProjectTemplate` deprecation commit pushed.

---

## Project Conventions

Walked at planning time (2026-05-21). Re-walk on-demand only.

### Repo root
- `/CLAUDE.md` (HEAD at `3b5de66`): Contributor guidelines for superRA internals. Treat skill/agent edits as skill creation (load `skill-creator` first). Ownership boundaries table — `research-project-setup` is a new top-level skill, owns its concern and references project-skeleton + scaffolder. Internal design philosophy mandates: lean SKILL.md + references, behavior-shaping instructions only (DRY + Necessity tests), no wrapper instructions around authoritative content, no reminders of harness defaults. Generated artifacts (e.g., Codex agent TOMLs from `sync_codex_agents.py`) stay generated — PLAN.md must list them and the generator command when touched. Commit hygiene: stage only files this turn touched.
- `/AGENTS.md` and `/AGENT.md`: symlinks/aliases to `/CLAUDE.md`.
- `/README.md` (HEAD at `3b5de66`): User-facing product model. New skill must be added to its Utility-skills table and (optionally) the intro feature list. Skill inventory in `skills/using-superRA/SKILL.md` is the agent-facing authority and must mirror.

### Module-level docs walked
- `/skills/CATEGORIES.md` (HEAD at `3b5de66`): Authoritative grouping index. New skill goes under **Utility** with a one-row addition. The "Adding a Skill" section at the bottom encodes the four required surfaces to update (CATEGORIES.md row, README.md row, flat layout, optional stage-scoped references if domain skill — N/A here).
- `/skills/codex-superra-setup/SKILL.md` (HEAD at `3b5de66`): Pattern reference for the new skill — `SKILL.md` + `scripts/sync_codex_agents.py` shape. Mirrors what `research-project-setup` will look like (SKILL.md + `scripts/create_project.sh` + `template/` + `template-share/` + `references/`).
- `/skills/using-superRA/SKILL.md` (HEAD at `3b5de66`): Carries the Skill Inventory table (must add row) and the Skill-Load Manifest (no new Stage needed — this skill is invoked by user trigger phrases, not by workflow Stage).

### Source repo walked (not part of superRA)
- `/Users/zhiyufu/Dropbox/package_dev/ResearchProjectTemplate/README.md`: User-facing entry point of the template. Documents the two-folder design (`MyProject/` + share folder), `create_project.sh` flags, agent-driven setup via the `research-project-setup` skill, retrofit playbooks, superRA + Codex plugin declarations. Content is the source for `skills/research-project-setup/SKILL.md` and `references/feature-catalog.md`.
- `/Users/zhiyufu/Dropbox/package_dev/ResearchProjectTemplate/create_project.sh`: The scaffolder being moved. Existing flag parser (`--share-path`, `--no-superra`, `--no-codex`, `--with-overleaf`, `--with-ci`) is preserved; path constants and the new share-path sandbox-registration logic are added.
- `/Users/zhiyufu/Dropbox/package_dev/ResearchProjectTemplate/ProjectExample/`: Git-side skeleton. `Data`, `Notes`, `Output` are symlinks pointing at `../ProjectExample-Share/{Data,Notes,Output}`. Symlinks must survive the move with `cp -a` (or `cp -P`).
- `/Users/zhiyufu/Dropbox/package_dev/ResearchProjectTemplate/ProjectExample-Share/`: Share-side skeleton. Contains only `.gitkeep` in `Data/`, `Notes/`, `Output/`, and `Notes/.env` (API-key template).
- `/Users/zhiyufu/Dropbox/package_dev/ResearchProjectTemplate/.claude/skills/research-project-setup/SKILL.md`: Source SKILL.md being rewritten into the leaner superRA shape; existing six retrofit playbooks move into `references/retrofit-playbooks.md` verbatim.

### Not walked (not reachable from the planned diff)
- `superRA/hooks/`, `superRA/agents/implementer.md`, `superRA/agents/reviewer.md`, `superRA/skills/{econ-data-analysis,theory-modeling,writing,reproduction,semantic-merge,...}` — unchanged by this work.
- `ResearchProjectTemplate/TestDataAnalysis-Share/`, `ResearchProjectTemplate/ProjectExample-Share/Notes/.env` (treated as a template — not customized here), `ResearchProjectTemplate/.claude/settings.local.json` — local test/scratch artifacts.

---

## Decisions

> **User decision (2026-05-21):** Move canonical template files into the new superRA skill; do not retain separate `*-template.md` files — use the `ProjectExample/CLAUDE.md` and `ProjectExample/README.md` as the single source, applying `sed s/ProjectExample/$PROJECT_NAME/g` on copy. Fold the few extra lines that today live only in `CLAUDE-template.md` / `README-template.md` into the surviving copies.
> **Question asked:** Where should the canonical template files live? Do we still need separate `*-template.md` files?
> **Rationale:** Single source avoids drift; the variants differ by only a handful of lines.

> **User decision (2026-05-21):** Fully archive / deprecate the standalone `ResearchProjectTemplate` repo after the superRA-side changes land. Replace its README with a deprecation note pointing at superRA install. Do not delete the GitHub repo.
> **Question asked:** What should the standalone repo become?
> **Rationale:** Once the skill, script, and templates live in superRA, the old repo has nothing left to maintain.

> **User decision (2026-05-21):** Keep the retrofit feature catalog at parity with today — the six existing playbooks. No new retrofit features added in this PR.
> **Question asked:** Should retrofit playbooks expand now?
> **Rationale:** Move first, expand later — avoid scope creep.

> **User decision (2026-05-21):** Preserve the two-folder structure inside the skill — `template/` (Git skeleton, internal symlinks preserved) plus `template-share/` (share-side skeleton) — mirroring `ProjectExample/` + `ProjectExample-Share/` one-for-one.
> **Question asked:** Don't we have the two-folder structure originally?
> **Rationale:** The two-folder layout is the canonical design the template embodies; preserving it inside the skill visually documents the design and matches what `create_project.sh` provisions.

> **User decision (2026-05-21):** `create_project.sh` (and `setup_mac.sh`) must register the absolute share-folder path in `.claude/settings.local.json` (`additionalDirectories`) and in `.codex/config.toml` (`[sandbox_workspace_write] writable_roots`) when the user supplies a non-default share path, so the agents have permission to write into `Data/`/`Notes/`/`Output/` (whose symlink targets sit outside the project root).
> **Question asked:** When the share path is arbitrary, should the scaffolder also register it with Claude / Codex sandboxes?
> **Rationale:** Permissions are enforced against resolved absolute paths, not symlink names — without this, scaffolded projects with non-sibling share folders trigger permission prompts on every write into the share folder.

---

### Task 1: Scaffold skill directory + move templates

**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:** *(not started)*

**Script:** N/A (file moves + directory creation; no analysis code).
**Input:** `/Users/zhiyufu/Dropbox/package_dev/ResearchProjectTemplate/{ProjectExample,ProjectExample-Share,create_project.sh,CLAUDE-template.md,README-template.md}`
**Output:** `skills/research-project-setup/{scripts/,template/,template-share/,references/}` populated.

- [x] **Step 1: Create the skill directory tree and confirm absence**

```bash
cd /Users/zhiyufu/package_dev/superRA-project-template
mkdir -p skills/research-project-setup/{scripts,template,template-share,references}
ls -la skills/research-project-setup/
```

- [x] **Step 2: Copy `ProjectExample/` → `template/` preserving symlinks**

The internal `Data`, `Notes`, `Output` symlinks (`-> ../ProjectExample-Share/{Data,Notes,Output}`) must survive the move. After copying, retarget them at the new sibling `template-share/` so they resolve inside the skill directory.

```bash
SRC=/Users/zhiyufu/Dropbox/package_dev/ResearchProjectTemplate
DST=skills/research-project-setup/template
cp -a "$SRC/ProjectExample/." "$DST/"
# Retarget the three symlinks at the new sibling template-share/
for sub in Data Notes Output; do
    ln -sfn "../template-share/$sub" "$DST/$sub"
done
# Verify
for sub in Data Notes Output; do readlink "$DST/$sub"; done
ls -la "$DST/" | grep -E '^l'
```

- [x] **Step 3: Copy `ProjectExample-Share/` → `template-share/`**

```bash
SRC=/Users/zhiyufu/Dropbox/package_dev/ResearchProjectTemplate
DST=skills/research-project-setup/template-share
cp -a "$SRC/ProjectExample-Share/." "$DST/"
find "$DST" -mindepth 1 | sort
# Confirm: Data/.gitkeep, Notes/.gitkeep, Notes/.env, Output/.gitkeep
```

- [x] **Step 4: Fold `*-template.md` unique lines into `template/CLAUDE.md` and `template/README.md`**

Diff snapshot at planning time (Step 4 of approved plan): `CLAUDE-template.md` lacks the "For Codex Only" example-specific block and one share-folder paragraph at line 28–29; `README-template.md` has slightly leaner share-folder prose at lines 3–28. Keep the **template-style** (generic) wording where the variants differ. Concretely:

```bash
SRC=/Users/zhiyufu/Dropbox/package_dev/ResearchProjectTemplate
DST=skills/research-project-setup/template
diff "$SRC/CLAUDE-template.md" "$DST/CLAUDE.md"
diff "$SRC/README-template.md" "$DST/README.md"
# For each diff hunk, decide whether to keep the template-side (generic) or ProjectExample-side wording.
# Apply the resolved single-source version with Edit/Write directly on $DST/CLAUDE.md and $DST/README.md.
```

Decisions for the fold:
- **CLAUDE.md**: Drop the "For Codex Only" section (it lists ProjectExample-specific skills which are example-only context). Keep the share-folder paragraph from the ProjectExample copy (more informative).
- **README.md**: Use the generic phrasing from the template variant where it diverges (it is the rendered-into-a-new-project wording, which is what we want).

- [x] **Step 5: Copy `create_project.sh` → `scripts/create_project.sh` (paths edited in Task 2)**

```bash
SRC=/Users/zhiyufu/Dropbox/package_dev/ResearchProjectTemplate
DST=skills/research-project-setup/scripts/create_project.sh
cp -a "$SRC/create_project.sh" "$DST"
chmod +x "$DST"
head -20 "$DST"
```

- [x] **Step 6: Verify, stage, and commit**

```bash
# Verify all the moved content is in place and symlinks resolve.
ls -la skills/research-project-setup/
ls -la skills/research-project-setup/template/
ls -la skills/research-project-setup/template-share/
test -L skills/research-project-setup/template/Data
test -L skills/research-project-setup/template/Notes
test -L skills/research-project-setup/template/Output
ls -L skills/research-project-setup/template/Notes/  # should resolve into template-share/Notes
git add skills/research-project-setup
git status
git diff --cached --stat | head
git commit -m "feat(skill): scaffold research-project-setup with bundled template + share skeleton"
```

---

### Task 2: Update `create_project.sh` paths and add share-path sandbox registration

**Depends on:** Task 1
**Review status:** APPROVED
**Integration status:** *(not started)*

**Script:** `skills/research-project-setup/scripts/create_project.sh` (and the bundled `template/setup_mac.sh` for the coauthor side).
**Input:** The copied `create_project.sh` from Task 1.
**Output:** Updated script that (a) reads templates from the new in-skill paths and (b) writes the absolute share-folder path into `.claude/settings.local.json` and `.codex/config.toml` for arbitrary share paths.

- [x] **Step 1: Rewrite path constants**

Map (`$SCRIPT_DIR` is the script's own dir, now `skills/research-project-setup/scripts/`; `template/` and `template-share/` are siblings of `scripts/` under the skill root):

| Old | New |
| --- | --- |
| `$SCRIPT_DIR/ProjectExample/Notes/.env`             | `$SCRIPT_DIR/../template-share/Notes/.env` |
| `$SCRIPT_DIR/ProjectExample/pyproject.toml`         | `$SCRIPT_DIR/../template/pyproject.toml` |
| `$SCRIPT_DIR/ProjectExample/setup_mac.sh`           | `$SCRIPT_DIR/../template/setup_mac.sh` |
| `$SCRIPT_DIR/CLAUDE-template.md`                    | `$SCRIPT_DIR/../template/CLAUDE.md` |
| `$SCRIPT_DIR/README-template.md`                    | `$SCRIPT_DIR/../template/README.md` |
| `$SCRIPT_DIR/ProjectExample/.claude`                | `$SCRIPT_DIR/../template/.claude` |
| `$SCRIPT_DIR/ProjectExample/.codex`                 | `$SCRIPT_DIR/../template/.codex` |
| `$SCRIPT_DIR/ProjectExample/.mcp.json`              | `$SCRIPT_DIR/../template/.mcp.json` |
| `$SCRIPT_DIR/ProjectExample/.gitignore`             | `$SCRIPT_DIR/../template/.gitignore` |
| `$SCRIPT_DIR/ProjectExample/overleaf-sync`          | `$SCRIPT_DIR/../template/overleaf-sync` |
| `$SCRIPT_DIR/ProjectExample/.github`                | `$SCRIPT_DIR/../template/.github` |

Use `Edit` to apply each substitution in `skills/research-project-setup/scripts/create_project.sh`. After the edits, smoke-test it (Step 5).

- [x] **Step 2: Add share-path sandbox registration to `create_project.sh`**

After `SHARE_PATH` is resolved to absolute and after `.claude/settings.json` + `.codex/config.toml` are copied/patched, append a new section:

```bash
# Register the absolute share-folder path with Claude and Codex sandboxes so
# the agents can write into Data/Notes/Output regardless of where the share
# folder physically lives. settings.local.json is per-machine and gitignored.
register_share_path_with_agents() {
    local share_abs="$1"
    # Claude: .claude/settings.local.json — merge into additionalDirectories.
    mkdir -p .claude
    if [ -f .claude/settings.local.json ]; then
        python3 - "$share_abs" <<'PY'
import json, sys
share = sys.argv[1]
p = '.claude/settings.local.json'
with open(p) as f: cfg = json.load(f)
perms = cfg.setdefault('permissions', {})
dirs = perms.setdefault('additionalDirectories', [])
for d in (share, f"{share}/Data", f"{share}/Notes", f"{share}/Output"):
    if d not in dirs:
        dirs.append(d)
with open(p, 'w') as f: json.dump(cfg, f, indent=2)
PY
    else
        python3 - "$share_abs" <<'PY'
import json, sys
share = sys.argv[1]
cfg = {
    "permissions": {
        "additionalDirectories": [share, f"{share}/Data", f"{share}/Notes", f"{share}/Output"]
    }
}
with open('.claude/settings.local.json', 'w') as f: json.dump(cfg, f, indent=2)
PY
    fi

    # Codex: .codex/config.toml — append the absolute paths to writable_roots
    # alongside the existing relative ./Data /Notes /Output entries.
    if [ -f .codex/config.toml ]; then
        python3 - "$share_abs" <<'PY'
import re, sys
share = sys.argv[1]
p = '.codex/config.toml'
with open(p) as f: txt = f.read()
# Locate [sandbox_workspace_write] writable_roots = [ ... ] and inject the
# absolute paths just before the closing bracket if not already present.
m = re.search(r'(\[sandbox_workspace_write\][^\[]*writable_roots\s*=\s*\[)([^\]]*)(\])', txt, flags=re.DOTALL)
if m:
    body = m.group(2)
    additions = []
    for d in (share, f"{share}/Data", f"{share}/Notes", f"{share}/Output"):
        if d not in body:
            additions.append(f'    "{d}",')
    if additions:
        new_body = body.rstrip() + ('\n' if not body.endswith('\n') else '') + '\n'.join(additions) + '\n'
        txt = txt[:m.start(2)] + new_body + txt[m.end(2):]
        with open(p, 'w') as f: f.write(txt)
PY
    fi

    # Ensure .claude/settings.local.json is gitignored (per-machine, never committed).
    if ! grep -qxF '.claude/settings.local.json' .gitignore 2>/dev/null; then
        echo '.claude/settings.local.json' >> .gitignore
    fi
}

register_share_path_with_agents "$SHARE_PATH"
```

Place this call near the end of `create_project.sh`, *after* the `.claude/` and `.codex/` copies but *before* the final `setup_mac.sh` invocation (so the per-machine settings exist before `setup_mac.sh` runs — `setup_mac.sh` will run the same function on coauthor machines).

- [x] **Step 3: Mirror the registration into `template/setup_mac.sh` for coauthor machines**

`setup_mac.sh` runs after a coauthor clones the repo on a new machine; their `$SHARE_PATH` comes from `.share-path`. The same function lives there:

```bash
# Inside template/setup_mac.sh, after $SHARE_PATH is resolved (it currently
# reads from .share-path or prompts):
register_share_path_with_agents "$SHARE_PATH"   # same function body, copy verbatim
```

`Edit` `skills/research-project-setup/template/setup_mac.sh` to insert the same function definition and call.

- [x] **Step 4: Confirm `template/.gitignore` already lists `.claude/settings.local.json`** (idempotency check)

```bash
grep -nF '.claude/settings.local.json' skills/research-project-setup/template/.gitignore || echo "not yet listed — add it"
```

Add the entry if absent so freshly-scaffolded projects start with the right gitignore line.

- [x] **Step 5: Smoke-test the scaffolder against /tmp**

```bash
rm -rf /tmp/SmokeProj /tmp/SmokeProj-Share /tmp/SmokeShare
bash skills/research-project-setup/scripts/create_project.sh /tmp/SmokeProj \
    --share-path /tmp/SmokeShare --with-overleaf --with-ci
# Assertions:
test -d /tmp/SmokeProj/Code && echo "Code/ ok"
test -d /tmp/SmokeShare/Data && echo "share Data/ ok"
test -L /tmp/SmokeProj/Notes && echo "Notes symlink ok"
[ "$(readlink /tmp/SmokeProj/Notes)" = "/tmp/SmokeShare/Notes" ] && echo "Notes target ok"
grep -F "/tmp/SmokeShare" /tmp/SmokeProj/.claude/settings.local.json && echo "claude registration ok"
grep -F "/tmp/SmokeShare" /tmp/SmokeProj/.codex/config.toml && echo "codex registration ok"
grep -xF '.claude/settings.local.json' /tmp/SmokeProj/.gitignore && echo "gitignore ok"
# Re-run idempotency: a second registration call must not duplicate entries
bash -c 'cd /tmp/SmokeProj && . ../SmokeProj/setup_mac.sh 2>/dev/null; true'
test "$(grep -c "/tmp/SmokeShare\"" /tmp/SmokeProj/.codex/config.toml)" -le 4 && echo "no duplicate codex entries"
# Cleanup
rm -rf /tmp/SmokeProj /tmp/SmokeShare
```

- [x] **Step 6: Commit**

```bash
git add skills/research-project-setup/scripts/create_project.sh \
        skills/research-project-setup/template/setup_mac.sh \
        skills/research-project-setup/template/.gitignore
git commit -m "feat(skill): wire create_project.sh to new paths + share-path sandbox registration"
```

---

### Task 3: Write `SKILL.md` + reference files

**Depends on:** Task 1
**Review status:** APPROVED
**Integration status:** *(not started)*

**Script:** N/A — markdown authoring.
**Input:** Existing `/Users/zhiyufu/Dropbox/package_dev/ResearchProjectTemplate/.claude/skills/research-project-setup/SKILL.md` (source content for the move).
**Output:** `skills/research-project-setup/SKILL.md`, `skills/research-project-setup/references/feature-catalog.md`, `skills/research-project-setup/references/retrofit-playbooks.md`.

- [x] **Step 1: Author `SKILL.md`**

Frontmatter `description` must include trigger phrases (verbatim list):

```
Create a new academic research project from the bundled template, OR add template features to an existing project (superRA Claude plugin, Codex superRA plugin + named agents, Overleaf sync, GitHub Actions CI, decoupled .share-path, Figures/Tables restructure). Use when the user asks to "create a new research project", "scaffold a project", "bootstrap a research repo", "add Overleaf sync", "add CI workflows to this project", "retrofit superRA", or similar. Supports interactive opt-ins and ex-post retrofit on existing projects. Invokable standalone — does not require the PLAN→IMPLEMENT→INTEGRATE workflow.
```

Body structure (target ~100–120 lines):

1. One-paragraph "what this skill does".
2. **Mode detection** — Fresh-setup vs Retrofit detection signals (cwd-content based: empty/unrelated → fresh; presence of `pyproject.toml` / `Code/` / `setup_mac.sh` → retrofit). Ambiguous → one `AskUserQuestion`.
3. **Fresh-setup procedure** — collect inputs (name, destination, share path, one multi-select question for the four opt-ins: superRA Claude plugin / Codex / Overleaf / CI), invoke `scripts/create_project.sh` with the right flags, write `Notes/setup_decisions.md` decision log, report flag-dependent next steps.
4. **Retrofit procedure** — identify feature, look up playbook in `references/retrofit-playbooks.md`, apply targeted edits, one commit per feature.
5. **When-to-ask vs when-to-act** — carried over from the source skill body verbatim (good guidance and not duplicated elsewhere).
6. Pointers to `references/feature-catalog.md` (for "what's available?") and `references/retrofit-playbooks.md` (for the recipes).

Write directly with `Write` after authoring the content in-head.

- [x] **Step 2: Author `references/feature-catalog.md`**

One section per opt-in feature, each with:
- **What it is** — 1–2 sentence description
- **Default** — ON / OFF
- **Flag** — `create_project.sh` flag
- **Wiring it requires after install** — concrete next-steps

Features at launch (six total — four opt-ins plus the two retrofit-only ones for reference): superRA Claude plugin (ON), superRA Codex plugin + named agents (ON), Overleaf sync (OFF), GitHub Actions CI (OFF). Plus reference sections for the retrofit-only playbooks (Figures/Tables restructure; decoupled `.share-path`).

- [x] **Step 3: Author `references/retrofit-playbooks.md`**

Move the six playbooks from the source `SKILL.md` verbatim, updating paths:
- `$TEMPLATE_DIR/ProjectExample/...` → `$SKILL_DIR/template/...` (where `$SKILL_DIR` is `skills/research-project-setup/` of the active superRA install).
- The "Where this skill ships" section at the bottom of the source SKILL.md is dropped entirely (superseded by the new install model — the skill ships with superRA).

Playbooks:
1. Add superRA Claude plugin
2. Add Codex superRA plugin + named agents
3. Add Overleaf sync
4. Add GitHub Actions CI
5. Restructure Figures/Tables under `Paper/` (pre-v2 migration, destructive — confirm first)
6. Switch from sibling-Share to decoupled `.share-path` — **extended** to also rewrite `.claude/settings.local.json` and `.codex/config.toml` for the new absolute share path (mirroring the new logic in `create_project.sh` Task 2 Step 2).

- [x] **Step 4: Commit**

```bash
git add skills/research-project-setup/SKILL.md \
        skills/research-project-setup/references/feature-catalog.md \
        skills/research-project-setup/references/retrofit-playbooks.md
git commit -m "feat(skill): research-project-setup SKILL.md + feature catalog + retrofit playbooks"
```

---

### Task 4: Update superRA inventory surfaces

**Depends on:** Task 3 (skill body must exist so descriptions match)
**Review status:** IMPLEMENTED
**Integration status:** *(not started)*

**Script:** N/A — markdown edits to three inventory files.
**Input:** Existing `skills/CATEGORIES.md`, `README.md`, `skills/using-superRA/SKILL.md`.
**Output:** Same three files with a new row for `research-project-setup`.

- [x] **Step 1: Add Utility-table row in `skills/CATEGORIES.md`**

`Edit` the file; insert a new row in the Utility table (between `report-in-markdown` and `semantic-merge` alphabetically):

```markdown
| `research-project-setup` | Interactive scaffolder + retrofit playbooks for academic research projects. Owns `create_project.sh`, the canonical project skeleton (`template/` + `template-share/`), and the six feature playbooks (superRA Claude plugin, Codex superRA plugin + named agents, Overleaf sync, GitHub Actions CI, Figures/Tables restructure, decoupled `.share-path`). Invokable standalone — no workflow Stage. |
```

- [x] **Step 2: Add row to the Utility table in `/README.md`**

Insert in the Utility-skill table (alphabetic position). Use one-line summary consistent with the CATEGORIES.md row. Also extend the intro feature list at the top of the README to mention "interactive project scaffolding + feature retrofit" as a third axis.

- [x] **Step 3: Add row to the Skill Inventory in `skills/using-superRA/SKILL.md`**

Add to the Utility section of the Skill Inventory table:

```markdown
| Utility | `research-project-setup` | Interactive scaffolder + retrofit for academic research projects (`create_project.sh`, bundled template, six feature playbooks). Standalone-invokable. |
```

Confirm no row needs adding in the Skill-Load Manifest — this skill is invoked by user trigger phrases, not by workflow Stage, so it does not appear in the Stage → required-skills table.

- [x] **Step 4: Commit**

```bash
git add skills/CATEGORIES.md README.md skills/using-superRA/SKILL.md
git commit -m "docs: register research-project-setup in inventory surfaces"
```

---

### Task 5: End-to-end verification

**Depends on:** Task 2, Task 3, Task 4
**Review status:** *(not started)*
**Integration status:** *(not started)*

**Script:** Manual verification + small shell assertions.
**Input:** The completed skill from Tasks 1–4.
**Output:** A short verification log written into `RESULTS.md` Task 5 section.

- [ ] **Step 1: Standalone scaffolder with arbitrary share path**

```bash
rm -rf /tmp/TestProj /tmp/TestShareDropbox
mkdir -p /tmp/TestShareDropbox
bash skills/research-project-setup/scripts/create_project.sh /tmp/TestProj \
    --share-path /tmp/TestShareDropbox --with-overleaf --with-ci
# Structure
find /tmp/TestProj -maxdepth 2 -type d | sort
test -L /tmp/TestProj/Data && [ "$(readlink /tmp/TestProj/Data)" = "/tmp/TestShareDropbox/Data" ]
test -L /tmp/TestProj/Notes
test -L /tmp/TestProj/Output
test -d /tmp/TestProj/Paper/Figures
test -d /tmp/TestProj/.github/workflows
test -x /tmp/TestProj/overleaf-sync
# Sandbox registration
cat /tmp/TestProj/.claude/settings.local.json
grep -F '/tmp/TestShareDropbox' /tmp/TestProj/.claude/settings.local.json
grep -F '/tmp/TestShareDropbox' /tmp/TestProj/.codex/config.toml
grep -xF '.claude/settings.local.json' /tmp/TestProj/.gitignore
# superRA on by default
grep -F '"superRA@superRA"' /tmp/TestProj/.claude/settings.json
grep -F 'plugins."superra@superra"' /tmp/TestProj/.codex/config.toml
```

- [ ] **Step 2: Opt-out flags strip declarations**

```bash
rm -rf /tmp/TestProjNoSR /tmp/TestProjNoSR-Share
bash skills/research-project-setup/scripts/create_project.sh /tmp/TestProjNoSR --no-superra --no-codex
grep -F '"superRA@superRA"' /tmp/TestProjNoSR/.claude/settings.json && echo "FAIL — superRA still declared" || echo "ok"
test ! -d /tmp/TestProjNoSR/.codex && echo "ok — .codex stripped"
```

- [ ] **Step 3: Open scaffolded project in Claude Code and write into the share folder without prompt**

Manual: open `/tmp/TestProj` in a fresh Claude Code session, ask "touch a file at Notes/test.txt and stage it". Confirm no permissions prompt appears. (If a prompt does appear, the share-path registration failed — return to Task 2.)

- [ ] **Step 4: Agent fresh-setup path**

Manual: open a fresh Claude Code or Codex session in an empty directory and say "create a new research project named `VerifyFoo`". Confirm:
- Agent invokes the skill (mode = fresh-setup).
- Asks the four-checkbox opt-in question once.
- Runs `create_project.sh` with the right flags.
- Writes `<share-path>/Notes/setup_decisions.md` with the three-line user-decision blockquote.

- [ ] **Step 5: Agent retrofit path**

Manual: in the project produced by Step 4, say "add Overleaf sync to this project". Confirm:
- Agent invokes the skill (mode = retrofit).
- Applies the Overleaf playbook (copies `overleaf-sync` from `skills/research-project-setup/template/overleaf-sync`, updates `.gitignore`, commits).

- [ ] **Step 6: superRA-internal regression — codex agent sync still works**

```bash
python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check
echo "exit=$?"
```

- [ ] **Step 7: Inventory discoverability**

Open Claude Code in any directory with superRA installed; type a trigger phrase ("create a new research project"). Confirm the skill is surfaced by the harness.

- [ ] **Step 8: Cleanup + RESULTS.md**

```bash
rm -rf /tmp/TestProj /tmp/TestShareDropbox /tmp/TestProjNoSR /tmp/TestProjNoSR-Share
# Move VerifyFoo to /tmp before cleanup if it was scaffolded into the cwd.
```

Update `RESULTS.md` Task 5 section with the verification outcomes (pass/fail per step). Commit RESULTS.md.

---

### Task 6: Deprecate the standalone `ResearchProjectTemplate` repo

**Depends on:** Task 5 (verified-working superRA-side skill)
**Review status:** *(not started)*
**Integration status:** *(not started)*

**Script:** N/A — operates in a separate git repo (`/Users/zhiyufu/Dropbox/package_dev/ResearchProjectTemplate`).
**Input:** The verified superRA install.
**Output:** Deprecation commit in `ResearchProjectTemplate` pushed to its remote.

- [ ] **Step 1: Replace `ResearchProjectTemplate/README.md` with a deprecation note**

```markdown
# ResearchProjectTemplate (deprecated)

This template has moved into the [superRA](https://github.com/FuZhiyu/superRA) plugin under `skills/research-project-setup/`. To create a new academic research project:

**Agent-driven (recommended):** Install superRA in Claude Code or Codex, then ask: "create a new research project named `MyProject`."

**CLI (script directly):**
```bash
git clone https://github.com/FuZhiyu/superRA
bash superRA/skills/research-project-setup/scripts/create_project.sh MyProject [--share-path PATH] [--with-overleaf] [--with-ci] [--no-superra] [--no-codex]
```

See `superRA/skills/research-project-setup/SKILL.md` and `superRA/README.md` for details.

This repo is preserved for backlink stability but no longer maintained.
```

- [ ] **Step 2: Delete superseded files from `ResearchProjectTemplate`**

```bash
cd /Users/zhiyufu/Dropbox/package_dev/ResearchProjectTemplate
git rm -r ProjectExample ProjectExample-Share TestDataAnalysis-Share CLAUDE-template.md README-template.md create_project.sh PLAN.md RESULTS.md
# Keep: README.md (new), LICENSE (if present), .gitignore, .claude/skills/research-project-setup/ (delete too — already in superRA)
git rm -r .claude/skills/research-project-setup
git status
```

- [ ] **Step 3: Commit and push**

```bash
git add README.md
git commit -m "deprecate: move research-project-setup into superRA plugin"
git push origin main
```

- [ ] **Step 4: Confirm deprecation lands**

```bash
# Verify on GitHub:
gh repo view FuZhiyu/ResearchProjectTemplate --web
# Or via API:
gh api repos/FuZhiyu/ResearchProjectTemplate --jq '.description, .pushed_at'
```

Update the new `README.md` for the deprecated repo if `gh repo view` reveals additional surface (e.g., repo description, topics) that should reflect deprecation. Optionally edit the GitHub repo description through `gh repo edit FuZhiyu/ResearchProjectTemplate --description "Deprecated — moved into FuZhiyu/superRA"`.

---
