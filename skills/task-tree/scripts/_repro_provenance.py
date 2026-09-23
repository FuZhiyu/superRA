"""Where a changed node's recorded and current bytes came from, for `repro explain`.

Three causes, keyed on the node's role in the step: an input (dependency or
step definition) changed, an output holds another recorded build, or an output
matches nothing recorded. Everything finer is a source fact on the row, found
in the local receipt, the acceptance ledger, the committed lock history on
local and remote-tracking branches (parsed once per revision into
`.superra-repro/lock-index/`),
the git blob history of tracked files, and Dropbox conflicted copies. Only
changed nodes are resolved; git is optional. Stdlib only.
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
    STATE_DIRNAME, ReproStateError, absolute, dependency_state, directory_dep_nodes, node_state,
    output_nodes, spec_hash, stamp_ref, step_nodes, tomllib, _stamp,
)

LOCK_REV_CAP = 200
BLOB_DEPTH = 50
BLOB_MAX_BYTES = 16 << 20   # larger historical versions are not read
BLOB_TOTAL_BYTES = 64 << 20
DIFF_LINES = 20
BRANCHES_SHOWN = 3
ENTRIES_SHOWN = 3
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

    def revs(self, *args) -> list[dict]:
        out = self.text('log', _LOG_FORMAT, _LOG_DATE, *args) or ''
        rows = []
        for line in out.splitlines():
            parts = line.split('\x1f')
            if len(parts) == 4:
                rows.append(dict(zip(('sha', 'rev', 'author', 'date'), parts)))
        return rows

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
        try:
            digest = hashlib.sha256(paths.lock_file.read_bytes()).hexdigest()
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
            spec = './' + paths.lock_file.name
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
    from _repro_builds import BUILDS, lock_id, read_builds
    commit = lock_commit(paths, memo)
    if 'builds' not in memo:
        try:
            memo['builds'] = read_builds((paths.project_root / BUILDS).read_text(encoding='utf-8'))
        except OSError:
            memo['builds'] = {}
    record = memo['builds'].get(name) or {}
    built = (f" on {record['platform']}" if record.get('platform')
             and record.get('lock_id') == lock_id(entry.depends_on, entry.produces) else '')
    return f"{CHECK_ELSEWHERE} {'lock ' + commit if commit else 'the working lock'}{built}; not run here"


# ---------------------------------------------------------------------------
# Lock history
# ---------------------------------------------------------------------------

def _parse_lock(text) -> dict:
    try:
        document = tomllib.loads(text) if text else {}
    except ValueError:
        document = {}
    return {item['id']: {'deps': dict(item.get('depends_on') or {}),
                         'products': dict(item.get('produces') or {})}
            for item in document.get('task', []) or []
            if isinstance(item, dict) and isinstance(item.get('id'), str)}


class LockHistory:
    """Every committed `pytask.lock` on local and remote-tracking branches and HEAD, indexed by (node, hash)."""

    def __init__(self, paths, git: Git):
        self.paths, self.git = paths, git
        self.revs: list[dict] = []
        self.by_sha: dict[str, dict] = {}
        self.capped = False
        self.on_head: set[str] = set()
        self.head_values: dict[str, dict[str, list[str]]] = {}  # node -> hash -> step entries
        self.index: dict[str, dict[str, list[str]]] = {}
        self._behind: dict[str, int] = {}
        self._builds: dict[str, dict] = {}
        self.entries: dict[str, dict] = {}
        self._branches: dict[str, list[str]] = {}
        if not git.ok or tomllib is None:
            return
        spec = './' + paths.lock_file.name
        revs = git.revs(f'--max-count={LOCK_REV_CAP + 1}', '--full-history', '--topo-order', '--branches', '--remotes', 'HEAD', '--', spec)
        self.capped = len(revs) > LOCK_REV_CAP
        self.revs = revs[:LOCK_REV_CAP]
        self.by_sha = {r['sha']: r for r in self.revs}
        self.on_head = set((git.text('rev-list', 'HEAD') or '').split())
        head = git.blobs([f'HEAD:{spec}']).get(f'HEAD:{spec}')
        for step_id, groups in _parse_lock(head.decode('utf-8', 'replace') if head else '').items():
            for group in groups.values():
                for node, value in group.items():
                    entries = self.head_values.setdefault(node, {}).setdefault(value, [])
                    if step_id not in entries:
                        entries.append(step_id)
        self._load(spec)

    def _load(self, spec):
        cache_dir = self.paths.state_dir / 'lock-index'
        entries, missing = {}, []
        for rev in self.revs:
            try:
                entries[rev['sha']] = json.loads((cache_dir / f"{rev['sha']}.json").read_text(encoding='utf-8'))
            except (OSError, ValueError):
                missing.append(rev['sha'])
        blobs = self.git.blobs([f'{sha}:{spec}' for sha in missing])
        for sha in missing:
            raw = blobs.get(f'{sha}:{spec}')
            entries[sha] = _parse_lock(raw.decode('utf-8', 'replace') if raw else '')
            if self.paths.state_dir.is_dir():  # a revision never changes, so neither does its entry
                from _repro_acceptance import atomic_json
                try:
                    atomic_json(cache_dir / f'{sha}.json', entries[sha])
                except OSError:
                    pass
        self.entries = entries
        for rev in self.revs:
            for groups in entries[rev['sha']].values():
                for group in groups.values():
                    for node, value in group.items():
                        shas = self.index.setdefault(node, {}).setdefault(value, [])
                        if not shas or shas[-1] != rev['sha']:
                            shas.append(rev['sha'])

    def match(self, node: str, value: str) -> dict | None:
        """The revision that introduced *value* for *node*: the oldest on HEAD, else the oldest anywhere."""
        shas = self.index.get(node, {}).get(value, [])
        if not shas:
            return None
        sha = ([s for s in shas if s in self.on_head] or shas)[-1]
        behind = self.behind(sha)
        entries = self.head_values.get(node, {}).get(value, [])
        return dict(self.by_sha[sha], head=bool(entries), head_entries=entries, behind=behind,
                    branches=self.branches(sha) if behind is None else [])

    def builds_at(self, sha) -> dict:
        """`repro-builds.json` as committed at *sha*."""
        if sha not in self._builds:
            from _repro_builds import BUILDS, read_builds
            raw = self.git.blobs([f'{sha}:./{BUILDS}']).get(f'{sha}:./{BUILDS}')
            self._builds[sha] = read_builds(raw.decode('utf-8', 'replace') if raw else '')
        return self._builds[sha]

    def branches(self, sha) -> list[str]:
        """Local and remote-tracking branches whose history holds *sha*."""
        if sha not in self._branches:
            out = self.git.text('for-each-ref', f'--contains={sha}', '--format=%(refname:short)',
                                'refs/heads', 'refs/remotes') or ''
            self._branches[sha] = [name for name in out.splitlines() if not name.endswith('/HEAD')]
        return self._branches[sha]

    def behind(self, sha) -> int | None:
        """Commits HEAD has beyond *sha*; None when *sha* is not in HEAD's history."""
        if sha not in self.on_head:
            return None
        if sha not in self._behind:
            self._behind[sha] = int(self.git.text('rev-list', '--count', f'{sha}..HEAD') or 0)
        return self._behind[sha]


