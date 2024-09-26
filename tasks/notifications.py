"""
Task for sending email notification.
"""

from pathlib import Path
from aws_infrastructure.tasks.collection import compose_collection
from invoke import Collection

import scope.tasks.notifications

INSTANCE_SSH_CONFIG_PATH = "./secrets/configuration/instance_ssh.yaml"
DOCUMENTDB_CONFIG_PATH = "./secrets/configuration/documentdb.yaml"
DATABASE_DEV_CONFIG_PATH = "./secrets/configuration/database_dev.yaml"

# Build task collection
ns = Collection("notifications")


if Path(DATABASE_DEV_CONFIG_PATH).exists():
    ns_dev = Collection("dev")
    ns_dev.add_task(
        scope.tasks.notifications.task_email(
            instance_ssh_config_path=INSTANCE_SSH_CONFIG_PATH,
            documentdb_config_path=DOCUMENTDB_CONFIG_PATH,
            database_config_path=DATABASE_DEV_CONFIG_PATH,
        ),
        "email",
    )
    compose_collection(ns, ns_dev, name="dev")
