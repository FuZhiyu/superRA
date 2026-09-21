"""Exact-state reviewed reuse and successful receipts; no engine dependency."""
from __future__ import annotations

import difflib
import getpass
import hashlib
import json
import os
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path

from _repro_state import (
    Change, HashCache, ReproStateError, absolute, dependency_state, directory_dep_nodes, node_state,
    output_nodes, read_lock, read_run_record, select_steps, spec_hash,
    spec_node_id, step_nodes, _topological,
)

LEDGER = 'repro-acceptance.json'
SNAPSHOT_LIMIT = 128 * 1024


def identity(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix='.' + path.name)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            json.dump(value, handle, sort_keys=True, indent=2)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


@contextmanager
def mutation_lock(paths):
    """Reject concurrent builds/record changes, releasing even after interruption."""
    import fcntl
    paths.state_dir.mkdir(parents=True, exist_ok=True)
    with (paths.state_dir / 'mutation.lock').open('a') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ReproStateError('another reproduction build or acceptance mutation is running') from None
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def read_json(path, default):
    if not path.exists():
        return default
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise ReproStateError(f'{path}: invalid record: {exc}') from None
    if not isinstance(value, dict):
        raise ReproStateError(f'{path}: expected a JSON object')
    return value


def read_ledger(paths):
    value = read_json(paths.project_root / LEDGER, {'version': 1, 'steps': {}})
    if value.get('version') != 1 or not isinstance(value.get('steps'), dict):
        raise ReproStateError(f'{LEDGER}: unsupported or malformed record')
    for name, record in value['steps'].items():
        if (not isinstance(record, dict)
                or not all(isinstance(record.get(key), dict) for key in ('baseline', 'state', 'reviews', 'evidence', 'upstream'))
                or not isinstance(record.get('reason'), str)
                or not isinstance(record.get('boundary_inputs'), list)
                or record.get('basis') != 'reviewed'
                or record.get('id') != identity({k: v for k, v in record.items() if k != 'id'})):
            raise ReproStateError(f'{LEDGER}: malformed acceptance for {name}')
    return value


def logical_rows(rows):
    """Committed saved-input rows key on the logical path; a resolved root is per-checkout."""
    return [{key: value for key, value in row.items() if key != 'resolved'} for row in rows]


def lock_state(entry):
    return {'deps': entry.depends_on, 'products': entry.produces} if entry else None


def current_state(graph, step, paths, cache=None, *, recorded=True):
    cache = cache or HashCache()
    deps, products = step_nodes(step, output_nodes(graph))
    deps += directory_dep_nodes(graph, step)
    entry = read_lock(paths.lock_file).get(step.name) if recorded else None
    prior = entry.depends_on if entry else {}
    state = {
        'deps': {node[0]: dependency_state(cache, paths.project_root, node, prior.get(node[0])) for node in deps},
        'products': {node[0]: node_state(cache, paths.project_root, node) for node in products},
        'outputs': {out.path.logical: cache.path_state(absolute(paths.project_root, out.path.resolved)) for out in step.outs},
    }
    state['deps'][spec_node_id(step.name)] = spec_hash(step)
    if step.kind == 'check':
        state['outputs'] = dict(state['products'])
    return state


def receipt_path(paths, name):
    return paths.state_dir / 'baselines' / f'{name}.json'


def source_snapshots(step, paths, state):
    snapshots = {}
    remaining = 1024 * 1024
    for dep in step.deps:
        path = absolute(paths.project_root, dep.resolved)
        try:
            if path.stat().st_size > min(SNAPSHOT_LIMIT, remaining):
                continue
            with path.open('rb') as handle:
                raw = handle.read(min(SNAPSHOT_LIMIT, remaining) + 1)
            if len(raw) > min(SNAPSHOT_LIMIT, remaining):
                continue
            if hashlib.sha256(raw).hexdigest() != state['deps'].get(dep.logical):
                continue
            snapshots[dep.logical] = raw.decode('utf-8')
            remaining -= len(raw)
        except (OSError, UnicodeError):
            continue
    return snapshots


