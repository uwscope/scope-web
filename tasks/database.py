"""
Tasks for accessing a database.
"""

import aws_infrastructure.task_templates.minikube_helm_instance
from invoke import Collection
from invoke import task
from pathlib import Path

#
# We just want one task ripped out from minikube_helm_instance
#
# TODO: Refactor instance tasks so this can be less of a hack

CONFIG_KEY_FORWARD_PROD = 'server_prod'

ns_instance = aws_infrastructure.task_templates.minikube_helm_instance.create_tasks(
    config_key=CONFIG_KEY_FORWARD_PROD,
    working_dir='.',
    instance_dir=Path('serverconfig', 'prod')
)


@task
def forward_prod(context):
    """
    Forward the database from our production server, listening on `localhost:8000`.

    Access the database using SSH port forwarding and the server's `private` ingress entrypoint.
    """

    ns_instance.tasks['ssh-port-forward'](context, port=8000)


# Build task collection
ns = Collection()

ns_forward = Collection()
ns_forward.add_task(forward_prod, 'prod')

ns.add_collection(ns_forward, 'forward')
