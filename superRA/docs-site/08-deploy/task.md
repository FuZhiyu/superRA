---
title: "Build Pipeline + GitHub Pages Deploy"
status: implemented
depends_on:
  - 02-dashboard-features
  - 03-landing-and-concepts
  - 07-showcase
tags: []
created: 2026-06-10
---

## Objective

Stand up the site build and publish it:

- A GitHub Actions workflow that builds the site — doc-mode export of the docs tree as the main site entry plus the two showcase exports — and deploys to GitHub Pages. Triggers: `workflow_dispatch` plus push to the default branch (the push trigger goes live once the workstream lands). GitHub registers `workflow_dispatch` only for workflow files present on the default branch, so in-branch verification requires seeding the workflow file onto `main` first, then dispatching with `--ref` pointing at this branch.
- A single committed local build script that produces the identical site output for local preview, used by the workflow (the pipeline entry point for this workstream).
- The build fails loudly on export errors or missing inputs; no silent partial deploys.
- The live site URL recorded where users discover it: repo About, `.claude-plugin`/`.codex-plugin` manifest homepage fields, and handed to `09-readme-front-door` for the README links.

**Stop point (resolved 2026-06-11):** the researcher chose the live-verification path and authorized both admin actions — enable GitHub Pages (Actions source; attempt via `gh api repos/{owner}/{repo}/pages -X POST -f build_type=workflow`, fall back to asking the researcher to flip it in Settings) and seed the workflow file onto `main` as a single-file commit, then dispatch with `--ref` this branch. The live-URL validation below applies.

Validation, in-branch: the local build script succeeds, and — per the stop-point outcome — either a `workflow_dispatch --ref <this branch>` run deploys a real Pages site where the landing page, sidebar nav, search, highlighted code blocks, deep links, and both showcase exports work (verified by loading the published URL), or, on the fallback path, the exported site artifact is verified locally and the live-URL check is recorded in `## Results` as a landing-time follow-up. The push-trigger path is verified after the workstream lands on the default branch.

**Known plumbing issue to resolve (found by 03 during authoring):** the standalone export re-bases repo-relative file links against the doc node's directory under the docs root, so a contract-compliant authority link like `skills/superplan/SKILL.md` on a page at `03-concepts/01-the-workflow/` resolves to `<repo-file-base>/site/03-concepts/01-the-workflow/skills/superplan/SKILL.md` — a nonexistent path. The build must make repo-file links resolve repo-root-relative against `--repo-file-base` (an export-flag or doc-mode change coordinated with the `02-dashboard-features/doc-mode` flag surface). Acceptance: every authority link on the built site points at a real blob URL.

## Planner Guidance

`skills/task-tree/scripts/templates/superra-dashboard-artifact.yml` is the existing CI export precedent; the doc-mode flag/invocation comes from `02-dashboard-features/doc-mode`'s recorded `## Results`.

Content tasks 04–06 are not build prerequisites — the site can deploy with the IA-scaffolded stubs present — but confirm with the researcher before publishing a visibly incomplete site versus deploying to Pages only after 04–06 land.

## Results

The site build and GitHub Pages deploy are stood up: a committed local build script ([docs/build_site.sh](../../../docs/build_site.sh)) is the single pipeline entry point, a GitHub Actions workflow ([.github/workflows/docs-site.yml](../../../.github/workflows/docs-site.yml)) runs it and deploys to Pages, and the repo-file link re-basing bug is fixed in the export plumbing. GitHub Pages was already enabled by the researcher (`build_type: workflow`, site `http://fuzhiyu.me/superRA/`), confirmed via `gh api repos/FuZhiyu/superRA/pages` — not re-enabled.

### Build script (the pipeline entry point)

[docs/build_site.sh](../../../docs/build_site.sh) builds the whole site into one output dir (default `_site`) with three self-contained HTML files:

| File | Tree | Mode |
|---|---|---|
| `index.html` | `docs/site` | doc-mode (chrome suppressed) — the site entry |
| `demo-tree.html` | `docs/showcase-demo` | full task-tracker chrome |
| `superra-dev-tree.html` | `superRA` | full task-tracker chrome |

The two `*-tree.html` exports land beside `index.html` so the showcase framing page's relative links (`demo-tree.html`, `superra-dev-tree.html`) resolve. It derives `--repo-file-base` from `origin` + `HEAD` (overridable via `REPO_FILE_BASE` / `GITHUB_SHA` / `GITHUB_REPOSITORY` in CI), verifies all three input trees exist before writing anything, and exits non-zero if any export produces no output — fails loudly, no silent partial site. The same script runs locally and in CI, so local preview is byte-identical to the deploy.

### Doc-mode invocation (coordination with `02-dashboard-features/doc-mode`)

The site export uses the recorded `--doc-mode` flag plus two new additive flags this task introduced (see plumbing below):

```
plan_dashboard.py generate --plan-root docs/site --output _site/index.html \
  --doc-mode --repo-file-base <blob-base> --repo-file-prefix docs/site \
  --doc-local-link demo-tree.html --doc-local-link superra-dev-tree.html
```

The showcase exports run non-doc-mode with `--repo-file-base` + `--repo-file-prefix <tree>` (full chrome by design, per `07-showcase` §Results).