def capture_receipt(graph, step, paths, before):
    state = current_state(graph, step, paths, recorded=False)
    if state['deps'] != before['deps']:
        raise ReproStateError(f'{step.name}: dependencies changed during execution; rerun')
    if any(value is None for group in state.values() for value in group.values()):
        raise ReproStateError(f'{step.name}: required input or output is missing after execution')
    receipt = {'state': state, 'snapshots': source_snapshots(step, paths, state),
               'spec': step.to_dict(), 'recorded_at': time.time(),
               'run': dict(read_run_record(paths, step.name), outcome='success')}
    from _repro_scope import boundary_inputs
    scope = getattr(graph, '_execution_names', {s.name for s in graph.steps})
    boundary = boundary_inputs(graph, scope, paths, consumers={step.name})
    old_boundary = before.get('boundary_inputs', [])
    fingerprints = lambda rows: {(r['logical'], r['resolved']): r['digest'] for r in rows}
    if fingerprints(boundary) != fingerprints(old_boundary):
        raise ReproStateError(f'{step.name}: saved inputs changed during execution; rerun')
    if any(item['digest'] is None for item in boundary):
        raise ReproStateError(f'{step.name}: saved input is missing after execution')
    receipt['boundary_inputs'] = boundary
    receipt['execution_scope'] = sorted(scope)
    receipt['id'] = identity(receipt)
    atomic_json(receipt_path(paths, step.name), receipt)
    return receipt


def baseline(step, paths, entry, *, required=True):
    if entry is None:
        if required:
            raise ReproStateError(f'{step.name}: never built')
        return {'lock': None, 'outputs': {}, 'receipt': None, 'snapshots': {}, 'spec': None, 'run': {}}
    recorded = lock_state(entry)
    receipt = read_json(receipt_path(paths, step.name), {})
    if receipt and receipt.get('id') == identity({k: v for k, v in receipt.items() if k != 'id'}):
        state = receipt.get('state', {})
        if {key: state.get(key) for key in ('deps', 'products')} == recorded:
            return {'lock': recorded, 'outputs': state['outputs'], 'receipt': receipt['id'],
                    'snapshots': receipt.get('snapshots', {}), 'spec': receipt.get('spec'), 'run': receipt.get('run', {}),
                    'boundary_inputs': receipt.get('boundary_inputs', [])}
    accepted = read_ledger(paths)['steps'].get(step.name, {}).get('baseline', {})
    if accepted.get('lock') == recorded:
        return accepted
    sidecar = any(out.sidecar for out in step.outs)
    if sidecar and required:
        raise ReproStateError(f'{step.name}: no verified output digest for sidecar baseline; rerun this step')
    return {'lock': recorded, 'outputs': {} if sidecar else dict(entry.produces), 'receipt': None, 'snapshots': {}, 'spec': None, 'run': read_run_record(paths, step.name)}


def differences(before, after):
    return [{'node': key, 'kind': 'spec' if key.endswith('::spec') else 'dependency',
             'before': before.get(key), 'after': after.get(key)}
            for key in sorted(before.keys() | after.keys()) if before.get(key) != after.get(key)]


def validate_record(graph, step, paths, record, locks, ledger, cache=None):
    """Return the reason reuse is invalid; callers already validate upstream state."""
    if not record:
        return 'no acceptance'
    if record.get('baseline', {}).get('lock') != lock_state(locks.get(step.name)):
        return 'successful baseline changed'
    if read_run_record(paths, step.name).get('outcome') in ('failed', 'running', 'pending'):
        return 'last execution did not succeed'
    # A bound producer that still holds an acceptance or a successful lock keeps
    # this record: the reviewed dep hashes below already pin its output bytes, so
    # re-accepting it is not a change here. Losing its every baseline is.
    revoked = next((name for name in record.get('upstream', {})
                    if name not in ledger['steps'] and name not in locks), None)
    if revoked:
        return f'upstream acceptance for {revoked!r} was revoked'
    cache = cache or HashCache()
    current_paths = {dep.logical: dep.resolved for dep in step.deps}
    for item in record.get('boundary_inputs', []):
        resolved = current_paths.get(item['logical'])
        if resolved is None or cache.path_state(absolute(paths.project_root, resolved)) != item['digest']:
            return 'saved input bytes changed'
    state = current_state(graph, step, paths, cache)
    if any(value is None for group in state.values() for value in group.values()):
        return 'required input or output missing'
    if state != record.get('state'):
        return 'reviewed state changed'
    return None


def supersede(paths, name):
    ledger = read_ledger(paths)
    if ledger['steps'].pop(name, None) is not None:
        atomic_json(paths.project_root / LEDGER, ledger)


