"""Real-engine reviewed reuse, precise scopes, and trustworthy evidence."""
import json
import shutil

import pytest

from test_repro_runner import CHAIN, project, _use_a_sidecar  # noqa: F401
from _repro_acceptance import (
    accept, preview, read_ledger, receipt_path,
    ReproStateError, LEDGER,
)
from _repro_state import compute_status, read_lock, read_run_record


def review(project, names=('01-a#build-a',), *, apply=True):
    first = preview(project.graph(), project.paths, names, '', {})
    reviews = {change['node']: 'Comment only; execution and output are unchanged.'
               for row in first['steps'] for change in row['changes']}
    args = (project.graph(), project.paths, names, 'Harmless source changes', reviews)
    # One shot is the default; `apply=False` returns the arguments and a dry run.
    return accept(*args) if apply else (args, accept(*args, dry_run=True))


def test_accepted_build_skips_producer_but_runs_independently_dirty_descendant(project):
    assert project.run('build', *CHAIN) == 0
    before = project.run_times()
    lock = read_lock(project.paths.lock_file)['build-a']
    project.write('Code/a.sh', project.read('Code/a.sh') + '# harmless\n')
    project.write('Code/b.sh', project.read('Code/b.sh') + '# independently changed\n')
    review(project)
    assert project.states()['build-a'] == 'fresh'
    assert project.states()['build-b'] == 'stale'
    assert project.run('build', *CHAIN) == 0
    after = project.run_times()
    assert before['build-a'] == after['build-a']
    assert before['build-b'] < after['build-b']
    assert read_lock(project.paths.lock_file)['build-a'] == lock
    assert project.states()['check-b'] == 'fresh'
    assert project.run('build', *CHAIN) == 0
    assert project.run_times() == after


@pytest.mark.parametrize('change', ['dep', 'spec', 'output'])
def test_later_changes_invalidate_acceptance(project, change):
    assert project.run('build', *CHAIN) == 0
    project.write('Code/a.sh', project.read('Code/a.sh') + '# harmless\n')
    review(project)
    if change == 'dep':
        project.write('Code/a.sh', project.read('Code/a.sh') + '# later\n')
    elif change == 'spec':
        project.write('superRA/01-a/task.md', project.read('superRA/01-a/task.md').replace('sh Code/a.sh', 'sh Code/a.sh ' + '&& true'))
    else:
        project.write('output/a.txt', 'different\n')
    assert project.states()['build-a'] != 'fresh'


def test_sidecar_acceptance_verifies_actual_output_bytes(project):
    _use_a_sidecar(project)
    assert project.run('build', *CHAIN) == 0
    project.write('Code/a.sh', project.read('Code/a.sh') + '# harmless\n')
    review(project)
    project.write('output/a.txt', 'corrupted without sidecar change')
    assert project.states()['build-a'] == 'stale'
    args, proposal = review(project, apply=False)
    assert any(row['kind'] == 'output' for row in proposal['steps'][0]['changes'])
    accept(*args)
    assert project.states()['build-a'] == 'fresh'


def test_reason_required(project):
    with pytest.raises(ReproStateError, match='required input or output is missing'):
        review(project)
    assert project.run('build', *CHAIN) == 0
    project.write('Code/a.sh', project.read('Code/a.sh') + '# harmless\n')
    args = (project.graph(), project.paths, ['01-a#build-a'], '', {})
    proposal = accept(*args, dry_run=True)
    assert not proposal['ready']
    with pytest.raises(ReproStateError, match='requires --reason'):
        accept(*args)
    args = (project.graph(), project.paths, ['01-a#build-a'], 'Reviewed', {})
    proposal = accept(*args, dry_run=True)
    assert proposal['ready']
    accept(*args)
    assert project.states()['build-a'] == 'fresh'


def test_failure_revokes_before_execution_even_after_cache_loss(project):
    assert project.run('build', *CHAIN) == 0
    original = project.read('Code/a.sh')
    project.write('Code/a.sh', original + '# harmless\n')
    review(project)
    project.write('Code/a.sh', 'exit 1\n')
    assert project.run('build', '01-a#build-a', '--force') != 0
    assert 'build-a' not in read_ledger(project.paths)['steps']
    project.write('Code/a.sh', original + '# harmless\n')
    shutil.rmtree(project.paths.state_dir)
    assert project.states()['build-a'] == 'stale'


