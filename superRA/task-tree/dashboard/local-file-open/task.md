---
title: "Open Task Files on the Researcher's Machine"
status: not-started
depends_on:  []
---

## Objective

Make every file the dashboard shows openable on the researcher's own machine in whatever application that machine already uses for the file type, instead of only through a `vscode://` deep link that names one editor and no workspace.

- A `POST /api/open` route opens a project-root-relative path on the server's host: `target: "native"` hands it to the OS default application, `target: "editor"` opens it inside this worktree's VS Code window (pass the worktree folder alongside the file so it lands in the window holding that worktree, not whichever window was last focused). The editor executable is overridable by environment variable for VS Code forks.
- The route acts only when the dashboard is loopback-bound and not in doc-mode. The page learns this from a render-time flag and keeps the existing `vscode://` links whenever it is false — standalone export, doc-mode, and an off-loopback `--host`, where the viewer may not be at the server's machine. GitHub-file mode (`REPO_FILE_BASE`) is unchanged. The loopback bind is the entire remote-access story for this task: no SSH-tunnel detection, no per-browser target setting, and no Remote-SSH URI form.
- The route accepts only same-origin `application/json` requests, resolves paths inside the project root only, and starts no shell.
- The active-task card-head button opens that task's `task.md` in the default application.
- The header worktree button opens the **active task's** file inside this worktree's VS Code window and re-points as the researcher navigates. Label it `VS Code`: `Workspace` is already the `#btn-workspace` view toggle in the same header.
- Body file links — memos under `attachments/`, figures, scripts — open in the default application on a plain left-click. Modifier and middle clicks keep the `vscode://` href so the browser's own "open elsewhere" gesture survives.
- A failed or refused open surfaces in the page rather than leaving a button that appears dead.
- The chrome buttons in the card head and header share one visual treatment — height, icon weight, and hover — so no button reads as foreign. The current VS Code-blue hover sits outside the palette.
- Verification: the dashboard and full task-tree script suites pass, and a live server is exercised by hand for each of the three surfaces (card head, header button, a body link to a markdown memo), including the header button's workspace behavior with two worktrees of this repo open.

## Planner Guidance

Researcher decisions from the planning session, all binding: the plain "Open" affordance targets the OS default application rather than an editor, on the reasoning that a researcher who wants VS Code for a file type can set it as that type's handler; the header worktree button absorbs the editor role and gains the current file, which makes a separate per-task VS Code button redundant; and the header button is named `VS Code` because of the `#btn-workspace` collision.

Why the route is server-side at all: a page can only fire `vscode://`, which hardcodes one editor and cannot express "in this workspace." The dashboard's server is by construction on the researcher's machine, so it is the only component that can hand a file to the OS. That is also why the loopback gate matters — off-loopback the browser may be elsewhere and the route would open windows on a host nobody is sitting at.

Files and what each carries:

- `skills/task-tree/scripts/plan_dashboard.py` — the route, the bound-host record (`serve()` is the single in-process serve path, so the host it is handed is the one to record), and the render-time flag threaded into the index route's `template.render(...)` call beside `doc_mode`. The `/files/` route just above the comment routes is the closest existing model for path containment: build under `state.project_root`, `resolve()`, then check `is_relative_to`.
- `skills/task-tree/scripts/templates/base.html` — the injected flag beside `window.DOC_MODE`, and the header button element.
- `skills/task-tree/scripts/templates/dashboard.js` — `loadActiveNode` builds the card head and sets the file button's href; `updateWorktreeOpenHref` owns the header button; `renderMarkdown`'s relative-link branch is where a body link becomes `vscode://file/...`.
- `skills/task-tree/scripts/templates/dashboard.css` — `.vscode-btn` is shared by *both* buttons, so the restyle is one rule; a rename also touches the doc-mode hide rule, the `pointer: coarse` tap-highlight list, and the `#worktree-open-btn { margin-left: 0 }` override. `--control-h` is the height every inline chrome control pins to.

Path bases, which are easy to get wrong: `PROJECT_ROOT` is the resolved task root's **parent**, `ROOT_PREFIX` its basename, and `RESOLVED_ROOT` its absolute path. The existing `/files/` image rewrite already composes the project-root-relative address as `ROOT_PREFIX + '/' + taskPath + '/' + src`. Reuse that same composition for `/api/open` so the two routes agree for any `--root`, including a nested tree and a rootless forest — the per-task and in-body link builders were deliberately delinked from a hardcoded `superRA/` and must stay that way.

CSRF matters here because the route starts processes. Requiring `application/json` forces a preflight on any cross-origin `fetch`, and no CORS middleware is installed so that preflight fails; checking `Sec-Fetch-Site` closes the simple-form-POST path that would otherwise skip the preflight. Both checks are cheap and neither depends on a token.

For the editor invocation, `code <folder> <file>` reuses an existing window already holding that folder, and `--goto <file>:<line>` carries a line — which is what the body-link `#L123` anchors already parse out. When no editor CLI is on `PATH`, hand the `vscode://` URI back to the page rather than failing; that is exactly today's behavior.

Existing tests pin the current shape and must be updated rather than deleted: `TestWorktreeOpenButton` asserts the header button's class, hidden-until-JS state, and `vscodeFileUri(PROJECT_ROOT)` href; `TestFileLinkConsistency` asserts the `vscode://` builders and the `/files/` composition; `TestDocMode` and `TestStandaloneSelfContained` assert the button is hidden or absent. New coverage should include the route's refusals (off-loopback, doc-mode, wrong content type, cross-site, path escape) and the flag's effect on the rendered page.

The loopback gate is sufficient but not complete, and the researcher accepted the gap knowingly. It covers the researcher's actual remote path — a Tailscale or LAN `--host` bind, which the gate blocks. It does not cover an SSH port-forward: the tunnelled request arrives from `127.0.0.1` and is indistinguishable from a local one, so an open would run on the server's machine. Process-environment sniffing (`SSH_CONNECTION`) does not fix this either, because the dashboard is one reused background server per repo — a server started locally and later reached over SSH keeps its original environment. Leave the gap; do not add detection heuristics, a per-browser target setting, or `vscode://vscode-remote/ssh-remote+<host>/…` URIs.

The sibling `nonloopback-host-serve` task edits the same background-supervisor and host-handling region of `plan_dashboard.py`. Do not run the two in one worktree at the same time, and note that the loopback gate here is a deliberate restriction that task must not quietly lift.

## Results