def apply_to_status(report, paths, cache, ledger=None, lock=None):
    """Apply exact reviewed state, then propagate selected producer uncertainty."""
    ledger = read_ledger(paths) if ledger is None else ledger
    lock = read_lock(paths.lock_file) if lock is None else lock
    by_name = {entry.step.name: entry for entry in report.entries}
    parents = {name: [] for name in by_name}
    for src, dst, _ in report.graph.step_edges:
        if src in by_name and dst in parents and src not in parents[dst]:
            parents[dst].append(src)
    valid_graph = not any(f.severity == 'error' for f in report.graph.findings)
    for name in _topological(by_name, parents):
        entry = by_name[name]
        record = ledger['steps'].get(name)
        blocked = next((p for p in parents[name] if by_name[p].status != 'fresh'), None)
        invalid = validate_record(report.graph, entry.step, paths, record, lock, ledger, cache) if record else None
        if valid_graph and record and not invalid:
            entry.status, entry.reason, entry.acceptance = 'fresh', 'reviewed baseline', record
            entry.changes = []
            if entry.last_run is None:
                run = record['baseline'].get('run', {})
                entry.last_run, entry.duration, entry.log = run.get('ended_at'), run.get('duration'), run.get('log')
        elif record and invalid:
            state = current_state(report.graph, entry.step, paths, cache)
            entry.changes = [Change(c['node'], c['kind'], 'missing' if c['after'] is None else 'changed')
                             for c in state_differences(record['state'], state)] + [
                                 c for c in entry.changes if c.kind == 'boundary']
            if entry.status == 'fresh' or (entry.status == 'missing' and all(
                    v is not None for group in state.values() for v in group.values())):
                entry.status, entry.reason = 'stale', invalid
            if read_run_record(paths, name).get('outcome') in ('failed', 'running', 'pending'):
                entry.status, entry.reason = 'failed', 'last execution did not succeed'
        entry.local_status, entry.local_reason = entry.status, entry.reason
        if blocked and entry.status == 'fresh':
            entry.status, entry.reason = 'stale', f'upstream step {blocked!r} is {by_name[blocked].status}'


def state_differences(before, after):
    """Input/output hashes, plus distinct engine metadata such as sidecars."""
    changes = []
    for group, kind in (('deps', 'dependency'), ('outputs', 'output'), ('products', 'output')):
        for row in differences(before.get(group, {}), after[group]):
            if group == 'products':
                if any(c['node'] == row['node'] and c['before'] == row['before']
                       and c['after'] == row['after'] for c in changes):
                    continue
                row['node'] += '::product'
            row['kind'] = 'spec' if row['node'].endswith('::spec') else kind
            changes.append(row)
    return changes


def inspect_baseline(graph, step, paths):
    accepted = read_ledger(paths)['steps'].get(step.name)
    reviewed = None
    if accepted:
        diffs = [dict(row, diff=None, history='unavailable')
                 for row in state_differences(accepted['state'], current_state(graph, step, paths))]
        reviewed = {'available': True, 'basis': 'reviewed', 'receipt': None, 'diffs': diffs}
    entry = read_lock(paths.lock_file).get(step.name)
    try:
        before = baseline(step, paths, entry)
    except ReproStateError as exc:
        return reviewed or {'available': False, 'reason': str(exc), 'diffs': []}
    now = current_state(graph, step, paths)
    diffs = []
    by_logical = {d.logical: d for d in step.deps}
    for change in differences(before['lock']['deps'], now['deps']):
        row = dict(change, diff=None, history='unavailable')
        old = before.get('snapshots', {}).get(change['node'])
        dep = by_logical.get(change['node'])
        if old is not None and hashlib.sha256(old.encode()).hexdigest() == change['before'] and dep:
            try:
                with absolute(paths.project_root, dep.resolved).open('rb') as handle:
                    raw = handle.read(SNAPSHOT_LIMIT + 1)
                if len(raw) <= SNAPSHOT_LIMIT and hashlib.sha256(raw).hexdigest() == change['after']:
                    row.update(history='verified snapshot', diff=''.join(difflib.unified_diff(old.splitlines(True), raw.decode().splitlines(True), fromfile='successful/' + dep.logical, tofile='current/' + dep.logical)))
            except (OSError, UnicodeError):
                pass
        if change['kind'] == 'spec' and before['spec']:
            row.update(history='verified receipt', before_spec=before['spec'], after_spec=step.to_dict())
        diffs.append(row)
    return {'available': True, 'receipt': before['receipt'], 'diffs': diffs, 'reviewed': reviewed}


