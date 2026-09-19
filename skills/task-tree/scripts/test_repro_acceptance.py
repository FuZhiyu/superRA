"""Real-engine reviewed reuse, precise scopes, and trustworthy evidence."""
import json
import shutil

import pytest

from test_repro_runner import project, dir_project, needs_pytask, _use_a_sidecar
from _repro_acceptance import (
    accept, preview, revoke, impact, read_ledger, receipt_path, mutation_lock,
    ReproStateError, LEDGER,
)
from _repro_state import read_lock, read_run_record


def review(project, names=('build-a',), *, apply=True):
    project.write('review.md', 'Reviewed the changes: comments only; outputs remain valid.\n')
    first = preview(project.graph(), project.paths, names, '', {}, [])
    reviews = {change['node']: 'Comment only; execution and output are unchanged.'
               for row in first['steps'] for change in row['changes']}
    args = (project.graph(), project.paths, names, 'Harmless source changes', reviews, ['review.md'])
    proposal = accept(*args)
    return accept(*args, token=proposal['token']) if apply else (args, proposal)


@needs_pytask
@pytest.mark.parametrize('jobs', ['1', '2'])
def test_accepted_build_skips_producer_but_runs_independently_dirty_descendant(project, jobs):
    assert project.run('build') == 0
    before = project.run_times()
    lock = read_lock(project.paths.lock_file)['build-a']
    project.write('Code/a.sh', project.read('Code/a.sh') + '# harmless\n')
    project.write('Code/b.sh', project.read('Code/b.sh') + '# independently changed\n')
    review(project)
    assert project.states()['build-a'] == 'fresh'
    assert project.states()['build-b'] == 'stale'
    assert project.run('build', '-j', jobs) == 0
    after = project.run_times()
    assert before['build-a'] == after['build-a']
    assert before['build-b'] < after['build-b']
    assert read_lock(project.paths.lock_file)['build-a'] == lock
    assert project.states()['check-b'] == 'fresh'
    assert project.run('build', '-j', jobs) == 0
    assert project.run_times() == after


@needs_pytask
def test_dry_run_force_scope_and_real_success_supersedes(project):
    assert project.run('build') == 0
    project.write('Code/a.sh', project.read('Code/a.sh') + '# harmless\n')
    review(project)
    times = project.run_times()
    lock = project.paths.lock_file.read_bytes()
    assert project.run('build', '--dry-run') == 0
    assert project.run('build', 'build-b', '--force', '--dry-run') == 0
    assert times == project.run_times()
    assert lock == project.paths.lock_file.read_bytes()
    assert project.run('build', 'build-b', '--force') == 0
    assert project.run_times()['build-a'] == times['build-a']
    assert project.run('build', 'build-b', '--force-all') == 0
    assert project.run_times()['build-a'] > times['build-a']
    assert 'build-a' not in read_ledger(project.paths)['steps']


@needs_pytask
def test_portable_acceptance_without_local_cache_and_receipts(project):
    assert project.run('build') == 0
    project.write('Code/a.sh', project.read('Code/a.sh') + '# harmless\n')
    review(project)
    shutil.rmtree(project.paths.state_dir)
    assert project.states()['build-a'] == 'fresh'
    assert project.run('build', 'build-a') == 0
    assert not project.paths.run_file('build-a').exists()


@needs_pytask
@pytest.mark.parametrize('change', ['dep', 'spec', 'output', 'missing_input', 'missing_output', 'revoke'])
def test_later_changes_invalidate_acceptance(project, change):
    assert project.run('build') == 0
    project.write('Code/a.sh', project.read('Code/a.sh') + '# harmless\n')
    review(project)
    if change == 'dep':
        project.write('Code/a.sh', project.read('Code/a.sh') + '# later\n')
    elif change == 'spec':
        project.write('superRA/01-a/task.md', project.read('superRA/01-a/task.md').replace('sh Code/a.sh', 'sh Code/a.sh ' + '&& true'))
    elif change == 'output':
        project.write('output/a.txt', 'different\n')
    elif change == 'missing_input':
        (project.root / 'Code/a.sh').unlink()
    elif change == 'missing_output':
        (project.root / 'output/a.txt').unlink()
    else:
        assert revoke(project.graph(), project.paths, ['01-a'])['revoked'] == ['build-a']
    assert project.states()['build-a'] != 'fresh'


