"""Where a changed node's recorded and current bytes came from, for `repro explain`.

Sources: the local receipt, the acceptance ledger, the committed lock history
across local branches (parsed once per revision into `.superra-repro/lock-index/`),
the git blob history of tracked files, and Dropbox conflicted copies beside a
file. Only changed nodes are resolved; git is optional. Stdlib only.
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
DIFF_LINES = 20
CHECK_ELSEWHERE = 'passed at these inputs in'

# cause -> (plain-language cause, likely reading). The command is per row.
CAUSES = {
    'missing': ('missing on disk', 'nothing to compare; the file is absent here'),
    'failed': ('last execution failed', 'the log says where the last run died'),
    'upstream': ('upstream step not fresh', 'this step has no change of its own'),
    'definition-changed': ('step definition changed', 'the declaration, a ${VAR}, or a runner template moved'),
    'reviewed-replaced': ('reviewed bytes replaced', 'the bytes differ from the reviewed acceptance'),
    'dependency-edited': ('dependency edited in commit {rev}', 'the step last ran on the version before this edit'),
    'uncommitted-edit': ('dependency edited, not committed', 'the working copy differs from every recent commit'),
    'conflicted-copy': ('recorded bytes in a Dropbox conflicted copy', 'Dropbox set the recorded build aside beside the file'),
    'recorded-from-branch': ('recorded build from another branch', 'the lock records a build made on a merged branch; that build\'s bytes are not here'),
    'older-build': ('older build synced here', 'the newer build recorded in the lock has not synced here yet'),
    'current-from-branch': ('current bytes from another branch', 'the file holds a build recorded on a branch HEAD does not contain'),
    'local-build': ('built here; lock records another build', 'this checkout built it, then the lock took another build'),
    'check-elsewhere': ('check passed elsewhere, not run here', 'its lock entry matches the current inputs; the stamp is local'),
    'no-known-source': ('no known source', 'the current bytes match no recorded state'),
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
_BATCH_HEADER = re.compile(rb'^[0-9a-f]{40,64} \w+ (\d+)$')


class Git:
    def __init__(self, root: Path):
        self.root = Path(root)
        top = self.text('rev-parse', '--show-toplevel')
        self.ok = bool(top)

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

    def blobs(self, specs: list[str]) -> dict[str, bytes | None]:
        """`rev:./path` -> blob bytes (None when absent), in one `cat-file --batch`."""
        if not specs:
            return {}
        out = self.raw('cat-file', '--batch', stdin=('\n'.join(specs) + '\n').encode())
        result: dict[str, bytes | None] = {spec: None for spec in specs}
        if out is None:
            return result
        pos = 0
        for spec in specs:
            end = out.find(b'\n', pos)
            if end < 0:
                break
            match = _BATCH_HEADER.match(out[pos:end])
            pos = end + 1
            if match:
                size = int(match.group(1))
                result[spec] = out[pos:pos + size]
                pos += size + 1
        return result


# ---------------------------------------------------------------------------
# Lock history
# ---------------------------------------------------------------------------

class LockHistory:
    """Every committed `pytask.lock` on local branches, indexed by (node, hash)."""

    def __init__(self, paths, git: Git):
        self.paths, self.git = paths, git
        self.revs: list[dict] = []
        self.capped = False
        self.branches: list[str] = []
        self.head_branch = None
        self.on_head: set[str] = set()
        self.first_parent: set[str] = set()
        self.working_committed = True
        self.entries: dict[str, dict] = {}
        self.index: dict[str, dict[str, list[str]]] = {}
        self._merges: dict[str, dict | None] = {}
        if not git.ok or tomllib is None:
            return
        spec = './' + paths.lock_file.name
        revs = git.revs(f'--max-count={LOCK_REV_CAP + 1}', '--full-history', '--branches', 'HEAD', '--', spec)
        self.capped = len(revs) > LOCK_REV_CAP
        self.revs = revs[:LOCK_REV_CAP]
        self.by_sha = {r['sha']: r for r in self.revs}
        self.branches = (git.text('for-each-ref', '--format=%(refname:short)', 'refs/heads') or '').split()
        self.head_branch = git.text('symbolic-ref', '--short', '-q', 'HEAD') or 'detached'
        self.on_head = set((git.text('rev-list', 'HEAD') or '').split())
        self.first_parent = set((git.text('rev-list', '--first-parent', 'HEAD') or '').split())
        head_blob = git.text('rev-parse', f'HEAD:{spec}')
        work_blob = git.text('hash-object', '--', spec) if paths.lock_file.is_file() else None
        self.working_committed = head_blob == work_blob
        self._load(spec)

    def _load(self, spec):
        cache_dir = self.paths.state_dir / 'lock-index'
        missing = []
        for rev in self.revs:
            path = cache_dir / f"{rev['sha']}.json"
            try:
                self.entries[rev['sha']] = json.loads(path.read_text(encoding='utf-8'))
            except (OSError, ValueError):
                missing.append(rev['sha'])
        blobs = self.git.blobs([f'{sha}:{spec}' for sha in missing])
        for sha in missing:
            raw = blobs.get(f'{sha}:{spec}')
            try:
                document = tomllib.loads(raw.decode('utf-8')) if raw else {}
            except (UnicodeError, ValueError):
                document = {}
            parsed = {item['id']: {'deps': dict(item.get('depends_on') or {}),
                                   'products': dict(item.get('produces') or {})}
                      for item in document.get('task', []) or []
                      if isinstance(item, dict) and isinstance(item.get('id'), str)}
            self.entries[sha] = parsed
            if self.paths.state_dir.is_dir():  # a revision never changes, so neither does its entry
                from _repro_acceptance import atomic_json
                try:
                    atomic_json(cache_dir / f'{sha}.json', parsed)
                except OSError:
                    pass
        for rev in self.revs:
            for groups in self.entries[rev['sha']].values():
                for group in groups.values():
                    for node, value in group.items():
                        shas = self.index.setdefault(node, {}).setdefault(value, [])
                        if not shas or shas[-1] != rev['sha']:
                            shas.append(rev['sha'])

    def matches(self, node: str, value: str) -> list[str]:
        """Revisions whose lock records *value* for *node*, newest first."""
        return self.index.get(node, {}).get(value, [])

    def introduced(self, shas: list[str]) -> str | None:
        """The oldest revision on HEAD among *shas*, else the oldest anywhere."""
        head = [s for s in shas if s in self.on_head]
        return (head or shas or [None])[-1]

    def step_entry_rev(self, name: str, entry) -> str | None:
        want = {'deps': entry.depends_on, 'products': entry.produces}
        return self.introduced([r['sha'] for r in self.revs if self.entries[r['sha']].get(name) == want])

    def merge_into_head(self, sha: str) -> dict | None:
        """The oldest first-parent commit of HEAD that descends from *sha*."""
        if sha not in self._merges:
            descendants = (self.git.text('rev-list', '--ancestry-path', f'{sha}..HEAD') or '').split()
            merge = next((c for c in reversed(descendants) if c in self.first_parent), None)
            found = self.git.revs('-1', merge) if merge else []
            self._merges[sha] = found[0] if found else None
        return self._merges[sha]

    def containing_branches(self, sha: str) -> list[str]:
        return (self.git.text('branch', '--contains', sha, '--format=%(refname:short)') or '').split()

    def describe(self, sha: str) -> dict:
        rev = dict(self.by_sha[sha])
        if sha in self.on_head:
            if sha not in self.first_parent:
                merge = self.merge_into_head(sha)
                rev['merge'] = merge['rev'] if merge else None
        else:
            rev['branches'] = self.containing_branches(sha)
        return rev


def check_elsewhere_reason(paths, name, entry, memo) -> str:
    """Status reason for a check whose lock entry matches its inputs but has no local stamp."""
    if 'history' not in memo:
        memo['history'] = LockHistory(paths, Git(paths.project_root))
    history = memo['history']
    sha = history.step_entry_rev(name, entry) if history.revs else None
    where = f"lock {history.by_sha[sha]['rev']}" if sha else 'the working lock'
    return f'{CHECK_ELSEWHERE} {where}; not run here'


# ---------------------------------------------------------------------------
# Resolver
# ---------------------------------------------------------------------------

class Resolver:
    def __init__(self, report, paths, cache, *, full_diff=False):
        from _repro_acceptance import read_ledger
        from _repro_state import read_lock
        self.report, self.graph, self.paths, self.cache = report, report.graph, paths, cache
        self.full_diff = full_diff
        self.git = Git(paths.project_root)
        self.history = LockHistory(paths, self.git)
        self.lock = read_lock(paths.lock_file)
        self.ledger = read_ledger(paths)['steps']
        self.blob_histories: dict[str, list[tuple[dict, str]]] = {}
        self.copies_searched: list[str] = []
        self._receipts: dict[str, dict] = {}

    # -- recorded evidence --------------------------------------------------

    def receipt(self, name) -> dict:
        if name not in self._receipts:
            from _repro_acceptance import identity, read_json, receipt_path
            value = read_json(receipt_path(self.paths, name), {})
            ok = value and value.get('id') == identity({k: v for k, v in value.items() if k != 'id'})
            self._receipts[name] = value if ok else {}
        return self._receipts[name]

    def inside(self, resolved) -> Path | None:
        path = absolute(self.paths.project_root, resolved)
        try:
            path.resolve().relative_to(self.paths.project_root.resolve())
        except (OSError, ValueError):
            return None  # never hash a file outside this checkout
        return path

    def blob_history(self, resolved) -> list[tuple[dict, str]]:
        """(revision, sha256 of its blob) newest first, for a tracked file."""
        if resolved in self.blob_histories:
            return self.blob_histories[resolved]
        rows = []
        if self.git.ok and self.inside(resolved) is not None and not resolved.startswith(STATE_DIRNAME + '/'):
            spec = './' + resolved
            revs = self.git.revs(f'-n{BLOB_DEPTH}', '--branches', 'HEAD', '--', spec)
            blobs = self.git.blobs([f"{r['sha']}:{spec}" for r in revs])
            for rev in revs:
                raw = blobs.get(f"{rev['sha']}:{spec}")
                if raw is not None:
                    rows.append((rev, hashlib.sha256(raw).hexdigest()))
        self.blob_histories[resolved] = rows
        return rows

    def conflicted_copies(self, resolved) -> list[Path]:
        path = self.inside(resolved)
        if path is None or not path.parent.is_dir() or resolved.startswith(STATE_DIRNAME + '/'):
            return []
        self.copies_searched.append(resolved)
        pattern = f"{glob.escape(path.stem)} (*conflicted copy*){glob.escape(path.suffix)}"
        return sorted(path.parent.glob(pattern))

    def sources(self, step, node, value, *, resolved=None, recorded_side=False) -> list[dict]:
        """Every known state that holds *value* for *node*, most specific first."""
        if value is None:
            return []
        found = []
        if resolved and not value.startswith(('dir:', 'saved-input:')) and '::' not in node:
            match = next((rev for rev, digest in self.blob_history(resolved) if digest == value), None)
            if match:
                found.append(dict(source='git', **match))
        shas = self.history.matches(node, value)
        if shas:
            sha = self.history.introduced(shas)
            relation = ('working' if (self.lock.get(step.name) and value in (
                self.lock[step.name].depends_on.get(node), self.lock[step.name].produces.get(node)))
                else 'older' if sha in self.history.on_head else 'other-branch')
            found.append(dict(source='lock', relation=relation, **self.history.describe(sha)))
        elif recorded_side and not self.history.working_committed:
            found.append({'source': 'working-lock'})
        receipt = self.receipt(step.name)
        if any(group.get(node) == value for group in receipt.get('state', {}).values()):
            run = receipt.get('run', {})
            found.append({'source': 'receipt', 'at': run.get('ended_at') or receipt.get('recorded_at')})
        record = self.ledger.get(step.name)
        if record and any(group.get(node) == value for group in record.get('state', {}).values()):
            found.append({'source': 'acceptance', 'actor': record.get('actor'), 'at': record.get('recorded_at')})
        if recorded_side and resolved and not value.startswith(('dir:', 'saved-input:')):
            for copy in self.conflicted_copies(resolved):
                if self.cache.file_hash(copy) == value:
                    found.append({'source': 'conflicted-copy',
                                  'path': str(copy.relative_to(self.paths.project_root))})
        return found

    # -- rows ---------------------------------------------------------------

    def step_rows(self, entry) -> list[dict]:
        step = entry.step
        if entry.status == 'fresh':
            return []
        rows = []
        invalid = getattr(entry, 'acceptance_invalid', None)
        record = self.ledger.get(step.name)
        if record and invalid:
            from _repro_acceptance import current_state, state_differences
            state = current_state(self.graph, step, self.paths, self.cache)
            resolved = self._resolved_paths(step)
            for diff in state_differences(record['state'], state):
                node = diff['node'].removesuffix('::product')
                rows.append(self.row(step, node, diff['kind'], diff['before'], diff['after'],
                                     resolved.get(node), reviewed=True))
        else:
            rows += self._lock_rows(entry)
        if entry.status == 'failed':
            log = entry.log or self.paths.log_ref(step.name)
            rows.append(self._fact(step, 'failed', f'log {log}', f'tail -n 40 {shlex.quote(log)}'))
        if not rows and entry.status == 'stale':
            parent = next((src for src, dst, _ in self.graph.step_edges if dst == step.name
                           and self.report.entry(src) and self.report.entry(src).status != 'fresh'), None)
            if parent:
                ref = target_ref(self.graph.step(parent))
                rows.append(self._fact(step, 'upstream', entry.reason, f'superra repro explain {shlex.quote(ref)}'))
        return rows

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
        rows = []
        changes = entry.changes
        stamp = stamp_ref(step.name)
        if step.kind == 'check' and lock and any(c.node == stamp for c in changes):
            if entry.reason.startswith(CHECK_ELSEWHERE):
                sha = self.history.step_entry_rev(step.name, lock) if self.history.revs else None
                where = label([dict(source='lock', relation='working', **self.history.by_sha[sha])]) if sha else 'the working lock'
                return [self._fact(step, 'check-elsewhere', f'passed at {where}',
                                   f'superra repro build {shlex.quote(target_ref(step))}', node=stamp)]
            # A missing stamp hides the inputs that moved since the lock's run.
            from _repro_state import _changed_nodes
            changes = _changed_nodes(step, lock, self.paths, self.cache, deps, [])
        for change in changes:
            node, kind = change.node, change.kind
            if kind == 'spec':
                recorded = lock.depends_on.get(node) if lock else None
                rows.append(self.row(step, node, 'spec', recorded, spec_hash(step), None, change=change.change))
                continue
            if kind == 'boundary':
                recorded = next((item['digest'] for item in self.receipt(step.name).get('boundary_inputs', [])
                                 if item['logical'] == node), None)
                dep = next((d for d in step.deps if d.logical == node), None)
                current = self.cache.path_state(absolute(root, dep.resolved)) if dep else None
                rows.append(self.row(step, node, 'boundary', recorded, current, dep and dep.resolved, change=change.change))
                continue
            if kind == 'dependency':
                spec = dep_nodes.get(node)
                recorded = lock.depends_on.get(node) if lock else None
                current = dependency_state(self.cache, root, spec, recorded) if spec else None
            else:
                spec = out_nodes.get(node)
                recorded = lock.produces.get(node) if lock else None
                current = node_state(self.cache, root, spec) if spec else None
            rows.append(self.row(step, node, kind, recorded, current, spec and spec[1], change=change.change))
        return rows

    def _fact(self, step, cause, evidence, command, node=None) -> dict:
        text, reading = CAUSES[cause]
        return dict(step=step.name, task=step.task_path, node=node, kind=cause, change=None,
                    recorded=None, current=None, recorded_sources=[], current_sources=[],
                    cause=cause, cause_text=text, reading=reading, evidence=evidence, command=command,
                    diffstat=None, diff=None)

    def row(self, step, node, kind, recorded, current, resolved, *, reviewed=False, change=None) -> dict:
        rec = self.sources(step, node, recorded, resolved=resolved, recorded_side=True)
        if reviewed:
            record = self.ledger[step.name]
            rec = [s for s in rec if s['source'] != 'acceptance']
            rec.insert(0, {'source': 'acceptance', 'actor': record.get('actor'), 'at': record.get('recorded_at')})
        cur = self.sources(step, node, current, resolved=resolved)
        row = dict(step=step.name, task=step.task_path, node=node, kind=kind,
                   change=change or ('missing' if current is None else 'changed'),
                   recorded=recorded, current=current, recorded_sources=rec, current_sources=cur,
                   diffstat=None, diff=None)
        cause, rev = self._cause(row, kind, resolved, reviewed)
        text, reading = CAUSES[cause]
        row.update(cause=cause, cause_text=text.format(rev=rev), reading=reading)
        row['evidence'] = self._evidence(row)
        row['command'] = self._command(step, row, resolved)
        return row

    def _cause(self, row, kind, resolved, reviewed):
        first = lambda sources, name: next((s for s in sources if s['source'] == name), None)
        rec, cur = row['recorded_sources'], row['current_sources']
        rec_lock, cur_lock = first(rec, 'lock'), first(cur, 'lock')
        if row['current'] is None:
            return ('recorded-from-branch' if rec_lock and rec_lock.get('merge') else 'missing'), None
        if kind == 'spec':
            return 'definition-changed', None
        if reviewed:
            return 'reviewed-replaced', None
        if row['recorded'] is None:
            return 'definition-changed', None
        rec_git, cur_git = first(rec, 'git'), first(cur, 'git')
        snapshot = self.receipt(row['step']).get('snapshots', {}).get(row['node'])
        if not rec_git and snapshot is not None and resolved and kind == 'dependency' \
                and hashlib.sha256(snapshot.encode()).hexdigest() == row['recorded']:
            self._snapshot_diff(row, resolved, snapshot)
            if row['diff'] is not None:
                return 'uncommitted-edit', None
        if rec_git and resolved:
            self._diff(row, resolved, rec_git['rev'], cur_git and cur_git['rev'])
            if cur_git:
                return 'dependency-edited', cur_git['rev']
            return 'uncommitted-edit', None
        if first(rec, 'conflicted-copy'):
            return 'conflicted-copy', None
        if rec_lock and rec_lock.get('merge'):
            return 'recorded-from-branch', None
        if cur_lock and cur_lock['relation'] == 'older':
            return 'older-build', None
        if cur_lock and cur_lock['relation'] == 'other-branch':
            return 'current-from-branch', None
        if first(cur, 'receipt'):
            return 'local-build', None
        return 'no-known-source', None

    def _diff(self, row, resolved, old, new):
        spec = './' + resolved
        revs = [old] + ([new] if new else [])
        stat = self.git.text('diff', '--shortstat', *revs, '--', spec)
        diff = self.git.text('diff', *revs, '--', spec) or ''
        lines = diff.splitlines()
        hunk = next((i for i, line in enumerate(lines) if line.startswith('@@')), 0)
        lines = lines[hunk:]  # the row already names the path and both revisions
        row['diffstat'] = stat or None
        row['diff_lines'] = len(lines)
        row['diff'] = '\n'.join(lines if self.full_diff else lines[:DIFF_LINES]) or None

    def _snapshot_diff(self, row, resolved, snapshot):
        import difflib
        try:
            now = absolute(self.paths.project_root, resolved).read_text(encoding='utf-8')
        except (OSError, UnicodeError):
            return
        lines = [line.rstrip('\n') for line in difflib.unified_diff(
            snapshot.splitlines(True), now.splitlines(True), n=3)][2:]
        row['diff_lines'] = len(lines)
        row['diff'] = '\n'.join(lines if self.full_diff else lines[:DIFF_LINES]) or None

    def _evidence(self, row) -> str:
        if row['cause'] == 'uncommitted-edit' and not any(s['source'] == 'git' for s in row['recorded_sources']):
            return 'snapshot from the build here → working copy'
        if row['diffstat'] is not None or (row['cause'] in ('dependency-edited', 'uncommitted-edit')):
            rec = next(s for s in row['recorded_sources'] if s['source'] == 'git')
            cur = next((s for s in row['current_sources'] if s['source'] == 'git'), None)
            text = f"git {rec['rev']} → {cur['rev'] if cur else 'working copy'}"
            return text + (f", {row['diffstat']}" if row['diffstat'] else '')
        prefer = ['conflicted-copy'] if row['cause'] == 'conflicted-copy' else []
        current = 'missing here' if row['current'] is None else f"current {label(row['current_sources'])}"
        return f"recorded {label(row['recorded_sources'], prefer)}; {current}"

    def _command(self, step, row, resolved) -> str:
        ref = shlex.quote(target_ref(step))
        cause = row['cause']
        git_rev = lambda side: next((s['rev'] for s in row[side] if s['source'] == 'git'), None)
        if cause == 'dependency-edited':
            return f"git diff {git_rev('recorded_sources')} {git_rev('current_sources')} -- {shlex.quote(resolved)}"
        if cause == 'uncommitted-edit' and not git_rev('recorded_sources'):
            return f'superra repro explain {ref} --diff'
        if cause == 'uncommitted-edit':
            return f"git diff {git_rev('recorded_sources')} -- {shlex.quote(resolved)}"
        if cause == 'definition-changed':
            plan = self.graph_root_name()
            task_md = f"{plan}/{step.task_path + '/' if step.task_path else ''}task.md"
            rev = next((s['rev'] for s in row['recorded_sources'] if s['source'] == 'lock'), None)
            return f"git diff {rev + ' ' if rev else ''}-- {shlex.quote(task_md)} {plan}/config.yaml"
        if cause == 'reviewed-replaced':
            return f'superra repro accept {ref} --dry-run'
        if cause == 'conflicted-copy':
            copy = next(s['path'] for s in row['recorded_sources'] if s['source'] == 'conflicted-copy')
            return f'ls -l {shlex.quote(resolved)} {shlex.quote(copy)}'
        if cause == 'older-build' or (cause == 'missing' and row['kind'] == 'dependency'
                                      and resolved not in self.graph.producers):
            return f'superra repro status {ref}'
        return f'superra repro build {ref}'

    def graph_root_name(self) -> str:
        return getattr(self, '_plan_name', 'superRA')

    def searched(self) -> dict:
        history = self.history
        return {
            'receipts': str(self.paths.state_dir.relative_to(self.paths.project_root) / 'baselines'),
            'ledger': 'repro-acceptance.json',
            'lock_revisions': [r['rev'] for r in history.revs],
            'lock_history_capped': history.capped,
            'branches': history.branches,
            'head_branch': history.head_branch,
            'git_available': self.git.ok,
            'blob_histories': {path: len(rows) for path, rows in self.blob_histories.items() if rows},
            'conflicted_copies_beside': sorted(set(self.copies_searched)),
        }


def label(sources, prefer=()) -> str:
    ordered = sorted(sources, key=lambda s: (s['source'] not in prefer))
    if not ordered:
        return 'no known source'
    s = ordered[0]
    if s['source'] == 'lock':
        text = f"{'superseded ' if s['relation'] == 'older' else ''}lock {s['rev']} ({s['author']}, {s['date']})"
        if s.get('merge'):
            text += f" via merge {s['merge']}"
        if s['relation'] == 'other-branch':
            text += f" on {', '.join(s.get('branches') or ['an unnamed ref'])}"
        return text
    if s['source'] == 'git':
        return f"git {s['rev']}"
    if s['source'] == 'working-lock':
        return 'working lock (uncommitted)'
    if s['source'] == 'receipt':
        return f"built here {_stamp(s['at'])}"
    if s['source'] == 'acceptance':
        return f"reviewed {_stamp(s['at'])}"
    return f"conflicted copy {s['path']}"


# ---------------------------------------------------------------------------
# Grouping and rendering
# ---------------------------------------------------------------------------

_STEP_COMMAND = re.compile(r"^(superra repro \w+) (\S+)((?: --\S+)*)$")


def group_rows(rows) -> list[dict]:
    """Rows sharing a cause and command collapse; step-target commands merge their targets."""
    groups: dict[tuple, dict] = {}
    for row in rows:
        match = _STEP_COMMAND.match(row['command'])
        key = (row['cause_text'], match.group(1) + match.group(3) if match else row['command'])
        group = groups.setdefault(key, dict(cause=row['cause'], text=row['cause_text'], reading=row['reading'],
                                            steps=[], rows=[], targets=[], command=row['command']))
        group['rows'].append(row)
        if row['step'] not in group['steps']:
            group['steps'].append(row['step'])
        if match and match.group(2) not in group['targets']:
            group['targets'].append(match.group(2))
            group['command'] = f"{match.group(1)} {' '.join(group['targets'])}{match.group(3)}"
    for group in groups.values():
        del group['targets']
    return list(groups.values())


def _row_line(row, with_step) -> list[str]:
    who = f"{row['step']}  " if with_step else ''
    if row['recorded_sources'] or row['current_sources'] or row['recorded'] or row['current']:
        head = f"    {who}{row['kind']:<10} {row['node']}  {short(row['recorded'])} → {short(row['current'])}  {row['evidence']}"
    else:
        head = f"    {who}{row['evidence']}"
    lines = [head]
    if row.get('diff'):
        lines += ['      ' + line for line in row['diff'].splitlines()]
        hidden = row.get('diff_lines', 0) - len(row['diff'].splitlines())
        if hidden > 0:
            lines.append(f'      … {hidden} more line(s); --diff shows all')
    return lines


def render_groups(groups, *, with_step) -> list[str]:
    lines = []
    for group in groups:
        lines.append(f"  {group['text']} — {group['reading']}")
        shown = set()
        for row in group['rows']:
            diff = (row['node'], row['diff'])
            lines += _row_line(row if diff not in shown else dict(row, diff=None), with_step)
            shown.add(diff)
        lines.append(f"    next: {group['command']}")
    return lines


def _names(items, noun, limit=5) -> str:
    if len(items) <= limit:
        return f"{noun} {', '.join(items) or '(none)'}"
    return f"{len(items)} {noun} ({', '.join(items[:limit])}, …)"


def render_searched(searched) -> str:
    parts = [f"receipts in {searched['receipts']}", f"acceptance ledger {searched['ledger']}"]
    if not searched['git_available']:
        parts.append('no git history (not a git checkout)')
    else:
        revs = searched['lock_revisions']
        shown = ', '.join(revs[:10]) + (f', … {len(revs) - 10} more' if len(revs) > 10 else '')
        capped = f' (newest {len(revs)} only)' if searched['lock_history_capped'] else ''
        parts.append(f"pytask.lock at {len(revs)} revision(s){capped}"
                     + (f" [{shown}]" if revs else '')
                     + f" on {_names(searched['branches'], 'local branch(es)')}; HEAD is {searched['head_branch']}")
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
        same = [s for s in graph.steps + graph.archived_steps if s.name == target]
        if len(same) > 1:
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
    candidate = Path(target)
    if candidate.is_absolute():
        try:
            text = str(candidate.resolve().relative_to(Path(project_root).resolve()))
        except (OSError, ValueError):
            return None
    text = text.removeprefix('./').rstrip('/')
    producer = consumers = None
    node = resolved = None
    for step in graph.steps:
        for out in step.outs:
            if text in (out.path.logical, out.path.resolved):
                producer, node, resolved = step, out.path.logical, (out.sidecar or out.path).resolved
    consumers = [s for s in graph.steps if any(text in (d.logical, d.resolved) for d in s.deps)]
    if producer is None and not consumers:
        return None
    if node is None:
        dep = next(d for d in consumers[0].deps if text in (d.logical, d.resolved))
        node, resolved = dep.logical, dep.resolved
        owner = output_nodes(graph).get(dep.resolved)
        if owner:
            node, resolved = owner[0], owner[1]
    return dict(path=text, node=node, resolved=resolved, producer=producer, consumers=consumers)


def explain(report, paths, cache, kind, value, *, full_diff=False, plan_name='superRA') -> dict:
    resolver = Resolver(report, paths, cache, full_diff=full_diff)
    resolver._plan_name = plan_name
    if kind == 'path':
        return _explain_path(resolver, value)
    names = [value] if kind == 'step' else value[1]
    entries = [report.entry(name) for name in names]
    steps = []
    rows = []
    for entry in entries:
        step_rows = resolver.step_rows(entry)
        rows += step_rows
        steps.append(dict(entry.to_dict(), rows=step_rows))
    result = {'target': target_ref(entries[0].step) if kind == 'step' else (value[0] or '.'),
              'kind': kind, 'steps': steps, 'groups': group_rows(rows)}
    result['searched'] = resolver.searched()
    return result


def _explain_path(resolver, target) -> dict:
    root = resolver.paths.project_root
    node, resolved = target['node'], target['resolved']
    current = resolver.cache.path_state(absolute(root, resolved))
    owner = target['producer']
    readers = target['consumers']
    rows, seen = [], set()
    for step in ([owner] if owner else []) + readers:
        lock = resolver.lock.get(step.name)
        recorded = (lock.produces.get(node) or lock.depends_on.get(node)) if lock else None
        if recorded is None or recorded == current or recorded in seen:
            continue
        seen.add(recorded)
        kind = 'output' if step is owner else 'dependency'
        rows.append(resolver.row(step, node, kind, recorded, current, resolved))
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
               f"now {short(result['current'])}  " + (f"matches {label(result['current_sources'])}"
                                                      if result['current_sources'] else 'matches no recorded state'))
        lines.append(f"{result['target']}  {now}")
        lines.append(f"  produced by {result['producer'] or '(no step; external input)'}")
        lines.append(f"  read by {', '.join(result['consumers']) or '(no step)'}")
        if not result['rows']:
            lines.append('  every lock entry for it matches the current bytes' if result['current']
                         else '  no lock entry records it')
        lines += render_groups(result['groups'], with_step=True)
    elif result['kind'] == 'step':
        step = result['steps'][0]
        entry = report.entry(step['name'])
        lines.append(f"{step['name']}  [{step['status']}]  {step['reason']}")
        lines += _step_header(entry, report)
        if not result['groups']:
            lines.append('  nothing changed since the recorded build or acceptance')
        lines += render_groups(result['groups'], with_step=False)
    else:
        stale = [s for s in result['steps'] if s['status'] != 'fresh']
        lines.append(f"{result['target']}: {len(stale)} of {len(result['steps'])} step(s) not fresh")
        lines += render_groups(result['groups'], with_step=True)
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
