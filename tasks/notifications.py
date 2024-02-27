"""
Task for executing a webpush notification.
"""

from pathlib import Path
from invoke import Collection, task

import aws_infrastructure.tasks.terminal

import scope.tasks.webpush_notifications

INSTANCE_SSH_CONFIG_PATH = "./secrets/configuration/instance_ssh.yaml"
DOCUMENTDB_CONFIG_PATH = "./secrets/configuration/documentdb.yaml"
DATABASE_DEV_CONFIG_PATH = "./secrets/configuration/database_dev.yaml"
VAPID_KEYS_CONFIG_PATH = "./secrets/configuration/vapid_keys_local.yaml"

# Build task collection
ns = Collection("notifications")


if Path(DATABASE_DEV_CONFIG_PATH).exists() and Path(VAPID_KEYS_CONFIG_PATH).exists():
    ns.add_task(
        scope.tasks.webpush_notifications.task_webpush_notifications(
            instance_ssh_config_path=INSTANCE_SSH_CONFIG_PATH,
            documentdb_config_path=DOCUMENTDB_CONFIG_PATH,
            database_config_path=DATABASE_DEV_CONFIG_PATH,
            vapid_config_path=VAPID_KEYS_CONFIG_PATH,
        ),
        "trigger-push-notification",
    )