@needs_pytask
def test_failed_force_cannot_be_accepted_or_hidden_by_restored_inputs(project):
    assert project.run('build') == 0
    original = project.read('Code/a.sh')
    project.write('Code/a.sh', original + '# harmless\n')
    review(project)
    project.write('Code/a.sh', 'exit 2\n')
    assert project.run('build', 'build-a', '--force') != 0
    project.write('Code/a.sh', original)
    assert project.states()['build-a'] == 'failed'
    project.write('Code/a.sh', original + '# harmless\n')
    with pytest.raises(ReproStateError, match='did not succeed'):
        review(project)


@needs_pytask
def test_sidecar_acceptance_verifies_actual_output_bytes(project):
    _use_a_sidecar(project)
    assert project.run('build') == 0
    project.write('Code/a.sh', project.read('Code/a.sh') + '# harmless\n')
    review(project)
    project.write('output/a.txt', 'corrupted without sidecar change')
    assert project.states()['build-a'] == 'stale'
    with pytest.raises(ReproStateError, match='output differs'):
        review(project)


@needs_pytask
def test_legacy_lock_missing_history_can_accept_normal_outputs(project):
    assert project.run('build') == 0
    receipt_path(project.paths, 'build-a').unlink()
    project.write('Code/a.sh', project.read('Code/a.sh') + '# harmless\n')
    args, proposal = review(project, apply=False)
    assert proposal['steps'][0]['baseline_details']['diffs'][0]['history'] == 'unavailable'
    accept(*args, token=proposal['token'])
    assert project.states()['build-a'] == 'fresh'


@needs_pytask
def test_legacy_sidecar_needs_trustworthy_baseline(project):
    _use_a_sidecar(project)
    assert project.run('build') == 0
    receipt_path(project.paths, 'build-a').unlink()
    project.write('Code/a.sh', project.read('Code/a.sh') + '# harmless\n')
    with pytest.raises(ReproStateError, match='no verified output digest'):
        review(project)


@needs_pytask
def test_dirty_source_snapshot_is_verified_and_preview_rejects_concurrent_edit(project):
    project.write('Code/a.sh', project.read('Code/a.sh') + '# dirty before run\n')
    assert project.run('build') == 0
    project.write('Code/a.sh', project.read('Code/a.sh') + '# harmless\n')
    args, proposal = review(project, apply=False)
    diff = proposal['steps'][0]['baseline_details']['diffs'][0]
    assert diff['history'] == 'verified snapshot'
    assert 'dirty before run' in diff['diff']
    project.write('Code/a.sh', project.read('Code/a.sh') + '# concurrent\n')
    with pytest.raises(ReproStateError, match='preview no longer matches'):
        accept(*args, token=proposal['token'])
    assert not (project.root / LEDGER).exists()


@needs_pytask
def test_missing_evidence_and_uncovered_changes_do_not_apply(project):
    assert project.run('build') == 0
    project.write('Code/a.sh', project.read('Code/a.sh') + '# harmless\n')
    proposal = accept(project.graph(), project.paths, ['build-a'], 'Reviewed', {}, [])
    assert not proposal['ready']
    with pytest.raises(ReproStateError, match='cover every changed'):
        accept(project.graph(), project.paths, ['build-a'], 'Reviewed', {}, [], proposal['token'])
    with pytest.raises(ReproStateError, match='evidence is unavailable'):
        accept(project.graph(), project.paths, ['build-a'], 'Reviewed', {}, ['absent.md'])


@needs_pytask
def test_check_acceptance_preserves_successful_stamp(project):
    assert project.run('build') == 0
    path = project.paths.stamps_dir / 'check-b'
    # stamp_ref uses a .stamp extension.
    path = next(project.paths.stamps_dir.iterdir())
    before = path.read_bytes(), path.stat().st_mtime_ns, project.run_times()['check-b']
    project.write('superRA/02-b/task.md', project.read('superRA/02-b/task.md').replace('test -s output/b.txt', 'test -s output/b.txt && true'))
    review(project, ['check-b'])
    assert project.run('build') == 0
    assert (path.read_bytes(), path.stat().st_mtime_ns, project.run_times()['check-b']) == before


@needs_pytask
def test_output_verification_failure_never_creates_success_receipt(project):
    project.write('Code/a.sh', 'true\n')
    assert project.run('build', 'build-a') != 0
    assert not receipt_path(project.paths, 'build-a').exists()
    assert read_run_record(project.paths, 'build-a')['outcome'] == 'failed'


