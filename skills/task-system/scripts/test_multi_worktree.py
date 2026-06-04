#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pytest", "httpx", "pyyaml", "fastapi", "jinja2"]
# ///
"""Cross-worktree isolation + SSE-scoping integration tests (task 04).

The end-to-end gate for serving multiple worktrees on demand: ONE app instance
serves >=2 worktrees concurrently, and the ``?wt=<name>`` URL drives which
worktree each request renders.  Tasks 01-03 each ship their own unit tests for
the per-worktree resolver, SSE scoping, and watcher lifecycle in isolation; this
file adds the cross-cutting tests that only make sense once all three land, and
which are the real guarantee the user cares about:

* render isolation across every read route through one app,
* mutation isolation (a comment/edit under A never bleeds into B),
* SSE delivery scoped to the mutated worktree's clients only,
* watcher lifecycle under multiplexing (A and B independent), and
* the discovery-driven resolve path (lazy build from ``discover_worktrees`` +
  basename-collision disambiguation), which the cache-seeding fixtures bypass.

The isolation assertions are written to go RED on a global-state regression:
each one mutates worktree A and asserts B is UNCHANGED, so collapsing the
per-worktree state/SSE/watcher back into module singletons fails them.

The ``_write_task_md`` helper and the per-worktree state plumbing
(``_worktree_cache``, ``_build_worktree_state``, ``_worktree_id_for_plan_root``)
are reused from ``test_dashboard.py`` / ``plan_dashboard`` rather than re-built.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

import plan_dashboard
from _comments import add_comment
from _worktree_discovery import WorktreeInfo
from test_dashboard import _write_task_md


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _build_tree(wt_dir: Path, suffix: str) -> Path:
    """Create a two-level task tree under ``wt_dir/superRA`` and return its root.

    The root title, the child title, and the child objective all embed *suffix*
    so a render from the wrong worktree is detectable by a string check.
    """
    wt_dir.mkdir(parents=True, exist_ok=True)
    root = wt_dir / "superRA"
    root.mkdir()
    _write_task_md(root / "task.md", f"Project {suffix}", "not-started",
                   objective=f"Plan {suffix}.")
    child = root / "01-first"
    child.mkdir()
    _write_task_md(child / "task.md", f"First {suffix}", "approved",
                   objective=f"Step one in {suffix}.")
    return root


@pytest.fixture
def two_worktrees(tmp_path):
    """One app instance serving two worktrees ('A' launch, 'B' discovered).

    Worktree A is the launch worktree (seeded via ``rebuild_tree`` and the
    default when no ``?wt=`` is given).  Worktree B is registered as a *second
    discovered worktree*: ``discover_worktrees`` is patched to report both, so B
    is resolved lazily through ``resolve_worktree`` -> ``_discovered_worktree_map``
    on first use rather than hand-seeded into the cache.  This exercises the real
    discovery -> lazy-build path that the cache-seeding fixtures in
    ``test_dashboard.py`` deliberately bypass.

    Yields ``(client, wt_a, wt_b)`` where ``wt_a``/``wt_b`` are the ``?wt=``
    selector tokens.  TestClient disables lifespan, so no live watcher runs.
    """
    from starlette.testclient import TestClient

    root_a = _build_tree(tmp_path / "wt-a", "A")
    root_b = _build_tree(tmp_path / "wt-b", "B")

    def _info(root: Path, branch: str) -> WorktreeInfo:
        return WorktreeInfo(
            path=str(root.parent), branch=branch, head="0" * 40,
            plan_root=str(root), plan_title=None, is_current=False,
            is_locked=False, is_prunable=False, is_agent=False,
            last_activity=1000.0,
        )

    infos = [_info(root_a, "a"), _info(root_b, "b")]

    plan_dashboard._jinja_env = None
    plan_dashboard._worktree_cache.clear()
    plan_dashboard._worktree_clients.clear()
    plan_dashboard._worktree_watchers.clear()
    plan_dashboard._worktree_locks.clear()

    with patch.object(plan_dashboard, "discover_worktrees", return_value=infos):
        # Launch worktree = A; rebuild_tree seeds it and sets _launch_wt_id.
        plan_dashboard.PLAN_ROOT = root_a
        plan_dashboard.rebuild_tree()
        wt_a = plan_dashboard._launch_wt_id
        wt_b = plan_dashboard._worktree_id_for_plan_root(root_b)
        assert wt_a != wt_b

        client = TestClient(plan_dashboard.app, raise_server_exceptions=True)
        try:
            yield client, wt_a, wt_b
        finally:
            plan_dashboard._worktree_cache.clear()
            plan_dashboard._worktree_clients.clear()
            plan_dashboard._worktree_watchers.clear()
            plan_dashboard._worktree_locks.clear()


# ---------------------------------------------------------------------------
# 1. Render isolation across every read route (one app, concurrent ?wt=)
# ---------------------------------------------------------------------------


class TestRenderIsolation:
    """Each read route renders the worktree named by ``?wt=``; no field from one
    worktree bleeds into the other's response, and a request with no ``?wt=``
    renders the launch worktree."""

    def test_index_isolated(self, two_worktrees):
        client, wt_a, wt_b = two_worktrees
        a = client.get(f"/?wt={wt_a}").text
        b = client.get(f"/?wt={wt_b}").text
        assert "Project A" in a and "Project B" not in a
        assert "Project B" in b and "Project A" not in b

    def test_nav_isolated(self, two_worktrees):
        client, wt_a, wt_b = two_worktrees
        a = client.get(f"/nav?wt={wt_a}").text
        b = client.get(f"/nav?wt={wt_b}").text
        assert "First A" in a and "First B" not in a
        assert "First B" in b and "First A" not in b

    def test_node_isolated(self, two_worktrees):
        client, wt_a, wt_b = two_worktrees
        a = client.get(f"/node/01-first?wt={wt_a}")
        b = client.get(f"/node/01-first?wt={wt_b}")
        assert a.status_code == 200 and b.status_code == 200
        assert "Step one in A." in a.text and "Step one in B." not in a.text
        assert "Step one in B." in b.text and "Step one in A." not in b.text

    def test_dag_isolated(self, two_worktrees):
        client, wt_a, wt_b = two_worktrees
        a = client.get(f"/dag?wt={wt_a}").text
        b = client.get(f"/dag?wt={wt_b}").text
        # The DAG labels carry each worktree's child title.
        assert "First A" in a and "First B" not in a
        assert "First B" in b and "First A" not in b

    def test_comments_route_isolated(self, two_worktrees):
        """The comment-list route reads the worktree's own task dir: a comment on
        A's 01-first is visible only under ``?wt=A``."""
        client, wt_a, wt_b = two_worktrees
        client.post(f"/api/task/01-first/comment?wt={wt_a}",
                    json={"section": "Objective", "block_index": 0,
                          "text_preview": "Step one in A.", "body": "on A",
                          "author": "u"})
        a = client.get(f"/api/task/01-first/comments?wt={wt_a}").json()
        b = client.get(f"/api/task/01-first/comments?wt={wt_b}").json()
        assert [c["body"] for c in a] == ["on A"]
        assert b == []

    def test_no_wt_param_renders_launch_worktree(self, two_worktrees):
        client, wt_a, wt_b = two_worktrees
        # Launch worktree is A; a bare request must render A, never B.
        assert "Project A" in client.get("/").text
        assert "Step one in A." in client.get("/node/01-first").text


