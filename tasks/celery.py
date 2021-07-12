"""
Tasks for the Celery worker.
"""

from invoke import Collection
from invoke import task
from pathlib import Path

from tasks.terminal import run_new_terminal


@task
def dev(context):
    """
    Start a development instance of Celery.

    For development purposes, asynchronously starts in a new terminal.
    """

    with context.cd(Path('server', 'celery')):
        run_new_terminal(
            context=context,
            command=' '.join([
                'celery',
                '-A app',
                'worker',
                '--concurrency=1',
            ]),
        )


# Build task collection
ns = Collection('celery')

ns.add_task(dev, name='dev')