def test_invalid_graph_never_accepts_or_builds(project):
    assert project.run('build', *CHAIN) == 0
    project.write('Code/a.sh', project.read('Code/a.sh') + '# harmless\n')
    review(project)
    project.write('superRA/01-a/task.md', project.read('superRA/01-a/task.md').replace('steps:', 'bogus: 1\nsteps:'))
    assert not project.status(*CHAIN).ok
    assert project.run('build', '01-a#build-a') == 1
    with pytest.raises(ReproStateError, match='invalid graph'):
        review(project)


def test_cli_preview_accept_explain_revoke_and_scope(project, capsys):
    assert project.run('build', *CHAIN) == 0
    capsys.readouterr()
    project.write('Code/a.sh', project.read('Code/a.sh') + '# harmless\n')
    args = ['accept', '01-a', '--reason', 'Harmless comment', '--review', 'Code/a.sh=Comment only', '--json']
    assert project.run(*args, '--dry-run') == 0
    proposal = json.loads(capsys.readouterr().out)
    assert [row['step'] for row in proposal['steps']] == ['build-a']
    assert not (project.root / LEDGER).exists()
    assert project.run(*args) == 0
    capsys.readouterr()
    assert project.run('explain', '01-a#build-a', '--json') == 0
    explanation = json.loads(capsys.readouterr().out)
    assert explanation['status'] == 'fresh'
    assert explanation['acceptance']['reason'] == 'Harmless comment'
    assert explanation['rows'] == [] and explanation['groups'] == []
    assert project.run('impact', 'Code/a.sh', '--scope', '02-b', '--json') == 0
    assert not json.loads(capsys.readouterr().out)['direct'][0]['in_scope']
    assert project.run('revoke', '01-a', '--json') == 0
    assert json.loads(capsys.readouterr().out)['revoked'] == ['build-a']


def test_textual_input_snapshots_stay_local_and_reuse_remains_portable(project):
    secret = 'private-research-observation-73982'
    project.write('input.csv', 'id,value\n1,' + secret + '\n')
    project.write('superRA/01-a/task.md', project.read('superRA/01-a/task.md').replace('    deps:\n', '    deps:\n      - input.csv\n'))
    assert project.run('build', *CHAIN) == 0
    assert secret in receipt_path(project.paths, 'build-a').read_text()
    project.write('Code/a.sh', project.read('Code/a.sh') + '# harmless\n')
    review(project)
    assert all(secret not in text for text in map(bytes.decode, committed_records(project).values()))
    assert secret not in json.dumps(project.status(*CHAIN).to_dict())
    shutil.rmtree(project.paths.state_dir)
    assert project.states()['build-a'] == 'fresh'
    assert project.run('build', '01-a#build-a') == 0
    assert not project.paths.run_file('build-a').exists()
    assert secret not in json.dumps(project.status(*CHAIN).to_dict())


def test_first_acceptance_skips_without_fabricating_execution(project):
    project.write('output/a.txt', 'interactive result\n')
    args = (project.graph(), project.paths, ['01-a'], 'Reviewed the interactive result', {})
    proposal = accept(*args, dry_run=True)
    assert proposal['ready']
    assert not proposal['steps'][0]['baseline_details']['available']
    accept(*args)
    entry = project.status('01-a').entry('build-a')
    assert entry.status == 'fresh' and entry.acceptance['basis'] == 'reviewed'
    assert entry.last_run is None and entry.log is None
    assert 'build-a' not in read_lock(project.paths.lock_file)
    assert read_run_record(project.paths, 'build-a') == {}
    assert not receipt_path(project.paths, 'build-a').exists()
    assert project.run('build', *CHAIN) == 0
    assert 'build-a' not in project.run_times()
    assert 'build-a' not in read_lock(project.paths.lock_file)
    assert project.read('output/b.txt') == 'interactive result\n' * 2
    assert project.states()['check-b'] == 'fresh'
    assert project.run('build', '01-a', '--force', '--dry-run') == 0
    assert read_run_record(project.paths, 'build-a') == {}
    assert project.run('build', '01-a', '--force') == 0
    assert read_run_record(project.paths, 'build-a')['outcome'] == 'success'
    assert 'build-a' not in read_ledger(project.paths)['steps']


