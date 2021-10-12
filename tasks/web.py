"""
Tasks for the web client.

These are intentionally thin wrappers around the scripts found in `scripts`,
because those will be executed in a production environment that does not include Python.
"""

from aws_infrastructure.tasks.collection import compose_collection
from invoke import Collection
from invoke import task

from tasks.terminal import spawn_new_terminal


@task
def dev_web(context):
    """
    Serve the client, listening on `localhost:3000`, including hot reloading.

    Builds according to 'config/webpack.dev.js'.

    For development purposes, asynchronously starts in a new terminal.
    """

    if spawn_new_terminal(context):
        context.run(
            command=' '.join([
                'yarn',
                'dev_web',
            ])
        )


@task
def prod_web_build(context):
    """
    Build a production bundle of the client.

    Builds according to 'config/webpack.prod.js', including hot reloading.

    For production purposes, synchronously executes in the current terminal.

    Is a thin wrapper around `scripts/web_prod_build.js`,
    because that script will be executed in a production environment that does not include Python.
    """

    context.run(
        command=' '.join([
            'yarn',
            'prod_web_build',
        ])
    )


@task
def prod_web_serve(context):
    """
    Serve a production bundle of the client, listening on `0.0.0.0:3000`.

    For production purposes, synchronously executes in the current terminal.

    Is a thin wrapper around `scripts/web_prod_serve.js`,
    because that script will be executed in a production environment that does not include Python.
    """

    context.run(
        command=' '.join([
            'yarn',
            'prod_web_serve',
        ])
    )


# Build task collection
ns = Collection('web')

ns_dev = Collection('dev')
ns_dev.add_task(dev_web, name='web')

ns_prod = Collection('prod')
ns_prod.add_task(prod_web_build, 'web_build')
ns_prod.add_task(prod_web_serve, 'web_serve')

compose_collection(ns, ns_dev, name='dev')
compose_collection(ns, ns_prod, name='prod')