def evidence_files(paths, references):
    result = {}
    for reference in references:
        filename = reference.split('#', 1)[0]
        path = absolute(paths.project_root, filename)
        digest = HashCache().file_hash(path)
        if digest is None:
            raise ReproStateError(f'evidence is unavailable: {reference}')
        result[reference] = digest
    return result


def preview(graph, paths, targets, reason, reviews, evidence):
    if any(f.severity == 'error' for f in graph.findings):
        raise ReproStateError('invalid graph; acceptance is unavailable')
    names, unknown = select_steps(graph, targets, include_ancestors=False)
    if unknown or not names or not targets:
        raise ReproStateError('select exact step or task targets: ' + ', '.join(unknown))
    ledger = read_ledger(paths)
    original = identity(ledger)
    lock = read_lock(paths.lock_file)
    parents = {s.name: [] for s in graph.steps}
    for src, dst, _ in graph.step_edges:
        parents[dst].append(src)
    rows = []
    evidence_hashes = evidence_files(paths, evidence) if evidence else {}
    for name in _topological({s.name: s for s in graph.steps}, parents):
        if name not in names:
            continue
        step = graph.step(name)
        if read_run_record(paths, name).get('outcome') in ('failed', 'running', 'pending'):
            raise ReproStateError(f'{name}: last execution did not succeed')
        before = baseline(step, paths, lock.get(name), required=step.kind == 'check')
        state = current_state(graph, step, paths)
        if any(v is None for group in state.values() for v in group.values()):
            raise ReproStateError(f'{name}: required input or output is missing')
        if step.kind == 'check' and state['products'] != before['lock']['products']:
            raise ReproStateError(f'{name}: check stamp differs from successful baseline; run the check')
        previous_record = ledger['steps'].get(name)
        previous_state = previous_record['state'] if previous_record else {
            'deps': (before['lock'] or {}).get('deps', {}),
            'products': (before['lock'] or {}).get('products', {}), 'outputs': before['outputs']}
        changes = state_differences(previous_state, state)
        from _repro_scope import boundary_inputs
        boundary = boundary_inputs(graph, {name}, paths, consumers={name})
        previous_boundary = {item['logical']: item for item in
                             (previous_record or before).get('boundary_inputs', [])}
        for item in boundary:
            previous = previous_boundary.get(item['logical'])
            if previous and previous['digest'] != item['digest']:
                changes.append({'node': item['logical'] + '::boundary', 'kind': 'boundary',
                                'before': previous['digest'], 'after': item['digest']})
        coverage = {change['node']: reviews[change['node']] for change in changes if change['node'] in reviews}
        portable_baseline = {key: value for key, value in before.items() if key != 'snapshots'}
        if 'boundary_inputs' in portable_baseline:
            portable_baseline['boundary_inputs'] = logical_rows(portable_baseline['boundary_inputs'])
        record = {'basis': 'reviewed', 'baseline': portable_baseline, 'state': state,
                  'reason': reason, 'reviews': coverage, 'evidence': evidence_hashes,
                  'boundary_inputs': logical_rows(boundary),
                  # Only producers accepted alongside this one bind it; the rest
                  # stay saved inputs, recorded above by their actual bytes.
                  'upstream': {p: ledger['steps'][p]['id'] for p in parents[name]
                               if p in names and p in ledger['steps']}}
        # Deterministic provisional ids also bind downstream batch acceptances.
        record['id'] = identity(record)
        ledger['steps'][name] = record
        rows.append({'step': name, 'changes': changes, 'record': record,
                     'baseline_details': inspect_baseline(graph, step, paths)})
    ready = bool(reason.strip())
    result = {'steps': rows, 'ledger_before': original, 'ready': ready}
    result['token'] = identity(result)
    return result


def accept(graph, paths, targets, reason, reviews, evidence, token=None, *, dry_run=False):
    """Apply the reviewed baseline in one call; *dry_run* previews, *token* re-applies one."""
    with mutation_lock(paths):
        check_sources(graph)
        result = preview(graph, paths, targets, reason, reviews, evidence)
        if dry_run:
            return result
        if token is not None and token != result['token']:
            raise ReproStateError('preview no longer matches current state; inspect a new preview')
        if not result['ready']:
            raise ReproStateError('acceptance requires --reason describing the reviewed current results')
        # Re-read hashes and evidence immediately before the atomic write.
        check_sources(graph)
        if preview(graph, paths, targets, reason, reviews, evidence)['token'] != result['token']:
            raise ReproStateError('state changed during acceptance; inspect a new preview')
        ledger = read_ledger(paths)
        replacements = {}
        for row in result['steps']:
            record = row['record']
            record['upstream'] = {p: replacements.get(v, v) for p, v in record['upstream'].items()}
            old = record.pop('id')
            try:
                actor = getpass.getuser()
            except (KeyError, OSError):
                actor = None
            record.update(recorded_at=time.time(), actor=actor)
            record['id'] = identity(record)
            replacements[old] = record['id']
            ledger['steps'][row['step']] = record
        atomic_json(paths.project_root / LEDGER, ledger)
        return dict(result, applied=True)


