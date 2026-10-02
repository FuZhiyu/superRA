"""Where a changed node's recorded and current bytes came from, for `repro explain`.

Three causes, keyed on the node's role in the step: an input (dependency or
step definition) changed, an output holds another recorded build, or an output
matches nothing recorded. Everything finer is a source fact on the row, found
in the local receipt, the acceptance ledger, the committed lock history and the
git blob history of tracked files on HEAD and local and remote-tracking branches
(one `git log` pass per call, cached per refs in `.superra-repro/history.json`;
each lock revision parsed once into `.superra-repro/lock-index/`), and Dropbox
conflicted copies. Only changed nodes are resolved; git is optional. Stdlib only.
"""
from __future__ import annotations

import glob
import hashlib
import json
import re
import shlex
import subprocess
from pathlib import Path

from _repro_state import (
    LEGACY_BUILDS_FILENAME, LEGACY_LOCK_FILENAME, LOCK_FILENAME, STATE_DIRNAME, ReproStateError,
    absolute, convert_legacy, dependency_state, directory_dep_nodes, is_online_only, node_state, output_nodes,
    parse_lock, spec_hash, stamp_ref, step_nodes, tomllib, unread, unread_phrase, _stamp,
)

LOCK_REV_CAP = 200
BLOB_DEPTH = 50
BLOB_MAX_BYTES = 16 << 20   # larger historical versions are not read
BLOB_TOTAL_BYTES = 64 << 20
DIFF_LINES = 20
BRANCHES_SHOWN = 3
ENTRIES_SHOWN = 3
STEPS_SHOWN = 8
FILES_SHOWN = 3
CHECK_ELSEWHERE = 'passed at these inputs in'

CAUSES = {
    'input-changed': 'an input or the step definition differs from the last build',
    'other-build': 'the output holds bytes from another recorded build',
    'unknown-output': 'the output matches no recorded build',
}


def target_ref(step) -> str:
    return f"{step.task_path or '.'}#{step.name}"


def short(value) -> str:
    if value is None:
        return '—'
    text = str(value)
    for prefix in ('saved-input:', 'dir:'):
        text = text.removeprefix(prefix)
    return text.split(':', 1)[0][:8]


# ---------------------------------------------------------------------------
# Git
# ---------------------------------------------------------------------------

_LOG_FORMAT = '--format=%H%x1f%h%x1f%an%x1f%ad'
_LOG_DATE = '--date=format:%Y-%m-%d %H:%M %z'
_BATCH_HEADER = re.compile(rb'^([0-9a-f]{40,64}) \w+ (\d+)$')


class Git:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.ok = bool(self.text('rev-parse', '--show-toplevel'))

    def raw(self, *args, stdin: bytes | None = None) -> bytes | None:
        try:
            done = subprocess.run(['git', '-C', str(self.root), *args], input=stdin,
                                  capture_output=True, check=False)
        except OSError:
            return None
        return done.stdout if done.returncode == 0 else None

    def text(self, *args) -> str | None:
        out = self.raw(*args)
        return None if out is None else out.decode('utf-8', 'replace').strip()

    def walk(self, ranges, specs):
        """(revision, changed paths among *specs*) newest first; a merge lists what it resolved."""
        out = self.raw('log', '-z', '-c', '--name-only', '--relative', '--full-history', '--topo-order',
                       '--format=%x1e' + _LOG_FORMAT.removeprefix('--format='), _LOG_DATE, *ranges, '--', *specs)
        for record in (out or b'').decode('utf-8', 'replace').split('\x1e')[1:]:
            header, _, names = record.partition('\0')
            parts = header.split('\x1f')
            if len(parts) == 4:
                yield dict(zip(('sha', 'rev', 'author', 'date'), parts)), set(filter(None, names.strip('\n').split('\0')))

    def _batch(self, flag, specs):
        out = self.raw('cat-file', flag, stdin=('\n'.join(specs) + '\n').encode()) or b''
        pos, result = 0, {}
        for spec in specs:
            end = out.find(b'\n', pos)
            if end < 0:
                break
            match = _BATCH_HEADER.match(out[pos:end])
            pos = end + 1
            if not match:
                continue
            size = int(match.group(2))
            if flag == '--batch':
                result[spec] = out[pos:pos + size]
                pos += size + 1
            else:
                result[spec] = (match.group(1).decode(), size)
        return result

    def blob_ids(self, specs: list[str]) -> dict[str, tuple[str, int]]:
        """`rev:./path` -> (blob id, size), without reading content."""
        return self._batch('--batch-check', specs) if specs else {}

    def blobs(self, specs: list[str]) -> dict[str, bytes]:
        """`rev:./path` or blob id -> bytes, in one `cat-file --batch`."""
        return self._batch('--batch', specs) if specs else {}