# ---------------------------------------------------------------------------
# Resolver
# ---------------------------------------------------------------------------

class Resolver:
    def __init__(self, report, paths, cache, *, full_diff=False, plan_name='superRA'):
        from _repro_acceptance import read_ledger
        from _repro_state import read_lock
        self.report, self.graph, self.paths, self.cache = report, report.graph, paths, cache
        self.full_diff, self.plan_name = full_diff, plan_name
        self.git = Git(paths.project_root)
        self.history = LockHistory(paths, self.git)
        self.lock = read_lock(paths.lock_file)
        self.ledger = read_ledger(paths)['steps']
        self.blob_histories: dict[str, list[tuple[dict, str]]] = {}
        self.copies_searched: list[str] = []
        self._receipts: dict[str, dict] = {}

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

    def blob_history(self, resolved) -> list[tuple[dict, str]]:
        """(revision, sha256 of its blob) newest first, for a tracked file; oversize versions skipped."""
        if resolved in self.blob_histories:
            return self.blob_histories[resolved]
        rows = []
        if self.git.ok and self.inside(resolved) is not None:
            spec = './' + resolved
            revs = self.git.revs(f'-n{BLOB_DEPTH}', '--branches', 'HEAD', '--', spec)
            ids = self.git.blob_ids([f"{r['sha']}:{spec}" for r in revs])
            wanted, budget = [], BLOB_TOTAL_BYTES
            for blob, size in dict.fromkeys(ids.values()):
                if size <= min(BLOB_MAX_BYTES, budget):
                    wanted.append(blob)
                    budget -= size
            digests = {blob: hashlib.sha256(raw).hexdigest() for blob, raw in self.git.blobs(wanted).items()}
            for rev in revs:
                blob = ids.get(f"{rev['sha']}:{spec}")
                if blob and blob[0] in digests:
                    rows.append((rev, digests[blob[0]]))
        self.blob_histories[resolved] = rows
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
        if value is None:
            return []
        found = []
        is_file = resolved and not value.startswith(('dir:', 'saved-input:')) and '::' not in node
        if is_file:
            history = self.blob_history(resolved)
            match = next((rev for rev, digest in history if digest == value), None)
            if match:
                found.append(dict(source='git', **match))
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
            found.append({'source': 'acceptance', 'actor': record.get('actor'), 'at': record.get('recorded_at')})
        if recorded_side and is_file:
            for copy in self.conflicted_copies(resolved):
                if self.cache.file_hash(copy) == value:
                    found.append({'source': 'conflicted-copy',
                                  'path': str(copy.relative_to(self.paths.project_root))})
        return found

    # -- rows ---------------------------------------------------------------

    def step_rows(self, entry) -> list[dict]:
        """Rows for the step's changed nodes; missing, failed, and upstream stay status reasons."""
        step = entry.step
        if entry.status == 'fresh':
            return []
        record = self.ledger.get(step.name)
        if record and entry.acceptance_invalid:
            from _repro_acceptance import current_state, state_differences
            state = current_state(self.graph, step, self.paths, self.cache)
            resolved = self._resolved_paths(step)
            return [self.row(step, d['node'].removesuffix('::product'), d['kind'], d['before'], d['after'],
                             resolved.get(d['node'].removesuffix('::product')), reviewed=True)
                    for d in state_differences(record['state'], state) if d['after'] is not None]
        return self._lock_rows(entry)

    def _resolved_paths(self, step) -> dict[str, str]:
        deps, products = step_nodes(step, output_nodes(self.graph))
        return {node[0]: node[1] for node in deps + directory_dep_nodes(self.graph, step) + products}

    def _lock_rows(self, entry) -> list[dict]:
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
            if current is not None:
                rows.append(self.row(step, node, kind, recorded, current, resolved))
        return rows

    def row(self, step, node, kind, recorded, current, resolved, *, reviewed=False) -> dict:
        rec = self.sources(step, node, recorded, resolved=resolved, recorded_side=True)
        if reviewed:
            record = self.ledger[step.name]
            rec = [{'source': 'acceptance', 'actor': record.get('actor'), 'at': record.get('recorded_at')}] + [
                s for s in rec if s['source'] != 'acceptance']
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
        if rec_git and path:
            cur_git = _first(row['current_sources'], 'git')
            revs = [rec_git['rev']] + ([cur_git['rev']] if cur_git else [])
            spec = './' + path
            row['diffstat'] = self.git.text('diff', '--shortstat', *revs, '--', spec) or None
            self._set_diff(row, (self.git.text('diff', *revs, '--', spec) or '').splitlines())
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
        from _repro_builds import BUILDS, differences, env_here, lock_id, read_builds
        if source['source'] == 'lock':
            where = f"lock {source['rev']}"
            record = self.history.builds_at(source['sha']).get(builder)
            entry = self.history.entries.get(source['sha'], {}).get(builder, {})
            locked = lock_id(entry.get('deps', {}), entry.get('products', {})) if entry else None
        else:
            where = 'the working lock'
            try:
                record = read_builds((self.paths.project_root / BUILDS).read_text(encoding='utf-8')).get(builder)
            except OSError:
                record = None
            entry = self.lock.get(builder)
            locked = lock_id(entry.depends_on, entry.produces) if entry else None
        if not record:
            return None
        env = dict(builder=builder, where=where, record=record)
        if record.get('lock_id') != locked:
            return dict(env, status='record-mismatch')
        diffs = differences(record, env_here(self.graph, self.paths, self.cache, record))
        return dict(env, status='differs' if diffs else 'same', differences=diffs)

    def _evidence(self, row) -> str:
        text = f"recorded {label(row['recorded_sources'])}; current {label(row['current_sources'])}"
        env = row.get('env')
        if env and env['status'] == 'same':
            text += '; env: same as lock builder'
        elif env and env['status'] == 'differs':
            text += '; env: differs — ' + ', '.join(env['differences'])
        elif env:
            text += f"; env: {env['where']} has a build record for {env['builder']} that does not match its lock entry"
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
            'ledger': 'repro-acceptance.json',
            'lock_revisions': [r['rev'] for r in self.history.revs],
            'lock_history_capped': self.history.capped,
            'git_available': self.git.ok,
            'blob_histories': {path: len(rows) for path, rows in self.blob_histories.items() if rows},
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