def revoke(graph, paths, targets):
    names, unknown = select_steps(graph, targets, include_ancestors=False)
    with mutation_lock(paths):
        ledger = read_ledger(paths)
        names += [name for name in unknown if name in ledger['steps']]
        unknown = [name for name in unknown if name not in ledger['steps']]
        if unknown or not targets:
            raise ReproStateError('select known step, task, or stored record names: ' + ', '.join(unknown))
        removed = [name for name in names if ledger['steps'].pop(name, None)]
        atomic_json(paths.project_root / LEDGER, ledger)
    return {'revoked': removed}


def impact(graph, paths, files, scope=()):
    selected, unknown = select_steps(graph, scope, include_ancestors=False)
    if unknown:
        raise ReproStateError('unknown scope: ' + ', '.join(unknown))
    resolved = {str(absolute(paths.project_root, p).resolve()) for p in files}
    direct = []
    for step in graph.steps:
        reasons = []
        for dep in step.deps:
            path = str(absolute(paths.project_root, dep.resolved).resolve())
            if dep.logical in files or any(path == p or path.startswith(p + '/') or p.startswith(path + '/') for p in resolved):
                reasons.append({'path': dep.logical, 'origins': step.dependency_origins.get(dep.logical, [])})
        if reasons:
            direct.append({'step': step.name, 'task': step.task_path, 'reasons': reasons, 'in_scope': not scope or step.name in selected})
    affected = {r['step'] for r in direct}
    edges = []
    changed = True
    while changed:
        changed = False
        for src, dst, via in graph.step_edges:
            if src in affected:
                if (src, dst, via) not in edges:
                    edges.append((src, dst, via))
                if dst not in affected:
                    affected.add(dst)
                    changed = True
    return {'paths': list(files), 'direct': direct,
            'affected': [{'step': name, 'in_scope': not scope or name in selected} for name in sorted(affected)],
            'edges': edges, 'findings': [f.to_dict() for f in graph.findings],
            'prediction': 'conservative invalidation; unchanged output bytes can stop a cascade'}


def source_signature(root, cache=None):
    """Graph declarations only: human prose and active status rollups are independent."""
    from _task_io import VALID_STATUSES, iter_task_markdown_files, parse_body_sections, parse_task
    from _repro import extract_repro_block, load_project_config, parse_yaml_subset
    cache = {} if cache is None else cache
    hashes = cache.setdefault('_hashes', HashCache())
    result = {}
    for path in iter_task_markdown_files(root) + [root / 'config.yaml']:
        key = str(path.relative_to(root))
        digest = hashes.file_hash(path)
        cached = cache.get(key)
        if cached and cached[0] == digest:
            result[key] = cached[1]
            continue
        try:
            if key == 'config.yaml':
                declaration = load_project_config(root)
            else:
                task = parse_task(path, root)
                section = parse_body_sections(task.body).get('Reproduction')
                declaration = {
                    'title_valid': bool(task.title),
                    'status': ('archived' if task.status == 'archived' else
                               'active' if task.status in VALID_STATUSES else task.status),
                    'depends_on': sorted(map(str, task.depends_on)),
                    'reproduction': (parse_yaml_subset(extract_repro_block(section))
                                     if section is not None else None),
                }
        except (OSError, ValueError) as exc:
            declaration = {'error': str(exc), 'digest': digest}
        value = identity(declaration)
        cache[key] = (digest, value)
        result[key] = value
    return result


def bind_sources(graph, root, signature=None):
    graph._acceptance_sources = (root, signature if signature is not None else source_signature(root), {})


def check_sources(graph):
    build_guard = getattr(graph, '_build_guard', None)
    if build_guard is not None:
        build_guard.check()
        return
    guard = getattr(graph, '_acceptance_sources', None)
    if guard is not None and source_signature(guard[0], guard[2]) != guard[1]:
        raise ReproStateError('task declarations or configuration changed during this operation; retry')