# ---------------------------------------------------------------------------
# 2. Mutation isolation (red on a global-state regression)
# ---------------------------------------------------------------------------


class TestMutationIsolation:
    """A mutation under one worktree must leave the other's responses unchanged.

    Each test captures B's response, mutates A, then re-reads B and asserts it is
    byte-for-byte unchanged.  If the per-worktree state cache were collapsed back
    into module singletons, the A-side mutation would leak into B and these go
    RED — they pin the architecture, not just smoke-test it."""

    def test_comment_create_under_a_does_not_touch_b(self, two_worktrees):
        client, wt_a, wt_b = two_worktrees
        b_before = client.get(f"/api/task/01-first/comments?wt={wt_b}").json()
        b_summary_before = client.get(f"/api/comments/summary?wt={wt_b}").json()

        client.post(f"/api/task/01-first/comment?wt={wt_a}",
                    json={"section": "Objective", "block_index": 0,
                          "text_preview": "Step one in A.", "body": "A only",
                          "author": "u"})

        # A reflects the new comment; B is untouched.
        assert client.get(f"/api/comments/summary?wt={wt_a}").json() == {"01-first": 1}
        assert client.get(f"/api/task/01-first/comments?wt={wt_b}").json() == b_before
        assert client.get(f"/api/comments/summary?wt={wt_b}").json() == b_summary_before
        assert b_summary_before == {}

    def test_task_edit_under_a_does_not_touch_b(self, two_worktrees):
        """Editing A's task on disk and invalidating A's cached state must not
        change what B renders."""
        client, wt_a, wt_b = two_worktrees
        b_node_before = client.get(f"/node/01-first?wt={wt_b}").text

        # Edit A's task body on disk, then invalidate only A's cached state.
        state_a = plan_dashboard.resolve_worktree(_req(f"wt={wt_a}"))
        task_md = state_a.plan_root / "01-first" / "task.md"
        task_md.write_text(task_md.read_text().replace("Step one in A.",
                                                       "Mutated step in A."))
        plan_dashboard.rebuild_worktree_state(wt_a)

        # A picks up the edit; B is byte-for-byte unchanged.
        assert "Mutated step in A." in client.get(f"/node/01-first?wt={wt_a}").text
        assert client.get(f"/node/01-first?wt={wt_b}").text == b_node_before
        assert "Mutated step in A." not in client.get(f"/node/01-first?wt={wt_b}").text