def _label(s) -> str:
    kind = s['source']
    if kind == 'lock':
        if s['head']:
            names = s['head_entries']
            relation = (f"in HEAD's lock, {'entry' if len(names) == 1 else 'entries'} "
                        + _capped(names, ENTRIES_SHOWN))
        elif s['behind'] is not None:
            relation = f"earlier commit, {s['behind']} behind HEAD"
        else:
            names = s['branches']
            relation = "not in HEAD's history" + (f"; on {_capped(names, BRANCHES_SHOWN)}" if names else '')
        return f"lock {s['rev']} ({s['author']}, {s['date']}; {relation})"
    if kind == 'git':
        return f"git {s['rev']}"
    if kind == 'uncommitted':
        return 'uncommitted'
    if kind == 'working-lock':
        return 'working lock (not committed)'
    if kind == 'snapshot':
        return 'snapshot from the build here'
    if kind == 'receipt':
        return f"built here {_stamp(s['at'])}"
    if kind == 'acceptance':
        return f"reviewed {_stamp(s['at'])}"
    return f"conflicted copy {s['path']}"


# ---------------------------------------------------------------------------
# Grouping and rendering
# ---------------------------------------------------------------------------

MULTI_TARGET_VERBS = ('build', 'status')  # `explain` takes one target
_STEP_COMMAND = re.compile(r"^(superra repro \w+) (\S+)((?: --\S+)*)$")


