"""
These are intentionally thin wrappers around the scripts found in `scripts`,
because those will be executed in a production environment that does not include Python.
"""

from aws_infrastructure.tasks.collection import compose_collection
import aws_infrastructure.tasks.terminal
from invoke import Collection
from invoke import task
from pathlib import Path

WEB_PATIENT_PATH = './web_patient'


@task
def dev_serve(context):
    """
    Serve the client, listening on `localhost:3000`, including hot reloading.

    Builds according to 'config/webpack.dev.js'.

    For development purposes, asynchronously starts in a new terminal.
    """

    if aws_infrastructure.tasks.terminal.spawn_new_terminal(context):
        with context.cd(Path(WEB_PATIENT_PATH)):
            context.run(
                command=' '.join([
                    'yarn',
                    'dev_serve',
                ])
            )


@task
def prod_build(context):
    """
    Build a bundle of the client.

    Builds according to 'config/webpack.prod.js', including hot reloading.

    For production purposes, synchronously executes in the current terminal.

    Is a thin wrapper around `scripts/web_prod_build.js`,
    because that script will be executed in a production environment that does not include Python.
    """

    with context.cd(Path(WEB_PATIENT_PATH)):
        context.run(
            command=' '.join([
                'yarn',
                'prod_build',
            ])
        )


@task
def prod_serve(context):
    """
    Serve a bundle of the client, listening on `0.0.0.0:3000`.

    For production purposes, synchronously executes in the current terminal.

    Is a thin wrapper around `scripts/web_prod_serve.js`,
    because that script will be executed in a production environment that does not include Python.
    """

    with context.cd(Path(WEB_PATIENT_PATH)):
        context.run(
            command=' '.join([
                'yarn',
                'prod_serve',
            ])
        )


# Build task collection
ns = Collection('registry')

ns_dev = Collection('dev')
ns_dev.add_task(dev_serve, name='serve')

ns_prod = Collection('prod')
ns_prod.add_task(prod_build, 'build')
ns_prod.add_task(prod_serve, 'serve')

compose_collection(ns, ns_dev, name='dev')
compose_collection(ns, ns_prod, name='prod')
