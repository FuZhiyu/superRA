"""Task-scoped execution and concurrent declaration edits, using real commands."""
import json

import pytest

from _repro_state import compute_status, read_run_record, select_steps
from _repro_acceptance import receipt_path
from test_repro_runner import CHAIN, project, TASK_X  # noqa: F401


def test_task_and_qualified_step_targets(project):
    assert select_steps(project.graph(), ['02-b'])[0] == ['build-b', 'check-b']
    assert select_steps(project.graph(), ['02-b#check-b'])[0] == ['check-b']
    assert select_steps(project.graph(), ['02-b#build-a'])[1]
    assert set(select_steps(project.graph(), ['.'])[0]) == {'build-a', 'build-b', 'check-b', 'build-x'}


def test_scoped_build_uses_existing_unrecorded_inputs(project):
    project.write('output/a.txt', 'saved without a build record\n')
    assert project.run('build', '02-b') == 0
    assert set(project.run_times()) == {'build-b', 'check-b'}
    assert compute_status(project.graph(), project.paths, targets=['02-b']).ok
    assert not compute_status(project.graph(), project.paths, targets=['02-b'], upstream=True).ok


def test_scoped_build_survives_failed_upstream_and_rebuilds_changed_inputs(project):
    assert project.run('build', *CHAIN) == 0
    project.write('Code/a.sh', 'exit 1\n')
    assert project.run('build', '01-a') == 1
    failed = read_run_record(project.paths, 'build-a')
    project.write('output/a.txt', 'changed saved input\n')
    assert project.run('build', '02-b') == 0
    assert project.read('output/b.txt') == 'changed saved input\n' * 2
    assert read_run_record(project.paths, 'build-a') == failed
    assert compute_status(project.graph(), project.paths, targets=['02-b']).ok


def test_missing_boundary_does_not_expand_but_upstream_does(project):
    assert project.run('build', '02-b') != 0
    assert not (project.root / 'output/a.txt').exists()
    assert project.run('build', '02-b', '--upstream') == 0
    assert set(project.run_times()) == {'build-a', 'build-b', 'check-b'}


@pytest.mark.parametrize('jobs', ['2'])
def test_unrelated_task_creation_during_execution_is_allowed(project, jobs):
    project.write('new-task.txt', TASK_X.replace('build-x', 'build-new').replace('x.txt', 'new.txt'))
    project.write('Code/a.sh', project.read('Code/a.sh') + 'mkdir -p superRA/unrelated\ncp new-task.txt superRA/unrelated/task.md\n')
    assert project.run('build', '01-a', '-j', jobs) == 0
    assert read_run_record(project.paths, 'build-a')['outcome'] == 'success'


def test_saved_input_evidence_and_unchanged_repeat(project):
    project.write('output/a.txt', 'unverified\n')
    assert project.run('build', '02-b') == 0
    receipt = json.loads(receipt_path(project.paths, 'build-b').read_text())
    assert receipt['boundary_inputs'][0]['provenance'] == 'no successful build recorded'
    assert receipt['boundary_inputs'][0]['digest']
    before = project.run_times()
    project.write('Code/a.sh', 'exit 1\n')
    assert project.run('build', '02-b') == 0
    assert project.run_times() == before
    assert project.run('status', '02-b') == 3
    assert project.run('status', '02-b', '--upstream') == 1


def test_task_reader_preserves_global_freshness_and_local_evidence(project):
    from task_read import _reproduction_view, _render_reproduction_human
    project.write('output/a.txt', 'saved\n')
    assert project.run('build', '02-b') == 0
    graph = project.graph()
    view = _reproduction_view(project.root / 'superRA', graph.dependencies.tasks['02-b'],
                              graph.dependencies.tasks[''], graph=graph)
    row = next(item for item in view['steps'] if item['name'] == 'build-b')
    assert row['status'] == 'stale'
    assert row['local_status'] == 'fresh'
    assert row['boundary_inputs'][0]['provenance'] == 'no successful build recorded'
    assert 'for saved inputs: fresh' in '\n'.join(_render_reproduction_human(view))


def test_saved_input_mutation_during_execution_rejects_receipt(project):
    project.write('output/a.txt', 'old\n')
    project.write('Code/b.sh', project.read('Code/b.sh') + 'echo new > output/a.txt\n')
    assert project.run('build', '02-b') == 1
    assert not receipt_path(project.paths, 'build-b').exists()