def test_mutation_lock_blocks_concurrent_acceptance(project):
    with mutation_lock(project.paths):
        with pytest.raises(ReproStateError, match='another reproduction'):
            with mutation_lock(project.paths):
                pass


def test_impact_preserves_outside_scope_and_origins(project):
    result = impact(project.graph(), project.paths, ['Code/a.sh'], ['02-b'])
    assert result['direct'][0]['step'] == 'build-a'
    assert not result['direct'][0]['in_scope']
    assert result['direct'][0]['reasons'][0]['origins'] == [{'kind': 'declared'}]
    assert {r['step'] for r in result['affected']} == {'build-a', 'build-b', 'check-b'}


@needs_pytask
def test_batch_targets_and_upstream_binding(project):
    assert project.run('build') == 0
    project.write('Code/a.sh', project.read('Code/a.sh') + '# harmless\n')
    project.write('Code/b.sh', project.read('Code/b.sh') + '# harmless\n')
    with pytest.raises(ReproStateError, match='upstream producers'):
        review(project, ['build-b'])
    result = review(project, ['01-a', 'build-b'])
    assert [r['step'] for r in result['steps']] == ['build-a', 'build-b']
    ledger = read_ledger(project.paths)['steps']
    assert ledger['build-b']['upstream'] == {'build-a': ledger['build-a']['id']}
    assert set(ledger) == {'build-a', 'build-b'}
    times = project.run_times()
    assert project.run('build', '-j', '2') == 0
    assert times == project.run_times()
    revoke(project.graph(), project.paths, ['build-a'])
    assert project.states()['build-b'] == 'stale'


@needs_pytask
def test_sidecar_corruption_with_restored_lock_inputs_forces_repair(project):
    _use_a_sidecar(project)
    original = project.read('Code/a.sh')
    assert project.run('build') == 0
    project.write('Code/a.sh', original + '# harmless\n')
    review(project)
    project.write('Code/a.sh', original)
    project.write('output/a.txt', 'corrupt')
    assert project.states()['build-a'] == 'stale'
    assert project.run('build') == 0
    assert project.read('output/a.txt') == 'hello\n'
    assert project.states()['build-a'] == 'fresh'


@needs_pytask
def test_failure_revokes_before_execution_even_after_cache_loss(project):
    assert project.run('build') == 0
    original = project.read('Code/a.sh')
    project.write('Code/a.sh', original + '# harmless\n')
    review(project)
    project.write('Code/a.sh', 'exit 1\n')
    assert project.run('build', 'build-a', '--force') != 0
    assert 'build-a' not in read_ledger(project.paths)['steps']
    project.write('Code/a.sh', original + '# harmless\n')
    shutil.rmtree(project.paths.state_dir)
    assert project.states()['build-a'] == 'stale'


@needs_pytask
def test_invalid_graph_never_accepts_or_builds(project):
    assert project.run('build') == 0
    project.write('Code/a.sh', project.read('Code/a.sh') + '# harmless\n')
    review(project)
    project.write('superRA/01-a/task.md', project.read('superRA/01-a/task.md').replace('depends_on: []', 'depends_on: [02-b]'))
    assert not project.status().ok
    assert project.run('build', 'build-a') == 1
    with pytest.raises(ReproStateError, match='invalid graph'):
        review(project)


@needs_pytask
def test_cli_preview_apply_explain_revoke_and_scope(project, capsys):
    assert project.run('build') == 0
    capsys.readouterr()
    project.write('Code/a.sh', project.read('Code/a.sh') + '# harmless\n')
    project.write('review.md', 'Reviewed comment-only edit.\n')
    args = ['accept', '01-a', '--reason', 'Harmless comment', '--review', 'Code/a.sh=Comment only', '--evidence', 'review.md', '--json']
    assert project.run(*args) == 0
    proposal = json.loads(capsys.readouterr().out)
    assert [row['step'] for row in proposal['steps']] == ['build-a']
    assert project.run(*args, '--apply', proposal['token']) == 0
    capsys.readouterr()
    assert project.run('explain', 'build-a', '--json') == 0
    explanation = json.loads(capsys.readouterr().out)
    assert explanation['status'] == 'fresh'
    assert explanation['acceptance']['reason'] == 'Harmless comment'
    assert explanation['baseline']['diffs'][0]['history'] == 'verified snapshot'
    assert project.run('impact', 'Code/a.sh', '--scope', '02-b', '--json') == 0
    assert not json.loads(capsys.readouterr().out)['direct'][0]['in_scope']
    assert project.run('revoke', '01-a', '--json') == 0
    assert json.loads(capsys.readouterr().out)['revoked'] == ['build-a']


