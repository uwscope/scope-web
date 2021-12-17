"""
Tasks for ensuring project dependencies are installed.
"""

from collections import namedtuple
from invoke import Collection
from invoke import task
from pathlib import Path

ProjectTuple = namedtuple('ProjectTuple', ['pipfile_dirs', 'yarn_dirs'])

PROJECTS = {
    'all': ProjectTuple(
        pipfile_dirs=[
            '.',
            './server_celery',
            './server_flask',
        ],
        yarn_dirs=[
            './web_registry',
        ]
    ),
    'root': ProjectTuple(
        pipfile_dirs=['.'],
        yarn_dirs=None
    ),
    'celery': ProjectTuple(
        pipfile_dirs=['./server_celery'],
        yarn_dirs=None
    ),
    'flask': ProjectTuple(
        pipfile_dirs=['./server_flask'],
        yarn_dirs=None
    ),
    'registry': ProjectTuple(
        pipfile_dirs=None,
        yarn_dirs=['./web_registry']
    ),
}


def _pipfile_lock(*, context, target_dir: Path):
    """
    Execute a pipenv lock, including development dependencies.
    """

    with context.cd(target_dir):
        context.run(
            command='pipenv lock --dev',
        )


def _pipfile_sync(*, context, target_dir: Path):
    """
    Execute a pipenv clean and sync, including development dependencies.
    """

    with context.cd(target_dir):
        # We also clean so that we don't accidentally have other packages installed,
        # which would likely cause failure in production where those are missing.

        context.run(
            command='pipenv clean',
        )
        context.run(
            command='pipenv sync --dev',
        )


def _yarn_install_frozen(*, context, target_dir: Path):
    """
    Execute a yarn install, keeping the lockfile frozen.
    """

    with context.cd(target_dir):
        context.run(
            command='yarn install --frozen-lockfile',
        )


def _yarn_upgrade(*, context, target_dir: Path):
    """
    Execute a yarn upgrade.
    """

    with context.cd(target_dir):
        context.run(
            command='yarn upgrade',
        )


def _task_install(*, project_name: str):
    @task
    def install(context):
        """
        Install {} dependencies.
        """
        project = PROJECTS[project_name]

        if project.pipfile_dirs:
            for target_dir in project.pipfile_dirs:
                _pipfile_sync(context=context, target_dir=Path(target_dir))
        if project.yarn_dirs:
            for target_dir in project.yarn_dirs:
                _yarn_install_frozen(context=context, target_dir=Path(target_dir))

    install.__doc__ = install.__doc__.format(project_name)

    return install


def _task_update(*, project_name: str):
    @task
    def update(context):
        """
        Update {} dependencies.
        """
        project = PROJECTS[project_name]

        if project.pipfile_dirs:
            for target_dir in project.pipfile_dirs:
                _pipfile_lock(context=context, target_dir=Path(target_dir))
        if project.yarn_dirs:
            for target_dir in project.yarn_dirs:
                _yarn_upgrade(context=context, target_dir=Path(target_dir))

    update.__doc__ = update.__doc__.format(project_name)

    return update


# Build task collection
ns = Collection('dependencies')

ns_install = Collection('install')
for project_current in PROJECTS.keys():
    ns_install.add_task(_task_install(project_name=project_current), name=project_current)

ns_update = Collection('update')
for project_current in PROJECTS.keys():
    ns_update.add_task(_task_update(project_name=project_current), name=project_current)

ns.add_collection(ns_install, 'install')
ns.add_collection(ns_update, 'update')