def group_rows(rows) -> list[dict]:
    """One group per cause, in cause order; multi-target commands merge their targets."""
    groups = []
    for cause, hint in CAUSES.items():
        members = [row for row in rows if row['cause'] == cause]
        if not members:
            continue
        commands, merged = [], {}
        for row in members:
            match = _STEP_COMMAND.match(row['command'])
            if not match:
                if row['command'] not in commands:
                    commands.append(row['command'])
                continue
            if match.group(1).split()[-1] not in MULTI_TARGET_VERBS:
                if row['command'] not in commands:
                    commands.append(row['command'])
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
                           rows=members, commands=commands))
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


def render_groups(groups, *, with_step) -> list[str]:
    lines = []
    for group in groups:
        lines.append(f"  {group['cause']} — {group['hint']}")
        shown = set()
        for row in group['rows']:
            key = (row['node'], row['diff'])
            lines += _row_lines(row, with_step, key not in shown)
            shown.add(key)
        lines += [f"    next: {command}" for command in group['commands']]
    return lines


def render_searched(searched) -> str:
    parts = [f"receipts in {searched['receipts']}", f"acceptance ledger {searched['ledger']}"]
    if not searched['git_available']:
        parts.append('no git history (not a git checkout)')
    else:
        revs = searched['lock_revisions']
        shown = ', '.join(revs[:10]) + (f', … {len(revs) - 10} more' if len(revs) > 10 else '')
        capped = f' (newest {len(revs)} only)' if searched['lock_history_capped'] else ''
        parts.append(f"pytask.lock at {len(revs)} revision(s){capped} on local and remote-tracking branches and HEAD"
                     + (f" [{shown}]" if revs else ''))
        for path, count in searched['blob_histories'].items():
            parts.append(f"git history of {path} ({count} revision(s))")
    if searched['conflicted_copies_beside']:
        parts.append('conflicted copies beside ' + ', '.join(searched['conflicted_copies_beside']))
    return 'searched: ' + '; '.join(parts)