@needs_pytask
def test_source_and_evidence_edits_after_preview_reject_without_partial_write(project):
    from _repro_acceptance import bind_sources
    assert project.run('build') == 0
    project.write('Code/a.sh', project.read('Code/a.sh') + '# harmless\n')
    args, proposal = review(project, apply=False)
    bind_sources(args[0], project.plan_root)
    project.write('superRA/01-a/task.md', project.read('superRA/01-a/task.md').replace('sh Code/a.sh', 'sh Code/a.sh && true'))
    with pytest.raises(ReproStateError, match='declarations or configuration changed'):
        accept(*args, token=proposal['token'])
    assert not (project.root / LEDGER).exists()
    args, proposal = review(project, apply=False)
    project.write('review.md', 'Changed review evidence\n')
    with pytest.raises(ReproStateError, match='preview no longer matches'):
        accept(*args, token=proposal['token'])


@needs_pytask
def test_input_change_during_execution_cannot_establish_baseline(project):
    project.write('Code/a.sh', project.read('Code/a.sh') + "echo '# changed during run' >> Code/a.sh\n")
    assert project.run('build', 'build-a') != 0
    assert not receipt_path(project.paths, 'build-a').exists()
    assert read_run_record(project.paths, 'build-a')['outcome'] == 'failed'


@needs_pytask
def test_directory_receipt_and_reuse(dir_project):
    project = dir_project
    assert project.run('build') == 0
    project.write('Code/gen.sh', project.read('Code/gen.sh') + '# harmless\n')
    review(project, ['z-gen'])
    times = project.run_times()
    assert project.run('build', '-j', '2') == 0
    assert times == project.run_times()
    project.write('output/parts/extra.txt', 'new file\n')
    assert project.states()['z-gen'] == 'stale'


@needs_pytask
@pytest.mark.parametrize('jobs', ['1', '2'])
def test_failed_predecessor_does_not_skip_as_success_or_run_accepted_child(project, jobs):
    assert project.run('build') == 0
    project.write('Code/b.sh', project.read('Code/b.sh') + '# harmless\n')
    review(project, ['build-b'])
    before = project.run_times()['build-b']
    project.write('Code/a.sh', 'exit 4\n')
    assert project.run('build', 'build-b', '--force-all', '-j', jobs) != 0
    assert project.run_times()['build-b'] == before
    assert project.states()['build-b'] == 'stale'


@needs_pytask
def test_revalidates_between_task_creation_and_engine_setup(project, monkeypatch):
    import repro_run
    assert project.run('build') == 0
    project.write('Code/a.sh', project.read('Code/a.sh') + '# harmless\n')
    review(project)
    before = project.run_times()['build-a']
    original = repro_run.make_tasks
    def changed(*args, **kwargs):
        tasks = original(*args, **kwargs)
        project.write('Code/a.sh', project.read('Code/a.sh') + '# edit after build selection\n')
        return tasks
    monkeypatch.setattr(repro_run, 'make_tasks', changed)
    assert project.run('build', 'build-a') == 0
    assert project.run_times()['build-a'] > before
    assert 'build-a' not in read_ledger(project.paths)['steps']


@needs_pytask
def test_shared_helper_fanout_accepts_only_reviewed_consumer(project):
    for task in ('01-a', '03-x'):
        filename = f'superRA/{task}/task.md'
        project.write(filename, project.read(filename).replace('    deps:\n', '    deps:\n      - Code/shared.sh\n'))
    project.write('Code/shared.sh', '# shared utilities\n')
    assert project.run('build', '--tier', 'all') == 0
    before = project.run_times()
    project.write('Code/shared.sh', '# shared utilities; harmless for A\n')
    project.write('Code/x.sh', project.read('Code/x.sh') + '# independent edit\n')
    result = impact(project.graph(), project.paths, ['Code/shared.sh'])
    assert {r['step'] for r in result['direct']} == {'build-a', 'build-x'}
    review(project, ['build-a'])
    assert project.run('build', '--tier', 'all', '-j', '2') == 0
    assert project.run_times()['build-a'] == before['build-a']
    assert project.run_times()['build-x'] > before['build-x']


