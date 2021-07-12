"""
Tasks for the web client.

These are intentionally thin wrappers around `scripts`,
because those scripts will be executed in a production environment that does not include Python.
"""

from invoke import Collection
from invoke import task

from tasks.terminal import run_new_terminal


@task
def dev(context):
    """
    Start a development instance of the client, listening on `localhost:3000`, including hot reloading.

    Builds according to 'config/webpack.dev.js'.

    For development purposes, asynchronously starts in a new terminal.
    """

    run_new_terminal(
        context=context,
        command=' '.join([
            'yarn',
            'web_dev',
        ]),
    )


@task
def prod_build(context):
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
            'web_prod_build',
        ])
    )


@task
def prod_serve(context):
    """
    Serve a production bundle of the client, listening on `0.0.0.0:3000`.

    For production purposes, synchronously executes in the current terminal.

    Is a thin wrapper around `scripts/web_prod_serve.js`,
    because that script will be executed in a production environment that does not include Python.
    """

    context.run(
        command=' '.join([
            'yarn',
            'web_prod_serve',
        ])
    )


# Build task collection
ns = Collection('web')

ns.add_task(dev, name='dev')

ns_prod = Collection('prod')
ns_prod.add_task(prod_build, 'build')
ns_prod.add_task(prod_serve, 'serve')

ns.add_collection(ns_prod)