# ---------------------------------------------------------------------------
# Targets
# ---------------------------------------------------------------------------

def resolve_target(graph, target, project_root):
    """('step', name) | ('task', (task_path, names)) | ('path', path_target dict)."""
    from _repro_state import select_steps
    if '#' in target:
        names, unknown = select_steps(graph, [target])
        if unknown:
            raise ReproStateError(f'no step matches {target!r}')
        return 'step', names[0]
    try:
        names, unknown = select_steps(graph, [target])
    except ReproStateError as exc:
        if 'is a step name' not in str(exc):
            raise
        if len([s for s in graph.steps + graph.archived_steps if s.name == target]) > 1:
            raise
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
    resolver = Resolver(report, paths, cache, full_diff=full_diff, plan_name=plan_name)
    if kind == 'path':
        return _explain_path(resolver, value)
    names = [value] if kind == 'step' else value[1]
    steps, rows = [], []
    for entry in (report.entry(name) for name in names):
        step_rows = resolver.step_rows(entry)
        rows += step_rows
        steps.append(dict(entry.to_dict(), rows=step_rows))
    return {'target': target_ref(report.entry(names[0]).step) if kind == 'step' else (value[0] or '.'),
            'kind': kind, 'steps': steps, 'groups': group_rows(rows), 'searched': resolver.searched()}


def _explain_path(resolver, target) -> dict:
    node, resolved = target['node'], target['resolved']
    current = resolver.cache.path_state(absolute(resolver.paths.project_root, resolved))
    owner, readers = target['producer'], target['consumers']
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
        'target': target['path'], 'kind': 'path', 'node': node, 'current': current,
        'current_sources': resolver.sources(owner or readers[0], node, current, resolved=resolved),
        'producer': target_ref(owner) if owner else None,
        'consumers': [target_ref(s) for s in readers],
        'rows': rows, 'groups': group_rows(rows), 'searched': resolver.searched(),
    }


def format_explain(result, report) -> str:
    lines = []
    if result['kind'] == 'path':
        now = ('missing here' if result['current'] is None else
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
        lines += render_groups(result['groups'], with_step=True)
        other = [s for s in stale if not s['rows'] or s['status'] == 'failed']
        if other:
            lines.append('  status (no hash to resolve):')
            lines += [f"    {s['name']}  [{s['status']}]  {s['reason']}" for s in other]
        notes = [s for s in result['steps'] if s['status'] == 'fresh'
                 and s['reason'] not in ('up to date', 'reviewed baseline')]
        lines += [f"  note: {s['name']} fresh — {s['reason']}" for s in notes]
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