@needs_pytask
def test_derived_configuration_stops_irrelevant_fanout(project):
    project.write('superRA/00-config/task.md', '''---
title: Config
status: implemented
depends_on: []
---
## Reproduction
```yaml
tier: required
steps:
  - name: config
    cmd: sh Code/config.sh
    deps: [Code/config.sh, Code/specs.txt]
    outs: [output/config-a.txt, output/config-x.txt]
```
''')
    project.write('Code/config.sh', 'mkdir -p output\nsed -n 1p Code/specs.txt > output/config-a.txt\nsed -n 2p Code/specs.txt > output/config-x.txt\n')
    project.write('Code/specs.txt', 'a-setting\nx-setting\n')
    for task, dep in [('01-a', 'a'), ('03-x', 'x')]:
        filename = f'superRA/{task}/task.md'
        project.write(filename, project.read(filename).replace('    deps:\n', f'    deps:\n      - output/config-{dep}.txt\n'))
    assert project.run('build', '--tier', 'all') == 0
    before = project.run_times()
    project.write('Code/specs.txt', 'a-setting\nx-changed\n')
    assert project.run('build', '--tier', 'all') == 0
    after = project.run_times()
    assert after['config'] > before['config']
    assert after['build-a'] == before['build-a']
    assert after['build-x'] > before['build-x']
    assert after['build-b'] == before['build-b']


@needs_pytask
def test_textual_input_snapshots_stay_local_and_reuse_remains_portable(project):
    secret = 'private-research-observation-73982'
    project.write('input.csv', 'id,value\n1,' + secret + '\n')
    project.write('superRA/01-a/task.md', project.read('superRA/01-a/task.md').replace('    deps:\n', '    deps:\n      - input.csv\n'))
    assert project.run('build') == 0
    assert secret in receipt_path(project.paths, 'build-a').read_text()
    project.write('Code/a.sh', project.read('Code/a.sh') + '# harmless\n')
    review(project)
    assert secret not in (project.root / LEDGER).read_text()
    assert secret not in json.dumps(project.status().to_dict())
    shutil.rmtree(project.paths.state_dir)
    assert project.states()['build-a'] == 'fresh'
    assert project.run('build', 'build-a') == 0
    assert not project.paths.run_file('build-a').exists()
    assert secret not in json.dumps(project.status().to_dict())


@needs_pytask
def test_malformed_ledger_and_never_built_acceptance_fail(project):
    with pytest.raises(ReproStateError, match='never built'):
        review(project)
    assert project.run('build') == 0
    project.write(LEDGER, '{malformed')
    with pytest.raises(ReproStateError, match='invalid record'):
        project.status()
    with pytest.raises(ReproStateError, match='invalid record'):
        review(project)


@needs_pytask
def test_force_dry_run_preserves_ledger_and_evidence(project):
    assert project.run('build') == 0
    project.write('Code/a.sh', project.read('Code/a.sh') + '# harmless\n')
    review(project)
    ledger = (project.root / LEDGER).read_bytes()
    receipt = receipt_path(project.paths, 'build-a').read_bytes()
    assert project.run('build', 'build-a', '--force', '--dry-run', '-j', '2') == 0
    assert (project.root / LEDGER).read_bytes() == ledger
    assert receipt_path(project.paths, 'build-a').read_bytes() == receipt


@needs_pytask
def test_precommand_forced_failure_preserves_truth_and_invalidates_cache(project, monkeypatch):
    import repro_run
    assert project.run('build') == 0
    project.write('Code/a.sh', project.read('Code/a.sh') + '# harmless\n')
    review(project)
    before = project.run_times()['build-a']
    def fail_before_command(*args, **kwargs):
        def execute(deps, spec):
            raise OSError('cannot initialize command log')
        return execute
    monkeypatch.setattr(repro_run, '_run_step', fail_before_command)
    assert project.run('build', 'build-a', '--force') != 0
    assert project.run_times()['build-a'] == before
    assert read_run_record(project.paths, 'build-a')['outcome'] == 'failed'
    assert 'build-a' not in read_ledger(project.paths)['steps']