### Repo-file link fix (the known plumbing issue)

Two distinct defects had to be fixed for the acceptance "every authority link on the built site points at a real blob URL," both in [plan_dashboard.py](../../../skills/task-tree/scripts/plan_dashboard.py) export plumbing + [base.html](../../../skills/task-tree/scripts/templates/base.html) link rewriting, all additive and flag-gated (default output byte-unchanged):

1. **Doc-node re-basing (the reported bug).** In doc-mode, a body authority link written repo-root-relative (`skills/superplan/SKILL.md`, per the IA authoring contract) was being prepended with the doc node's dir, yielding `<base>/site/03-concepts/01-the-workflow/skills/superplan/SKILL.md`. Fix: in doc-mode the genuine-file-link branch resolves the href repo-root-relative (`repoFileHref(href)`), so it becomes `<base>/skills/superplan/SKILL.md`. Sibling-export links the build emits beside the site (`--doc-local-link`, embedded as `DOC_LOCAL_LINKS`) are left as plain relative hrefs — those `.html` files are CI artifacts, not repo files, and must resolve against `index.html`'s directory.
2. **Nested-root prefix (found while verifying the fix).** For `--repo-file-base` exports the repo-link prefix was the resolved root's *basename* (`ROOT_PREFIX`, e.g. `showcase-demo` or `site`), not its path relative to the repo root. So the showcase demo tree's links and every `task.md` "view on GitHub" button pointed at `<base>/showcase-demo/...` / `<base>/site/...` — missing the `docs/` lead. Fix: a new `--repo-file-prefix` export flag (embedded as `REPO_ROOT_PREFIX`, defaulting to `ROOT_PREFIX`) supplies the repo-root-relative root path; the build passes each tree's path (`docs/site`, `docs/showcase-demo`, `superRA`). The dev tree (`superRA`, already at repo root) is unaffected. This only touches the `REPO_FILE_BASE` branches; local vscode (`RESOLVED_ROOT`) and server `/files/` (`ROOT_PREFIX`) links are unchanged.

New flags on `generate` and `dashboard export` (forwarded through `cli.py`): `--repo-file-prefix BASENAME`, `--doc-local-link BASENAME` (repeatable). Both default empty → current behavior.

### GitHub Actions workflow

[.github/workflows/docs-site.yml](../../../.github/workflows/docs-site.yml): `workflow_dispatch` + push to `main` (path-filtered to docs sources, the build script, the scripts dir, and the workflow). The push trigger is dormant until the workstream lands on `main`; it goes live then. The job installs uv, runs `docs/build_site.sh _site`, uploads the Pages artifact (`upload-pages-artifact@v3`), and a dependent `deploy` job publishes via `deploy-pages@v4` with the `pages: write` + `id-token: write` permissions Pages deploy requires.

### Validation

- **Full scripts test suite:** 678 passed, 2 skipped (`uv run --with pytest … python -m pytest skills/task-tree/scripts`). +8 new tests lock in the fix: `DOC_LOCAL_LINKS` embedding/default/CLI-forwarding, `REPO_ROOT_PREFIX` embedding/default/CLI-forwarding, and a node-backed behavioral test of the doc-mode link branch (authority link → repo-root blob URL; sibling export → relative; doc-mode off → task-relative, unchanged).
- **Local build:** `docs/build_site.sh` produces all three files; missing-input and empty-output guards exercised by the structure of the script.
- **Real-artifact (headless Chrome, `file://` open):** the doc-mode `index.html` opens on the landing page ("superRA Documentation"), carries `data-doc-mode="true"`, embeds a 25-record search index covering every doc node, and renders highlighted code blocks (`<code class="hljs …">`) on the how-to pages. Authority links on `#/03-concepts/01-the-workflow` resolve to real blob URLs (`…/skills/superplan/SKILL.md`, …); the `task.md` button resolves to `…/docs/site/03-concepts/01-the-workflow/task.md`. On `#/06-showcase` the two `*-tree.html` links stay relative and no `.html` link is wrongly rebased to GitHub. The demo-tree export's body links resolve to `…/docs/showcase-demo/…` (the `docs/` lead restored). No href anywhere carries the bug signature (`blob/<sha>/site/…` without the `docs/` lead).

### Live deploy (in-branch verification)

Per the resolved stop point, the live path was taken: the workflow file was seeded onto `main` as a single-file commit (Contents API, commit `84715d69`) so GitHub registers `workflow_dispatch`, then dispatched against this branch with `--ref better-handoff-doc`. Deploy outcome and published-URL spot-check recorded below.

### Follow-ups for `09-readme-front-door` and landing

- **Live site URL:** `http://fuzhiyu.me/superRA/` (custom domain already configured on the repo with an approved HTTPS cert). Hand this to `09-readme-front-door` for the README links.
- **Discovery surfaces not yet updated** (deferred to landing, since they should change when the workstream merges to `main`, not on a feature branch): repo About description/homepage and the `.claude-plugin` / `.codex-plugin` manifest `homepage` fields. Recorded here as a landing-time checklist item.
- **Push trigger:** verified only after the workstream lands on the default branch (the trigger is dormant until then by design).