def test_acceptance_of_saved_inputs_does_not_certify_or_build_upstream(project):
    project.write('output/a.txt', 'saved without producer execution\n')
    project.write('output/b.txt', 'reviewed downstream result\n')
    review(project, ['02-b#build-b'])
    saved = read_ledger(project.paths)['steps']['build-b']['boundary_inputs']
    assert [item['logical'] for item in saved] == ['${OUT}/a.txt']
    assert all('resolved' not in item for item in saved)
    assert project.status('02-b').entry('build-b').status == 'fresh'
    assert compute_status(project.graph(), project.paths, targets=['02-b'], upstream=True).entry('build-b').status != 'fresh'
    assert project.run('build', '02-b', '--only') == 0
    assert set(project.run_times()) == {'check-b'}
    assert project.read('output/b.txt') == 'reviewed downstream result\n'


# ---------------------------------------------------------------------------
# Portable committed records
# ---------------------------------------------------------------------------

PORTABLE_CONFIG = """\
reproduction:
  vars:
    OUT:
      env: OUTROOT
"""


def _portable_project(root):
    from test_repro_runner import Project
    proj = Project(root)
    proj.write('superRA/config.yaml', PORTABLE_CONFIG)
    for task, name, deps, out in (('01-a', 'build-a', ['Code/a.sh'], 'a'),
                                  ('02-b', 'build-b', ['Code/b.sh', '"${OUT}/a.txt"'], 'b')):
        dep_lines = ''.join(f'      - {d}\n' for d in deps)
        proj.write(f'superRA/{task}/task.md', f'---\ntitle: "{task}"\nstatus: not-started\ndepends_on: []\n---\n\n'
                   f'## Reproduction\n\n```yaml\nsteps:\n  - name: {name}\n    cmd: sh Code/{out}.sh\n'
                   f'    deps:\n{dep_lines}    outs:\n      - "${{OUT}}/{out}.txt"\n```\n')
    proj.write('Code/a.sh', 'echo hello > "$OUTROOT/a.txt"\n')
    proj.write('Code/b.sh', 'cat "$OUTROOT/a.txt" "$OUTROOT/a.txt" > "$OUTROOT/b.txt"\n')
    return proj


def committed_records(proj):
    files = [p for p in sorted(proj.root.glob('repro-*')) if p.is_file()]
    files += sorted((proj.root / 'repro-acceptance').glob('*.json'))
    return {p.relative_to(proj.root).as_posix(): p.read_bytes() for p in files}


def test_committed_records_are_identical_across_roots_and_users(tmp_path, monkeypatch):
    records = []
    for user in ('alice', 'bob'):
        out = tmp_path / user / 'out'
        out.mkdir(parents=True)
        monkeypatch.setenv('OUTROOT', str(out))
        monkeypatch.setenv('LOGNAME', user)
        monkeypatch.setenv('USER', user)
        proj = _portable_project(tmp_path / user / 'proj')
        assert proj.run('build', '.') == 0
        for script in ('Code/a.sh', 'Code/b.sh'):
            proj.write(script, proj.read(script) + '# harmless\n')
        # Accepted apart, so build-b keeps ${OUT}/a.txt as a saved input.
        assert proj.run('accept', '02-b', '--reason', 'Comment-only edit') == 0
        assert proj.run('accept', '01-a', '--reason', 'Comment-only edit') == 0
        found = committed_records(proj)
        assert any('acceptance' in name for name in found)
        text = b''.join(found.values()).decode()
        assert str(tmp_path) not in text and user not in text
        records.append(found)
    assert records[0] == records[1]


def _git_project(project):
    from test_repro_provenance import git
    project.write('.gitignore', '.superra-repro/\n')
    git(project.root, 'init', '-q')
    assert project.run('build', '.') == 0
    for script in ('Code/a.sh', 'Code/x.sh'):
        project.write(script, project.read(script) + '# harmless\n')
    git(project.root, 'add', '-A')
    git(project.root, 'commit', '-qm', 'base')
    return git


def test_branches_accepting_different_steps_merge_cleanly(project):
    git = _git_project(project)
    git(project.root, 'checkout', '-qb', 'left')
    assert project.run('accept', '01-a', '--reason', 'Reviewed on left') == 0
    git(project.root, 'add', '-A')
    git(project.root, 'commit', '-qm', 'accept a')
    git(project.root, 'checkout', '-q', 'main')
    assert project.run('accept', '03-x', '--reason', 'Reviewed on main') == 0
    git(project.root, 'add', '-A')
    git(project.root, 'commit', '-qm', 'accept x')
    git(project.root, 'merge', '-q', '--no-edit', 'left')  # raises on conflict
    assert project.states('.')['build-a'] == project.states('.')['build-x'] == 'fresh'