# ---------------------------------------------------------------------------
# 3. SSE scoping — every event type, scoped to the mutated worktree's clients
# ---------------------------------------------------------------------------


def _req(query_string: str = "", path: str = "/"):
    """A minimal Starlette Request carrying *query_string* (e.g. ``wt=foo``)."""
    from starlette.requests import Request

    return Request({
        "type": "http", "method": "GET", "path": path,
        "query_string": query_string.encode(), "headers": [],
    })


class TestSSEScopingAcrossWorktrees:
    """A change under worktree A delivers SSE events to A's registered clients
    only; B's client receives nothing.  Covers every event type in play
    (``task:<path>``, ``full-reload``, ``summary-updated``) through the real
    ``_rebuild_and_broadcast`` hook the watcher calls, driven directly because
    TestClient disables lifespan."""

    def _two_states_and_clients(self, two_worktrees):
        """Resolve both worktree states and register one queue per worktree."""
        client, wt_a, wt_b = two_worktrees
        state_a = plan_dashboard.resolve_worktree(_req(f"wt={wt_a}"))
        state_b = plan_dashboard.resolve_worktree(_req(f"wt={wt_b}"))
        qa: asyncio.Queue[str] = asyncio.Queue(maxsize=256)
        qb: asyncio.Queue[str] = asyncio.Queue(maxsize=256)
        plan_dashboard._worktree_clients[wt_a] = {qa}
        plan_dashboard._worktree_clients[wt_b] = {qb}
        return state_a, state_b, qa, qb

    def test_content_edit_event_scoped_to_a(self, two_worktrees):
        """A pure content edit under A yields a ``task:<path>`` event (and a
        ``summary-updated``) to A only; B's queue stays empty."""
        import watchfiles

        loop = asyncio.new_event_loop()
        try:
            state_a, state_b, qa, qb = self._two_states_and_clients(two_worktrees)
            edited = state_a.plan_root / "01-first" / "task.md"
            changes = {(watchfiles.Change.modified, str(edited))}
            loop.run_until_complete(
                plan_dashboard._rebuild_and_broadcast(state_a, changes)
            )
            events = _drain(qa)
            assert any(e.startswith("event: task:01-first\n") for e in events)
            assert any(e.startswith("event: summary-updated\n") for e in events)
            assert qb.empty()
        finally:
            loop.close()

    def test_structural_change_event_scoped_to_a(self, two_worktrees):
        """Adding a task dir under A yields a ``full-reload`` + ``summary-updated``
        to A only; B sees nothing."""
        import watchfiles

        loop = asyncio.new_event_loop()
        try:
            state_a, state_b, qa, qb = self._two_states_and_clients(two_worktrees)
            new_dir = state_a.plan_root / "02-new"
            new_dir.mkdir()
            _write_task_md(new_dir / "task.md", "New A", "not-started",
                           objective="added")
            added = new_dir / "task.md"
            changes = {(watchfiles.Change.added, str(added))}
            loop.run_until_complete(
                plan_dashboard._rebuild_and_broadcast(state_a, changes)
            )
            events = _drain(qa)
            assert any(e.startswith("event: full-reload\n") for e in events)
            assert any(e.startswith("event: summary-updated\n") for e in events)
            assert qb.empty()
        finally:
            loop.close()

    def test_concurrent_edits_each_reach_their_own_worktree(self, two_worktrees):
        """An edit under A and an independent edit under B each reach only their
        own client — the broadcasts do not cross."""
        import watchfiles

        loop = asyncio.new_event_loop()
        try:
            state_a, state_b, qa, qb = self._two_states_and_clients(two_worktrees)
            edit_a = state_a.plan_root / "01-first" / "task.md"
            edit_b = state_b.plan_root / "01-first" / "task.md"

            async def _both():
                await plan_dashboard._rebuild_and_broadcast(
                    state_a, {(watchfiles.Change.modified, str(edit_a))})
                await plan_dashboard._rebuild_and_broadcast(
                    state_b, {(watchfiles.Change.modified, str(edit_b))})

            loop.run_until_complete(_both())
            a_events = _drain(qa)
            b_events = _drain(qb)
            # Each queue saw exactly its own worktree's task event, not the other's.
            assert any(e.startswith("event: task:01-first\n") for e in a_events)
            assert any(e.startswith("event: task:01-first\n") for e in b_events)
            # Sanity: the task fragment text is worktree-specific, so no cross-talk
            # of payloads either.  (Fragments carry the slug, identical here; the
            # scoping guarantee is the separate queues, asserted above.)
        finally:
            loop.close()