def test_sidecar_does_not_hide_saved_input_change(project):
    from test_repro_runner import _use_a_sidecar
    _use_a_sidecar(project)
    assert project.run('build', *CHAIN) == 0
    before = project.run_times()
    project.write('output/a.txt', 'changed without updating sidecar\n')
    assert not compute_status(project.graph(), project.paths, targets=['02-b']).ok
    assert project.run('build', '02-b') == 0
    assert project.run_times()['build-a'] == before['build-a']
    assert project.read('output/b.txt') == 'changed without updating sidecar\n' * 2
    assert project.run('status', '02-b') == 0
    after = project.run_times()
    assert project.run('build', '02-b') == 0
    assert project.run_times() == after


@pytest.mark.parametrize('drop_receipt', [False])
def test_acceptance_cannot_hide_changed_saved_bytes(project, drop_receipt):
    from test_repro_runner import _use_a_sidecar
    from test_repro_acceptance import review
    _use_a_sidecar(project)
    assert project.run('build', *CHAIN) == 0
    assert project.run('build', '02-b') == 0
    project.write('Code/b.sh', project.read('Code/b.sh') + '# harmless\n')
    review(project, ['02-b#build-b'])
    if drop_receipt:
        receipt_path(project.paths, 'build-b').unlink()
    assert project.run('status', '02-b') == 0
    project.write('output/a.txt', 'changed with unchanged sidecar\n')
    assert project.run('status', '02-b') == 1
    assert project.run('status', '02-b', '--upstream') == 1
    before = project.run_times()
    assert project.run('build', '02-b') == 0
    assert project.run_times()['build-a'] == before['build-a']
    assert project.read('output/b.txt') == 'changed with unchanged sidecar\n' * 2


def test_batch_acceptance_tracks_inputs_between_accepted_steps(project):
    from test_repro_runner import _use_a_sidecar
    from test_repro_acceptance import review
    _use_a_sidecar(project)
    assert project.run('build', *CHAIN) == 0
    for script in ['Code/a.sh', 'Code/b.sh']:
        project.write(script, project.read(script) + '# harmless\n')
    review(project, ['01-a#build-a', '02-b#build-b'])
    assert project.run('status', '02-b') == 0
    project.write('output/a.txt', 'changed after batch acceptance\n')
    assert project.run('status', '02-b') == 1


@pytest.mark.parametrize('accepted', [False])
def test_saved_input_evidence_follows_logical_path_relocation(project, accepted):
    import shutil
    from test_repro_runner import _use_a_sidecar
    from test_repro_acceptance import review
    _use_a_sidecar(project)
    assert project.run('build', *CHAIN) == 0
    assert project.run('build', '02-b') == 0
    if accepted:
        project.write('Code/b.sh', project.read('Code/b.sh') + '# harmless\n')
        review(project, ['02-b#build-b'])
    shutil.copytree(project.root / 'output', project.root / 'relocated')
    project.write('superRA/config.yaml', project.read('superRA/config.yaml').replace('OUT: output', 'OUT: relocated'))
    assert project.run('status', '02-b') == 0
    project.write('relocated/a.txt', 'new bytes with old sidecar\n')
    assert project.run('status', '02-b') == 1
    assert project.run('status', '02-b', '--upstream') == 1


def test_partial_selection_leaves_intervening_producer_untouched(project):
    assert project.run('build', *CHAIN) == 0
    before = project.run_times()
    project.write('Code/a.sh', 'echo changed > output/a.txt\n')
    assert project.run('build', '01-a', '02-b#check-b', '--force') == 0
    assert project.run_times()['build-b'] == before['build-b']
    assert project.read('output/b.txt') == 'hello\nhello\n'
    assert project.run('status', '02-b#check-b') == 3
    assert project.run('status', '02-b#check-b', '--upstream') == 1


@pytest.mark.parametrize('change', ['path'])
def test_relevant_declaration_change_during_execution_is_rejected(project, change):
    if change == 'path':
        project.write('replacement.txt', project.read('superRA/config.yaml').replace('OUT: output', 'OUT: elsewhere'))
        edit = 'cp replacement.txt superRA/config.yaml\n'
    elif change == 'ownership':
        project.write('replacement.txt', TASK_X.replace('x.txt', 'a.txt'))
        edit = 'cp replacement.txt superRA/03-x/task.md\n'
    else:
        project.write('replacement.txt', project.read('superRA/01-a/task.md').replace('status: not-started', 'status: archived'))
        edit = 'cp replacement.txt superRA/01-a/task.md\n'
    project.write('Code/a.sh', project.read('Code/a.sh') + edit)
    assert project.run('build', '01-a') == 1
    assert not receipt_path(project.paths, 'build-a').exists()

