"""
Tasks for the Flask server.
"""

from invoke import Collection
from invoke import task
from pathlib import Path

from tasks.terminal import run_new_terminal


@task
def dev(context):
    """
    Start a development instance of Flask, listening on `localhost:4000`, including hot reloading.

    For development purposes, asynchronously starts in a new terminal.
    """

    with context.cd(Path('server', 'flask')):
        run_new_terminal(
            context=context,
            command=' '.join([
                'flask',
                'run',
            ]),
            env={
                'FLASK_ENV': 'development',
                'FLASK_RUN_HOST': 'localhost',
                'FLASK_RUN_PORT': '4000',
            },
        )


@task
def prod(context):
    """
    Start a production build of Flask, listening on `0.0.0.0:4000`.

    For production purposes, synchronously executes in the current terminal.
    """

    with context.cd(Path('server', 'flask')):
        context.run(
            command=' '.join([
                'waitress-serve',
                '--port=4000',
                '--call "app:create_app"'
            ]),
            env={
                'FLASK_ENV': 'production'
            }
        )


# Build task collection
ns = Collection('flask')

ns.add_task(dev, name='dev')
ns.add_task(prod, name='prod')
