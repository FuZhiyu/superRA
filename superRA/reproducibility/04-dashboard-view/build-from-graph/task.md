---
title: "Build and Diagnose Steps from the Graph"
status: not-started
---

## Objective

From any task or step card in the Reproduction view, the researcher can build it, see what the build will cost, and see why a step is stale, without an agent or the CLI.

- **A Build menu on every card.** Each task card and step card carries a `▶ Build` chip, shown on card hover, keyboard focus, or selection, that opens an `rp-menu` on click. Each item shows the exact command it runs:
  - "Build this task" / "Build this step" — `superra repro build <target>`
  - "Build with upstream" — `superra repro build <target> --upstream`
  - below a divider, "Rebuild all" — `superra repro build <target> --force`
  - The target is the task path, `task#step`, or `.` for the project-root card.
  - The menu head carries the estimate: "N steps would run · ~Xm by last runs", or "Nothing stale".
- **Timings on cards.** A step card shows its last duration beside its state. A task card shows the summed last duration of its steps.
- **Explain as a hover card.** Hovering or focusing a non-fresh step's state, or a task card's freshness summary, shows the `superra repro explain` causes: each changed node, its cause, and the next command. Clicking pins the card open and adds the diffs.
- **Build lifecycle.**
  - While a build runs, its card reads "Building…" and its executing steps read `running`, never `failed`.
  - A Stop control ends the build; the runner records the stopped steps as failed.
  - On completion, one status line shows the runner's summary or its error verbatim.
  - One build per worktree. A second build, from the page or from the CLI, shows the runner's lock refusal verbatim.
  - The build runs in the worktree the page selects (`?wt=`) and keeps running if the dashboard server stops.
  - The build runs with the researcher's login-shell environment, not the dashboard process's.
- **Out of scope:** `accept`, `revoke`, and `-j` stay CLI actions.

### Constraints

- **The build route executes declared commands, so it accepts only a same-origin request:** JSON content type and `Sec-Fetch-Site` as [`/api/open`](../../../../skills/task-tree/scripts/plan_dashboard.py#L1627) checks, plus a `Host` check that defeats DNS rebinding.
- **The client sends a target, never command text.** The server accepts only a task path or step present in the current graph, and passes it as an argv element after `--`, never through a shell string.
- **An off-loopback `--host` bind keeps the Build controls**, under the same checks: the researcher opts into that bind. Standalone export and doc mode render no Build or explain controls.
- **Timing, estimate, and explain stay read-only:** on a never-built tree they create no `.superra-repro/` and write nothing to the project, like the existing repro routes.
- **The state glyph-and-word accessibility and both themes hold** for every new control, per [the parent task's palette results](../task.md#the-state-palette-is-a-status-scale-not-a-series-palette).

### Validation

- Dashboard tests cover the build route's refusals (cross-site, rebinding `Host`, wrong content type, unknown target, flag-like target), the build lifecycle (start, `running` state, lock refusal, stop, completion summary), and the read-only invariant of the estimate and explain routes.
- A browser pass on the parent's 16-step fixture (retired at Protect; recover it with `git show 27b7e181^:superRA/reproducibility/04-dashboard-view/attachments/repro_fixture.py`) exercises: build a step, build with upstream, rebuild all, stop mid-build, a lock refusal from a concurrent CLI build, the hover card (hover, keyboard focus, pinned), and the timings. Record it with screenshots in both themes and at 430px in `attachments/`.

## Details

- **Wording.** The CLI verb is *build* ("Execute every stale step in the target scope"); *run* names one step's execution ("Last run", "Run log"). Menu labels and status lines follow the runner's own strings, such as "Nothing to execute: every selected step is fresh."
- **Code surfaces.**
  - Cards: step node and task card templates at [dashboard.js:1573-1578](../../../../skills/task-tree/scripts/templates/dashboard.js#L1573-L1578); the menu pattern is `.rp-menu` at [dashboard.css:2362](../../../../skills/task-tree/scripts/templates/dashboard.css#L2362) (Status key, Diagnostics).
  - Inspector: [renderReproDetail](../../../../skills/task-tree/scripts/templates/dashboard.js#L1998) already shows reason, last run, duration, and log tail.
  - Server: the `/api/open` gate and [`_local_open_enabled`](../../../../skills/task-tree/scripts/plan_dashboard.py#L1581); [the status payload](../../../../skills/task-tree/scripts/plan_dashboard.py#L1471); the lock watcher in [`_watch_worktree`](../../../../skills/task-tree/scripts/plan_dashboard.py#L565), which already refreshes the view per completed step.
  - Runner: [`run_build`](../../../../skills/task-tree/scripts/repro_run.py#L356), [`format_cost`](../../../../skills/task-tree/scripts/repro_run.py#L423), [`explain`](../../../../skills/task-tree/scripts/_repro_provenance.py#L865).
- **Cost budget.** Measured on a real 112-step project (ElasticityBound-Local, 2,350 commits), warm cache: `status .` takes 1.5s; `explain` takes 1.3s for `.` and 2.1s for one step, mostly the status computation it contains. A stale node adds one `git log` pass, cached per refs, plus reads of the changed historical blobs, each capped at 16 MiB.
  - Timings need no request: durations are already in the status payload.
  - Compute the estimate in the browser from the graph and status payloads: the non-fresh steps in scope and their last durations. Label it approximate, since downstream steps can rerun once an upstream output changes.
  - The hover card shows the status `reason` at once and fills in the explain rows when they arrive: fetch after a short hover delay, one request per hovered target, cached until the next status refresh. Fetch diffs only when the card is pinned.
- **Known difficulties.**
  - **A step node is a `<button>`,** so its chip cannot nest inside it. Restructure the node as a wrapper holding a select button and the Build chip as siblings, keeping node ids, selection, and keyboard order.
  - **An executing step reads `failed` today:** `compute_status` treats a `running` run record as an interrupted run ([_repro_state.py:881](../../../../skills/task-tree/scripts/_repro_state.py#L881)). While the worktree's build is live, the dashboard must report `running` for those steps, and the interrupted-run rule must still apply after a crash.
  - **`build --dry-run` takes the mutation lock** ([_repro_acceptance.py:54](../../../../skills/task-tree/scripts/_repro_acceptance.py#L54)), so an estimate computed that way fails during a build. Compute it from the status selection plus run records, as `format_cost` does.
  - **The runner's state directory is not watched,** so the per-step `running` state needs either a watch on it or polling while a build is live.
  - **Server lifetime.** Start the build in its own session (process group) so it survives a server restart, and send Stop to that group; the runner already records interrupted steps as failed. Read build state from run records and the mutation lock, not server memory.
  - **Environment.** Spawn through the login shell with the target as a positional argument, e.g. `[$SHELL, "-lc", 'exec "$@"', "superra", <runner>, "build", "--", <target>]`, so Julia, conda, and `PATH` match the researcher's terminal.
  - **Rebinding on an off-loopback bind.** A loopback-only `Host` check would block the researcher's own LAN or Tailscale access. Accept loopback names, IP literals, and the machine's own hostnames; an attacker's rebinding page sends its own domain.
- **Review.** The build route turns the page into a command runner. Worth a thorough independent review focused on the route's refusals and argv handling.
- **Status impact.** This child reopens its ancestors through normal rollup. It changes no reproduction schema, so sibling approvals stand. A `compute_status` change for live builds also changes `superra repro status` output; keep the CLI and the page reporting the same state.