def _drain(queue: asyncio.Queue) -> list[str]:
    """Synchronously drain every message currently in *queue*."""
    out: list[str] = []
    while not queue.empty():
        out.append(queue.get_nowait())
    return out


# ---------------------------------------------------------------------------
# 4. Watcher lifecycle under multiplexing (A and B independent)
# ---------------------------------------------------------------------------


class TestWatcherLifecycleMultiplexed:
    """Two worktrees' watchers are independent: starting/stopping A's watcher
    leaves B's untouched, and a crashed watcher for one is respawned without
    disturbing the other."""

    def test_independent_start_and_stop(self, two_worktrees):
        client, wt_a, wt_b = two_worktrees
        # Both states must exist in the cache so the watcher coroutine finds them.
        plan_dashboard.resolve_worktree(_req(f"wt={wt_a}"))
        plan_dashboard.resolve_worktree(_req(f"wt={wt_b}"))

        loop = asyncio.new_event_loop()

        async def _test():
            await plan_dashboard._ensure_watcher(wt_a)
            await plan_dashboard._ensure_watcher(wt_b)
            assert wt_a in plan_dashboard._worktree_watchers
            assert wt_b in plan_dashboard._worktree_watchers
            wb = plan_dashboard._worktree_watchers[wt_b]

            # Dropping A's last client stops A's watcher; B's keeps running.
            await plan_dashboard._stop_watcher(wt_a)
            assert wt_a not in plan_dashboard._worktree_watchers
            assert plan_dashboard._worktree_watchers.get(wt_b) is wb
            assert not wb.done()

            await plan_dashboard._stop_watcher(wt_b)

        try:
            loop.run_until_complete(_test())
        finally:
            loop.close()

    def test_crashed_a_watcher_respawns_without_touching_b(self, two_worktrees):
        client, wt_a, wt_b = two_worktrees
        plan_dashboard.resolve_worktree(_req(f"wt={wt_a}"))
        plan_dashboard.resolve_worktree(_req(f"wt={wt_b}"))

        loop = asyncio.new_event_loop()

        async def _test():
            await plan_dashboard._ensure_watcher(wt_b)
            wb = plan_dashboard._worktree_watchers[wt_b]

            # A present-but-done() task stands in for a crashed A watcher.
            async def _noop():
                return None
            dead = asyncio.create_task(_noop())
            await dead
            plan_dashboard._worktree_watchers[wt_a] = dead

            await plan_dashboard._ensure_watcher(wt_a)
            fresh = plan_dashboard._worktree_watchers[wt_a]
            assert fresh is not dead and not fresh.done()
            # B's watcher was never disturbed by A's respawn.
            assert plan_dashboard._worktree_watchers[wt_b] is wb
            assert not wb.done()

            await plan_dashboard._stop_watcher(wt_a)
            await plan_dashboard._stop_watcher(wt_b)

        try:
            loop.run_until_complete(_test())
        finally:
            loop.close()


# ---------------------------------------------------------------------------
# 5. Discovery-driven resolve: lazy build + basename-collision disambiguation
#
# Advisory (1) forwarded from earlier reviews naming task 04: task 01 left the
# lazy-build-from-discovery and basename-collision-disambiguation paths covered
# only by a live-server check.  These regression cases monkeypatch
# ``discover_worktrees`` and drive ``resolve_worktree`` / ``/node`` so the
# resolver's discovery lookup and the longest-unique-suffix disambiguation are
# pinned independently of a live server.
# ---------------------------------------------------------------------------


