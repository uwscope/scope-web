"""
Tasks for accessing a database.
"""

import aws_infrastructure.tasks.library.minikube_helm_instance
from invoke import Collection
from invoke import task
from pathlib import Path

from tasks.terminal import spawn_new_terminal

#
# We just want one task ripped out from minikube_helm_instance
#
# TODO: Refactor instance tasks so this can be less of a hack

CONFIG_KEY = 'server_prod'

ns_instance = aws_infrastructure.tasks.library.minikube_helm_instance.create_tasks(
    config_key=CONFIG_KEY,
    working_dir='.',
    instance_dir=Path('secrets', 'server', 'prod')
)


@task
def forward_prod(context):
    """
    Forward the database from our production server, listening on `localhost:8000`.

    For development purposes, asynchronously spawns a new terminal.

    Access the database using SSH port forwarding and the server's `private` ingress entrypoint.
    """

    if spawn_new_terminal(context=context):
        ns_instance.tasks['ssh-port-forward'](context, port=8000)


# Build task collection
ns = Collection('database')

ns_forward = Collection('forward')
ns_forward.add_task(forward_prod, 'prod')

ns.add_collection(ns_forward)
