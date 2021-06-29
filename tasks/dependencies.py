"""
Tasks for ensuring project dependencies are installed.
"""

from invoke import Collection
from invoke import task


@task
def pipfile_sync_dev(context):
    """
    Execute a pipenv sync, including development dependencies.
    """
    context.run(
        command='pipenv sync --dev',
    )


@task
def yarn_install(context):
    """
    Execute a yarn install.
    """
    context.run(
        command='yarn install',
    )


@task(pre=[pipfile_sync_dev, yarn_install])
def dependencies_dev(context):
    """
    Ensure dependencies are installed, including development dependencies.
    """

    # Actual work is performed in the pre-requisites
    pass


# Build task collection
ns = Collection('dependencies')

ns_ensure = Collection('ensure')
ns_ensure.add_task(dependencies_dev, name='dev')

ns.add_collection(ns_ensure)