def lock_commit(paths, memo) -> str | None:
    """Short sha of the last commit touching the lock, if the working lock is that commit's.

    Cached by lock content in `.superra-repro/lock-commit.json`, so `status` spawns git
    only for lock bytes it has not seen committed.
    """
    if 'lock_commit' not in memo:
        lock_file = paths.legacy_lock_file if paths.reads_legacy_lock else paths.lock_file
        try:
            digest = hashlib.sha256(lock_file.read_bytes()).hexdigest()
        except OSError:
            digest = None
        cache_file = paths.state_dir / 'lock-commit.json'
        try:
            known = json.loads(cache_file.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            known = {}
        commit = known.get(digest) if digest else None
        if commit is None and digest:
            git = Git(paths.project_root)
            spec = './' + lock_file.name
            clean = git.ok and git.raw('diff', '--quiet', 'HEAD', '--', spec) is not None
            commit = (git.text('log', '-1', '--format=%h', '--', spec) or None) if clean else None
            if commit and paths.state_dir.is_dir():  # committed bytes keep their commit
                from _repro_acceptance import atomic_json
                try:
                    atomic_json(cache_file, {**known, digest: commit})
                except OSError:
                    pass
        memo['lock_commit'] = commit
    return memo['lock_commit']


def check_elsewhere_reason(paths, memo, name, entry) -> str:
    """Status reason for a check whose lock entry matches its inputs but has no local stamp."""
    commit = lock_commit(paths, memo)
    platform = entry.built_on.get('platform')
    built = f" on {platform}" if platform else ''
    return f"{CHECK_ELSEWHERE} {'lock ' + commit if commit else 'the working lock'}{built}; not run here"


# ---------------------------------------------------------------------------
# Lock history
# ---------------------------------------------------------------------------

LOCK_INDEX_VERSION = 3


def _parse_revision(lock_text, legacy_text, builds_text) -> dict | None:
    """One revision's lock as {name: {deps, products, built_on}}; None when this Python cannot read it."""
    try:
        if lock_text is not None:
            document = parse_lock(lock_text)
        elif legacy_text is not None:
            if tomllib is None:
                return None
            document = convert_legacy(legacy_text, builds_text)
        else:
            document = {'steps': {}}
    except (ValueError, ReproStateError):
        document = {'steps': {}}
    steps = {}
    for name, raw in document['steps'].items():
        deps = dict(raw.get('deps') or {})
        if raw.get('spec') is not None:
            deps[f'{name}::spec'] = raw['spec']
        steps[name] = {'deps': deps, 'products': dict(raw.get('outs') or {}),
                       'built_on': dict(raw.get('built_on') or {})}
    return steps


HISTORY_VERSION = 1
LOCK_FILES = (LOCK_FILENAME, LEGACY_LOCK_FILENAME)
_HEAD_WALK, _OTHER_WALK = ['HEAD'], ['--branches', '--remotes', '--not', 'HEAD']


class History:
    """Git history of the lock and of tracked files: one pass per call, one blob budget, cached per refs.

    The pass walks HEAD's history, then the local and remote-tracking branches outside it, so each
    revision is known to be on HEAD or not without a `rev-list` of all of HEAD. The result is kept in
    `.superra-repro/history.json` keyed on HEAD and every branch tip; a repeat call with the same refs
    and paths walks nothing. Blob digests are content-addressed and outlive a ref change.
    """

    def __init__(self, paths, git: Git):
        self.paths, self.git = paths, git
        self.file = paths.state_dir / 'history.json'
        self.data = {'version': HISTORY_VERSION, 'refs': None, 'lock': None, 'paths': {}, 'revs': {},
                     'behind': {}, 'branches': {}, 'digests': {}}
        self.dirty = False
        if not git.ok:
            return
        head = git.text('rev-parse', 'HEAD') or ''
        refs = git.text('for-each-ref', '--format=%(objectname) %(refname)', 'refs/heads', 'refs/remotes') or ''
        key = hashlib.sha256(f'{head}\n{refs}'.encode()).hexdigest()
        try:
            cached = json.loads(self.file.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            cached = None
        if isinstance(cached, dict) and cached.get('version') == HISTORY_VERSION:
            if cached.get('refs') == key:
                self.data = cached
            else:
                self.data['digests'] = cached.get('digests', {})
        self.data['refs'] = key

    def load(self, files):
        """Walk once for the lock (unless cached) and every file not yet cached; then digest their blobs."""
        files = sorted(set(files) - set(self.data['paths']))
        need_lock = self.data['lock'] is None
        if not self.git.ok or not (files or need_lock):
            return
        self.dirty = True
        specs = [f'./{name}' for name in LOCK_FILES if need_lock] + [f'./{f}' for f in files]
        lock, capped, found = [], False, {f: [] for f in files}
        for on_head, ranges in ((True, _HEAD_WALK), (False, _OTHER_WALK)):
            lock_n, path_n = 0, dict.fromkeys(files, 0)
            for rev, names in self.git.walk(ranges, specs):
                self.data['revs'].setdefault(rev['sha'], dict(rev, on_head=on_head))
                if need_lock and names & set(LOCK_FILES):
                    lock_n += 1
                    if lock_n <= LOCK_REV_CAP:
                        lock.append(rev['sha'])
                    capped = capped or lock_n > LOCK_REV_CAP
                for name in names & found.keys():
                    if path_n[name] < BLOB_DEPTH:
                        path_n[name] += 1
                        found[name].append(rev['sha'])
        if need_lock:
            self.data['lock'] = {'revs': lock, 'capped': capped}
        specs = [f'{sha}:./{f}' for f, shas in found.items() for sha in shas] + [f'HEAD:./{f}' for f in files]
        ids = self.git.blob_ids(specs)
        for f, shas in found.items():
            head = ids.get(f'HEAD:./{f}')
            self.data['paths'][f] = {
                'head': head and head[0],
                'revs': [[sha, *ids[f'{sha}:./{f}']] for sha in shas if f'{sha}:./{f}' in ids],
            }
        self._digest(files)

    def _digest(self, files):
        """sha256 of the paths' historical blobs, newest first across paths, within one budget per call."""
        digests, budget, wanted = self.data['digests'], BLOB_TOTAL_BYTES, {}
        queues = [self.data['paths'][f]['revs'] for f in files]
        for depth in range(max(map(len, queues), default=0)):
            for revs in queues:
                if depth < len(revs):
                    _, blob, size = revs[depth]
                    if blob not in digests and blob not in wanted and size <= min(BLOB_MAX_BYTES, budget):
                        wanted[blob] = size
                        budget -= size
        for blob, raw in self.git.blobs(list(wanted)).items():
            digests[blob] = hashlib.sha256(raw).hexdigest()

    def lock_revs(self) -> tuple[list[dict], bool]:
        self.load([])
        lock = self.data['lock'] or {'revs': [], 'capped': False}
        return [self.data['revs'][sha] for sha in lock['revs']], lock['capped']

    def blob_history(self, path) -> list[tuple[dict, str, str]]:
        """(revision, sha256, blob id): HEAD's history newest first, then other branches; unread blobs skipped."""
        entry = self.data['paths'].get(path) or {'revs': []}
        digests = self.data['digests']
        return [(self.data['revs'][sha], digests[blob], blob) for sha, blob, _ in entry['revs'] if blob in digests]

    def head_blob(self, path) -> str | None:
        return (self.data['paths'].get(path) or {}).get('head')

    def on_head(self, sha) -> bool:
        return self.data['revs'].get(sha, {}).get('on_head', False)

    def behind(self, sha) -> int | None:
        """Commits HEAD has beyond *sha*; None when *sha* is not in HEAD's history."""
        if not self.on_head(sha):
            return None
        if sha not in self.data['behind']:
            self.data['behind'][sha] = int(self.git.text('rev-list', '--count', f'{sha}..HEAD') or 0)
            self.dirty = True
        return self.data['behind'][sha]

    def branches(self, sha) -> list[str]:
        """Local and remote-tracking branches whose history holds *sha*."""
        if sha not in self.data['branches']:
            out = self.git.text('for-each-ref', f'--contains={sha}', '--format=%(refname:short)',
                                'refs/heads', 'refs/remotes') or ''
            self.data['branches'][sha] = [name for name in out.splitlines() if not name.endswith('/HEAD')]
            self.dirty = True
        return self.data['branches'][sha]

    def relation(self, sha) -> dict:
        behind = self.behind(sha)
        return {'behind': behind, 'branches': self.branches(sha) if behind is None else []}

    def save(self):
        if self.dirty and self.git.ok and self.paths.state_dir.is_dir():
            from _repro_acceptance import atomic_json
            try:
                atomic_json(self.file, self.data)
            except OSError:
                pass


class LockHistory:
    """Every committed lock on local and remote-tracking branches and HEAD, indexed by (node, hash).

    A revision holds `repro-lock.json`, or, before it, `pytask.lock` with `repro-builds.json`.
    """

    def __init__(self, paths, git: Git, store: History):
        self.paths, self.git, self.store = paths, git, store
        self.revs: list[dict] = []
        self.by_sha: dict[str, dict] = {}
        self.capped = False
        self.head_values: dict[str, dict[str, list[str]]] = {}  # node -> hash -> step entries
        self.index: dict[str, dict[str, list[str]]] = {}
        self.entries: dict[str, dict] = {}
        if not git.ok:
            return
        self.revs, self.capped = store.lock_revs()
        self.by_sha = {r['sha']: r for r in self.revs}
        head = self._read(['HEAD'])['HEAD'] or {}
        for step_id, groups in head.items():
            for key in ('deps', 'products'):
                for node, value in groups[key].items():
                    entries = self.head_values.setdefault(node, {}).setdefault(value, [])
                    if step_id not in entries:
                        entries.append(step_id)
        self._load()

    def _read(self, shas) -> dict[str, dict | None]:
        """Each revision's lock, read from git in one batch; None for a legacy lock without tomllib."""
        names = (LOCK_FILENAME, LEGACY_LOCK_FILENAME, LEGACY_BUILDS_FILENAME)
        blobs = self.git.blobs([f'{sha}:./{name}' for sha in shas for name in names])
        text = lambda sha, name: (lambda raw: raw.decode('utf-8', 'replace') if raw is not None else None)(
            blobs.get(f'{sha}:./{name}'))
        return {sha: _parse_revision(*(text(sha, name) for name in names)) for sha in shas}

    def _load(self):
        cache_dir = self.paths.state_dir / 'lock-index'
        entries, missing = {}, []
        for rev in self.revs:
            try:
                cached = json.loads((cache_dir / f"{rev['sha']}.json").read_text(encoding='utf-8'))
            except (OSError, ValueError):
                cached = None
            if isinstance(cached, dict) and cached.get('version') == LOCK_INDEX_VERSION:
                entries[rev['sha']] = cached['lock']
            else:
                missing.append(rev['sha'])
        for sha, parsed in self._read(missing).items():
            entries[sha] = parsed or {}
            if parsed is not None and self.paths.state_dir.is_dir():  # a revision never changes, so neither does its entry
                from _repro_acceptance import atomic_json
                try:
                    atomic_json(cache_dir / f'{sha}.json', {'version': LOCK_INDEX_VERSION, 'lock': parsed})
                except OSError:
                    pass
        self.entries = entries
        for rev in self.revs:
            for groups in self.entries[rev['sha']].values():
                for group in (groups['deps'], groups['products']):
                    for node, value in group.items():
                        shas = self.index.setdefault(node, {}).setdefault(value, [])
                        if not shas or shas[-1] != rev['sha']:
                            shas.append(rev['sha'])

    def match(self, node: str, value: str) -> dict | None:
        """The revision that introduced *value* for *node*: the oldest on HEAD, else the oldest anywhere."""
        shas = self.index.get(node, {}).get(value, [])
        if not shas:
            return None
        sha = ([s for s in shas if self.store.on_head(s)] or shas)[-1]
        entries = self.head_values.get(node, {}).get(value, [])
        return dict(self.by_sha[sha], head=bool(entries), head_entries=entries, **self.store.relation(sha))


# ---------------------------------------------------------------------------
# Resolver
# ---------------------------------------------------------------------------

class Resolver:
    def __init__(self, report, paths, cache, *, full_diff=False, plan_name='superRA'):
        from _repro_acceptance import read_ledger
        from _repro_state import lock_entry, read_lock_document
        self.report, self.graph, self.paths, self.cache = report, report.graph, paths, cache
        self.full_diff, self.plan_name = full_diff, plan_name
        self.git = Git(paths.project_root)
        self.store = History(paths, self.git)
        self._history = None
        self.lock_document = read_lock_document(paths.lock_file)
        self.lock = {name: lock_entry(name, raw) for name, raw in self.lock_document['steps'].items()}
        self.ledger = read_ledger(paths)['steps']
        self.blob_paths: set[str] = set()
        self.copies_searched: list[str] = []
        self._receipts: dict[str, dict] = {}
        self._diffs: dict[tuple, tuple] = {}

    @property
    def history(self) -> LockHistory:
        if self._history is None:
            self._history = LockHistory(self.paths, self.git, self.store)
        return self._history

    def prepare(self, resolved_paths):
        """Read the git history of every path the rows need in one pass, before any row resolves."""
        self.store.load(path for path in resolved_paths if self.inside(path) is not None)

    def receipt(self, name) -> dict:
        if name not in self._receipts:
            from _repro_acceptance import identity, read_json, receipt_path
            value = read_json(receipt_path(self.paths, name), {})
            ok = value and value.get('id') == identity({k: v for k, v in value.items() if k != 'id'})
            self._receipts[name] = value if ok else {}
        return self._receipts[name]

    def inside(self, resolved) -> Path | None:
        """The path, when it lies in this checkout and outside the runner's own state."""
        if not resolved or resolved.startswith(STATE_DIRNAME + '/'):
            return None
        path = absolute(self.paths.project_root, resolved)
        try:
            path.resolve().relative_to(self.paths.project_root.resolve())
        except (OSError, ValueError):
            return None  # never hash a file outside this checkout
        return path

    def blob_history(self, resolved) -> list[tuple[dict, str, str]]:
        """(revision, sha256, blob id) for a tracked file, HEAD's history first; unread versions skipped."""
        if not self.git.ok or self.inside(resolved) is None:
            return []
        self.store.load([resolved])  # no walk when `prepare` already read it
        rows = self.store.blob_history(resolved)
        if rows:
            self.blob_paths.add(resolved)
        return rows

    def conflicted_copies(self, resolved) -> list[Path]:
        path = self.inside(resolved)
        if path is None or not path.parent.is_dir():
            return []
        self.copies_searched.append(resolved)
        pattern = f"{glob.escape(path.stem)} (*conflicted copy*){glob.escape(path.suffix)}"
        return sorted(path.parent.glob(pattern))

    def sources(self, step, node, value, *, resolved=None, recorded_side=False) -> list[dict]:
        """Every known state that holds *value* for *node*."""
        if value is None or unread(value):
            return []
        found = []
        is_file = resolved and not value.startswith(('dir:', 'saved-input:')) and '::' not in node
        if is_file:
            history = self.blob_history(resolved)
            match = next(((rev, blob) for rev, digest, blob in history if digest == value), None)
            if match:
                rev, blob = match
                found.append(dict(source='git', **{k: rev[k] for k in ('sha', 'rev', 'author', 'date')},
                                  head=blob == self.store.head_blob(resolved), **self.store.relation(rev['sha'])))
            elif history and not recorded_side:
                found.append({'source': 'uncommitted'})
        match = self.history.match(node, value)
        if match:
            found.append(dict(source='lock', **match))
        elif any(value in (e.depends_on.get(node), e.produces.get(node)) for e in self.lock.values()):
            found.append({'source': 'working-lock'})  # uncommitted, or no git
        receipt = self.receipt(step.name)
        if any(group.get(node) == value for group in receipt.get('state', {}).values()):
            run = receipt.get('run', {})
            found.append({'source': 'receipt', 'at': run.get('ended_at') or receipt.get('recorded_at')})
        record = self.ledger.get(step.name)
        if record and any(group.get(node) == value for group in record.get('state', {}).values()):
            found.append({'source': 'acceptance'})
        if recorded_side and is_file:
            for copy in self.conflicted_copies(resolved):
                if self.cache.file_hash(copy) == value:
                    found.append({'source': 'conflicted-copy',
                                  'path': str(copy.relative_to(self.paths.project_root))})
        return found

    # -- rows ---------------------------------------------------------------

    def step_changes(self, entry) -> list[tuple]:
        """`row` arguments for the step's changed nodes; missing, failed, and upstream stay status reasons."""
        step = entry.step
        if entry.status == 'fresh':
            return []
        record = self.ledger.get(step.name)
        if record and entry.acceptance_invalid:
            from _repro_acceptance import current_state, state_differences
            state = current_state(self.graph, step, self.paths, self.cache)
            resolved = self._resolved_paths(step)
            return [(step, d['node'].removesuffix('::product'), d['kind'], d['before'], d['after'],
                     resolved.get(d['node'].removesuffix('::product')), True)
                    for d in state_differences(record['state'], state)
                    if d['after'] is not None and not unread(d['after'])]
        return self._lock_changes(entry)

    def _resolved_paths(self, step) -> dict[str, str]:
        deps, products = step_nodes(step, output_nodes(self.graph))
        return {node[0]: node[1] for node in deps + directory_dep_nodes(self.graph, step) + products}

    def _lock_changes(self, entry) -> list[tuple]:
        step = entry.step
        lock = self.lock.get(step.name)
        deps, products = step_nodes(step, output_nodes(self.graph))
        dep_nodes = {n[0]: n for n in deps + directory_dep_nodes(self.graph, step)}
        out_nodes = {n[0]: n for n in products}
        root = self.paths.project_root
        changes = entry.changes
        if step.kind == 'check' and lock and any(c.node == stamp_ref(step.name) for c in changes):
            # A missing stamp hides the inputs that moved since the lock's run.
            from _repro_state import _changed_nodes
            changes = _changed_nodes(step, lock, self.paths, self.cache, deps, [])
        rows = []
        for change in changes:
            node, kind = change.node, change.kind
            if kind == 'spec':
                recorded, current, resolved = (lock.depends_on.get(node) if lock else None), spec_hash(step), None
            elif kind == 'boundary':
                recorded = next((item['digest'] for item in self.receipt(step.name).get('boundary_inputs', [])
                                 if item['logical'] == node), None)
                dep = next((d for d in step.deps if d.logical == node), None)
                resolved = dep and dep.resolved
                current = self.cache.path_state(absolute(root, resolved)) if dep else None
            elif kind == 'dependency':
                spec = dep_nodes.get(node)
                recorded = lock.depends_on.get(node) if lock else None
                current = dependency_state(self.cache, root, spec, recorded) if spec else None
                resolved = spec and spec[1]
            else:
                spec = out_nodes.get(node)
                recorded = lock.produces.get(node) if lock else None
                current = node_state(self.cache, root, spec) if spec else None
                resolved = spec and spec[1]
            if current is not None and not unread(current):
                rows.append((step, node, kind, recorded, current, resolved, False))
        return rows

    def row(self, step, node, kind, recorded, current, resolved, reviewed=False) -> dict:
        rec = self.sources(step, node, recorded, resolved=resolved, recorded_side=True)
        if reviewed:
            rec = [{'source': 'acceptance'}] + [s for s in rec if s['source'] != 'acceptance']
        cur = self.sources(step, node, current, resolved=resolved)
        role = 'output' if kind == 'output' else 'input'
        other = [s for s in cur if s['source'] != 'uncommitted']
        cause = 'input-changed' if role == 'input' else 'other-build' if other else 'unknown-output'
        row = dict(step=step.name, task=step.task_path, node=node, kind=kind, path=resolved,
                   recorded=recorded, current=current, recorded_sources=rec, current_sources=cur,
                   cause=cause, hint=CAUSES[cause], diffstat=None, diff=None)
        if role == 'input':
            self._input_diff(row, step)
        row['env'] = self._env(row, step)
        row['evidence'] = self._evidence(row)
        row['command'] = self._command(step, row)
        return row

    def _input_diff(self, row, step):
        rec_git = _first(row['recorded_sources'], 'git')
        path = row['path']
        cur_git = _first(row['current_sources'], 'git')
        if path and self._online_only(path) and not (rec_git and cur_git):
            return  # only a diff between two revisions leaves the working tree unread
        if rec_git and path:
            revs = [rec_git['rev']] + ([cur_git['rev']] if cur_git else [])
            spec = './' + path
            key = (*revs, spec)
            if key not in self._diffs:  # rows of several readers share one diff
                self._diffs[key] = (self.git.text('diff', '--shortstat', *revs, '--', spec) or None,
                                    (self.git.text('diff', *revs, '--', spec) or '').splitlines())
            row['diffstat'], lines = self._diffs[key]
            self._set_diff(row, lines)
            return
        snapshot = self.receipt(step.name).get('snapshots', {}).get(row['node'])
        if (snapshot is not None and path and path not in self.graph.producers
                and hashlib.sha256(snapshot.encode()).hexdigest() == row['recorded']):
            import difflib
            try:
                now = absolute(self.paths.project_root, path).read_text(encoding='utf-8')
            except (OSError, UnicodeError):
                return
            row['recorded_sources'].insert(0, {'source': 'snapshot'})
            self._set_diff(row, [line.rstrip('\n') for line in difflib.unified_diff(
                snapshot.splitlines(True), now.splitlines(True), n=3)])

    def _online_only(self, resolved) -> bool:
        path = absolute(self.paths.project_root, resolved)
        try:
            return is_online_only(path, path.stat())
        except OSError:
            return False

    def _set_diff(self, row, lines):
        hunk = next((i for i, line in enumerate(lines) if line.startswith('@@')), 0)
        lines = lines[hunk:]  # the row already names the path and both sides
        row['diff_lines'] = len(lines)
        row['diff'] = '\n'.join(lines if self.full_diff else lines[:DIFF_LINES]) or None

    def _env(self, row, step) -> dict | None:
        """The build record behind the row's lock source, compared with this machine."""
        builder = step.name if row['kind'] == 'output' else self.graph.producers.get(row['path'] or '')
        source = next((s for s in row['recorded_sources'] + row['current_sources']
                       if s['source'] in ('lock', 'working-lock')), None)
        if builder is None or source is None:
            return None
        from _repro_builds import builder_record, differences, env_here
        if source['source'] == 'lock':
            where = f"lock {source['rev']}"
            entry = self.history.entries.get(source['sha'], {}).get(builder)
        else:
            where = 'the working lock'
            entry = self.lock_document['steps'].get(builder)
            entry = entry and {'deps': entry.get('deps', {}), 'built_on': entry.get('built_on', {})}
        record = builder_record(self.graph, entry)
        if not record:
            return None
        diffs = differences(record, env_here(self.graph, self.paths, self.cache, record))
        return dict(builder=builder, where=where, record=record, status='differs' if diffs else 'same',
                    differences=diffs)

    def _evidence(self, row) -> str:
        text = f"recorded {label(row['recorded_sources'])}; current {label(row['current_sources'])}"
        env = row.get('env')
        if env and env['status'] == 'same':
            text += '; env: same as lock builder'
        elif env:
            text += '; env: differs — ' + ', '.join(env['differences'])
        return text + (f"; {row['diffstat']}" if row['diffstat'] else '')

    def _command(self, step, row) -> str:
        path = row['path']
        rec_git, cur_git = _first(row['recorded_sources'], 'git'), _first(row['current_sources'], 'git')
        if row['cause'] == 'input-changed':
            if row['kind'] == 'spec':
                task_md = f"{self.plan_name}/{step.task_path + '/' if step.task_path else ''}task.md"
                rev = _first(row['recorded_sources'], 'lock')
                return f"git diff {rev['rev'] + ' ' if rev else ''}-- {shlex.quote(task_md)} {self.plan_name}/config.yaml"
            if rec_git:
                return f"git diff {rec_git['rev']} {cur_git['rev'] + ' ' if cur_git else ''}-- {shlex.quote(path)}"
            producer = self.graph.producers.get(path or '')
            if producer:
                entry = self.report.entry(producer)
                if entry is not None and entry.status == 'fresh':  # nothing left to explain upstream
                    return f'superra repro build {shlex.quote(target_ref(step))}'
                return f'superra repro explain {shlex.quote(target_ref(self.graph.step(producer)))}'
            if row['diff']:
                return f'superra repro explain {shlex.quote(target_ref(step))} --diff'
        elif row['cause'] == 'other-build':
            shown = row['current_sources'][0]  # the source the row prints
            if shown['source'] in ('lock', 'git'):
                return f"git show --stat {shown['rev']}"
        return f"superra repro explain {shlex.quote(path or row['node'])} --json"

    def searched(self) -> dict:
        return {
            'receipts': f'{STATE_DIRNAME}/baselines',
            'ledger': 'repro-acceptance/',
            'lock_revisions': [r['rev'] for r in self.history.revs],
            'lock_history_capped': self.history.capped,
            'git_available': self.git.ok,
            'blob_histories': {path: len(self.store.blob_history(path)) for path in sorted(self.blob_paths)},
            'conflicted_copies_beside': sorted(set(self.copies_searched)),
        }


def _capped(names, shown) -> str:
    return ', '.join(names[:shown]) + (f" and {len(names) - shown} more" if len(names) > shown else '')


def _first(sources, name):
    return next((s for s in sources if s['source'] == name), None)


def label(sources) -> str:
    if not sources:
        return 'no known source'
    text = _label(sources[0])
    copy = _first(sources[1:], 'conflicted-copy')
    return text + (f", also in {_label(copy)}" if copy else '')


def _relation(s, at_head) -> str:
    """How a lock or git source's revision relates to HEAD."""
    if s['head']:
        return at_head
    if s['behind'] is not None:
        return f"earlier commit, {s['behind']} behind HEAD"
    names = s['branches']
    return "not in HEAD's history" + (f"; on {_capped(names, BRANCHES_SHOWN)}" if names else '')


def _label(s) -> str:
    kind = s['source']
    if kind == 'lock':
        names = s['head_entries']
        at_head = f"in HEAD's lock, {'entry' if len(names) == 1 else 'entries'} " + _capped(names, ENTRIES_SHOWN)
        return f"lock {s['rev']} ({s['author']}, {s['date']}; {_relation(s, at_head)})"
    if kind == 'git':
        return f"git {s['rev']} ({_relation(s, "HEAD's version")})"
    if kind == 'uncommitted':
        return 'uncommitted'
    if kind == 'working-lock':
        return 'working lock (not committed)'
    if kind == 'snapshot':
        return 'snapshot from the build here'
    if kind == 'receipt':
        return f"built here {_stamp(s['at'])}"
    if kind == 'acceptance':
        return 'reviewed acceptance'
    return f"conflicted copy {s['path']}"


# ---------------------------------------------------------------------------
# Grouping and rendering
# ---------------------------------------------------------------------------

MULTI_TARGET_VERBS = ('build', 'status')  # `explain` takes one target
_STEP_COMMAND = re.compile(r"^(superra repro \w+) (\S+)((?: --\S+)*)$")


def group_rows(rows) -> list[dict]:
    """One group per cause, in cause order, with one file per changed node and current hash.

    A file read by several steps is one entry naming them all; its first row stands for it in text
    and in the commands. Multi-target commands merge their targets.
    """
    groups = []
    for cause, hint in CAUSES.items():
        members = [row for row in rows if row['cause'] == cause]
        if not members:
            continue
        files = {}
        for index, row in enumerate(members):
            files.setdefault((row['node'], row['current']), []).append(index)
        files = [dict(node=node, current=current, row=indices[0],
                      steps=sorted(dict.fromkeys(members[i]['step'] for i in indices)),
                      other_recorded=sum(members[i]['recorded'] != members[indices[0]]['recorded'] for i in indices))
                 for (node, current), indices in files.items()]
        commands, merged = [], {}
        for command in (members[f['row']]['command'] for f in files):
            match = _STEP_COMMAND.match(command)
            if not match or match.group(1).split()[-1] not in MULTI_TARGET_VERBS:
                if command not in commands:
                    commands.append(command)
                continue
            key = match.group(1) + match.group(3)
            if key not in merged:
                merged[key] = (len(commands), [])
                commands.append(None)
            if match.group(2) not in merged[key][1]:
                merged[key][1].append(match.group(2))
        for key, (index, targets) in merged.items():
            verb, _, flags = key.partition(' --')
            commands[index] = f"{verb} {' '.join(targets)}{' --' + flags if flags else ''}"
        groups.append(dict(cause=cause, hint=hint, steps=list(dict.fromkeys(r['step'] for r in members)),
                           rows=members, files=files, commands=commands))
    return groups


def _row_lines(row, with_step, show_diff) -> list[str]:
    who = f"{row['step']}  " if with_step else ''
    lines = [f"    {who}{row['kind']:<10} {row['node']}  {short(row['recorded'])} → {short(row['current'])}  {row['evidence']}"]
    if show_diff and row.get('diff'):
        lines += ['      ' + line for line in row['diff'].splitlines()]
        hidden = row.get('diff_lines', 0) - len(row['diff'].splitlines())
        if hidden > 0:
            lines.append(f'      … {hidden} more line(s); --diff shows all')
    return lines


def render_groups(groups, *, with_step, diffs=True) -> list[str]:
    lines = []
    for group in groups:
        lines.append(f"  {group['cause']} — {group['hint']}")
        for file in group['files']:
            steps = file['steps']
            lines += _row_lines(group['rows'][file['row']], with_step and len(steps) == 1, diffs)
            if with_step and len(steps) > 1:
                other = file['other_recorded']
                lines.append(f"      steps: {_capped(steps, STEPS_SHOWN)}"
                             + (f"; {other} recorded a different hash (--json lists each)" if other else ''))
        lines += [f"    next: {command}" for command in group['commands']]
    return lines


def render_searched(searched) -> str:
    parts = [f"receipts in {searched['receipts']}", f"acceptance ledger {searched['ledger']}"]
    if not searched['git_available']:
        parts.append('no git history (not a git checkout)')
    else:
        revs = searched['lock_revisions']
        capped = f' (newest {len(revs)} only)' if searched['lock_history_capped'] else ''
        parts.append(f"the lock at {len(revs)} revision(s){capped} on local and remote-tracking branches and HEAD")
        histories = searched['blob_histories']
        if len(histories) > FILES_SHOWN:
            parts.append(f"git history of {len(histories)} tracked files")
        parts += [f"git history of {path} ({count} revision(s))"
                  for path, count in histories.items() if len(histories) <= FILES_SHOWN]
    copies = searched['conflicted_copies_beside']
    if copies:
        parts.append('conflicted copies beside ' + (', '.join(copies) if len(copies) <= FILES_SHOWN
                                                    else f'{len(copies)} files'))
    return 'searched: ' + '; '.join(parts)


# ---------------------------------------------------------------------------
# Targets
# ---------------------------------------------------------------------------

def resolve_target(graph, target, project_root):
    """('step', name) | ('task', (task_path, names)) | ('path', path_target dict)."""
    from _repro_state import bare_step, select_steps
    if '#' in target:
        names, unknown = select_steps(graph, [target])
        if unknown:
            raise ReproStateError(f'no step matches {target!r}')
        return 'step', names[0]
    names, unknown = select_steps(graph, [target])
    if not unknown and names == [target] and '/' not in target and target != '.' and bare_step(graph, target):
        owned = [s for s in graph.steps if s.task_path == target or s.task_path.startswith(target + '/')]
        if not owned:
            return 'step', target
    if not unknown:
        task = target.removeprefix('./').rstrip('/')
        return 'task', ('' if task == '.' else task, names)
    path = path_target(graph, target, project_root)
    if path is None:
        raise ReproStateError(f'{target!r} is no task, step, or declared path')
    return 'path', path


def path_target(graph, target, project_root):
    text = target
    if Path(target).is_absolute():
        try:
            text = str(Path(target).resolve().relative_to(Path(project_root).resolve()))
        except (OSError, ValueError):
            return None
    text = text.removeprefix('./').rstrip('/')
    producer = node = resolved = None
    for step in graph.steps:
        for out in step.outs:
            if text in (out.path.logical, out.path.resolved):
                producer, node, resolved = step, out.path.logical, (out.sidecar or out.path).resolved
    consumers = [s for s in graph.steps if any(text in (d.logical, d.resolved) for d in s.deps)]
    if producer is None and not consumers:
        return None
    if node is None:
        dep = next(d for d in consumers[0].deps if text in (d.logical, d.resolved))
        node, resolved = output_nodes(graph).get(dep.resolved, (dep.logical, dep.resolved))[:2]
    return dict(path=text, node=node, resolved=resolved, producer=producer, consumers=consumers)


def explain(report, paths, cache, kind, value, *, full_diff=False, plan_name='superRA') -> dict:
    from _repro import step_errors
    resolver = Resolver(report, paths, cache, full_diff=full_diff, plan_name=plan_name)
    if kind == 'path':
        result = _explain_path(resolver, value)
        names = [s.name for s in ([value['producer']] if value['producer'] else []) + value['consumers']]
    else:
        names = [value] if kind == 'step' else value[1]
        pending = {name: resolver.step_changes(report.entry(name)) for name in names}
        resolver.prepare(change[5] for changes in pending.values() for change in changes)
        steps, rows = [], []
        for name in names:
            step_rows = [resolver.row(*change) for change in pending[name]]
            rows += step_rows
            steps.append(dict(report.entry(name).to_dict(), rows=step_rows))
        result = {'target': target_ref(report.entry(names[0]).step) if kind == 'step' else (value[0] or '.'),
                  'kind': kind, 'steps': steps, 'groups': group_rows(rows)}
    result['errors'] = [f.to_dict() for f in step_errors(report.graph, names)[0]]
    result['graph_errors'] = sum(f.severity == 'error' for f in report.graph.findings)
    result['searched'] = resolver.searched()
    resolver.store.save()
    return result


def _explain_path(resolver, target) -> dict:
    node, resolved = target['node'], target['resolved']
    current = resolver.cache.path_state(absolute(resolver.paths.project_root, resolved))
    here = None
    if unread(current):
        here, current = unread_phrase(current), None
    owner, readers = target['producer'], target['consumers']
    resolver.prepare([resolved])
    rows, seen = [], set()
    if current is not None:
        for step in ([owner] if owner else []) + readers:
            lock = resolver.lock.get(step.name)
            recorded = (lock.produces.get(node) or lock.depends_on.get(node)) if lock else None
            if recorded is None or recorded == current or recorded in seen:
                continue
            seen.add(recorded)
            rows.append(resolver.row(step, node, 'output' if step is owner else 'dependency',
                                     recorded, current, resolved))
    return {
        'target': target['path'], 'kind': 'path', 'node': node, 'current': current, 'here': here,
        'current_sources': resolver.sources(owner or readers[0], node, current, resolved=resolved),
        'producer': target_ref(owner) if owner else None,
        'consumers': [target_ref(s) for s in readers],
        'rows': rows, 'groups': group_rows(rows),
    }


def format_explain(result, report, *, full_diff=False) -> str:
    lines = []
    if result['kind'] == 'path':
        now = (result['here'] if result.get('here') else 'missing here' if result['current'] is None else
               f"now {short(result['current'])}  {label(result['current_sources'])}")
        lines += [f"{result['target']}  {now}",
                  f"  produced by {result['producer'] or '(no step; external input)'}",
                  f"  read by {', '.join(result['consumers']) or '(no step)'}"]
        if not result['rows'] and result['current'] is not None:
            lines.append('  every lock entry for it matches the current bytes')
        lines += render_groups(result['groups'], with_step=True)
    elif result['kind'] == 'step':
        step = result['steps'][0]
        lines.append(f"{step['name']}  [{step['status']}]  {step['reason']}")
        lines += _step_header(report.entry(step['name']), report)
        if step['status'] == 'fresh':
            lines.append('  nothing changed since the recorded build or acceptance')
        lines += render_groups(result['groups'], with_step=False)
    else:
        stale = [s for s in result['steps'] if s['status'] != 'fresh']
        lines.append(f"{result['target']}: {len(stale)} of {len(result['steps'])} step(s) not fresh")
        lines += render_groups(result['groups'], with_step=True, diffs=full_diff)
        other = [s for s in stale if not s['rows'] or s['status'] == 'failed']
        if other:
            lines.append('  status (no hash to resolve):')
            lines += [f"    {s['name']}  [{s['status']}]  {s['reason']}" for s in other]
        notes = [s for s in result['steps'] if s['status'] == 'fresh'
                 and s['reason'] not in ('up to date', 'reviewed baseline')]
        lines += [f"  note: {s['name']} fresh — {s['reason']}" for s in notes]
    if result['errors']:
        lines.append('  graph errors on these steps; `build` refuses them:')
        lines += [f"    [{f['severity'].upper()}] {f['task_path'] or '(root)'}: {f['message']}" for f in result['errors']]
    if result['graph_errors']:
        lines.append(f"{result['graph_errors']} graph error(s); run `superra task check`.")
    lines.append(render_searched(result['searched']))
    return '\n'.join(lines)


def _step_header(entry, report) -> list[str]:
    step = entry.step
    owner = step.task_path or '(root)'
    lines = [f"  task {owner} · {step.kind} · cmd {step.cmd_logical}"]
    run = []
    if entry.duration:
        run.append(f"last run {entry.duration:.1f}s at {_stamp(entry.last_run)}")
    if entry.log:
        run.append(f"log {entry.log}")
    if run:
        lines.append('  ' + ' · '.join(run))
    if entry.acceptance:
        lines.append(f"  reviewed acceptance: {entry.acceptance['reason']}")
    upstream = sorted({src for src, dst, _ in report.graph.step_edges if dst == step.name})
    if upstream:
        lines.append('  upstream: ' + ', '.join(
            f"{name} {report.entry(name).status if report.entry(name) else 'unknown'}" for name in upstream))
    if entry.external_consumers:
        lines.append(f"  outs read outside {owner}: {', '.join(entry.external_consumers)}")
    else:
        lines.append(f"  no step outside {owner} reads its outs")
    return lines