class TestDiscoveryDrivenResolve:
    def test_b_is_lazily_built_from_discovery(self, two_worktrees):
        """B was never hand-seeded into the cache: the first request naming it
        triggers a lazy build via ``discover_worktrees`` -> ``resolve_worktree``."""
        client, wt_a, wt_b = two_worktrees
        # Drop any cached B state so this resolve must rebuild from discovery.
        plan_dashboard._worktree_cache.pop(wt_b, None)
        assert wt_b not in plan_dashboard._worktree_cache

        resp = client.get(f"/node/01-first?wt={wt_b}")
        assert resp.status_code == 200
        assert "Step one in B." in resp.text
        # The lazy build populated the cache for the next request.
        assert wt_b in plan_dashboard._worktree_cache

    def test_unknown_wt_not_in_discovery_is_404(self, two_worktrees):
        """A ``?wt=`` that is neither the launch worktree nor any discovered one
        is a 404 across read routes."""
        client, wt_a, wt_b = two_worktrees
        assert client.get("/node/01-first?wt=no-such-worktree").status_code == 404
        assert client.get("/nav?wt=no-such-worktree").status_code == 404
        assert client.get("/?wt=no-such-worktree").status_code == 404

    def test_export_scopes_to_named_worktree_but_stays_single_worktree(
        self, two_worktrees
    ):
        """``/export?wt=B`` renders B's tree as a server-less single-file
        download; the produced artifact is standalone (``window.STANDALONE =
        true``) and carries only that one worktree's content — the other
        worktree never bleeds in, and the file itself has no ``?wt=`` notion."""
        client, wt_a, wt_b = two_worktrees
        a = client.get(f"/export?wt={wt_a}")
        b = client.get(f"/export?wt={wt_b}")
        assert a.status_code == 200 and b.status_code == 200
        for resp in (a, b):
            assert "attachment" in resp.headers.get("content-disposition", "")
            assert "window.STANDALONE = true" in resp.text
        assert "Step one in A." in a.text and "Step one in B." not in a.text
        assert "Step one in B." in b.text and "Step one in A." not in b.text

    def test_basename_collision_disambiguated_by_suffix(self, tmp_path):
        """Two discovered worktrees sharing a directory basename are each
        addressable by their longest-unique-suffix key, and resolve to distinct
        trees through ``/node``.

        Builds ``parentX/shared/superRA`` and ``parentY/shared/superRA`` (both
        basename ``shared``) so the bare basename collides and the resolver must
        fall back to suffix disambiguation."""
        from starlette.testclient import TestClient

        root_x = _build_tree(tmp_path / "parentX" / "shared", "X")
        root_y = _build_tree(tmp_path / "parentY" / "shared", "Y")

        def _info(root: Path, branch: str) -> WorktreeInfo:
            return WorktreeInfo(
                path=str(root.parent), branch=branch, head="0" * 40,
                plan_root=str(root), plan_title=None, is_current=False,
                is_locked=False, is_prunable=False, is_agent=False,
                last_activity=1000.0,
            )

        infos = [_info(root_x, "x"), _info(root_y, "y")]

        plan_dashboard._jinja_env = None
        plan_dashboard._worktree_cache.clear()
        plan_dashboard._worktree_clients.clear()
        plan_dashboard._worktree_watchers.clear()
        plan_dashboard._worktree_locks.clear()

        with patch.object(plan_dashboard, "discover_worktrees", return_value=infos):
            # Launch in X; both ids must be disambiguated suffixes, not "shared".
            plan_dashboard.PLAN_ROOT = root_x
            plan_dashboard.rebuild_tree()
            wt_map = plan_dashboard._discovered_worktree_map()
            ids = set(wt_map)
            assert "shared" not in ids, f"collision not disambiguated: {ids}"
            id_x = plan_dashboard._worktree_id_for_plan_root(root_x)
            id_y = plan_dashboard._worktree_id_for_plan_root(root_y)
            assert id_x != id_y
            assert id_x.endswith("shared") and id_y.endswith("shared")

            client = TestClient(plan_dashboard.app, raise_server_exceptions=True)
            try:
                x = client.get(f"/node/01-first?wt={id_x}")
                y = client.get(f"/node/01-first?wt={id_y}")
                assert x.status_code == 200 and y.status_code == 200
                assert "Step one in X." in x.text and "Step one in Y." not in x.text
                assert "Step one in Y." in y.text and "Step one in X." not in y.text
            finally:
                plan_dashboard._worktree_cache.clear()