@needs_pytask
@pytest.mark.parametrize('jobs', ['1', '2'])
def test_identical_upstream_rerun_preserves_independent_child_acceptance(project, jobs):
    assert project.run('build') == 0
    project.write('Code/b.sh', project.read('Code/b.sh') + '# harmless\n')
    review(project, ['build-b'])
    before = project.run_times()
    ledger = read_ledger(project.paths)['steps']['build-b']
    project.write('Code/a.sh', project.read('Code/a.sh') + '# identical output\n')
    assert project.run('build', '-j', jobs) == 0
    after = project.run_times()
    assert after['build-a'] > before['build-a']
    assert after['build-b'] == before['build-b']
    assert read_ledger(project.paths)['steps']['build-b'] == ledger
    assert project.states()['build-b'] == 'fresh'


def test_impact_reports_script_include_and_environment_origins(project):
    project.write('Code/main.jl', 'include("helper.jl")\n')
    project.write('Code/helper.jl', 'x = 1\n')
    project.write('Project.toml', '[deps]\n')
    project.write('superRA/config.yaml', project.read('superRA/config.yaml').replace('reproduction:\n', 'reproduction:\n  env_deps: [Project.toml]\n'))
    project.write('superRA/01-a/task.md', project.read('superRA/01-a/task.md').replace('    deps:\n', '    deps:\n      - Code/main.jl\n'))
    graph = project.graph()
    helper = impact(graph, project.paths, ['Code/helper.jl'])['direct'][0]
    assert helper['reasons'][0]['origins'] == [{'kind': 'include', 'via': 'Code/main.jl'}]
    env = impact(graph, project.paths, ['Project.toml'])['direct']
    assert len(env) == 4
    assert all(row['reasons'][0]['origins'] == [{'kind': 'environment'}] for row in env)
    script = impact(graph, project.paths, ['Code/b.sh'])['direct'][0]
    assert script['reasons'][0]['origins'] == [{'kind': 'script'}]


@needs_pytask
def test_arbitrary_sidecar_requires_real_output_equality_and_can_be_reaccepted(project):
    _use_a_sidecar(project)
    project.write('Code/a.sh', project.read('Code/a.sh') + 'echo arbitrary-version > output/a.txt.sha256\n')
    assert project.run('build') == 0
    project.write('Code/a.sh', project.read('Code/a.sh') + '# harmless\n')
    review(project)
    shutil.rmtree(project.paths.state_dir)
    project.write('Code/a.sh', project.read('Code/a.sh') + '# another harmless edit\n')
    review(project)
    assert project.states()['build-a'] == 'fresh'
    project.write('output/a.txt', 'corruption\n')
    with pytest.raises(ReproStateError, match='output differs'):
        review(project)


@needs_pytask
def test_prose_edits_and_active_rollups_do_not_invalidate_preview(project):
    from _repro_acceptance import bind_sources
    assert project.run('build') == 0
    project.write('Code/a.sh', project.read('Code/a.sh') + '# harmless\n')
    args, proposal = review(project, apply=False)
    bind_sources(args[0], project.plan_root)
    project.write('superRA/01-a/task.md', project.read('superRA/01-a/task.md').replace('status: not-started', 'status: implemented') + '\n## Results\n\nIndependent reporting edit.\n')
    accept(*args, token=proposal['token'])
    assert project.states()['build-a'] == 'fresh'


@needs_pytask
def test_results_edit_during_real_execution_does_not_abort(project):
    project.write('Code/a.sh', project.read('Code/a.sh') + "printf '\\n## Results\\n\\nRecorded while running.\\n' >> superRA/01-a/task.md\n")
    assert project.run('build', 'build-a') == 0
    assert read_run_record(project.paths, 'build-a')['outcome'] == 'success'
    assert project.states()['build-a'] == 'fresh'


@pytest.mark.parametrize('change', ['archive', 'dependency', 'topology', 'config'])
def test_semantic_graph_guard_catches_validity_changes(project, change):
    from _repro_acceptance import bind_sources, check_sources
    graph = project.graph()
    bind_sources(graph, project.plan_root)
    if change == 'archive':
        project.write('superRA/01-a/task.md', project.read('superRA/01-a/task.md').replace('status: not-started', 'status: archived'))
    elif change == 'dependency':
        project.write('superRA/01-a/task.md', project.read('superRA/01-a/task.md').replace('depends_on: []', 'depends_on: [02-b]'))
    elif change == 'topology':
        project.write('superRA/new/task.md', '---\ntitle: New\nstatus: not-started\n---\n')
    else:
        project.write('superRA/config.yaml', project.read('superRA/config.yaml').replace('OUT: output', 'OUT: changed'))
    with pytest.raises(ReproStateError, match='declarations or configuration changed'):
        check_sources(graph)