def test_conflicted_record_disables_only_its_own_step(project, capsys):
    import subprocess
    git = _git_project(project)
    assert project.run('accept', '03-x', '--reason', 'Reviewed x') == 0
    git(project.root, 'add', '-A')
    git(project.root, 'commit', '-qm', 'accept x')
    git(project.root, 'checkout', '-qb', 'left')
    assert project.run('accept', '01-a', '--reason', 'Reviewed on left') == 0
    git(project.root, 'add', '-A')
    git(project.root, 'commit', '-qm', 'accept a left')
    git(project.root, 'checkout', '-q', 'main')
    assert project.run('accept', '01-a', '--reason', 'Reviewed on main') == 0
    git(project.root, 'add', '-A')
    git(project.root, 'commit', '-qm', 'accept a main')
    merged = subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', 'merge', '--no-edit', 'left'],
                            cwd=project.root, capture_output=True, text=True)
    assert merged.returncode != 0 and 'CONFLICT' in merged.stdout
    capsys.readouterr()
    states = project.states('.')
    assert states['build-x'] == 'fresh' and states['build-a'] == 'stale'
    assert 'build-a' in capsys.readouterr().err
    assert project.run('status', '.') in (0, 1)
    assert project.run('accept', '01-a', '--reason', 'Resolved: reviewed again') == 0
    assert project.states('.')['build-a'] == 'fresh'
    assert project.run('build', '03-x') == 0


def test_accept_writes_small_records_only_for_steps_that_changed(project):
    assert project.run('build', '.') == 0
    project.write('Code/a.sh', project.read('Code/a.sh') + '# harmless\n')
    assert project.run('accept', '01-a', '--reason', 'Comment-only edit') == 0
    record = project.root / LEDGER / 'build-a.json'
    before = record.read_bytes(), record.stat().st_mtime_ns
    assert project.run('accept', '.', '--reason', 'Everything reviewed') == 0
    assert sorted(p.name for p in (project.root / LEDGER).iterdir()) == ['build-a.json']
    assert (record.read_bytes(), record.stat().st_mtime_ns) == before
    assert set(json.loads(before[0])) == {'basis', 'boundary_inputs', 'id', 'lock', 'reason', 'reviews', 'state'}
    assert len(before[0]) < 1500


def test_deleting_local_state_stales_no_step(project):
    _use_a_sidecar(project)
    assert project.run('build', '.') == 0
    project.write('Code/b.sh', project.read('Code/b.sh') + '# harmless\n')
    assert project.run('accept', '02-b#build-b', '--reason', 'Comment-only edit') == 0
    before = project.states('.')
    assert set(before.values()) == {'fresh'}
    shutil.rmtree(project.paths.state_dir)
    assert project.states('.') == before


def _dropbox_ignored(path, *, clear=False):
    """Whether *path* carries Dropbox's ignore flag; *clear* removes it first."""
    import os
    import subprocess
    import sys
    if hasattr(os, 'getxattr'):
        try:
            if clear:
                os.removexattr(path, 'user.com.dropbox.ignored')
            return os.getxattr(path, 'user.com.dropbox.ignored') == b'1'
        except OSError:
            return False
    if sys.platform != 'darwin':
        pytest.skip('no extended attributes on this platform')
    if clear:
        subprocess.run(['xattr', '-d', 'com.dropbox.ignored', str(path)], capture_output=True)
    found = subprocess.run(['xattr', '-p', 'com.dropbox.ignored', str(path)], capture_output=True, text=True)
    return found.returncode == 0 and found.stdout.strip() == '1'


def test_local_state_carries_the_dropbox_ignore_attribute(project):
    assert project.run('status', '.') in (0, 1)
    assert _dropbox_ignored(project.paths.state_dir)
    # A folder that already synced gains the flag the next time superRA opens it.
    assert not _dropbox_ignored(project.paths.state_dir, clear=True)
    assert project.run('status', '.') in (0, 1)
    assert _dropbox_ignored(project.paths.state_dir)

