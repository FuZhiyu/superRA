---
title: "Open Task Files on the Researcher's Machine"
status: revise
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

Every file the dashboard shows now opens on the machine the server runs on, through a `POST /api/open` route the page calls in place of firing a `vscode://` URI. Three surfaces use it: the active-task card head, the header `VS Code` button, and body file links.

### The route

[`POST /api/open`](../../../../skills/task-tree/scripts/plan_dashboard.py#L1355-L1409) takes `{path, target}` where `path` is project-root-relative and `target` is `native` (the OS default application for the file type) or `editor`.

- **Gate.** [`_local_open_enabled()`](../../../../skills/task-tree/scripts/plan_dashboard.py#L1310-L1319) requires a loopback bind and non-doc-mode. [`serve()`](../../../../skills/task-tree/scripts/plan_dashboard.py#L2187-L2217) records the host it binds in [`BOUND_HOST`](../../../../skills/task-tree/scripts/plan_dashboard.py#L88) (default `127.0.0.1`, restored when the server exits, so nothing is left stale); [`_is_loopback_host`](../../../../skills/task-tree/scripts/plan_dashboard.py#L1299-L1307) decides via `ipaddress`, so `127.0.0.53` and `::1` count and `0.0.0.0` does not.
- **CSRF.** `application/json` is required (forcing a preflight no CORS middleware answers) and `Sec-Fetch-Site` must be absent, `same-origin`, or `none` (closing the simple-form-POST path that skips the preflight).
- **Containment.** The path is joined under `state.project_root`, `resolve()`d, and checked with `is_relative_to` — the same shape [`/files/`](../../../../skills/task-tree/scripts/plan_dashboard.py#L1274-L1288) uses. Traversal and filesystem-absolute paths both land outside and are refused; a missing file is 404.
- **No shell.** [`_spawn`](../../../../skills/task-tree/scripts/plan_dashboard.py#L1326-L1334) is the one launch point: argv list, `shell=False`, stdio to `DEVNULL`. Native open is `open` / `xdg-open` (`os.startfile` on Windows); editor open is `code <worktree-folder> <file>`, the folder first so the file lands in the window already holding that worktree. `SUPERRA_EDITOR` ([`EDITOR_ENV_VAR`](../../../../skills/task-tree/scripts/plan_dashboard.py#L92)) overrides the executable for a fork such as `cursor`. With no editor CLI on `PATH` the route answers `{"status": "fallback", "uri": "vscode://file/…"}` and the page follows it — the pre-route behavior. Both spawns and the `which` lookup run via `asyncio.to_thread`.

### The page

The index route injects [`local_open`](../../../../skills/task-tree/scripts/plan_dashboard.py#L1076) and base.html emits [`window.LOCAL_OPEN`](../../../../skills/task-tree/scripts/templates/base.html#L233) beside `window.DOC_MODE`. The standalone export and doc-mode never pass it, so it renders `false` there and every control keeps its `vscode://` link. GitHub-file mode (`REPO_FILE_BASE`) is untouched.

- [`taskFileOpenPath`](../../../../skills/task-tree/scripts/templates/dashboard.js#L969-L971) composes the route address as `ROOT_PREFIX + '/' + taskPath + '/…'` — the same composition `/files/` is handed, so both agree for any `--root`, a nested tree, and a rootless forest.
- Card head ([`loadActiveNode`](../../../../skills/task-tree/scripts/templates/dashboard.js#L1058-L1062)): label `Open`, a neutral open-file glyph, and `target: native`. Without the route it is the old `VS Code` button verbatim.
- Header ([`updateWorktreeOpenHref`](../../../../skills/task-tree/scripts/templates/dashboard.js#L2550-L2565)): labelled `VS Code` (`Workspace` is the `#btn-workspace` view toggle), opens the **active task's** file with `target: editor`, and is re-pointed from [`setActive`](../../../../skills/task-tree/scripts/templates/dashboard.js#L855-L856) so it follows navigation. Without the route it keeps its deep link to the worktree root.
- Body links ([`renderMarkdown`](../../../../skills/task-tree/scripts/templates/dashboard.js#L264-L271)) keep their `vscode://` href — which still carries the `#L123` line anchor — and gain `data-open-path`.
- One [delegated click handler](../../../../skills/task-tree/scripts/templates/dashboard.js#L1015-L1022) serves all three: a plain left-click calls [`openLocalPath`](../../../../skills/task-tree/scripts/templates/dashboard.js#L995-L1008); any modifier or non-primary button falls through to the href, so the browser's own open-elsewhere gestures survive.
- A refusal or failure is reported by [`showOpenError`](../../../../skills/task-tree/scripts/templates/dashboard.js#L976-L989) in a transient [`.open-toast`](../../../../skills/task-tree/scripts/templates/dashboard.css#L1127-L1146) — a successful open's only visible result is on the desktop, so without this a refused click reads as a dead button.

### Chrome

`.vscode-btn` is renamed [`.open-btn`](../../../../skills/task-tree/scripts/templates/dashboard.css#L1097-L1122) (it now also styles a native-open control), and its off-palette `#007acc` hover is replaced by the `--accent-soft` / `--accent` pair the neighbouring `.share-btn` already uses, so the card-head and header buttons read as one family at the shared `--control-h`. The rename carries through the doc-mode hide rule, the `pointer: coarse` tap-highlight list, and the `#worktree-open-btn { margin-left: 0 }` override.

`SUPERRA_EDITOR` and the open behavior are documented in [internals.md §Dashboard](../../../../skills/task-tree/references/internals.md#L232), beside the existing binding note.

### Deviation from guidance

The guidance suggested carrying a line number to `code --goto <file>:<line>`. No surface needs it: the card head and header open a `task.md` (no line), and body links open natively, where the OS opener cannot take a line. The line survives where it already worked — a modifier-click follows the `vscode://` href with its `#L123` anchor translated. So `{path, target}` is the whole route contract.

### Verification

Full suites, run fresh from this worktree: `726 passed` across `skills/task-tree/scripts` (299 of them in `test_dashboard.py`).

New coverage in `TestLocalOpen` ([test_dashboard.py](../../../../skills/task-tree/scripts/test_dashboard.py#L3150-L3417)) pins the flag in all four render modes, the loopback predicate, the host record, both open paths' exact argv, the no-CLI fallback, the env override, `shell=False`, every refusal (off-loopback, doc-mode, wrong content type, cross-site, traversal, absolute path, missing file, unknown target), and the client wiring. `TestWorktreeOpenButton` is updated for the rename, the `VS Code` label, the active-task target, and the re-point on navigation.

Live server on port 8995, restarted so the one-hour-cached CSS/JS were re-served (verified: served CSS carries `.open-btn` and no `#007acc`; served page carries `window.LOCAL_OPEN = true`):

| Exercise | Result |
|---|---|
| Card head — `superRA/task-tree/dashboard/local-file-open/task.md`, native | `{"status":"opened","target":"native"}`, opened in the default markdown app |
| Body link — a real task-relative memo href (`…/03-defaults-and-docs/../../../skills/worktree-data-sync/SKILL.md`), native | `200`, opened; the un-normalized `..` segments resolve inside the project root |
| Header button — `target: editor`, launch worktree | `code` invoked as `<repo root> <repo root>/superRA/task-tree/dashboard/local-file-open/task.md` |
| Header button — `target: editor`, `?wt=nonloopback-host-serve` | `code` invoked as `<that worktree> <that worktree>/superRA/task.md` — each worktree's file paired with its own folder |
| Cross-site / form content type / traversal / absolute / missing / bad target | `403` / `415` / `403` / `403` / `404` / `400` |
| Second server bound `--host 0.0.0.0` | page renders `window.LOCAL_OPEN = false`; route answers `403 Local open is disabled on this server` |

The editor invocations were captured by pointing `SUPERRA_EDITOR` at a recording script on a scratch server, which also exercised the env override end-to-end. `node --check` parses `dashboard.js` clean.

### Known gap (accepted at planning)

An SSH port-forward is indistinguishable from a local request, so an open over a tunnel runs on the server's machine. No detection heuristic, per-browser setting, or Remote-SSH URI form was added.

## Review Notes

1. **MAJOR — the same-origin defense does not survive DNS rebinding, so any web page the researcher visits can drive the process-spawning route.** [plan_dashboard.py:1373-1378](../../../../skills/task-tree/scripts/plan_dashboard.py#L1373-L1378) checks content type and `Sec-Fetch-Site` but never the `Host` header, and no `TrustedHostMiddleware` is installed anywhere in the app. An attacker page served from `evil.example.com` that rebinds that name to `127.0.0.1` is, to the browser, *same-origin* with the dashboard: it sends `Sec-Fetch-Site: same-origin`, needs no preflight, and may set `Content-Type: application/json` freely. Both checks pass. Verified live against a server started from this branch on port 8907: `curl -H 'Host: evil.example.com:8907' -H 'Origin: http://evil.example.com:8907' -H 'Sec-Fetch-Site: same-origin' -H 'Content-Type: application/json' -d '{"path":"…/task.md","target":"editor"}'` returned `{"status":"opened","target":"editor"}` and the recorded editor argv confirmed the spawn. The port is deterministic in 8100–8999 and script-scannable, and the server is background-by-default and long-lived, so the precondition is cheap to meet. This is an escalation over the pre-existing read (`/files/`) and comment-write surfaces because it starts processes: on macOS `open` on a repo-contained `.app` bundle, `.command`, `.jar`, or `.scpt` executes it. `## Objective` states the route "accepts only same-origin `application/json` requests" — under rebinding that property does not hold. Either add a `Host`-header check (accept only a loopback/`localhost` authority, mirroring `_is_loopback_host`) with a test alongside the other refusals, or, if the researcher decides to accept this the way the SSH-tunnel gap was accepted, record it explicitly in `## Results` §Known gap so it is a decision rather than an omission.

2. **MAJOR — body links to files whose names need percent-encoding open with an error toast instead of opening.** [dashboard.js:270](../../../../skills/task-tree/scripts/templates/dashboard.js#L270) sets `data-open-path` from the raw `href` attribute, which markdown-it has already normalized: verified against the vendored [markdown-it.min.js](../../../../skills/task-tree/scripts/vendor/markdown-it.min.js) that `[memo](<my file.md>)` renders `href="my%20file.md"` and `[memo](résumé.pdf)` renders `href="r%C3%A9sum%C3%A9.pdf"`. The `vscode://` href works because VS Code decodes the URI, and `/files/` works because the value rides a URL path that Starlette decodes — but `/api/open` receives the value in a **JSON body**, where nothing decodes it. Verified live: with `zz probe file.md` present at the project root, `{"path":"zz%20probe%20file.md"}` → `404 File not found` while `{"path":"zz probe file.md"}` → `200 opened`, and `GET /files/zz%20probe%20file.md` → `200`. This breaks the objective's "body file links … open in the default application on a plain left-click" for any filename with a space or a non-ASCII character — a common case for figures and memos. It also makes the `## Results` claim that `taskFileOpenPath` uses "the same composition the `/files/` route is handed, so both agree" inaccurate: the *composition* agrees, the *decoding contract* does not. Fix by decoding client-side before setting `data-open-path` (guarding `decodeURIComponent` against a malformed sequence) or by unquoting server-side, and pin it with a test.

3. **MAJOR — the header button's central claim was never exercised against a real editor.** `## Objective` requires "the header button's workspace behavior with two worktrees of this repo open," and the design claim is that `code <folder> <file>` "lands in the window holding that worktree, not whichever window was last focused." `## Results` §Verification records only that `SUPERRA_EDITOR` was pointed at a recording script and the argv captured — that verifies path *pairing*, not window targeting. `code` is on this machine (`/opt/homebrew/bin/code`), so the real check is available: open two worktrees of this repo in two VS Code windows, focus the wrong one, then click the header button from each worktree's dashboard view and confirm the file lands in the matching window. Note the realistic miss this would catch: if the window holds a *subfolder* or a multi-root workspace rather than the passed project root, `code <projectRoot> <file>` opens a new window instead of reusing.

4. **MINOR — the route opens directories, unlike `/files/`.** [plan_dashboard.py:1399](../../../../skills/task-tree/scripts/plan_dashboard.py#L1399) gates on `resolved.exists()` where [serve_file](../../../../skills/task-tree/scripts/plan_dashboard.py#L1285) uses `is_file()`. Verified live: `{"path":"superRA/task-tree","target":"editor"}` → `200 opened`. No surface sends a directory, and no test pins the behavior either way. On macOS this is also the sharp edge of item 1, since an `.app` bundle *is* a directory. Either restrict to `is_file()` or state the intent in the route docstring and pin it.

5. **MINOR — user-facing docs still describe the pre-route behavior.** [docs/site/02-quickstart/task.md:23](../../../../docs/site/02-quickstart/task.md#L23) reads "If you use VS Code, the dashboard doubles as a launcher: clicking a task opens its `task.md`, and a header button opens the active worktree in a VS Code window." Both halves are now wrong for a loopback live server: the card-head button opens `task.md` in the OS default application (no VS Code needed), and the header button opens the *active task's file*, not the worktree. `internals.md` was updated; this adopter-facing page was not.

6. **MINOR — stale comment and icon-weight question in the chrome.** The comment above `VSCODE_ICON` at [dashboard.js:929-930](../../../../skills/task-tree/scripts/templates/dashboard.js#L929-L930) still says the icon is "mid-grey at rest, VS Code blue on hover"; the hover is now `--accent`. Separately, `## Objective` asks the two chrome buttons to share "height, icon weight, and hover" — they share height and hover, but the card head carries a 2px-stroke outline glyph while the header carries a solid-filled brand mark. Confirm that reads as one family in the rendered header, or note why the brand mark is the exception.

7. **MINOR — a non-string `path` is coerced instead of rejected.** [plan_dashboard.py:1387](../../../../skills/task-tree/scripts/plan_dashboard.py#L1387) does `str(body.get("path") or "")`, so `{"path": ["a"]}` becomes the literal `"['a']"` and returns 404 rather than a 400 for a malformed body. Cosmetic, but the neighbouring `target` validation is strict.
