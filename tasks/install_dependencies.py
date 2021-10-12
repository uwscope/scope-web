"""
Tasks for ensuring project dependencies are installed.
"""

from aws_infrastructure.tasks.collection import compose_collection
from invoke import Collection
from invoke import task


@task
def _dev_pipfile(context):
    """
    Execute a pipenv sync, including development dependencies.
    """
    context.run(
        command='pipenv sync --dev',
    )


@task
def _dev_yarn(context):
    """
    Execute a yarn install.
    """
    context.run(
        command='yarn install',
    )


@task(pre=[_dev_pipfile, _dev_yarn])
def dev_install_dependencies(context):
    """
    Ensure development dependencies are installed.
    """

    # Actual work is performed in the pre-requisites
    pass


# Build task collection
ns = Collection('install_dependencies')

ns_dev = Collection('dev')
ns_dev.add_task(dev_install_dependencies, 'install_dependencies')

compose_collection(ns, ns_dev, name='dev')
